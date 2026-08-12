from app.rag.retriever import get_faq_retriever


def test_retrieval():
    retriever = get_faq_retriever()

    question = "Can I cancel my ride?"

    documents = retriever.invoke(question)

    print("\nUSER QUESTION:")
    print(question)

    print("\nRETRIEVED DOCUMENTS:")
    
    for index, document in enumerate(documents, start=1):
        print(f"\n--- Result {index} ---")
        print(document.page_content)
        print("Metadata:", document.metadata)


if __name__ == "__main__":
    test_retrieval()