# day10_health_server.py
# Standalone health endpoint server — for LinkedIn screenshot
# Run this, then visit http://localhost:8000/health/deep in your browser

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

load_dotenv()

app = FastAPI(title="RAG Knowledge Bot — Health Check")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "phase": "Phase 1 - RAG Knowledge Bot"
    }

@app.get("/health/deep")
async def health_deep():
    checks = {
        "openai_key_set":    bool(os.getenv("OPENAI_API_KEY")),
        "langsmith_key_set": bool(os.getenv("LANGCHAIN_API_KEY")),
        "logs_dir_exists":   os.path.exists("logs"),
        "chroma_db_exists":  os.path.exists("chroma_db"),
        "env_file_exists":   os.path.exists(".env"),
    }
    all_ok = all(checks.values())
    return JSONResponse(content={
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)