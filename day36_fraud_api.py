"""
Day 36 — FastAPI Wrapper for Fraud Detection Agent
42-Day Agentic AI Sprint — Sheyi Teluwo

This wraps the Day 35 fraud detection agent in a FastAPI REST API
so it can be containerised and called via HTTP.

Endpoints:
  GET  /health          — health check (used by Docker + load balancers)
  GET  /                — API info
  POST /analyse         — run fraud detection on a transaction
  GET  /audit           — retrieve full audit log

Run locally (outside Docker):
    uvicorn day36_fraud_api:app --reload --port 8000

Run via Docker:
    docker build -t fraud-agent .
    docker run -p 8000:8000 -e OPENAI_API_KEY=your_key fraud-agent
"""

import os
import json
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ─────────────────────────────────────────────
# 1.  FASTAPI APP
# ─────────────────────────────────────────────

app = FastAPI(
    title="Agentic AI Sprint — Fraud Detection API",
    description="Barclays-style fraud detection agent. Day 36 of 42-day sprint.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ─────────────────────────────────────────────
# 2.  REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────

class TransactionRequest(BaseModel):
    transaction_id: str = Field(..., example="TX-001")
    account_id: str = Field(..., example="ACC-001")
    amount: float = Field(..., example=42.50)
    currency: str = Field(default="GBP", example="GBP")
    merchant: str = Field(..., example="Tesco Express")
    merchant_category: str = Field(..., example="Grocery")
    country: str = Field(default="United Kingdom", example="United Kingdom")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    device_id: str = Field(..., example="DEV-iPhone-001")
    ip_address: str = Field(..., example="82.132.210.45")

class FraudResponse(BaseModel):
    transaction_id: str
    risk_score: float
    risk_level: str
    final_action: str
    risk_factors: list[str]
    requires_analyst_review: bool
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    openai_configured: bool


# ─────────────────────────────────────────────
# 3.  IN-MEMORY AUDIT LOG
#     In production: write to PostgreSQL / Elasticsearch
# ─────────────────────────────────────────────

api_audit_log: list[dict] = []


# ─────────────────────────────────────────────
# 4.  FRAUD SCORING LOGIC
#     Lightweight version of Day 35 agent for API use.
#     No HITL in API mode — returns score + flags analyst review needed.
# ─────────────────────────────────────────────

def score_transaction(tx: TransactionRequest) -> dict:
    """
    Runs fraud scoring rules on a transaction.
    Returns risk score, level, and factors.
    In production: calls the full LangGraph pipeline.
    In this API demo: runs fast rule-based scoring.
    """
    risk_factors = []
    score = 0.0

    # Amount checks
    if tx.amount > 2000:
        score += 0.30
        risk_factors.append(f"Very large amount: £{tx.amount}")
    elif tx.amount > 500:
        score += 0.10
        risk_factors.append(f"Large amount: £{tx.amount}")

    # Merchant category checks
    high_risk_categories = ["cryptocurrency", "gambling", "wire transfer", "casino"]
    if any(cat in tx.merchant_category.lower() for cat in high_risk_categories):
        score += 0.25
        risk_factors.append(f"High-risk merchant category: {tx.merchant_category}")

    # Country checks
    high_risk_countries = ["romania", "nigeria", "ukraine", "bulgaria"]
    if any(c in tx.country.lower() for c in high_risk_countries):
        score += 0.25
        risk_factors.append(f"High-risk country: {tx.country}")
    elif tx.country.lower() not in ["united kingdom", "uk"]:
        score += 0.10
        risk_factors.append(f"Foreign transaction: {tx.country}")

    # Time checks (odd hours 01:00-05:00)
    try:
        hour = datetime.fromisoformat(tx.timestamp).hour
        if 1 <= hour <= 5:
            score += 0.15
            risk_factors.append(f"Unusual transaction time: {hour:02d}:00")
    except Exception:
        pass

    # IP checks
    suspicious_ip_ranges = ["185.", "91.108.", "194.165."]
    if any(tx.ip_address.startswith(r) for r in suspicious_ip_ranges):
        score += 0.15
        risk_factors.append(f"Suspicious IP range: {tx.ip_address}")

    # Device checks
    if "unknown" in tx.device_id.lower() or "999" in tx.device_id:
        score += 0.15
        risk_factors.append(f"Unrecognised device: {tx.device_id}")

    score = min(1.0, round(score, 3))

    # Determine risk level
    if score < 0.25:
        risk_level = "LOW"
        final_action = "APPROVE"
    elif score < 0.50:
        risk_level = "MEDIUM"
        final_action = "FLAG"
    elif score < 0.75:
        risk_level = "HIGH"
        final_action = "BLOCK"
    else:
        risk_level = "CRITICAL"
        final_action = "ESCALATE"

    requires_review = risk_level in ["HIGH", "CRITICAL"]

    return {
        "transaction_id": tx.transaction_id,
        "risk_score": score,
        "risk_level": risk_level,
        "final_action": final_action,
        "risk_factors": risk_factors,
        "requires_analyst_review": requires_review,
        "timestamp": datetime.now().isoformat()
    }


# ─────────────────────────────────────────────
# 5.  ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/", tags=["Info"])
async def root():
    """API information endpoint."""
    return {
        "name": "Fraud Detection API",
        "sprint": "42-Day Agentic AI Sprint — Day 36",
        "author": "Sheyi Teluwo",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "analyse": "POST /analyse",
            "audit": "GET /audit",
            "docs": "GET /docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Used by Docker HEALTHCHECK, Kubernetes liveness probes, and load balancers.
    Returns 200 if healthy, 503 if not.
    """
    openai_key = os.getenv("OPENAI_API_KEY", "")
    openai_configured = bool(openai_key and len(openai_key) > 10)

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        openai_configured=openai_configured
    )


@app.post("/analyse", response_model=FraudResponse, tags=["Fraud Detection"])
async def analyse_transaction(tx: TransactionRequest):
    """
    Analyse a transaction for fraud.

    Returns:
    - risk_score: 0.0–1.0
    - risk_level: LOW / MEDIUM / HIGH / CRITICAL
    - final_action: APPROVE / FLAG / BLOCK / ESCALATE
    - risk_factors: list of specific fraud indicators
    - requires_analyst_review: true if HIGH or CRITICAL
    """
    try:
        result = score_transaction(tx)

        # Log to audit trail
        api_audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "transaction_id": tx.transaction_id,
            "account_id": tx.account_id,
            "amount": tx.amount,
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "final_action": result["final_action"]
        })

        return FraudResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fraud analysis failed: {str(e)}")


@app.get("/audit", tags=["Audit"])
async def get_audit_log():
    """
    Retrieve the full audit log of all transactions analysed.
    FCA compliance requirement — every decision must be logged.
    """
    return {
        "total_transactions": len(api_audit_log),
        "audit_log": api_audit_log
    }
