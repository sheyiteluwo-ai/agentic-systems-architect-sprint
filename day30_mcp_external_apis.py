"""
Day 30 — MCP Tools: External APIs
42-Day Agentic AI Sprint — Sheyi Teluwo

What we build today:
  - MCP Server with 3 REAL external API tools:
      1. Finance Tool   → yfinance (live stock/market data, no API key needed)
      2. News Tool      → DuckDuckGo (live news search)
      3. FCA Doc Tool   → ChromaDB (reuses your Phase 1 vector store)
  - MCP Client agent loop that calls all 3 tools
  - Structured JSON responses from every tool
  - Full error handling on every external call

Run:
    python day30_mcp_external_apis.py
"""

import json
import os
import sys
from datetime import datetime
from typing import Any

# ─────────────────────────────────────────────
# 0.  DEPENDENCY CHECK
#     Tells you exactly what to pip-install if anything is missing
# ─────────────────────────────────────────────
def check_dependencies():
    missing = []
    try:
        import yfinance  # noqa: F401
    except ImportError:
        missing.append("yfinance")
    try:
        from ddgs import DDGS  # noqa: F401
    except ImportError:
        missing.append("ddgs")
    try:
        import chromadb  # noqa: F401
    except ImportError:
        missing.append("chromadb")
    try:
        import openai  # noqa: F401
    except ImportError:
        missing.append("openai")
    if missing:
        print("\n❌  Missing packages. Run this command first:\n")
        print(f"    pip install {' '.join(missing)}\n")
        sys.exit(1)
    print("✅  All dependencies present.")

check_dependencies()

# ─────────────────────────────────────────────
# 1.  IMPORTS  (after dependency check passes)
# ─────────────────────────────────────────────
import yfinance as yf
from ddgs import DDGS
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌  OPENAI_API_KEY not found in .env — check your .env file.")
    sys.exit(1)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ─────────────────────────────────────────────
# 2.  MCP TOOL DEFINITIONS
#     Each tool is a plain Python class with:
#       - name       : what the LLM calls it
#       - description: what the LLM reads to decide when to use it
#       - parameters : JSON Schema the LLM fills in
#       - execute()  : the real work
# ─────────────────────────────────────────────

class FinanceTool:
    """
    Tool 1 — Finance Data
    Fetches live stock price + key fundamentals using yfinance.
    Works for any ticker: AAPL, LLOY.L (Lloyds), BARC.L (Barclays), etc.
    """
    name = "get_stock_data"
    description = (
        "Fetch live stock price and key financial data for a company. "
        "Use this when the user asks about share prices, market cap, P/E ratio, "
        "or any financial metric for a publicly listed company. "
        "For UK stocks add '.L' to the ticker, e.g. BARC.L for Barclays."
    )
    parameters = {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": (
                    "Stock ticker symbol. UK stocks end in .L "
                    "(e.g. BARC.L, LLOY.L, HSBA.L). US stocks: AAPL, MSFT, GOOGL."
                )
            }
        },
        "required": ["ticker"]
    }

    def execute(self, ticker: str) -> dict[str, Any]:
        print(f"\n  📈  [FinanceTool] Fetching data for ticker: {ticker}")
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Pull the fields we care about — with safe .get() defaults
            price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
            currency = info.get("currency", "USD")
            market_cap = info.get("marketCap", "N/A")
            pe_ratio = info.get("trailingPE", "N/A")
            company_name = info.get("longName") or info.get("shortName", ticker)
            sector = info.get("sector", "N/A")
            country = info.get("country", "N/A")
            fifty_two_week_high = info.get("fiftyTwoWeekHigh", "N/A")
            fifty_two_week_low = info.get("fiftyTwoWeekLow", "N/A")

            # Format market cap nicely (billions)
            if isinstance(market_cap, (int, float)) and market_cap != "N/A":
                market_cap_bn = f"£{market_cap / 1e9:.1f}B" if "L" in ticker else f"${market_cap / 1e9:.1f}B"
            else:
                market_cap_bn = "N/A"

            result = {
                "status": "success",
                "ticker": ticker,
                "company_name": company_name,
                "sector": sector,
                "country": country,
                "current_price": f"{price} {currency}" if price != "N/A" else "N/A",
                "market_cap": market_cap_bn,
                "pe_ratio": round(pe_ratio, 2) if isinstance(pe_ratio, float) else pe_ratio,
                "52_week_high": f"{fifty_two_week_high} {currency}" if fifty_two_week_high != "N/A" else "N/A",
                "52_week_low": f"{fifty_two_week_low} {currency}" if fifty_two_week_low != "N/A" else "N/A",
                "retrieved_at": datetime.now().isoformat()
            }
            print(f"  ✅  Got data for {company_name}: {result['current_price']}")
            return result

        except Exception as e:
            print(f"  ❌  FinanceTool error: {e}")
            return {
                "status": "error",
                "ticker": ticker,
                "error": str(e),
                "hint": "Check the ticker symbol. UK stocks need .L suffix (e.g. BARC.L)"
            }


