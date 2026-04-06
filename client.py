"""Client for connecting to the Wildfire Dispatch environment."""

from __future__ import annotations

try:
    from openenv.core.env_client import EnvClient
except ImportError:
    class EnvClient:
        """Minimal fallback when openenv-core is not installed."""

        def __init__(self, base_url: str = "http://localhost:8000"):
            self.base_url = base_url

        @classmethod
        async def from_docker_image(cls, image_name: str, **kwargs):
            raise NotImplementedError(
                "from_docker_image requires openenv-core. "
                "pip install openenv-core"
            )


class WildfireDispatchEnv(EnvClient):
    """Typed OpenEnv client for the Wildfire Dispatch environment."""
    pass
