# Day 31 — LangGraph + MCP Integration
**Date:** 2026-05-21
**Sprint:** 42-Day Agentic AI Zero-to-Hero (Day 31 of 42)
**Phase:** 3 — Enterprise MCP Architect (Days 29–42)

---

## What We Built Today

### LangGraph State Machine Wired to MCP Tools

A full LangGraph pipeline that ORCHESTRATES the 3 MCP tools from Day 30 inside a state machine.

### Graph Architecture

```
                    ┌─────────┐
   User Query ────► │  router │  (classifies: finance / news / fca_docs / multi)
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │tool_call│  (calls correct MCP tool(s))
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │validate │  (scores confidence 0.0–1.0)
                    └────┬────┘
                         │
              ┌──────────▼──────────┐
         conf < 0.7            conf ≥ 0.7
              │                     │
       ┌──────▼──────┐        ┌─────▼──────┐
       │human_review │        │   respond   │
       └──────┬──────┘        └─────┬──────┘
              │                     │
              └──────────┬──────────┘
                    ┌────▼────┐
                    │   END   │
                    └─────────┘
```

### Nodes Built

| Node | What It Does |
|---|---|
| `router` | GPT-4o classifies query → finance / news / fca_docs / multi / unknown |
| `tool_call` | Calls correct MCP tool(s); extracts ticker via LLM for finance queries |
| `validate` | Scores confidence 0.0–1.0 based on tool result quality |
| `human_review` | HITL gate — fires when confidence < 0.7; pauses for human input |
| `respond` | GPT-4o synthesises tool results into structured final answer |

### State Object Fields

| Field | Type | Purpose |
|---|---|---|
| `query` | str | Original user question |
| `route` | str | finance / news / fca_docs / multi / unknown |
| `tool_results` | list[dict] | Raw data from MCP tool calls |
| `final_answer` | str | Synthesised response |
| `confidence` | float | Quality score 0.0–1.0 |
| `requires_human_review` | bool | True if confidence < 0.7 |
| `human_feedback` | str | Input from HITL gate |
| `trace` | list[str] | Full audit trail of every node |

---

## Demo Scenarios Run

| Scenario | Route | Tools Called |
|---|---|---|
| HSBC share price | finance | mcp_finance_tool |
| FCA financial promotions | fca_docs | mcp_fca_tool |
| FCA AI regulation + news | multi | mcp_news_tool + mcp_fca_tool |

---

## Files

| File | Purpose |
|---|---|
| `day31_langgraph_mcp.py` | Main script — LangGraph state machine + MCP tools |
| `day31_progress.md` | This file |

---

## Screenshots Required

| Screenshot | Filename |
|---|---|
| Full terminal output | `day31_langgraph_mcp_2026-05-21.png` |

---

## Packages Required

```
pip install langgraph langchain-openai yfinance ddgs chromadb python-dotenv
```

---

## Metrics — Running Total

| Metric | Value |
|---|---|
| LangGraph nodes built today | 5 |
| Conditional edges | 1 |
| MCP tools integrated | 3 |
| Total GitHub commits (after today) | 40 |
| LinkedIn posts scheduled | 26 |

---

## GitHub Commit

```
git add day31_langgraph_mcp.py day31_progress.md
git commit -m "Day 31: LangGraph state machine with MCP tool integration"
git push origin main
```

---

## LinkedIn Posts — Calendar Check

Next available slots after Day 30 (Thu 4 Jun already taken):

| Date | Day | Status |
|---|---|---|
| Fri 5 Jun | Fri | ✅ Day 31 posts |

**Day 31 posts: Friday 5 June 2026**
- **7:30am** — Post 1
- **1:00pm** — Post 2

---

### Post 1 — Friday 5 June, 7:30am

```
Day 31 of 42 🔗

Today I connected LangGraph to my MCP tools.

Here's what the state machine does:

1️⃣ Router — GPT-4o reads the query and decides: finance? news? FCA docs? multi?
2️⃣ Tool Call — fires the right MCP tool (or two tools at once)
3️⃣ Validate — scores confidence 0.0 to 1.0
4️⃣ HITL Gate — if confidence < 0.7, a human reviews before the answer goes out
5️⃣ Respond — GPT-4o synthesises everything into a structured answer

That's not a chatbot.
That's a production-grade decision pipeline.

#LangGraph #AgenticAI #MCP #Python #FinancialServices #Day31of42
```

### Post 2 — Friday 5 June, 1:00pm

```
Most AI demos skip the hard part.

The hard part isn't getting an LLM to answer a question.

The hard part is:
→ Knowing WHICH tool to call for each question
→ Knowing WHEN the answer isn't good enough
→ Knowing WHEN to stop the pipeline and ask a human

Today I built all three into one LangGraph state machine.

Router classifies the query.
Validator scores the confidence.
HITL gate catches the risky answers.

That's the difference between a proof of concept and a system you'd trust with a client.

#StateMachine #HITL #ProductionAI #AIArchitect #UKJobs #Day31of42
```

---

## Day 31 Checklist

- [ ] Activate .venv312
- [ ] `pip install langgraph langchain-openai`
- [ ] Run `day31_langgraph_mcp.py`
- [ ] Screenshot terminal output → `day31_langgraph_mcp_2026-05-21.png`
- [ ] Git commit + push (commit #40)
- [ ] Schedule LinkedIn posts for Fri 5 Jun (7:30am + 1:00pm)
- [ ] Confirm Day 31 complete ✅
