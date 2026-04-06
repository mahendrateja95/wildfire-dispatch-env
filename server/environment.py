"""Core environment logic for wildfire dispatch simulation."""

from __future__ import annotations

import copy
import uuid
from typing import Any, Dict, List, Optional, Tuple

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    ActionType,
    AircraftInfo,
    CrewInfo,
    EvacZoneInfo,
    FireInfo,
    WeatherInfo,
    WildfireAction,
    WildfireObservation,
    WildfireState,
)
from scenarios import ALL_SCENARIOS
from graders import GRADERS


class WildfireDispatchEnvironment:
    """Simulates wildfire resource dispatch decisions."""

    def __init__(self) -> None:
        self._state: Optional[WildfireState] = None
        self._scenario: Optional[Dict[str, Any]] = None
        self._diagnostic_info: Dict[str, str] = {}
        self._dangerous_action_map: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # OpenEnv API
    # ------------------------------------------------------------------

    def reset(self, seed: Optional[int] = None, task_id: str = "easy_single_fire", **kwargs) -> WildfireObservation:
        if task_id not in ALL_SCENARIOS:
            task_id = "easy_single_fire"

        self._scenario = copy.deepcopy(ALL_SCENARIOS[task_id])
        self._diagnostic_info = self._scenario.get("diagnostic_info", {})
        self._dangerous_action_map = self._scenario.get("dangerous_action_map", {})

        budget_start = self._scenario.get("budget_start", self._scenario.get("budget_total", 500000.0))

        self._state = WildfireState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            task_id=task_id,
            fires=copy.deepcopy(self._scenario["fires"]),
            crews=copy.deepcopy(self._scenario["crews"]),
            aircraft=copy.deepcopy(self._scenario["aircraft"]),
            evac_zones=copy.deepcopy(self._scenario["evac_zones"]),
            weather=copy.deepcopy(self._scenario["weather"]),
            budget_remaining=budget_start,
            budget_total=self._scenario.get("budget_total", 500000.0),
            max_steps=self._scenario.get("max_steps", 20),
            correct_evacuations=self._scenario.get("correct_evacuations", []),
            correct_crew_deployments=self._scenario.get("correct_crew_deployments", {}),
            correct_aircraft_deployments=self._scenario.get("correct_aircraft_deployments", {}),
            critical_actions=self._scenario.get("critical_actions", []),
            dangerous_action_map=self._scenario.get("dangerous_action_map", {}),
        )

        return self._build_observation(
            hint="Review the situation: active fires, available resources, weather forecast, and evacuation zones. Prioritize life safety."
        )

    def step(self, action: WildfireAction) -> Tuple[WildfireObservation, float, bool, Dict[str, Any]]:
        if self._state is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")

        self._state.step_count += 1
        self._state.time_elapsed_hours += 0.5  # Each step = 30 simulated minutes

        step_reward = 0.0
        hint = ""
        info: Dict[str, Any] = {}

        at = action.action_type
        params = action.parameters

        # ---- DEPLOY CREW ----
        if at == ActionType.DEPLOY_CREW:
            crew_id = params.get("crew_id", "")
            fire_id = params.get("fire_id", "")
            step_reward, hint, info = self._handle_deploy_crew(crew_id, fire_id)

        # ---- DEPLOY AIRCRAFT ----
        elif at == ActionType.DEPLOY_AIRCRAFT:
            aircraft_id = params.get("aircraft_id", "")
            fire_id = params.get("fire_id", "")
            step_reward, hint, info = self._handle_deploy_aircraft(aircraft_id, fire_id)

        # ---- CREATE FIREBREAK ----
        elif at == ActionType.CREATE_FIREBREAK:
            location = params.get("location", "")
            fire_id = params.get("fire_id", "")
            self._state.firebreaks_created.append(f"{location}_near_{fire_id}")
            self._state.budget_remaining -= 15000
            step_reward = 0.08
            hint = f"Firebreak created at {location} near {fire_id}."

        # ---- ORDER EVACUATION ----
        elif at == ActionType.ORDER_EVACUATION:
            zone_id = params.get("zone_id", "")
            step_reward, hint, info = self._handle_evacuation(zone_id)

        # ---- ROTATE CREW ----
        elif at == ActionType.ROTATE_CREW:
            crew_id = params.get("crew_id", "")
            step_reward, hint = self._handle_rotate_crew(crew_id)

        # ---- REQUEST MUTUAL AID ----
        elif at == ActionType.REQUEST_MUTUAL_AID:
            if not self._state.mutual_aid_requested:
                self._state.mutual_aid_requested = True
                self._state.mutual_aid_eta_hours = 4.0
                self._state.budget_remaining -= 50000
                step_reward = 0.08
                hint = "Mutual aid requested. 3 additional crews + 2 helicopters ETA 4-5 hours."
            else:
                step_reward = 0.0
                hint = "Mutual aid already requested."

        # ---- REASSESS PRIORITY ----
        elif at == ActionType.REASSESS_PRIORITY:
            fire_id = params.get("fire_id", "")
            new_priority = params.get("priority", 1)
            self._state.priorities_reassessed.append(fire_id)
            if fire_id in self._state.fires:
                self._state.fires[fire_id]["priority"] = new_priority

            # Check for dangerous prioritization
            if self._state.task_id == "hard_cascading_disaster":
                if fire_id == "fire_x" and new_priority == 1:
                    self._state.dangerous_actions_taken.append("prioritize_powerline_fire")
                    self._state.penalties += 0.05
                    step_reward = -0.05
                    hint = "WARNING: Prioritizing Powerline Fire over life-safety threats (school, hospital) is the wrong call. Power outages don't kill -- fires near schools do."
                elif fire_id == "fire_y" and new_priority == 1:
                    step_reward = 0.08
                    hint = "Correct: Hillside Fire is the top priority -- it threatens lives."
                else:
                    step_reward = 0.02
                    hint = f"Priority for {fire_id} set to {new_priority}."
            else:
                step_reward = 0.05
                hint = f"Priority for {fire_id} updated to {new_priority}."

        # ---- SET BACKFIRE ----
        elif at == ActionType.SET_BACKFIRE:
            location = params.get("location", "")
            fire_id = params.get("fire_id", "")
            self._state.backfires_set.append(f"{location}_{fire_id}")

            # Dangerous near hospital
            if self._state.task_id == "hard_cascading_disaster" and fire_id == "fire_y":
                loc_lower = location.lower()
                if "hospital" in loc_lower or "school" in loc_lower or "senior" in loc_lower:
                    self._state.dangerous_actions_taken.append("set_backfire_near_hospital")
                    self._state.penalties += 0.08
                    step_reward = -0.08
                    hint = "CRITICAL ERROR: Backfire near hospital/school creates smoke endangering patients and children!"
                else:
                    step_reward = 0.06
                    hint = f"Backfire set at {location}. Monitor closely."
            else:
                step_reward = 0.06
                hint = f"Backfire set at {location} for {fire_id}."
                self._state.budget_remaining -= 10000

        # ---- INVESTIGATE ----
        elif at == ActionType.INVESTIGATE:
            target = params.get("target", "")
            if target in self._diagnostic_info:
                result_text = self._diagnostic_info[target]
                self._state.diagnostics_run.append(target)
                info["diagnostic_output"] = result_text
                step_reward = 0.08
                hint = f"Investigation result: {result_text}"
            else:
                available = list(self._diagnostic_info.keys())
                step_reward = -0.01
                hint = f"Unknown investigation target '{target}'. Available: {', '.join(available)}"

        # ---- COMMUNICATE ----
        elif at == ActionType.COMMUNICATE:
            message = params.get("message", "")
            channel = params.get("channel", "dispatch")
            self._state.communications_sent.append(f"[{channel}] {message}")
            step_reward = 0.04
            hint = "Communication sent."

            # Check if pipeline communication (hard task)
            msg_lower = message.lower()
            if any(kw in msg_lower for kw in ["pipeline", "gas", "transco"]):
                step_reward = 0.10
                hint = "CRITICAL communication: Gas company alerted about pipeline threat."

        # ---- RESOLVE ----
        elif at == ActionType.RESOLVE:
            step_reward, hint = self._handle_resolve()

        # Accumulate reward (tracked for debugging)
        if not hasattr(self._state, "_reward_accumulated"):
            self._state._reward_accumulated = 0.0
        self._state._reward_accumulated += step_reward

        # Simulate fire growth each step
        self._simulate_fire_growth()

        # Check done
        done = False
        if self._state.resolved:
            done = True
        elif self._state.step_count >= self._state.max_steps:
            done = True
            hint = "Time limit reached. Situation auto-resolved for scoring."

        # Final grading
        final_score = 0.0
        if done:
            grader = GRADERS.get(self._state.task_id)
            if grader:
                state_dict = self._state.model_dump()
                final_score = grader(state_dict)
            info["final_score"] = final_score
            info["grader_task_id"] = self._state.task_id

        obs = self._build_observation(hint=hint, done=done)
        obs.reward = step_reward if not done else final_score

        return obs, obs.reward, done, info

    def state(self) -> WildfireState:
        if self._state is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        return self._state

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _handle_deploy_crew(self, crew_id: str, fire_id: str) -> Tuple[float, str, Dict]:
        info: Dict[str, Any] = {}
        if crew_id not in self._state.crews:
            return -0.01, f"Unknown crew '{crew_id}'. Available: {list(self._state.crews.keys())}", info
        if fire_id not in self._state.fires:
            return -0.01, f"Unknown fire '{fire_id}'. Active fires: {list(self._state.fires.keys())}", info

        crew = self._state.crews[crew_id]

        # Check fatigue -- dangerous action
        if crew.get("hours_on_duty", 0) >= 12 and crew.get("status") == "fatigued":
            dangerous_key = f"deploy_fatigued_{crew_id}"
            self._state.dangerous_actions_taken.append(dangerous_key)
            self._state.penalties += 0.06
            return -0.06, f"SAFETY VIOLATION: {crew['name']} has been on duty {crew['hours_on_duty']}h. Deploying fatigued crews risks injury. Rest them first.", info

        crew["assigned_to"] = fire_id
        crew["status"] = "deployed"
        crew["location"] = f"{self._state.fires[fire_id]['name']} front line"
        self._state.fires[fire_id]["crews_assigned"].append(crew_id)
        self._state.budget_remaining -= 20000

        # Check if correct deployment
        correct = self._scenario.get("correct_crew_deployments", {})
        if correct.get(crew_id) == fire_id:
            return 0.12, f"{crew['name']} deployed to {self._state.fires[fire_id]['name']}. Good deployment.", info
        else:
            return 0.04, f"{crew['name']} deployed to {self._state.fires[fire_id]['name']}.", info

    def _handle_deploy_aircraft(self, aircraft_id: str, fire_id: str) -> Tuple[float, str, Dict]:
        info: Dict[str, Any] = {}
        if aircraft_id not in self._state.aircraft:
            return -0.01, f"Unknown aircraft '{aircraft_id}'. Available: {list(self._state.aircraft.keys())}", info
        if fire_id not in self._state.fires:
            return -0.01, f"Unknown fire '{fire_id}'.", info

        ac = self._state.aircraft[aircraft_id]
        if ac.get("status") == "maintenance":
            return -0.01, f"{ac['name']} is in maintenance and not available yet.", info

        ac["assigned_to"] = fire_id
        ac["status"] = "deployed"
        self._state.fires[fire_id]["aircraft_assigned"].append(aircraft_id)
        self._state.budget_remaining -= 30000

        correct = self._scenario.get("correct_aircraft_deployments", {})
        if correct.get(aircraft_id) == fire_id:
            return 0.10, f"{ac['name']} deployed for water drops on {self._state.fires[fire_id]['name']}.", info
        else:
            return 0.03, f"{ac['name']} deployed to {self._state.fires[fire_id]['name']}.", info

    def _handle_evacuation(self, zone_id: str) -> Tuple[float, str, Dict]:
        info: Dict[str, Any] = {}
        if zone_id not in self._state.evac_zones:
            return -0.01, f"Unknown zone '{zone_id}'. Zones: {list(self._state.evac_zones.keys())}", info

        zone = self._state.evac_zones[zone_id]
        if zone.get("is_evacuated"):
            return 0.0, f"{zone['name']} already evacuated.", info

        zone["is_evacuated"] = True
        self._state.evacuations_ordered.append(zone_id)
        cost = zone.get("population", 0) * 100  # $100 per person evacuation cost
        self._state.budget_remaining -= cost

        correct = self._scenario.get("correct_evacuations", [])
        if zone_id in correct:
            pop = zone.get("population", 0)
            vuln = zone.get("has_vulnerable", False)
            reward = 0.15 if vuln else 0.10
            return reward, f"EVACUATION ORDERED: {zone['name']} ({pop} people). {'Vulnerable population -- critical evacuation.' if vuln else 'Residents being moved to safety.'}", info
        else:
            return 0.02, f"Evacuation ordered for {zone['name']}. (This zone was not in immediate danger.)", info

    def _handle_rotate_crew(self, crew_id: str) -> Tuple[float, str]:
        if crew_id not in self._state.crews:
            return -0.01, f"Unknown crew '{crew_id}'."

        crew = self._state.crews[crew_id]
        old_hours = crew.get("hours_on_duty", 0)
        old_status = crew.get("status", "")
        old_assignment = crew.get("assigned_to")

        # Remove from fire assignment
        if old_assignment and old_assignment in self._state.fires:
            fire = self._state.fires[old_assignment]
            if crew_id in fire["crews_assigned"]:
                fire["crews_assigned"].remove(crew_id)

        # Reset crew state
        crew["status"] = "available"
        crew["hours_on_duty"] = 0.0
        crew["assigned_to"] = None
        crew["location"] = "Rest area"
        self._state.crews_rotated.append(crew_id)

        # Reward based on pre-rotation fatigue
        if old_hours >= 10 or old_status == "fatigued":
            return 0.06, f"{crew['name']} rotated off duty for rest. Good safety practice."
        return 0.03, f"{crew['name']} rotated off duty."

    def _handle_resolve(self) -> Tuple[float, str]:
        # Check minimum conditions for resolution
        evacs = self._state.evacuations_ordered
        correct_evacs = self._scenario.get("correct_evacuations", [])
        comms = self._state.communications_sent

        missing_evacs = [e for e in correct_evacs if e not in evacs]
        if missing_evacs and len(correct_evacs) > 0:
            return -0.05, f"Cannot safely resolve -- {len(missing_evacs)} evacuation(s) still needed for life safety."

        self._state.resolved = True
        if len(comms) == 0:
            return 0.05, "Resolved, but you never communicated status to anyone."
        return 0.10, "Incident resolved. Resources being demobilized."

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    def _simulate_fire_growth(self) -> None:
        """Each step, fires grow based on rate, reduced by assigned resources.
        Also simulates weather changes based on forecast timeline."""
        # Dynamic weather: update conditions based on elapsed time
        self._update_weather()

        for fid, fire in self._state.fires.items():
            base_rate = fire.get("spread_rate_acres_per_hour", 10.0)
            # Resources slow fire: each crew reduces by 30%, each aircraft by 25%
            num_crews = len(fire.get("crews_assigned", []))
            num_aircraft = len(fire.get("aircraft_assigned", []))
            reduction = min(0.95, num_crews * 0.30 + num_aircraft * 0.25)
            effective_rate = base_rate * (1.0 - reduction)
            # Each step is 0.5 hours
            growth = effective_rate * 0.5
            fire["acres"] = fire.get("acres", 0) + growth
            # Containment increases with resources
            if num_crews > 0 or num_aircraft > 0:
                fire["containment_percent"] = min(
                    100.0,
                    fire.get("containment_percent", 0) + (num_crews * 3.0 + num_aircraft * 2.0),
                )
            # Update distance to evac zones
            for zid, zone in self._state.evac_zones.items():
                if zone.get("nearest_fire") == fid:
                    dist = zone.get("distance_to_nearest_fire_km", 10.0)
                    # Fire approaches: rough model
                    approach_km = (effective_rate * 0.5) * 0.01  # acres to rough km
                    zone["distance_to_nearest_fire_km"] = max(0.1, dist - approach_km)

    def _update_weather(self) -> None:
        """Simulate weather changes over time based on scenario forecasts."""
        hours = self._state.time_elapsed_hours
        weather = self._state.weather
        task = self._state.task_id

        if task == "medium_two_fires" and hours >= 4.0:
            # Wind shifts toward Oakdale after 4 hours
            weather["wind_direction"] = "W"
            weather["wind_speed_kmh"] = 30.0
            weather["temperature_celsius"] = 42.0
            weather["humidity_percent"] = 10.0
            weather["fire_danger_rating"] = "extreme"
            # Valley Fire accelerates toward town
            if "fire_valley" in self._state.fires:
                self._state.fires["fire_valley"]["spread_rate_acres_per_hour"] = 40.0

        elif task == "hard_cascading_disaster":
            if hours >= 2.0 and hours < 6.0:
                # First shift: NE wind pushes Hillside Fire faster toward school
                weather["wind_direction"] = "NE"
                weather["wind_speed_kmh"] = 35.0
                if "fire_y" in self._state.fires:
                    self._state.fires["fire_y"]["spread_rate_acres_per_hour"] = 45.0
            elif hours >= 6.0 and hours < 10.0:
                # Second shift: E wind
                weather["wind_direction"] = "E"
                weather["wind_speed_kmh"] = 25.0
            elif hours >= 10.0:
                # Third shift: SE wind pushes Creek Fire toward pipeline
                weather["wind_direction"] = "SE"
                weather["wind_speed_kmh"] = 30.0
                weather["humidity_percent"] = 5.0
                if "fire_z" in self._state.fires:
                    self._state.fires["fire_z"]["spread_rate_acres_per_hour"] = 20.0
                    self._state.fires["fire_z"]["spread_direction"] = "SE"

    # ------------------------------------------------------------------
    # Observation builder
    # ------------------------------------------------------------------

    def _build_observation(self, hint: str = "", done: bool = False) -> WildfireObservation:
        fires = [FireInfo(**f) for f in self._state.fires.values()]
        crews = [CrewInfo(**c) for c in self._state.crews.values()]
        aircraft_list = [AircraftInfo(**a) for a in self._state.aircraft.values()]
        evac_zones = [EvacZoneInfo(**z) for z in self._state.evac_zones.values()]
        weather = WeatherInfo(**self._state.weather) if self._state.weather else None

        # Build situation report
        sitrep_parts = []
        for f in fires:
            sitrep_parts.append(
                f"[FIRE] {f.name}: {f.acres:.0f} acres, {f.containment_percent:.0f}% contained, "
                f"spreading {f.spread_direction} at {f.spread_rate_acres_per_hour} ac/hr. "
                f"Threats: {', '.join(f.threats)}"
            )

        available_actions = [
            "deploy_crew(crew_id='<id>', fire_id='<id>')",
            "deploy_aircraft(aircraft_id='<id>', fire_id='<id>')",
            "create_firebreak(location='<desc>', fire_id='<id>')",
            "order_evacuation(zone_id='<id>')",
            "rotate_crew(crew_id='<id>')",
            "request_mutual_aid()",
            "reassess_priority(fire_id='<id>', priority=1-5)",
            "set_backfire(location='<desc>', fire_id='<id>')",
            f"investigate(target=<one of: {', '.join(self._diagnostic_info.keys())}>)" if self._diagnostic_info else "investigate(target='<topic>')",
            "communicate(message='<msg>', channel='<channel>')",
            "resolve()",
        ]

        # Add investigation hint early in episode
        if self._state.step_count <= 2 and self._diagnostic_info:
            hint += f"\n\nTIP: Use investigate(target='<topic>') to gather information before acting. "
            hint += f"Available topics: {', '.join(self._diagnostic_info.keys())}"

        return WildfireObservation(
            done=done,
            reward=None,
            fires=fires,
            crews=crews,
            aircraft=aircraft_list,
            evacuation_zones=evac_zones,
            weather=weather,
            budget_remaining=self._state.budget_remaining,
            budget_total=self._state.budget_total,
            time_elapsed_hours=self._state.time_elapsed_hours,
            communication_log=self._state.communications_sent,
            available_actions=available_actions,
            hint=hint,
            task_id=self._state.task_id,
            task_description=self._scenario.get("task_description", ""),
            mutual_aid_eta_hours=self._state.mutual_aid_eta_hours,
            situation_report="\n".join(sitrep_parts),
        )
