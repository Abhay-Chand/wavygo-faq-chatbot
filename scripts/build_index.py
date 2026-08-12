from app.rag.ingest import (
    load_faq_documents,
    split_documents,
)

from app.rag.embeddings import get_embeddings
from app.rag.vectorstore import get_vectorstore



def build_index():
    print("Loading FAQ documents...")

    documents = load_faq_documents()

    print(f"Loaded {len(documents)} FAQ documents.")

    chunks = split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    vectorstore = get_vectorstore()

    print("Creating embeddings and storing documents...")

    vectorstore.add_documents(
        documents=chunks
    )

    print("FAQ vector database created successfully.")


if __name__ == "__main__":
    build_index()