from langgraph.graph import StateGraph, START, END

from app.chatbot.state import ChatState

from app.chatbot.nodes import (
    classify_node,
    normal_response_node,
    retrieve_faq_node,
    relevance_node,
    generate_answer_node,
)

from app.chatbot.fallback import fallback_node

from app.chatbot.router import (
    route_after_classification,
    route_after_retrieval,
)


def build_chatbot_graph():

    builder = StateGraph(ChatState)

    # -------------------------
    # Nodes
    # -------------------------

    builder.add_node(
        "classify",
        classify_node,
    )

    builder.add_node(
        "normal_response",
        normal_response_node,
    )

    builder.add_node(
        "retrieve_faq",
        retrieve_faq_node,
    )

    builder.add_node(
        "relevance_check",
        relevance_node,
    )

    builder.add_node(
        "generate_answer",
        generate_answer_node,
    )

    builder.add_node(
        "fallback",
        fallback_node,
    )

    # -------------------------
    # Start
    # -------------------------

    builder.add_edge(
        START,
        "classify",
    )

    # -------------------------
    # Classification
    # -------------------------

    builder.add_conditional_edges(
        "classify",
        route_after_classification,
        {
            "normal": "normal_response",
            "faq": "retrieve_faq",
            "out_of_scope": "fallback",
        },
    )

    # -------------------------
    # Retrieval
    # -------------------------

    builder.add_edge(
        "retrieve_faq",
        "relevance_check",
    )

    # -------------------------
    # Relevance
    # -------------------------

    builder.add_conditional_edges(
        "relevance_check",
        route_after_retrieval,
        {
            "answer": "generate_answer",
            "fallback": "fallback",
        },
    )

    # -------------------------
    # End
    # -------------------------

    builder.add_edge(
        "normal_response",
        END,
    )

    builder.add_edge(
        "generate_answer",
        END,
    )

    builder.add_edge(
        "fallback",
        END,
    )

    return builder.compile()


chatbot_graph = build_chatbot_graph()