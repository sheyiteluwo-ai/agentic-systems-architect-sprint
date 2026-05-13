# day19_hitl_report_approval.py
# Day 19 — HITL Gate #2 — Report Approval
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Wednesday 13 May 2026
# Stack: CrewAI · OpenAI GPT-4o · Human-in-the-Loop

"""
Day 19 Goal: Add human approval gate to multi-agent pipeline.

Flow:
    Pipeline produces report
        ↓
    HITL Gate — human reviews
        ↓
    APPROVE  → delivered
    REJECT   → regenerated with feedback
    ESCALATE → senior partner notified

Use Case: Magic Circle Law Firm — no AI report goes to a
client without human sign-off.

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


# ── Report Generator ──────────────────────────────────────────────────────────

def generate_legal_report(topic: str, feedback: str = None) -> dict:
    """
    Generates a legal report using GPT-4o.
    If feedback is provided, incorporates it into the regeneration.
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system = (
        "You are a senior legal report writer at a Magic Circle law firm. "
        "Produce professional, accurate, client-ready legal reports."
    )

    if feedback:
        prompt = (
            f"Regenerate this legal report incorporating the following "
            f"feedback from a senior partner:\n\n"
            f"FEEDBACK: {feedback}\n\n"
            f"TOPIC: {topic}\n\n"
            f"Structure as:\n"
            f"## EXECUTIVE SUMMARY\n"
            f"## KEY OBLIGATIONS\n"
            f"## RISKS\n"
            f"## RECOMMENDATIONS\n"
            f"## CONCLUSION"
        )
    else:
        prompt = (
            f"Write a professional legal report on:\n\n"
            f"TOPIC: {topic}\n\n"
            f"Structure as:\n"
            f"## EXECUTIVE SUMMARY\n"
            f"## KEY OBLIGATIONS\n"
            f"## RISKS\n"
            f"## RECOMMENDATIONS\n"
            f"## CONCLUSION"
        )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    report = response.choices[0].message.content.strip()

    return {
        "topic": topic,
        "report": report,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "word_count": len(report.split()),
        "feedback_applied": feedback is not None
    }


# ── HITL Gate ─────────────────────────────────────────────────────────────────

