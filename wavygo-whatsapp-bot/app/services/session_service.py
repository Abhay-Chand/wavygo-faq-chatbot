"""Per-user conversation session, backed by Redis.

Why Redis and not a database table: this is short-lived, high-churn,
key-value state (current step, chosen language) that needs a TTL so
abandoned conversations clean themselves up automatically. A SQL/NoSQL
table would work but you'd have to build expiry yourself; Redis gives
you EX for free and is materially faster for this access pattern.
"""

import json

from app.config import config
from app.extensions import redis_client

SESSION_KEY_PREFIX = "wavygo:session:"

DEFAULT_SESSION = {
    "state": "LANGUAGE_SELECTION",
    "language": config.DEFAULT_LANGUAGE,
    "pending_category": None,
}


def _key(phone: str) -> str:
    return f"{SESSION_KEY_PREFIX}{phone}"


def get_session(phone: str) -> dict:
    raw = redis_client.get(_key(phone))
    if not raw:
        return dict(DEFAULT_SESSION)
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return dict(DEFAULT_SESSION)


def save_session(phone: str, session: dict) -> None:
    redis_client.set(
        _key(phone),
        json.dumps(session),
        ex=config.SESSION_TTL_SECONDS,
    )


def reset_session(phone: str) -> dict:
    session = dict(DEFAULT_SESSION)
    save_session(phone, session)
    return session
