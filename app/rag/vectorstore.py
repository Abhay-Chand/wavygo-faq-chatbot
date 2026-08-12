import os

from dotenv import load_dotenv
from langchain_chroma import Chroma

from app.rag.embeddings import get_embeddings


load_dotenv()


def get_vectorstore() -> Chroma:
    """
    Return the persistent Chroma vector store.
    """

    persist_directory = os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        "./chroma_db"
    )

    return Chroma(
        collection_name="wavygo_faq",
        embedding_function=get_embeddings(),
        persist_directory=persist_directory,
    )