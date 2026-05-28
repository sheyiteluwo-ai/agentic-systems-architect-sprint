# Day 35 — Barclays Fraud Detection Agent
**Date:** 2026-05-28
**Sprint:** 42-Day Agentic AI Zero-to-Hero (Day 35 of 42)
**Phase:** 3 — Enterprise MCP Architect (Days 29–42)

---

## What We Built Today

### Barclays-Style Fraud Detection Agent

A production-architecture LangGraph agent that analyses bank transactions
across 5 dimensions and routes high-risk cases to a human analyst.

> ⚠️ DEMONSTRATION SYSTEM — NOT for real use. Real fraud systems require FCA authorisation.

---

### Risk Levels

| Level | Score Range | Action | HITL? |
|---|---|---|---|
| 🟢 LOW | 0.00–0.24 | APPROVE | ❌ No |
| 🟡 MEDIUM | 0.25–0.49 | FLAG | ❌ No |
| 🟠 HIGH | 0.50–0.74 | BLOCK | ✅ Yes |
| 🔴 CRITICAL | 0.75–1.00 | ESCALATE | ✅ Yes |

---

### 5 Fraud Detection Tools

| Tool | What It Checks | In Production Would Use |
|---|---|---|
| `tool_transaction_analyser` | Amount, merchant, time anomalies | ML model on transaction history |
| `tool_velocity_checker` | Too many transactions in short window | Real-time transaction DB |
| `tool_geolocation_checker` | Foreign/high-risk country, suspicious IP | IP geolocation + travel history |
| `tool_device_checker` | Unknown/emulated device | Device fingerprint database |
| `tool_account_history` | Amount vs historical patterns, account age | Account analytics DB |

### Risk Score Weights

| Tool | Weight |
|---|---|
| Transaction analyser | 30% |
| Velocity checker | 25% |
| Geolocation checker | 20% |
| Device checker | 15% |
| Account history | 10% |

---

### Graph Architecture

```
Transaction Input
      │
      ▼
  ┌────────┐
  │ ingest │  validates + logs transaction
  └───┬────┘
      │
      ▼
  ┌─────────┐
  │ analyse │  runs all 5 fraud detection tools
  └───┬─────┘
      │
      ▼
  ┌───────┐
  │ score │  weighted composite risk score
  └───┬───┘
      │
 ┌────▼──────────────────┐
 │ HIGH or CRITICAL?     │
 └────┬──────────┬────────┘
     YES         NO
      │           │
      ▼           ▼
┌──────────┐  ┌────────┐
│ analyst  │  │ action │
│ review   │  └───┬────┘
└────┬─────┘      │
     │             │
     ▼             │
┌────────┐         │
│ action │◄────────┘
└───┬────┘
    │
   END
```

---

### Demo Transactions

| TX | Amount | Merchant | Country | Expected Risk |
|---|---|---|---|---|
| TX-001 | £42.50 | Tesco Express | UK | LOW — auto approve |
| TX-002 | £2,500 | Crypto Exchange | Romania | CRITICAL — analyst review |
| TX-003 | £899 | Apple Store Paris | France | MEDIUM — flagged, no HITL |

---

## Files

| File | Purpose |
|---|---|
| `day35_fraud_detection_agent.py` | Main script — full fraud detection agent |
| `day35_progress.md` | This file |

---

## Screenshots Required

| Screenshot | Filename |
|---|---|
| Analyst review dashboard for TX-002 | `day35_fraud_detection_hitl_2026-05-28.png` |
| Full audit log + DAY 35 COMPLETE | `day35_fraud_detection_agent_2026-05-28.png` |

---

## GitHub Commit

```
git add day35_fraud_detection_agent.py day35_progress.md
git commit -m "Day 35: Barclays fraud detection agent — 5 tools, risk scoring, HITL analyst review"
git push origin main
```

---

## LinkedIn Calendar Check

| Date | Day | Status |
|---|---|---|
| Thu 28 May | Today | — |
| Fri 29 May | Fri | ✅ |
| Sat 30 May | Sat | ❌ Weekend |
| Sun 31 May | Sun | ❌ Weekend |
| Mon 1 Jun | Mon | ❌ Day 27 taken |
| Tue 2 Jun | Tue | ❌ Day 28 taken |
| Wed 3 Jun | Wed | ❌ Day 29 taken |
| Thu 4 Jun | Thu | ❌ Day 30 taken |
| Fri 5 Jun | Fri | ❌ Day 31 taken |
| Sat 6 Jun | Sat | ❌ Weekend |
| Sun 7 Jun | Sun | ❌ Weekend |
| Mon 8 Jun | Mon | ❌ Day 32 taken |
| Tue 9 Jun | Tue | ❌ Day 33 taken |
| Wed 10 Jun | Wed | ❌ Day 34 taken |
| **Thu 11 Jun** | **Thu** | ✅ **Day 35 posts** |

**Day 35 posts: Thursday 11 June 2026**
- **7:30am** — Post 1
- **1:00pm** — Post 2

---

## Day 35 Checklist

- [ ] Activate .venv312
- [ ] Move files to project folder
- [ ] Run `day35_fraud_detection_agent.py`
- [ ] Type FA001 + BLOCK when TX-002 analyst review fires
- [ ] Screenshot 1 → `day35_fraud_detection_hitl_2026-05-28.png`
- [ ] Screenshot 2 → `day35_fraud_detection_agent_2026-05-28.png`
- [ ] Git commit + push (commit #44)
- [ ] Schedule LinkedIn posts for Thu 11 Jun (7:30am + 1:00pm)
- [ ] Confirm Day 35 complete ✅
