import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


FAQ_PATH = Path("data/faq/faq.json")


def load_faq_documents() -> list[Document]:
    """
    Load FAQ data and convert each FAQ into a LangChain Document.
    """

    with open(FAQ_PATH, "r", encoding="utf-8") as file:
        faq_data = json.load(file)

    documents = []

    for faq in faq_data:
        content = (
            f"Question: {faq['question']}\n"
            f"Answer: {faq['answer']}"
        )

        metadata = {
            "faq_id": faq["id"],
            "category": faq.get("category", "general"),
            "source": "faq"
        }

        documents.append(
            Document(
                page_content=content,
                metadata=metadata
            )
        )

    return documents


def split_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Split FAQ documents into chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    return splitter.split_documents(documents)