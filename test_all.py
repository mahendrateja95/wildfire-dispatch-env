"""
Complete Test Suite for Wildfire Dispatch Environment
=====================================================
Run: python test_all.py

Tests everything judges will check:
1. All API endpoints
2. All 3 tasks (reset, step, grading)
3. Reward signals (positive, negative, partial)
4. Dangerous action penalties
5. Grader scores in 0.0-1.0 range
6. Log format compliance
7. File structure checks
8. Docker + openenv.yaml checks
"""

import json
import os
import sys
import requests

ENV_URL = "http://localhost:8000"
PASSED = 0
FAILED = 0
TOTAL = 0


def test(name, condition, detail=""):
    global PASSED, FAILED, TOTAL
    TOTAL += 1
    if condition:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name} -- {detail}")


def api_get(path):
    resp = requests.get(f"{ENV_URL}{path}", timeout=10)
    return resp


def api_post(path, data):
    resp = requests.post(f"{ENV_URL}{path}", json=data, timeout=10)
    return resp


# =====================================================================
print("\n" + "=" * 60)
print("TEST SUITE: Wildfire Dispatch Environment")
print("=" * 60)

# =====================================================================
print("\n--- TEST GROUP 1: File Structure ---")
# =====================================================================

test("inference.py exists at root", os.path.exists("inference.py"))
test("openenv.yaml exists", os.path.exists("openenv.yaml"))
test("pyproject.toml exists", os.path.exists("pyproject.toml"))
test("Dockerfile exists", os.path.exists("Dockerfile"))
test("README.md exists", os.path.exists("README.md"))
test("models.py exists", os.path.exists("models.py"))
test("scenarios.py exists", os.path.exists("scenarios.py"))
test("graders.py exists", os.path.exists("graders.py"))
test("server/app.py exists", os.path.exists("server/app.py"))
test("server/environment.py exists", os.path.exists("server/environment.py"))
test("uv.lock exists", os.path.exists("uv.lock"))

# Check openenv.yaml content
with open("openenv.yaml") as f:
    content = f.read()
test("openenv.yaml has spec_version", "spec_version: 1" in content)
test("openenv.yaml has name", "name:" in content)
test("openenv.yaml has app entry", "app: server.app:app" in content)

# Check inference.py has required elements
with open("inference.py") as f:
    inf_content = f.read()
test("inference.py imports OpenAI", "from openai import OpenAI" in inf_content)
test("inference.py reads API_BASE_URL", "API_BASE_URL" in inf_content)
test("inference.py reads MODEL_NAME", "MODEL_NAME" in inf_content)
test("inference.py reads HF_TOKEN", "HF_TOKEN" in inf_content)
test("inference.py has [START] log", "[START]" in inf_content)
test("inference.py has [STEP] log", "[STEP]" in inf_content)
test("inference.py has [END] log", "[END]" in inf_content)

# =====================================================================
print("\n--- TEST GROUP 2: API Endpoints ---")
# =====================================================================

# GET /
r = api_get("/")
test("GET / returns 200", r.status_code == 200)

# GET /health
r = api_get("/health")
test("GET /health returns 200", r.status_code == 200)
test("GET /health returns healthy", r.json().get("status") == "healthy")

# GET /metadata
r = api_get("/metadata")
test("GET /metadata returns 200", r.status_code == 200)
d = r.json()
test("metadata has name", "name" in d)
test("metadata has description", "description" in d)
test("metadata name is correct", d.get("name") == "wildfire_dispatch_env")

# GET /schema
r = api_get("/schema")
test("GET /schema returns 200", r.status_code == 200)
d = r.json()
test("schema has action", "action" in d)
test("schema has observation", "observation" in d)
test("schema has state", "state" in d)

# POST /reset
r = api_post("/reset", {"task_id": "easy_single_fire"})
test("POST /reset returns 200", r.status_code == 200)
d = r.json()
test("reset returns observation", "observation" in d)
test("reset returns done=false", d.get("done") == False)
test("reset observation has task_id", d["observation"].get("task_id") == "easy_single_fire")
test("reset observation has fires", len(d["observation"].get("fires", [])) > 0)
test("reset observation has crews", len(d["observation"].get("crews", [])) > 0)
test("reset observation has weather", d["observation"].get("weather") is not None)

# POST /step
r = api_post("/step", {"action": {"action_type": "deploy_crew", "parameters": {"crew_id": "crew_alpha", "fire_id": "fire_cedar"}}})
test("POST /step returns 200", r.status_code == 200)
d = r.json()
test("step returns observation", "observation" in d)
test("step returns reward", "reward" in d)
test("step returns done", "done" in d)
test("step reward is float", isinstance(d["reward"], (int, float)))

