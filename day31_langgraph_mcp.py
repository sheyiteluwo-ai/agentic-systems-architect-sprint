"""
Day 31 — LangGraph + MCP Integration
42-Day Agentic AI Sprint — Sheyi Teluwo

What we build today:
  - A LangGraph state machine that ORCHESTRATES your Day 30 MCP tools
  - 5 nodes: route → tool_call → validate → respond → end
  - Conditional edges: query type decides which MCP tool to call
  - State object tracks the full conversation + tool results
  - HITL checkpoint: low-confidence answers pause for human review

Run:
    python day31_langgraph_mcp.py
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Literal

# ─────────────────────────────────────────────
# 0.  DEPENDENCY CHECK
# ─────────────────────────────────────────────
def check_dependencies():
    missing = []
    for pkg, import_name in [
        ("langgraph", "langgraph"),
        ("langchain_openai", "langchain_openai"),
        ("yfinance", "yfinance"),
        ("ddgs", "ddgs"),
        ("chromadb", "chromadb"),
        ("openai", "openai"),
    ]:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("\n❌  Missing packages. Run:\n")
        print(f"    pip install {' '.join(missing)}\n")
        sys.exit(1)
    print("✅  All dependencies present.")

check_dependencies()

# ─────────────────────────────────────────────
# 1.  IMPORTS
# ─────────────────────────────────────────────
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import yfinance as yf
from ddgs import DDGS
import chromadb
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌  OPENAI_API_KEY not found in .env")
    sys.exit(1)

llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY, temperature=0)

# ─────────────────────────────────────────────
# 2.  STATE DEFINITION
#     This is the "memory" that flows through every node.
#     Every node reads from it and writes back to it.
# ─────────────────────────────────────────────

class AgentState(TypedDict):
    """
    The state object that travels through every node in the graph.
    Think of it like a clipboard that every worker reads and updates.
    """
    # The original user query
    query: str

    # Which tool the router decided to use
    # Options: "finance", "news", "fca_docs", "multi", "unknown"
    route: str

    # Raw results from MCP tool calls
    tool_results: list[dict]

    # The final answer text
    final_answer: str

    # Confidence score 0.0-1.0 — triggers HITL if below 0.7
    confidence: float

    # Whether a human needs to review this answer
    requires_human_review: bool

    # Human feedback if review was triggered
    human_feedback: str

    # Full trace of what happened at each node (for debugging)
    trace: Annotated[list[str], operator.add]


# ─────────────────────────────────────────────
# 3.  MCP TOOLS  (same as Day 30, trimmed for reuse)
# ─────────────────────────────────────────────

def mcp_finance_tool(ticker: str) -> dict:
    print(f"    📈  [MCP FinanceTool] ticker={ticker}")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
        currency = info.get("currency", "USD")
        market_cap = info.get("marketCap", "N/A")
        company_name = info.get("longName") or info.get("shortName", ticker)
        pe_ratio = info.get("trailingPE", "N/A")
        if isinstance(market_cap, (int, float)):
            mc_str = f"£{market_cap/1e9:.1f}B" if ".L" in ticker else f"${market_cap/1e9:.1f}B"
        else:
            mc_str = "N/A"
        return {
            "status": "success", "ticker": ticker, "company": company_name,
            "price": f"{price} {currency}", "market_cap": mc_str,
            "pe_ratio": round(pe_ratio, 2) if isinstance(pe_ratio, float) else pe_ratio
        }
    except Exception as e:
        return {"status": "error", "ticker": ticker, "error": str(e)}


def mcp_news_tool(query: str, max_results: int = 5) -> dict:
    print(f"    📰  [MCP NewsTool] query='{query}'")
    try:
        articles = []
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                articles.append({
                    "title": r.get("title", ""),
                    "source": r.get("source", ""),
                    "snippet": r.get("body", "")[:200],
                    "date": r.get("date", "")
                })
        return {"status": "success", "query": query, "articles": articles}
    except Exception as e:
        return {"status": "error", "query": query, "error": str(e)}


def mcp_fca_tool(query: str, n_results: int = 3) -> dict:
    print(f"    📚  [MCP FCADocTool] query='{query}'")
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collections = [c.name for c in client.list_collections()]
        fca_cols = [c for c in collections if "fca" in c.lower()]
        col_name = fca_cols[0] if fca_cols else (collections[0] if collections else None)
        if not col_name:
            return {"status": "no_db", "message": "ChromaDB not found — run from project root"}
        col = client.get_collection(col_name)
        results = col.query(query_texts=[query], n_results=min(n_results, col.count()))
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            chunks.append({
                "content": doc[:300] + "..." if len(doc) > 300 else doc,
                "source": meta.get("source", "FCA doc"),
                "relevance": round(1 - dist, 3)
            })
        return {"status": "success", "query": query, "chunks": chunks}
    except Exception as e:
        return {"status": "error", "query": query, "error": str(e)}


# ─────────────────────────────────────────────
# 4.  LANGGRAPH NODES
#     Each function = one node in the graph.
#     Every function receives state, returns a dict of updates.
# ─────────────────────────────────────────────

def node_router(state: AgentState) -> dict:
    """
    NODE 1 — ROUTER
    Reads the user query and decides which MCP tool to use.
    Uses GPT-4o to classify the query type.
    """
    print("\n  🔀  [Node: router] Classifying query...")

    query = state["query"]

    classification_prompt = f"""
