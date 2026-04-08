"""Client for connecting to the Wildfire Dispatch OpenEnv environment."""

from __future__ import annotations

from typing import Any, Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult

from models import (
    AircraftInfo,
    CrewInfo,
    EvacZoneInfo,
    FireInfo,
    WeatherInfo,
    WildfireAction,
    WildfireObservation,
    WildfireState,
)


class WildfireDispatchEnv(EnvClient[WildfireAction, WildfireObservation, WildfireState]):
    """Typed OpenEnv client for the Wildfire Dispatch environment."""

    def _step_payload(self, action: WildfireAction) -> Dict[str, Any]:
        at = action.action_type
        return {
            "action_type": at.value if hasattr(at, "value") else str(at),
            "parameters": dict(action.parameters or {}),
        }

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[WildfireObservation]:
        obs_data = payload.get("observation", {}) or {}

        def _build_list(key, cls):
            return [cls(**item) for item in obs_data.get(key, []) or []]

        weather_data = obs_data.get("weather")
        weather = WeatherInfo(**weather_data) if weather_data else None

        observation = WildfireObservation(
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}) or {},
            fires=_build_list("fires", FireInfo),
            crews=_build_list("crews", CrewInfo),
            aircraft=_build_list("aircraft", AircraftInfo),
            evacuation_zones=_build_list("evacuation_zones", EvacZoneInfo),
            weather=weather,
            budget_remaining=obs_data.get("budget_remaining", 0.0),
            budget_total=obs_data.get("budget_total", 0.0),
            time_elapsed_hours=obs_data.get("time_elapsed_hours", 0.0),
            communication_log=obs_data.get("communication_log", []) or [],
            available_actions=obs_data.get("available_actions", []) or [],
            hint=obs_data.get("hint", ""),
            task_id=obs_data.get("task_id", ""),
            task_description=obs_data.get("task_description", ""),
            mutual_aid_eta_hours=obs_data.get("mutual_aid_eta_hours"),
            situation_report=obs_data.get("situation_report", ""),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict[str, Any]) -> WildfireState:
        try:
            return WildfireState(**payload)
        except Exception:
            # Tolerate unexpected extra fields — WildfireState allows extras.
            return WildfireState(
                episode_id=payload.get("episode_id"),
                step_count=payload.get("step_count", 0),
            )
