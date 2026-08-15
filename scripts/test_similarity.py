from app.rag.retriever import get_faq_retriever


retriever = get_faq_retriever()


TEST_QUESTIONS = [
    # Exact / near-exact FAQ
    "How do I book a ride?",
    "How can I cancel my ride?",

    # Hinglish
    "Bike rent kaise karu?",
    "Scooty kaise book hoti hai?",
    "Mere area ke paas bike available hai?",
    "Kal Activa mil jayegi kya?",
    "Bike lene ke liye license chahiye?",
    "Aadhaar dena padega kya?",
    "Learner license hai, bike mil sakti hai?",
    "Bike hotel pe deliver ho sakti hai?",
    "Bike kaha return karni hogi?",
    "Petrol ka paisa kaun dega?",
    "Helmet milega kya?",
    "Pickup pe bike damaged mili toh kya karu?",
    "Bike raste mein kharab ho gayi, kya karu?",
    "Bike se accident ho gaya toh kya karna hai?",
    "Booking cancel karne par refund milega?",
    "Payment cut gaya lekin booking confirm nahi hui.",
    "Paisa do baar cut gaya.",
    "Booking confirm hui hai ya nahi kaise check karu?",
    "Sabse sasti scooty kaunsi hai?",
    "Ek week ke rent pe discount milega?",
    "Vendor bike dene se mana kar raha hai.",
    "Mujhe support se baat karni hai.",

    # English paraphrases
    "Can I rent a scooter near my location?",
    "Do I need a driving licence to rent a bike?",
    "Can I get the bike delivered to my hotel?",
    "What should I do if the rental bike breaks down?",
    "I was charged twice for the booking.",

    # Out-of-scope
    "What is the weather today?",
    "Who is the president of the United States?",
    "How do I learn Python?",
]


for question in TEST_QUESTIONS:

    print("\n" + "=" * 70)
    print(f"QUESTION: {question}")
    print("=" * 70)

    results = retriever.invoke(question)

    if not results:
        print("NO RESULTS")
        continue

    for i, document in enumerate(results, start=1):

        print(f"\nResult {i}")

        print(
            "Content:",
            document.page_content
        )

        print(
            "Metadata:",
            document.metadata
        )