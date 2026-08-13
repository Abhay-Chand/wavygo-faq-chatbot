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
    """
    Classify a user message into one of the supported chatbot routes.

    This is intentionally conservative.
    """

    normalized_message = message.strip().lower()

    # Empty input
    if not normalized_message:
        return "out_of_scope"

    # Normal conversational behaviour
    if normalized_message in NORMAL_MESSAGES:
        return "normal"

    # Everything else initially goes through the FAQ retrieval layer.
    return "faq"

def route_after_classification(
    state: dict,
) -> Route:
    """
    Determine the next LangGraph node after classification.
    """

    intent = state.get("intent")

    if intent == "normal":
        return "normal"

    if intent == "faq":
        return "faq"

    return "out_of_scope"

def route_after_retrieval(
    state: dict,
) -> str:
    """
    Determine whether retrieved FAQ context is sufficient.
    """

    if state.get("context_relevant", False):
        return "answer"

    return "fallback"