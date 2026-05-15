# day27_magic_circle_pitch.py
# Day 27 — Magic Circle Legal Pitch
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Friday 15 May 2026

"""
Day 27 Goal: Write full Magic Circle use case document.
Frame ROI for law firm. Create CTO one-page summary.

Generates:
    1. magic_circle_full_pitch.md  — full business case
    2. magic_circle_cto_summary.md — one-page CTO summary

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

from datetime import datetime, timezone


def generate_full_pitch():
    date_str = datetime.now(timezone.utc).strftime("%d %B %Y")

    lines = [
        "# Multi-Agent Legal Research System",
        "## Full Business Case — Magic Circle Law Firms",
        "",
        f"**Prepared by:** Sheyi Teluwo",
        f"**Date:** {date_str}",
        "**Sprint:** 42-Day Agentic AI Zero-to-Hero",
        "**GitHub:** github.com/sheyiteluwo-ai/agentic-systems-architect-sprint",
        "**Loom Demo:** https://www.loom.com/share/bec8aee08b784e55969551aa6bce593f",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "This document presents a business case for deploying a",
        "multi-agent AI research system within a Magic Circle law firm.",
        "The system automates the research layer of commercial legal work,",
        "reducing a 4-8 hour junior associate task to 10-15 minutes while",
        "maintaining partner-level quality control through a human-in-the-loop",
        "approval gate.",
        "",
        "Target firms: Freshfields, Linklaters, Allen & Overy,",
        "Clifford Chance, Slaughter and May.",
        "",
        "---",
        "",
        "## The Problem",
        "",
        "Magic Circle law firms face three compounding pressures:",
        "",
        "**1. Fee pressure from clients**",
        "Corporate clients increasingly challenge legal bills.",
        "Research tasks that once billed at £3,000-£5,000 are being",
        "questioned as AI-capable work.",
        "",
        "**2. Associate time cost**",
        "Junior associates bill at £400-£650/hour.",
        "40-60% of their time is spent on research — work AI can assist.",
        "At 100 matters per month, that is £300,000+ in research costs alone.",
        "",
        "**3. Inconsistent quality**",
        "Research quality varies by associate experience.",
        "Senior partners spend significant time correcting junior work.",
        "No systematic fact-checking exists before partner review.",
        "",
        "---",
        "",
        "## The Solution — Phase 2 Multi-Agent Research Crew",
        "",
        "A production-grade multi-agent pipeline that handles the research",
        "layer of legal work while keeping humans in control of every output.",
        "",
        "### The Full Pipeline",
        "",
        "```",
        "Legal question / contract scenario",
        "    -> Web Searcher Agent",
        "       Finds current UK case law, legislation, regulatory guidance",
        "       Tool: DuckDuckGo live web search",
        "    -> Fact-Checker Agent",
        "       Verifies every claim independently",
        "       Result: 100% wrong claim detection in testing",
        "    -> Model Router",
        "       GPT-4o for structured output",
        "       Claude for nuanced analytical reasoning",
        "    -> Summariser Agent",
        "       Condenses verified research into structured brief",
        "    -> Report Writer Agent",
        "       Produces partner-ready legal research report",
        "    -> HITL Approval Gate",
        "       Partner reviews: Approve / Reject with feedback / Escalate",
        "       Rejected reports regenerated with feedback automatically",
        "    -> Final report delivered to client",
        "```",
        "",
        "### Supporting Systems",
        "",
        "- **Agent Memory** — persistent ChromaDB stores client facts,",
        "  past decisions, and precedents across sessions",
        "- **Error Recovery** — retry, fallback chain, circuit breaker",
        "  ensure the pipeline never fails silently",
        "- **LangGraph State Machine** — quality loops built into architecture",
        "- **LangSmith Observability** — every step traced and evaluated",
        "",
        "---",
        "",
        "## Evaluation Results",
        "",
        "| Metric | Score | Notes |",
        "|---|---|---|",
        "| Phase 1 Correctness (RAG) | 0.94 / 1.0 | Above 0.75 industry benchmark |",
        "| Phase 1 Faithfulness | 0.465 / 1.0 | Identified document corpus gaps |",
        "| Phase 2 Multi-Agent Quality | 0.733 / 1.0 | 5-dimension evaluation |",
        "| Fact-Checker Accuracy | 100% | All wrong claims caught in testing |",
        "| HITL Flows Tested | 3 | Approve, Reject, Escalate |",
        "",
        "---",
        "",
        "## Return on Investment",
        "",
        "### Per Matter Calculation",
        "",
        "| Item | Current | With Pipeline |",
        "|---|---|---|",
        "| Research time | 4-8 hours | 10-15 minutes |",
        "| Associate cost (at £500/hr) | £2,000-£4,000 | £2-£5 (API cost) |",
        "| Partner review time | 1-2 hours | 30 minutes |",
        "| Total saving per matter | - | £1,970-£3,995 |",
        "",
        "### At Scale — 100 Matters Per Month",
        "",
        "| Item | Value |",
        "|---|---|",
        "| Current monthly research cost | £300,000+ |",
        "| Pipeline API cost | £500 |",
        "| Monthly saving | £299,500 |",
        "| Annual saving | £3,594,000 |",
        "| Build cost (one-off) | £50,000-£100,000 |",
        "| Break-even | < 2 weeks |",
        "",
        "### Build vs Buy",
        "",
        "| Option | Cost | Timeline | Control |",
        "|---|---|---|---|",
        "| Commercial legal AI platform | £200k-£1M/year | 12-18 months | Low |",
        "| This pipeline | £50k-£100k one-off | 8-10 weeks | Full |",
        "| Current manual process | £300k+/month | Ongoing | Full |",
        "",
        "---",
        "",
        "## Risk Mitigation",
        "",
        "**Hallucination risk**",
        "The Fact-Checker Agent catches wrong claims before they reach",
        "the writer. In testing, 100% of deliberately wrong inputs were",
        "flagged. The faithfulness guardrail blocks ungrounded answers.",
        "",
        "**Client confidentiality**",
        "All processing happens via secure API calls. No client data",
        "is stored in third-party systems beyond the API request lifecycle.",
        "Agent memory is stored locally in ChromaDB.",
        "",
        "**Human oversight**",
        "The HITL gate means no output reaches a client without a",
        "qualified partner reviewing and approving it. The full review",
        "trail is logged to JSON for audit purposes.",
        "",
        "**System reliability**",
        "Three error recovery patterns (retry, fallback chain, circuit",
        "breaker) ensure the pipeline never fails silently. A static",
        "safe response is always available as a last resort.",
        "",
        "---",
        "",
        "## Technical Stack",
        "",
        "| Component | Technology |",
        "|---|---|",
        "| Agent Framework | CrewAI 0.193 |",
        "| State Machine | LangGraph 1.2 |",
        "| LLM (primary) | OpenAI GPT-4o |",
        "| LLM (analytical) | Anthropic Claude |",
        "| Vector Memory | ChromaDB |",
        "| Web Search | DuckDuckGo |",
        "| Observability | LangSmith |",
        "| Language | Python 3.12 |",
        "",
        "---",
        "",
        "## Roadmap",
        "",
        "### Phase 2 Complete (Days 15-27)",
        "- Multi-agent research crew",
        "- LangGraph state machine",
        "- Live web search",
        "- Model routing (GPT-4o + Claude)",
        "- HITL approval gate",
        "- Fact-checker agent",
        "- Persistent agent memory",
        "- Error recovery patterns",
        "- LangSmith Eval #3",
        "",
        "### Phase 3 (Days 29-42)",
        "- Model Context Protocol (MCP) integration",
        "- NHS patient triage workflow",
        "- Barclays fraud detection agent",
        "- Docker containerisation",
        "- CI/CD with GitHub Actions",
        "- Full security audit",
        "",
        "---",
        "",
        "## The Ask",
        "",
        "A 30-minute technical conversation with your innovation or",
        "technology team to explore how this pipeline could be deployed",
        "within existing research workflows at your firm.",
        "",
        "No vendor lock-in. No subscription. Full ownership of the code.",
        "",
        "---",
        "",
        "*Sheyi Teluwo*",
        "*github.com/sheyiteluwo-ai/agentic-systems-architect-sprint*",
        "*Loom Demo: https://www.loom.com/share/bec8aee08b784e55969551aa6bce593f*",
    ]

    content = "\n".join(lines)
    with open("magic_circle_full_pitch.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("  magic_circle_full_pitch.md generated")
    return content


def generate_cto_summary():
    date_str = datetime.now(timezone.utc).strftime("%d %B %Y")

    lines = [
        "# Multi-Agent Legal Research System",
        "## One-Page CTO Summary — Magic Circle Law Firms",
        "",
        f"**Prepared by:** Sheyi Teluwo  |  **Date:** {date_str}",
        "",
        "---",
        "",
        "## What It Is",
        "",
        "A production-grade multi-agent AI system that automates the",
        "research layer of commercial legal work. Built in Python using",
        "CrewAI, LangGraph, GPT-4o, and Anthropic Claude.",
        "",
        "## The Problem It Solves",
        "",
        "Junior associates spend 40-60% of billable time on research.",
        "At £400-£650/hour, that is £300,000+ per month for a 100-matter team.",
        "Quality is inconsistent. Hallucination risk is real and unmanaged.",
        "No systematic fact-checking exists before partner review.",
        "",
        "## What It Does",
        "",
        "- Searches the web for current UK case law and legislation",
        "- Fact-checks every claim (100% wrong claim detection in testing)",
        "- Routes tasks to the right model (GPT-4o or Claude)",
        "- Produces a structured partner-ready research brief in 10-15 mins",
        "- Requires partner approval before any output reaches a client",
        "- Remembers client context across sessions via ChromaDB",
        "- Fails gracefully — retry, fallback, circuit breaker built in",
        "",
        "## Numbers That Matter",
        "",
        "| Metric | Value |",
        "|---|---|",
        "| Research time reduction | 4-8 hours to 10-15 minutes |",
        "| Saving per matter | £1,970-£3,995 |",
        "| Monthly saving (100 matters) | £299,500 |",
        "| Annual saving | £3,594,000 |",
        "| Build cost | £50,000-£100,000 one-off |",
        "| Break-even | Less than 2 weeks |",
        "| Eval score (correctness) | 0.94 / 1.0 |",
        "| Eval score (multi-agent quality) | 0.733 / 1.0 |",
        "| Fact-checker accuracy | 100% wrong claims caught |",
        "",
        "## Is It Safe For A Magic Circle Firm?",
        "",
        "Yes. Four layers of protection:",
        "1. Fact-Checker — wrong claims caught before they reach the writer",
        "2. HITL Gate — partner approves every output before client delivery",
        "3. Full audit trail — every decision logged to JSON",
        "4. Error recovery — system never fails silently",
        "",
        "## What It Is Built On",
        "",
        "CrewAI · LangGraph · OpenAI GPT-4o · Anthropic Claude",
        "ChromaDB · LangSmith · Python 3.12 · DuckDuckGo",
        "",
        "## The Ask",
        "",
        "A 30-minute conversation with your innovation team.",
        "Full code ownership. No vendor lock-in. No subscription.",
        "",
        "---",
        "",
        "*Sheyi Teluwo*",
        "*github.com/sheyiteluwo-ai/agentic-systems-architect-sprint*",
        "*Loom: https://www.loom.com/share/bec8aee08b784e55969551aa6bce593f*",
    ]

    content = "\n".join(lines)
    with open("magic_circle_cto_summary.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("  magic_circle_cto_summary.md generated")
    return content


if __name__ == "__main__":
    print("\n" + "="*65)
    print("  DAY 27 — MAGIC CIRCLE LEGAL PITCH")
    print("  Date: Friday 15 May 2026")
    print("="*65 + "\n")

    print("Generating full pitch document...")
    generate_full_pitch()

    print("Generating CTO one-page summary...")
    generate_cto_summary()

    print("\n" + "="*65)
    print("  DAY 27 COMPLETE — PITCH DOCUMENTS GENERATED")
    print("="*65)
    print(f"  Full pitch:    magic_circle_full_pitch.md")
    print(f"  CTO summary:   magic_circle_cto_summary.md")
    print("="*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I wrote a full business case for deploying my")
    print("  multi-agent system at a Magic Circle law firm.")
    print("  The ROI calculation shows £3.6M annual saving")
    print("  for a 100-matter team with a break-even of less")
    print("  than 2 weeks. I can speak to the technical AND")
    print("  the business value in the same conversation.")
    print("  Most engineers can only do one.")
    print("  " + "-"*56 + "\n")
