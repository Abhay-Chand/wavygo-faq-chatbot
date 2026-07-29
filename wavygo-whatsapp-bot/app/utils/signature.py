"""Verifies the X-Hub-Signature-256 header Meta sends on every webhook call.

Without this, anyone who discovers your webhook URL can POST fake
WhatsApp messages to your bot. Meta signs the raw request body with
your app secret (HMAC-SHA256) - we recompute it and compare.
"""

import hashlib
import hmac

from app.config import config


def is_valid_signature(request_body: bytes, signature_header: str) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected = hmac.new(
        key=config.META_APP_SECRET.encode("utf-8"),
        msg=request_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    received = signature_header.split("sha256=", 1)[1]
    return hmac.compare_digest(expected, received)
