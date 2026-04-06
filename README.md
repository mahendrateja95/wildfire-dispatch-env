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

# Wildfire Dispatch Environment

**A high-fidelity AI evaluation environment that simulates wildfire resource dispatch under life-or-death pressure -- testing whether language models can prioritize human lives over political noise, manage hidden threats, and make split-second triage decisions that real incident commanders face every fire season.**

---

## Motivation

Wildfire suppression is one of the most consequential resource-allocation problems in emergency management. In 2023, the United States spent **$3.1 billion** on wildfire suppression. The 2023 Maui wildfire killed 101 people -- many deaths attributable to delayed evacuations. The 2018 Camp Fire destroyed 18,804 structures in 24 hours. Behind every one of these disasters was a dispatch coordinator making decisions under incomplete information, political pressure, and impossible resource constraints.

This environment models that decision-making process with calibrated realism:

- **Resource scarcity** -- never enough crews, aircraft, or budget for all active fires simultaneously
- **Life-safety triage** -- evacuating a school of 180 children must come before protecting $4M in timber, regardless of who is calling
- **Information asymmetry** -- a "low-priority" brush fire may be heading toward a high-pressure gas pipeline, but only if the agent investigates
- **Political pressure traps** -- a County Commissioner demands resources on a power outage while children are in the path of an uncontained canyon fire
- **Temporal dynamics** -- wind shifts that transform a manageable fire into a catastrophe within hours
- **Crew safety** -- deploying a fatigued crew is not just suboptimal, it is a safety violation that has killed firefighters in real incidents (Yarnell Hill 2013, South Canyon 1994)

The environment follows **ICS (Incident Command System) doctrine**: Life Safety > Incident Stabilization > Property Conservation. Agents that invert these priorities are penalized. Agents that resist political pressure, investigate hidden threats, and protect vulnerable populations are rewarded.

---

## Features

| Category | What Makes This Special |
|----------|------------------------|
| **Terrain-aware fire physics** | 7 terrain types with calibrated spread multipliers (canyon 2.0x, grassland 1.5x, urban interface 0.7x). Compound terrain blending (canyon + urban = 1.6x). |
| **Wind-fire vector interaction** | Dot-product model computes how wind direction aids or opposes fire spread. Aligned wind adds up to +40% spread rate; opposing wind reduces up to -30%. |
| **Dynamic weather system** | Wind direction, speed, temperature, humidity, and fire danger rating shift over time. The hard task has 3 distinct wind shifts across 12 simulated hours. |
| **Crew fatigue progression** | Deployed crews accumulate 0.5 hours of duty per step. At 12+ hours, crews transition to "fatigued" status. Deploying a fatigued crew is a safety violation with negative reward. |
| **Surprise events** | In the hard task, if Creek Fire is not investigated by step 10, it explodes to 3x size as an underground gas seep accelerates the blaze -- revealing a hidden pipeline threat. |
| **Proximity urgency** | Continuous negative reward signal when vulnerable, un-evacuated populations are dangerously close to fire. Closer distance = stronger penalty, creating urgency. |
| **Information asymmetry** | Agents must use the `investigate` action to discover hidden threats (e.g., gas pipeline 6km from a "minor" fire). Without investigation, critical information remains hidden. |
| **Political pressure traps** | A politician demands resources on a power outage (no lives at risk) while 180 children sit in a school 1.8km from an uncontained canyon fire. Yielding to pressure is penalized. |
| **ICS-209 situation reports** | Every scenario opens with a realistic Incident Command System briefing -- incident number, IC name, jurisdiction, resource status, IAP objectives -- matching real wildfire documentation. |
| **Multi-objective grading** | Final score blends evacuations, resource deployment, dangerous action avoidance, communication quality, budget efficiency, timing bonuses, and action ordering. |
| **Budget tracking** | Every action has a cost. The grader separately tracks useful vs. wasteful spending and awards/penalizes based on budget efficiency. |

---

## Action Space

The agent has 11 available actions per step. Each action consumes one step (30 simulated minutes).

