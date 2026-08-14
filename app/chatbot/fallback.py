import os

from dotenv import load_dotenv

from app.chatbot.state import ChatState


load_dotenv()


def fallback_node(state: ChatState) -> ChatState:
    """
    Handle questions that are outside the available FAQ knowledge.
    """

    support_email = os.getenv(
        "SUPPORT_EMAIL",
        "support@example.com",
    )

    support_phone = os.getenv(
        "SUPPORT_PHONE",
        "+91 XXXXX XXXXX",
    )

    answer = (
        "I'm sorry, I couldn't find an answer to that "
        "in our FAQ.\n\n"
        "For further assistance, please contact our support team:\n\n"
        f"📞 {support_phone}\n"
        f"📧 {support_email}"
    )

    return {
        "answer": answer,
        "contact_support": True,
    }