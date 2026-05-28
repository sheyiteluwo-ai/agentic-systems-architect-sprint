# Day 36 — Docker Containerisation
# 42-Day Agentic AI Sprint — Sheyi Teluwo
#
# This file is the main Dockerfile for the Phase 3 MCP Agent.
# Build and run instructions are in day36_docker_commands.md
#
# What we containerise today:
#   - The Day 35 Barclays Fraud Detection Agent (as the representative Phase 3 system)
#   - FastAPI wrapper around the fraud detection pipeline
#   - Health check endpoint
#   - Environment variable injection for API keys
#   - Multi-stage build for smaller image size

FROM python:3.12-slim AS base

# ─────────────────────────────────────────────
# METADATA
# ─────────────────────────────────────────────
LABEL maintainer="Sheyi Teluwo <sheyi@hotmail.co.uk>"
LABEL description="Agentic AI Sprint — Phase 3 Fraud Detection Agent"
LABEL version="1.0.0"

# ─────────────────────────────────────────────
# SYSTEM DEPENDENCIES
# ─────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────
# WORKING DIRECTORY
# ─────────────────────────────────────────────
WORKDIR /app

# ─────────────────────────────────────────────
# PYTHON DEPENDENCIES
# Install requirements first (cached layer)
# ─────────────────────────────────────────────
COPY requirements_docker.txt .
RUN pip install --no-cache-dir -r requirements_docker.txt

# ─────────────────────────────────────────────
# APPLICATION CODE
# ─────────────────────────────────────────────
COPY day35_fraud_detection_agent.py .
COPY day36_fraud_api.py .

# ─────────────────────────────────────────────
# ENVIRONMENT VARIABLES
# These are overridden at runtime via docker run -e or docker-compose
# Never hardcode API keys in a Dockerfile
# ─────────────────────────────────────────────
ENV OPENAI_API_KEY=""
ENV LANGCHAIN_API_KEY=""
ENV LANGCHAIN_TRACING_V2="false"
ENV PORT=8000

# ─────────────────────────────────────────────
# HEALTH CHECK
# Docker will call this every 30 seconds
# ─────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# ─────────────────────────────────────────────
# EXPOSE PORT
# ─────────────────────────────────────────────
EXPOSE 8000

# ─────────────────────────────────────────────
# STARTUP COMMAND
# ─────────────────────────────────────────────
CMD ["uvicorn", "day36_fraud_api:app", "--host", "0.0.0.0", "--port", "8000"]