You are a query classifier for a UK financial services AI agent.

Classify this query into ONE of these categories:
- finance     : asks about stock prices, market data, company financials
- news        : asks about recent news, events, announcements
- fca_docs    : asks about FCA regulations, compliance, regulatory rules
- multi       : needs BOTH news AND fca_docs (regulatory news questions)
- unknown     : cannot be answered by any available tool

Query: "{query}"

Respond with ONLY the category word. Nothing else.
"""
    response = llm.invoke([HumanMessage(content=classification_prompt)])
    route = response.content.strip().lower()

    # Sanitise — must be one of our valid routes
    valid_routes = ["finance", "news", "fca_docs", "multi", "unknown"]
    if route not in valid_routes:
        route = "unknown"

    print(f"    ✅  Routed to: '{route}'")

    return {
        "route": route,
        "trace": [f"[router] Query classified as: {route}"]
    }


def node_tool_call(state: AgentState) -> dict:
    """
    NODE 2 — TOOL CALL
    Calls the correct MCP tool(s) based on the route.
    """
    print(f"\n  🛠️   [Node: tool_call] Executing MCP tool for route='{state['route']}'")

    query = state["query"]
    route = state["route"]
    results = []

    if route == "finance":
        # Extract ticker from query using LLM
        ticker_prompt = f"""
