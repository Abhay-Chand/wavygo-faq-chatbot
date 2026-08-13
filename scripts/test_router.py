from app.chatbot.router import classify_query


test_messages = [
    "Hi",
    "Hello",
    "Thanks",
    "How do I cancel my ride?",
    "What payment methods do you support?",
    "What is the weather today?",
]


for message in test_messages:
    result = classify_query(message)

    print(
        f"Message: {message}\n"
        f"Route:   {result}\n"
        f"{'-' * 40}"
    )