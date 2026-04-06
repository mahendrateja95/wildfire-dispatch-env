"""FastAPI application for the Wildfire Dispatch OpenEnv environment."""

from __future__ import annotations

import sys
import os
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.environment import WildfireDispatchEnvironment
from models import WildfireAction, WildfireObservation, WildfireState


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ResetRequest(BaseModel):
    seed: Optional[int] = Field(default=None, ge=0)
    episode_id: Optional[str] = Field(default=None, max_length=255)
    task_id: str = Field(
        default="easy_single_fire",
        description="Task: easy_single_fire | medium_two_fires | hard_cascading_disaster",
    )


class ResetResponse(BaseModel):
    observation: Dict[str, Any]
    reward: Optional[float] = None
    done: bool = False


class StepRequest(BaseModel):
    action: Dict[str, Any]
    timeout_s: Optional[float] = Field(default=None, gt=0)
    request_id: Optional[str] = Field(default=None, max_length=255)


class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: Optional[float] = None
    done: bool = False


class HealthResponse(BaseModel):
    status: str = "healthy"


class MetadataResponse(BaseModel):
    name: str
    description: str


class SchemaResponse(BaseModel):
    action: Dict[str, Any]
    observation: Dict[str, Any]
    state: Dict[str, Any]


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Wildfire Dispatch Environment",
    description="OpenEnv environment simulating wildfire resource dispatch and emergency coordination",
    version="0.1.0",
)

env = WildfireDispatchEnvironment()


@app.get("/")
def root():
    return {
        "name": "wildfire_dispatch_env",
        "description": "Wildfire Dispatch Environment - OpenEnv",
        "version": "0.1.0",
        "endpoints": ["/health", "/metadata", "/schema", "/reset (POST)", "/step (POST)", "/state", "/docs"],
        "tasks": ["easy_single_fire", "medium_two_fires", "hard_cascading_disaster"],
    }


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="healthy")


@app.get("/metadata", response_model=MetadataResponse)
def metadata():
    return MetadataResponse(
        name="wildfire_dispatch_env",
        description=(
            "Simulates real-world wildfire resource dispatch: allocate firefighting crews, "
            "aircraft, and equipment across active wildfires. Manage evacuations, handle "
            "weather shifts, avoid dangerous decisions, and protect lives under pressure. "
            "3 tasks from single fire containment to cascading multi-fire disaster."
        ),
    )


@app.get("/schema", response_model=SchemaResponse)
def schema():
    return SchemaResponse(
        action=WildfireAction.model_json_schema(),
        observation=WildfireObservation.model_json_schema(),
        state=WildfireState.model_json_schema(),
    )


@app.post("/reset", response_model=ResetResponse)
def reset(req: ResetRequest):
    obs = env.reset(seed=req.seed, task_id=req.task_id)
    return ResetResponse(
        observation=obs.model_dump(),
        reward=obs.reward,
        done=obs.done,
    )


@app.post("/step", response_model=StepResponse)
def step(req: StepRequest):
    try:
        action = WildfireAction(**req.action)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid action: {e}")

    obs, reward, done, info = env.step(action)
    obs_dict = obs.model_dump()
    obs_dict["info"] = info

    return StepResponse(
        observation=obs_dict,
        reward=reward,
        done=done,
    )


@app.get("/state")
def state():
    try:
        s = env.state()
        return s.model_dump()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


def main():
    """Entry point for server."""
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
