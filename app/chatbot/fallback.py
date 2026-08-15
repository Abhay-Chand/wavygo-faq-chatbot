import os

from dotenv import load_dotenv

from app.chatbot.state import ChatState


load_dotenv()


def fallback_node(state: ChatState) -> ChatState:

    support_email = os.getenv(
        "SUPPORT_EMAIL",
        "support@example.com",
    )

    support_phone = os.getenv(
        "SUPPORT_PHONE",
        "+91 XXXXX XXXXX",
    )

    return {
        "answer": (
            "I'm sorry, I couldn't find an answer to that "
            "in the WavyGo FAQ.\n\n"
            "For further Support, please contact our support team:\n"
            f"Phone: {support_phone}\n"
            f"Email: {support_email}"
        ),
        "contact_support": True,
    }