"""
Inference Script -- Wildfire Dispatch Environment
===================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL       The API endpoint for the LLM.
    MODEL_NAME         The model identifier to use for inference.
    HF_TOKEN           Your Hugging Face / API key.
    LOCAL_IMAGE_NAME   The name of the local image to use for the environment if you are using from_docker_image()

- Defaults are set only for API_BASE_URL and MODEL_NAME:
    API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")

STDOUT FORMAT
- The script must emit exactly three line types to stdout, in this order:

    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import asyncio
import json
import os
import sys
import textwrap
from typing import Any, Dict, List, Optional

from openai import OpenAI

from client import WildfireDispatchEnv
from models import WildfireAction

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME") or os.getenv("IMAGE_NAME")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
ENV_URL = os.getenv("ENV_URL") or "http://localhost:8000"

BENCHMARK = "wildfire_dispatch"
TEMPERATURE = 0.1
MAX_TOKENS = 512
SUCCESS_SCORE_THRESHOLD = 0.3

TASKS = [
    {"task_id": "easy_single_fire", "task_name": "single-fire-containment", "max_steps": 12},
    {"task_id": "medium_two_fires", "task_name": "two-fires-resource-allocation", "max_steps": 16},
    {"task_id": "hard_cascading_disaster", "task_name": "cascading-wildfire-disaster", "max_steps": 20},
]

# ---------------------------------------------------------------------------
# Structured Logging -- EXACT FORMAT REQUIRED
# ---------------------------------------------------------------------------


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# OpenAI LLM Client
# ---------------------------------------------------------------------------

_openai_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    return _openai_client


SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert Wildfire Dispatch Coordinator managing active wildfires.
    You receive situation reports with active fires, crews, aircraft, evacuation zones, and weather.
    Your priority order: 1) Human life  2) Crew safety  3) Property  4) Environment

    You must respond with EXACTLY ONE JSON action object per turn. No explanation, no markdown.

    Available actions:
    {"action_type": "deploy_crew", "parameters": {"crew_id": "<id>", "fire_id": "<id>"}}
    {"action_type": "deploy_aircraft", "parameters": {"aircraft_id": "<id>", "fire_id": "<id>"}}
    {"action_type": "create_firebreak", "parameters": {"location": "<desc>", "fire_id": "<id>"}}
    {"action_type": "order_evacuation", "parameters": {"zone_id": "<id>"}}
    {"action_type": "rotate_crew", "parameters": {"crew_id": "<id>"}}
    {"action_type": "request_mutual_aid", "parameters": {}}
    {"action_type": "reassess_priority", "parameters": {"fire_id": "<id>", "priority": 1}}
    {"action_type": "set_backfire", "parameters": {"location": "<desc>", "fire_id": "<id>"}}
    {"action_type": "investigate", "parameters": {"target": "<topic>"}}
    {"action_type": "communicate", "parameters": {"message": "<msg>", "channel": "<channel>"}}
    {"action_type": "resolve", "parameters": {}}

    RULES:
    - NEVER deploy fatigued crews (12+ hours) -- rotate them first
    - ALWAYS evacuate zones with schools/hospitals BEFORE fire reaches them
    - Prioritize LIVES over property or political pressure
    - Use investigate() to check small remote fires for hidden threats (pipelines, fuel stations)
    - Communicate status regularly and alert relevant agencies about discovered threats

    Respond with ONLY the JSON. No other text.
""").strip()


# ---------------------------------------------------------------------------
# Observation -> Text (for LLM context)
# ---------------------------------------------------------------------------


def _obs_to_dict(obs: Any) -> Dict[str, Any]:
    if hasattr(obs, "model_dump"):
        return obs.model_dump()
    if isinstance(obs, dict):
        return obs
    return {}