| Action | Parameters | Description | Cost |
|--------|-----------|-------------|------|
| `deploy_crew` | `crew_id`, `fire_id` | Send a crew to a fire's front line | $20,000 |
| `deploy_aircraft` | `aircraft_id`, `fire_id` | Deploy helicopter or air tanker for water/retardant drops | $30,000 |
| `create_firebreak` | `location`, `fire_id` | Build a firebreak to halt fire spread | $15,000 |
| `order_evacuation` | `zone_id` | Evacuate a population zone ($100/person) | Variable |
| `rotate_crew` | `crew_id` | Pull a crew off the line for mandatory rest | Free |
| `request_mutual_aid` | -- | Request additional crews + aircraft from neighboring counties (4-5 hr ETA) | $50,000 |
| `reassess_priority` | `fire_id`, `priority` | Change a fire's priority level (1 = highest, 5 = lowest) | Free |
| `set_backfire` | `location`, `fire_id` | Controlled burn to create buffer (dangerous near structures) | $10,000 |
| `investigate` | `target` | Investigate a fire, crew, or infrastructure for hidden information | Free |
| `communicate` | `message`, `channel` | Send status update, evacuation alert, or agency notification | Free |
| `resolve` | -- | Mark the incident as handled and trigger final grading | Free |

**Example action:**
```json
{"action_type": "order_evacuation", "parameters": {"zone_id": "zone_school"}}
```

---

## Observation Space

Each step returns a structured observation with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `fires` | List[FireInfo] | Active fires: acres, containment %, spread direction/rate, terrain, threats, assigned crews/aircraft |
| `crews` | List[CrewInfo] | Crews: status (available/deployed/fatigued), hours on duty, specialty, location |
| `aircraft` | List[AircraftInfo] | Aircraft: type (helicopter/air_tanker), status (available/deployed/maintenance), capacity |
| `evacuation_zones` | List[EvacZoneInfo] | Zones: population, distance to nearest fire (km), vulnerability flag, evacuation status |
| `weather` | WeatherInfo | Wind speed/direction, temperature, humidity, forecast changes, fire danger rating |
| `budget_remaining` | float | Remaining operational budget in dollars |
| `budget_total` | float | Starting budget allocation |
| `time_elapsed_hours` | float | Simulated time since incident start |
| `communication_log` | List[str] | All messages sent during the incident |
| `situation_report` | str | Auto-generated ICS-style situation report of all fire statuses |
| `available_actions` | List[str] | All actions the agent can take with parameter hints |
| `hint` | str | Context-sensitive guidance (investigation tips, error feedback, surprise events) |
| `mutual_aid_eta_hours` | float | Hours until mutual aid arrives (null if not requested) |
| `task_id` | str | Current task identifier |
| `task_description` | str | Natural language description of the scenario |

---

## Tasks

### Task 1: Single Fire Containment (Easy)

| Property | Value |
|----------|-------|
| **Task ID** | `easy_single_fire` |
| **Difficulty** | Easy |
| **Max Steps** | 12 |
| **Fires** | 1 (Cedar Fire, 120 acres, grassland) |
| **Resources** | 3 crews, 2 aircraft, $500K budget |
| **Objective** | Deploy resources to Cedar Fire, create firebreak protecting Highway 89, assess evacuation need for Pine Ranch (12 residents), communicate status, resolve |
| **Key Decision** | Straightforward resource deployment with ample capacity |
| **Investigation Targets** | 4 -- fire behavior, weather detail, road access, structure assessment |
| **Baseline Score** | 0.750 (LLaMA 3.3 70B) |

### Task 2: Two Fires, Limited Resources (Medium)

| Property | Value |
|----------|-------|
| **Task ID** | `medium_two_fires` |
| **Difficulty** | Medium |
| **Max Steps** | 16 |
| **Fires** | 2 (Ridge Fire 520 ac in forest, Valley Fire 80 ac in grassland/WUI) |
| **Resources** | 2 crews (1 fatigued at 11 hrs), 1 helicopter, $400K budget |
| **Objective** | Prioritize Valley Fire (threatens Oakdale, pop. 500 including 120 children in school), evacuate Oakdale before wind shift, rotate fatigued Crew Delta, request mutual aid |
| **Dilemmas** | Pull resources from partially-contained Ridge Fire? Deploy tired crew or rest them? Evacuate now or wait for confirmation? |
| **Weather Shift** | Wind shifts W at 30 km/h after 4 hours, accelerating Valley Fire to 40 ac/hr directly toward town |
| **Investigation Targets** | 5 -- Valley Fire behavior, Ridge Fire behavior, evacuation routes, mutual aid availability, Crew Delta fatigue assessment |
| **Baseline Score** | 0.850 (LLaMA 3.3 70B) |

