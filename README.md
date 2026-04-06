---
title: Wildfire Dispatch Environment
emoji: 🔥
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 8000
tags:
  - openenv
---

# Wildfire Dispatch Environment (OpenEnv)

An OpenEnv-compliant environment simulating **wildfire resource dispatch and emergency coordination**. An AI agent acts as a Wildfire Dispatch Coordinator — allocating firefighting crews, aircraft, and equipment across active wildfires while managing evacuations, weather shifts, and life-safety decisions under extreme pressure.

## Motivation

Wildfire management is a critical global challenge. In 2023 alone, the US spent $3.1B on wildfire suppression. Dispatch coordinators must make split-second decisions that determine whether communities are saved or lost. This environment models the real decision-making process:

- **Resource allocation** under scarcity (not enough crews for all fires)
- **Life-safety prioritization** (evacuate schools before protecting timber)
- **Temporal dynamics** (wind shifts change everything in hours)
- **Hidden threats** (a "small" fire heading toward a gas pipeline)
- **Pressure resistance** (political/media pressure vs. tactical priorities)

## Action Space

| Action | Parameters | Description |
|--------|-----------|-------------|
| `deploy_crew` | `crew_id`, `fire_id` | Send a crew to fight a fire |
| `deploy_aircraft` | `aircraft_id`, `fire_id` | Deploy helicopter/tanker for water drops |
| `create_firebreak` | `location`, `fire_id` | Build firebreak to stop spread |
| `order_evacuation` | `zone_id` | Evacuate a population zone |
| `rotate_crew` | `crew_id` | Rest a fatigued crew (safety) |
| `request_mutual_aid` | — | Request additional resources (4-5hr ETA) |
| `reassess_priority` | `fire_id`, `priority` | Change fire priority (1=highest) |
| `set_backfire` | `location`, `fire_id` | Controlled burn (risky near structures) |
| `communicate` | `message`, `channel` | Send status update / alert agencies |
| `resolve` | — | Mark situation as handled |

### Example Action
```json
{"action_type": "order_evacuation", "parameters": {"zone_id": "zone_school"}}
```

## Observation Space

Each observation includes:
- **fires**: Active fires with size (acres), containment %, spread direction/rate, terrain, threats, assigned resources
- **crews**: Firefighting crews with status, fatigue (hours on duty), location, specialty
- **aircraft**: Helicopters/tankers with status, capacity, assignment
- **evacuation_zones**: Population zones with size, distance to fire, vulnerability (schools, hospitals)
- **weather**: Wind speed/direction, temperature, humidity, forecast changes, fire danger rating
- **budget**: Remaining operational budget
- **situation_report**: Summary of all fire statuses
- **communication_log**: Messages sent during incident

## Tasks

### Task 1: Single Fire Containment (Easy)
- **ID**: `easy_single_fire`
- **Scenario**: One fire (Cedar Fire, 120 acres) near Highway 89. Ample resources (3 crews, 2 aircraft). Stable weather.
- **Objective**: Deploy resources, create firebreak, assess evacuation need, communicate, contain
- **Max steps**: 12
- **Baseline score**: 0.750 (LLaMA 3.3 70B)

### Task 2: Two Fires, Limited Resources (Medium)
- **ID**: `medium_two_fires`
- **Scenario**: Ridge Fire (large, forest, partially contained) and Valley Fire (small, fast, near town of 500). Only 2 crews (1 fatigued), 1 helicopter. Wind shifting toward town in 4 hours.
- **Objective**: Prioritize life safety (Valley Fire), evacuate Oakdale, manage fatigued crew, request mutual aid
- **Dilemma**: Pull resources from contained fire? Evacuate now or wait? Deploy tired crew?
- **Max steps**: 16
- **Baseline score**: 0.850 (LLaMA 3.3 70B)

### Task 3: Cascading Disaster (Hard)
- **ID**: `hard_cascading_disaster`
- **Scenario**: 3 fires, red herrings, political pressure. Fire X near power lines (media pressure), Fire Y threatening school + hospital, Fire Z appears minor but heading toward gas pipeline. Minimal budget, fatigued crew, wind shifts 3 times.
- **Red herrings**: Politician demanding resources on Powerline Fire; Creek Fire looking harmless
- **Dangerous actions**: Deploying fatigued crew, setting backfire near hospital, ignoring pipeline threat, bowing to political pressure
- **Max steps**: 20
- **Baseline score**: 0.500 (LLaMA 3.3 70B)

## Reward Design

### Per-step rewards
| Action | Reward |
|--------|--------|
| Correct crew/aircraft deployment | +0.10 to +0.12 |
| Evacuating threatened zone | +0.10 to +0.15 |
| Critical communication (pipeline) | +0.10 |
| Creating firebreak | +0.08 |
| Requesting mutual aid | +0.08 |
| Rotating fatigued crew | +0.06 |
| General communication | +0.04 |
| Wrong deployment | +0.03 (partial) |
| Deploying fatigued crew | **-0.06** |
| Backfire near hospital | **-0.08** |
| Wrong prioritization | **-0.05** |

### Final grading (0.0–1.0)
Multi-objective scoring weighted by: evacuations completed, resources deployed correctly, dangerous actions avoided, communication quality, resolution, and efficiency.

## Setup & Usage

### Local Development
```bash
pip install -r requirements.txt
python -m server.app
# In another terminal:
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export OPENAI_API_KEY="your-key"
export ENV_URL="http://localhost:8000"
python inference.py
```

### Docker
```bash
docker build -t wildfire-dispatch-env .
docker run -p 8000:8000 wildfire-dispatch-env
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns `{"status": "healthy"}` |
| `/metadata` | GET | Environment name and description |
| `/schema` | GET | JSON schemas for action/observation/state |
| `/reset` | POST | Reset with `task_id` parameter |
| `/step` | POST | Execute an action |
| `/state` | GET | Current internal state |

## Baseline Scores (LLaMA 3.3 70B via Groq)

| Task | Score | Steps | Notes |
|------|-------|-------|-------|
| easy_single_fire | 0.750 | 12 | Deploys resources correctly, sometimes over-communicates |
| medium_two_fires | 0.850 | 16 | Good prioritization, sometimes misses crew rotation |
| hard_cascading_disaster | 0.500 | 20 | Evacuates correctly but misses pipeline threat and wastes steps |

**Average: 0.700**

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_BASE_URL` | LLM API endpoint | Yes |
| `MODEL_NAME` | Model identifier | Yes |
| `HF_TOKEN` | Hugging Face / API key | Yes |
| `OPENAI_API_KEY` | Fallback API key | No |
| `ENV_URL` | Environment server URL | No (default: http://localhost:8000) |
| `PORT` | Server port | No (default: 8000) |

## Project Structure

```
wildfire-dispatch-env/
├── openenv.yaml          # OpenEnv manifest
├── pyproject.toml         # Project metadata & dependencies
├── Dockerfile             # Container config (HF Spaces compatible)
├── requirements.txt       # Python dependencies
├── inference.py           # Baseline inference script (OpenAI client)
├── models.py              # Pydantic Action/Observation/State models
├── scenarios.py           # 3 wildfire scenarios (easy/medium/hard)
├── graders.py             # Deterministic task graders (0.0–1.0)
├── client.py              # EnvClient subclass
├── __init__.py
├── README.md
└── server/
    ├── __init__.py
    ├── app.py             # FastAPI application (all endpoints)
    └── environment.py     # Core dispatch simulation logic
```

## License

MIT
