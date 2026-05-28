"""
Day 36 — Docker API Test Script
42-Day Agentic AI Sprint — Sheyi Teluwo

Run this AFTER starting the Docker container (or local uvicorn server)
to verify all endpoints are working correctly.

Run:
    python day36_test_api.py
"""

import json
import sys

try:
    import httpx
except ImportError:
    print("❌  httpx not installed. Run: pip install httpx")
    sys.exit(1)

BASE_URL = "http://localhost:8000"

def print_result(test_name: str, passed: bool, details: str = ""):
    icon = "✅" if passed else "❌"
    print(f"  {icon}  {test_name}")
    if details:
        print(f"       {details}")

def run_tests():
    print("\n" + "█"*60)
    print("  DAY 36 — DOCKER API TEST SUITE")
    print("  42-Day Agentic AI Sprint — Sheyi Teluwo")
    print("█"*60)
    print(f"\n  Testing API at: {BASE_URL}\n")

    results = []

    # ── TEST 1: Root endpoint ──────────────────────────────────
    print("  TEST 1 — Root endpoint")
    try:
        r = httpx.get(f"{BASE_URL}/", timeout=10)
        passed = r.status_code == 200 and "Fraud Detection API" in r.text
        print_result("GET / returns 200 + API name", passed, f"Status: {r.status_code}")
        results.append(passed)
    except Exception as e:
        print_result("GET / returns 200 + API name", False, str(e))
        results.append(False)

    # ── TEST 2: Health check ───────────────────────────────────
    print("\n  TEST 2 — Health check")
    try:
        r = httpx.get(f"{BASE_URL}/health", timeout=10)
        data = r.json()
        passed = r.status_code == 200 and data.get("status") == "healthy"
        print_result("GET /health returns healthy", passed,
                     f"Status: {r.status_code} | Response: {data.get('status')}")
        results.append(passed)
    except Exception as e:
        print_result("GET /health returns healthy", False, str(e))
        results.append(False)

    # ── TEST 3: Low risk transaction ───────────────────────────
    print("\n  TEST 3 — Low risk transaction (Tesco, UK)")
    try:
        payload = {
            "transaction_id": "TEST-001",
            "account_id": "ACC-001",
            "amount": 32.50,
            "currency": "GBP",
            "merchant": "Tesco Express",
            "merchant_category": "Grocery",
            "country": "United Kingdom",
            "timestamp": "2026-05-28T14:30:00",
            "device_id": "DEV-iPhone-001",
            "ip_address": "82.132.210.45"
        }
        r = httpx.post(f"{BASE_URL}/analyse", json=payload, timeout=10)
        data = r.json()
        passed = r.status_code == 200 and data.get("risk_level") == "LOW"
        print_result("Low risk → APPROVE", passed,
                     f"Score: {data.get('risk_score')} | Level: {data.get('risk_level')} | Action: {data.get('final_action')}")
        results.append(passed)
    except Exception as e:
        print_result("Low risk → APPROVE", False, str(e))
        results.append(False)

    # ── TEST 4: Critical risk transaction ──────────────────────
    print("\n  TEST 4 — Critical risk transaction (Crypto, Romania, 3am)")
    try:
        payload = {
            "transaction_id": "TEST-002",
            "account_id": "ACC-FRAUD",
            "amount": 2500.00,
            "currency": "GBP",
            "merchant": "Crypto Exchange XYZ",
            "merchant_category": "Cryptocurrency",
            "country": "Romania",
            "timestamp": "2026-05-28T03:17:00",
            "device_id": "DEV-Unknown-999",
            "ip_address": "185.220.101.47"
        }
        r = httpx.post(f"{BASE_URL}/analyse", json=payload, timeout=10)
        data = r.json()
        passed = r.status_code == 200 and data.get("risk_level") in ["HIGH", "CRITICAL"]
        print_result("Critical risk → BLOCK/ESCALATE", passed,
                     f"Score: {data.get('risk_score')} | Level: {data.get('risk_level')} | Action: {data.get('final_action')}")
        if data.get("risk_factors"):
            print(f"       Risk factors: {len(data['risk_factors'])} identified")
        results.append(passed)
    except Exception as e:
        print_result("Critical risk → BLOCK/ESCALATE", False, str(e))
        results.append(False)

    # ── TEST 5: Audit log ──────────────────────────────────────
    print("\n  TEST 5 — Audit log")
    try:
        r = httpx.get(f"{BASE_URL}/audit", timeout=10)
        data = r.json()
        passed = r.status_code == 200 and data.get("total_transactions", 0) >= 2
        print_result("GET /audit returns transaction log", passed,
                     f"Total transactions logged: {data.get('total_transactions')}")
        results.append(passed)
    except Exception as e:
        print_result("GET /audit returns transaction log", False, str(e))
        results.append(False)

    # ── SUMMARY ───────────────────────────────────────────────
    passed_count = sum(results)
    total = len(results)
    score = round(passed_count / total, 2)

    print(f"\n{'═'*60}")
    print(f"  API TEST RESULTS")
    print(f"  Passed: {passed_count}/{total} | Score: {score}/1.0")
    print(f"  Status: {'✅ ALL TESTS PASSED' if passed_count == total else '❌ SOME TESTS FAILED'}")
    print(f"{'═'*60}")

    print(f"\n📸  SCREENSHOT THIS OUTPUT — save as:")
    print(f"    day36_docker_test_2026-05-28.png")

if __name__ == "__main__":
    run_tests()