# GET /state
r = api_get("/state")
test("GET /state returns 200", r.status_code == 200)
d = r.json()
test("state has task_id", "task_id" in d)
test("state has step_count", "step_count" in d)
test("state step_count > 0", d.get("step_count", 0) > 0)

# POST /step with invalid action
r = api_post("/step", {"action": {"action_type": "invalid_action", "parameters": {}}})
test("invalid action returns 422", r.status_code == 422)

# =====================================================================
print("\n--- TEST GROUP 3: Easy Task Full Playthrough ---")
# =====================================================================

api_post("/reset", {"task_id": "easy_single_fire"})

steps = [
    {"action_type": "deploy_crew", "parameters": {"crew_id": "crew_alpha", "fire_id": "fire_cedar"}},
    {"action_type": "deploy_crew", "parameters": {"crew_id": "crew_bravo", "fire_id": "fire_cedar"}},
    {"action_type": "deploy_aircraft", "parameters": {"aircraft_id": "heli_1", "fire_id": "fire_cedar"}},
    {"action_type": "create_firebreak", "parameters": {"location": "south of highway 89", "fire_id": "fire_cedar"}},
    {"action_type": "communicate", "parameters": {"message": "Cedar Fire update: crews deployed", "channel": "dispatch"}},
    {"action_type": "resolve", "parameters": {}},
]

rewards = []
for i, action in enumerate(steps):
    r = api_post("/step", {"action": action})
    d = r.json()
    rewards.append(d["reward"])

test("Easy: 6 steps completed", len(rewards) == 6)
test("Easy: deploy_crew gives positive reward", rewards[0] > 0, f"got {rewards[0]}")
test("Easy: deploy_aircraft gives positive reward", rewards[2] > 0, f"got {rewards[2]}")
test("Easy: firebreak gives positive reward", rewards[3] > 0, f"got {rewards[3]}")
test("Easy: communicate gives positive reward", rewards[4] > 0, f"got {rewards[4]}")
test("Easy: final score in 0.0-1.0", 0.0 <= rewards[-1] <= 1.0, f"got {rewards[-1]}")
test("Easy: final score > 0.7 with good play", rewards[-1] > 0.7, f"got {rewards[-1]}")
test("Easy: done=true on resolve", d.get("done") == True)

# =====================================================================
print("\n--- TEST GROUP 4: Medium Task Full Playthrough ---")
# =====================================================================

api_post("/reset", {"task_id": "medium_two_fires"})

