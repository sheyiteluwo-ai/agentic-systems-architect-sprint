"""
Day 32 — NHS Use Case: Patient Triage Agent
42-Day Agentic AI Sprint — Sheyi Teluwo

What we build today:
  - A Patient Triage Agent for NHS use
  - Classifies patient symptoms into: EMERGENCY / URGENT / ROUTINE / SELF_CARE
  - 4 triage tools: symptom checker, medication checker, wait time lookup, GP finder
  - LangGraph state machine: intake → assess → triage → recommend → END
  - HITL Gate: EMERGENCY and URGENT cases always pause for clinician review
  - Structured triage report output

IMPORTANT SAFETY NOTE:
  This is a DEMONSTRATION SYSTEM for an AI engineering portfolio.
  It is NOT a real medical device. It must never be used for real medical decisions.
  Real NHS triage systems require CQC registration and clinical validation.

Run:
    python day32_nhs_triage_agent.py
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
# 2.  TRIAGE LEVELS
# ─────────────────────────────────────────────
TRIAGE_LEVELS = {
    "EMERGENCY": {
        "label": "🔴 EMERGENCY",
        "action": "Call 999 immediately",
        "timeframe": "Immediate — within minutes",
        "requires_hitl": True
    },
    "URGENT": {
        "label": "🟠 URGENT",
        "action": "Go to A&E or call 111 now",
        "timeframe": "Within 1–2 hours",
        "requires_hitl": True
    },
    "ROUTINE": {
        "label": "🟡 ROUTINE",
        "action": "Book a GP appointment",
        "timeframe": "Within 24–72 hours",
        "requires_hitl": False
    },
    "SELF_CARE": {
        "label": "🟢 SELF-CARE",
        "action": "Manage at home with pharmacy advice",
        "timeframe": "Monitor symptoms",
        "requires_hitl": False
    }
}

# ─────────────────────────────────────────────
# 3.  STATE DEFINITION
# ─────────────────────────────────────────────

class TriageState(TypedDict):
    # Patient input
    patient_id: str
    age: int
    symptoms: str
    duration: str
    medical_history: str

    # Assessment outputs
    triage_level: str           # EMERGENCY / URGENT / ROUTINE / SELF_CARE
    triage_reasoning: str       # Why this level was chosen
    red_flags: list[str]        # Dangerous symptoms identified
    symptom_analysis: str       # Detailed symptom breakdown
    medication_warnings: list[str]  # Drug interactions / contraindications
    recommended_action: str     # What to do next
    nearest_service: str        # NHS service recommendation

    # HITL fields
    requires_clinician_review: bool
    clinician_feedback: str
    clinician_approved: bool

    # Report
    triage_report: str
    timestamp: str

    # Audit trail
    trace: Annotated[list[str], operator.add]


# ─────────────────────────────────────────────
# 4.  TRIAGE TOOLS
#     These simulate NHS data lookups.
#     In production these would call real NHS APIs (NHS Digital, etc.)
# ─────────────────────────────────────────────

def tool_symptom_checker(symptoms: str, age: int, medical_history: str) -> dict:
    """
    Simulates NHS symptom checker logic.
    In production: calls NHS Digital Symptom Checker API.
    """
    print(f"    🩺  [SymptomChecker] Analysing: '{symptoms[:50]}...'")

    prompt = f"""
You are an NHS clinical decision support system.

Patient details:
- Age: {age}
- Symptoms: {symptoms}
- Medical history: {medical_history}

Analyse the symptoms and return a JSON object with:
{{
  "triage_level": "EMERGENCY" or "URGENT" or "ROUTINE" or "SELF_CARE",
  "red_flags": ["list of dangerous symptoms if any"],
  "reasoning": "clinical reasoning for triage decision",
  "symptom_analysis": "detailed breakdown of what the symptoms suggest",
  "confidence": 0.0 to 1.0
}}

TRIAGE CRITERIA:
- EMERGENCY: chest pain, difficulty breathing, stroke symptoms, severe bleeding, unconsciousness, anaphylaxis
- URGENT: high fever >39C, severe pain, signs of infection, worsening chronic condition
- ROUTINE: persistent but non-urgent symptoms lasting more than 3 days
- SELF_CARE: mild cold, minor cuts, mild headache, mild indigestion

