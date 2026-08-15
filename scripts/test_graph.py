from app.chatbot.graph import chatbot_graph


TEST_MESSAGES = [
    "Hi",
    "Hello",
    "How can I cancel my ride?",
    "Can I cancel a booking?",
    "How do I book a ride?",
    "What is the weather today?",
    "Who is the president of the United States?",
]


for message in TEST_MESSAGES:

    print("\n" + "=" * 70)
    print(f"USER: {message}")
    print("=" * 70)

    result = chatbot_graph.invoke(
        {
            "user_message": message,
        }
    )

    print("Intent:", result.get("intent"))
    print("Relevance Score:", result.get("relevance_score"))
    print("Context Relevant:", result.get("context_relevant"))
    print("Contact Support:", result.get("contact_support"))

    print("\nANSWER:")
    print(result.get("answer"))