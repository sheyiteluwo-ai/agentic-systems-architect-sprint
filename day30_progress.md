# Day 30 — MCP Tools: External APIs
**Date:** 2026-05-20
**Sprint:** 42-Day Agentic AI Zero-to-Hero (Day 30 of 42)
**Phase:** 3 — Enterprise MCP Architect (Days 29–42)

---

## What We Built Today

### Three Production-Grade MCP Tools

| Tool | Source | What It Does |
|---|---|---|
| `get_stock_data` | yfinance | Live stock price, market cap, P/E ratio for any ticker |
| `search_news` | DuckDuckGo | Real-time news search, 5 headlines + snippets |
| `search_fca_documents` | ChromaDB (Phase 1) | Queries your 494-chunk FCA regulatory database |

### Architecture

```
User Query
    │
    ▼
MCPClient (agent loop — max 8 iterations)
    │  sends messages + tool schemas
    ▼
GPT-4o (decides which tool to call)
    │  tool_call request
    ▼
MCPServer (tool registry + dispatcher)
    │  routes to correct tool
    ▼
Tool Execution
  ├── FinanceTool   → yfinance API
  ├── NewsTool      → DuckDuckGo API
  └── FCADocTool    → ChromaDB vector store
    │  JSON result
    ▼
MCPClient adds result to message history
    │  loops back to GPT-4o
    ▼
Final Answer (when finish_reason == "stop")
```

### Key Design Decisions

1. **Dependency check at startup** — script tells you exactly what to `pip install` if anything is missing
2. **Safe `.get()` defaults** — Finance tool never crashes on missing fields
3. **Collection auto-discovery** — FCA tool scans all ChromaDB collections if exact name not found
4. **JSON responses from every tool** — consistent structure for the LLM to parse
5. **Iteration cap at 8** — prevents infinite loops in the agent

---

## Demo Scenarios Run

1. **Scenario 1 — Finance Tool:** Barclays (BARC.L) live share price + market cap
2. **Scenario 2 — News Tool:** Latest FCA AI regulation news, 3-sentence summary
3. **Scenario 3 — Multi-Tool:** Consumer Duty from FCA docs + recent news combined

---

## Files

| File | Purpose |
|---|---|
| `day30_mcp_external_apis.py` | Main script — MCP Server + Client + 3 tools |
| `day30_progress.md` | This file |

---

## Screenshots Required

| Screenshot | Filename |
|---|---|
| Full terminal output from running the script | `day30_mcp_external_apis_2026-05-20.png` |

---

## Packages Required

```
pip install yfinance ddgs chromadb openai python-dotenv
```

---

## Metrics — Running Total

| Metric | Value |
|---|---|
| MCP tools built (Day 30) | 3 |
| Total MCP tools across Phase 3 | 6 (3 from Day 29 + 3 today) |
| FCA chunks in ChromaDB | 494 |
| Eval score — correctness (Phase 1) | 0.94/1.0 |
| Eval score — faithfulness (Phase 1) | 0.465/1.0 |
| Eval score — multi-agent quality (Phase 2) | 0.733/1.0 |
| GitHub commits (after today) | 39 |
| LinkedIn posts scheduled | 24 (26 after today) |

---

## GitHub Commit

```
git add day30_mcp_external_apis.py day30_progress.md
git commit -m "Day 30: MCP external API tools — finance, news, FCA doc retrieval"
git push origin main
```

---

## LinkedIn Posts — Scheduled for Thu 4 Jun 2026

### Post 1 — 7:30am

```
Day 30 of 42 🏗️

Today I connected my MCP agent to 3 real external APIs:

📈 Finance tool — live stock data (Barclays, HSBC, any ticker)
📰 News tool — real-time news via DuckDuckGo
📚 FCA doc tool — my Phase 1 regulatory vector store

The agent decides which tool to call, calls it, reads the result, and decides what to do next.

That's the ReAct loop in production.

Not a demo. Real data. Real decisions.

Tomorrow: LangGraph + MCP integration — connecting state machines to external APIs.

#AgenticAI #MCP #Python #LLMOps #FinancialServices #Day30of42
```

### Post 2 — 1:00pm

```
The difference between a chatbot and an agent?

A chatbot knows things.
An agent does things.

Today my MCP agent:
→ Fetched Barclays' live share price
→ Searched for latest FCA regulation news
→ Retrieved relevant Consumer Duty guidance from 494 regulatory chunks
→ Synthesised all 3 into one coherent answer

It didn't guess. It used tools.

That's why UK banks are hiring AI engineers at £850+/day.

They need people who can build systems that connect to real enterprise data.

Not people who can prompt ChatGPT.

#MCPProtocol #AIArchitect #FinTech #UKJobs #Day30of42
```

---

## Day 30 Checklist

- [ ] Activate .venv312
- [ ] `pip install yfinance ddgs chromadb openai python-dotenv`
- [ ] Run `day30_mcp_external_apis.py`
- [ ] Screenshot terminal output → `day30_mcp_external_apis_2026-05-20.png`
- [ ] Git commit + push (commit #39)
- [ ] Schedule LinkedIn posts for Thu 4 Jun
- [ ] Confirm Day 30 complete ✅
