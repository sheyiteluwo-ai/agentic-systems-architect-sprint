import json
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import DocArrayInMemorySearch
import uvicorn

load_dotenv()

# ── Request and Response models ───────────────────────────────────────
# These define exactly what the API accepts and returns.
# Pydantic validates every request automatically.
# If a field is missing or wrong type, FastAPI returns
# a clear error message automatically.

class QueryRequest(BaseModel):
    question: str
    session_id: str = "default"
    client_classification: str = "retail"

class QueryResponse(BaseModel):
    question: str
    answer: str
    hitl_decision: str
    sources_used: list
    session_id: str
    timestamp: str
    escalated: bool
    reference: str = ""

class HealthResponse(BaseModel):
    status: str
    documents_loaded: int
    chunks_indexed: int
    hitl_gate: str
    timestamp: str

# ── HITL Decision Types ───────────────────────────────────────────────
class HITLDecision(Enum):
    ANSWER_DIRECTLY   = "answer_directly"
    ANSWER_WITH_FLAG  = "answer_with_flag"
    ESCALATE_TO_HUMAN = "escalate_to_human"

ESCALATION_TRIGGERS = [
    "sue", "legal action", "court", "tribunal",
    "liability", "compensation claim", "damages",
    "enforcement", "investigation", "prosecution",
    "my specific case", "my complaint", "my situation",
    "should i complain", "can i get compensation",
    "am i entitled", "what should i do",
    "mental health", "dementia", "power of attorney",
    "bereavement", "suicide", "crisis",
    "pension", "inheritance", "redundancy",
]

FLAG_TRIGGERS = [
    "must", "legally required", "mandatory", "obligation",
    "breach", "deadline", "enforcement", "penalty",
    "maximum", "minimum", "limit",
]

def assess_hitl(question):
    q = question.lower()
    escalation = [t for t in ESCALATION_TRIGGERS if t in q]
    if escalation:
        return (HITLDecision.ESCALATE_TO_HUMAN,
                "High-stakes terms: " + ", ".join(escalation[:3]))
    flags = [t for t in FLAG_TRIGGERS if t in q]
    if flags:
        return (HITLDecision.ANSWER_WITH_FLAG,
                "Regulatory obligation language detected")
    return (HITLDecision.ANSWER_DIRECTLY,
            "Safe to answer directly")

# ── Load documents and build vector store ────────────────────────────
print("Loading FCA documents...")

def load_and_tag(loader, source_doc, doc_type):
    docs = loader.load()
    for doc in docs:
        doc.metadata["source_doc"] = source_doc
        doc.metadata["doc_type"] = doc_type
        doc.metadata["page_display"] = doc.metadata.get("page", 0) + 1
    return docs

consumer_duty_docs = load_and_tag(
    PyPDFLoader("fca_consumer_duty.pdf"),
    "FCA Consumer Duty PS22/9", "Policy Statement"
)
complaints_docs = load_and_tag(
    TextLoader("fca_complaints_rules.txt", encoding="utf-8"),
    "FCA Complaints DISP 1", "Handbook Rules"
)
vulnerable_docs = load_and_tag(
    TextLoader("fca_vulnerable_customers.txt", encoding="utf-8"),
    "FCA Vulnerable Customers FG21/1", "Finalised Guidance"
)
extended_docs = load_and_tag(
    TextLoader("fca_complaints_extended.txt", encoding="utf-8"),
    "FCA Complaints Extended DISP", "Handbook Rules"
)

all_documents = (consumer_duty_docs + complaints_docs +
                 vulnerable_docs + extended_docs)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=300,
)
all_chunks = splitter.split_documents(all_documents)

embeddings  = OpenAIEmbeddings()
vectorstore = DocArrayInMemorySearch.from_documents(all_chunks, embeddings)
retriever   = vectorstore.as_retriever(search_kwargs={"k": 6})

print(f"Loaded {len(all_chunks)} chunks across 4 FCA documents")

# ── RAG chain ─────────────────────────────────────────────────────────
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior UK Compliance Officer.
Answer using ONLY the context provided.
Always cite source document and page number.
Use must/should/may exactly as the FCA uses them.
State which client classification applies.
If the answer is not in the context say so explicitly.

Client Classification: {client_classification}

