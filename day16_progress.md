# Day 16 Progress Log — 14 May 2026

## Goal
LangGraph Introduction — build first state machine with
nodes, edges, and conditional logic.

## What I Built
- `day16_langgraph_intro.py` — 3-node LangGraph state machine
- `day16_progress.md` — this file

## Graph Structure

```
START → researcher → reviewer → [conditional] → writer → END
                         ↑                          |
                         └──── loop if score < 0.7 ─┘
```

## Nodes
- **researcher** — analyses legal question, produces research brief
- **reviewer** — scores research quality (0.0–1.0)
- **writer** — writes structured legal report

## Conditional Edge
- Score < 0.7 AND iterations < 2 → loop back to researcher
- Score ≥ 0.7 OR iterations ≥ 2 → proceed to writer

## State
LegalResearchState flows through every node carrying:
question, research, quality_score, report, iteration, messages

## Metrics
- GitHub commits: 22
- Days complete: 16 / 42
- Phase 2 day: 2 of 14

## Day 17 Preview
Multi-Agent Research Pipeline — build web search to
summarise to draft report pipeline.

## Interview Talking Point
"I built a LangGraph state machine with 3 nodes and a
conditional edge that loops back if research quality is
below 0.7. This is how enterprise agentic workflows handle
quality control — not with hope, but with automated
evaluation and retry logic built into the graph structure."