Respond ONLY with the JSON object. No preamble. No markdown.
"""
    response = llm.invoke([SystemMessage(content="You are a clinical decision support AI."),
                           HumanMessage(content=prompt)])
    try:
        clean = response.content.strip().replace("```json", "").replace("```", "")
        result = json.loads(clean)
    except json.JSONDecodeError:
        result = {
            "triage_level": "URGENT",
            "red_flags": ["Unable to parse symptoms — defaulting to URGENT for safety"],
            "reasoning": "Parse error — escalated for safety",
            "symptom_analysis": response.content,
            "confidence": 0.5
        }

    print(f"    ✅  Triage level: {result.get('triage_level')} | Confidence: {result.get('confidence')}")
    return result


def tool_medication_checker(symptoms: str, medical_history: str) -> dict:
    """
    Checks for medication warnings and contraindications.
    In production: calls NHS BNF (British National Formulary) API.
    """
    print(f"    💊  [MedicationChecker] Checking contraindications...")

    prompt = f"""
You are an NHS pharmacy decision support system.

Patient symptoms: {symptoms}
Medical history (may include current medications): {medical_history}

Check for:
1. Any over-the-counter medications that are UNSAFE given the history
2. Any drug interactions to warn about
3. Safe OTC recommendations if appropriate

Return JSON:
{{
  "warnings": ["list of warnings if any"],
  "safe_otc_options": ["safe over-the-counter options if self-care appropriate"],
  "contraindications": ["list of contraindicated drugs"]
}}

Respond ONLY with the JSON. No preamble. No markdown.
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        clean = response.content.strip().replace("```json", "").replace("```", "")
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"warnings": [], "safe_otc_options": [], "contraindications": []}


def tool_wait_time_lookup(triage_level: str) -> dict:
    """
    Simulates NHS 111 wait time data.
    In production: calls NHS Capacity Management API.
    """
    print(f"    ⏱️   [WaitTimeLookup] Looking up wait times for: {triage_level}")

    # Simulated NHS wait time data (representative 2026 figures)
    wait_times = {
        "EMERGENCY": {
            "service": "999 / A&E Resus",
            "average_wait": "Immediate",
            "nearest_ae": "Your nearest Major A&E",
            "note": "Call 999 — do not travel yourself"
        },
        "URGENT": {
            "service": "A&E / Urgent Treatment Centre",
            "average_wait": "2–4 hours at A&E | 45 mins at UTC",
            "nearest_ae": "Check NHS 111 online for nearest UTC",
            "note": "Urgent Treatment Centres are faster for non-life-threatening urgent cases"
        },
        "ROUTINE": {
            "service": "GP Surgery",
            "average_wait": "1–3 days for routine appointment",
            "nearest_ae": "Contact your registered GP",
            "note": "Use NHS App to book online"
        },
        "SELF_CARE": {
            "service": "Pharmacy",
            "average_wait": "Walk-in — no wait",
            "nearest_ae": "Your local pharmacy",
            "note": "Pharmacists can prescribe for 7 common conditions under Pharmacy First"
        }
    }

    result = wait_times.get(triage_level, wait_times["ROUTINE"])
    print(f"    ✅  Service: {result['service']}")
    return result


def tool_gp_finder(triage_level: str) -> dict:
    """
    Simulates NHS GP/service finder.
    In production: calls NHS Find a GP API.
    """
    print(f"    🏥  [GPFinder] Finding appropriate NHS service...")

    services = {
        "EMERGENCY": {
            "primary": "999 Emergency Services",
            "secondary": "A&E Department",
            "digital": "N/A — call 999",
            "phone": "999"
        },
        "URGENT": {
            "primary": "NHS 111",
            "secondary": "Urgent Treatment Centre",
            "digital": "111.nhs.uk",
            "phone": "111"
        },
        "ROUTINE": {
            "primary": "Registered GP Surgery",
            "secondary": "NHS Walk-in Centre",
            "digital": "NHS App (nhsapp.service.nhs.uk)",
            "phone": "Your GP surgery number"
        },
        "SELF_CARE": {
            "primary": "Community Pharmacy (Pharmacy First)",
            "secondary": "NHS 111 Online",
            "digital": "111.nhs.uk or NHS App",
            "phone": "111 if symptoms worsen"
        }
    }

    result = services.get(triage_level, services["ROUTINE"])
    print(f"    ✅  Primary service: {result['primary']}")
    return result


