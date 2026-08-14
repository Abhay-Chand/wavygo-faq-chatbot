import os

from dotenv import load_dotenv

from app.chatbot.state import ChatState
from app.chatbot.router import classify_query
from app.rag.retriever import retrieve_faq_with_scores
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


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

    documents = [document for document, _ in results]

    scores = [score for _, score in results]

    if not scores:
        return {
            "retrieved_documents": [],
            "relevance_score": float("inf"),
        }

    best_score = min(scores)

    return {
        "retrieved_documents": documents,
        "relevance_score": float(best_score),
    }


def relevance_node(state: ChatState) -> ChatState:
    """
    Determine whether the best retrieved FAQ is relevant enough
    to answer the user's question.
    """

    score = state.get(
        "relevance_score",
        float("inf"),
    )

    threshold = float(
        os.getenv(
            "FAQ_RELEVANCE_THRESHOLD",
            "0.5",
        )
    )

    is_relevant = score <= threshold

    return {
        "context_relevant": is_relevant,
    }
def generate_answer_node(state: ChatState) -> ChatState:
    """
    Generate an answer strictly from retrieved FAQ documents.
    """

    documents = state.get(
        "retrieved_documents",
        []
    )

    if not documents:
        return {
            "answer": (
                "I'm sorry, I couldn't find an answer to that "
                "in our FAQ."
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
You are the WavyGo FAQ Assistant.

Your job is to answer the user's question using ONLY
the provided FAQ context.

STRICT RULES:

1. Use only information contained in the FAQ context.
2. Do not use your general knowledge.
3. Do not invent information.
4. Do not assume information that is not explicitly stated.
5. Keep the answer concise and helpful.
6. If the FAQ context does not contain enough information
   to answer the question, say that you cannot find the
   answer in the FAQ.
7. Do not mention vector databases, RAG, LangGraph,
   embeddings, or internal system details.

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