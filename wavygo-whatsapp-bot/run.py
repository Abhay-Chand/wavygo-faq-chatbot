from app import create_app
from app.config import config

app = create_app()

if __name__ == "__main__":
    # Local dev only. In production, gunicorn imports `app` directly
    # (see Procfile) - this block never runs there.
    app.run(host="0.0.0.0", port=config.PORT, debug=True)
