# WavyGo WhatsApp FAQ Bot (Flask)

A production-lean WhatsApp FAQ bot for WavyGo, built on the Meta WhatsApp
Cloud API directly (no third-party BSP, so the only recurring cost is
Meta's own conversation pricing).

## Architecture

```
WhatsApp user -> Meta Cloud API -> Flask /webhook -> Redis (session state)
                                                   -> FAQ matcher (TF-IDF, in-memory)
                                  <- Meta Cloud API <- reply sent back
```

- **Flask** handles the webhook (I/O-bound, ack-fast-then-process).
- **Redis** stores per-user conversation state with a TTL (no DB table needed).
- **FAQ matcher** is TF-IDF + cosine similarity over `app/data/faqs.json` -
  no LLM call, no vector DB, rebuilt in memory at startup. Fine up to a
  few thousand FAQ entries; swap in embeddings/FAISS only if you outgrow that.

## Project structure

```
wavygo-whatsapp-bot/
├── app/
│   ├── __init__.py            # Flask app factory
│   ├── config.py              # all env-driven settings
│   ├── extensions.py          # Redis client (with local fallback)
│   ├── routes/
│   │   └── webhook.py         # GET verify + POST receive
│   ├── services/
│   │   ├── whatsapp_client.py # send text / list menu via Cloud API
│   │   ├── session_service.py # Redis-backed session get/save
│   │   ├── faq_matcher.py     # TF-IDF cosine similarity matching
│   │   └── state_machine.py   # conversation state transitions + copy
│   ├── utils/
│   │   ├── signature.py       # HMAC verification of Meta webhook calls
│   │   └── dedupe.py          # prevents double-processing on retries
│   └── data/
│       └── faqs.json          # FAQ content, English + Hindi
├── tests/
│   └── test_webhook.py
├── requirements.txt
├── run.py
├── Procfile
└── .env.example
```

## Local setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in your real values
```

Run Redis locally (or point REDIS_URL at Upstash/Redis Cloud - both have
free tiers that are enough for this bot):

```bash
docker run -p 6379:6379 redis:7-alpine
```

Start the server:

```bash
python run.py
```

Run tests:

```bash
pytest
```

## Meta setup (one-time)

1. Create a Meta app at developers.facebook.com, add the "WhatsApp" product.
2. Grab your **temporary access token**, **phone number ID**, and **app
   secret** from the Meta dashboard - put them in `.env`.
3. Set `META_VERIFY_TOKEN` in `.env` to any random string you choose.
4. Deploy the app somewhere with a public HTTPS URL (see below).
5. In the Meta dashboard, set the webhook URL to
   `https://your-domain.com/webhook` and the verify token to the same
   value you put in `META_VERIFY_TOKEN`. Meta will call the GET endpoint
   once to confirm - `verify_webhook()` handles that handshake.
6. Subscribe to the `messages` field.
7. Once you're out of test mode, generate a **permanent** access token
   (System User token) instead of the temporary one - temporary tokens
   expire in 24h and will silently break your bot.

## Deploying (low-cost)

Any small host works since the actual load here is tiny. Render or
Railway's free/hobby tier is enough:

```bash
# Procfile is already set up for gunicorn:
web: gunicorn run:app --workers 2 --timeout 30 --bind 0.0.0.0:$PORT
```

Set the same environment variables from `.env.example` in your host's
dashboard. Use a real Redis add-on (Upstash free tier is fine) - do not
rely on the in-memory fallback in `extensions.py` in production; it
exists only so local dev doesn't crash without Redis running, and it
will lose all session state on every restart/deploy.

## Editing FAQ content

Edit `app/data/faqs.json` directly - no code changes needed. Keep the
same `id` across the `en` and `hi` arrays for a given question so both
language versions stay in sync. Restart the process (or wire up an
admin endpoint calling `faq_matcher.load()`) to pick up changes.

Tune `FAQ_MATCH_THRESHOLD` in `.env` if the bot is matching wrong
answers (raise it) or falling to NO_MATCH too often on valid questions
(lower it). Start at 0.30 and adjust based on real conversation logs.

## Testing the webhook manually

```bash
curl -X GET "http://localhost:5000/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=123"
```

Should return `123` with a 200 status.
