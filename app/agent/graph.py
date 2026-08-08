"""
LangGraph agent that powers the AI chat assistant.
Uses xAI Grok as the LLM backbone with tool-calling capability.
"""
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from sqlalchemy.orm import Session
from app.config import get_settings
from app.agent.tools import _get_tools

settings = get_settings()

SYSTEM_PROMPT = """You are an AI Personal Finance Advisor. You help users understand their spending, 
manage budgets, and make smarter financial decisions.

You have access to tools that can query the user's actual financial data:
- get_spending_summary: Get income/expense/balance breakdown, optionally for a specific month (YYYY-MM)
- get_budget_status: Check budget limits vs actual spending for a period (YYYY-MM)
- get_recent_transactions: View the latest transactions
- get_anomalies: Find unusual/suspicious transactions

Always use these tools to answer questions about the user's finances rather than making assumptions.
When giving advice, be specific and reference actual numbers from their data.
Be conversational, helpful, and proactive in suggesting ways to save money.
Use Indian Rupee (₹) for currency formatting.
Keep responses concise but informative."""


# In-memory conversation store keyed by session_id
_conversation_store: dict[str, list[BaseMessage]] = {}


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda x, y: list(x) + list(y)]


def _should_continue(state: AgentState) -> str:
    """Determines whether the agent should call a tool or end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def create_agent(db: Session, user_id: int):
    """
    Creates a LangGraph agent instance bound to a user's DB session.
    Returns a compiled graph that can be invoked with messages.
    """
    api_key = settings.xai_api_key
    if not api_key:
        return None

    tools = _get_tools(db, user_id)

    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
        temperature=0.3,
    )
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: AgentState):
        messages = list(state["messages"])
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", _should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


def chat_with_agent(
    db: Session,
    user_id: int,
    user_message: str,
    session_id: str,
) -> tuple[str, str, list[dict] | None]:
    """
    Main entry point for chat. Manages conversation memory and invokes the agent.
    Returns (reply_text, session_id, tool_calls_info).
    """
    # Generate session_id if not provided
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())

    # Get or create conversation history
    if session_id not in _conversation_store:
        _conversation_store[session_id] = [SystemMessage(content=SYSTEM_PROMPT)]

    history = _conversation_store[session_id]

    # Retrieve relevant knowledge via RAG
    from app.rag.retriever import retrieve
    rag_docs = retrieve(user_message, k=2)
    if rag_docs:
        rag_context = "\n\n".join(
            [f"[{d['title']}]: {d['content']}" for d in rag_docs]
        )
        augmented_message = (
            f"{user_message}\n\n"
            f"---\nRelevant financial knowledge (use this if helpful):\n{rag_context}"
        )
    else:
        augmented_message = user_message

    history.append(HumanMessage(content=augmented_message))

    agent = create_agent(db, user_id)
    if agent is None:
        reply = (
            "The AI chat feature requires a Groq API key. "
            "Please set XAI_API_KEY in your .env file."
        )
        history.append(AIMessage(content=reply))
        return reply, session_id, None

    # Invoke the agent graph
    result = agent.invoke({"messages": history})

    # Extract the final AI response
    final_messages = result["messages"]
    ai_response = final_messages[-1]
    reply_text = ai_response.content

    # Record tool calls for transparency
    tool_calls_info = []
    for msg in final_messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls_info.append({
                    "name": tc["name"],
                    "args": tc["args"],
                })

    # Update conversation memory
    _conversation_store[session_id] = list(final_messages)

    return reply_text, session_id, tool_calls_info or None
