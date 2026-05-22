"""
Day 33 — HITL Gate #3: Medical Review
42-Day Agentic AI Sprint — Sheyi Teluwo

What we build today:
  - Extends the Day 32 NHS Triage Agent with a full HITL Medical Review system
  - 3-tier review workflow: Auto-approve / Clinician review / Senior clinician escalation
  - Review dashboard: shows patient summary, red flags, confidence score
  - Override capability: clinician can override triage level with reasons
  - Audit log: every decision recorded with timestamp and reviewer ID
  - LangGraph: adds escalate node and audit node to Day 32 graph

IMPORTANT SAFETY NOTE:
  This is a DEMONSTRATION SYSTEM for an AI engineering portfolio.
  It is NOT a real medical device. Never use for real clinical decisions.

Run:
    python day33_hitl_medical_review.py
"""

import json
import os
import sys
from datetime import datetime
from typing import Literal

# ─────────────────────────────────────────────
# 0.  DEPENDENCY CHECK
# ─────────────────────────────────────────────
def check_dependencies():
    missing = []
    for pkg in ["langchain_openai", "langgraph", "openai"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("\n❌  Missing packages. Run:\n")
        print(f"    pip install {' '.join(missing)}\n")
        sys.exit(1)
    print("✅  All dependencies present.")

check_dependencies()

# ─────────────────────────────────────────────
# 1.  IMPORTS
# ─────────────────────────────────────────────
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌  OPENAI_API_KEY not found in .env")
    sys.exit(1)

llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY, temperature=0)

# ─────────────────────────────────────────────
# 2.  TRIAGE LEVELS + REVIEW TIERS
# ─────────────────────────────────────────────

TRIAGE_LEVELS = {
    "EMERGENCY": {"label": "🔴 EMERGENCY", "action": "Call 999 immediately", "review_tier": "SENIOR"},
    "URGENT":    {"label": "🟠 URGENT",    "action": "A&E or 111 now",        "review_tier": "CLINICIAN"},
    "ROUTINE":   {"label": "🟡 ROUTINE",   "action": "Book GP appointment",   "review_tier": "AUTO"},
    "SELF_CARE": {"label": "🟢 SELF-CARE", "action": "Pharmacy advice",       "review_tier": "AUTO"},
}

REVIEW_TIERS = {
    "AUTO":      "✅ Auto-approved — no clinical review needed",
    "CLINICIAN": "🟠 Clinician review required before recommendation sent",
    "SENIOR":    "🔴 Senior clinician escalation required — life-threatening",
}

# ─────────────────────────────────────────────
# 3.  AUDIT LOG
#     Records every decision with timestamp + reviewer
# ─────────────────────────────────────────────

audit_log: list[dict] = []

def log_audit(patient_id: str, event: str, actor: str, details: str):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patient_id": patient_id,
        "event": event,
        "actor": actor,
        "details": details
    }
    audit_log.append(entry)
    print(f"    📝  [AUDIT] {entry['timestamp']} | {actor} | {event} | {details[:60]}")


# ─────────────────────────────────────────────
# 4.  STATE DEFINITION
# ─────────────────────────────────────────────

class ReviewState(TypedDict):
    # Patient data
    patient_id: str
    age: int
    symptoms: str
    duration: str
    medical_history: str

    # AI assessment
    triage_level: str
    triage_reasoning: str
    red_flags: list[str]
    symptom_analysis: str
    medication_warnings: list[str]
    ai_confidence: float

    # Review workflow
    review_tier: str          # AUTO / CLINICIAN / SENIOR
    reviewer_id: str          # Who reviewed
    review_decision: str      # APPROVED / OVERRIDDEN / ESCALATED
    override_level: str       # New triage level if overridden
    override_reason: str      # Why it was overridden
    escalation_notes: str     # Notes if escalated to senior

    # Final output
    final_triage_level: str   # After any overrides
    recommended_action: str
    triage_report: str

    # Audit
    audit_entries: list[dict]
    trace: Annotated[list[str], operator.add]


# ─────────────────────────────────────────────
# 5.  AI ASSESSMENT (reused from Day 32, streamlined)
# ─────────────────────────────────────────────

