import os


class Config:
    """Single source of truth for all environment-driven settings.

    Nothing in the rest of the app should call os.environ directly -
    it should read from this class so every setting is documented
    and defaults are visible in one place.
    """

    # Meta WhatsApp Cloud API
    META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
    META_PHONE_NUMBER_ID = os.environ.get("META_PHONE_NUMBER_ID", "")
    META_VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN", "")
    META_APP_SECRET = os.environ.get("META_APP_SECRET", "")
    META_API_VERSION = os.environ.get("META_API_VERSION", "v20.0")

    @property
    def META_BASE_URL(self):
        return f"https://graph.facebook.com/{self.META_API_VERSION}/{self.META_PHONE_NUMBER_ID}"

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Bot behaviour
    SESSION_TTL_SECONDS = int(os.environ.get("SESSION_TTL_SECONDS", 86400))
    FAQ_MATCH_THRESHOLD = float(os.environ.get("FAQ_MATCH_THRESHOLD", 0.30))
    DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "en")
    SUPPORTED_LANGUAGES = ["en", "hi"]

    # Support contact shown on NO_MATCH
    SUPPORT_EMAIL = os.environ.get("SUPPORT_EMAIL", "support@wavygo.in")
    SUPPORT_PHONE = os.environ.get("SUPPORT_PHONE", "+91XXXXXXXXXX")

    # Flask
    PORT = int(os.environ.get("PORT", 5000))


config = Config()
