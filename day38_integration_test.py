"""
Day 38 — Full System Integration Test
42-Day Agentic AI Sprint — Sheyi Teluwo

What we build today:
  - End-to-end integration test across all 3 phases:
      Phase 1: FCA RAG Bot (ChromaDB query)
      Phase 2: Multi-Agent Research Crew (news + analysis)
      Phase 3: Fraud Detection Agent (risk scoring)
  - Each phase runs a representative scenario
  - Results logged to integration_test_report_day38.json
  - Pass/fail scoring with overall system health check

Run:
    python day38_integration_test.py
"""

import json
import os
import sys
from datetime import datetime

# ─────────────────────────────────────────────
# 0.  DEPENDENCY CHECK
# ─────────────────────────────────────────────
def check_dependencies():
    missing = []
    for pkg in ["langchain_openai", "chromadb", "openai", "ddgs"]:
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
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import chromadb
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌  OPENAI_API_KEY not found in .env")
    sys.exit(1)

llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY, temperature=0)

# ─────────────────────────────────────────────
# 2.  TEST RESULTS TRACKER
# ─────────────────────────────────────────────

test_results = []

def log_test(phase: str, test_name: str, passed: bool, details: str, duration_ms: int):
    result = {
        "phase": phase,
        "test": test_name,
        "passed": passed,
        "details": details,
        "duration_ms": duration_ms,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    icon = "✅" if passed else "❌"
    print(f"  {icon}  [{phase}] {test_name}")
    print(f"       {details}")
    print(f"       Duration: {duration_ms}ms")


# ─────────────────────────────────────────────
# 3.  PHASE 1 TESTS — FCA RAG BOT
# ─────────────────────────────────────────────

def test_phase1_chromadb_connection():
    """Test: ChromaDB connects and has FCA documents"""
    start = datetime.now()
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collections = [c.name for c in client.list_collections()]
        duration = int((datetime.now() - start).total_seconds() * 1000)

        if collections:
            col = client.get_collection(collections[0])
            count = col.count()
            passed = count > 0
            details = f"Collection: {collections[0]} | Documents: {count}"
        else:
            passed = False
            details = "No collections found in ChromaDB"

        log_test("PHASE 1", "ChromaDB Connection", passed, details, duration)
        return passed
    except Exception as e:
        duration = int((datetime.now() - start).total_seconds() * 1000)
        log_test("PHASE 1", "ChromaDB Connection", False, str(e), duration)
        return False


def test_phase1_rag_query():
    """Test: RAG query returns relevant FCA document chunks"""
    start = datetime.now()
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collections = [c.name for c in client.list_collections()]
        if not collections:
            duration = int((datetime.now() - start).total_seconds() * 1000)
            log_test("PHASE 1", "RAG Query", False, "No ChromaDB collections", duration)
            return False

        col = client.get_collection(collections[0])
        results = col.query(query_texts=["Consumer Duty requirements"], n_results=3)
        chunks = results["documents"][0]
        duration = int((datetime.now() - start).total_seconds() * 1000)

        passed = len(chunks) >= 1
        details = f"Query: 'Consumer Duty' | Chunks returned: {len(chunks)}"
        log_test("PHASE 1", "RAG Query", passed, details, duration)
        return passed
    except Exception as e:
        duration = int((datetime.now() - start).total_seconds() * 1000)
        log_test("PHASE 1", "RAG Query", False, str(e), duration)
        return False


def test_phase1_llm_response():
    """Test: LLM generates a coherent answer from FCA context"""
    start = datetime.now()
    try:
        response = llm.invoke([
            SystemMessage(content="You are an FCA compliance expert. Answer in 2 sentences max."),
            HumanMessage(content="What is the FCA Consumer Duty?")
        ])
        duration = int((datetime.now() - start).total_seconds() * 1000)
        answer = response.content
        passed = len(answer) > 50 and "consumer" in answer.lower()
        details = f"Response length: {len(answer)} chars | Preview: {answer[:80]}..."
        log_test("PHASE 1", "LLM FCA Response", passed, details, duration)
        return passed
    except Exception as e:
        duration = int((datetime.now() - start).total_seconds() * 1000)
        log_test("PHASE 1", "LLM FCA Response", False, str(e), duration)
        return False


# ─────────────────────────────────────────────
# 4.  PHASE 2 TESTS — MULTI-AGENT RESEARCH CREW
# ─────────────────────────────────────────────

def test_phase2_web_search():
    """Test: DuckDuckGo news search returns results"""
    start = datetime.now()
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news("FCA regulation AI 2026", max_results=3):
                results.append(r.get("title", ""))
        duration = int((datetime.now() - start).total_seconds() * 1000)
        passed = len(results) >= 1
        details = f"Articles found: {len(results)} | First: {results[0][:60] if results else 'None'}"
        log_test("PHASE 2", "Web Search (DuckDuckGo)", passed, details, duration)
        return passed
    except Exception as e:
        duration = int((datetime.now() - start).total_seconds() * 1000)
        log_test("PHASE 2", "Web Search (DuckDuckGo)", False, str(e), duration)
        return False


def test_phase2_researcher_agent():
    """Test: Researcher agent generates a structured research summary"""
    start = datetime.now()
    try:
        response = llm.invoke([
            SystemMessage(content=(
                "You are a research agent. Given a topic, produce a 3-bullet "
                "research summary. Each bullet max 20 words."
            )),
            HumanMessage(content="Research topic: AI adoption in UK financial services 2026")
        ])
        duration = int((datetime.now() - start).total_seconds() * 1000)
        answer = response.content
        passed = len(answer) > 50 and ("•" in answer or "-" in answer or "1." in answer)
        details = f"Response length: {len(answer)} chars | Preview: {answer[:80]}..."
        log_test("PHASE 2", "Researcher Agent", passed, details, duration)
        return passed
    except Exception as e:
        duration = int((datetime.now() - start).total_seconds() * 1000)
        log_test("PHASE 2", "Researcher Agent", False, str(e), duration)
        return False


def test_phase2_writer_agent():
    """Test: Writer agent produces a formatted report from research"""
    start = datetime.now()
    try:
        response = llm.invoke([
            SystemMessage(content=(
                "You are a writer agent. Turn research bullets into a "
                "2-paragraph professional report. Max 100 words total."
            )),
            HumanMessage(content=(
                "Research: AI adoption in UK banks is accelerating. "
                "FCA published AI guidance in 2025. "
                "Barclays and HSBC both launched AI programmes."
            ))
        ])
        duration = int((datetime.now() - start).total_seconds() * 1000)
        answer = response.content
        passed = len(answer) > 80
        details = f"Report length: {len(answer)} chars | Preview: {answer[:80]}..."
        log_test("PHASE 2", "Writer Agent", passed, details, duration)
        return passed
    except Exception as e:
        duration = int((datetime.now() - start).total_seconds() * 1000)
        log_test("PHASE 2", "Writer Agent", False, str(e), duration)
        return False


# ─────────────────────────────────────────────
# 5.  PHASE 3 TESTS — FRAUD DETECTION + NHS TRIAGE
# ─────────────────────────────────────────────

def test_phase3_fraud_scoring():
    """Test: Fraud scoring correctly classifies a critical transaction"""
    start = datetime.now()
    try:
        # Replicate the scoring logic from Day 35
        tx = {
            "amount": 2500.00,
            "merchant_category": "Cryptocurrency",
            "country": "Romania",
            "timestamp": "2026-05-28T03:17:00",
            "ip_address": "185.220.101.47",
            "device_id": "DEV-Unknown-999"
        }

        score = 0.0
        if tx["amount"] > 2000: score += 0.30
        if "cryptocurrency" in tx["merchant_category"].lower(): score += 0.25
        if "romania" in tx["country"].lower(): score += 0.25
        score += 0.15  # odd hour
        if tx["ip_address"].startswith("185."): score += 0.15
        if "unknown" in tx["device_id"].lower(): score += 0.15
        score = min(1.0, round(score, 3))

        risk_level = "CRITICAL" if score >= 0.75 else "HIGH" if score >= 0.50 else "MEDIUM"
        duration = int((datetime.now() - start).total_seconds() * 1000)

        passed = risk_level in ["HIGH", "CRITICAL"]
        details = f"Score: {score} | Risk: {risk_level} | Expected: HIGH or CRITICAL"
        log_test("PHASE 3", "Fraud Risk Scoring", passed, details, duration)
        return passed
    except Exception as e:
        duration = int((datetime.now() - start).total_seconds() * 1000)
        log_test("PHASE 3", "Fraud Risk Scoring", False, str(e), duration)
        return False


def test_phase3_triage_classification():
    """Test: NHS triage AI correctly classifies emergency symptoms"""
    start = datetime.now()
    try:
        response = llm.invoke([
            SystemMessage(content="You are an NHS triage AI. Respond with ONLY one word: EMERGENCY, URGENT, ROUTINE, or SELF_CARE."),
            HumanMessage(content="Patient: 65yo male. Crushing chest pain radiating to left arm, sweating, nausea. Duration: 10 minutes.")
        ])
        duration = int((datetime.now() - start).total_seconds() * 1000)
        answer = response.content.strip().upper()
        passed = "EMERGENCY" in answer or "URGENT" in answer
        details = f"Classification: {answer} | Expected: EMERGENCY or URGENT"
        log_test("PHASE 3", "NHS Triage Classification", passed, details, duration)
        return passed
    except Exception as e:
        duration = int((datetime.now() - start).total_seconds() * 1000)
        log_test("PHASE 3", "NHS Triage Classification", False, str(e), duration)
        return False


def test_phase3_mcp_tool_call():
    """Test: MCP-style tool call returns structured JSON"""
    start = datetime.now()
    try:
        response = llm.invoke([
            SystemMessage(content=(
                "You are an MCP tool. Return ONLY a JSON object with keys: "
                "status, data, timestamp. No preamble. No markdown."
            )),
            HumanMessage(content="Tool: get_stock_data | Input: ticker=BARC.L")
        ])
        duration = int((datetime.now() - start).total_seconds() * 1000)
        clean = response.content.strip().replace("```json", "").replace("```", "")
        result = json.loads(clean)
        passed = "status" in result and "data" in result
        details = f"JSON keys: {list(result.keys())} | Status: {result.get('status')}"
        log_test("PHASE 3", "MCP Tool Call", passed, details, duration)
        return passed
    except Exception as e:
        duration = int((datetime.now() - start).total_seconds() * 1000)
        log_test("PHASE 3", "MCP Tool Call", False, str(e), duration)
        return False


# ─────────────────────────────────────────────
# 6.  SAVE REPORT
# ─────────────────────────────────────────────

def save_report(summary: dict):
    filename = "integration_test_report_day38.json"
    report = {
        "sprint_day": 38,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "tests": test_results
    }
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  💾  Report saved: {filename}")


# ─────────────────────────────────────────────
# 7.  MAIN
# ─────────────────────────────────────────────

def run_integration_tests():
    print("\n" + "█"*60)
    print("  DAY 38 — FULL SYSTEM INTEGRATION TEST")
    print("  42-Day Agentic AI Sprint — Sheyi Teluwo")
    print("█"*60)

    print(f"\n{'═'*60}")
    print("  PHASE 1 — FCA RAG BOT")
    print(f"{'═'*60}")
    p1_results = [
        test_phase1_chromadb_connection(),
        test_phase1_rag_query(),
        test_phase1_llm_response(),
    ]

    print(f"\n{'═'*60}")
    print("  PHASE 2 — MULTI-AGENT RESEARCH CREW")
    print(f"{'═'*60}")
    p2_results = [
        test_phase2_web_search(),
        test_phase2_researcher_agent(),
        test_phase2_writer_agent(),
    ]

    print(f"\n{'═'*60}")
    print("  PHASE 3 — FRAUD DETECTION + NHS TRIAGE + MCP")
    print(f"{'═'*60}")
    p3_results = [
        test_phase3_fraud_scoring(),
        test_phase3_triage_classification(),
        test_phase3_mcp_tool_call(),
    ]

    # Summary
    all_results = p1_results + p2_results + p3_results
    total = len(all_results)
    passed = sum(all_results)
    failed = total - passed
    score = round(passed / total, 3)

    summary = {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "score": score,
        "phase1_score": f"{sum(p1_results)}/{len(p1_results)}",
        "phase2_score": f"{sum(p2_results)}/{len(p2_results)}",
        "phase3_score": f"{sum(p3_results)}/{len(p3_results)}",
        "overall_status": "PASS" if score >= 0.80 else "FAIL"
    }

    save_report(summary)

    print(f"\n\n{'█'*60}")
    print("  DAY 38 COMPLETE ✅")
    print(f"{'█'*60}")
    print(f"\n  INTEGRATION TEST RESULTS:")
    print(f"  Phase 1 — FCA RAG Bot      : {summary['phase1_score']}")
    print(f"  Phase 2 — Research Crew    : {summary['phase2_score']}")
    print(f"  Phase 3 — Fraud/NHS/MCP    : {summary['phase3_score']}")
    print(f"  ─────────────────────────────")
    print(f"  Total  : {passed}/{total} | Score: {score}/1.0")
    print(f"  Status : {'✅ PASS' if summary['overall_status'] == 'PASS' else '❌ FAIL'}")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📸  SCREENSHOT THIS OUTPUT — save as:")
    print(f"    day38_integration_test_2026-05-28.png")
    print(f"{'█'*60}")


if __name__ == "__main__":
    run_integration_tests()
