# Architecture Decision Records (ADRs)
## 42-Day Agentic AI Sprint — Sheyi Teluwo

ADRs document every major technical decision made during the sprint,
including the context, the options considered, and why the chosen approach was selected.

---

## ADR-001: Vector Store — ChromaDB over Pinecone

**Date:** Day 2  
**Status:** Accepted  

### Context
Phase 1 required a vector store to index 494 FCA document chunks for semantic retrieval.

### Options Considered
| Option | Pros | Cons |
|---|---|---|
| ChromaDB | Free, local, no API key, persistent | Not cloud-native |
| Pinecone | Managed, scalable, cloud-native | Paid, adds dependency |
| FAISS | Fast, free | In-memory only, no persistence |

### Decision
ChromaDB with persistent storage.

### Reasoning
For a portfolio sprint, removing external dependencies reduces setup friction.
ChromaDB's persistence means the index survives restarts — critical for demo reliability.
In production, Pinecone or Weaviate would be preferred for scale.

---

## ADR-002: LLM Routing — GPT-4o for Reasoning, Claude for Writing

**Date:** Day 18  
**Status:** Accepted  

### Context
Phase 2 multi-agent crew needed different LLMs for different task types.

### Options Considered
| Option | Pros | Cons |
|---|---|---|
| GPT-4o only | Simpler, one API | Less optimal for writing tasks |
| Claude only | Excellent writing | Less strong on structured reasoning |
| Routing by task | Best model per task | More complex implementation |

### Decision
GPT-4o for research/reasoning tasks. Claude for writing/summarisation tasks.

### Reasoning
Real enterprise AI systems use model routing to optimise cost and quality per task type.
This demonstrates awareness of the production LLM landscape — a key differentiator
in senior AI engineering interviews.

---

## ADR-003: Agent Orchestration — LangGraph over AutoGen

**Date:** Day 16  
**Status:** Accepted  

### Context
Phase 2 required a state machine to orchestrate multi-agent workflows with
conditional routing and HITL gates.

### Options Considered
| Option | Pros | Cons |
|---|---|---|
| LangGraph | Explicit state, conditional edges, HITL-ready | More verbose |
| AutoGen | Less code | Black-box orchestration, harder to audit |
| CrewAI alone | Simple API | Less control over state transitions |

### Decision
LangGraph for state machine orchestration, CrewAI for agent definitions.

### Reasoning
Regulated industries (FCA, NHS, SRA) require auditable AI pipelines.
LangGraph's explicit state object and conditional edges make every decision
traceable — which is a hard requirement for enterprise deployment.
AutoGen's implicit orchestration makes audit trails harder to implement.

---

## ADR-004: HITL Implementation — Synchronous Input over Async Queue

**Date:** Day 7  
**Status:** Accepted  

### Context
All three phases required Human-in-the-Loop gates for high-risk outputs.

### Options Considered
| Option | Pros | Cons |
|---|---|---|
| Synchronous terminal input | Simple, reliable, demonstrable | Not production-scalable |
| Async message queue (Redis/SQS) | Production-ready | Complex, overkill for sprint |
| Webhook callback | API-friendly | Requires separate service |

### Decision
Synchronous terminal input for the sprint. Architecture notes production path.

### Reasoning
For a portfolio demonstration, synchronous HITL clearly shows the concept to
interviewers and CTOs. The code structure (separate node in LangGraph) means
swapping to async queues in production requires changing only the node implementation,
not the graph architecture.

---

## ADR-005: Search Tool — DuckDuckGo over Serper/Tavily

**Date:** Day 23  
**Status:** Accepted  

### Context
Phase 2 and Phase 3 agents needed live web search capability.

### Options Considered
| Option | Pros | Cons |
|---|---|---|
| DuckDuckGo (ddgs) | Free, no API key, reliable | Rate limits at high volume |
| Serper | Fast, structured results | Paid ($50/month) |
| Tavily | AI-optimised | Paid, newer |

### Decision
DuckDuckGo via the ddgs package.

### Reasoning
Removing paid dependencies lowers the barrier to running the sprint code.
DuckDuckGo is sufficient for portfolio demonstration purposes.
In production, Serper or Tavily would be preferred for reliability and rate limits.

---

## ADR-006: Evaluation Framework — LangSmith over Custom Metrics

**Date:** Day 6  
**Status:** Accepted  

### Context
Every phase required measurable evaluation of AI output quality.

### Options Considered
| Option | Pros | Cons |
|---|---|---|
| LangSmith | Industry standard, dashboard, tracing | Requires API key |
| Custom scoring | Full control | No industry benchmark |
| Ragas | RAG-specific | Limited to retrieval evals |

### Decision
LangSmith for all evaluations.

### Reasoning
LangSmith is the industry standard for LLM observability in 2026.
Mentioning LangSmith eval scores (0.94 correctness, 1.0 bias) in interviews
signals production engineering maturity. Custom metrics would not carry the same weight.

---

## ADR-007: Containerisation — Docker over Serverless

**Date:** Day 36  
**Status:** Accepted  

### Context
Phase 3 required a deployment strategy for the fraud detection agent.

### Options Considered
| Option | Pros | Cons |
|---|---|---|
| Docker + docker-compose | Portable, industry standard | Requires container runtime |
| AWS Lambda | Serverless, auto-scaling | Cold starts, complex for LLM workloads |
| Heroku | Simple deploy | Limited free tier, less enterprise credibility |

### Decision
Docker with docker-compose.

### Reasoning
Docker is the standard deployment unit for enterprise AI in 2026.
Every Tier 1 bank, NHS trust, and law firm runs containerised workloads.
Showing a working Dockerfile + health check + CI/CD pipeline signals
production engineering readiness to technical interviewers.

---

## ADR-008: CI/CD — GitHub Actions over Jenkins/CircleCI

**Date:** Day 37  
**Status:** Accepted  

### Context
The sprint needed an automated testing and build pipeline.

### Options Considered
| Option | Pros | Cons |
|---|---|---|
| GitHub Actions | Free, integrated with GitHub, YAML-based | Limited compute minutes |
| Jenkins | Powerful, self-hosted | Requires server setup |
| CircleCI | Fast, good UI | Paid for parallelism |

### Decision
GitHub Actions.

### Reasoning
GitHub Actions is free for public repos and integrates directly with the sprint
repository. The 5-job pipeline (lint, test, docker build, security, notify) runs
in 1m 14s — demonstrating CI/CD competency without infrastructure overhead.

---

*These ADRs will be referenced in the Day 41 Loom demo and used as talking points
in technical interviews for senior AI engineering roles.*
