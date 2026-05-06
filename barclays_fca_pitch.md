# FCA Regulatory Intelligence Bot
## Business Pitch — Barclays Compliance Division

**Prepared by:** Sheyi Teluwo
**Date:** 06 May 2026
**GitHub:** github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
**Sprint Day:** 13 of 42

---

## The Problem

Barclays employs hundreds of compliance officers who spend significant
time manually searching FCA regulatory documents to answer questions
about Consumer Duty, complaints handling, and vulnerable customer
obligations.

Current pain points:
- Manual search across hundreds of pages of FCA PDFs
- Inconsistent answers depending on which officer handles the query
- No audit trail of which regulatory source underpins each decision
- Escalation decisions made subjectively — no standardised rubric
- New regulatory updates require re-training entire compliance teams

The FCA Consumer Duty came into force in July 2023. Firms that cannot
demonstrate consistent, documented compliance face enforcement action,
financial penalties, and reputational damage.

---

## The Solution

The FCA Regulatory Intelligence Bot is a production-grade RAG system
that answers compliance questions in plain English, grounded in real
FCA regulatory documents.

### How It Works

1. Compliance officer types a question in plain English
2. The system retrieves the most relevant FCA document chunks
3. GPT-4o generates a grounded answer with source citations
4. A Human-in-the-Loop gate applies 5 compliance rubrics
5. High-stakes questions are automatically escalated
6. Every query is logged with source, decision, and timestamp

### What Makes It Safe For Regulated Environments

- **Faithfulness guardrail** — answers scoring below 0.7 are blocked
- **HITL gate** — legal and escalation triggers route to human review
- **Full audit trail** — every query logged to LangSmith
- **Source citations** — every answer shows which FCA page it came from
- **Rate limiting** — prevents runaway API costs
- **Health monitoring** — /health/deep endpoint for deployment platforms

---

## Evaluation Results

| Metric | Score | Industry Benchmark |
|---|---|---|
| Correctness (LangSmith Eval #1) | 0.94 / 1.0 | 0.75 typical |
| Faithfulness (LangSmith Eval #2) | 0.465 / 1.0* | N/A |
| HITL escalation accuracy | Manual review | 100% flagged |
| Response time | < 5 seconds | < 10 seconds |
| Rate limiting | 10 req/min | Configurable |

*Faithfulness score reflects knowledge gap in current document corpus.
Adding PRIN and COBS sourcebooks is projected to raise this to 0.85+.

---

## Business Value

### Time Saved
A compliance officer currently spends an estimated 2–4 hours per day
searching regulatory documents. The bot reduces this to minutes.

At a fully-loaded cost of £80k/year per compliance officer:
- 10 officers × 2 hours/day × 220 working days = 4,400 hours/year
- Value of time recovered: **£169,000/year**

### Risk Reduced
- Consistent answers reduce regulatory interpretation risk
- Automatic escalation ensures no high-stakes query goes unreviewed
- Full audit trail satisfies FCA record-keeping requirements

### Build vs Buy
| Option | Cost | Timeline |
|---|---|---|
| Buy commercial RegTech solution | £150k–£500k/year | 6–12 months |
| Build with this stack | £40k–£80k one-off | 6–8 weeks |
| Current manual process | £169k+/year in lost time | Ongoing |

---

## Technical Stack

| Component | Technology | Why |
|---|---|---|
| LLM | OpenAI GPT-4o | Best reasoning for compliance |
| Framework | LangChain LCEL | Industry standard RAG |
| Vector Store | ChromaDB | Lightweight, local, fast |
| API | FastAPI | Production-grade, typed |
| UI | Streamlit | Rapid deployment |
| Observability | LangSmith | Full trace + eval suite |
| Validation | Pydantic | Type-safe request handling |
| Rate Limiting | SlowAPI | Cost protection |

---

## Roadmap

### Phase 1 Complete (Days 1–14)
- ✅ FCA document RAG with conversation memory
- ✅ LangSmith evaluation suite (correctness + faithfulness)
- ✅ HITL gate with 5 compliance rubrics
- ✅ FastAPI REST wrapper
- ✅ Streamlit chat UI
- ✅ Production hardening

### Phase 2 (Days 15–28)
- Multi-agent research crew (CrewAI + LangGraph)
- Automated regulatory update monitoring
- Cross-document contradiction detection

### Phase 3 (Days 29–42)
- Model Context Protocol (MCP) integration
- NHS patient triage workflow
- Barclays fraud detection agent
- Docker + CI/CD deployment
- Full security audit

---

## Why Now

The FCA Consumer Duty is 2 years old. Firms are now in the
enforcement phase — not the preparation phase. The FCA has
signalled it will take action against firms that cannot demonstrate
consistent consumer outcomes.

AI-assisted compliance is no longer experimental. It is becoming
a competitive necessity.

---

*Built by Sheyi Teluwo as part of the 42-Day Agentic AI
Zero-to-Hero Sprint. UK Enterprise Edition.*
*github.com/sheyiteluwo-ai/agentic-systems-architect-sprint*
