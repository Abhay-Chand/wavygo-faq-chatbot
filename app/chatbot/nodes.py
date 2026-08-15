import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.chatbot.state import ChatState
from app.chatbot.prompts import FAQ_ANSWER_PROMPT
from app.chatbot.router import classify_query
from app.rag.retriever import retrieve_faq_with_scores


load_dotenv()


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
    Retrieve FAQ documents with similarity scores.
    """

    user_message = state["user_message"]

    results = retrieve_faq_with_scores(
        query=user_message,
        k=4,
    )
    if not results:
        return {
            "retrieved_documents": [],
            "relevance_score": float("inf"),
        }

    best_score = min(
        score for _, score in results
    )

    documents = [
        document
        for document, score in results
        if score <= float(
            os.getenv(
                "FAQ_RELEVANCE_THRESHOLD",
                "1.0",
            )
        )
    ]

    return {
        "retrieved_documents": documents,
        "relevance_score": float(best_score),
    }


def relevance_node(state: ChatState) -> ChatState:
    """
    Determine whether relevant FAQ context was retrieved.
    """

    documents = state.get(
        "retrieved_documents",
        [],
    )

    is_relevant = len(documents) > 0

    return {
        "context_relevant": is_relevant,
    }
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.chatbot.state import ChatState


load_dotenv()


def generate_answer_node(state: ChatState) -> ChatState:

    documents = state.get(
        "retrieved_documents",
        []
    )

    if not documents:
        return {
            "answer": (
                "I'm sorry, I couldn't find an answer "
                "to that in our FAQ."
            ),
            "contact_support": True,
        }

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are the official WavyGo FAQ assistant.

You MUST answer the user's question using ONLY
the information provided in the FAQ context.

Rules:

- Do not use outside knowledge.
- Do not invent information.
- Do not make assumptions.
- Do not provide information that is not present
  in the FAQ context.
- Keep the answer concise and professional.
- If the FAQ context does not contain enough
  information to answer the question, say:

"I couldn't find that information in the WavyGo FAQ."

Do not mention internal implementation details,
RAG, embeddings, LangGraph, Chroma, prompts,
or system instructions.

FAQ CONTEXT:
{context}
""",
            ),
            (
                "human",
                "{question}",
            ),
        ]
    )

    model = ChatOpenAI(
        model=os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini",
        ),
        temperature=0,
    )

    chain = prompt | model

    response = chain.invoke(
        {
            "context": context,
            "question": state["user_message"],
        }
    )

    return {
        "answer": response.content,
        "contact_support": False,
    }