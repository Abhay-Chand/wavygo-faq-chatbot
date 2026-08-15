from typing import Literal

from langchain_core.documents import Document
from typing_extensions import TypedDict


Intent = Literal[
    "faq",
    "normal",
    "out_of_scope",
]


class ChatState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    # Original user message
    user_message: str

    # Query classification
    intent: Intent

    # Retrieved FAQ documents
    retrieved_documents: list[Document]

    # Best Chroma similarity distance
    relevance_score: float

    # Whether relevant FAQ context exists
    context_relevant: bool

    # Final chatbot response
    answer: str

    # Whether frontend should show support contact options
    contact_support: bool