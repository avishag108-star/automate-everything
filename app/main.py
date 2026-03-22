"""
StatusWatch — URL Health Checker API
A simple FastAPI app that checks if websites/services are up.
Perfect for a DevOps portfolio: real use-case, easy to understand.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from prometheus_fastapi_instrumentator import Instrumentator
import httpx
import time
import os

app = FastAPI(
    title="StatusWatch",
    description="URL Health Checker — built for DevOps portfolio",
    version="1.0.0",
)

# Expose /metrics for Prometheus scraping
Instrumentator().instrument(app).expose(app)


class CheckRequest(BaseModel):
    url: HttpUrl
    timeout: int = 5


class CheckResult(BaseModel):
    url: str
    status: str          # "up" or "down"
    status_code: int | None
    response_time_ms: float | None
    checked_at: float


@app.get("/health")
def health():
    """Kubernetes liveness & readiness probe endpoint."""
    return {"status": "ok", "version": os.getenv("APP_VERSION", "dev")}


@app.post("/check", response_model=CheckResult)
async def check_url(req: CheckRequest):
    """Check if a URL is reachable and return its status."""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=req.timeout) as client:
            response = await client.get(str(req.url))
        elapsed = round((time.time() - start) * 1000, 2)
        return CheckResult(
            url=str(req.url),
            status="up" if response.status_code < 500 else "down",
            status_code=response.status_code,
            response_time_ms=elapsed,
            checked_at=time.time(),
        )
    except Exception:
        return CheckResult(
            url=str(req.url),
            status="down",
            status_code=None,
            response_time_ms=None,
            checked_at=time.time(),
        )


@app.get("/")
def root():
    return {"message": "StatusWatch API — use /check to test a URL", "docs": "/docs"}
