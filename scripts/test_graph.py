from app.chatbot.graph import chatbot_graph


test_messages = [
    "Hi",
    "How can I cancel my ride?",
    "Can I cancel a booking?",
    "What is the weather today?",
]


for message in test_messages:

    print("\n" + "=" * 60)
    print(f"USER: {message}")
    print("=" * 60)

    result = chatbot_graph.invoke(
        {
            "user_message": message
        }
    )

    print("Intent:", result.get("intent"))
    print("Score:", result.get("relevance_score"))
    print("Relevant:", result.get("context_relevant"))
    print("Answer:", result.get("answer"))
    print("Contact Support:", result.get("contact_support"))