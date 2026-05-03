# Day 10 Progress Log — 03 May 2026

## Goal
Production Hardening — make the RAG bot resilient before deployment.

## What I Built
- `day10_production_hardening.py` — standalone demo of all 5 hardening layers
- `app/validators.py`   — Pydantic input/output models
- `app/middleware.py`   — request logging middleware  
- `app/health.py`       — /health and /health/deep endpoints
- `app/main.py`         — fully updated with rate limiting + error handling

## 5 Layers Added
1. Input Validation     — Pydantic, min/max length, blocked terms
2. Error Handling       — Global exception handler, 3x retry with backoff
3. Rate Limiting        — SlowAPI, 10 requests/minute per IP
4. Health Checks        — Liveness + deep check (env vars, dirs, DB)
5. Structured Logging   — File (logs/app.log) + terminal output

## Metrics
- Eval score: 0.94 / 1.0 (maintained)
- Commits today: 1
- New endpoints: /health, /health/deep
- All 5 curl tests: PASSED

## Day 11 Preview
- Docker containerisation
- Write Dockerfile and .dockerignore
- Build and run the bot inside a container
- Test container health endpoint

## Interview Talking Point
"I production-hardened my RAG API on Day 10 before touching deployment.
Input validation blocks bad requests at the door. Rate limiting protects
against cost blowouts. Retry logic with exponential backoff handles 
transient LLM failures. Health endpoints give deployment platforms a 
heartbeat to monitor. All queries are logged with unique request IDs 
for full traceability. A compliance officer at Barclays could run this 
with confidence."