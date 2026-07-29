"""Prevents double-processing when Meta retries a webhook delivery.

Meta will resend the same webhook event if your server doesn't ack
within its timeout window. Without this check, a slow response (or a
network blip on the reply) can cause the same user question to be
answered twice.
"""

from app.extensions import redis_client

DEDUPE_KEY_PREFIX = "wavygo:seen_msg:"
DEDUPE_TTL_SECONDS = 60 * 60 * 24  # 24h is plenty for Meta's retry window


def already_processed(message_id: str) -> bool:
    """Returns True if this exact WhatsApp message ID was already handled.

    Uses SETNX semantics: the first caller to see a message ID "claims"
    it and gets False (not a duplicate); every subsequent call for the
    same ID gets True.
    """
    key = f"{DEDUPE_KEY_PREFIX}{message_id}"
    claimed = redis_client.setnx(key, "1")
    if claimed:
        redis_client.expire(key, DEDUPE_TTL_SECONDS)
        return False
    return True