class HITLReportGate:
    """
    Human-in-the-loop gate for legal report approval.

    Three outcomes:
        APPROVE  → report is delivered as-is
        REJECT   → report is regenerated with human feedback
        ESCALATE → flagged for senior partner review
    """

    def __init__(self):
        self.review_log = []

    def display_report(self, report_data: dict) -> None:
        """Displays the report for human review."""
        print("\n" + "="*65)
        print("  📄 REPORT FOR REVIEW")
        print("="*65)
        print(f"\n  Topic: {report_data['topic']}")
        print(f"  Words: {report_data['word_count']}")
        print(f"  Generated: {report_data['generated_at']}")
        if report_data['feedback_applied']:
            print(f"  ⚡ Feedback applied in this version")
        print("\n" + "-"*65)
        print(report_data['report'][:1200] + "..."
              if len(report_data['report']) > 1200
              else report_data['report'])
        print("-"*65)

    def get_human_decision(self) -> tuple[str, str]:
        """
        Prompts the human reviewer for a decision.
        Returns (decision, feedback)
        """
        print("\n" + "="*65)
        print("  👤 HUMAN REVIEW REQUIRED")
        print("="*65)
        print("\n  Options:")
        print("  [A] APPROVE  — report is ready for client")
        print("  [R] REJECT   — regenerate with your feedback")
        print("  [E] ESCALATE — flag for senior partner")
        print()

        while True:
            decision = input("  Your decision (A/R/E): ").strip().upper()
            if decision in ["A", "R", "E"]:
                break
            print("  Please enter A, R, or E")

        feedback = ""
        if decision == "R":
            print()
            feedback = input("  Your feedback for regeneration: ").strip()

        return decision, feedback

    def process_decision(self, decision: str, feedback: str,
                         report_data: dict) -> dict:
        """Processes the human decision and logs it."""
        decision_map = {
            "A": "APPROVED",
            "R": "REJECTED",
            "E": "ESCALATED"
        }

        result = {
            "decision": decision_map[decision],
            "feedback": feedback,
            "topic": report_data["topic"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "word_count": report_data["word_count"]
        }

        self.review_log.append(result)

        if decision == "A":
            print("\n  ✅ APPROVED — Report cleared for client delivery")
        elif decision == "R":
            print(f"\n  🔄 REJECTED — Regenerating with feedback: {feedback}")
        elif decision == "E":
            print("\n  🚨 ESCALATED — Senior partner notified")

        return result

    def save_review_log(self) -> None:
        """Saves the full review log to file."""
        with open("day19_review_log.json", "w", encoding="utf-8") as f:
            json.dump({
                "session_date": datetime.now(timezone.utc).isoformat(),
                "total_reviews": len(self.review_log),
                "reviews": self.review_log
            }, f, indent=2)
        print(f"\n  📋 Review log saved: day19_review_log.json")


# ── Demo Mode ─────────────────────────────────────────────────────────────────

def run_automated_demo():
    """
    Runs an automated demo of all three HITL outcomes.
    No human input required — simulates approve, reject, escalate.
    """
    print("\n" + "="*65)
    print("  DAY 19 — HITL GATE #2 — REPORT APPROVAL")
    print("  Date: Wednesday 13 May 2026")
    print("  Mode: Automated Demo (simulating human decisions)")
    print("="*65)

    gate = HITLReportGate()

    TOPIC = (
        "Key employer obligations under the UK Worker Protection "
        "Act 2023 — what firms must do to comply."
    )

    # ── Demo 1: APPROVE flow ──────────────────────────────────────────────────
    print("\n\n── DEMO 1: APPROVE FLOW ────────────────────────────────")
    print("  Generating report...")
    report1 = generate_legal_report(TOPIC)
    print(f"  ✅ Report generated: {report1['word_count']} words")
    print(f"\n  Report Preview:")
    print(f"  {report1['report'][:400]}...")
    print(f"\n  [Simulating human decision: APPROVE]")
    result1 = gate.process_decision("A", "", report1)
    print(f"  Decision logged: {result1['decision']}")

    # ── Demo 2: REJECT → REGENERATE flow ─────────────────────────────────────
    print("\n\n── DEMO 2: REJECT → REGENERATE FLOW ───────────────────")
    print("  Generating initial report...")
    report2 = generate_legal_report(TOPIC)
    print(f"  ✅ Initial report generated: {report2['word_count']} words")

    feedback = (
        "The recommendations section is too generic. "
        "Add specific timelines and name the EHRC guidance directly."
    )
    print(f"\n  [Simulating human decision: REJECT]")
    print(f"  Feedback: {feedback}")
    result2 = gate.process_decision("R", feedback, report2)

    print(f"\n  Regenerating with feedback...")
    report2_v2 = generate_legal_report(TOPIC, feedback=feedback)
    print(f"  ✅ Regenerated: {report2_v2['word_count']} words")
    print(f"\n  [Simulating second review: APPROVE]")
    result2b = gate.process_decision("A", "", report2_v2)
    print(f"  Decision logged: {result2b['decision']}")

    # ── Demo 3: ESCALATE flow ─────────────────────────────────────────────────
    print("\n\n── DEMO 3: ESCALATE FLOW ───────────────────────────────")
    SENSITIVE_TOPIC = (
        "A senior partner has been accused of workplace harassment. "
        "What are the firm's legal obligations?"
    )
    print("  Generating report on sensitive topic...")
    report3 = generate_legal_report(SENSITIVE_TOPIC)
    print(f"  ✅ Report generated: {report3['word_count']} words")
    print(f"\n  [Simulating human decision: ESCALATE]")
    result3 = gate.process_decision("E", "", report3)
    print(f"  Decision logged: {result3['decision']}")

    # ── Save log and summary ──────────────────────────────────────────────────
    gate.save_review_log()

    print("\n" + "="*65)
    print("  HITL GATE #2 — ALL FLOWS VERIFIED")
    print("="*65)
    print(f"  Total reviews:     {len(gate.review_log)}")
    print(f"  APPROVED:          {sum(1 for r in gate.review_log if r['decision'] == 'APPROVED')}")
    print(f"  REJECTED:          {sum(1 for r in gate.review_log if r['decision'] == 'REJECTED')}")
    print(f"  ESCALATED:         {sum(1 for r in gate.review_log if r['decision'] == 'ESCALATED')}")
    print(f"  Review log:        day19_review_log.json")
    print("="*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I added a human-in-the-loop approval gate to my")
    print("  multi-agent legal research pipeline. No AI report")
    print("  reaches a client without human sign-off. The gate")
    print("  has three outcomes — Approve, Reject with feedback,")
    print("  or Escalate to senior partner. Rejected reports are")
    print("  automatically regenerated incorporating the reviewer's")
    print("  feedback. The full review trail is logged to JSON.")
    print("  " + "-"*56 + "\n")


# ── Interactive Mode ──────────────────────────────────────────────────────────

def run_interactive():
    """
    Runs the HITL gate interactively — you make the decisions.
    """
    print("\n" + "="*65)
    print("  DAY 19 — HITL GATE #2 — INTERACTIVE MODE")
    print("  Date: Wednesday 13 May 2026")
    print("="*65)

    gate = HITLReportGate()
    topic = (
        "Key employer obligations under the UK Worker Protection "
        "Act 2023 — what firms must do to comply."
    )

    max_iterations = 3
    iteration = 0
    feedback = None
    approved = False

    while not approved and iteration < max_iterations:
        iteration += 1
        print(f"\n  Generating report (attempt {iteration})...")
        report = generate_legal_report(topic, feedback=feedback)
        gate.display_report(report)

        decision, feedback = gate.get_human_decision()
        result = gate.process_decision(decision, feedback, report)

        if decision == "A":
            approved = True
        elif decision == "E":
            print("\n  Report escalated. Ending review session.")
            break

    if iteration >= max_iterations and not approved:
        print(f"\n  ⚠️  Maximum iterations ({max_iterations}) reached.")

    gate.save_review_log()


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive()
    else:
        run_automated_demo()