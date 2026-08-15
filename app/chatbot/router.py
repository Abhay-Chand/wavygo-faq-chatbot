from typing import Literal


Route = Literal[
    "faq",
    "normal",
    "out_of_scope",
]


NORMAL_MESSAGES = {
    "hi",
    "hello",
    "hey",
    "thanks",
    "thank you",
    "good morning",
    "good afternoon",
    "good evening",
    "bye",
    "goodbye",
}


def classify_query(message: str) -> Route:

    normalized_message = message.strip().lower()

    if not normalized_message:
        return "out_of_scope"

    if normalized_message in NORMAL_MESSAGES:
        return "normal"

    return "faq"


def route_after_classification(
    state: dict,
) -> Route:

    intent = state.get("intent")

    if intent == "normal":
        return "normal"

    if intent == "faq":
        return "faq"

    return "out_of_scope"


def route_after_retrieval(
    state: dict,
) -> str:

    if state.get("context_relevant", False):
        return "answer"

    return "fallback"