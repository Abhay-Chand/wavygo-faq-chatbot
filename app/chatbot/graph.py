from langgraph.graph import StateGraph, START, END

print("LangGraph imported successfully")

builder = StateGraph(dict)

builder.add_node("test", lambda state: state)

builder.add_edge(START, "test")
builder.add_edge("test", END)

graph = builder.compile()

print("LangGraph workflow compiled successfully")