steps = [
    {"action_type": "reassess_priority", "parameters": {"fire_id": "fire_valley", "priority": 1}},
    {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_oakdale"}},
    {"action_type": "deploy_crew", "parameters": {"crew_id": "crew_echo", "fire_id": "fire_valley"}},
    {"action_type": "deploy_aircraft", "parameters": {"aircraft_id": "heli_2", "fire_id": "fire_valley"}},
    {"action_type": "request_mutual_aid", "parameters": {}},
    {"action_type": "rotate_crew", "parameters": {"crew_id": "crew_delta"}},
    {"action_type": "communicate", "parameters": {"message": "Valley Fire priority 1. Oakdale evacuation underway.", "channel": "dispatch"}},
    {"action_type": "communicate", "parameters": {"message": "Mutual aid requested. Crew Delta rotated.", "channel": "dispatch"}},
    {"action_type": "resolve", "parameters": {}},
]

rewards = []
for action in steps:
    r = api_post("/step", {"action": action})
    d = r.json()
    rewards.append(d["reward"])

test("Medium: 9 steps completed", len(rewards) == 9)
test("Medium: evacuation gives high reward", rewards[1] >= 0.10, f"got {rewards[1]}")
test("Medium: mutual aid gives reward", rewards[4] > 0, f"got {rewards[4]}")
test("Medium: final score in 0.0-1.0", 0.0 <= rewards[-1] <= 1.0, f"got {rewards[-1]}")
test("Medium: final score > 0.8 with good play", rewards[-1] > 0.8, f"got {rewards[-1]}")
test("Medium: done=true", d.get("done") == True)

# =====================================================================
print("\n--- TEST GROUP 5: Hard Task Full Playthrough ---")
# =====================================================================

api_post("/reset", {"task_id": "hard_cascading_disaster"})

steps = [
    {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_school"}},
    {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_hospital"}},
    {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_senior"}},
    {"action_type": "deploy_crew", "parameters": {"crew_id": "crew_foxtrot", "fire_id": "fire_y"}},
    {"action_type": "deploy_aircraft", "parameters": {"aircraft_id": "heli_3", "fire_id": "fire_y"}},
    {"action_type": "communicate", "parameters": {"message": "Investigating Creek Fire for pipeline threat", "channel": "dispatch"}},
    {"action_type": "communicate", "parameters": {"message": "URGENT: Creek Fire heading toward TransCo gas pipeline. Request emergency shutoff.", "channel": "gas_company"}},
    {"action_type": "request_mutual_aid", "parameters": {}},
    {"action_type": "communicate", "parameters": {"message": "All vulnerable zones evacuated. Pipeline risk communicated.", "channel": "command"}},
    {"action_type": "resolve", "parameters": {}},
]

rewards = []
for action in steps:
    r = api_post("/step", {"action": action})
    d = r.json()
    rewards.append(d["reward"])

test("Hard: 10 steps completed", len(rewards) == 10)
test("Hard: school evacuation gives high reward", rewards[0] >= 0.10, f"got {rewards[0]}")
test("Hard: hospital evacuation gives high reward", rewards[1] >= 0.10, f"got {rewards[1]}")
test("Hard: pipeline comms gives high reward", rewards[6] >= 0.08, f"got {rewards[6]}")
test("Hard: final score in 0.0-1.0", 0.0 <= rewards[-1] <= 1.0, f"got {rewards[-1]}")
test("Hard: final score > 0.7 with good play", rewards[-1] > 0.7, f"got {rewards[-1]}")
test("Hard: done=true", d.get("done") == True)

# =====================================================================
print("\n--- TEST GROUP 6: Dangerous Actions (Penalties) ---")
# =====================================================================

# Test: Deploy fatigued crew
api_post("/reset", {"task_id": "hard_cascading_disaster"})
r = api_post("/step", {"action": {"action_type": "deploy_crew", "parameters": {"crew_id": "crew_golf", "fire_id": "fire_y"}}})
d = r.json()
test("Fatigued crew deploy gives NEGATIVE reward", d["reward"] < 0, f"got {d['reward']}")
test("Fatigued crew hint mentions safety", "safety" in d["observation"]["hint"].lower() or "violation" in d["observation"]["hint"].lower())

# Test: Prioritize Powerline Fire (political pressure)
r = api_post("/step", {"action": {"action_type": "reassess_priority", "parameters": {"fire_id": "fire_x", "priority": 1}}})
d = r.json()
test("Political pressure priority gives NEGATIVE reward", d["reward"] < 0, f"got {d['reward']}")
test("Political pressure hint warns", "wrong" in d["observation"]["hint"].lower() or "power" in d["observation"]["hint"].lower())

# Test: Backfire near hospital
r = api_post("/step", {"action": {"action_type": "set_backfire", "parameters": {"location": "near hospital", "fire_id": "fire_y"}}})
d = r.json()
test("Backfire near hospital gives NEGATIVE reward", d["reward"] < 0, f"got {d['reward']}")

# Check penalties accumulated in state
r = api_get("/state")
state = r.json()
test("Penalties > 0 after dangerous actions", state.get("penalties", 0) > 0, f"got {state.get('penalties', 0)}")
test("Dangerous actions tracked", len(state.get("dangerous_actions_taken", [])) >= 2, f"got {state.get('dangerous_actions_taken', [])}")

# =====================================================================
print("\n--- TEST GROUP 7: Edge Cases ---")
# =====================================================================

# Reset to easy, try to resolve without doing anything needed
api_post("/reset", {"task_id": "medium_two_fires"})
r = api_post("/step", {"action": {"action_type": "resolve", "parameters": {}}})
d = r.json()
test("Premature resolve gives negative reward", d["reward"] < 0, f"got {d['reward']}")
test("Premature resolve is NOT done", d["done"] == False)

# Deploy to non-existent fire
r = api_post("/step", {"action": {"action_type": "deploy_crew", "parameters": {"crew_id": "crew_echo", "fire_id": "fake_fire"}}})
d = r.json()
test("Invalid fire_id gives negative reward", d["reward"] < 0, f"got {d['reward']}")

# Deploy non-existent crew
r = api_post("/step", {"action": {"action_type": "deploy_crew", "parameters": {"crew_id": "fake_crew", "fire_id": "fire_valley"}}})
d = r.json()
test("Invalid crew_id gives negative reward", d["reward"] < 0, f"got {d['reward']}")

# Deploy aircraft in maintenance
api_post("/reset", {"task_id": "hard_cascading_disaster"})
r = api_post("/step", {"action": {"action_type": "deploy_aircraft", "parameters": {"aircraft_id": "heli_4", "fire_id": "fire_y"}}})
d = r.json()
test("Maintenance aircraft gives negative reward", d["reward"] < 0, f"got {d['reward']}")

# Request mutual aid twice
api_post("/reset", {"task_id": "easy_single_fire"})
api_post("/step", {"action": {"action_type": "request_mutual_aid", "parameters": {}}})
r = api_post("/step", {"action": {"action_type": "request_mutual_aid", "parameters": {}}})
d = r.json()
test("Duplicate mutual aid gives 0 reward", d["reward"] == 0.0, f"got {d['reward']}")

# Evacuate same zone twice
api_post("/reset", {"task_id": "medium_two_fires"})
api_post("/step", {"action": {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_oakdale"}}})
r = api_post("/step", {"action": {"action_type": "order_evacuation", "parameters": {"zone_id": "zone_oakdale"}}})
d = r.json()
test("Duplicate evacuation gives 0 reward", d["reward"] == 0.0, f"got {d['reward']}")

# =====================================================================
print("\n--- TEST GROUP 8: Graders (Direct) ---")
# =====================================================================

from graders import GRADERS

# Test graders with empty state
for task_id, grader in GRADERS.items():
    score = grader({"step_count": 10, "max_steps": 20})
    test(f"Grader {task_id}: empty state score >= 0.0", score >= 0.0, f"got {score}")
    test(f"Grader {task_id}: empty state score <= 1.0", score <= 1.0, f"got {score}")

# Test graders with perfect state
perfect_easy = {
    "step_count": 5, "max_steps": 12, "penalties": 0,
    "crews": {"crew_alpha": {"assigned_to": "fire_cedar"}, "crew_bravo": {"assigned_to": "fire_cedar"}},
    "aircraft": {"heli_1": {"assigned_to": "fire_cedar"}},
    "firebreaks_created": ["south_highway_near_fire_cedar"],
    "communications_sent": ["status update"],
    "resolved": True,
}
score = GRADERS["easy_single_fire"](perfect_easy)
test(f"Easy grader perfect play > 0.85", score > 0.85, f"got {score}")

perfect_medium = {
    "step_count": 8, "max_steps": 16, "penalties": 0,
    "priorities_reassessed": ["fire_valley"],
    "evacuations_ordered": ["zone_oakdale"],
    "crews": {"crew_echo": {"assigned_to": "fire_valley"}},
    "aircraft": {"heli_2": {"assigned_to": "fire_valley"}},
    "mutual_aid_requested": True,
    "crews_rotated": ["crew_delta"],
    "communications_sent": ["msg1", "msg2"],
    "resolved": True,
}
score = GRADERS["medium_two_fires"](perfect_medium)
test(f"Medium grader perfect play > 0.85", score > 0.85, f"got {score}")

perfect_hard = {
    "step_count": 10, "max_steps": 20, "penalties": 0,
    "evacuations_ordered": ["zone_school", "zone_hospital", "zone_senior"],
    "crews": {"crew_foxtrot": {"assigned_to": "fire_y"}},
    "aircraft": {"heli_3": {"assigned_to": "fire_y"}},
    "diagnostics_run": ["check_creek_fire_detail"],
    "communications_sent": ["update1", "pipeline gas alert", "update3"],
    "mutual_aid_requested": True,
    "dangerous_actions_taken": [],
    "priorities_reassessed": [],
    "resolved": True,
}
score = GRADERS["hard_cascading_disaster"](perfect_hard)
test(f"Hard grader perfect play > 0.85", score > 0.85, f"got {score}")

# =====================================================================
print("\n--- TEST GROUP 9: Log Format Compliance ---")
# =====================================================================

from inference import log_start, log_step, log_end, format_action_str, parse_action
import io
from contextlib import redirect_stdout

# Capture log_start output
f = io.StringIO()
with redirect_stdout(f):
    log_start(task="test-task", env="test-env", model="test-model")
output = f.getvalue().strip()
test("log_start format correct", output == "[START] task=test-task env=test-env model=test-model", f"got: {output}")

# Capture log_step output
f = io.StringIO()
with redirect_stdout(f):
    log_step(step=1, action="deploy_crew(id='a')", reward=0.12, done=False, error=None)
output = f.getvalue().strip()
test("log_step format correct", output == "[STEP] step=1 action=deploy_crew(id='a') reward=0.12 done=false error=null", f"got: {output}")

# log_step with error
f = io.StringIO()
with redirect_stdout(f):
    log_step(step=2, action="bad()", reward=0.0, done=False, error="something broke")
output = f.getvalue().strip()
test("log_step with error", "error=something broke" in output, f"got: {output}")

# log_step done=true
f = io.StringIO()
with redirect_stdout(f):
    log_step(step=3, action="resolve()", reward=0.95, done=True, error=None)
output = f.getvalue().strip()
test("log_step done=true format", "done=true" in output)

# Capture log_end output
f = io.StringIO()
with redirect_stdout(f):
    log_end(success=True, steps=3, score=0.85, rewards=[0.12, 0.10, 0.85])
output = f.getvalue().strip()
test("log_end format correct", output == "[END] success=true steps=3 score=0.850 rewards=0.12,0.10,0.85", f"got: {output}")

# log_end failure
f = io.StringIO()
with redirect_stdout(f):
    log_end(success=False, steps=5, score=0.2, rewards=[0.1, 0.0, -0.05, 0.1, 0.2])
output = f.getvalue().strip()
test("log_end failure format", "success=false" in output)

# format_action_str
test("format_action with params", format_action_str({"action_type": "deploy_crew", "parameters": {"crew_id": "a"}}) == "deploy_crew(crew_id='a')")
test("format_action no params", format_action_str({"action_type": "resolve", "parameters": {}}) == "resolve()")

# parse_action
test("parse clean JSON", parse_action('{"action_type":"resolve","parameters":{}}') == {"action_type": "resolve", "parameters": {}})
test("parse markdown JSON", parse_action('```json\n{"action_type":"resolve","parameters":{}}\n```') == {"action_type": "resolve", "parameters": {}})
test("parse messy text", parse_action('Here is action: {"action_type":"resolve","parameters":{}} done') == {"action_type": "resolve", "parameters": {}})

# =====================================================================
print("\n--- TEST GROUP 10: Task Enumeration ---")
# =====================================================================

from scenarios import ALL_SCENARIOS

test("3 scenarios defined", len(ALL_SCENARIOS) == 3)
test("easy_single_fire exists", "easy_single_fire" in ALL_SCENARIOS)
test("medium_two_fires exists", "medium_two_fires" in ALL_SCENARIOS)
test("hard_cascading_disaster exists", "hard_cascading_disaster" in ALL_SCENARIOS)

for task_id, scenario in ALL_SCENARIOS.items():
    test(f"{task_id} has fires", len(scenario.get("fires", {})) > 0)
    test(f"{task_id} has crews", len(scenario.get("crews", {})) > 0)
    test(f"{task_id} has weather", scenario.get("weather") is not None)
    test(f"{task_id} has grader", task_id in GRADERS)
    test(f"{task_id} has max_steps", scenario.get("max_steps", 0) > 0)

# =====================================================================
print("\n--- TEST GROUP 11: Max Steps Boundary ---")
# =====================================================================

api_post("/reset", {"task_id": "easy_single_fire"})
# Do 12 steps (max) of communication to hit limit
for i in range(12):
    r = api_post("/step", {"action": {"action_type": "communicate", "parameters": {"message": f"msg {i}", "channel": "test"}}})
    d = r.json()

test("Max steps reached -> done=true", d["done"] == True)
test("Max steps final score in 0.0-1.0", 0.0 <= d["reward"] <= 1.0, f"got {d['reward']}")

# =====================================================================
print("\n--- TEST GROUP 12: HF Space Live Check ---")
# =====================================================================

HF = "https://Mahendra95-wildfire-dispatch-env.hf.space"

r = requests.get(f"{HF}/health", timeout=15)
test("HF /health returns 200", r.status_code == 200)
test("HF /health returns healthy", r.json().get("status") == "healthy")

r = requests.get(f"{HF}/metadata", timeout=15)
test("HF /metadata returns 200", r.status_code == 200)

r = requests.get(f"{HF}/schema", timeout=15)
test("HF /schema returns 200", r.status_code == 200)

r = requests.post(f"{HF}/reset", json={"task_id": "easy_single_fire"}, timeout=15)
test("HF /reset returns 200", r.status_code == 200)
test("HF /reset has observation", "observation" in r.json())

r = requests.post(f"{HF}/step", json={"action": {"action_type": "communicate", "parameters": {"message": "test", "channel": "test"}}}, timeout=15)
test("HF /step returns 200", r.status_code == 200)
test("HF /step has reward", "reward" in r.json())

r = requests.get(f"{HF}/state", timeout=15)
test("HF /state returns 200", r.status_code == 200)

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "=" * 60)
print(f"  RESULTS: {PASSED}/{TOTAL} passed, {FAILED} failed")
print("=" * 60)

if FAILED == 0:
    print("\n  ALL TESTS PASSED! Ready to submit.")
else:
    print(f"\n  {FAILED} TESTS FAILED. Fix before submitting.")

sys.exit(0 if FAILED == 0 else 1)
