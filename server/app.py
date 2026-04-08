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


app = create_app(
    WildfireDispatchEnvironment,
    WildfireAction,
    WildfireObservation,
    env_name="wildfire_dispatch",
    max_concurrent_envs=1,
)


def main(host: str = "0.0.0.0", port: int | None = None) -> None:
    """Entry point for `python -m server.app`."""
    import uvicorn

    if port is None:
        port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()
    main(host=args.host, port=args.port)
