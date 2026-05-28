"""
Day 35 — Barclays Fraud Detection Agent
42-Day Agentic AI Sprint — Sheyi Teluwo

What we build today:
  - A fraud detection agent for a Barclays-style retail bank
  - 5 fraud detection tools: transaction analyser, velocity checker,
    geolocation checker, device fingerprint checker, account history checker
  - LangGraph state machine: ingest → analyse → score → review → action
  - HITL Gate: HIGH and CRITICAL risk transactions pause for analyst review
  - Risk scoring: 0.0-1.0 with thresholds LOW / MEDIUM / HIGH / CRITICAL
  - Action outputs: APPROVE / FLAG / BLOCK / ESCALATE
  - Audit log: every decision recorded for FCA compliance

IMPORTANT:
  This is a DEMONSTRATION SYSTEM for an AI engineering portfolio.
  It is NOT a real fraud detection system.
  Real fraud systems require FCA authorisation and extensive testing.

Run:
    python day35_fraud_detection_agent.py
"""

import json
import os
import sys
import random
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
# 2.  RISK LEVELS + ACTIONS
# ─────────────────────────────────────────────

RISK_LEVELS = {
    "LOW":      {"label": "🟢 LOW",      "threshold": 0.25, "action": "APPROVE",   "hitl": False},
    "MEDIUM":   {"label": "🟡 MEDIUM",   "threshold": 0.50, "action": "FLAG",      "hitl": False},
    "HIGH":     {"label": "🟠 HIGH",     "threshold": 0.75, "action": "BLOCK",     "hitl": True},
    "CRITICAL": {"label": "🔴 CRITICAL", "threshold": 1.00, "action": "ESCALATE",  "hitl": True},
}

def get_risk_level(score: float) -> str:
    if score < 0.25:
        return "LOW"
    elif score < 0.50:
        return "MEDIUM"
    elif score < 0.75:
        return "HIGH"
    else:
        return "CRITICAL"

# ─────────────────────────────────────────────
# 3.  AUDIT LOG
# ─────────────────────────────────────────────

audit_log: list[dict] = []

def log_audit(transaction_id: str, event: str, actor: str, details: str):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_id": transaction_id,
        "event": event,
        "actor": actor,
        "details": details
    }
    audit_log.append(entry)
    print(f"    📝  [AUDIT] {entry['timestamp']} | {actor} | {event}")

# ─────────────────────────────────────────────
# 4.  STATE DEFINITION
# ─────────────────────────────────────────────

class FraudState(TypedDict):
    # Transaction data
    transaction_id: str
    account_id: str
    amount: float
    currency: str
    merchant: str
    merchant_category: str
    country: str
    timestamp: str
    device_id: str
    ip_address: str

    # Tool results
    transaction_analysis: dict
    velocity_check: dict
    geolocation_check: dict
    device_check: dict
    account_history: dict

    # Risk scoring
    risk_score: float
    risk_level: str
    risk_factors: list[str]

    # Decision
    recommended_action: str
    requires_analyst_review: bool
    analyst_id: str
    analyst_decision: str
    analyst_notes: str
    final_action: str

    # Report
    fraud_report: str

    # Audit
    trace: Annotated[list[str], operator.add]


# ─────────────────────────────────────────────
# 5.  FRAUD DETECTION TOOLS
# ─────────────────────────────────────────────

