import logging

from flask import Blueprint, request, jsonify

from app.config import config
from app.services import state_machine, whatsapp_client
from app.utils.dedupe import already_processed
from app.utils.signature import is_valid_signature

logger = logging.getLogger(__name__)

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/webhook", methods=["GET"])
def verify_webhook():
    """One-time handshake Meta calls when you set up the webhook URL
    in the developer console. Must echo back hub.challenge if the
    verify token matches what you configured.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == config.META_VERIFY_TOKEN:
        return challenge, 200

    logger.warning("Webhook verification failed: bad token or mode.")
    return "Verification failed", 403


@webhook_bp.route("/webhook", methods=["POST"])
def receive_webhook():
    """Receives every message/status event from Meta.

    IMPORTANT: we ack with 200 as early as possible. Meta retries on
    timeout, and a slow ack under load is the single most common cause
    of duplicate replies for bots like this.
    """
    raw_body = request.get_data()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if config.META_APP_SECRET and not is_valid_signature(raw_body, signature):
        logger.warning("Rejected webhook call with invalid signature.")
        return jsonify({"status": "invalid signature"}), 403

    payload = request.get_json(silent=True) or {}

    try:
        _process_payload(payload)
    except Exception:  # noqa: BLE001
        # Never let a bug in message handling turn into a 500 that makes
        # Meta retry-storm the same event. Log it, still ack 200.
        logger.exception("Error while processing webhook payload")

    return jsonify({"status": "ok"}), 200


def _process_payload(payload: dict) -> None:
    entries = payload.get("entry", [])
    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            for message in messages:
                _handle_single_message(message)


def _handle_single_message(message: dict) -> None:
    message_id = message.get("id")
    phone = message.get("from")

    if not message_id or not phone:
        return

    if already_processed(message_id):
        logger.info("Skipping duplicate message id=%s", message_id)
        return

    whatsapp_client.mark_as_read(message_id)

    msg_type = message.get("type")
    text = ""
    interactive_id = None

    if msg_type == "text":
        text = message.get("text", {}).get("body", "")
    elif msg_type == "interactive":
        interactive = message.get("interactive", {})
        if interactive.get("type") == "list_reply":
            interactive_id = interactive["list_reply"].get("id")
            text = interactive["list_reply"].get("title", "")
        elif interactive.get("type") == "button_reply":
            interactive_id = interactive["button_reply"].get("id")
            text = interactive["button_reply"].get("title", "")
    else:
        # Unsupported message type (image, audio, location, etc.)
        text = ""

    if not text and not interactive_id:
        return

    state_machine.handle_incoming_message(phone, text, interactive_id)