# ─────────────────────────────────────────────
# 5.  LANGGRAPH NODES
# ─────────────────────────────────────────────

def node_intake(state: TriageState) -> dict:
    """
    NODE 1 — INTAKE
    Validates and logs the patient intake data.
    """
    print(f"\n  📋  [Node: intake] Processing patient {state['patient_id']}")
    print(f"       Age: {state['age']} | Symptoms: {state['symptoms'][:60]}...")

    # Basic validation
    warnings = []
    if state["age"] < 0 or state["age"] > 120:
        warnings.append("Invalid age — defaulting safety protocols")
    if len(state["symptoms"]) < 5:
        warnings.append("Insufficient symptom description")

    print(f"    ✅  Intake complete. Warnings: {warnings if warnings else 'None'}")

    return {
        "timestamp": datetime.now().isoformat(),
        "trace": [f"[intake] Patient {state['patient_id']} | Age {state['age']} | {datetime.now().strftime('%H:%M:%S')}"]
    }


def node_assess(state: TriageState) -> dict:
    """
    NODE 2 — ASSESS
    Runs symptom checker and medication checker tools.
    """
    print(f"\n  🔬  [Node: assess] Running clinical assessment tools...")

    # Run symptom checker
    symptom_result = tool_symptom_checker(
        state["symptoms"],
        state["age"],
        state["medical_history"]
    )

    # Run medication checker
    med_result = tool_medication_checker(
        state["symptoms"],
        state["medical_history"]
    )

    triage_level = symptom_result.get("triage_level", "URGENT")
    red_flags = symptom_result.get("red_flags", [])
    reasoning = symptom_result.get("reasoning", "")
    symptom_analysis = symptom_result.get("symptom_analysis", "")
    med_warnings = med_result.get("warnings", [])

    print(f"    ✅  Assessment complete | Level: {triage_level} | Red flags: {len(red_flags)}")

    return {
        "triage_level": triage_level,
        "triage_reasoning": reasoning,
        "red_flags": red_flags,
        "symptom_analysis": symptom_analysis,
        "medication_warnings": med_warnings,
        "trace": [f"[assess] Level={triage_level} | RedFlags={red_flags} | MedWarnings={len(med_warnings)}"]
    }


def node_triage(state: TriageState) -> dict:
    """
    NODE 3 — TRIAGE
    Looks up wait times and NHS service, sets HITL flag.
    """
    print(f"\n  🏷️   [Node: triage] Finalising triage level: {state['triage_level']}")

    triage_level = state["triage_level"]
    triage_info = TRIAGE_LEVELS.get(triage_level, TRIAGE_LEVELS["URGENT"])

    # Look up NHS services
    wait_info = tool_wait_time_lookup(triage_level)
    service_info = tool_gp_finder(triage_level)

    nearest_service = (
        f"{service_info['primary']} | "
        f"Wait: {wait_info['average_wait']} | "
        f"Contact: {service_info['phone']}"
    )

    recommended_action = (
        f"{triage_info['action']} — {triage_info['timeframe']}. "
        f"{wait_info.get('note', '')}"
    )

    requires_review = triage_info["requires_hitl"]

    print(f"    ✅  Action: {triage_info['action']} | HITL required: {requires_review}")

    return {
        "nearest_service": nearest_service,
        "recommended_action": recommended_action,
        "requires_clinician_review": requires_review,
        "clinician_approved": False,
        "trace": [f"[triage] {triage_level} | HITL={requires_review} | Action={triage_info['action']}"]
    }


