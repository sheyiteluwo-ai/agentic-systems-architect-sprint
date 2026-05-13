# Day 20 Progress Log — 14 May 2026

## Goal
Fact-Checker Agent — build third agent that cross-validates
claims in the pipeline. Test with deliberately wrong inputs.

## What I Built
- `day20_fact_checker.py` — fact-checker agent with 3 test cases
- `day20_progress.md` — this file
- `day20_fact_report.json` — auto-generated verification report

## How The Fact-Checker Works
1. Receives research text from the Researcher agent
2. Extracts every individual factual claim using GPT-4o
3. Verifies each claim independently (GPT-4o as judge)
4. Assigns status: VERIFIED / UNVERIFIED / UNCERTAIN / HALLUCINATION
5. Only passes claims with confidence ≥ 0.7 to the Writer
6. Flags everything else with explanation

## Test Cases
### Test 1 — Correct Research
- Input: Accurate information about Worker Protection Act 2023
- Result: High verification rate — most claims passed

### Test 2 — Deliberately Wrong Inputs
- Input: Wrong dates, wrong penalties, wrong jurisdiction
- Result: Hallucinations caught and flagged correctly
- The Writer never received unverified claims

### Test 3 — Write From Verified Claims Only
- Writer used only verified claims from Test 1
- Output: Grounded, reliable legal report

## Pipeline Position
```
Researcher → Fact-Checker → Writer
```
Fact-Checker sits between Researcher and Writer.
Acts as quality gate — only verified facts pass through.

## Metrics
- GitHub commits: 28
- Days complete: 20 / 42
- Phase 2 day: 6 of 14

## Day 21 Preview
Magic Circle Legal Use Case — frame crew for contract
analysis, test with legal documents, document Magic Circle
pitch.

## Interview Talking Point
"I built a fact-checker agent that sits between the
Researcher and Writer in my pipeline. It extracts every
factual claim, verifies each one independently, and only
passes verified claims to the Writer. When I fed it
deliberately wrong information — wrong dates, wrong
penalties, wrong jurisdiction — it caught them. The Writer
never sees an unverified claim. That is how you build AI
systems you can trust in regulated environments."
