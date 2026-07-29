import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.config import config
from app.services.faq_matcher import faq_matcher


def test_webhook_verification_succeeds_with_correct_token():
    app = create_app()
    client = app.test_client()
    resp = client.get(
        "/webhook",
        query_string={
            "hub.mode": "subscribe",
            "hub.verify_token": config.META_VERIFY_TOKEN,
            "hub.challenge": "12345",
        },
    )
    assert resp.status_code == 200
    assert resp.data.decode() == "12345"


def test_webhook_verification_fails_with_wrong_token():
    app = create_app()
    client = app.test_client()
    resp = client.get(
        "/webhook",
        query_string={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "12345",
        },
    )
    assert resp.status_code == 403


def test_health_check():
    app = create_app()
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200


def test_faq_matcher_finds_documents_question():
    entry, score = faq_matcher.match("what documents do I need", "en")
    assert entry is not None
    assert entry["category"] == "Documents"
    assert score > 0.3


def test_faq_matcher_returns_low_score_for_unrelated_query():
    entry, score = faq_matcher.match("what is the weather today", "en")
    assert entry is None or score < config.FAQ_MATCH_THRESHOLD
