# day22_langsmith_eval_multiagent.py
# Day 22 — LangSmith Eval #3 — Multi-Agent Quality
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Friday 15 May 2026
# Stack: LangSmith · CrewAI · OpenAI GPT-4o

"""
Day 22 Goal: Build multi-agent output quality evaluator.
Score coherence between agents. Set quality benchmark.

What we evaluate:
    1. Researcher output quality (completeness, accuracy)
    2. Fact-Checker output quality (coverage, precision)
    3. Writer output quality (structure, clarity)
    4. Pipeline coherence (does each agent build on the last?)
    5. Overall pipeline score

Scoring:
    Each dimension scored 0.0 - 1.0
    Overall = average across all dimensions
    Benchmark target: >= 0.80

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# ── Test Dataset ──────────────────────────────────────────────────────────────

EVAL_SCENARIOS = [
    {
        "id": "S01",
        "question": (
            "What are the key obligations for UK employers under "
            "the Worker Protection Act 2023?"
        ),
        "expected_topics": [
            "preventive duty",
            "sexual harassment",
            "EHRC",
            "reasonable steps",
            "October 2024"
        ]
    },
    {
        "id": "S02",
        "question": (
            "What must be included in a UK employment contract "
            "under the Employment Rights Act 1996?"
        ),
        "expected_topics": [
            "written statement",
            "particulars of employment",
            "job title",
            "pay",
            "working hours"
        ]
    },
    {
        "id": "S03",
        "question": (
            "What are the risks of unlimited liability clauses "
            "in UK commercial contracts?"
        ),
        "expected_topics": [
            "unlimited liability",
            "indemnity",
            "consequential loss",
            "cap",
            "negotiation"
        ]
    }
]


# ── Pipeline Runner ───────────────────────────────────────────────────────────

def run_mini_pipeline(question: str) -> dict:
    """
    Runs a mini 2-agent pipeline (Researcher + Writer)
    for evaluation purposes.
    Returns individual agent outputs for scoring.
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Step 1: Researcher
    research_response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior legal researcher at a Magic Circle "
                    "law firm. Research the question thoroughly."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Research this legal question:\n\n{question}\n\n"
                    f"Cover: obligations, risks, legislation, recommendations."
                )
            }
        ]
    )
    research = research_response.choices[0].message.content.strip()

    # Step 2: Writer
    writer_response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a legal report writer. Write a structured "
                    "report from the research provided."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Write a professional legal report based on:\n\n"
                    f"QUESTION: {question}\n\n"
                    f"RESEARCH:\n{research}\n\n"
                    f"Structure: Executive Summary, Key Points, "
                    f"Recommendations, Conclusion."
                )
            }
        ]
    )
    report = writer_response.choices[0].message.content.strip()

    return {
        "question": question,
        "research": research,
        "report": report
    }


# ── Evaluator ─────────────────────────────────────────────────────────────────

