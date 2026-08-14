from app.rag.retriever import retrieve_faq_with_scores


test_questions = [
    "How can I cancel my ride?",
    "Can I cancel a booking?",
    "What payment methods do you accept?",
    "How do I book a ride?",
    "What is the weather today?",
    "Who is the president of the United States?",
]


for question in test_questions:

    print("\n" + "=" * 60)
    print(f"QUESTION: {question}")
    print("=" * 60)

    results = retrieve_faq_with_scores(question)

    for index, (document, score) in enumerate(results, start=1):

        print(f"\nResult {index}")
        print(f"Score: {score}")
        print(f"Content: {document.page_content}")
        print(f"Metadata: {document.metadata}")