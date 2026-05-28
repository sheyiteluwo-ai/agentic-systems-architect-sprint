# 42-Day Agentic AI Sprint — Agentic Systems Architect

**Author:** Sheyi Teluwo  
**Email:** sheyi@hotmail.co.uk  
**LinkedIn:** [linkedin.com/in/sheyi](https://linkedin.com/in/sheyi)  
**GitHub:** [github.com/sheyiteluwo-ai/agentic-systems-architect-sprint](https://github.com/sheyiteluwo-ai/agentic-systems-architect-sprint)  
**Loom Demo (Phase 1):** [Watch the full Phase 1 system walkthrough — 10 mins](https://www.loom.com/share/bec8aee08b784e55969551aa6bce593f)  
**Loom Demo (All 3 Phases):** Coming Day 41  
**Target:** £95,000+ salary / £850+/day contract  

---

## What This Is

A 42-day structured sprint to build 3 production-grade Agentic AI systems
targeting UK regulated industries: Financial Services, Legal, and Healthcare.

Every system includes:
- Real external API integrations
- Human-in-the-Loop (HITL) safety gates
- LangSmith evaluation scores
- FCA/CQC-compliant audit logging
- Docker containerisation
- GitHub Actions CI/CD pipeline

---

## The Three Systems

### Phase 1 — FCA RAG Knowledge Bot (Days 1–14) ✅
> *"How do I reduce my Barclays compliance team's research time by 80%?"*

| Component | Detail |
|---|---|
| Vector store | ChromaDB — 494 FCA document chunks |
| Retrieval | LangChain LCEL RAG pipeline |
| Eval — Correctness | **0.94/1.0** ✅ |
| Eval — Faithfulness | 0.465/1.0 ❌ (identified for improvement) |
| HITL Gate | 5 FCA compliance rubrics |
| API | FastAPI + SlowAPI rate limiting |
| UI | Streamlit chat interface |
| Business case | £169,000/year saving for Barclays compliance team |

### Phase 2 — Multi-Agent Research Crew (Days 15–28) ✅
> *"How do I save Magic Circle law firms £3.6M/year on legal research?"*

| Component | Detail |
|---|---|
| Framework | CrewAI 0.193 — Researcher + Writer agents |
| State machine | LangGraph — 3 nodes + conditional edge |
| Live search | DuckDuckGo (ddgs package) |
| Model routing | GPT-4o / Claude by task type |
| HITL Gate | Approve / Reject / Escalate with feedback |
| Fact checker | 100% wrong claim detection |
| Eval — Quality | 0.733/1.0 (below 0.80 benchmark — documented) |
| Agent memory | ChromaDB persistent — 14 memories |
| Error recovery | Retry, fallback chain, circuit breaker |
| Business case | £299,500/month saving for 100-matter team |

### Phase 3 — Enterprise MCP Architect (Days 29–42) ✅
> *"How do I connect enterprise AI to real regulated-industry data?"*

| Component | Detail |
|---|---|
| Protocol | Model Context Protocol (MCP) |
| External tools | yfinance, DuckDuckGo, ChromaDB |
| State machine | LangGraph — 5 nodes, 2 conditional edges |
| NHS Triage Agent | 4 triage levels, 3-tier HITL review |
| Fraud Detection | 5 tools, weighted risk scoring, analyst HITL |
| Eval — Safety | **0.95/1.0** ✅ |
| Eval — Bias | **1.0/1.0** ✅ |
| Integration test | 8/9 tests passing (0.889/1.0) |
| Security review | 4/5 checks passing (0.8/1.0) |
| Deployment | Docker + docker-compose |
| CI/CD | GitHub Actions — 5 jobs, 1m 14s pipeline |

---

## Evaluation Scorecard

| Eval | Phase | System | Score | Status |
|---|---|---|---|---|
| Correctness | Phase 1 | FCA RAG Bot | 0.94/1.0 | ✅ PASS |
| Faithfulness | Phase 1 | FCA RAG Bot | 0.465/1.0 | ❌ FAIL |
| Multi-agent quality | Phase 2 | Research Crew | 0.733/1.0 | ❌ FAIL |
| Safety | Phase 3 | NHS Triage | 0.95/1.0 | ✅ PASS |
| Bias | Phase 3 | NHS Triage | 1.0/1.0 | ✅ PASS |
| Integration | Phase 3 | All systems | 0.889/1.0 | ✅ PASS |
| Security | Phase 3 | All systems | 0.8/1.0 | ✅ PASS |

> Note: Failed evals are documented deliberately. Real production systems have known failure modes.
> Faithfulness and multi-agent quality are flagged for improvement in a future sprint.

---

## Technical Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| AI Frameworks | LangChain LCEL, LangGraph, CrewAI 0.193, MCP |
| LLMs | OpenAI GPT-4o, Anthropic Claude |
| Vector Store | ChromaDB (persistent) |
| APIs | FastAPI + SlowAPI, Streamlit |
| Observability | LangSmith |
| Search | DuckDuckGo (ddgs) |
| Finance data | yfinance |
| Containerisation | Docker + docker-compose |
| CI/CD | GitHub Actions (5 jobs) |
| Security | Secrets scan, dependency audit, prompt injection testing |

---

## Sprint Metrics

| Metric | Value |
|---|---|
| GitHub commits | 49 |
| LinkedIn posts | 42 |
| Days completed | 40 of 42 |
| FCA chunks indexed | 494 |
| Agent memories stored | 14 |
| Fact-checker accuracy | 100% |
| CI/CD pipeline duration | 1m 14s |
| Integration tests passing | 8/9 |

---

## Repository Structure

```
agentic-systems-architect-sprint/
│
├── Phase 1 — FCA RAG Bot
│   ├── day01–day14 Python files
│   ├── fca_*.txt / fca_*.pdf  (source documents)
│   └── chroma_db/             (persistent vector store)
│
├── Phase 2 — Research Crew
│   ├── day15–day28 Python files
│   ├── magic_circle_*.md      (business case documents)
│   └── phase2_architecture_diagram.png
│
├── Phase 3 — Enterprise MCP
│   ├── day29–day42 Python files
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements_docker.txt
│   └── .github/workflows/ci.yml
│
├── Evaluation Reports
│   ├── eval_report_day06.json
│   ├── eval_report_day11.json
│   ├── eval_report_day22.json
│   ├── eval_report_day34.json
│   ├── integration_test_report_day38.json
│   └── security_report_day39.json
│
└── README.md
```

---

## Business Cases

### Barclays — FCA Compliance Team
- **Problem:** Senior compliance analysts spend 4+ hours/day manually searching FCA guidance
- **Solution:** RAG bot retrieves accurate answers in under 3 seconds
- **ROI:** £169,000/year (2 FTE hours saved daily × £42.25/hour blended rate)

### Magic Circle Law Firm — Legal Research Crew
- **Problem:** Trainee solicitors spend 60% of time on research that could be automated
- **Solution:** Multi-agent crew researches, writes, fact-checks, and presents for partner review
- **ROI:** £299,500/month saving for a 100-matter team

### Barclays — Fraud Detection
- **Problem:** Manual fraud review misses velocity patterns and cross-channel signals
- **Solution:** 5-tool weighted scoring with analyst HITL for HIGH/CRITICAL cases
- **ROI:** Even 0.1% improvement on 1.2bn annual transactions = significant loss prevention

### NHS — Patient Triage
- **Problem:** A&E overcrowding from triage errors costs NHS £2.4bn/year
- **Solution:** AI pre-triage with 3-tier clinician review — right patient, right place, first time
- **ROI:** Reduction in avoidable A&E admissions

---

## How to Run

### Prerequisites
```
Python 3.12
pip install -r requirements_docker.txt
cp .env.example .env  # add your API keys
```

### Phase 1 — FCA RAG Bot
```
python day14_production_hardening.py
```

### Phase 2 — Research Crew
```
python day28_phase2_complete.py
```

### Phase 3 — Fraud Detection API
```
uvicorn day36_fraud_api:app --reload --port 8000
python day36_test_api.py
```

### Docker
```
docker build -t fraud-agent .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key fraud-agent
```

### Full Integration Test
```
python day38_integration_test.py
```

---

## Contact

**Sheyi Teluwo** — AI Solutions Architect  
📧 sheyi@hotmail.co.uk  
💼 [linkedin.com/in/sheyi](https://linkedin.com/in/sheyi)  
🐙 [github.com/sheyiteluwo-ai](https://github.com/sheyiteluwo-ai)  

*Available for £95,000+ permanent roles or £850+/day contract engagements
in UK Financial Services, Legal, or Healthcare AI.*

---

*Built in 42 days. May–June 2026.*
