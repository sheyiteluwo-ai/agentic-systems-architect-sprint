# day14_demo_day.py
# Day 14 — Phase 1 Complete — Demo Day
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Wednesday 7 May 2026

"""
Day 14 Goal: Phase 1 completion summary.
Records all Phase 1 achievements and prepares for Phase 2.

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

from datetime import datetime, timezone


PHASE1_SUMMARY = {
    "phase": "Phase 1 — FCA RAG Knowledge Bot",
    "days_completed": 14,
    "github_commits": 20,
    "linkedin_posts": 8,
    "eval_correctness": 0.94,
    "eval_faithfulness": 0.465,
    "fca_chunks_indexed": 494,
    "files_created": [
        "day01_hello_agent.py",
        "day02_rag_loader.py",
        "day03_rag_memory.py",
        "day04_prompt_engineering.py",
        "day05_multi_doc_rag.py",
        "day06_langsmith_evals.py",
        "day07_hitl_and_fixes.py",
        "day08_fastapi.py",
        "day09_streamlit_ui.py",
        "day10_production_hardening.py",
        "day11_hallucination_detection.py",
        "day12_readme_architecture.py",
        "day13_use_case_framing.py",
        "day14_demo_day.py",
    ],
    "key_features": [
        "FCA document RAG with 494 chunks indexed",
        "Conversation memory with source citations",
        "LangSmith correctness evaluation — 0.94/1.0",
        "LangSmith faithfulness evaluation — hallucination detection",
        "Human-in-the-loop gate with 5 compliance rubrics",
        "FastAPI REST wrapper with rate limiting",
        "Streamlit chat UI with HITL safety badges",
        "Production hardening — health checks + logging",
        "Guardrails — SERVE / SERVE_WITH_WARNING / BLOCK",
        "Architecture diagram",
        "Barclays FCA pitch + CTO one-page summary",
        "10-minute Loom demo recorded",
    ],
    "next_phase": "Phase 2 — Multi-Agent Research Crew (Days 15-28)"
}


def print_phase1_summary():
    print("\n" + "="*65)
    print("  PHASE 1 COMPLETE — FCA RAG KNOWLEDGE BOT")
    print("  Date: Wednesday 7 May 2026")
    print("="*65)

    print(f"\n  Days completed:      {PHASE1_SUMMARY['days_completed']}")
    print(f"  GitHub commits:      {PHASE1_SUMMARY['github_commits']}")
    print(f"  LinkedIn posts:      {PHASE1_SUMMARY['linkedin_posts']}")
    print(f"  Eval (correctness):  {PHASE1_SUMMARY['eval_correctness']}/1.0")
    print(f"  Eval (faithfulness): {PHASE1_SUMMARY['eval_faithfulness']}/1.0")
    print(f"  FCA chunks indexed:  {PHASE1_SUMMARY['fca_chunks_indexed']}")
    print(f"  Loom demo:           Recorded ✅")

    print("\n  KEY FEATURES BUILT:")
    for feature in PHASE1_SUMMARY["key_features"]:
        print(f"  ✅ {feature}")

    print(f"\n  NEXT: {PHASE1_SUMMARY['next_phase']}")

    print("\n" + "="*65)
    print("  PHASE 1 INTERVIEW TALKING POINT")
    print("="*65)
    print("""
  In 14 days, working part-time, I built a production-grade
  FCA compliance RAG system from scratch. The beginner
  benchmark was 112 hours — I completed it in roughly half
  that time.

  The system has two LangSmith evaluation suites, a
  human-in-the-loop gate with 5 compliance rubrics, a FastAPI
  REST wrapper with rate limiting, a Streamlit chat UI, and
  production hardening including health endpoints and guardrails.

  I also built the full business case — £169k/year value
  recovered for a 10-person Barclays compliance team, with
  a build cost of £40k-£80k versus £150k-£500k/year for a
  commercial alternative.

  The system is documented, evaluated, demoed, and
  interview-ready. Phase 2 starts tomorrow.
    """)
    print("="*65 + "\n")


if __name__ == "__main__":
    print_phase1_summary()
