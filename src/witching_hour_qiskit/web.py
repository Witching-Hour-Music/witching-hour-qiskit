"""HTTP API for Witching Hour qBraid and Qiskit workflows."""

from __future__ import annotations

from typing import Any

import uvicorn
from fastapi import FastAPI, Query
from fastapi import HTTPException
from pydantic import BaseModel, Field

from .api import (
    DEFAULT_DEVICE_ID,
    DEFAULT_SHOTS,
    run_bell_state_job_summary,
    serialize_devices,
)


class RunBellRequest(BaseModel):
    """Request body for running the Bell-state ritual."""

    device_id: str = Field(default=DEFAULT_DEVICE_ID)
    shots: int = Field(default=DEFAULT_SHOTS, ge=1, le=100_000)
    ritual_type: str = Field(default="bell")
    user_id: str | None = None
    wallet: str | None = None


class RunBellResponse(BaseModel):
    """Normalized Bell-state result for Witching Hour clients."""

    job_id: str | None = None
    device_id: str
    shots: int
    counts: dict[str, int]
    dominant_state: str | None = None
    seed: str
    ritual_outcome: str


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    app = FastAPI(
        title="witching-hour-qiskit",
        version="0.1.0",
        description="Minimal qBraid and Qiskit API for Witching Hour ritual runs.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/devices")
    def devices(limit: int = Query(default=10, ge=1, le=100)) -> dict[str, Any]:
        visible_devices = serialize_devices(limit=limit)
        return {
            "count": len(visible_devices),
            "devices": visible_devices,
        }

    @app.post("/run-bell", response_model=RunBellResponse)
    def run_bell(payload: RunBellRequest) -> RunBellResponse:
        if payload.ritual_type != "bell":
            raise HTTPException(
                status_code=400,
                detail="Only the 'bell' ritual_type is currently supported.",
            )

        return RunBellResponse(
            **run_bell_state_job_summary(
                device_id=payload.device_id,
                shots=payload.shots,
            )
        )

    return app


app = create_app()


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the API server with uvicorn."""
    uvicorn.run("witching_hour_qiskit.web:app", host=host, port=port)