def node_clinician_review(state: TriageState) -> dict:
    """
    NODE 4 — CLINICIAN REVIEW (HITL Gate)
    Fires for EMERGENCY and URGENT cases.
    Pauses the pipeline for human clinician approval.
    """
    level_info = TRIAGE_LEVELS.get(state["triage_level"], {})

    print(f"\n  👨‍⚕️  [Node: clinician_review] {level_info.get('label', 'REVIEW REQUIRED')}")
    print(f"\n{'─'*60}")
    print(f"  ⚠️  CLINICIAN REVIEW REQUIRED")
    print(f"{'─'*60}")
    print(f"  Patient ID  : {state['patient_id']}")
    print(f"  Age         : {state['age']}")
    print(f"  Triage Level: {state['triage_level']}")
    print(f"  Symptoms    : {state['symptoms']}")
    print(f"  Red Flags   : {', '.join(state['red_flags']) if state['red_flags'] else 'None identified'}")
    print(f"  Reasoning   : {state['triage_reasoning']}")
    print(f"  Recommended : {state['recommended_action']}")
    print(f"\n  Options:")
    print(f"  1. Type APPROVE to confirm this triage decision")
    print(f"  2. Type DOWNGRADE to reduce to ROUTINE")
    print(f"  3. Type your own notes/override")
    print(f"{'─'*60}")

    feedback = input("  Clinician decision: ").strip()

    approved = True
    if feedback.upper() == "APPROVE" or feedback == "":
        feedback = "APPROVED by clinician"
        approved = True
    elif feedback.upper() == "DOWNGRADE":
        feedback = "DOWNGRADED to ROUTINE by clinician"
        approved = True
    else:
        approved = True  # any feedback counts as reviewed

    print(f"    ✅  Clinician review recorded: '{feedback}'")

    return {
        "clinician_feedback": feedback,
        "clinician_approved": approved,
        "trace": [f"[clinician_review] feedback='{feedback}' | approved={approved}"]
    }


def node_recommend(state: TriageState) -> dict:
    """
    NODE 5 — RECOMMEND
    Generates the full structured triage report.
    """
    print(f"\n  📄  [Node: recommend] Generating triage report...")

    triage_info = TRIAGE_LEVELS.get(state["triage_level"], TRIAGE_LEVELS["URGENT"])

    # Build the triage report
    report_lines = [
        "═" * 60,
        "  NHS PATIENT TRIAGE REPORT",
        "  ⚠️  DEMONSTRATION SYSTEM — NOT FOR REAL CLINICAL USE",
        "═" * 60,
        f"  Patient ID     : {state['patient_id']}",
        f"  Age            : {state['age']}",
        f"  Timestamp      : {state['timestamp']}",
        "─" * 60,
        f"  TRIAGE LEVEL   : {triage_info['label']}",
        f"  RECOMMENDED    : {state['recommended_action']}",
        f"  NHS SERVICE    : {state['nearest_service']}",
        "─" * 60,
        "  SYMPTOMS REPORTED:",
        f"  {state['symptoms']}",
        "─" * 60,
        "  CLINICAL ASSESSMENT:",
        f"  {state['symptom_analysis']}",
        "─" * 60,
    ]

    if state["red_flags"]:
        report_lines.append("  ⚠️  RED FLAGS IDENTIFIED:")
        for flag in state["red_flags"]:
            report_lines.append(f"     • {flag}")
        report_lines.append("─" * 60)

    if state["medication_warnings"]:
        report_lines.append("  💊  MEDICATION WARNINGS:")
        for w in state["medication_warnings"]:
            report_lines.append(f"     • {w}")
        report_lines.append("─" * 60)

    if state.get("clinician_feedback"):
        report_lines.append(f"  👨‍⚕️  CLINICIAN REVIEW: {state['clinician_feedback']}")
        report_lines.append("─" * 60)

    report_lines += [
        "  REASONING:",
        f"  {state['triage_reasoning']}",
        "─" * 60,
        "  ⚠️  DISCLAIMER: This is a portfolio demonstration system.",
        "  Real clinical triage requires qualified healthcare professionals.",
        "═" * 60,
    ]

    report = "\n".join(report_lines)
    print(report)

    return {
        "triage_report": report,
        "trace": [f"[recommend] Report generated | Level={state['triage_level']}"]
    }


# ─────────────────────────────────────────────
# 6.  CONDITIONAL EDGE
# ─────────────────────────────────────────────

def needs_clinician(state: TriageState) -> Literal["clinician_review", "recommend"]:
    if state.get("requires_clinician_review", False):
        print("    ⚠️   EMERGENCY/URGENT — routing to clinician review")
        return "clinician_review"
    else:
        print("    ✅  ROUTINE/SELF_CARE — routing directly to recommend")
        return "recommend"


