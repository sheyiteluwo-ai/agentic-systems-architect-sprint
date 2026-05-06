# FCA Regulatory Intelligence Bot
## One-Page CTO Summary

**Prepared by:** Sheyi Teluwo | 06 May 2026

---

## What It Is
A production-grade AI system that answers FCA compliance questions
in plain English, grounded in real regulatory documents, with a
human-in-the-loop approval gate for high-stakes queries.

## The Problem It Solves
Compliance officers spend 2–4 hours daily manually searching FCA
PDFs. Answers are inconsistent. There is no audit trail. Escalation
decisions are subjective.

## What It Does
- Answers FCA Consumer Duty, complaints, and vulnerable customer
  questions in under 5 seconds
- Shows the exact FCA source page for every answer
- Automatically escalates legal and high-stakes queries to humans
- Logs every decision with timestamp for FCA audit requirements
- Blocks answers it cannot ground in regulatory documents

## Numbers That Matter

| Metric | Value |
|---|---|
| Correctness score | 0.94 / 1.0 |
| Response time | < 5 seconds |
| Build cost | £40k–£80k one-off |
| Commercial alternative | £150k–£500k/year |
| Time recovered per officer | 2 hours/day |
| Annual value (10 officers) | £169,000 |

## Is It Safe For A Regulated Environment?
Yes. Three layers of protection:
1. Faithfulness guardrail — low-confidence answers are blocked
2. HITL gate — legal triggers route to qualified human review
3. Full audit trail — every query logged and traceable

## What It Is Built On
LangChain · OpenAI GPT-4o · ChromaDB · FastAPI · LangSmith

## What Comes Next
Phase 2 adds multi-agent monitoring of regulatory updates.
Phase 3 adds MCP integration for live data sources.

## The Ask
A 30-minute technical conversation to explore deployment
within Barclays compliance infrastructure.

---

*Sheyi Teluwo | github.com/sheyiteluwo-ai/agentic-systems-architect-sprint*
