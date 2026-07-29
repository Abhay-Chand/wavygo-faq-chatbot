import logging

import redis

from app.config import config

logger = logging.getLogger(__name__)


class _InMemoryFallback:
    """Minimal drop-in used ONLY if Redis is unreachable at boot.

    This exists so a broken REDIS_URL fails soft on your laptop instead
    of crashing the app - it is NOT safe for real deployments because
    state disappears on every restart and isn't shared across workers.
    If you see this in production logs, fix REDIS_URL immediately.
    """

    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value, ex=None):
        self._store[key] = value
        return True

    def setnx(self, key, value):
        if key in self._store:
            return False
        self._store[key] = value
        return True

    def expire(self, key, seconds):
        return True

    def delete(self, key):
        self._store.pop(key, None)
        return True


def _build_redis_client():
    try:
        client = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)
        client.ping()
        logger.info("Connected to Redis at %s", config.REDIS_URL)
        return client
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Could not connect to Redis (%s). Falling back to in-memory "
            "store - sessions will NOT persist or scale. Fix REDIS_URL "
            "before deploying.",
            exc,
        )
        return _InMemoryFallback()


redis_client = _build_redis_client()
