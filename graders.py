"""Deterministic graders for each wildfire task -- scores 0.0 to 1.0."""

from __future__ import annotations

from typing import Any, Dict, List


def _set_overlap(actual: List[str], expected: List[str]) -> float:
    """Fraction of expected items present in actual (case-insensitive)."""
    if not expected:
        return 1.0
    actual_s = {s.lower().strip() for s in actual}
    expected_s = {s.lower().strip() for s in expected}
    return len(actual_s & expected_s) / len(expected_s)


def _check_actions(done_actions: List[str], critical: List[str]) -> float:
    """What fraction of critical actions were completed?"""
    return _set_overlap(done_actions, critical)


# ======================================================================
# EASY GRADER
# ======================================================================

def grade_easy(state: Dict[str, Any]) -> float:
    """
    Easy task: Single fire containment.

    Breakdown (1.0 total):
      - Deployed crew to fire:        0.25
      - Deployed aircraft to fire:    0.20
      - Created firebreak:            0.20
      - Communication sent:           0.10
      - Resolved:                     0.15
      - Efficiency (fewer steps):     0.10
    """
    score = 0.0

    # Crew deployment (0.25)
    crews = state.get("crews", {})
    crew_on_cedar = sum(
        1 for c in crews.values()
        if c.get("assigned_to") == "fire_cedar"
    )
    if crew_on_cedar >= 2:
        score += 0.25
    elif crew_on_cedar >= 1:
        score += 0.15

    # Aircraft deployment (0.20)
    aircraft = state.get("aircraft", {})
    air_on_cedar = sum(
        1 for a in aircraft.values()
        if a.get("assigned_to") == "fire_cedar"
    )
    if air_on_cedar >= 1:
        score += 0.20

    # Firebreak (0.20)
    firebreaks = state.get("firebreaks_created", [])
    if any("cedar" in fb.lower() or "highway" in fb.lower() for fb in firebreaks):
        score += 0.20
    elif len(firebreaks) > 0:
        score += 0.10

    # Communication (0.10)
    comms = state.get("communications_sent", [])
    if len(comms) >= 1:
        score += 0.10

    # Resolved (0.15)
    if state.get("resolved", False):
        score += 0.15

    # Efficiency (0.10)
    steps = state.get("step_count", 0)
    max_steps = state.get("max_steps", 12)
    if steps > 0:
        efficiency = max(0, 1.0 - (steps / max_steps))
        score += 0.10 * efficiency

    score -= state.get("penalties", 0.0)
    return round(min(1.0, max(0.0, score)), 4)


# ======================================================================
# MEDIUM GRADER
# ======================================================================

def grade_medium(state: Dict[str, Any]) -> float:
    """
    Medium task: Two fires, limited resources.

    Breakdown (1.0 total):
      - Prioritized Valley Fire:     0.10
      - Evacuated Oakdale:           0.25
      - Deployed crew to Valley:     0.15
      - Deployed aircraft to Valley: 0.10
      - Requested mutual aid:        0.10
      - Rotated fatigued crew:       0.05
      - Communication:               0.10
      - Resolved:                    0.10
      - Efficiency:                  0.05
    """
    score = 0.0

    # Priority reassessment (0.10)
    priorities = state.get("priorities_reassessed", [])
    if any("valley" in p.lower() or "fire_valley" in p.lower() for p in priorities):
        score += 0.10
    elif len(priorities) > 0:
        score += 0.03

    # Evacuation of Oakdale (0.25) -- most important
    evacuations = state.get("evacuations_ordered", [])
    if any("oakdale" in e.lower() or "zone_oakdale" in e.lower() for e in evacuations):
        score += 0.25

    # Crew deployment to Valley Fire (0.15)
    crews = state.get("crews", {})
    crew_on_valley = sum(
        1 for c in crews.values()
        if c.get("assigned_to") == "fire_valley"
    )
    if crew_on_valley >= 1:
        score += 0.15

    # Aircraft to Valley Fire (0.10)
    aircraft = state.get("aircraft", {})
    air_on_valley = sum(
        1 for a in aircraft.values()
        if a.get("assigned_to") == "fire_valley"
    )
    if air_on_valley >= 1:
        score += 0.10

    # Mutual aid (0.10)
    if state.get("mutual_aid_requested", False):
        score += 0.10

    # Crew rotation (0.05)
    rotations = state.get("crews_rotated", [])
    if any("delta" in r.lower() for r in rotations):
        score += 0.05

    # Communication (0.10)
    comms = state.get("communications_sent", [])
    if len(comms) >= 2:
        score += 0.10
    elif len(comms) >= 1:
        score += 0.05

    # Resolved (0.10)
    if state.get("resolved", False):
        score += 0.10

    # Efficiency (0.05)
    steps = state.get("step_count", 0)
    max_steps = state.get("max_steps", 16)
    if steps > 0:
        efficiency = max(0, 1.0 - (steps / max_steps))
        score += 0.05 * efficiency

    # Penalties
    score -= state.get("penalties", 0.0)
    return round(min(1.0, max(0.0, score)), 4)


