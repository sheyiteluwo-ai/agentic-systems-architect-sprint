# Day 12 Progress Log — 06 May 2026

## Goal
Write professional README and generate system architecture
diagram for Phase 1 FCA RAG Knowledge Bot.

## What I Built
- `day12_readme_architecture.py` — generates architecture_diagram.png
- `architecture_diagram.png` — full Phase 1 system diagram
- `README.md` — updated professional portfolio README
- `day12_progress.md` — this file

## Architecture Diagram Shows
- Full Phase 1 system flow: User → Streamlit → FastAPI → RAG → ChromaDB → GPT-4o
- HITL gate and guardrail layer
- LangSmith observability
- Phase 1 evaluation metrics
- Full stack labels

## Metrics
- Eval score (correctness): 0.94 / 1.0
- Eval score (faithfulness): 0.465 / 1.0
- GitHub commits: 19
- Days complete: 12 / 42

## Day 13 Preview
- UK Use Case Framing
- Write FCA Regulatory Intelligence Bot pitch
- Frame for Barclays compliance
- Document business value

## Interview Talking Point
"My Phase 1 README documents a production-grade FCA compliance
RAG system with two LangSmith evaluation suites, a HITL gate,
rate limiting, health checks, and guardrails. The architecture
diagram shows the complete data flow from user query to grounded
answer. A hiring manager can understand the full system in under
60 seconds."
