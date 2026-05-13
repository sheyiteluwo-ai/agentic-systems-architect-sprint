# day15_crewai_setup.py
# Day 15 — CrewAI Setup: Researcher + Writer Agents
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Tuesday 13 May 2026
# Stack: CrewAI · OpenAI GPT-4o

"""
Day 15 Goal: Build first multi-agent crew with two agents.

Agents:
    1. Legal Researcher — finds and analyses relevant legal information
    2. Legal Writer    — transforms research into structured reports

Use Case: Magic Circle Law Firm — Contract Analysis Research
Task: Research key legal obligations in UK employment contracts

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


def build_legal_research_crew(topic: str):
    """
    Builds and runs a two-agent legal research crew.
    Agent 1 — Legal Researcher: researches the topic thoroughly.
    Agent 2 — Legal Writer: writes a structured professional report.
    """
    from crewai import Agent, Task, Crew, Process

    print(f"\n  Topic: {topic}")
    print(f"  Agents: Legal Researcher + Legal Writer")
    print(f"  Process: Sequential\n")

    # ── Agent 1: Legal Researcher ─────────────────────────────────────────────
    researcher = Agent(
        role="Senior Legal Researcher",
        goal=(
            "Research legal topics thoroughly and identify key obligations, "
            "risks, case precedents, and regulatory requirements relevant to "
            "UK Magic Circle law firm clients."
        ),
        backstory=(
            "You are a senior legal researcher with 15 years of experience "
            "at a Magic Circle law firm. You specialise in UK employment law, "
            "contract law, and regulatory compliance. You are meticulous, "
            "precise, and always cite your sources. You understand that "
            "inaccurate legal research can expose clients to significant risk."
        ),
        verbose=True,
        allow_delegation=False,
        llm="gpt-4o"
    )

    # ── Agent 2: Legal Writer ─────────────────────────────────────────────────
    writer = Agent(
        role="Legal Report Writer",
        goal=(
            "Transform legal research into clear, structured, professional "
            "reports that senior partners and clients can act on immediately."
        ),
        backstory=(
            "You are a legal report writer at a Magic Circle law firm. "
            "You have a gift for turning complex legal research into "
            "concise, actionable reports. Your reports follow a consistent "
            "structure: Executive Summary, Key Findings, Obligations, "
            "Risks, and Recommendations. Partners trust your work."
        ),
        verbose=True,
        allow_delegation=False,
        llm="gpt-4o"
    )

    # ── Task 1: Research ──────────────────────────────────────────────────────
    research_task = Task(
        description=(
            f"Research the following legal topic thoroughly:\n\n"
            f"TOPIC: {topic}\n\n"
            f"Your research must cover:\n"
            f"1. Key legal obligations under UK law\n"
            f"2. Common risks and pitfalls\n"
            f"3. Relevant UK legislation or case law\n"
            f"4. What a Magic Circle law firm would advise clients\n"
            f"5. Any recent developments or regulatory changes\n\n"
            f"Be thorough. Be precise. This research will be used to "
            f"write a professional legal report."
        ),
        expected_output=(
            "A comprehensive research brief covering all five areas above. "
            "Minimum 400 words. Written in professional legal language. "
            "Clearly structured with numbered sections."
        ),
        agent=researcher
    )

    # ── Task 2: Write Report ──────────────────────────────────────────────────
    writing_task = Task(
        description=(
            "Using the research provided, write a professional legal report "
            "suitable for a Magic Circle law firm partner.\n\n"
            "The report must follow this exact structure:\n"
            "1. EXECUTIVE SUMMARY (3-4 sentences)\n"
            "2. KEY LEGAL OBLIGATIONS (bulleted list)\n"
            "3. KEY RISKS (bulleted list)\n"
            "4. RELEVANT LEGISLATION (listed)\n"
            "5. RECOMMENDATIONS (3-5 actionable points)\n"
            "6. CONCLUSION (2-3 sentences)\n\n"
            "Write for a senior partner audience. "
            "Clear, concise, and immediately actionable."
        ),
        expected_output=(
            "A structured professional legal report following the six-section "
            "format above. Suitable for immediate use by a Magic Circle law "
            "firm partner. Minimum 500 words."
        ),
        agent=writer,
        context=[research_task]
    )

    # ── Assemble Crew ─────────────────────────────────────────────────────────
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True
    )

    return crew


def run_crew(topic: str) -> str:
    """Runs the legal research crew and saves output to file."""
    print("\n" + "="*65)
    print("  DAY 15 — CREWAI MULTI-AGENT LEGAL RESEARCH")
    print("  Date: Tuesday 13 May 2026")
    print("  Phase 2: Magic Circle Legal Research Automation")
    print("="*65)

    crew = build_legal_research_crew(topic)

    print("\n🚀 Crew is running — both agents working sequentially...\n")
    result = crew.kickoff()

    # Save output to file
    output_path = "day15_output.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"DAY 15 — CREWAI LEGAL RESEARCH OUTPUT\n")
        f.write(f"Date: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"Topic: {topic}\n")
        f.write("="*65 + "\n\n")
        f.write(str(result))

    print("\n" + "="*65)
    print("  CREW COMPLETED SUCCESSFULLY")
    print("="*65)
    print(f"  Output saved to: day15_output.txt")
    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I built a two-agent CrewAI system where a Legal")
    print("  Researcher and Legal Writer work sequentially.")
    print("  The researcher finds and analyses UK legal obligations.")
    print("  The writer transforms that into a structured report")
    print("  a Magic Circle law firm partner can act on immediately.")
    print("  Neither agent does the other's job. Together they")
    print("  produce something neither could alone.")
    print("  " + "-"*56 + "\n")

    return str(result)


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    TOPIC = (
        "Key legal obligations in UK employment contracts — "
        "what must be included under the Employment Rights Act 1996, "
        "common employer risks, and what Magic Circle law firms "
        "advise clients when drafting or reviewing employment contracts."
    )

    result = run_crew(TOPIC)
    print("\n📄 FINAL REPORT PREVIEW:")
    print("-"*65)
    print(result[:500] + "..." if len(result) > 500 else result)
    print("-"*65)