class NewsTool:
    """
    Tool 2 — News Search
    Searches for recent news articles using DuckDuckGo.
    Returns the 5 most relevant headlines + snippets.
    """
    name = "search_news"
    description = (
        "Search for recent news articles about a topic, company, or event. "
        "Use this when the user asks about recent developments, announcements, "
        "regulatory news, or anything that might have happened recently."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The news search query. Be specific for better results."
            },
            "max_results": {
                "type": "integer",
                "description": "Number of news results to return. Default 5, max 10.",
                "default": 5
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, max_results: int = 5) -> dict[str, Any]:
        print(f"\n  📰  [NewsTool] Searching news for: '{query}'")
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.news(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", "No title"),
                        "source": r.get("source", "Unknown"),
                        "published": r.get("date", "Unknown date"),
                        "snippet": r.get("body", "No snippet available"),
                        "url": r.get("url", "")
                    })

            if not results:
                return {
                    "status": "no_results",
                    "query": query,
                    "message": "No news articles found for this query."
                }

            print(f"  ✅  Found {len(results)} news articles.")
            return {
                "status": "success",
                "query": query,
                "article_count": len(results),
                "articles": results,
                "retrieved_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"  ❌  NewsTool error: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e)
            }


class FCADocTool:
    """
    Tool 3 — FCA Document Retrieval
    Queries YOUR Phase 1 ChromaDB vector store (494 FCA chunks).
    If the Phase 1 DB is not found, falls back to a helpful message.
    """
    name = "search_fca_documents"
    description = (
        "Search the FCA (Financial Conduct Authority) regulatory document database. "
        "Use this when the user asks about FCA rules, regulations, compliance requirements, "
        "consumer duty, financial promotions, or any UK financial regulation topic."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The regulatory question or topic to search for in FCA documents."
            },
            "n_results": {
                "type": "integer",
                "description": "Number of document chunks to retrieve. Default 3.",
                "default": 3
            }
        },
        "required": ["query"]
    }

    # Path to Phase 1 ChromaDB — adjust if yours is in a different location
    CHROMA_PATH = "./chroma_db"
    COLLECTION_NAME = "fca_documents"

    def execute(self, query: str, n_results: int = 3) -> dict[str, Any]:
        print(f"\n  📚  [FCADocTool] Searching FCA docs for: '{query}'")
        try:
            chroma_client = chromadb.PersistentClient(path=self.CHROMA_PATH)

            # List collections to check what's available
            collections = [c.name for c in chroma_client.list_collections()]
            print(f"       Available ChromaDB collections: {collections}")

            if self.COLLECTION_NAME not in collections:
                # Try to find any collection with 'fca' in the name
                fca_collections = [c for c in collections if "fca" in c.lower()]
                if fca_collections:
                    collection_name = fca_collections[0]
                    print(f"       Using collection: {collection_name}")
                elif collections:
                    collection_name = collections[0]
                    print(f"       FCA collection not found — using: {collection_name}")
                else:
                    return {
                        "status": "no_database",
                        "message": (
                            "Phase 1 ChromaDB not found at ./chroma_db. "
                            "Make sure you run this from your project root directory "
                            "where Phase 1 files are stored."
                        ),
                        "hint": "Run: cd path/to/your/sprint/project then try again."
                    }
            else:
                collection_name = self.COLLECTION_NAME

            collection = chroma_client.get_collection(collection_name)
            results = collection.query(
                query_texts=[query],
                n_results=min(n_results, collection.count())
            )

            chunks = []
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
                chunks.append({
                    "rank": i + 1,
                    "content": doc[:400] + "..." if len(doc) > 400 else doc,
                    "source": meta.get("source", meta.get("filename", "FCA document")),
                    "relevance_score": round(1 - dist, 3)  # convert distance to similarity
                })

            print(f"  ✅  Retrieved {len(chunks)} FCA document chunks.")
            return {
                "status": "success",
                "query": query,
                "chunks_retrieved": len(chunks),
                "collection": collection_name,
                "results": chunks,
                "retrieved_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"  ❌  FCADocTool error: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e)
            }


# ─────────────────────────────────────────────
# 3.  MCP SERVER
#     Manages the tool registry and dispatches calls
# ─────────────────────────────────────────────

class MCPServer:
    """
    MCP Server — the 'brain' that holds all tools.
    The LLM calls these tools by name.
    """

    def __init__(self):
        self.tools: dict[str, Any] = {}
        self._register_tools()

    def _register_tools(self):
        """Register all available tools."""
        for tool_class in [FinanceTool, NewsTool, FCADocTool]:
            instance = tool_class()
            self.tools[instance.name] = instance
            print(f"  🔧  Registered tool: {instance.name}")

    def get_tool_schemas(self) -> list[dict]:
        """Return OpenAI-format tool schemas for all registered tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self.tools.values()
        ]

    def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call a tool by name and return JSON string result."""
        if tool_name not in self.tools:
            result = {
                "status": "error",
                "error": f"Unknown tool: '{tool_name}'. Available: {list(self.tools.keys())}"
            }
        else:
            result = self.tools[tool_name].execute(**arguments)

        return json.dumps(result, indent=2, default=str)


