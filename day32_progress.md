# Day 32 — NHS Patient Triage Agent
**Date:** 2026-05-21
**Sprint:** 42-Day Agentic AI Zero-to-Hero (Day 32 of 42)
**Phase:** 3 — Enterprise MCP Architect (Days 29–42)

---

## What We Built Today

### NHS Patient Triage Agent

A production-architecture LangGraph agent that triages patients into 4 levels
and routes high-risk cases to a clinician for review before any recommendation goes out.

> ⚠️ DEMONSTRATION SYSTEM — NOT for real clinical use. Real NHS triage requires CQC registration and clinical validation.

---

### Triage Levels

| Level | Label | Action | HITL? |
|---|---|---|---|
| EMERGENCY | 🔴 EMERGENCY | Call 999 immediately | ✅ Yes |
| URGENT | 🟠 URGENT | A&E or call 111 now | ✅ Yes |
| ROUTINE | 🟡 ROUTINE | Book GP appointment | ❌ No |
| SELF_CARE | 🟢 SELF-CARE | Pharmacy / home care | ❌ No |

---

### Graph Architecture

```
Patient Input
    │
    ▼
┌─────────┐
│  intake │  validates patient data
└────┬────┘
     │
     ▼
┌─────────┐
│  assess │  symptom checker + medication checker tools
└────┬────┘
     │
     ▼
┌─────────┐
│  triage │  wait times + GP finder + sets HITL flag
└────┬────┘
     │
 ┌───▼────────────────────┐
 │ EMERGENCY or URGENT?   │
 └───┬──────────┬─────────┘
    YES         NO
     │           │
     ▼           ▼
┌─────────┐  ┌───────────┐
│clinician│  │ recommend │
│ review  │  └─────┬─────┘
└────┬────┘        │
     │             │
     ▼             │
┌─────────┐        │
│recommend│◄───────┘
└────┬────┘
     │
    END
```

---

### Tools Built

| Tool | Simulates | Production Would Call |
|---|---|---|
| `tool_symptom_checker` | GPT-4o clinical reasoning | NHS Digital Symptom Checker API |
| `tool_medication_checker` | GPT-4o pharmacy reasoning | NHS BNF (British National Formulary) API |
| `tool_wait_time_lookup` | Static NHS wait data | NHS Capacity Management API |
| `tool_gp_finder` | Static NHS service data | NHS Find a GP API |

---

### Demo Patients

| Patient | Age | Scenario | Triage Level | HITL? |
|---|---|---|---|---|
| NHS-001 | 34 | Mild cold symptoms | SELF_CARE | No |
| NHS-002 | 58 | Persistent cough, diabetic | ROUTINE | No |
| NHS-003 | 67 | Chest pain, left arm pain, hypertension | URGENT/EMERGENCY | Yes |

---

## Files

| File | Purpose |
|---|---|
| `day32_nhs_triage_agent.py` | Main script — full NHS triage agent |
| `day32_progress.md` | This file |

---

## Screenshots Required

| Screenshot | Filename |
|---|---|
| Patient NHS-001 and NHS-002 results | `day32_nhs_triage_agent_2026-05-21.png` |
| Patient NHS-003 HITL gate + report | `day32_nhs_triage_hitl_2026-05-21.png` |

---

## Packages Required

```
pip install langgraph langchain-openai openai python-dotenv
```
(All already installed from Day 31)

---

## Metrics — Running Total

| Metric | Value |
|---|---|
| LangGraph nodes built (Day 32) | 5 |
| Triage tools built | 4 |
| HITL gates across all 3 phases | 3 |
| GitHub commits (after today) | 41 |
| LinkedIn posts scheduled | 26 (28 after today) |

---

## GitHub Commit

```
git add day32_nhs_triage_agent.py day32_progress.md
git commit -m "Day 32: NHS patient triage agent with HITL clinician review gate"
git push origin main
```

---

## LinkedIn Calendar Check

| Date | Day | Status |
|---|---|---|
| Thu 4 Jun | Thu | ✅ Day 30 already scheduled |
| Fri 5 Jun | Fri | ✅ Day 31 already scheduled |
| Sat 6 Jun | Sat | ❌ Weekend |
| Sun 7 Jun | Sun | ❌ Weekend |
| **Mon 9 Jun** | **Mon** | ✅ **Day 32 posts** |

**Day 32 posts: Monday 9 June 2026**
- **7:30am** — Post 1
- **1:00pm** — Post 2

---

## LinkedIn Posts

### Post 1 — Monday 9 June, 7:30am
**Screenshot:** Terminal output showing Patient NHS-003 HITL gate firing — where it prints `⚠️ CLINICIAN REVIEW REQUIRED` and pauses for input. Save as `day32_nhs_triage_hitl_2026-05-21.png`

```
Day 32 of 42 🏥

Today I built an NHS Patient Triage Agent.

It classifies patients into 4 levels:
🔴 EMERGENCY — Call 999 now
🟠 URGENT — A&E within 2 hours
🟡 ROUTINE — Book a GP
🟢 SELF-CARE — Pharmacy advice

Here's what makes it production-ready:

For EMERGENCY and URGENT cases the pipeline STOPS.
It does not send a recommendation until a clinician reviews and approves.

That's HITL Gate #3.

The NHS cannot afford AI hallucinations in clinical decisions.
Neither can Barclays. Neither can any Magic Circle law firm.

Every system I've built in this sprint has a human checkpoint.
That's not a limitation. That's the architecture.

#AgenticAI #NHS #HealthcareAI #HITL #Python #Day32of42
```

### Post 2 — Monday 9 June, 1:00pm
**Screenshot:** The full triage report printed in the terminal for Patient NHS-003 — showing the structured report with red flags, medication warnings and clinician review section. Save as `day32_nhs_triage_agent_2026-05-21.png`

```
The NHS spends £2.4 billion a year on avoidable A&E admissions.

A significant chunk of that is triage errors — people going to the wrong place at the wrong time.

Today I built a triage agent that:
→ Analyses symptoms using clinical decision logic
→ Checks medication history for contraindications
→ Looks up NHS wait times and routes to the right service
→ Stops the pipeline for a clinician to review before any URGENT recommendation goes out

This is the use case I'd pitch to NHS Digital.

Not "AI will replace doctors."

"AI will make sure the right patient gets to the right clinician faster."

That's the pitch that gets the contract.

#NHSDigital #HealthTech #AIArchitect #UKJobs #ProductionAI #Day32of42
```

---

## Day 32 Checklist

- [ ] Activate .venv312
- [ ] Run `day32_nhs_triage_agent.py`
- [ ] Type APPROVE when Patient NHS-003 HITL gate fires
- [ ] Screenshot 1: HITL gate → `day32_nhs_triage_hitl_2026-05-21.png`
- [ ] Screenshot 2: Full triage report → `day32_nhs_triage_agent_2026-05-21.png`
- [ ] Git commit + push (commit #41)
- [ ] Schedule LinkedIn posts for Mon 9 Jun (7:30am + 1:00pm)
- [ ] Confirm Day 32 complete ✅
