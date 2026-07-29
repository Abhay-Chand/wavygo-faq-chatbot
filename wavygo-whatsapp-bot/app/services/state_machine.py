"""Conversation state machine.

States (matches the WavyGo report):
  LANGUAGE_SELECTION -> WELCOME -> FAQ_MENU -> (FAQ_RESPONSE | NO_MATCH) -> FAQ_MENU ...

FAQ_MENU is the resting state: once language is picked, the user can
type any question at any time and get matched, or type "menu" to see
categories again. This keeps the bot forgiving of free text instead
of forcing a rigid category-first flow.
"""

from app.config import config
from app.services import session_service, whatsapp_client
from app.services.faq_matcher import faq_matcher

COPY = {
    "en": {
        "language_prompt": (
            "Welcome to WavyGo!\nPlease select your preferred language.\n"
            "1. English\n2. Hindi"
        ),
        "language_not_understood": (
            "Sorry, I didn't catch that. Reply 1 for English or 2 for Hindi."
        ),
        "welcome": (
            "Welcome to WavyGo!\nI'm here to help answer your frequently "
            "asked questions.\nType your question, or type Menu to see categories."
        ),
        "menu_header": "FAQ categories",
        "menu_body": "Choose a category, or just type your question directly.",
        "menu_button": "View categories",
        "another_question": "Do you have another question? Type it, or type Menu.",
        "no_match": (
            "Sorry, I couldn't find an answer to that question.\n"
            "Please contact our support team:\n"
            f"Email: {config.SUPPORT_EMAIL}\n"
            f"Phone: {config.SUPPORT_PHONE}\n"
            "Reply Menu to view the FAQ categories again."
        ),
    },
    "hi": {
        "language_prompt": (
            "WavyGo mein aapka swagat hai!\nKripya apni pasandida bhasha chunein.\n"
            "1. English\n2. Hindi"
        ),
        "language_not_understood": (
            "Kshama karein, samajh nahi aaya. English ke liye 1 ya Hindi ke liye 2 likhein."
        ),
        "welcome": (
            "WavyGo mein aapka swagat hai!\nMain aapke saamanya prashno ke uttar "
            "dene mein sahayata karoonga.\nApna prashn likhein, ya Menu likhein."
        ),
        "menu_header": "FAQ shreniyan",
        "menu_body": "Ek shreni chunein, ya seedhe apna prashn likhein.",
        "menu_button": "Shreniyan dekhein",
        "another_question": "Kya aapka koi aur prashn hai? Likhein, ya Menu likhein.",
        "no_match": (
            "Kshama karein, mujhe is prashn ka uttar nahi mila.\n"
            "Kripya hamari sahayata team se sampark karein:\n"
            f"Email: {config.SUPPORT_EMAIL}\n"
            f"Phone: {config.SUPPORT_PHONE}\n"
            "FAQ suchi dekhne ke liye Menu likhein."
        ),
    },
}


def _detect_language(text: str):
    normalized = text.strip().lower()
    if normalized in ("1", "english", "en"):
        return "en"
    if normalized in ("2", "hindi", "hi", "हिंदी"):
        return "hi"
    return None


def _is_menu_command(text: str) -> bool:
    return text.strip().lower() in ("menu", "hi", "hello", "start")


def _send_category_menu(phone: str, lang: str):
    categories = faq_matcher.categories(lang)
    copy = COPY[lang]
    rows = [{"id": f"cat_{c}", "title": c} for c in categories]
    whatsapp_client.send_list_menu(
        to=phone,
        header=copy["menu_header"],
        body=copy["menu_body"],
        button_text=copy["menu_button"],
        rows=rows,
    )


def handle_incoming_message(phone: str, text: str, interactive_id: str = None) -> None:
    """Main entry point called by the webhook route for every inbound message.

    `text` is the free-text body (or the title of a selected list row).
    `interactive_id` is the row id if the user tapped a list option
    (e.g. "cat_Documents") - used to jump straight to a category.
    """
    session = session_service.get_session(phone)
    state = session.get("state", "LANGUAGE_SELECTION")
    lang = session.get("language", config.DEFAULT_LANGUAGE)

    if state == "LANGUAGE_SELECTION":
        chosen = _detect_language(text)
        if not chosen:
            whatsapp_client.send_text(phone, COPY["en"]["language_prompt"])
            return
        session["language"] = chosen
        session["state"] = "FAQ_MENU"
        session_service.save_session(phone, session)
        whatsapp_client.send_text(phone, COPY[chosen]["welcome"])
        _send_category_menu(phone, chosen)
        return

    # From here on the user is in the FAQ_MENU "resting state".
    if _is_menu_command(text) and not interactive_id:
        _send_category_menu(phone, lang)
        return

    if interactive_id and interactive_id.startswith("cat_"):
        category = interactive_id[len("cat_"):]
        entries = faq_matcher.entries_for_category(lang, category)
        if entries:
            lines = "\n".join(f"- {e['q']}" for e in entries[:10])
            whatsapp_client.send_text(phone, f"{category}:\n{lines}")
        return

    entry, score = faq_matcher.match(text, lang)
    if entry and score >= config.FAQ_MATCH_THRESHOLD:
        whatsapp_client.send_text(phone, entry["a"])
        whatsapp_client.send_text(phone, COPY[lang]["another_question"])
    else:
        whatsapp_client.send_text(phone, COPY[lang]["no_match"])

    session["state"] = "FAQ_MENU"
    session_service.save_session(phone, session)
