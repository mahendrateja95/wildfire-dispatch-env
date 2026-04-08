"""
Wildfire Dispatch Environment -- Demo Script
=============================================

Quick demo that runs all 3 tasks against the environment using a deterministic
scripted "smart" agent. NO API key required.

This is the fastest way for a judge or first-time user to verify the
environment works end-to-end and produces meaningful scores.

Usage:
    # Against a local server (start with `python -m server.app` first):
    python demo.py

    # Against the live HF Space:
    ENV_URL=https://mahendra95-wildfire-dispatch-env.hf.space python demo.py

What it does:
    1. Connects to the environment via the OpenEnv WildfireDispatchEnv client
    2. Runs each of the 3 tasks (easy / medium / hard) using a hand-crafted
       optimal action sequence per task
    3. Prints per-step rewards and final grader score for each task
    4. Prints a summary table at the end

Expected output: All 3 tasks should score above 0.7 with the optimal sequences.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List

from client import WildfireDispatchEnv
from models import WildfireAction


ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")


# Hand-crafted "optimal" action sequences -- demonstrate what success looks like.
SCRIPTED_RUNS: Dict[str, List[Dict[str, Any]]] = {
    "easy_single_fire": [
        {"action_type": "deploy_crew",     "parameters": {"crew_id": "crew_alpha", "fire_id": "fire_cedar"}},
        {"action_type": "deploy_crew",     "parameters": {"crew_id": "crew_bravo", "fire_id": "fire_cedar"}},
        {"action_type": "deploy_aircraft", "parameters": {"aircraft_id": "heli_1", "fire_id": "fire_cedar"}},
        {"action_type": "create_firebreak","parameters": {"location": "highway_89", "fire_id": "fire_cedar"}},
        {"action_type": "communicate",     "parameters": {"message": "Cedar fire crews on scene, highway 89 firebreak in progress", "channel": "dispatch"}},
        {"action_type": "resolve",         "parameters": {}},
    ],
    "medium_two_fires": [
        {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_oakdale"}},
        {"action_type": "reassess_priority","parameters": {"fire_id": "fire_valley", "priority": 1}},
        {"action_type": "deploy_crew",      "parameters": {"crew_id": "crew_echo", "fire_id": "fire_valley"}},
        {"action_type": "deploy_aircraft",  "parameters": {"aircraft_id": "heli_2", "fire_id": "fire_valley"}},
        {"action_type": "request_mutual_aid","parameters": {}},
        {"action_type": "rotate_crew",      "parameters": {"crew_id": "crew_delta"}},
        {"action_type": "communicate",      "parameters": {"message": "Valley Fire priority 1, Oakdale evacuation under way", "channel": "dispatch"}},
        {"action_type": "communicate",      "parameters": {"message": "Mutual aid requested, Crew Delta rotated for rest", "channel": "command"}},
        {"action_type": "resolve",          "parameters": {}},
    ],
    "hard_cascading_disaster": [
        {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_school"}},
        {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_hospital"}},
        {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_senior"}},
        {"action_type": "investigate",      "parameters": {"target": "weather_forecast"}},
        {"action_type": "investigate",      "parameters": {"target": "check_creek_fire_detail"}},
        {"action_type": "deploy_crew",      "parameters": {"crew_id": "crew_foxtrot", "fire_id": "fire_y"}},
        {"action_type": "deploy_aircraft",  "parameters": {"aircraft_id": "heli_3", "fire_id": "fire_y"}},
        {"action_type": "communicate",      "parameters": {"message": "URGENT: TransCo gas pipeline threatened by Creek Fire, T+10hr wind shift will accelerate", "channel": "emergency"}},
        {"action_type": "request_mutual_aid","parameters": {}},
        {"action_type": "communicate",      "parameters": {"message": "School, hospital, senior living evacuated. Pipeline risk reported.", "channel": "dispatch"}},
        {"action_type": "communicate",      "parameters": {"message": "All Hillside resources committed, mutual aid en route", "channel": "command"}},
        {"action_type": "resolve",          "parameters": {}},
    ],
}


async def run_demo_task(env: WildfireDispatchEnv, task_id: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    print(f"\n{'='*60}")
    print(f"  TASK: {task_id}")
    print(f"{'='*60}")

    result = await env.reset(task_id=task_id)
    obs = result.observation
    print(f"  Reset OK: {len(getattr(obs, 'fires', []))} active fires, "
          f"{len(getattr(obs, 'evacuation_zones', []))} evacuation zones")

    rewards: List[float] = []
    final_score = 0.0
    for i, action_dict in enumerate(actions, start=1):
        action = WildfireAction(
            action_type=action_dict["action_type"],
            parameters=action_dict["parameters"],
        )
        step_result = await env.step(action)
        reward = step_result.reward or 0.0
        done = bool(step_result.done)
        rewards.append(reward)

        action_summary = action_dict["action_type"]
        params = action_dict["parameters"]
        if params:
            short_params = ",".join(f"{k}={v}" for k, v in list(params.items())[:2])
            action_summary = f"{action_summary}({short_params})"
        print(f"  step {i:2d} | {action_summary:55s} | reward={reward:+.3f} done={done}")

        if done:
            final_score = reward  # Environment sets obs.reward = grader's final_score on terminal step
            break

    return {
        "task_id": task_id,
        "steps": len(rewards),
        "final_score": final_score,
        "rewards": rewards,
    }


async def main() -> None:
    print(f"Wildfire Dispatch Environment -- Demo")
    print(f"Connecting to: {ENV_URL}")

    env = WildfireDispatchEnv(base_url=ENV_URL)
    await env.connect()

    results = []
    try:
        for task_id, actions in SCRIPTED_RUNS.items():
            result = await run_demo_task(env, task_id, actions)
            results.append(result)
    finally:
        await env.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Task':35s} {'Steps':>6s} {'Score':>8s}")
    print(f"  {'-'*35} {'-'*6} {'-'*8}")
    for r in results:
        print(f"  {r['task_id']:35s} {r['steps']:>6d} {r['final_score']:>8.3f}")
    if results:
        avg = sum(r["final_score"] for r in results) / len(results)
        print(f"  {'-'*35} {'-'*6} {'-'*8}")
        print(f"  {'Average':35s} {'':>6s} {avg:>8.3f}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
