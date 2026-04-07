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


# ------------------------------------------------------------------
# Shared bonus helpers
# ------------------------------------------------------------------

def _timing_bonus(state: Dict[str, Any], zone_keyword: str, max_step: int, bonus: float) -> float:
    """Award a bonus if an evacuation matching zone_keyword happened at or before max_step."""
    action_history = state.get("action_history", [])
    for entry in action_history:
        if entry.get("action_type") == "order_evacuation":
            zone_id = entry.get("params", {}).get("zone_id", "")
            if zone_keyword in zone_id.lower():
                if entry.get("step", 999) <= max_step:
                    return bonus
    return 0.0


def _evacuation_before_crew_bonus(state: Dict[str, Any], bonus: float = 0.02) -> float:
    """Award bonus if ANY evacuation was ordered BEFORE any crew deployment (life safety first)."""
    action_history = state.get("action_history", [])
    first_evac_step = None
    first_crew_step = None
    for entry in action_history:
        atype = entry.get("action_type", "")
        step = entry.get("step", 999)
        if atype == "order_evacuation" and first_evac_step is None:
            first_evac_step = step
        if atype == "deploy_crew" and first_crew_step is None:
            first_crew_step = step
    # Bonus if evacuation came first (or if no crew was deployed at all)
    if first_evac_step is not None:
        if first_crew_step is None or first_evac_step < first_crew_step:
            return bonus
    return 0.0


def _budget_efficiency_bonus(state: Dict[str, Any]) -> float:
    """Score based on budget efficiency at resolution."""
    budget_remaining = state.get("budget_remaining", 0)
    budget_total = state.get("budget_total", 1)
    if budget_total <= 0:
        return 0.0
    ratio = budget_remaining / budget_total
    if ratio > 0.50:
        return 0.02  # Didn't overspend
    elif ratio < 0.10:
        return -0.02  # Wasteful
    return 0.0


def _communication_quality(state: Dict[str, Any], keywords: List[str]) -> float:
    """Score communications based on keyword relevance (0.0 to 0.05 bonus)."""
    comms = state.get("communications_sent", [])
    if not comms:
        return 0.0
    comms_text = " ".join(c.lower() for c in comms)
    matched = sum(1 for kw in keywords if kw in comms_text)
    if matched == 0:
        return 0.0
    # Proportional bonus up to 0.05 based on keyword coverage
    coverage = matched / len(keywords)
    return round(0.05 * coverage, 4)


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
      - Bonuses (comm quality, budget): up to ~0.07
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

    # --- ENHANCED BONUSES ---

    # Communication quality: reward mentioning relevant keywords
    score += _communication_quality(state, ["cedar", "highway", "fire"])

    # Budget efficiency
    score += _budget_efficiency_bonus(state)

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
      - Bonuses (timing, ordering, comm quality, budget): up to ~0.12
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

    # --- ENHANCED BONUSES ---

    # Timing: Oakdale evacuation in first 4 steps
    score += _timing_bonus(state, "oakdale", max_step=4, bonus=0.03)

    # Action ordering: evacuation before crew deployment (life safety first)
    score += _evacuation_before_crew_bonus(state, bonus=0.02)

    # Communication quality: reward mentioning relevant keywords
    score += _communication_quality(state, ["valley", "oakdale", "evacuation"])

    # Budget efficiency
    score += _budget_efficiency_bonus(state)

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
      - Bonuses (timing, ordering, investigation, comm quality, budget): up to ~0.16
    """
    score = 0.0

    evacuations = [e.lower() for e in state.get("evacuations_ordered", [])]

    # Evacuate school (0.15) -- TIME CRITICAL
    # Children at Maplewood Elementary need to clear the building before
    # the wind shift at T+2hr. School evacuation by step 4 = full credit;
    # delayed evacuation = partial credit only.
    if any("school" in e or "zone_school" in e for e in evacuations):
        # Check timing via action history
        history = state.get("action_history", [])
        school_evac_step = None
        for entry in history:
            if entry.get("action_type") == "order_evacuation":
                params = entry.get("params", {})
                if "school" in str(params.get("zone_id", "")).lower():
                    school_evac_step = entry.get("step", 99)
                    break
        if school_evac_step is None or school_evac_step <= 4:
            score += 0.15  # On time
        elif school_evac_step <= 8:
            score += 0.08  # Late but evacuated
        else:
            score += 0.04  # Very late -- children at risk during wind shift

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

    # Pipeline threat discovery (0.12) -- requires multi-step investigation:
    # Must check BOTH weather_forecast (timing) AND creek_fire_detail (target).
    # Frontier models often skip the prerequisite reasoning step.
    diagnostics = [d.lower() for d in state.get("diagnostics_run", [])]
    has_weather = any("weather_forecast" in d for d in diagnostics)
    has_creek = any("creek" in d for d in diagnostics)
    has_pipeline = any("pipeline" in d for d in diagnostics)
    if has_weather and (has_creek or has_pipeline):
        score += 0.12  # Full credit -- complete pipeline threat picture
    elif has_creek or has_pipeline:
        score += 0.06  # Partial -- found target but missed timing context
    elif len(diagnostics) > 0:
        score += 0.02  # Minimal -- investigated something

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

    # --- ENHANCED BONUSES ---

    # Timing: school evacuation in first 5 steps
    score += _timing_bonus(state, "school", max_step=5, bonus=0.03)

    # Action ordering: evacuation before crew deployment (life safety first)
    score += _evacuation_before_crew_bonus(state, bonus=0.02)

    # Communication quality: reward mentioning relevant keywords
    score += _communication_quality(state, ["pipeline", "school", "hospital"])

    # Budget efficiency
    score += _budget_efficiency_bonus(state)

    # Wasteful action penalty: count duplicate evacuation orders from history.
    # Real dispatchers don't repeatedly order the same evacuation -- it wastes
    # radio bandwidth and dispatch attention during critical operations.
    history = state.get("action_history", [])
    seen_evacs = set()
    duplicates = 0
    for entry in history:
        if entry.get("action_type") == "order_evacuation":
            zid = str(entry.get("params", {}).get("zone_id", ""))
            if zid in seen_evacs:
                duplicates += 1
            seen_evacs.add(zid)
    score -= min(0.10, duplicates * 0.02)

    score -= state.get("penalties", 0.0)
    return round(min(1.0, max(0.0, score)), 4)


GRADERS = {
    "easy_single_fire": grade_easy,
    "medium_two_fires": grade_medium,
    "hard_cascading_disaster": grade_hard,
}
