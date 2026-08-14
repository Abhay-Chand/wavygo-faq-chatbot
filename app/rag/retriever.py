from langchain_chroma import Chroma

from app.rag.vectorstore import get_vectorstore


def get_faq_vectorstore() -> Chroma:
    """
    Return the WavyGo FAQ vector store.
    """

    return get_vectorstore()


def retrieve_faq_with_scores(
    query: str,
    k: int = 4,
) -> list[tuple]:
    """
    Retrieve FAQ documents along with their similarity scores.

    Chroma returns a distance score where lower values indicate
    greater similarity.
    """

    vectorstore = get_faq_vectorstore()

    results = vectorstore.similarity_search_with_score(
        query,
        k=k,
    )

    return results


def get_faq_retriever():
    """
    Return the standard FAQ retriever.
    """

    vectorstore = get_faq_vectorstore()

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 4,
        },
    )