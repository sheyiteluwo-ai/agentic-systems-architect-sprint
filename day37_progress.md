# Day 37 — GitHub Actions CI/CD Pipeline
**Date:** 2026-05-28
**Sprint:** 42-Day Agentic AI Zero-to-Hero (Day 37 of 42)
**Phase:** 3 — Enterprise MCP Architect (Days 29–42)

---

## What We Built Today

### GitHub Actions CI/CD Pipeline — 5 Jobs

Every push to `main` automatically triggers the full pipeline.

---

### Pipeline Architecture

```
git push origin main
        │
        ▼
┌───────────────────────────────────────────┐
│         GitHub Actions Pipeline           │
│                                           │
│  Job 1: lint ──────────────────────────── │ ~30s
│    • pyflakes syntax check                │
│    • flake8 style check                   │
│                  │                        │
│                  ▼                        │
│  Job 2: test (needs: lint) ────────────── │ ~60s
│    • pip install dependencies             │
│    • start uvicorn server                 │
│    • run day36_test_api.py (5 tests)      │
│    • verify /health endpoint              │
│                  │                        │
│                  ▼                        │
│  Job 3: docker-build (needs: test) ────── │ ~2min
│    • docker build -t fraud-agent .        │
│    • verify image exists                  │
│                                           │
│  Job 4: security (needs: lint) ────────── │ ~30s
│    • safety check on requirements         │
│    • runs parallel to test                │
│                  │                        │
│                  ▼                        │
│  Job 5: notify (needs: all) ───────────── │ instant
│    • print pipeline summary               │
│    • shows pass/fail for each job         │
└───────────────────────────────────────────┘
```

---

### File Location

The workflow file MUST go in this exact folder:
```
.github/workflows/ci.yml
```

GitHub only reads CI/CD workflows from `.github/workflows/`.

---

### How to Set It Up

```
mkdir .github
mkdir .github\workflows
copy ci.yml .github\workflows\ci.yml
git add .github\workflows\ci.yml
git commit -m "Day 37: GitHub Actions CI/CD pipeline — lint, test, docker, security"
git push origin main
```

Then go to:
`https://github.com/sheyiteluwo-ai/agentic-systems-architect-sprint/actions`

You will see the pipeline running automatically. Takes about 3-4 minutes total.

---

## Files

| File | Location | Purpose |
|---|---|---|
| `ci.yml` | `.github/workflows/ci.yml` | GitHub Actions pipeline |
| `day37_progress.md` | project root | This file |

---

## Screenshots Required

| Screenshot | Filename |
|---|---|
| GitHub Actions tab showing pipeline running/passed | `day37_github_actions_2026-05-28.png` |
| Pipeline job detail showing all 5 jobs green | `day37_pipeline_jobs_2026-05-28.png` |

---

## GitHub Commit

```
git add .github/workflows/ci.yml day37_progress.md
git commit -m "Day 37: GitHub Actions CI/CD pipeline — lint, test, docker, security"
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
| Fri 12 Jun | Fri | ❌ Day 36 taken |
| Sat 13 Jun | Sat | ❌ Weekend |
| Sun 14 Jun | Sun | ❌ Weekend |
| **Mon 16 Jun** | **Mon** | ✅ **Day 37 posts** |

**Day 37 posts: Monday 16 June 2026**
- **7:30am** — Post 1
- **1:00pm** — Post 2

---

## Day 37 Checklist

- [ ] Create `.github/workflows/` folder
- [ ] Copy `ci.yml` into `.github/workflows/`
- [ ] Git commit + push (commit #46)
- [ ] Go to GitHub Actions tab and watch pipeline run
- [ ] Screenshot 1 → `day37_github_actions_2026-05-28.png`
- [ ] Screenshot 2 → `day37_pipeline_jobs_2026-05-28.png`
- [ ] Schedule LinkedIn posts for Mon 16 Jun (7:30am + 1:00pm)
- [ ] Confirm Day 37 complete ✅
