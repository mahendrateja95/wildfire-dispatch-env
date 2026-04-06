"""Pydantic models for the Wildfire Dispatch environment."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

try:
    from openenv.core.env_server.types import Action, Observation, State
except ImportError:
    from pydantic import BaseModel, ConfigDict

    class Action(BaseModel):
        model_config = ConfigDict(extra="forbid", validate_assignment=True, arbitrary_types_allowed=True)
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class Observation(BaseModel):
        model_config = ConfigDict(extra="forbid", validate_assignment=True, arbitrary_types_allowed=True)
        done: bool = Field(default=False)
        reward: float | int | None = Field(default=None)
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class State(BaseModel):
        model_config = ConfigDict(extra="allow", validate_assignment=True, arbitrary_types_allowed=True)
        episode_id: Optional[str] = None
        step_count: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ActionType(str, Enum):
    DEPLOY_CREW = "deploy_crew"
    DEPLOY_AIRCRAFT = "deploy_aircraft"
    CREATE_FIREBREAK = "create_firebreak"
    ORDER_EVACUATION = "order_evacuation"
    ROTATE_CREW = "rotate_crew"
    REQUEST_MUTUAL_AID = "request_mutual_aid"
    REASSESS_PRIORITY = "reassess_priority"
    SET_BACKFIRE = "set_backfire"
    INVESTIGATE = "investigate"
    COMMUNICATE = "communicate"
    RESOLVE = "resolve"


class CrewStatus(str, Enum):
    AVAILABLE = "available"
    DEPLOYED = "deployed"
    FATIGUED = "fatigued"
    INJURED = "injured"
    EN_ROUTE = "en_route"


class AircraftStatus(str, Enum):
    AVAILABLE = "available"
    DEPLOYED = "deployed"
    MAINTENANCE = "maintenance"
    REFUELING = "refueling"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class FireInfo(Observation):
    """Information about an active wildfire."""
    fire_id: str = Field(default="", description="Unique fire identifier")
    name: str = Field(default="", description="Fire name")
    acres: float = Field(default=0.0, description="Current fire size in acres")
    containment_percent: float = Field(default=0.0, description="Percentage contained (0-100)")
    spread_direction: str = Field(default="", description="Direction fire is spreading")
    spread_rate_acres_per_hour: float = Field(default=0.0, description="How fast fire is growing")
    terrain: str = Field(default="", description="Terrain type: forest, grassland, urban_interface, canyon")
    priority: int = Field(default=3, description="Current priority 1(highest) to 5(lowest)")
    threats: List[str] = Field(default_factory=list, description="What the fire threatens")
    crews_assigned: List[str] = Field(default_factory=list, description="Crew IDs assigned")
    aircraft_assigned: List[str] = Field(default_factory=list, description="Aircraft IDs assigned")


class CrewInfo(Observation):
    """Information about a firefighting crew."""
    crew_id: str = Field(default="")
    name: str = Field(default="")
    size: int = Field(default=20)
    status: str = Field(default="available")
    hours_on_duty: float = Field(default=0.0)
    assigned_to: Optional[str] = Field(default=None, description="Fire ID if deployed")
    location: str = Field(default="base")
    specialty: str = Field(default="general", description="general, hotshot, structure_protection")


class AircraftInfo(Observation):
    """Information about an aircraft."""
    aircraft_id: str = Field(default="")
    name: str = Field(default="")
    aircraft_type: str = Field(default="helicopter", description="helicopter, air_tanker")
    status: str = Field(default="available")
    water_capacity_gallons: int = Field(default=2000)
    assigned_to: Optional[str] = Field(default=None)
    location: str = Field(default="airbase")


class EvacZoneInfo(Observation):
    """Information about an evacuation zone."""
    zone_id: str = Field(default="")
    name: str = Field(default="")
    population: int = Field(default=0)
    distance_to_nearest_fire_km: float = Field(default=0.0)
    nearest_fire: str = Field(default="")
    is_evacuated: bool = Field(default=False)
    has_vulnerable: bool = Field(default=False, description="School, hospital, elderly home")
    description: str = Field(default="")


class WeatherInfo(Observation):
    """Weather conditions."""
    wind_speed_kmh: float = Field(default=0.0)
    wind_direction: str = Field(default="N")
    temperature_celsius: float = Field(default=30.0)
    humidity_percent: float = Field(default=30.0)
    forecast_change: str = Field(default="", description="Predicted change in coming hours")
    fire_danger_rating: str = Field(default="high", description="low, moderate, high, very_high, extreme")


# ---------------------------------------------------------------------------
# Action
# ---------------------------------------------------------------------------

class WildfireAction(Action):
    """An action the dispatch agent can take."""
    action_type: ActionType = Field(..., description="Type of action to perform")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Action parameters (e.g. crew_id, fire_id, zone_id, message)",
    )


# ---------------------------------------------------------------------------
# Observation
# ---------------------------------------------------------------------------

class WildfireObservation(Observation):
    """Full observation returned to the agent."""
    fires: List[FireInfo] = Field(default_factory=list)
    crews: List[CrewInfo] = Field(default_factory=list)
    aircraft: List[AircraftInfo] = Field(default_factory=list)
    evacuation_zones: List[EvacZoneInfo] = Field(default_factory=list)
    weather: Optional[WeatherInfo] = None
    budget_remaining: float = Field(default=500000.0)
    budget_total: float = Field(default=500000.0)
    time_elapsed_hours: float = Field(default=0.0)
    communication_log: List[str] = Field(default_factory=list)
    available_actions: List[str] = Field(default_factory=list)
    hint: str = Field(default="")
    task_id: str = Field(default="")
    task_description: str = Field(default="")
    mutual_aid_eta_hours: Optional[float] = Field(default=None)
    situation_report: str = Field(default="")


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class WildfireState(State):
    """Full internal state."""
    task_id: str = ""
    fires: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    crews: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    aircraft: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    evac_zones: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    weather: Dict[str, Any] = Field(default_factory=dict)
    budget_remaining: float = 500000.0
    budget_total: float = 500000.0
    time_elapsed_hours: float = 0.0
    communications_sent: List[str] = Field(default_factory=list)
    evacuations_ordered: List[str] = Field(default_factory=list)
    mutual_aid_requested: bool = False
    mutual_aid_eta_hours: Optional[float] = None
    firebreaks_created: List[str] = Field(default_factory=list)
    backfires_set: List[str] = Field(default_factory=list)
    crews_rotated: List[str] = Field(default_factory=list)
    priorities_reassessed: List[str] = Field(default_factory=list)
    diagnostics_run: List[str] = Field(default_factory=list)
    resolved: bool = False
    penalties: float = 0.0
    dangerous_actions_taken: List[str] = Field(default_factory=list)
    max_steps: int = 20
    # Ground truth for grading
    correct_evacuations: List[str] = Field(default_factory=list)
    correct_crew_deployments: Dict[str, str] = Field(default_factory=dict)
    correct_aircraft_deployments: Dict[str, str] = Field(default_factory=dict)
    critical_actions: List[str] = Field(default_factory=list)
    dangerous_action_map: Dict[str, str] = Field(default_factory=dict)
