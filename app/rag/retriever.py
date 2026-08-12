from langchain_chroma import Chroma

from app.rag.vectorstore import get_vectorstore


def get_faq_retriever():
    """
    Create a retriever for the WavyGo FAQ knowledge base.
    """

    vectorstore: Chroma = get_vectorstore()

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 4
        }
    )