def tool_transaction_analyser(transaction: dict) -> dict:
    """
    Tool 1 — Transaction Analyser
    Uses GPT-4o to assess the transaction for fraud indicators.
    In production: ML model trained on millions of Barclays transactions.
    """
    print(f"    💳  [TransactionAnalyser] Analysing £{transaction['amount']} at {transaction['merchant']}")

    prompt = f"""
You are a fraud detection AI for a UK retail bank.

Analyse this transaction for fraud indicators:
- Amount: £{transaction['amount']}
- Merchant: {transaction['merchant']}
- Merchant category: {transaction['merchant_category']}
- Country: {transaction['country']}
- Time: {transaction['timestamp']}
- Account ID: {transaction['account_id']}

Return ONLY a JSON object:
{{
  "fraud_indicators": ["list of specific fraud indicators found"],
  "transaction_risk_score": 0.0 to 1.0,
  "is_unusual_amount": true or false,
  "is_unusual_merchant": true or false,
  "is_unusual_time": true or false,
  "reasoning": "brief explanation"
}}

Common fraud indicators:
- Very large amounts (>£1000) at unusual merchants
- Transactions at odd hours (2am-5am)
- Unusual merchant categories (crypto, gambling, wire transfer)
- Foreign transactions without prior travel pattern
- Round number amounts (£500.00, £1000.00)

Respond ONLY with JSON. No preamble. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="You are a fraud detection AI."),
        HumanMessage(content=prompt)
    ])
    try:
        clean = response.content.strip().replace("```json", "").replace("```", "")
        result = json.loads(clean)
        print(f"    ✅  Transaction risk score: {result.get('transaction_risk_score')}")
        return result
    except json.JSONDecodeError:
        return {"fraud_indicators": [], "transaction_risk_score": 0.3, "reasoning": "Parse error"}


def tool_velocity_checker(account_id: str, amount: float, timestamp: str) -> dict:
    """
    Tool 2 — Velocity Checker
    Checks if the account has made too many transactions in a short window.
    In production: queries real-time transaction database.
    Simulated here with realistic patterns.
    """
    print(f"    ⚡  [VelocityChecker] Checking transaction velocity for {account_id}")

    # Simulate velocity data
    # In production this would query your transaction DB
    simulated_patterns = {
        "ACC-001": {"transactions_last_hour": 1, "transactions_last_24h": 3, "total_spent_24h": 245.50},
        "ACC-002": {"transactions_last_hour": 8, "transactions_last_24h": 23, "total_spent_24h": 4521.00},
        "ACC-003": {"transactions_last_hour": 2, "transactions_last_24h": 5, "total_spent_24h": 189.00},
        "ACC-FRAUD": {"transactions_last_hour": 15, "transactions_last_24h": 47, "total_spent_24h": 12000.00},
    }

    pattern = simulated_patterns.get(account_id, {
        "transactions_last_hour": random.randint(1, 4),
        "transactions_last_24h": random.randint(2, 8),
        "total_spent_24h": random.uniform(50, 500)
    })

    # Score velocity
    velocity_score = 0.0
    flags = []

    if pattern["transactions_last_hour"] > 5:
        velocity_score += 0.4
        flags.append(f"High transaction frequency: {pattern['transactions_last_hour']} in last hour")
    if pattern["transactions_last_24h"] > 20:
        velocity_score += 0.3
        flags.append(f"Unusual 24h activity: {pattern['transactions_last_24h']} transactions")
    if pattern["total_spent_24h"] > 3000:
        velocity_score += 0.3
        flags.append(f"High 24h spend: £{pattern['total_spent_24h']:.2f}")

    velocity_score = min(1.0, velocity_score)

    print(f"    ✅  Velocity score: {velocity_score} | Flags: {len(flags)}")
    return {
        "account_id": account_id,
        "transactions_last_hour": pattern["transactions_last_hour"],
        "transactions_last_24h": pattern["transactions_last_24h"],
        "total_spent_24h": round(pattern["total_spent_24h"], 2),
        "velocity_score": velocity_score,
        "velocity_flags": flags
    }


def tool_geolocation_checker(account_id: str, country: str, ip_address: str) -> dict:
    """
    Tool 3 — Geolocation Checker
    Checks if the transaction location is consistent with account history.
    In production: queries IP geolocation + account travel history.
    """
    print(f"    🌍  [GeolocationChecker] Checking location: {country} | IP: {ip_address}")

    # Simulate account home countries
    account_home = {
        "ACC-001": "United Kingdom",
        "ACC-002": "United Kingdom",
        "ACC-003": "United Kingdom",
        "ACC-FRAUD": "United Kingdom",
    }

    home_country = account_home.get(account_id, "United Kingdom")
    is_foreign = country.lower() not in ["united kingdom", "uk", "england", "great britain"]

    # High-risk countries for card fraud
    high_risk_countries = ["nigeria", "romania", "ukraine", "bulgaria", "indonesia"]
    is_high_risk_country = any(c in country.lower() for c in high_risk_countries)

    geo_score = 0.0
    flags = []

    if is_foreign:
        geo_score += 0.3
        flags.append(f"Foreign transaction: {country} (home: {home_country})")
    if is_high_risk_country:
        geo_score += 0.4
        flags.append(f"High-risk country: {country}")

    # Check IP consistency (simplified)
    if ip_address.startswith("185.") or ip_address.startswith("91."):
        geo_score += 0.2
        flags.append(f"Suspicious IP range: {ip_address}")

    geo_score = min(1.0, geo_score)

    print(f"    ✅  Geo score: {geo_score} | Foreign: {is_foreign}")
    return {
        "home_country": home_country,
        "transaction_country": country,
        "is_foreign_transaction": is_foreign,
        "is_high_risk_country": is_high_risk_country,
        "geo_score": geo_score,
        "geo_flags": flags
    }


def tool_device_checker(account_id: str, device_id: str) -> dict:
    """
    Tool 4 — Device Fingerprint Checker
    Checks if the device is recognised for this account.
    In production: queries device fingerprint database.
    """
    print(f"    📱  [DeviceChecker] Checking device: {device_id}")

    # Simulate known devices per account
    known_devices = {
        "ACC-001": ["DEV-iPhone-001", "DEV-MacBook-001"],
        "ACC-002": ["DEV-Samsung-002", "DEV-iPad-002"],
        "ACC-003": ["DEV-iPhone-003"],
        "ACC-FRAUD": ["DEV-iPhone-FRAUD"],
    }

    account_devices = known_devices.get(account_id, ["DEV-Unknown"])
    is_known_device = device_id in account_devices

    device_score = 0.0
    flags = []

    if not is_known_device:
        device_score += 0.35
        flags.append(f"Unrecognised device: {device_id}")

    if "emulator" in device_id.lower() or "virtual" in device_id.lower():
        device_score += 0.4
        flags.append("Virtual/emulated device detected")

    print(f"    ✅  Device score: {device_score} | Known device: {is_known_device}")
    return {
        "device_id": device_id,
        "is_known_device": is_known_device,
        "known_devices_count": len(account_devices),
        "device_score": device_score,
        "device_flags": flags
    }


def tool_account_history(account_id: str, amount: float) -> dict:
    """
    Tool 5 — Account History Checker
    Checks the transaction against the account's typical spending patterns.
    In production: queries account analytics database.
    """
    print(f"    📊  [AccountHistory] Checking account patterns for {account_id}")

    # Simulate account profiles
    profiles = {
        "ACC-001": {"avg_transaction": 45.00, "max_transaction": 250.00, "typical_countries": ["UK"], "account_age_days": 1825},
        "ACC-002": {"avg_transaction": 120.00, "max_transaction": 800.00, "typical_countries": ["UK", "France"], "account_age_days": 730},
        "ACC-003": {"avg_transaction": 35.00, "max_transaction": 150.00, "typical_countries": ["UK"], "account_age_days": 365},
        "ACC-FRAUD": {"avg_transaction": 40.00, "max_transaction": 200.00, "typical_countries": ["UK"], "account_age_days": 30},
    }

    profile = profiles.get(account_id, {
        "avg_transaction": 50.00,
        "max_transaction": 300.00,
        "typical_countries": ["UK"],
        "account_age_days": 500
    })

    history_score = 0.0
    flags = []

    # Check if amount is unusually large
    if amount > profile["max_transaction"] * 2:
        history_score += 0.4
        flags.append(f"Amount £{amount} far exceeds typical max £{profile['max_transaction']}")
    elif amount > profile["max_transaction"]:
        history_score += 0.2
        flags.append(f"Amount £{amount} exceeds typical max £{profile['max_transaction']}")

    # New accounts are higher risk
    if profile["account_age_days"] < 90:
        history_score += 0.3
        flags.append(f"New account: only {profile['account_age_days']} days old")

    history_score = min(1.0, history_score)

    print(f"    ✅  History score: {history_score} | Avg tx: £{profile['avg_transaction']}")
    return {
        "account_id": account_id,
        "avg_transaction_amount": profile["avg_transaction"],
        "max_historical_transaction": profile["max_transaction"],
        "account_age_days": profile["account_age_days"],
        "history_score": history_score,
        "history_flags": flags
    }


# ─────────────────────────────────────────────
# 6.  LANGGRAPH NODES
# ─────────────────────────────────────────────

def node_ingest(state: FraudState) -> dict:
    """NODE 1 — Ingest and validate transaction data"""
    print(f"\n  📥  [Node: ingest] Transaction {state['transaction_id']}")
    print(f"       £{state['amount']} at {state['merchant']} | {state['country']}")

    log_audit(state["transaction_id"], "TRANSACTION_RECEIVED", "SYSTEM",
              f"£{state['amount']} at {state['merchant']} | {state['country']}")

    return {
        "trace": [f"[ingest] {state['transaction_id']} | £{state['amount']} | {state['merchant']}"]
    }


def node_analyse(state: FraudState) -> dict:
    """NODE 2 — Run all 5 fraud detection tools"""
    print(f"\n  🔬  [Node: analyse] Running 5 fraud detection tools...")

    transaction_data = {
        "amount": state["amount"],
        "merchant": state["merchant"],
        "merchant_category": state["merchant_category"],
        "country": state["country"],
        "timestamp": state["timestamp"],
        "account_id": state["account_id"]
    }

    t_result = tool_transaction_analyser(transaction_data)
    v_result = tool_velocity_checker(state["account_id"], state["amount"], state["timestamp"])
    g_result = tool_geolocation_checker(state["account_id"], state["country"], state["ip_address"])
    d_result = tool_device_checker(state["account_id"], state["device_id"])
    h_result = tool_account_history(state["account_id"], state["amount"])

    print(f"    ✅  All 5 tools complete.")

    return {
        "transaction_analysis": t_result,
        "velocity_check": v_result,
        "geolocation_check": g_result,
        "device_check": d_result,
        "account_history": h_result,
        "trace": [f"[analyse] 5 tools executed for {state['transaction_id']}"]
    }


def node_score(state: FraudState) -> dict:
    """NODE 3 — Aggregate tool scores into a single risk score"""
    print(f"\n  📊  [Node: score] Calculating composite risk score...")

    # Weighted average of tool scores
    weights = {
        "transaction": 0.30,
        "velocity": 0.25,
        "geolocation": 0.20,
        "device": 0.15,
        "history": 0.10
    }

    scores = {
        "transaction": state["transaction_analysis"].get("transaction_risk_score", 0.0),
        "velocity": state["velocity_check"].get("velocity_score", 0.0),
        "geolocation": state["geolocation_check"].get("geo_score", 0.0),
        "device": state["device_check"].get("device_score", 0.0),
        "history": state["account_history"].get("history_score", 0.0)
    }

    composite_score = sum(scores[k] * weights[k] for k in weights)
    composite_score = round(composite_score, 3)

    # Collect all risk factors
    risk_factors = []
    risk_factors.extend(state["transaction_analysis"].get("fraud_indicators", []))
    risk_factors.extend(state["velocity_check"].get("velocity_flags", []))
    risk_factors.extend(state["geolocation_check"].get("geo_flags", []))
    risk_factors.extend(state["device_check"].get("device_flags", []))
    risk_factors.extend(state["account_history"].get("history_flags", []))

    risk_level = get_risk_level(composite_score)
    risk_info = RISK_LEVELS[risk_level]
    recommended_action = risk_info["action"]
    requires_review = risk_info["hitl"]

    print(f"\n    Component scores:")
    for k, v in scores.items():
        print(f"      {k:12} : {v:.3f} (weight {weights[k]})")
    print(f"    ─────────────────────────")
    print(f"    Composite    : {composite_score}")
    print(f"    Risk level   : {risk_info['label']}")
    print(f"    Action       : {recommended_action}")
    print(f"    HITL         : {requires_review}")

    log_audit(state["transaction_id"], "RISK_SCORED", "AI_SYSTEM",
              f"Score={composite_score} | Level={risk_level} | Action={recommended_action}")

    return {
        "risk_score": composite_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "recommended_action": recommended_action,
        "requires_analyst_review": requires_review,
        "trace": [f"[score] {composite_score} | {risk_level} | {recommended_action}"]
    }


def node_analyst_review(state: FraudState) -> dict:
    """
    NODE 4 — Analyst Review (HITL)
    Fires for HIGH and CRITICAL risk transactions.
    """
    risk_info = RISK_LEVELS.get(state["risk_level"], {})

    print(f"\n  👤  [Node: analyst_review] {risk_info.get('label')} — analyst review required")
    print(f"\n{'═'*60}")
    print(f"  🚨 FRAUD ANALYST REVIEW DASHBOARD")
    print(f"{'═'*60}")
    print(f"  Transaction ID : {state['transaction_id']}")
    print(f"  Account        : {state['account_id']}")
    print(f"  Amount         : £{state['amount']} {state['currency']}")
    print(f"  Merchant       : {state['merchant']} ({state['merchant_category']})")
    print(f"  Country        : {state['country']}")
    print(f"  Device         : {state['device_id']}")
    print(f"  Risk Score     : {state['risk_score']}")
    print(f"  Risk Level     : {risk_info.get('label')}")
    print(f"  AI Recommends  : {state['recommended_action']}")

    if state["risk_factors"]:
        print(f"\n  ⚠️  RISK FACTORS:")
        for factor in state["risk_factors"]:
            print(f"     • {factor}")

    print(f"\n{'─'*60}")
    print(f"  ANALYST OPTIONS:")
    print(f"  1. APPROVE  — override AI, approve transaction")
    print(f"  2. BLOCK    — confirm block")
    print(f"  3. ESCALATE — escalate to fraud team")
    print(f"{'─'*60}")

    analyst_id = input("  Analyst ID (e.g. FA001): ").strip() or "FA001"
    decision = input("  Decision (APPROVE / BLOCK / ESCALATE): ").strip().upper()

    if decision not in ["APPROVE", "BLOCK", "ESCALATE"]:
        decision = state["recommended_action"]

    notes = input("  Notes (optional, press Enter to skip): ").strip()

    log_audit(state["transaction_id"], f"ANALYST_{decision}", analyst_id,
              f"Risk={state['risk_level']} | Notes={notes[:40]}")

    print(f"    ✅  Analyst decision: {decision} by {analyst_id}")

    return {
        "analyst_id": analyst_id,
        "analyst_decision": decision,
        "analyst_notes": notes,
        "final_action": decision,
        "trace": [f"[analyst_review] {decision} by {analyst_id}"]
    }


def node_action(state: FraudState) -> dict:
    """NODE 5 — Execute the final action and generate report"""
    print(f"\n  ⚡  [Node: action] Executing final action...")

    # If no analyst review, use recommended action
    final_action = state.get("analyst_decision") or state["recommended_action"]
    risk_info = RISK_LEVELS.get(state["risk_level"], {})

    # Build report
    report_lines = [
        "═" * 60,
        "  BARCLAYS FRAUD DETECTION REPORT",
        "  ⚠️  DEMONSTRATION SYSTEM — NOT FOR REAL USE",
        "═" * 60,
        f"  Transaction ID : {state['transaction_id']}",
        f"  Account        : {state['account_id']}",
        f"  Timestamp      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "─" * 60,
        f"  AMOUNT         : £{state['amount']} {state['currency']}",
        f"  MERCHANT       : {state['merchant']}",
        f"  CATEGORY       : {state['merchant_category']}",
        f"  COUNTRY        : {state['country']}",
        "─" * 60,
        f"  RISK SCORE     : {state['risk_score']}/1.0",
        f"  RISK LEVEL     : {risk_info.get('label', state['risk_level'])}",
        f"  FINAL ACTION   : {final_action}",
    ]

    if state.get("analyst_id"):
        report_lines.append(f"  REVIEWED BY    : {state['analyst_id']}")

    report_lines.append("─" * 60)

    if state["risk_factors"]:
        report_lines.append("  RISK FACTORS:")
        for factor in state["risk_factors"]:
            report_lines.append(f"     • {factor}")
        report_lines.append("─" * 60)

    # Component scores
    report_lines += [
        "  COMPONENT SCORES:",
        f"     Transaction  : {state['transaction_analysis'].get('transaction_risk_score', 0):.3f}",
        f"     Velocity     : {state['velocity_check'].get('velocity_score', 0):.3f}",
        f"     Geolocation  : {state['geolocation_check'].get('geo_score', 0):.3f}",
        f"     Device       : {state['device_check'].get('device_score', 0):.3f}",
        f"     History      : {state['account_history'].get('history_score', 0):.3f}",
        "─" * 60,
    ]

    # Audit trail
    report_lines.append("  AUDIT TRAIL:")
    for entry in audit_log:
        if entry["transaction_id"] == state["transaction_id"]:
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

    log_audit(state["transaction_id"], f"FINAL_ACTION_{final_action}", "SYSTEM",
              f"Risk={state['risk_level']} | Score={state['risk_score']}")

    return {
        "final_action": final_action,
        "fraud_report": report,
        "trace": [f"[action] Final action: {final_action}"]
    }


# ─────────────────────────────────────────────
# 7.  CONDITIONAL EDGE
# ─────────────────────────────────────────────

def needs_analyst(state: FraudState) -> Literal["analyst_review", "action"]:
    if state.get("requires_analyst_review", False):
        print("    ⚠️   HIGH/CRITICAL risk — routing to analyst review")
        return "analyst_review"
    else:
        print("    ✅  LOW/MEDIUM risk — routing directly to action")
        return "action"


# ─────────────────────────────────────────────
# 8.  BUILD THE GRAPH
# ─────────────────────────────────────────────

def build_fraud_graph():
    graph = StateGraph(FraudState)

    graph.add_node("ingest", node_ingest)
    graph.add_node("analyse", node_analyse)
    graph.add_node("score", node_score)
    graph.add_node("analyst_review", node_analyst_review)
    graph.add_node("action", node_action)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "analyse")
    graph.add_edge("analyse", "score")
    graph.add_conditional_edges(
        "score",
        needs_analyst,
        {
            "analyst_review": "analyst_review",
            "action": "action"
        }
    )
    graph.add_edge("analyst_review", "action")
    graph.add_edge("action", END)

    return graph.compile()


# ─────────────────────────────────────────────
# 9.  DEMO TRANSACTIONS
# ─────────────────────────────────────────────

def run_transaction(app, tx: dict):
    print(f"\n\n{'▓'*60}")
    print(f"  TRANSACTION: {tx['transaction_id']}")
    print(f"{'▓'*60}")

    state: FraudState = {
        **tx,
        "transaction_analysis": {},
        "velocity_check": {},
        "geolocation_check": {},
        "device_check": {},
        "account_history": {},
        "risk_score": 0.0,
        "risk_level": "",
        "risk_factors": [],
        "recommended_action": "",
        "requires_analyst_review": False,
        "analyst_id": "",
        "analyst_decision": "",
        "analyst_notes": "",
        "final_action": "",
        "fraud_report": "",
        "trace": [f"[start] {tx['transaction_id']} received"]
    }

    result = app.invoke(state)

    print(f"\n  TRACE:")
    for step in result["trace"]:
        print(f"    → {step}")

    return result


def run_demo():
    print("\n" + "█"*60)
    print("  DAY 35 — BARCLAYS FRAUD DETECTION AGENT")
    print("  42-Day Agentic AI Sprint — Sheyi Teluwo")
    print("  ⚠️  DEMONSTRATION ONLY — NOT FOR REAL USE")
    print("█"*60)

    app = build_fraud_graph()
    print("✅  Fraud detection graph compiled.")

    # TX1: Normal transaction — LOW risk, auto-approve
    run_transaction(app, {
        "transaction_id": "TX-001",
        "account_id": "ACC-001",
        "amount": 42.50,
        "currency": "GBP",
        "merchant": "Tesco Express",
        "merchant_category": "Grocery",
        "country": "United Kingdom",
        "timestamp": "2026-05-28 14:32:00",
        "device_id": "DEV-iPhone-001",
        "ip_address": "82.132.210.45"
    })

    # TX2: Suspicious transaction — HIGH risk, analyst review
    # When prompted: enter FA001, then BLOCK, then press Enter for notes
    run_transaction(app, {
        "transaction_id": "TX-002",
        "account_id": "ACC-FRAUD",
        "amount": 2500.00,
        "currency": "GBP",
        "merchant": "Crypto Exchange XYZ",
        "merchant_category": "Cryptocurrency",
        "country": "Romania",
        "timestamp": "2026-05-28 03:17:00",
        "device_id": "DEV-Unknown-999",
        "ip_address": "185.220.101.47"
    })

    # TX3: Medium risk — flagged but no HITL
    run_transaction(app, {
        "transaction_id": "TX-003",
        "account_id": "ACC-002",
        "amount": 899.00,
        "currency": "GBP",
        "merchant": "Apple Store Paris",
        "merchant_category": "Electronics",
        "country": "France",
        "timestamp": "2026-05-28 11:45:00",
        "device_id": "DEV-Samsung-002",
        "ip_address": "90.85.142.33"
    })

    # Print full audit log
    print(f"\n\n{'═'*60}")
    print("  FULL AUDIT LOG — ALL TRANSACTIONS")
    print(f"{'═'*60}")
    for entry in audit_log:
        print(f"  {entry['timestamp']} | {entry['transaction_id']} | {entry['actor']} | {entry['event']}")

    print("\n\n" + "█"*60)
    print("  DAY 35 COMPLETE ✅")
    print("█"*60)
    print("\nBarclays Fraud Detection Agent:")
    print("  ✅  5 fraud detection tools")
    print("  ✅  Composite risk scoring (weighted average)")
    print("  ✅  4 risk levels: LOW / MEDIUM / HIGH / CRITICAL")
    print("  ✅  HITL gate for HIGH and CRITICAL transactions")
    print("  ✅  Full FCA-compliant audit log")
    print("  ✅  LangGraph: 5 nodes + 1 conditional edge")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📸  SCREENSHOT THIS OUTPUT — save as:")
    print("    day35_fraud_detection_agent_2026-05-28.png")
    print("█"*60)


if __name__ == "__main__":
    run_demo()