### Task 3: Cascading Disaster (Hard)

| Property | Value |
|----------|-------|
| **Task ID** | `hard_cascading_disaster` |
| **Difficulty** | Hard |
| **Max Steps** | 20 |
| **Fires** | 3 (Powerline Fire 950 ac, Hillside Fire 200 ac in canyon/WUI, Creek Fire 45 ac in brush) |
| **Resources** | 2 crews (1 fatigued at 13 hrs), 2 helicopters (1 in maintenance), **$50K remaining** of $500K |
| **Objective** | Evacuate school (180 children), hospital (45 patients, 3 on ventilators), senior living (60 elderly); deploy resources to Hillside Fire; discover and communicate pipeline threat; resist political pressure; request mutual aid |
| **Dilemmas** | Politician demands resources on Powerline Fire (50K homes without power) vs. uncontained canyon fire heading toward school. Creek Fire looks harmless but hides a gas pipeline threat. Budget nearly exhausted. |
| **Red Herrings** | Powerline Fire has intense media/political pressure but zero lives at risk. Creek Fire appears low-priority (remote brush) but threatens a high-pressure gas pipeline. |
| **Dangerous Actions** | Deploying fatigued Crew Golf (-0.06), setting backfire near hospital (-0.08), prioritizing Powerline Fire over life-safety (-0.05), ignoring pipeline threat |
| **Weather Shifts** | 3 shifts over 12 hours: NE at T+2hr (accelerates Hillside toward school), E at T+6hr (brief moderation), SE at T+10hr (pushes Creek toward pipeline) |
| **Surprise Event** | If Creek Fire is not investigated by step 10, it explodes to 3x size as a gas seep accelerates the blaze |
| **Investigation Targets** | 10 -- Hillside Fire behavior, Creek Fire detail, Powerline Fire detail, hospital evacuation logistics, Crew Golf fatigue, political situation, mutual aid options, pipeline infrastructure specs, weather forecast, road conditions |
| **Baseline Score** | 0.500 (LLaMA 3.3 70B) |

---

## Reward Design

### Per-Step Rewards

| Action | Reward | Condition |
|--------|--------|-----------|
| Correct crew deployment | +0.12 | Crew sent to the right fire |
| Correct aircraft deployment | +0.10 | Aircraft sent to the right fire |
| Evacuate threatened vulnerable zone | +0.15 | Zone has vulnerable population (school, hospital) |
| Evacuate threatened zone | +0.10 | Zone in danger but no vulnerable flag |
| Critical communication (pipeline/gas) | +0.10 | Message mentions pipeline, gas, or TransCo |
| Create firebreak | +0.08 | Any firebreak creation |
| Request mutual aid | +0.08 | First request only |
| Investigate hidden threat | +0.08 | Valid investigation target |
| Correct priority reassessment | +0.08 | Hillside Fire set to priority 1 |
| Set backfire (safe location) | +0.06 | Away from vulnerable structures |
| Rotate fatigued crew | +0.06 | Crew was at 10+ hours or fatigued status |
| General communication | +0.04 | Any communication sent |
| Wrong deployment (partial) | +0.03-0.04 | Resource sent to wrong fire |
| Wrong prioritization | **-0.05** | Prioritizing Powerline Fire over life-safety |
| Deploy fatigued crew | **-0.06** | Crew at 12+ hours and fatigued status |
| Backfire near hospital/school | **-0.08** | Smoke endangers patients/children |

### Grader Bonuses (Applied at Episode End)