Extract the stock ticker symbol from this query. 
For UK stocks add .L suffix (Barclays=BARC.L, Lloyds=LLOY.L, HSBC=HSBA.L, NatWest=NWG.L).
For US stocks use standard ticker (Apple=AAPL, Microsoft=MSFT).
Query: "{query}"
Respond with ONLY the ticker symbol. Nothing else.
"""
        ticker_response = llm.invoke([HumanMessage(content=ticker_prompt)])
        ticker = ticker_response.content.strip().upper()
        result = mcp_finance_tool(ticker)
        results.append({"tool": "finance", "data": result})

    elif route == "news":
        result = mcp_news_tool(query)
        results.append({"tool": "news", "data": result})

    elif route == "fca_docs":
        result = mcp_fca_tool(query)
        results.append({"tool": "fca_docs", "data": result})

    elif route == "multi":
        # Call both news AND fca_docs
        news_result = mcp_news_tool(query)
        fca_result = mcp_fca_tool(query)
        results.append({"tool": "news", "data": news_result})
        results.append({"tool": "fca_docs", "data": fca_result})

    else:
        results.append({
            "tool": "none",
            "data": {"status": "unknown", "message": "No suitable tool found for this query."}
        })

    print(f"    ✅  Tool call(s) complete. Results: {len(results)}")

    return {
        "tool_results": results,
        "trace": [f"[tool_call] Called {len(results)} tool(s) for route={route}"]
    }


def node_validate(state: AgentState) -> dict:
    """
    NODE 3 — VALIDATE
    Checks the tool results quality.
    Sets confidence score and flags for human review if needed.
    """
    print("\n  🔍  [Node: validate] Checking result quality...")

    results = state["tool_results"]
    confidence = 1.0
    issues = []

    for r in results:
        data = r.get("data", {})
        status = data.get("status", "")

        if status == "error":
            confidence -= 0.4
            issues.append(f"Tool '{r['tool']}' returned an error: {data.get('error', 'unknown')}")

        elif status == "no_db":
            confidence -= 0.3
            issues.append("FCA ChromaDB not available — answer will use LLM knowledge only")

        elif status == "no_results":
            confidence -= 0.2
            issues.append(f"Tool '{r['tool']}' returned no results")

        elif status == "success":
            # Check for empty results
            if r["tool"] == "news" and not data.get("articles"):
                confidence -= 0.2
                issues.append("News tool returned empty article list")
            elif r["tool"] == "fca_docs" and not data.get("chunks"):
                confidence -= 0.2
                issues.append("FCA tool returned no document chunks")

    confidence = max(0.0, round(confidence, 2))
    requires_review = confidence < 0.7

    if issues:
        print(f"    ⚠️   Issues found: {issues}")
    print(f"    ✅  Confidence: {confidence} | Requires review: {requires_review}")

    return {
        "confidence": confidence,
        "requires_human_review": requires_review,
        "trace": [f"[validate] confidence={confidence}, issues={issues}, review={requires_review}"]
    }


def node_human_review(state: AgentState) -> dict:
    """
    NODE 4 — HUMAN IN THE LOOP (HITL)
    Only reached if confidence < 0.7.
    Pauses and asks a human to approve or provide feedback.
    """
    print("\n  👤  [Node: human_review] LOW CONFIDENCE — Human review required")
    print(f"      Confidence score: {state['confidence']}")
    print(f"      Query: {state['query']}")
    print("\n" + "─"*50)
    print("  HITL GATE — Please review:")
    print("  1. Type APPROVE to proceed with LLM-only answer")
    print("  2. Type your correction/feedback to improve the answer")
    print("─"*50)

    feedback = input("  Your decision: ").strip()

    if feedback.upper() == "APPROVE" or feedback == "":
        feedback = "APPROVED — proceed with best available answer"

    print(f"    ✅  Human feedback recorded: '{feedback}'")

    return {
        "human_feedback": feedback,
        "trace": [f"[human_review] feedback='{feedback}'"]
    }


def node_respond(state: AgentState) -> dict:
    """
    NODE 5 — RESPOND
    Uses GPT-4o to synthesise tool results into a final answer.
    """
    print("\n  💬  [Node: respond] Generating final answer...")

    query = state["query"]
    results = state["tool_results"]
    feedback = state.get("human_feedback", "")
    confidence = state["confidence"]

    # Build context from tool results
    context_parts = []
    for r in results:
        tool_name = r["tool"]
        data = r["data"]
        context_parts.append(f"--- {tool_name.upper()} TOOL RESULT ---\n{json.dumps(data, indent=2, default=str)}")

    context = "\n\n".join(context_parts)

    human_note = ""
    if feedback:
        human_note = f"\n\nHuman reviewer note: {feedback}"

    confidence_note = ""
    if confidence < 0.7:
        confidence_note = "\n\nNote: Some data sources were unavailable. Supplement with your own knowledge where appropriate."

    system_prompt = (
        "You are an expert AI assistant specialising in UK financial services. "
        "Use the tool results below to answer the user's question clearly and accurately. "
        "Structure your answer with clear sections. Be specific, use the data provided."
    )

    user_prompt = f"""
User question: {query}

Tool results:
{context}
{human_note}
{confidence_note}

Please provide a clear, structured answer based on the tool results above.
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    final_answer = response.content
    print(f"    ✅  Answer generated ({len(final_answer)} chars)")

    return {
        "final_answer": final_answer,
        "trace": [f"[respond] Generated answer with confidence={confidence}"]
    }


# ─────────────────────────────────────────────
# 5.  CONDITIONAL EDGE FUNCTION
#     LangGraph calls this after node_validate
#     to decide: go to human_review OR go straight to respond
# ─────────────────────────────────────────────