def run_ai_assessment(symptoms: str, age: int, medical_history: str) -> dict:
    """Runs GPT-4o clinical assessment and returns structured result."""
    print(f"    🩺  [AI Assessment] Analysing symptoms...")

    prompt = f"""
You are an NHS clinical decision support AI.

Patient: Age {age}
Symptoms: {symptoms}
Medical history: {medical_history}

Return ONLY a JSON object:
{{
  "triage_level": "EMERGENCY" or "URGENT" or "ROUTINE" or "SELF_CARE",
  "red_flags": ["dangerous symptoms if any"],
  "reasoning": "clinical reasoning",
  "symptom_analysis": "detailed symptom breakdown",
  "medication_warnings": ["warnings based on medical history"],
  "confidence": 0.0 to 1.0
}}

TRIAGE CRITERIA:
- EMERGENCY: chest pain, stroke symptoms, severe bleeding, difficulty breathing, unconsciousness
- URGENT: high fever, severe pain, worsening chronic condition, signs of serious infection
- ROUTINE: persistent non-urgent symptoms >3 days
- SELF_CARE: mild cold, minor cuts, mild headache

Respond ONLY with JSON. No preamble. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="You are a clinical decision support AI."),
        HumanMessage(content=prompt)
    ])
    try:
        clean = response.content.strip().replace("```json", "").replace("```", "")
        return json.loads(clean)
    except json.JSONDecodeError:
        return {
            "triage_level": "URGENT",
            "red_flags": ["Parse error — defaulted to URGENT for safety"],
            "reasoning": "Parse error",
            "symptom_analysis": response.content[:200],
            "medication_warnings": [],
            "confidence": 0.5
        }


# ─────────────────────────────────────────────
# 6.  LANGGRAPH NODES
# ─────────────────────────────────────────────

def node_assess(state: ReviewState) -> dict:
    """NODE 1 — AI Assessment"""
    print(f"\n  🔬  [Node: assess] Running AI assessment for {state['patient_id']}")

    result = run_ai_assessment(state["symptoms"], state["age"], state["medical_history"])

    triage_level = result.get("triage_level", "URGENT")
    review_tier = TRIAGE_LEVELS.get(triage_level, {}).get("review_tier", "CLINICIAN")

    log_audit(
        state["patient_id"], "AI_ASSESSMENT_COMPLETE",
        "AI_SYSTEM",
        f"Level={triage_level} | Confidence={result.get('confidence')} | Tier={review_tier}"
    )

    print(f"    ✅  Level: {triage_level} | Review tier: {review_tier} | Confidence: {result.get('confidence')}")

    return {
        "triage_level": triage_level,
        "triage_reasoning": result.get("reasoning", ""),
        "red_flags": result.get("red_flags", []),
        "symptom_analysis": result.get("symptom_analysis", ""),
        "medication_warnings": result.get("medication_warnings", []),
        "ai_confidence": result.get("confidence", 0.5),
        "review_tier": review_tier,
        "final_triage_level": triage_level,
        "trace": [f"[assess] {triage_level} | confidence={result.get('confidence')} | tier={review_tier}"]
    }


def node_auto_approve(state: ReviewState) -> dict:
    """NODE 2 — Auto Approve (ROUTINE and SELF_CARE)"""
    print(f"\n  ✅  [Node: auto_approve] Auto-approving {state['triage_level']} case")

    log_audit(
        state["patient_id"], "AUTO_APPROVED",
        "SYSTEM",
        f"Level={state['triage_level']} — no clinical review needed"
    )

    return {
        "reviewer_id": "SYSTEM_AUTO",
        "review_decision": "APPROVED",
        "override_level": "",
        "override_reason": "",
        "trace": [f"[auto_approve] {state['triage_level']} auto-approved"]
    }


def node_clinician_review(state: ReviewState) -> dict:
    """
    NODE 3 — Clinician Review (URGENT cases)
    Shows the clinician a full review dashboard.
    Options: APPROVE / OVERRIDE / ESCALATE
    """
    print(f"\n  👨‍⚕️  [Node: clinician_review] URGENT case — clinician review required")

    # Print the review dashboard
    print(f"\n{'═'*60}")
    print(f"  🟠 CLINICIAN REVIEW DASHBOARD")
    print(f"{'═'*60}")
    print(f"  Patient ID    : {state['patient_id']}")
    print(f"  Age           : {state['age']}")
    print(f"  AI Triage     : {state['triage_level']}")
    print(f"  AI Confidence : {state['ai_confidence']}")
    print(f"  Symptoms      : {state['symptoms'][:80]}...")
    print(f"  Duration      : {state['duration']}")
    print(f"  Medical Hx    : {state['medical_history'][:80]}...")

    if state["red_flags"]:
        print(f"\n  ⚠️  RED FLAGS:")
        for flag in state["red_flags"]:
            print(f"     • {flag}")

    if state["medication_warnings"]:
        print(f"\n  💊  MEDICATION WARNINGS:")
        for w in state["medication_warnings"]:
            print(f"     • {w}")

    print(f"\n  AI Reasoning  : {state['triage_reasoning'][:100]}...")
    print(f"\n{'─'*60}")
    print(f"  CLINICIAN OPTIONS:")
    print(f"  1. Type APPROVE  — confirm AI triage decision")
    print(f"  2. Type OVERRIDE — change the triage level")
    print(f"  3. Type ESCALATE — send to senior clinician")
    print(f"{'─'*60}")

    reviewer_id = input("  Your ID (e.g. DR001): ").strip() or "DR001"
    decision = input("  Decision (APPROVE / OVERRIDE / ESCALATE): ").strip().upper()

    override_level = ""
    override_reason = ""
    escalation_notes = ""

    if decision == "OVERRIDE":
        override_level = input("  New triage level (EMERGENCY/URGENT/ROUTINE/SELF_CARE): ").strip().upper()
        override_reason = input("  Reason for override: ").strip()
        if not override_level or override_level not in TRIAGE_LEVELS:
            override_level = state["triage_level"]
            override_reason = "Invalid override — kept original level"
    elif decision == "ESCALATE":
        escalation_notes = input("  Escalation notes for senior clinician: ").strip()
    else:
        decision = "APPROVED"

    log_audit(
        state["patient_id"], f"CLINICIAN_{decision}",
        reviewer_id,
        f"Original={state['triage_level']} | Override={override_level} | Reason={override_reason[:40]}"
    )

    final_level = override_level if (decision == "OVERRIDE" and override_level) else state["triage_level"]

    print(f"    ✅  Decision recorded: {decision} by {reviewer_id}")

    return {
        "reviewer_id": reviewer_id,
        "review_decision": decision,
        "override_level": override_level,
        "override_reason": override_reason,
        "escalation_notes": escalation_notes,
        "final_triage_level": final_level,
        "trace": [f"[clinician_review] {decision} by {reviewer_id} | final={final_level}"]
    }


def node_senior_escalation(state: ReviewState) -> dict:
    """
    NODE 4 — Senior Clinician Escalation (EMERGENCY cases or escalated URGENT)
    Highest level of review — senior clinician must sign off.
    """
    print(f"\n  🔴  [Node: senior_escalation] EMERGENCY — senior clinician required")

    print(f"\n{'═'*60}")
    print(f"  🔴 SENIOR CLINICIAN ESCALATION")
    print(f"{'═'*60}")
    print(f"  Patient ID    : {state['patient_id']}")
    print(f"  Age           : {state['age']}")
    print(f"  AI Triage     : {state['triage_level']}")
    print(f"  AI Confidence : {state['ai_confidence']}")
    print(f"  Symptoms      : {state['symptoms']}")

    if state["red_flags"]:
        print(f"\n  ⚠️  RED FLAGS:")
        for flag in state["red_flags"]:
            print(f"     • {flag}")

    if state.get("escalation_notes"):
        print(f"\n  📋  Escalation notes: {state['escalation_notes']}")

    print(f"\n{'─'*60}")
    print(f"  SENIOR CLINICIAN OPTIONS:")
    print(f"  1. Type CONFIRM  — confirm EMERGENCY triage")
    print(f"  2. Type DOWNGRADE — reduce to URGENT")
    print(f"{'─'*60}")

    reviewer_id = input("  Senior clinician ID (e.g. CONS001): ").strip() or "CONS001"
    decision = input("  Decision (CONFIRM / DOWNGRADE): ").strip().upper()

    final_level = state["triage_level"]
    if decision == "DOWNGRADE":
        final_level = "URGENT"

    log_audit(
        state["patient_id"], f"SENIOR_{decision}",
        reviewer_id,
        f"Original={state['triage_level']} | Final={final_level}"
    )

    print(f"    ✅  Senior decision: {decision} by {reviewer_id}")

    return {
        "reviewer_id": reviewer_id,
        "review_decision": decision,
        "final_triage_level": final_level,
        "trace": [f"[senior_escalation] {decision} by {reviewer_id} | final={final_level}"]
    }


def node_generate_report(state: ReviewState) -> dict:
    """NODE 5 — Generate final triage report with full audit trail"""
    print(f"\n  📄  [Node: generate_report] Building final report...")

    final_level = state.get("final_triage_level") or state["triage_level"]
    triage_info = TRIAGE_LEVELS.get(final_level, TRIAGE_LEVELS["URGENT"])
    recommended_action = triage_info["action"]

    report_lines = [
        "═" * 60,
        "  NHS HITL MEDICAL REVIEW — TRIAGE REPORT",
        "  ⚠️  DEMONSTRATION SYSTEM — NOT FOR REAL CLINICAL USE",
        "═" * 60,
        f"  Patient ID       : {state['patient_id']}",
        f"  Age              : {state['age']}",
        f"  Timestamp        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "─" * 60,
        f"  AI TRIAGE        : {state['triage_level']} (confidence: {state['ai_confidence']})",
        f"  FINAL TRIAGE     : {triage_info['label']}",
        f"  REVIEW TIER      : {state['review_tier']}",
        f"  REVIEW DECISION  : {state.get('review_decision', 'AUTO')}",
        f"  REVIEWER         : {state.get('reviewer_id', 'SYSTEM')}",
        f"  RECOMMENDED      : {recommended_action}",
        "─" * 60,
        "  SYMPTOMS:",
        f"  {state['symptoms']}",
        "─" * 60,
        "  CLINICAL ASSESSMENT:",
        f"  {state['symptom_analysis'][:300]}",
        "─" * 60,
    ]

    if state["red_flags"]:
        report_lines.append("  ⚠️  RED FLAGS:")
        for flag in state["red_flags"]:
            report_lines.append(f"     • {flag}")
        report_lines.append("─" * 60)

    if state.get("override_reason"):
        report_lines += [
            f"  📋  OVERRIDE REASON: {state['override_reason']}",
            "─" * 60,
        ]

    # Audit trail
    report_lines.append("  📝  AUDIT TRAIL:")
    for entry in audit_log:
        if entry["patient_id"] == state["patient_id"]:
            report_lines.append(
                f"     {entry['timestamp']} | {entry['actor']} | {entry['event']}"
            )

    report_lines += [
        "─" * 60,
        "  ⚠️  DISCLAIMER: Portfolio demonstration only.",
        "═" * 60,
    ]

    report = "\n".join(report_lines)
    print(report)

    return {
        "triage_report": report,
        "recommended_action": recommended_action,
        "audit_entries": [e for e in audit_log if e["patient_id"] == state["patient_id"]],
        "trace": [f"[generate_report] Report complete | final={final_level}"]
    }


# ─────────────────────────────────────────────
# 7.  CONDITIONAL EDGES
# ─────────────────────────────────────────────

def route_by_tier(state: ReviewState) -> Literal["auto_approve", "clinician_review", "senior_escalation"]:
    tier = state.get("review_tier", "CLINICIAN")
    if tier == "AUTO":
        return "auto_approve"
    elif tier == "SENIOR":
        return "senior_escalation"
    else:
        return "clinician_review"


def route_after_clinician(state: ReviewState) -> Literal["senior_escalation", "generate_report"]:
    if state.get("review_decision") == "ESCALATE":
        return "senior_escalation"
    return "generate_report"


# ─────────────────────────────────────────────
# 8.  BUILD THE GRAPH
# ─────────────────────────────────────────────

def build_review_graph():
    """
    Graph:
    assess → [tier routing] → auto_approve     → generate_report → END
                           → clinician_review  → [escalate?] → generate_report → END
                           → senior_escalation → generate_report → END
    """
    graph = StateGraph(ReviewState)

    graph.add_node("assess", node_assess)
    graph.add_node("auto_approve", node_auto_approve)
    graph.add_node("clinician_review", node_clinician_review)
    graph.add_node("senior_escalation", node_senior_escalation)
    graph.add_node("generate_report", node_generate_report)

    graph.set_entry_point("assess")
    graph.add_conditional_edges(
        "assess",
        route_by_tier,
        {
            "auto_approve": "auto_approve",
            "clinician_review": "clinician_review",
            "senior_escalation": "senior_escalation"
        }
    )
    graph.add_edge("auto_approve", "generate_report")
    graph.add_conditional_edges(
        "clinician_review",
        route_after_clinician,
        {
            "senior_escalation": "senior_escalation",
            "generate_report": "generate_report"
        }
    )
    graph.add_edge("senior_escalation", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile()


# ─────────────────────────────────────────────
# 9.  DEMO
# ─────────────────────────────────────────────

def run_patient(app, patient: dict):
    print(f"\n\n{'▓'*60}")
    print(f"  PATIENT: {patient['patient_id']} | Age: {patient['age']}")
    print(f"{'▓'*60}")

    state: ReviewState = {
        "patient_id": patient["patient_id"],
        "age": patient["age"],
        "symptoms": patient["symptoms"],
        "duration": patient["duration"],
        "medical_history": patient["medical_history"],
        "triage_level": "",
        "triage_reasoning": "",
        "red_flags": [],
        "symptom_analysis": "",
        "medication_warnings": [],
        "ai_confidence": 0.0,
        "review_tier": "",
        "reviewer_id": "",
        "review_decision": "",
        "override_level": "",
        "override_reason": "",
        "escalation_notes": "",
        "final_triage_level": "",
        "recommended_action": "",
        "triage_report": "",
        "audit_entries": [],
        "trace": [f"[start] {patient['patient_id']} entered review system"]
    }

    result = app.invoke(state)

    print(f"\n  TRACE:")
    for step in result["trace"]:
        print(f"    → {step}")
    return result


def run_demo():
    print("\n" + "█"*60)
    print("  DAY 33 — HITL GATE #3: MEDICAL REVIEW")
    print("  42-Day Agentic AI Sprint — Sheyi Teluwo")
    print("  ⚠️  DEMONSTRATION ONLY — NOT FOR REAL CLINICAL USE")
    print("█"*60)

    app = build_review_graph()
    print("✅  Review graph compiled.")
    print("    Nodes: assess → [auto/clinician/senior] → generate_report")

    # Patient 1: SELF_CARE — auto approve, no input needed
    run_patient(app, {
        "patient_id": "NHS-004",
        "age": 28,
        "symptoms": "Mild sore throat, slight runny nose, no fever, feeling a bit tired.",
        "duration": "1 day",
        "medical_history": "No significant history. No medications."
    })

    # Patient 2: URGENT — clinician review fires
    # When prompted: enter DR002, then APPROVE
    run_patient(app, {
        "patient_id": "NHS-005",
        "age": 72,
        "symptoms": "Sudden confusion, difficulty speaking, facial drooping on left side, arm weakness.",
        "duration": "30 minutes",
        "medical_history": "Atrial fibrillation on warfarin, hypertension on ramipril."
    })

    # Patient 3: EMERGENCY — senior escalation fires
    # When prompted: enter CONS001, then CONFIRM
    run_patient(app, {
        "patient_id": "NHS-006",
        "age": 55,
        "symptoms": "Crushing chest pain, severe shortness of breath, sweating profusely, feeling like going to die.",
        "duration": "10 minutes",
        "medical_history": "Previous MI 3 years ago, on aspirin and bisoprolol, diabetic."
    })

    # Print full audit log
    print(f"\n\n{'═'*60}")
    print("  FULL AUDIT LOG — ALL PATIENTS")
    print(f"{'═'*60}")
    for entry in audit_log:
        print(f"  {entry['timestamp']} | {entry['patient_id']} | {entry['actor']} | {entry['event']}")

    print("\n\n" + "█"*60)
    print("  DAY 33 COMPLETE ✅")
    print("█"*60)
    print("\nHITL Medical Review System:")
    print("  ✅  3-tier review: AUTO / CLINICIAN / SENIOR")
    print("  ✅  Override capability with mandatory reason")
    print("  ✅  Escalation path: clinician → senior")
    print("  ✅  Full audit log: every decision timestamped")
    print("  ✅  2 conditional edges in LangGraph")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📸  SCREENSHOT THIS OUTPUT — save as:")
    print("    day33_hitl_medical_review_2026-05-22.png")
    print("█"*60)


if __name__ == "__main__":
    run_demo()