| Bonus | Value | Condition |
|-------|-------|-----------|
| **Timing bonus** | +0.03 | School evacuation within first 5 steps (hard) or Oakdale within first 4 steps (medium) |
| **Action ordering** | +0.02 | Any evacuation ordered BEFORE any crew deployment (life safety first principle) |
| **Communication quality** | up to +0.05 | Proportional to keyword coverage in communications (e.g., "pipeline", "school", "hospital") |
| **Budget efficiency** | +0.02 | More than 50% budget remaining at resolution |
| **Budget waste** | -0.02 | Less than 10% budget remaining (overspending) |

### Final Score Composition (Hard Task Example)

| Component | Weight | What It Measures |
|-----------|--------|-----------------|
| Evacuate school | 0.15 | Highest-priority life safety |
| Evacuate hospital | 0.12 | Critical vulnerable population |
| Discover pipeline threat | 0.12 | Investigation and hidden threat detection |
| Avoid dangerous actions | 0.10 | Resistance to traps (fatigue, backfire, political pressure) |
| Evacuate senior living | 0.08 | Vulnerable population protection |
| Communicate pipeline risk | 0.08 | Alerting the gas company |
| Deploy crew to Hillside | 0.08 | Correct resource allocation |
| Ignore political pressure | 0.05 | Not prioritizing Powerline Fire |
| Deploy aircraft to Hillside | 0.05 | Correct aerial suppression |
| Request mutual aid | 0.05 | Resource augmentation |
| Communications sent | 0.05 | General situational awareness |
| Resolve incident | 0.05 | Proper closure |
| Step efficiency | 0.02 | Fewer steps = higher efficiency |
| Bonuses | up to +0.12 | Timing, ordering, comm quality, budget |

---

## Environment Mechanics

### Fire Spread Physics

Fire growth each step is computed as:

```
effective_rate = base_rate * terrain_multiplier * wind_multiplier * (1 - resource_reduction)
growth_acres = effective_rate * 0.5  (each step = 30 minutes)
```

**Terrain Multipliers:**

| Terrain | Multiplier | Description |
|---------|-----------|-------------|
| Canyon | 2.0x | Steep slopes pre-heat fuels, convective column accelerates spread |
| Grassland | 1.5x | Continuous fine fuels, fast surface fire |
| Brush | 1.2x | Heavy shrub fuels (manzanita, chamise) |
| Forest | 1.0x | Baseline -- mixed conifer, timber litter |
| Urban Interface | 0.7x | Structures and defensible space slow spread |
| Canyon + Urban | 1.6x | Canyon dominates but urban slows slightly |
| Grassland + Urban | 1.1x | Grass spread moderated by structures |

**Resource Suppression:** Each assigned crew reduces fire spread by 30%, each aircraft by 25%, capped at 95% total reduction. Containment increases by 3% per crew and 2% per aircraft per step.

### Wind-Fire Interaction

Wind and fire spread directions are modeled as 2D vectors (N, NE, E, SE, S, SW, W, NW). The dot product determines the interaction:

- **Aligned (dot > 0.5):** Wind aids fire -- spread rate increases up to **+40%**
- **Opposed (dot < -0.5):** Wind fights fire -- spread rate decreases up to **-30%**
- **Perpendicular:** No significant effect (1.0x multiplier)

### Dynamic Weather Shifts

Weather conditions evolve based on elapsed time and scenario-specific forecast models:

- **Medium task:** Wind shifts from NW to W at 30 km/h after 4 hours, pushing Valley Fire directly toward Oakdale. Fire danger escalates to extreme.
- **Hard task:** Three sequential shifts -- NE at T+2hr (accelerates canyon fire), E at T+6hr (brief moderation), SE at T+10hr (redirects Creek Fire toward gas pipeline).

### Crew Fatigue Progression

- Deployed crews accumulate **0.5 hours of duty per step** (each step = 30 simulated minutes)
- At **12+ hours on duty**, crew status transitions to **"fatigued"**
- Deploying a fatigued crew triggers a **safety violation penalty (-0.06)** and is logged as a dangerous action
- Rotating a fatigued crew earns **+0.06 reward** and resets their hours to 0

### Surprise Events

In the hard task, if the agent has NOT investigated Creek Fire by **step 10**:

1. Creek Fire explodes to **3x its current size** (simulating an underground gas seep)
2. Spread rate **doubles**
3. The threat list updates to reveal the TransCo Gas Pipeline LP-7 at 3km distance
4. The agent receives an urgent surprise notification with guidance to investigate and alert the gas company

This mechanic rewards proactive investigation and punishes neglect of seemingly low-priority fires.

### Information Asymmetry

Each scenario includes investigation targets that reveal critical information not available in the default observation:

- **Easy (4 targets):** Fire behavior analysis, NWS spot forecast, road access conditions, structure triage assessments
- **Medium (5 targets):** Valley Fire behavior + FBAN recommendation, Ridge Fire assessment, evacuation routes with ADA transport details, mutual aid availability, crew fatigue medical assessment
- **Hard (10 targets):** Hillside Fire canyon behavior model with timeline, Creek Fire hidden pipeline threat, Powerline Fire political assessment, hospital patient manifest and transport requirements, Crew Golf safety officer determination, political/media situation brief, mutual aid from county/state/federal sources, pipeline infrastructure specs (24-inch, 800 PSI, 2-hour shutoff sequence), detailed NWS forecast with two danger windows, road conditions including bridge weight restrictions

---

## Setup and Usage

### Local Development

```bash
pip install -r requirements.txt
python -m server.app
```

In a separate terminal:

```bash
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
| `/schema` | GET | JSON schemas for action, observation, and state models |
| `/reset` | POST | Initialize a scenario with `task_id` parameter (`easy_single_fire`, `medium_two_fires`, `hard_cascading_disaster`) |
| `/step` | POST | Execute an action and receive observation, reward, done flag, and info dict |
| `/state` | GET | Full internal state (for debugging -- not available to agent during evaluation) |

---

## Baseline Scores

Scores obtained with LLaMA 3.3 70B via Groq inference.

| Task | Score | Steps Used | Max Steps | Key Observations |
|------|-------|-----------|-----------|-----------------|
| `easy_single_fire` | 0.750 | 12 | 12 | Deploys resources correctly, sometimes over-communicates |
| `medium_two_fires` | 0.850 | 16 | 16 | Good life-safety prioritization, sometimes misses crew rotation |
| `hard_cascading_disaster` | 0.500 | 20 | 20 | Evacuates correctly but misses pipeline threat and wastes steps on Powerline Fire |

**Composite Average: 0.700**

The hard task is intentionally designed so that current frontier models score around 50% -- they consistently fall for political pressure traps and fail to investigate the Creek Fire before the surprise event triggers. This leaves significant headroom for improved agent architectures.

---

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `API_BASE_URL` | LLM API endpoint (OpenAI-compatible) | Yes | -- |
| `MODEL_NAME` | Model identifier (e.g., `gpt-4o-mini`, `llama-3.3-70b`) | Yes | -- |
| `HF_TOKEN` | Hugging Face token or API key | Yes | -- |
| `OPENAI_API_KEY` | Fallback API key | No | -- |
| `ENV_URL` | Environment server URL | No | `http://localhost:8000` |
| `PORT` | Server port | No | `8000` |

---

## Project Structure

```
wildfire-dispatch-env/
├── openenv.yaml          # OpenEnv manifest
├── pyproject.toml         # Project metadata and dependencies
├── Dockerfile             # Container config (HF Spaces compatible)
├── requirements.txt       # Python dependencies
├── inference.py           # Baseline inference script (OpenAI-compatible client)
├── models.py              # Pydantic models: Action, Observation, State, FireInfo, CrewInfo, etc.
├── scenarios.py           # 3 wildfire scenarios with ICS-209 briefings, investigation targets, dangerous action descriptions
├── graders.py             # Deterministic multi-objective graders (timing, ordering, budget, comm quality bonuses)
├── client.py              # EnvClient subclass
├── __init__.py
├── README.md
└── server/
    ├── __init__.py
    ├── app.py             # FastAPI application (all endpoints)
    └── environment.py     # Core simulation: fire physics, wind interaction, fatigue, surprise events, proximity urgency
```

---

## License

MIT