def should_review(state: AgentState) -> Literal["human_review", "respond"]:
    """
    Routing function after validation.
    If confidence < 0.7 → human_review node
    Otherwise → respond node directly
    """
    if state.get("requires_human_review", False):
        print("    ⚠️   Low confidence — routing to HITL gate")
        return "human_review"
    else:
        print("    ✅  High confidence — routing directly to respond")
        return "respond"


# ─────────────────────────────────────────────
# 6.  BUILD THE LANGGRAPH STATE MACHINE
# ─────────────────────────────────────────────

def build_graph() -> StateGraph:
    """
    Assembles the LangGraph state machine.

    Graph structure:
        router → tool_call → validate → [conditional] → respond → END
                                              ↓
                                       human_review → respond → END
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", node_router)
    graph.add_node("tool_call", node_tool_call)
    graph.add_node("validate", node_validate)
    graph.add_node("human_review", node_human_review)
    graph.add_node("respond", node_respond)

    # Add edges (the arrows between nodes)
    graph.set_entry_point("router")
    graph.add_edge("router", "tool_call")
    graph.add_edge("tool_call", "validate")

    # Conditional edge — validate decides the next node
    graph.add_conditional_edges(
        "validate",
        should_review,
        {
            "human_review": "human_review",
            "respond": "respond"
        }
    )

    graph.add_edge("human_review", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


# ─────────────────────────────────────────────
# 7.  DEMO SCENARIOS
# ─────────────────────────────────────────────

def run_query(app, query: str, scenario_name: str):
    """Run a single query through the full LangGraph pipeline."""
    print(f"\n\n{'▓'*60}")
    print(f"  SCENARIO: {scenario_name}")
    print(f"  QUERY: {query}")
    print(f"{'▓'*60}")

    initial_state: AgentState = {
        "query": query,
        "route": "",
        "tool_results": [],
        "final_answer": "",
        "confidence": 1.0,
        "requires_human_review": False,
        "human_feedback": "",
        "trace": [f"[start] Query received: {query}"]
    }

    result = app.invoke(initial_state)

    print(f"\n{'─'*60}")
    print("FINAL ANSWER:")
    print(f"{'─'*60}")
    print(result["final_answer"])

    print(f"\n{'─'*60}")
    print("TRACE:")
    for step in result["trace"]:
        print(f"  → {step}")

    print(f"\nConfidence: {result['confidence']}")
    print(f"Route used: {result['route']}")
    print(f"Tools called: {[r['tool'] for r in result['tool_results']]}")

    return result


def run_demo():
    print("\n" + "█"*60)
    print("  DAY 31 — LANGGRAPH + MCP INTEGRATION")
    print("  42-Day Agentic AI Sprint — Sheyi Teluwo")
    print("█"*60)

    print("\n🔧  Building LangGraph state machine...")
    app = build_graph()
    print("✅  Graph compiled. Nodes: router → tool_call → validate → respond")

    # ── SCENARIO 1: Finance route ──────────────────────────────
    run_query(
        app,
        query="What is the current share price of HSBC?",
        scenario_name="Finance Route — HSBC Stock Price"
    )

    # ── SCENARIO 2: FCA docs route ─────────────────────────────
    run_query(
        app,
        query="What are the FCA rules on financial promotions?",
        scenario_name="FCA Docs Route — Financial Promotions"
    )

    # ── SCENARIO 3: Multi-tool route ───────────────────────────
    run_query(
        app,
        query="What does the FCA say about AI in financial services and what is the latest news?",
        scenario_name="Multi-Tool Route — FCA AI Regulation + News"
    )

    # ── SUMMARY ───────────────────────────────────────────────
    print("\n\n" + "█"*60)
    print("  DAY 31 COMPLETE ✅")
    print("█"*60)
    print("\nLangGraph state machine:")
    print("  ✅  5 nodes: router, tool_call, validate, human_review, respond")
    print("  ✅  Conditional edge: validate → HITL or respond")
    print("  ✅  3 MCP tools wired in: finance, news, fca_docs")
    print("  ✅  Confidence scoring on every response")
    print("  ✅  HITL gate triggers at confidence < 0.7")
    print("  ✅  Full trace logged at every node")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📸  SCREENSHOT THIS OUTPUT — save as:")
    print("    day31_langgraph_mcp_2026-05-21.png")
    print("█"*60)


if __name__ == "__main__":
    run_demo()
