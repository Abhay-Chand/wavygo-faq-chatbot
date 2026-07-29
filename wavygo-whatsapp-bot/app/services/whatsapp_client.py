"""Outbound message sending via the Meta WhatsApp Cloud API.

Uses the official Graph API directly - no third-party BSP - so the
only recurring cost is Meta's own conversation-based pricing, not a
markup layered on top by a middleman provider.
"""

import logging

import requests

from app.config import config

logger = logging.getLogger(__name__)


def _post(payload: dict) -> dict:
    url = f"{config.META_BASE_URL}/messages"
    headers = {
        "Authorization": f"Bearer {config.META_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code >= 400:
            logger.error(
                "WhatsApp send failed (%s): %s", resp.status_code, resp.text
            )
        return resp.json()
    except requests.RequestException as exc:
        logger.error("WhatsApp send raised an exception: %s", exc)
        return {"error": str(exc)}


def send_text(to: str, body: str) -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    return _post(payload)


def send_list_menu(to: str, header: str, body: str, button_text: str, rows: list) -> dict:
    """Send an interactive list message - used for FAQ category menus.

    rows: list of {"id": str, "title": str} (title max 24 chars per
    WhatsApp's own limit - keep category names short).
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header[:60]},
            "body": {"text": body[:1024]},
            "action": {
                "button": button_text[:20],
                "sections": [
                    {
                        "title": "Menu",
                        "rows": [
                            {"id": r["id"], "title": r["title"][:24]}
                            for r in rows[:10]  # WhatsApp caps at 10 rows
                        ],
                    }
                ],
            },
        },
    }
    return _post(payload)


def mark_as_read(message_id: str) -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    return _post(payload)