def observation_to_text(obs: Any) -> str:
    data = _obs_to_dict(obs)
    lines = []

    lines.append("=" * 50)
    lines.append("WILDFIRE DISPATCH -- SITUATION REPORT")
    lines.append("=" * 50)
    lines.append(f"Task: {data.get('task_id', '?')}")
    lines.append(f"Objective: {data.get('task_description', '')}")
    lines.append(f"Time: {data.get('time_elapsed_hours', 0):.1f}h elapsed")
    lines.append(f"Budget: ${data.get('budget_remaining', 0):,.0f} / ${data.get('budget_total', 0):,.0f}")

    if data.get("mutual_aid_eta_hours"):
        lines.append(f"Mutual aid ETA: {data['mutual_aid_eta_hours']:.1f}h")

    w = data.get("weather")
    if w:
        lines.append(f"\n--- WEATHER ---")
        lines.append(f"Wind: {w.get('wind_speed_kmh', 0)}km/h from {w.get('wind_direction', '?')}")
        lines.append(f"Temp: {w.get('temperature_celsius', 0)}C | Humidity: {w.get('humidity_percent', 0)}%")
        lines.append(f"Danger: {w.get('fire_danger_rating', '?')}")
        lines.append(f"Forecast: {w.get('forecast_change', 'stable')}")

    lines.append(f"\n--- FIRES ---")
    for fire in data.get("fires", []):
        lines.append(f"  {fire.get('name', '?')} [{fire.get('fire_id', '?')}]: "
                      f"{fire.get('acres', 0):.0f}ac, {fire.get('containment_percent', 0):.0f}% contained, "
                      f"spreading {fire.get('spread_direction', '?')} @ {fire.get('spread_rate_acres_per_hour', 0)}ac/hr, "
                      f"priority={fire.get('priority', '?')}")
        lines.append(f"    Threats: {', '.join(fire.get('threats', []))}")
        lines.append(f"    Crews: {fire.get('crews_assigned', [])} Aircraft: {fire.get('aircraft_assigned', [])}")

    lines.append(f"\n--- CREWS ---")
    for crew in data.get("crews", []):
        warn = " **FATIGUED**" if crew.get("status") == "fatigued" else ""
        lines.append(f"  {crew.get('name', '?')} [{crew.get('crew_id', '?')}]: "
                      f"{crew.get('status', '?')}{warn}, {crew.get('hours_on_duty', 0):.0f}h duty, "
                      f"at {crew.get('location', '?')}, type={crew.get('specialty', '?')}")

    lines.append(f"\n--- AIRCRAFT ---")
    for ac in data.get("aircraft", []):
        lines.append(f"  {ac.get('name', '?')} [{ac.get('aircraft_id', '?')}]: "
                      f"{ac.get('aircraft_type', '?')}, {ac.get('status', '?')}, "
                      f"{ac.get('water_capacity_gallons', 0)}gal")

    lines.append(f"\n--- EVACUATION ZONES ---")
    for zone in data.get("evacuation_zones", []):
        status = "EVACUATED" if zone.get("is_evacuated") else "NOT EVACUATED"
        vuln = " [VULNERABLE]" if zone.get("has_vulnerable") else ""
        lines.append(f"  {zone.get('name', '?')} [{zone.get('zone_id', '?')}]: "
                      f"{zone.get('population', 0)} people, "
                      f"{zone.get('distance_to_nearest_fire_km', 0):.1f}km from {zone.get('nearest_fire', '?')}, "
                      f"{status}{vuln}")
        if zone.get("description"):
            lines.append(f"    {zone['description']}")

    if data.get("communication_log"):
        lines.append(f"\n--- COMMS ---")
        for msg in data["communication_log"][-5:]:
            lines.append(f"  {msg}")

    lines.append(f"\n--- ACTIONS ---")
    for act in data.get("available_actions", []):
        lines.append(f"  {act}")

    if data.get("hint"):
        lines.append(f"\nHINT: {data['hint']}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Action formatting / parsing
# ---------------------------------------------------------------------------


def format_action_str(action: Dict[str, Any]) -> str:
    at = action.get("action_type", "unknown")
    params = action.get("parameters", {})
    if params:
        param_str = ",".join(f"{k}={v!r}" for k, v in params.items())
        return f"{at}({param_str})"
    return f"{at}()"


def parse_action(llm_response: str) -> Dict[str, Any]:
    text = llm_response.strip()

    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    continue

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return {"action_type": "resolve", "parameters": {}}


# ---------------------------------------------------------------------------
# LLM Decision Making
# ---------------------------------------------------------------------------


def get_model_action(
    step: int,
    obs_text: str,
    last_reward: float,
    history: List[str],
) -> str:
    history_block = "\n".join(history[-6:]) if history else "None"
    user_prompt = textwrap.dedent(f"""
        Step: {step}
        Last reward: {last_reward:.2f}
        Previous actions:
        {history_block}

        Current situation:
        {obs_text}

        Respond with ONE JSON action object.
    """).strip()

    try:
        completion = get_client().chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else '{"action_type": "resolve", "parameters": {}}'
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return '{"action_type": "resolve", "parameters": {}}'


# ---------------------------------------------------------------------------
# Run One Task
# ---------------------------------------------------------------------------


async def run_task(env: WildfireDispatchEnv, task_config: Dict[str, Any]) -> Dict[str, Any]:
    task_id = task_config["task_id"]
    task_name = task_config["task_name"]
    max_steps = task_config["max_steps"]

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(task_id=task_id)
        obs = result.observation
        obs_text = observation_to_text(obs)
        last_reward = 0.0
        done = bool(result.done)

        for step in range(1, max_steps + 1):
            if done:
                break

            llm_response = get_model_action(step, obs_text, last_reward, history)
            action_dict = parse_action(llm_response)
            action_str = format_action_str(action_dict)

            error = None
            try:
                wf_action = WildfireAction(
                    action_type=action_dict.get("action_type", "resolve"),
                    parameters=action_dict.get("parameters", {}) or {},
                )
                step_result = await env.step(wf_action)
            except Exception as e:
                error = str(e)
                log_step(step=step, action=action_str, reward=0.0, done=False, error=error)
                rewards.append(0.0)
                steps_taken = step
                history.append(f"Step {step}: {action_str} -> ERROR: {error}")
                continue

            obs = step_result.observation
            reward = step_result.reward or 0.0
            done = bool(step_result.done)

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            log_step(step=step, action=action_str, reward=reward, done=done, error=error)

            history.append(f"Step {step}: {action_str} -> reward {reward:+.2f}")
            obs_text = observation_to_text(obs)

            if done:
                # Environment sets obs.reward = final_score on terminal step
                info = _obs_to_dict(obs).get("metadata", {}) or {}
                if "final_score" in info:
                    score = info["final_score"]
                else:
                    score = reward  # Last reward is the grader's final_score
                break

        if score == 0.0 and rewards and not done:
            # Fallback only if episode never finished
            score = max(0.0, sum(rewards) / max(1, len(rewards)))
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Task {task_id} error: {exc}", flush=True)

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return {
        "task_id": task_id,
        "task_name": task_name,
        "score": score,
        "steps": steps_taken,
        "success": success,
        "rewards": rewards,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    if IMAGE_NAME:
        env = await WildfireDispatchEnv.from_docker_image(IMAGE_NAME)
    else:
        env = WildfireDispatchEnv(base_url=ENV_URL)
        await env.connect()

    results = []
    try:
        for task_config in TASKS:
            result = await run_task(env, task_config)
            results.append(result)
    finally:
        await env.close()

    print("\n=== SUMMARY ===", file=sys.stderr)
    for r in results:
        print(f"  {r['task_name']}: score={r['score']:.3f} steps={r['steps']} success={r['success']}", file=sys.stderr)
    if results:
        avg = sum(r["score"] for r in results) / len(results)
        print(f"  Average: {avg:.3f}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