# ─────────────────────────────────────────────
# 7.  BUILD THE GRAPH
# ─────────────────────────────────────────────

def build_triage_graph():
    """
    Graph structure:
    intake → assess → triage → [conditional] → recommend → END
                                     ↓
                             clinician_review → recommend → END
    """
    graph = StateGraph(TriageState)

    graph.add_node("intake", node_intake)
    graph.add_node("assess", node_assess)
    graph.add_node("triage", node_triage)
    graph.add_node("clinician_review", node_clinician_review)
    graph.add_node("recommend", node_recommend)

    graph.set_entry_point("intake")
    graph.add_edge("intake", "assess")
    graph.add_edge("assess", "triage")
    graph.add_conditional_edges(
        "triage",
        needs_clinician,
        {
            "clinician_review": "clinician_review",
            "recommend": "recommend"
        }
    )
    graph.add_edge("clinician_review", "recommend")
    graph.add_edge("recommend", END)

    return graph.compile()


# ─────────────────────────────────────────────
# 8.  DEMO PATIENTS
# ─────────────────────────────────────────────

def run_patient(app, patient: dict):
    print(f"\n\n{'▓'*60}")
    print(f"  PATIENT: {patient['patient_id']}")
    print(f"{'▓'*60}")

    initial_state: TriageState = {
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
        "recommended_action": "",
        "nearest_service": "",
        "requires_clinician_review": False,
        "clinician_feedback": "",
        "clinician_approved": False,
        "triage_report": "",
        "timestamp": "",
        "trace": [f"[start] Patient {patient['patient_id']} entered triage system"]
    }

    result = app.invoke(initial_state)

    print(f"\n  TRACE:")
    for step in result["trace"]:
        print(f"    → {step}")

    return result


def run_demo():
    print("\n" + "█"*60)
    print("  DAY 32 — NHS PATIENT TRIAGE AGENT")
    print("  42-Day Agentic AI Sprint — Sheyi Teluwo")
    print("  ⚠️  DEMONSTRATION ONLY — NOT FOR REAL CLINICAL USE")
    print("█"*60)

    app = build_triage_graph()
    print("✅  Triage graph compiled.")

    # ── PATIENT 1: SELF-CARE (no HITL) ────────────────────────
    run_patient(app, {
        "patient_id": "NHS-001",
        "age": 34,
        "symptoms": "Mild headache, runny nose, slight sore throat, feeling tired. No fever.",
        "duration": "2 days",
        "medical_history": "No significant medical history. No regular medications."
    })

    # ── PATIENT 2: ROUTINE (no HITL) ──────────────────────────
    run_patient(app, {
        "patient_id": "NHS-002",
        "age": 58,
        "symptoms": "Persistent cough for 2 weeks, mild breathlessness on exertion, no fever.",
        "duration": "14 days",
        "medical_history": "Type 2 diabetes, managed with metformin. Non-smoker."
    })

    # ── PATIENT 3: URGENT (HITL fires) ────────────────────────
    run_patient(app, {
        "patient_id": "NHS-003",
        "age": 67,
        "symptoms": "Sudden severe chest tightness, pain radiating to left arm, sweating, nausea.",
        "duration": "20 minutes",
        "medical_history": "Hypertension on amlodipine, high cholesterol on statins, previous angina."
    })

    # ── SUMMARY ───────────────────────────────────────────────
    print("\n\n" + "█"*60)
    print("  DAY 32 COMPLETE ✅")
    print("█"*60)
    print("\nNHS Triage Agent:")
    print("  ✅  4 triage tools: symptom checker, medication checker, wait times, GP finder")
    print("  ✅  5 LangGraph nodes: intake, assess, triage, clinician_review, recommend")
    print("  ✅  Conditional HITL: EMERGENCY + URGENT cases pause for clinician")
    print("  ✅  Structured triage report generated for every patient")
    print("  ✅  Full audit trace logged at every node")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📸  SCREENSHOT THIS OUTPUT — save as:")
    print("    day32_nhs_triage_agent_2026-05-21.png")
    print("█"*60)


if __name__ == "__main__":
    run_demo()
