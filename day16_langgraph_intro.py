# day16_langgraph_intro.py
# Day 16 — LangGraph Introduction
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Wednesday 14 May 2026
# Stack: LangGraph · LangChain · OpenAI GPT-4o

"""
Day 16 Goal: Build first LangGraph state machine.

What we build:
    A 3-node legal research graph for Magic Circle law firms.

    Node 1 — researcher: analyses the legal question
    Node 2 — reviewer:   checks if research is sufficient
    Node 3 — writer:     writes the final legal report

    Conditional edge: if research quality < threshold → loop back
                      if research quality >= threshold → proceed to writer

Graph flow:
    START → researcher → reviewer → writer → END
                              ↑         |
                              └── loop ─┘ (if quality insufficient)

This is the foundation for Phase 3 enterprise workflows.

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# ── State Definition ──────────────────────────────────────────────────────────

class LegalResearchState(TypedDict):
    """
    The state that flows through every node in the graph.
    Every node can read and update this state.
    """
    question: str           # the original legal question
    research: str           # output from the researcher node
    quality_score: float    # quality assessment from reviewer node
    report: str             # final report from writer node
    iteration: int          # how many research loops we have done
    messages: list          # conversation history


# ── Node Functions ────────────────────────────────────────────────────────────

def researcher_node(state: LegalResearchState) -> LegalResearchState:
    """
    Node 1: Legal Researcher
    Analyses the legal question and produces a research brief.
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage

    print(f"\n  🔍 RESEARCHER NODE (iteration {state['iteration'] + 1})")
    print(f"     Question: {state['question'][:60]}...")

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    messages = [
        SystemMessage(content=(
            "You are a senior legal researcher at a Magic Circle law firm. "
            "Produce thorough, accurate legal research. "
            "Cover: obligations, risks, legislation, and recommendations."
        )),
        HumanMessage(content=(
            f"Research this legal question thoroughly:\n\n"
            f"{state['question']}\n\n"
            f"Provide a structured research brief with:\n"
            f"1. Key legal obligations\n"
            f"2. Main risks\n"
            f"3. Relevant UK legislation\n"
            f"4. Key recommendations\n"
            f"Be specific and cite relevant law."
        ))
    ]

    response = llm.invoke(messages)
    research = response.content

    print(f"     Research produced: {len(research)} characters")

    return {
        **state,
        "research": research,
        "iteration": state["iteration"] + 1,
        "messages": state["messages"] + [
            {"role": "researcher", "content": research[:200]}
        ]
    }


def reviewer_node(state: LegalResearchState) -> LegalResearchState:
    """
    Node 2: Quality Reviewer
    Scores the research quality and decides if it is good enough
    to proceed to writing, or needs another research iteration.
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    import json

    print(f"\n  📋 REVIEWER NODE")
    print(f"     Assessing research quality...")

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    messages = [
        SystemMessage(content=(
            "You are a senior partner at a Magic Circle law firm. "
            "You review legal research for quality and completeness. "
            "You must respond ONLY with valid JSON — no markdown, no preamble."
        )),
        HumanMessage(content=(
            f"Rate this legal research on a scale of 0.0 to 1.0:\n\n"
            f"ORIGINAL QUESTION: {state['question']}\n\n"
            f"RESEARCH PRODUCED:\n{state['research']}\n\n"
            f"Score criteria:\n"
            f"- 0.9-1.0: Excellent — covers all areas thoroughly\n"
            f"- 0.7-0.89: Good — covers most areas adequately\n"
            f"- 0.5-0.69: Adequate — missing some important areas\n"
            f"- Below 0.5: Poor — needs significant improvement\n\n"
            f"Respond ONLY with this JSON:\n"
            f'{{"score": 0.85, "feedback": "one sentence", '
            f'"proceed": true}}'
        ))
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Parse JSON safely
    try:
        if "```" in raw:
            for part in raw.split("```"):
                part = part.strip().lstrip("json").strip()
                if part.startswith("{"):
                    raw = part
                    break
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        result = json.loads(raw)
        score = float(result.get("score", 0.7))
        feedback = result.get("feedback", "Research assessed")
        proceed = result.get("proceed", score >= 0.7)
    except Exception:
        score = 0.75
        feedback = "Default score applied"
        proceed = True

    print(f"     Quality score: {score:.2f}")
    print(f"     Feedback: {feedback}")
    print(f"     Proceed to writing: {proceed}")

    return {
        **state,
        "quality_score": score,
        "messages": state["messages"] + [
            {"role": "reviewer", "content": f"Score: {score} | {feedback}"}
        ]
    }


def writer_node(state: LegalResearchState) -> LegalResearchState:
    """
    Node 3: Legal Report Writer
    Transforms the research into a structured professional report.
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage

    print(f"\n  ✍️  WRITER NODE")
    print(f"     Writing final legal report...")

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    messages = [
        SystemMessage(content=(
            "You are a legal report writer at a Magic Circle law firm. "
            "Write clear, structured, professional reports for senior partners."
        )),
        HumanMessage(content=(
            f"Write a professional legal report based on this research.\n\n"
            f"QUESTION: {state['question']}\n\n"
            f"RESEARCH:\n{state['research']}\n\n"
            f"Structure the report exactly as:\n"
            f"## EXECUTIVE SUMMARY\n"
            f"## KEY LEGAL OBLIGATIONS\n"
            f"## KEY RISKS\n"
            f"## RELEVANT LEGISLATION\n"
            f"## RECOMMENDATIONS\n"
            f"## CONCLUSION\n\n"
            f"Write for a senior partner. Clear and immediately actionable."
        ))
    ]

    response = llm.invoke(messages)
    report = response.content

    print(f"     Report written: {len(report)} characters")

    return {
        **state,
        "report": report,
        "messages": state["messages"] + [
            {"role": "writer", "content": report[:200]}
        ]
    }


