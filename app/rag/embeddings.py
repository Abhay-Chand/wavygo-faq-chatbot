import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings


load_dotenv()


def get_embeddings() -> OpenAIEmbeddings:
    """
    Create and return the embedding model used by the FAQ RAG system.
    """

    model_name = os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small"
    )

    return OpenAIEmbeddings(
        model=model_name
    )