Day 8 of 42 — My RAG System is Now a REST API 🚀

Today I wrapped my FCA compliance AI in FastAPI.

It is no longer just a script you run in a terminal.
It is a production REST API that any application
can call via HTTP.

What the API returns for every query:

{
  "answer": "The four outcomes are: products 
             and services, price and value, 
             consumer understanding, consumer support",
  "hitl_decision": "answer_directly",
  "sources_used": [
    "FCA Consumer Duty PS22/9",
    "FCA Complaints DISP 1",
    "FCA Vulnerable Customers FG21/1"
  ],
  "session_id": "test-session-001",
  "timestamp": "2026-05-03T19:44:44",
  "escalated": false
}

Every response includes:
✅ The answer with source citations
✅ HITL decision — safe/flagged/escalated
✅ Which documents were used
✅ Session ID for conversation memory
✅ Timestamp for audit trail

A Barclays web portal could connect to this today.
An NHS mobile app could connect to this today.
A Magic Circle internal tool could connect to this today.

8 days in. Building in public.

github.com/sheyiteluwo-ai/agentic-systems-architect-sprint

#AgenticAI #FastAPI #RAG #FCA #APIDesign
#UKFintech #BuildingInPublic #LangChain