# ─────────────────────────────────────────────
# 4.  MCP CLIENT  (the agent loop)
#     Sends messages to GPT-4o, handles tool calls,
#     loops until the model stops calling tools
# ─────────────────────────────────────────────

class MCPClient:
    """
    MCP Client — the agent that uses the MCP Server.
    Implements the full ReAct loop:
      Think → Act (call tool) → Observe (get result) → Think again → Final Answer
    """

    def __init__(self, server: MCPServer):
        self.server = server
        self.model = "gpt-4o"
        self.max_iterations = 8  # safety limit — never loop forever

    def run(self, user_message: str) -> str:
        """
        Run the agent loop for a single user message.
        Returns the final text response.
        """
        print(f"\n{'═'*60}")
        print(f"USER: {user_message}")
        print(f"{'═'*60}")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert AI assistant specialising in UK financial services. "
                    "You have access to three tools:\n"
                    "1. get_stock_data — live stock prices and financials\n"
                    "2. search_news — recent news from the web\n"
                    "3. search_fca_documents — FCA regulatory guidance\n\n"
                    "Always use tools to get real data. Never guess prices or regulations. "
                    "When you have the data, give a clear, structured answer."
                )
            },
            {"role": "user", "content": user_message}
        ]

        tool_schemas = self.server.get_tool_schemas()
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n  🔄  Agent iteration {iteration}/{self.max_iterations}")

            response = openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto"
            )

            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            print(f"       Finish reason: {finish_reason}")

            # Append the assistant's response to conversation history
            messages.append(message)

            # ── CASE 1: No more tool calls — return the final answer ──
            if finish_reason == "stop" or not message.tool_calls:
                final_answer = message.content or "No response generated."
                print(f"\n{'─'*60}")
                print("FINAL ANSWER:")
                print(f"{'─'*60}")
                print(final_answer)
                return final_answer

            # ── CASE 2: The model wants to call one or more tools ──
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                print(f"\n  🛠️   Tool call: {tool_name}({arguments})")

                # Execute the tool via MCP Server
                tool_result = self.server.call_tool(tool_name, arguments)

                # Add the tool result back into the conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

        return "⚠️  Agent hit the iteration limit. Please try a simpler query."


# ─────────────────────────────────────────────
# 5.  DEMO SCENARIOS
#     3 tests that show all 3 tools working together
# ─────────────────────────────────────────────

def run_demo():
    print("\n" + "█"*60)
    print("  DAY 30 — MCP EXTERNAL API TOOLS DEMO")
    print("  42-Day Agentic AI Sprint — Sheyi Teluwo")
    print("█"*60)

    # Initialise the server (registers all 3 tools)
    print("\n📡  Starting MCP Server...")
    server = MCPServer()
    print(f"\n✅  MCP Server ready with {len(server.tools)} tools: {list(server.tools.keys())}")

    # Initialise the client
    client = MCPClient(server)

    # ── SCENARIO 1: Finance Tool ──────────────────────────────────────
    print("\n\n" + "▓"*60)
    print("  SCENARIO 1 — Finance Tool: Barclays Stock Data")
    print("▓"*60)
    client.run(
        "What is the current share price and market cap of Barclays? "
        "Ticker is BARC.L. Give me a brief investment summary."
    )

    # ── SCENARIO 2: News Tool ─────────────────────────────────────────
    print("\n\n" + "▓"*60)
    print("  SCENARIO 2 — News Tool: FCA Regulatory News")
    print("▓"*60)
    client.run(
        "What is the latest news about FCA regulation and AI in UK financial services? "
        "Give me a 3-sentence summary of the most important recent developments."
    )

    # ── SCENARIO 3: FCA Doc Tool + News (multi-tool) ──────────────────
    print("\n\n" + "▓"*60)
    print("  SCENARIO 3 — Multi-Tool: FCA Consumer Duty + Recent News")
    print("▓"*60)
    client.run(
        "Explain the FCA Consumer Duty requirements and any recent news about "
        "how UK banks are implementing it. Use both the FCA document database "
        "and recent news to give me a comprehensive answer."
    )

    # ── SUMMARY ───────────────────────────────────────────────────────
    print("\n\n" + "█"*60)
    print("  DAY 30 COMPLETE ✅")
    print("█"*60)
    print("\nTools demonstrated:")
    print("  ✅  FinanceTool     — yfinance (live stock data)")
    print("  ✅  NewsTool        — DuckDuckGo (live news search)")
    print("  ✅  FCADocTool      — ChromaDB (Phase 1 vector store)")
    print("\nMCP architecture:")
    print("  ✅  MCPServer       — tool registry + dispatcher")
    print("  ✅  MCPClient       — ReAct agent loop (max 8 iterations)")
    print("  ✅  JSON responses  — structured output from every tool")
    print("  ✅  Error handling  — every tool has try/except")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📸  SCREENSHOT THIS OUTPUT — save as:")
    print("    day30_mcp_external_apis_2026-05-20.png")
    print("█"*60)


if __name__ == "__main__":
    run_demo()
