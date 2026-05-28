# Day 36 — Docker Containerisation
**Date:** 2026-05-28
**Sprint:** 42-Day Agentic AI Zero-to-Hero (Day 36 of 42)
**Phase:** 3 — Enterprise MCP Architect (Days 29–42)

---

## What We Built Today

### Docker Container for the Fraud Detection Agent

Wrapped the Day 35 fraud detection agent in a FastAPI REST API
and containerised it with Docker. Enterprise-ready deployment.

---

### Files Created Today

| File | Purpose |
|---|---|
| `Dockerfile` | Multi-stage Docker build |
| `docker-compose.yml` | One-command deployment |
| `day36_fraud_api.py` | FastAPI wrapper — 4 endpoints |
| `requirements_docker.txt` | Pinned Python dependencies |
| `day36_test_api.py` | 5-test API test suite |
| `day36_progress.md` | This file |

---

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API info |
| GET | `/health` | Health check (Docker + load balancer) |
| POST | `/analyse` | Run fraud detection on a transaction |
| GET | `/audit` | FCA-compliant audit log |

---

### Docker Architecture

```
docker build -t fraud-agent .
         │
         ▼
┌─────────────────────────────┐
│  Docker Container           │
│  python:3.12-slim           │
│                             │
│  FastAPI (port 8000)        │
│    GET  /health             │
│    POST /analyse  ──────────┼──► Fraud scoring engine
│    GET  /audit              │
│                             │
│  HEALTHCHECK every 30s      │
│  ENV: OPENAI_API_KEY        │
└─────────────────────────────┘
         │
         ▼
  curl localhost:8000/health
  → {"status": "healthy"}
```

---

### How to Run

#### Option A — Docker directly
```bash
# Build
docker build -t fraud-agent .

# Run
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key fraud-agent

# Test
python day36_test_api.py
```

#### Option B — Docker Compose
```bash
docker-compose up --build
```

#### Option C — Local (no Docker)
```bash
pip install fastapi uvicorn httpx
uvicorn day36_fraud_api:app --reload --port 8000
python day36_test_api.py
```

---

### Test Results (5 tests)

| Test | Expected | Status |
|---|---|---|
| GET / returns API name | 200 + "Fraud Detection API" | TBD |
| GET /health returns healthy | status: healthy | TBD |
| Low risk transaction → APPROVE | risk_level: LOW | TBD |
| Critical risk transaction → ESCALATE | risk_level: CRITICAL | TBD |
| GET /audit returns log | total_transactions >= 2 | TBD |

---

## GitHub Commit

```
git add Dockerfile docker-compose.yml day36_fraud_api.py requirements_docker.txt day36_test_api.py day36_progress.md
git commit -m "Day 36: Docker containerisation — FastAPI wrapper, health check, 5-test suite"
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
| Thu 11 Jun | Thu | ❌ Day 35 taken |
| **Fri 12 Jun** | **Fri** | ✅ **Day 36 posts** |

**Day 36 posts: Friday 12 June 2026**
- **7:30am** — Post 1
- **1:00pm** — Post 2

---

## Day 36 Checklist

- [ ] Move all 5 files to project folder
- [ ] Run local test (Option C — no Docker needed)
- [ ] Run `day36_test_api.py` — all 5 tests pass
- [ ] Screenshot terminal → `day36_docker_test_2026-05-28.png`
- [ ] Git commit + push (commit #45)
- [ ] Schedule LinkedIn posts for Fri 12 Jun (7:30am + 1:00pm)
- [ ] Confirm Day 36 complete ✅