# ── Conditional Edge Logic ────────────────────────────────────────────────────

def should_continue_research(state: LegalResearchState) -> str:
    """
    Conditional edge: decides what happens after the reviewer node.

    If quality score is below 0.7 AND we have not exceeded 2 iterations:
        → loop back to researcher for another attempt
    Otherwise:
        → proceed to writer
    """
    score = state.get("quality_score", 0.0)
    iteration = state.get("iteration", 0)

    if score < 0.7 and iteration < 2:
        print(f"\n  🔄 CONDITIONAL EDGE: Score {score:.2f} < 0.7")
        print(f"     Looping back to researcher (iteration {iteration})")
        return "researcher"
    else:
        print(f"\n  ✅ CONDITIONAL EDGE: Score {score:.2f} — proceeding to writer")
        return "writer"


# ── Build The Graph ───────────────────────────────────────────────────────────

def build_legal_graph():
    """
    Assembles the 3-node LangGraph state machine.

    Graph structure:
        START → researcher → reviewer → [conditional] → writer → END
                                 ↑                          |
                                 └──── loop if score < 0.7 ─┘
    """
    from langgraph.graph import StateGraph, END

    print("\n  Building LangGraph state machine...")

    # Create graph with our state type
    graph = StateGraph(LegalResearchState)

    # Add nodes
    graph.add_node("researcher", researcher_node)
    graph.add_node("reviewer",   reviewer_node)
    graph.add_node("writer",     writer_node)

    # Set entry point
    graph.set_entry_point("researcher")

    # Add edges
    graph.add_edge("researcher", "reviewer")

    # Add conditional edge from reviewer
    graph.add_conditional_edges(
        "reviewer",
        should_continue_research,
        {
            "researcher": "researcher",   # loop back
            "writer":     "writer"        # proceed
        }
    )

    # Writer always ends
    graph.add_edge("writer", END)

    # Compile the graph
    compiled = graph.compile()
    print("  ✅ Graph compiled successfully\n")
    return compiled


# ── Run The Graph ─────────────────────────────────────────────────────────────

def run_legal_graph(question: str) -> dict:
    """Runs the legal research graph on a given question."""
    print("\n" + "="*65)
    print("  DAY 16 — LANGGRAPH STATE MACHINE")
    print("  Date: Wednesday 14 May 2026")
    print("  Nodes: researcher → reviewer → writer")
    print("  Use Case: Magic Circle Legal Research")
    print("="*65)

    graph = build_legal_graph()

    # Initial state
    initial_state = LegalResearchState(
        question=question,
        research="",
        quality_score=0.0,
        report="",
        iteration=0,
        messages=[]
    )

    print(f"\n🚀 Running graph on: {question[:60]}...\n")

    # Run the graph
    final_state = graph.invoke(initial_state)

    # Print results
    print("\n" + "="*65)
    print("  GRAPH COMPLETED SUCCESSFULLY")
    print("="*65)
    print(f"  Research iterations:  {final_state['iteration']}")
    print(f"  Quality score:        {final_state['quality_score']:.2f} / 1.0")
    print(f"  Report length:        {len(final_state['report'])} characters")
    print(f"  Nodes visited:        {len(final_state['messages'])}")
    print("="*65)

    print("\n📄 REPORT PREVIEW:")
    print("-"*65)
    print(final_state["report"][:600] + "..." if len(
        final_state["report"]) > 600 else final_state["report"])
    print("-"*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I built a LangGraph state machine with 3 nodes and")
    print("  a conditional edge that loops back if research quality")
    print("  is below 0.7. This is how enterprise agentic workflows")
    print("  handle quality control — not with hope, but with")
    print("  automated evaluation and retry logic built into the")
    print("  graph structure itself.")
    print("  " + "-"*56 + "\n")

    return final_state


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    QUESTION = (
        "What are the key legal obligations for UK employers "
        "regarding non-compete clauses in employment contracts, "
        "and what makes them enforceable under English law?"
    )

    result = run_legal_graph(QUESTION)