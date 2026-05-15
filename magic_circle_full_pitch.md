# Multi-Agent Legal Research System
## Full Business Case — Magic Circle Law Firms

**Prepared by:** Sheyi Teluwo
**Date:** 15 May 2026
**Sprint:** 42-Day Agentic AI Zero-to-Hero
**GitHub:** github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
**Loom Demo:** https://www.loom.com/share/bec8aee08b784e55969551aa6bce593f

---

## Executive Summary

This document presents a business case for deploying a
multi-agent AI research system within a Magic Circle law firm.
The system automates the research layer of commercial legal work,
reducing a 4-8 hour junior associate task to 10-15 minutes while
maintaining partner-level quality control through a human-in-the-loop
approval gate.

Target firms: Freshfields, Linklaters, Allen & Overy,
Clifford Chance, Slaughter and May.

---

## The Problem

Magic Circle law firms face three compounding pressures:

**1. Fee pressure from clients**
Corporate clients increasingly challenge legal bills.
Research tasks that once billed at £3,000-£5,000 are being
questioned as AI-capable work.

**2. Associate time cost**
Junior associates bill at £400-£650/hour.
40-60% of their time is spent on research — work AI can assist.
At 100 matters per month, that is £300,000+ in research costs alone.

**3. Inconsistent quality**
Research quality varies by associate experience.
Senior partners spend significant time correcting junior work.
No systematic fact-checking exists before partner review.

---

## The Solution — Phase 2 Multi-Agent Research Crew

A production-grade multi-agent pipeline that handles the research
layer of legal work while keeping humans in control of every output.

### The Full Pipeline

```
Legal question / contract scenario
    -> Web Searcher Agent
       Finds current UK case law, legislation, regulatory guidance
       Tool: DuckDuckGo live web search
    -> Fact-Checker Agent
       Verifies every claim independently
       Result: 100% wrong claim detection in testing
    -> Model Router
       GPT-4o for structured output
       Claude for nuanced analytical reasoning
    -> Summariser Agent
       Condenses verified research into structured brief
    -> Report Writer Agent
       Produces partner-ready legal research report
    -> HITL Approval Gate
       Partner reviews: Approve / Reject with feedback / Escalate
       Rejected reports regenerated with feedback automatically
    -> Final report delivered to client
```

### Supporting Systems

- **Agent Memory** — persistent ChromaDB stores client facts,
  past decisions, and precedents across sessions
- **Error Recovery** — retry, fallback chain, circuit breaker
  ensure the pipeline never fails silently
- **LangGraph State Machine** — quality loops built into architecture
- **LangSmith Observability** — every step traced and evaluated

---

## Evaluation Results

| Metric | Score | Notes |
|---|---|---|
| Phase 1 Correctness (RAG) | 0.94 / 1.0 | Above 0.75 industry benchmark |
| Phase 1 Faithfulness | 0.465 / 1.0 | Identified document corpus gaps |
| Phase 2 Multi-Agent Quality | 0.733 / 1.0 | 5-dimension evaluation |
| Fact-Checker Accuracy | 100% | All wrong claims caught in testing |
| HITL Flows Tested | 3 | Approve, Reject, Escalate |

---

## Return on Investment

### Per Matter Calculation

| Item | Current | With Pipeline |
|---|---|---|
| Research time | 4-8 hours | 10-15 minutes |
| Associate cost (at £500/hr) | £2,000-£4,000 | £2-£5 (API cost) |
| Partner review time | 1-2 hours | 30 minutes |
| Total saving per matter | - | £1,970-£3,995 |

### At Scale — 100 Matters Per Month

| Item | Value |
|---|---|
| Current monthly research cost | £300,000+ |
| Pipeline API cost | £500 |
| Monthly saving | £299,500 |
| Annual saving | £3,594,000 |
| Build cost (one-off) | £50,000-£100,000 |
| Break-even | < 2 weeks |

### Build vs Buy

| Option | Cost | Timeline | Control |
|---|---|---|---|
| Commercial legal AI platform | £200k-£1M/year | 12-18 months | Low |
| This pipeline | £50k-£100k one-off | 8-10 weeks | Full |
| Current manual process | £300k+/month | Ongoing | Full |

---

## Risk Mitigation

**Hallucination risk**
The Fact-Checker Agent catches wrong claims before they reach
the writer. In testing, 100% of deliberately wrong inputs were
flagged. The faithfulness guardrail blocks ungrounded answers.

**Client confidentiality**
All processing happens via secure API calls. No client data
is stored in third-party systems beyond the API request lifecycle.
Agent memory is stored locally in ChromaDB.

**Human oversight**
The HITL gate means no output reaches a client without a
qualified partner reviewing and approving it. The full review
trail is logged to JSON for audit purposes.

**System reliability**
Three error recovery patterns (retry, fallback chain, circuit
breaker) ensure the pipeline never fails silently. A static
safe response is always available as a last resort.

---

## Technical Stack

| Component | Technology |
|---|---|
| Agent Framework | CrewAI 0.193 |
| State Machine | LangGraph 1.2 |
| LLM (primary) | OpenAI GPT-4o |
| LLM (analytical) | Anthropic Claude |
| Vector Memory | ChromaDB |
| Web Search | DuckDuckGo |
| Observability | LangSmith |
| Language | Python 3.12 |

---

## Roadmap

### Phase 2 Complete (Days 15-27)
- Multi-agent research crew
- LangGraph state machine
- Live web search
- Model routing (GPT-4o + Claude)
- HITL approval gate
- Fact-checker agent
- Persistent agent memory
- Error recovery patterns
- LangSmith Eval #3

### Phase 3 (Days 29-42)
- Model Context Protocol (MCP) integration
- NHS patient triage workflow
- Barclays fraud detection agent
- Docker containerisation
- CI/CD with GitHub Actions
- Full security audit

---

## The Ask

A 30-minute technical conversation with your innovation or
technology team to explore how this pipeline could be deployed
within existing research workflows at your firm.

No vendor lock-in. No subscription. Full ownership of the code.

---

*Sheyi Teluwo*
*github.com/sheyiteluwo-ai/agentic-systems-architect-sprint*
*Loom Demo: https://www.loom.com/share/bec8aee08b784e55969551aa6bce593f*