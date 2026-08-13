from app.chatbot.state import ChatState
from app.chatbot.router import classify_query
from app.rag.retriever import get_faq_retriever


def classify_node(state: ChatState) -> ChatState:
    """
    Classify the user's query.
    """

    user_message = state["user_message"]

    intent = classify_query(user_message)

    return {
        "intent": intent
    }


def normal_response_node(state: ChatState) -> ChatState:
    """
    Handle normal conversational messages.
    """

    user_message = state["user_message"].strip().lower()

    if user_message in {"hi", "hello", "hey"}:
        answer = (
            "Hello! 👋 How can I help you with WavyGo?"
        )

    elif user_message in {
        "good morning",
        "good afternoon",
        "good evening",
    }:
        answer = (
            "Hello! 👋 How can I help you with WavyGo?"
        )

    elif user_message in {"thanks", "thank you"}:
        answer = (
            "You're welcome! If you have any WavyGo-related "
            "questions, feel free to ask."
        )

    elif user_message in {"bye", "goodbye"}:
        answer = (
            "Goodbye! Have a great day."
        )

    else:
        answer = (
            "Hello! I'm the WavyGo FAQ assistant. "
            "I can help you with questions about WavyGo."
        )

    return {
        "answer": answer,
        "contact_support": False,
    }


def retrieve_faq_node(state: ChatState) -> ChatState:
    """
    Retrieve relevant FAQ documents from the vector database.
    """

    user_message = state["user_message"]

    retriever = get_faq_retriever()

    documents = retriever.invoke(user_message)

    return {
        "retrieved_documents": documents
    }