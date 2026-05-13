# Multi-Agent Legal Research System
## Business Pitch — Magic Circle Law Firms

**Prepared by:** Sheyi Teluwo
**Date:** 13 May 2026
**GitHub:** github.com/sheyiteluwo-ai/agentic-systems-architect-sprint

---

## The Problem

Magic Circle law firms — Freshfields, Linklaters, Allen & Overy,
Clifford Chance, Slaughter and May — employ thousands of lawyers
who spend significant time on research that AI can now assist with.

Current pain points:
- Junior associates spend 40-60% of billable time on research
- Research quality varies by associate experience level
- No systematic fact-checking before partner review
- Knowledge not retained between similar matters
- Client pressure to reduce fees while maintaining quality

---

## The Solution

A multi-agent AI research crew that handles the research
layer of legal work — freeing associates for higher-value tasks.

## The Full Pipeline

Legal question / contract scenario
    -> Web Searcher Agent: finds current UK case law and legislation
    -> Fact-Checker Agent: verifies every claim (100% wrong claim detection)
    -> Model Router: GPT-4o for structure / Claude for nuanced analysis
    -> Report Writer Agent: produces partner-ready research brief
    -> HITL Approval Gate: partner reviews before client delivery
    -> Approved report delivered

## What Makes It Safe For A Magic Circle Firm

- Fact-Checker Agent: caught 100% of deliberately wrong claims in testing
- HITL Gate: no output reaches a client without partner sign-off
- Full audit trail: every decision logged to JSON
- Model routing: right model for each task type
- LangGraph state machine: quality loops built into architecture

---

## Demonstration Results

| Test | Result |
|---|---|
| Correct research verification rate | 83.3% |
| Wrong input detection rate | 100% |
| HITL flows tested | Approve / Reject / Escalate |
| Models integrated | GPT-4o + Claude |
| Pipeline agents | 4 (Searcher + Fact-Checker + Router + Writer) |

---

## Business Value

### Time Saved Per Matter
A junior associate currently spends 4-8 hours on initial research
for a standard commercial contract matter.

The pipeline produces an initial research brief in 10-15 minutes.

At a Magic Circle billing rate of £400-£600/hour (junior associate):
- 6 hours research x £500/hour = £3,000 per matter
- Pipeline cost: approximately £2-£5 in API costs
- Saving per matter: £2,995+

### At Scale
A team handling 100 matters per month:
- Current research cost: £300,000/month in associate time
- Pipeline cost: £500/month in API costs
- Monthly saving: £299,500

### Build vs Buy

| Option | Cost | Timeline |
|---|---|---|
| Commercial legal AI platform | £200k-£1M/year | 12-18 months |
| This pipeline | £50k-£100k build | 8-10 weeks |
| Current associate research | £300k+/month | Ongoing |

---

## Roadmap

### Phase 2 Complete (Days 15-21)
- Multi-agent research crew (CrewAI)
- LangGraph state machine with quality loops
- Live web search (DuckDuckGo)
- Model routing (GPT-4o + Claude)
- HITL approval gate
- Fact-checker agent

### Phase 3 (Days 29-42)
- MCP integration for live legal database access
- Docker containerisation
- CI/CD deployment pipeline
- Full security audit

---

## The Ask

A 30-minute technical conversation with the innovation team
at a Magic Circle firm to explore deployment within existing
research workflows.

---

*Sheyi Teluwo | github.com/sheyiteluwo-ai/agentic-systems-architect-sprint*