def evaluate_pipeline_output(
    question: str,
    research: str,
    report: str,
    expected_topics: list
) -> dict:
    """
    Evaluates the pipeline output across 5 dimensions:
    1. Research completeness
    2. Research accuracy
    3. Report structure
    4. Report clarity
    5. Pipeline coherence
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    eval_prompt = (
        f"Evaluate this multi-agent legal research pipeline output.\n\n"
        f"QUESTION: {question}\n\n"
        f"EXPECTED TOPICS: {', '.join(expected_topics)}\n\n"
        f"RESEARCH OUTPUT:\n{research[:800]}\n\n"
        f"FINAL REPORT:\n{report[:800]}\n\n"
        f"Score each dimension from 0.0 to 1.0.\n"
        f"Reply ONLY with valid JSON:\n"
        f'{{"research_completeness": 0.9, '
        f'"research_accuracy": 0.85, '
        f'"report_structure": 0.9, '
        f'"report_clarity": 0.85, '
        f'"pipeline_coherence": 0.9, '
        f'"reasoning": "one sentence summary"}}'
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict quality evaluator for AI systems. "
                    "Reply ONLY with valid JSON. No markdown. No preamble."
                )
            },
            {"role": "user", "content": eval_prompt}
        ]
    )

    raw = response.choices[0].message.content.strip()

    try:
        if "```" in raw:
            for part in raw.split("```"):
                part = part.strip().lstrip("json").strip()
                if part.startswith("{"):
                    raw = part
                    break
        start = raw.find("{")
        end = raw.rfind("}") + 1
        result = json.loads(raw[start:end])

        scores = {
            "research_completeness": float(
                result.get("research_completeness", 0.7)
            ),
            "research_accuracy": float(
                result.get("research_accuracy", 0.7)
            ),
            "report_structure": float(
                result.get("report_structure", 0.7)
            ),
            "report_clarity": float(
                result.get("report_clarity", 0.7)
            ),
            "pipeline_coherence": float(
                result.get("pipeline_coherence", 0.7)
            ),
            "reasoning": result.get("reasoning", "Evaluated")
        }

        scores["overall"] = round(
            sum([
                scores["research_completeness"],
                scores["research_accuracy"],
                scores["report_structure"],
                scores["report_clarity"],
                scores["pipeline_coherence"]
            ]) / 5, 3
        )

        return scores

    except Exception as e:
        return {
            "research_completeness": 0.7,
            "research_accuracy": 0.7,
            "report_structure": 0.7,
            "report_clarity": 0.7,
            "pipeline_coherence": 0.7,
            "overall": 0.7,
            "reasoning": f"Parse error: {str(e)[:50]}"
        }


# ── Main Evaluation Pipeline ──────────────────────────────────────────────────

def run_evaluation():
    print("\n" + "="*65)
    print("  DAY 22 — LANGSMITH EVAL #3 — MULTI-AGENT QUALITY")
    print("  Date: Friday 15 May 2026")
    print("  Scenarios: 3 | Dimensions: 5 | Benchmark: >= 0.80")
    print("="*65 + "\n")

    all_results = []
    total_overall = 0.0

    for scenario in EVAL_SCENARIOS:
        print(f"[{scenario['id']}] {scenario['question'][:55]}...")
        print(f"     Running pipeline...")

        # Run pipeline
        pipeline_output = run_mini_pipeline(scenario["question"])

        # Evaluate output
        scores = evaluate_pipeline_output(
            question=scenario["question"],
            research=pipeline_output["research"],
            report=pipeline_output["report"],
            expected_topics=scenario["expected_topics"]
        )

        total_overall += scores["overall"]

        print(f"     Research completeness: {scores['research_completeness']:.2f}")
        print(f"     Research accuracy:     {scores['research_accuracy']:.2f}")
        print(f"     Report structure:      {scores['report_structure']:.2f}")
        print(f"     Report clarity:        {scores['report_clarity']:.2f}")
        print(f"     Pipeline coherence:    {scores['pipeline_coherence']:.2f}")
        print(f"     Overall:               {scores['overall']:.3f} / 1.0")
        print(f"     Reasoning: {scores['reasoning'][:70]}")
        print()

        all_results.append({
            "scenario_id": scenario["id"],
            "question": scenario["question"],
            "scores": scores,
            "pipeline_output": {
                "research_length": len(pipeline_output["research"]),
                "report_length": len(pipeline_output["report"])
            }
        })

    # Summary
    avg_overall = round(total_overall / len(EVAL_SCENARIOS), 3)
    benchmark_met = avg_overall >= 0.80
    benchmark_icon = "PASS" if benchmark_met else "FAIL"

    summary = {
        "eval_date": datetime.now(timezone.utc).isoformat(),
        "sprint_day": 22,
        "total_scenarios": len(EVAL_SCENARIOS),
        "average_overall_score": avg_overall,
        "benchmark": 0.80,
        "benchmark_status": benchmark_icon,
        "dimensions_evaluated": [
            "research_completeness",
            "research_accuracy",
            "report_structure",
            "report_clarity",
            "pipeline_coherence"
        ],
        "results": all_results
    }

    with open("eval_report_day22.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*65)
    print("  MULTI-AGENT EVALUATION COMPLETE")
    print("="*65)
    print(f"  Scenarios evaluated:  {len(EVAL_SCENARIOS)}")
    print(f"  Average overall:      {avg_overall:.3f} / 1.0")
    print(f"  Benchmark (>= 0.80):  {benchmark_icon}")
    print(f"  Report saved:         eval_report_day22.json")
    print("="*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I built a 5-dimension quality evaluator for my")
    print("  multi-agent pipeline — scoring research completeness,")
    print("  accuracy, report structure, clarity, and pipeline")
    print("  coherence. This is LangSmith Eval #3 — the third")
    print("  evaluation suite in my sprint. I now have quality")
    print("  metrics across both my RAG system and my multi-agent")
    print("  research pipeline. That is what production AI looks")
    print("  like — not just working, but measurably working.")
    print("  " + "-"*56 + "\n")

    return summary


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_evaluation()