# ======================================================================
# HARD GRADER
# ======================================================================

def grade_hard(state: Dict[str, Any]) -> float:
    """
    Hard task: Cascading disaster with red herrings.

    Breakdown (1.0 total):
      - Evacuated school:            0.15
      - Evacuated hospital:          0.12
      - Evacuated senior living:     0.08
      - Deployed crew to Hillside:   0.08
      - Deployed aircraft to Hillside: 0.05
      - Discovered pipeline threat:  0.12
      - Communicated pipeline risk:  0.08
      - Requested mutual aid:        0.05
      - Avoided dangerous actions:   0.10
      - Ignored political pressure:  0.05
      - Communication:               0.05
      - Resolved:                    0.05
      - Efficiency:                  0.02
    """
    score = 0.0

    evacuations = [e.lower() for e in state.get("evacuations_ordered", [])]

    # Evacuate school (0.15)
    if any("school" in e or "zone_school" in e for e in evacuations):
        score += 0.15

    # Evacuate hospital (0.12)
    if any("hospital" in e or "zone_hospital" in e for e in evacuations):
        score += 0.12

    # Evacuate senior living (0.08)
    if any("senior" in e or "zone_senior" in e for e in evacuations):
        score += 0.08

    # Crew deployment to Hillside/Fire Y (0.08)
    crews = state.get("crews", {})
    crew_on_hillside = sum(
        1 for c in crews.values()
        if c.get("assigned_to") == "fire_y"
    )
    if crew_on_hillside >= 1:
        score += 0.08

    # Aircraft to Hillside (0.05)
    aircraft = state.get("aircraft", {})
    air_on_hillside = sum(
        1 for a in aircraft.values()
        if a.get("assigned_to") == "fire_y"
    )
    if air_on_hillside >= 1:
        score += 0.05

    # Pipeline threat discovery (0.12) -- checked diagnostic about creek fire or pipeline
    diagnostics = [d.lower() for d in state.get("diagnostics_run", [])]
    if any("creek" in d or "pipeline" in d for d in diagnostics):
        score += 0.12

    # Communicated pipeline risk (0.08)
    comms_lower = [c.lower() for c in state.get("communications_sent", [])]
    if any("pipeline" in c or "gas" in c or "transco" in c for c in comms_lower):
        score += 0.08

    # Mutual aid (0.05)
    if state.get("mutual_aid_requested", False):
        score += 0.05

    # Avoided dangerous actions (0.10)
    dangerous = state.get("dangerous_actions_taken", [])
    if len(dangerous) == 0:
        score += 0.10
    else:
        score += max(0, 0.10 - len(dangerous) * 0.03)

    # Ignored political pressure -- did NOT prioritize Powerline Fire (0.05)
    priorities = [p.lower() for p in state.get("priorities_reassessed", [])]
    powerline_prioritized = any(
        "powerline" in p or "fire_x" in p
        for p in priorities
    )
    if not powerline_prioritized:
        score += 0.05
    # Extra: if they explicitly deprioritized it, bonus already captured

    # Communication (0.05)
    comms = state.get("communications_sent", [])
    if len(comms) >= 3:
        score += 0.05
    elif len(comms) >= 2:
        score += 0.03
    elif len(comms) >= 1:
        score += 0.01

    # Resolved (0.05)
    if state.get("resolved", False):
        score += 0.05

    # Efficiency (0.02)
    steps = state.get("step_count", 0)
    max_steps = state.get("max_steps", 20)
    if steps > 0:
        efficiency = max(0, 1.0 - (steps / max_steps))
        score += 0.02 * efficiency

    score -= state.get("penalties", 0.0)
    return round(min(1.0, max(0.0, score)), 4)


GRADERS = {
    "easy_single_fire": grade_easy,
    "medium_two_fires": grade_medium,
    "hard_cascading_disaster": grade_hard,
}