CONTEXT:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

llm   = ChatOpenAI(model="gpt-4o", temperature=0.1)
chain = rag_prompt | llm | StrOutputParser()

# Session memory store
# In production this would be Redis or a database
# For now we use a simple dictionary
session_store = {}

def get_session_history(session_id: str) -> list:
    if session_id not in session_store:
        session_store[session_id] = []
    return session_store[session_id]

def get_rag_answer(question, session_id, client_classification):
    docs    = retriever.invoke(question)
    context = "\n\n".join(
        "[" + d.metadata.get("source_doc", "Unknown") +
        " | Page " + str(d.metadata.get("page_display", "?")) +
        "]\n" + d.page_content
        for d in docs
    )
    sources = list(set(
        d.metadata.get("source_doc", "Unknown") for d in docs
    ))
    history = get_session_history(session_id)
    answer  = chain.invoke({
        "context":               context,
        "question":              question,
        "chat_history":          history,
        "client_classification": client_classification,
    })
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=answer))
    return answer, sources

# ── FastAPI app ───────────────────────────────────────────────────────
app = FastAPI(
    title="FCA Compliance Intelligence API",
    description=(
        "Production-grade RAG system for UK Financial Services compliance. "
        "Queries FCA Consumer Duty, Complaints Handling and Vulnerable "
        "Customer guidance with Human-in-the-Loop safety gates."
    ),
    version="1.0.0",
    docs_url="/docs",
)

# Allow all origins for development
# In production restrict to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

escalation_counter = 0

# ── API Endpoints ─────────────────────────────────────────────────────

@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns system status and document statistics.
    Call this first to verify the API is running.
    """
    return HealthResponse(
        status="healthy",
        documents_loaded=len(all_documents),
        chunks_indexed=len(all_chunks),
        hitl_gate="active",
        timestamp=datetime.now().isoformat(),
    )

@app.post("/query", response_model=QueryResponse)
async def query_compliance(request: QueryRequest):
    """
    Main compliance query endpoint.
    Accepts a question and returns an answer with:
    - Source document citations
    - HITL decision (direct/flagged/escalated)
    - Session memory for follow-up questions
    - Compliance notices where required
    """
    global escalation_counter

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    if len(request.question) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Question too long — maximum 1000 characters"
        )

    decision, reason = assess_hitl(request.question)

    if decision == HITLDecision.ESCALATE_TO_HUMAN:
        escalation_counter += 1
        ref = "REF-" + str(escalation_counter).zfill(4)
        return QueryResponse(
            question=request.question,
            answer=(
                "This question has been escalated to a qualified "
                "compliance officer for review. " + reason +
                ". Reference: " + ref +
                ". Expected response within 2 business hours."
            ),
            hitl_decision="escalated",
            sources_used=[],
            session_id=request.session_id,
            timestamp=datetime.now().isoformat(),
            escalated=True,
            reference=ref,
        )

    answer, sources = get_rag_answer(
        request.question,
        request.session_id,
        request.client_classification,
    )

    if decision == HITLDecision.ANSWER_WITH_FLAG:
        answer = (answer + "\n\nCOMPLIANCE NOTICE: This answer addresses "
                  "regulatory obligations. Please verify with your "
                  "compliance team before acting on this information.")

    return QueryResponse(
        question=request.question,
        answer=answer,
        hitl_decision=decision.value,
        sources_used=sources,
        session_id=request.session_id,
        timestamp=datetime.now().isoformat(),
        escalated=False,
    )

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clears conversation memory for a session.
    Call this to start a fresh conversation.
    """
    if session_id in session_store:
        del session_store[session_id]
        return {"message": "Session cleared", "session_id": session_id}
    return {"message": "Session not found", "session_id": session_id}

@app.get("/sessions")
async def list_sessions():
    """
    Lists all active sessions and their message counts.
    """
    return {
        "active_sessions": len(session_store),
        "sessions": {
            sid: len(msgs) // 2
            for sid, msgs in session_store.items()
        }
    }

# ── Run the server ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*65)
    print("FCA COMPLIANCE API STARTING")
    print("="*65)
    print("API docs:    http://localhost:8000/docs")
    print("Health:      http://localhost:8000/")
    print("Query:       http://localhost:8000/query")
    print("="*65 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)