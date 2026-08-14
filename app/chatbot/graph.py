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
    """
    Build and compile the WavyGo FAQ chatbot LangGraph.
    """

    builder = StateGraph(ChatState)

    # Nodes
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

    # Entry point
    builder.add_edge(
        START,
        "classify",
    )

    # Classification routing
    builder.add_conditional_edges(
        "classify",
        route_after_classification,
        {
            "normal": "normal_response",
            "faq": "retrieve_faq",
            "out_of_scope": "fallback",
        },
    )

    # FAQ retrieval
    builder.add_edge(
        "retrieve_faq",
        "relevance_check",
    )

    # Relevance routing
    builder.add_conditional_edges(
        "relevance_check",
        route_after_retrieval,
        {
            "answer": "fallback",
            "fallback": "fallback",
        },
    )

    # Terminal nodes
    builder.add_edge(
        "normal_response",
        END,
    )

    builder.add_edge(
        "fallback",
        END,
    )

    return builder.compile()


chatbot_graph = build_chatbot_graph()