# day17_multi_agent_pipeline.py
# Day 17 — Multi-Agent Research Pipeline
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Thursday 15 May 2026
# Stack: CrewAI · OpenAI GPT-4o · DuckDuckGo Web Search

"""
Day 17 Goal: Build a 3-agent pipeline with live web search.

Agents:
    1. Web Searcher  — searches the web for current legal information
    2. Summariser    — condenses and structures the search results
    3. Report Writer — produces the final professional legal report

Pipeline:
    Web Searcher → Summariser → Report Writer

Use Case: Magic Circle Law Firm — Live Legal Research
The pipeline finds current legal information, not just training data.

FIXES APPLIED:
    FIX 1 → DuckDuckGoSearchRun imported from langchain_community
             instead of crewai_tools (moved in newer versions)

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


def build_research_pipeline(topic: str):
    """
    Builds a 3-agent research pipeline with live web search.
    """
    from crewai import Agent, Task, Crew, Process
    from langchain_community.tools import DuckDuckGoSearchRun

    print(f"\n  Topic: {topic}")
    print(f"  Agents: Web Searcher + Summariser + Report Writer")
    print(f"  Process: Sequential with web search\n")

    # Use DuckDuckGo — no API key needed
    search_tool = DuckDuckGoSearchRun()

    # ── Agent 1: Web Searcher ─────────────────────────────────────────────────
    web_searcher = Agent(
        role="Legal Web Researcher",
        goal=(
            "Search the web for the most current and relevant legal "
            "information on the given topic. Find recent cases, "
            "legislative updates, and authoritative legal sources."
        ),
        backstory=(
            "You are a specialist legal web researcher at a Magic Circle "
            "law firm. You know exactly where to find current UK legal "
            "information — legislation.gov.uk, bailii.org, law firm "
            "publications, and FCA guidance. You always find primary "
            "sources, not just summaries."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
        llm="gpt-4o"
    )

    # ── Agent 2: Summariser ───────────────────────────────────────────────────
    summariser = Agent(
        role="Legal Research Summariser",
        goal=(
            "Read the web research findings and produce a concise, "
            "structured summary that captures all key legal points, "
            "removing noise and keeping only what matters."
        ),
        backstory=(
            "You are a senior associate at a Magic Circle law firm "
            "with exceptional ability to read large amounts of legal "
            "material and extract the key points quickly and accurately. "
            "Partners rely on your summaries before reading full documents."
        ),
        verbose=True,
        allow_delegation=False,
        llm="gpt-4o"
    )

    # ── Agent 3: Report Writer ────────────────────────────────────────────────
    report_writer = Agent(
        role="Legal Report Writer",
        goal=(
            "Transform the research summary into a polished, "
            "professional legal report suitable for a Magic Circle "
            "law firm partner to present to a client."
        ),
        backstory=(
            "You are the go-to legal report writer at a Magic Circle "
            "law firm. You turn research summaries into clear, "
            "structured, actionable reports. Your work goes directly "
            "to partners and clients without revision."
        ),
        verbose=True,
        allow_delegation=False,
        llm="gpt-4o"
    )

    # ── Task 1: Web Search ────────────────────────────────────────────────────
    search_task = Task(
        description=(
            f"Search the web for current legal information on:\n\n"
            f"TOPIC: {topic}\n\n"
            f"Use your search tool to find:\n"
            f"1. Current UK legislation relevant to this topic\n"
            f"2. Recent case law or tribunal decisions\n"
            f"3. FCA or regulatory guidance if applicable\n"
            f"4. Recent legal commentary from authoritative sources\n"
            f"5. Any 2024-2026 updates or changes\n\n"
            f"Search multiple times with different queries to get "
            f"comprehensive results."
        ),
        expected_output=(
            "A comprehensive collection of web search findings covering "
            "current UK law on the topic. Include URLs where found. "
            "Minimum 5 distinct pieces of information from different sources."
        ),
        agent=web_searcher
    )

    # ── Task 2: Summarise ─────────────────────────────────────────────────────
    summarise_task = Task(
        description=(
            "Read all the web search findings provided and produce a "
            "structured legal research summary.\n\n"
            "Your summary must include:\n"
            "1. KEY LEGISLATION — what laws apply\n"
            "2. RECENT DEVELOPMENTS — what has changed recently\n"
            "3. KEY OBLIGATIONS — what parties must do\n"
            "4. KEY RISKS — what could go wrong\n"
            "5. SOURCES — where the information came from\n\n"
            "Remove duplicate information. Keep only what is legally "
            "significant. Maximum 600 words."
        ),
        expected_output=(
            "A structured 5-section research summary. Maximum 600 words. "
            "Clearly organised under the five headings above. "
            "No duplicate information."
        ),
        agent=summariser,
        context=[search_task]
    )

    # ── Task 3: Write Report ──────────────────────────────────────────────────
    report_task = Task(
        description=(
            "Using the research summary, write a professional legal "
            "report for a Magic Circle law firm partner.\n\n"
            "Structure the report as:\n"
            "## EXECUTIVE SUMMARY\n"
            "## KEY LEGAL OBLIGATIONS\n"
            "## RECENT DEVELOPMENTS (2024-2026)\n"
            "## KEY RISKS\n"
            "## RECOMMENDATIONS\n"
            "## CONCLUSION\n\n"
            "This report will be sent to a client. "
            "Write with that level of precision and care."
        ),
        expected_output=(
            "A six-section professional legal report. "
            "Client-ready quality. Minimum 500 words. "
            "Includes a Recent Developments section specific to 2024-2026."
        ),
        agent=report_writer,
        context=[summarise_task]
    )

    # ── Assemble Crew ─────────────────────────────────────────────────────────
    crew = Crew(
        agents=[web_searcher, summariser, report_writer],
        tasks=[search_task, summarise_task, report_task],
        process=Process.sequential,
        verbose=True
    )

    return crew


def run_pipeline(topic: str) -> str:
    """Runs the multi-agent research pipeline and saves output."""
    print("\n" + "="*65)
    print("  DAY 17 — MULTI-AGENT RESEARCH PIPELINE")
    print("  Date: Thursday 15 May 2026")
    print("  Phase 2: Magic Circle Legal Research Automation")
    print("  Pipeline: Web Search → Summarise → Report")
    print("="*65)

    crew = build_research_pipeline(topic)

    print("\n🚀 Pipeline running — 3 agents working sequentially...\n")
    result = crew.kickoff()

    # Save output
    output_path = "day17_output.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"DAY 17 — MULTI-AGENT PIPELINE OUTPUT\n")
        f.write(f"Date: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"Topic: {topic}\n")
        f.write("="*65 + "\n\n")
        f.write(str(result))

    print("\n" + "="*65)
    print("  PIPELINE COMPLETED SUCCESSFULLY")
    print("="*65)
    print(f"  Agents used:     3 (Searcher + Summariser + Writer)")
    print(f"  Output saved:    day17_output.txt")
    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I built a 3-agent pipeline where a Web Searcher finds")
    print("  current UK legal information, a Summariser condenses")
    print("  the findings, and a Report Writer produces a client-")
    print("  ready legal report. The pipeline uses live web search")
    print("  — not training data — meaning it finds information")
    print("  from 2024-2026. That is the difference between a demo")
    print("  and a system a Magic Circle law firm could actually use.")
    print("  " + "-"*56 + "\n")

    return str(result)


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    TOPIC = (
        "UK Worker Protection Act 2023 — key employer obligations, "
        "enforcement powers, and what Magic Circle law firms are "
        "advising clients to do before the October 2024 deadline."
    )

    result = run_pipeline(TOPIC)
    print("\n📄 FINAL REPORT PREVIEW:")
    print("-"*65)
    print(result[:600] + "..." if len(result) > 600 else result)
    print("-"*65)
