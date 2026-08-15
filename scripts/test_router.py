from app.chatbot.router import classify_query


test_messages = [
    "Hi",
    "Hello",
    "Thanks",
    "How can I cancel my ride?",
    "Can I cancel a booking?",
    "How do I book a ride?",
    "What payment methods do you accept?",
    "What is the weather today?",
    "Who is the president of the United States?",
    "Write me a Python program",
]


for message in test_messages:

    result = classify_query(message)

    print(
        f"Message: {message}\n"
        f"Route:   {result}\n"
        f"{'-' * 50}"
    )