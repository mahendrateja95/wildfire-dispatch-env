"""FastAPI application for the Wildfire Dispatch OpenEnv environment.

Uses openenv.core.env_server.http_server.create_app to expose the
WildfireDispatchEnvironment over HTTP and WebSocket endpoints, compatible
with EnvClient (matches the official OpenEnv hackathon sample pattern).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError(
        "openenv is required for the web interface. "
        "Install dependencies with 'pip install openenv-core'."
    ) from e

from models import WildfireAction, WildfireObservation
from server.environment import WildfireDispatchEnvironment
from scenarios import ALL_SCENARIOS
from graders import GRADERS


app = create_app(
    WildfireDispatchEnvironment,
    WildfireAction,
    WildfireObservation,
    env_name="wildfire_dispatch",
    max_concurrent_envs=1,
)


# ---------------------------------------------------------------------------
# Task discovery endpoints -- expose tasks + graders so external validators
# can enumerate them without parsing scenarios.py.
# ---------------------------------------------------------------------------

def _build_task_manifest():
    """Return a list of tasks with grader info for the validator."""
    manifest = []
    for task_id, scenario in ALL_SCENARIOS.items():
        grader = GRADERS.get(task_id)
        manifest.append({
            "task_id": task_id,
            "name": scenario.get("name", task_id),
            "description": scenario.get("description", ""),
            "difficulty": scenario.get("difficulty", "unknown"),
            "max_steps": scenario.get("max_steps", 20),
            "has_grader": grader is not None,
            "grader_name": grader.__name__ if grader else None,
            "score_range": [0.0, 1.0],
        })
    return manifest


@app.get("/tasks", tags=["Tasks"], summary="List all tasks with graders")
def list_tasks():
    """Enumerate all tasks available in this environment, each with its grader.

    The hackathon validator uses this to verify the env exposes 3+ graded tasks.
    """
    tasks = _build_task_manifest()
    return {
        "count": len(tasks),
        "tasks": tasks,
        "graders": {tid: g.__name__ for tid, g in GRADERS.items()},
    }


@app.get("/grade/{task_id}", tags=["Tasks"], summary="Run a grader against current state")
def grade_task(task_id: str):
    """Run the grader for the given task against the current environment state.

    Returns a deterministic score in [0.0, 1.0]. Used by the validator to
    confirm graders produce in-range scores.
    """
    if task_id not in GRADERS:
        return {"error": f"Unknown task '{task_id}'", "available": list(GRADERS.keys())}
    grader = GRADERS[task_id]
    # Run grader against an empty state -- just to verify it executes and
    # returns a value in [0.0, 1.0]. Real grading happens during step().
    sample_state = {
        "task_id": task_id,
        "step_count": 1,
        "max_steps": 20,
        "fires": {}, "crews": {}, "aircraft": {}, "evac_zones": {},
        "evacuations_ordered": [], "communications_sent": [],
        "diagnostics_run": [], "dangerous_actions_taken": [],
        "priorities_reassessed": [], "crews_rotated": [],
        "firebreaks_created": [], "action_history": [],
        "mutual_aid_requested": False, "resolved": False, "penalties": 0.0,
        "budget_remaining": 500000, "budget_total": 500000,
    }
    score = grader(sample_state)
    return {
        "task_id": task_id,
        "grader": grader.__name__,
        "score": float(score),
        "in_range": 0.0 <= score <= 1.0,
    }


def main() -> None:
    """Entry point for `python -m server.app`."""
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    port = args.port if args.port is not None else int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host=args.host, port=port)


if __name__ == "__main__":
    main()
