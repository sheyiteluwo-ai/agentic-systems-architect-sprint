# Day 17 Progress Log — 13 May 2026

## Goal
Multi-Agent Research Pipeline — build web search to
summarise to draft report pipeline with inter-agent
communication.

## What I Built
- `day17_multi_agent_pipeline.py` — 3-agent pipeline with live web search
- `day17_progress.md` — this file
- `day17_output.txt` — auto-generated pipeline output

## Agents Built

### Agent 1 — Legal Web Researcher
- Role: Search web for current UK legal information
- Tool: DuckDuckGo live web search
- Output: Comprehensive web search findings

### Agent 2 — Legal Research Summariser
- Role: Condense web findings into structured summary
- Output: 5-section research summary (max 600 words)

### Agent 3 — Legal Report Writer
- Role: Transform summary into client-ready report
- Output: 6-section professional legal report

## Pipeline
- Sequential — Searcher → Summariser → Writer
- Topic: UK Worker Protection Act 2023
- Framework: CrewAI 0.193.2 + DuckDuckGo + OpenAI GPT-4o
- Python: 3.12 (.venv312)

## Key Achievement
First pipeline using live web search — not training data.
Finds 2024-2026 legal developments in real time.
Three agents working sequentially to produce a
client-ready Magic Circle law firm report.

## Fixes Applied
- DuckDuckGoSearchRun moved to langchain_community
- ddgs package installed (pip install ddgs)
- DuckDuckGo wrapped with CrewAI @tool decorator

## Metrics
- GitHub commits: 24
- Days complete: 17 / 42
- Phase 2 day: 3 of 14

## Day 18 Preview
Add Claude as Second Model — integrate Anthropic Claude API,
compare GPT-4o vs Claude, build model routing logic.

## Interview Talking Point
"I built a 3-agent pipeline where a Web Searcher finds
current UK legal information, a Summariser condenses
the findings, and a Report Writer produces a client-ready
legal report. The pipeline uses live web search — not
training data — meaning it finds information from 2024-2026.
That is the difference between a demo and a system a
Magic Circle law firm could actually use."
