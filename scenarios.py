"""Wildfire scenarios for easy, medium, and hard tasks."""

from __future__ import annotations


# ======================================================================
# TASK 1 -- EASY: Single Fire Containment
# ======================================================================

TASK_EASY = {
    "task_id": "easy_single_fire",
    "task_description": (
        "A wildfire ('Cedar Fire') has broken out near Highway 89. You have ample resources. "
        "Deploy crews and aircraft, create a firebreak to protect the highway, "
        "assess whether evacuation is needed, communicate status, and contain the fire."
    ),
    "max_steps": 12,
    "situation_report": (
        "INCIDENT BRIEFING -- ICS-209 INITIAL\n"
        "Incident Name: Cedar Fire | Incident #: 2024-NF-0847\n"
        "IC: Battalion Chief Martinez | Type 3 Incident\n"
        "Date/Time: 1342 hours local\n"
        "Location: NW of Highway 89, Sections 14-15, T12N R8E, Prescott NF\n"
        "Jurisdiction: USFS / Prescott National Forest, Yavapai County\n"
        "\n"
        "SITUATION SUMMARY:\n"
        "- Fire reported at 1215 hours by Highway 89 motorist. Origin: downed power line on Forest Rd 12.\n"
        "- Current size: 120 acres, 5% contained. Spreading east in dry grass at 15 ac/hr.\n"
        "- Flat terrain, no significant topographic features accelerating spread.\n"
        "- Threats: Highway 89 corridor (~6 hr at current ROS), Pine Ranch Homes (3 structures, 12 residents, 3km east).\n"
        "\n"
        "IAP OBJECTIVES:\n"
        "1. Protect Highway 89 transportation corridor.\n"
        "2. Establish anchor point at Forest Rd 12 / Hwy 89 junction and construct direct attack line.\n"
        "3. Structure triage of Pine Ranch properties if fire advances within 1.5km.\n"
        "4. Full containment within operational period.\n"
        "\n"
        "RESOURCE STATUS: 3 crews available (Alpha, Bravo, Charlie), 1 helicopter (Hawk-1), 1 air tanker (Tanker-10).\n"
        "WEATHER: W wind 15 km/h, 34C, 22% RH. Stable high pressure. Fire Danger Rating: HIGH."
    ),
    "fires": {
        "fire_cedar": {
            "fire_id": "fire_cedar",
            "name": "Cedar Fire",
            "acres": 120.0,
            "containment_percent": 5.0,
            "spread_direction": "E",
            "spread_rate_acres_per_hour": 15.0,
            "terrain": "grassland",
            "priority": 3,
            "threats": [
                "Highway 89 corridor (major regional transport artery, ~6km east, est. 6hr at current ROS)",
                "Pine Ranch property (3 wood-frame homes, 12 residents including 2 children, 3km east, minimal defensible space)",
            ],
            "crews_assigned": [],
            "aircraft_assigned": [],
        },
    },
    "crews": {
        "crew_alpha": {
            "crew_id": "crew_alpha",
            "name": "Crew Alpha",
            "size": 20,
            "status": "available",
            "hours_on_duty": 0.0,
            "assigned_to": None,
            "location": "Station 5 (8km away, 20 min travel via Forest Rd 12)",
            "specialty": "general",
        },
        "crew_bravo": {
            "crew_id": "crew_bravo",
            "name": "Crew Bravo",
            "size": 20,
            "status": "available",
            "hours_on_duty": 0.0,
            "assigned_to": None,
            "location": "Station 12 (15km away, 35 min travel via Hwy 89)",
            "specialty": "hotshot",
        },
        "crew_charlie": {
            "crew_id": "crew_charlie",
            "name": "Crew Charlie",
            "size": 15,
            "status": "available",
            "hours_on_duty": 2.0,
            "assigned_to": None,
            "location": "Station 5 (8km away, 20 min travel)",
            "specialty": "structure_protection",
        },
    },
    "aircraft": {
        "heli_1": {
            "aircraft_id": "heli_1",
            "name": "Hawk-1",
            "aircraft_type": "helicopter",
            "status": "available",
            "water_capacity_gallons": 2600,
            "assigned_to": None,
            "location": "Airbase Delta (12 min flight time)",
        },
        "tanker_1": {
            "aircraft_id": "tanker_1",
            "name": "Tanker-10",
            "aircraft_type": "air_tanker",
            "status": "available",
            "water_capacity_gallons": 8000,
            "assigned_to": None,
            "location": "Airbase Delta (20 min flight time)",
        },
    },
    "evac_zones": {
        "zone_ranch": {
            "zone_id": "zone_ranch",
            "name": "Pine Ranch Homes",
            "population": 12,
            "distance_to_nearest_fire_km": 3.0,
            "nearest_fire": "fire_cedar",
            "is_evacuated": False,
            "has_vulnerable": False,
            "description": (
                "3 ranch homes with 12 residents (4 adults, 6 elderly, 2 children), "
                "3km east of Cedar Fire. All wood-frame construction, 1970s-era. "
                "Defensible space is minimal -- dry grass within 10m of structures. "
                "Single access road (Pine Ranch Rd) to Hwy 89. "
                "Evacuation not critical at current ROS but structure protection recommended "
                "if fire advances past 1.5km."
            ),
        },
    },
    "weather": {
        "wind_speed_kmh": 15.0,
        "wind_direction": "W",
        "temperature_celsius": 34.0,
        "humidity_percent": 22.0,
        "forecast_change": "Stable conditions expected for next 12 hours. High pressure ridge holding. Wind steady W at 10-18 km/h, RH bottoming at 18% by 1600 hours. No frontal passage or lightning risk. Overnight recovery expected with RH rising to 45% by 0400.",
        "fire_danger_rating": "high",
    },
    "budget_total": 500000.0,
    # Grading ground truth
    "correct_evacuations": [],  # Not strictly needed -- fire is 3km away
    "correct_crew_deployments": {"crew_alpha": "fire_cedar", "crew_bravo": "fire_cedar"},
    "correct_aircraft_deployments": {"heli_1": "fire_cedar"},
    "critical_actions": [
        "deploy_crew_to_cedar",
        "deploy_aircraft_to_cedar",
        "create_firebreak_highway",
        "communicate_status",
    ],
    "dangerous_action_map": {},
    "dangerous_action_descriptions": {},
    "diagnostic_info": {
        "check_fire_behavior": (
            "Cedar Fire burning in dry annual grass (fuel model GR2) with scattered blue oak. "
            "Moderate rate of spread at 15 ac/hr. Flame lengths 4-6 ft. Terrain is flat with <5% slope -- "
            "no canyon, chimney, or saddle effects. No spotting observed. "
            "Expected to reach Highway 89 right-of-way in ~6 hours at current ROS without intervention. "
            "Fire behavior analyst (FBAN) rates probability of reaching highway at 70% without suppression, "
            "dropping to <10% with 2 crews and aerial support on direct attack."
        ),
        "check_weather_detail": (
            "NWS spot forecast issued 1300 hours: Stable high pressure ridge centered over region. "
            "Surface wind W 15 km/h gusting 22 km/h. Transport wind W 20 km/h at 3000 ft. "
            "No significant wind shift expected for next 12 hours. "
            "Temperature: current 34C, max 36C by 1500. Relative humidity: current 22%, min 18% by 1600. "
            "No lightning risk. Haines Index 5 (moderate). Overnight humidity recovery to 45% by 0400 "
            "should moderate fire behavior significantly. No Red Flag Warning."
        ),
        "check_road_access": (
            "Highway 89: OPEN in both directions, no closures. CDOT aware and standing by for closure if needed. "
            "Crew access via Forest Road 12 from south: CLEAR, graded dirt, passable for all engine types. "
            "Good staging area at Hwy 89 mile marker 47 (paved pullout, 0.5 acre). "
            "Secondary staging at Pine Ranch Rd turnoff. "
            "Water tender fill site at Eagle Creek bridge (Forest Rd 12 at 2.3 mi), gravity-fed, 500 gpm."
        ),
        "check_structures": (
            "Pine Ranch -- 3 structures assessed by Engine 51 at 1305 hours:\n"
            "  Structure 1 (Johnson residence): Wood frame, comp shingle roof, NO defensible space. "
            "Dry grass to foundation. Propane tank (250 gal) on west side, 3m from house. TRIAGE: Threatened.\n"
            "  Structure 2 (Miller residence): Wood frame, metal roof, partial defensible space (mowed 15m S/E). "
            "TRIAGE: Defensible with crew.\n"
            "  Structure 3 (Barn/outbuilding): Wood frame, open sides. Low priority -- no life safety value.\n"
            "Recommend structure protection group if fire reaches 1.5km. "
            "Crew Charlie (structure protection specialty) is ideal for this assignment."
        ),
    },
}


# ======================================================================
# TASK 2 -- MEDIUM: Two Fires, Limited Resources
# ======================================================================

TASK_MEDIUM = {
    "task_id": "medium_two_fires",
    "task_description": (
        "Two active wildfires: 'Ridge Fire' (large, partially contained in forest) and 'Valley Fire' "
        "(small but threatening Oakdale town of 500 people). Resources are limited -- you have 2 crews "
        "(one fatigued) and 1 helicopter. Wind is shifting toward the town in 4 hours. "
        "Make tough resource allocation decisions, prioritize life safety, and manage the situation."
    ),
    "max_steps": 16,
    "situation_report": (
        "INCIDENT BRIEFING -- ICS-209 UPDATE #3\n"
        "Incident Name: Ridgeline Complex | Incident #: 2024-NF-1203\n"
        "IC: Division Chief Abrams | Type 2 Incident (IMT en route)\n"
        "Date/Time: 0945 hours local | Operational Period: 0600-1800\n"
        "Location: Sections 8-22, T14N R6E, Sierra NF / Oakdale Valley\n"
        "Jurisdiction: USFS Sierra NF / Butte County Fire\n"
        "\n"
        "SITUATION SUMMARY:\n"
        "- Two active fires managed as Ridgeline Complex.\n"
        "- RIDGE FIRE: 520 acres, 30% contained. Burning in mixed conifer (fuel model TL5). "
        "Slow spread north at 8 ac/hr. South containment line holding. Crew Delta on south flank since 2245 last night (11 hr).\n"
        "- VALLEY FIRE: 80 acres, 0% contained. Reported at 0830 hours, origin under investigation. "
        "Burning in dry annual grass / WUI (fuel model GR4). Rapid spread SE at 25 ac/hr. "
        "NO suppression resources currently assigned.\n"
        "- CRITICAL: NWS has issued Red Flag Warning effective 1400 hours. Wind shift from NW to W "
        "at 30 km/h forecast for ~1345 hours. This will align Valley Fire spread axis directly toward Oakdale.\n"
        "\n"
        "LIFE SAFETY THREAT:\n"
        "- Oakdale (pop. 500): 2.5km SE of Valley Fire. Includes Oakdale Elementary (120 children, in session).\n"
        "- Route 4 gas station: 12,000-gallon underground fuel storage, 1.8km from fire.\n"
        "\n"
        "IAP OBJECTIVES (Priority Order):\n"
        "1. Life safety: Protect Oakdale population. Initiate evacuation before wind shift.\n"
        "2. Incident stabilization: Suppress Valley Fire advance toward WUI.\n"
        "3. Property conservation: Maintain Ridge Fire containment.\n"
        "\n"
        "RESOURCE STATUS: 2 crews (Delta -- fatigued 11hr, Echo -- fresh), 1 helicopter (Hawk-2). "
        "No additional resources available within 4 hours. Mutual aid request recommended.\n"
        "WEATHER: NW 25 km/h, 38C, 14% RH. RED FLAG WARNING in effect. Fire Danger: VERY HIGH."
    ),
    "fires": {
        "fire_ridge": {
            "fire_id": "fire_ridge",
            "name": "Ridge Fire",
            "acres": 520.0,
            "containment_percent": 30.0,
            "spread_direction": "N",
            "spread_rate_acres_per_hour": 8.0,
            "terrain": "forest",
            "priority": 2,
            "threats": [
                "Commercial timber (est. $2.4M board-feet in fire perimeter, Sections 14-16)",
                "Critical spotted owl nesting habitat (USFWS designated, 3 known nest sites)",
                "Mountain cabins (6 seasonal structures, currently UNOCCUPIED, 4km north)",
            ],
            "crews_assigned": ["crew_delta"],
            "aircraft_assigned": [],
        },
        "fire_valley": {
            "fire_id": "fire_valley",
            "name": "Valley Fire",
            "acres": 80.0,
            "containment_percent": 0.0,
            "spread_direction": "SE",
            "spread_rate_acres_per_hour": 25.0,
            "terrain": "grassland_urban_interface",
            "priority": 3,
            "threats": [
                "Oakdale town center (500 residents, 2.5km SE, est. arrival 5hr pre-shift / 2hr post-shift)",
                "Oakdale Elementary School (120 children + 15 staff, in session, 2.8km SE)",
                "Route 4 Chevron station (12,000-gal underground fuel tanks, 1.8km SE -- explosion/HAZMAT risk)",
                "Oakdale water treatment plant (serves 3 communities, 3.2km SE)",
            ],
            "crews_assigned": [],
            "aircraft_assigned": [],
        },
    },
    "crews": {
        "crew_delta": {
            "crew_id": "crew_delta",
            "name": "Crew Delta",
            "size": 20,
            "status": "fatigued",
            "hours_on_duty": 11.0,
            "assigned_to": "fire_ridge",
            "location": "Ridge Fire south flank containment line",
            "specialty": "general",
        },
        "crew_echo": {
            "crew_id": "crew_echo",
            "name": "Crew Echo",
            "size": 20,
            "status": "available",
            "hours_on_duty": 1.0,
            "assigned_to": None,
            "location": "Station 7 (20km from Valley Fire, ~40 min travel via Route 4)",
            "specialty": "structure_protection",
        },
    },
    "aircraft": {
        "heli_2": {
            "aircraft_id": "heli_2",
            "name": "Hawk-2",
            "aircraft_type": "helicopter",
            "status": "available",
            "water_capacity_gallons": 2600,
            "assigned_to": None,
            "location": "Airbase Echo (18 min flight to Valley Fire)",
        },
    },
    "evac_zones": {
        "zone_oakdale": {
            "zone_id": "zone_oakdale",
            "name": "Oakdale Town",
            "population": 500,
            "distance_to_nearest_fire_km": 2.5,
            "nearest_fire": "fire_valley",
            "is_evacuated": False,
            "has_vulnerable": True,
            "description": (
                "Town of 500 residents including Oakdale Elementary (120 children + 15 staff, currently in session). "
                "21 residents are mobility-impaired (ADA registry). "
                "Route 4 Chevron station with 12,000-gallon underground fuel tanks sits between town and fire. "
                "Evacuation route: Route 4 south to County Fairgrounds shelter (15 min drive). "
                "School buses available (3 buses, 45 min to mobilize). "
                "Town has reverse-911 system (CodeRED) -- 4 min to reach all registered phones. "
                "Wind shifting toward town in ~4 hours -- evacuation MUST complete before shift."
            ),
        },
        "zone_cabins": {
            "zone_id": "zone_cabins",
            "name": "Mountain Cabins",
            "population": 0,
            "distance_to_nearest_fire_km": 4.0,
            "nearest_fire": "fire_ridge",
            "is_evacuated": False,
            "has_vulnerable": False,
            "description": "6 seasonal cabins, verified UNOCCUPIED by Ranger District patrol at 0730. 4km north of Ridge Fire. No immediate risk -- low priority.",
        },
    },
    "weather": {
        "wind_speed_kmh": 25.0,
        "wind_direction": "NW",
        "temperature_celsius": 38.0,
        "humidity_percent": 14.0,
        "forecast_change": (
            "RED FLAG WARNING in effect. Wind shift to westerly 28-35 km/h expected in 4-6 hours "
            "as cold front approaches from NW. This will realign Valley Fire spread axis directly toward Oakdale. "
            "Temperature rising to 42C ahead of front. RH dropping to 9% pre-frontal. "
            "Post-frontal: erratic winds 20-40 km/h for 2-3 hours, then W 15 km/h. "
            "Thunderstorms possible 12-18 hours out (dry lightning risk)."
        ),
        "fire_danger_rating": "very_high",
    },
    "budget_total": 400000.0,
    "correct_evacuations": ["zone_oakdale"],
    "correct_crew_deployments": {"crew_echo": "fire_valley"},
    "correct_aircraft_deployments": {"heli_2": "fire_valley"},
    "critical_actions": [
        "prioritize_valley_fire",
        "evacuate_oakdale",
        "deploy_crew_echo_to_valley",
        "deploy_heli_to_valley",
        "request_mutual_aid",
        "rotate_crew_delta",
        "communicate_status",
    ],
    "dangerous_action_map": {
        "deploy_fatigued_crew_without_rotation": "Crew Delta has been on duty 11 hours. Deploying them to a new fire without rest risks crew injury. Safety violation.",
        "ignore_evacuation": "Oakdale has 500 residents including 120 children. Wind is shifting toward town. Not evacuating before wind shift puts lives at extreme risk.",
        "prioritize_ridge_over_valley": "Ridge Fire threatens timber and empty cabins. Valley Fire threatens 500 lives. Prioritizing property over people is the wrong call.",
    },
    "dangerous_action_descriptions": {
        "deploy_fatigued_crew_without_rotation": (
            "WHY THIS IS DANGEROUS: NWCG standards and OSHA 29 CFR 1910.266 limit wildfire crew shifts to 12-16 hours "
            "with mandatory rest. Crew Delta at 11 hours is approaching the hard limit. Fatigued firefighters have "
            "slower reaction times, impaired judgment, and higher injury rates. The 2013 Yarnell Hill tragedy and "
            "2001 Thirtymile Fire both involved crew fatigue as contributing factors. Rotating them is not optional -- "
            "it is a life-safety requirement for the crew themselves."
        ),
        "ignore_evacuation": (
            "WHY THIS IS DANGEROUS: With a confirmed wind shift in 4 hours, the Valley Fire arrival time at Oakdale "
            "drops from 5 hours to approximately 2 hours post-shift. Evacuation requires ~2 hours for a town of 500. "
            "This means the evacuation window closes AT the wind shift -- any delay past that point traps residents. "
            "120 children are in school session. 21 residents are mobility-impaired. This is a zero-margin situation."
        ),
        "prioritize_ridge_over_valley": (
            "WHY THIS IS DANGEROUS: ICS doctrine (NIMS) mandates Life Safety > Incident Stabilization > Property Conservation. "
            "Ridge Fire threatens $2.4M in timber and empty cabins. Valley Fire threatens 500 human lives. "
            "Sending the only fresh crew (Echo) or the only helicopter to Ridge Fire while Valley Fire advances "
            "on a populated town is an inversion of priorities that could result in mass casualties."
        ),
    },
    "diagnostic_info": {
        "check_valley_fire_behavior": (
            "Valley Fire burning in dry annual grass with continuous fine fuels (fuel model GR4). "
            "Rate of spread: 25 ac/hr, flame lengths 6-10 ft. Running SE with NW wind. "
            "At current ROS, fire front reaches Oakdale outskirts (~2.5km) in approximately 5 hours. "
            "CRITICAL: After forecast wind shift to W at 30 km/h (in ~4 hours), fire spread axis realigns "
            "directly toward Oakdale. Estimated post-shift ROS: 40 ac/hr. Post-shift arrival at Oakdale: "
            "~2 hours (cumulative ~6 hours from now but only 2 hours after the shift). "
            "Route 4 gas station (12,000-gal fuel) in direct fire path at 1.8km. "
            "FBAN recommends immediate evacuation and aggressive aerial suppression before wind shift."
        ),
        "check_ridge_fire_behavior": (
            "Ridge Fire: 520 acres, 30% contained. Burning in mixed conifer (fuel model TL5) at 8 ac/hr. "
            "South flank containment line: HOLDING with Crew Delta on direct attack. Dozer line 80% complete. "
            "North flank: fire backing downhill at 2 ac/hr, minimal threat. "
            "If Crew Delta is pulled for rotation, south containment line will be unmanned. "
            "Estimated time to loss of south line without crew: 3-4 hours. "
            "However, fire spread north threatens ONLY timber and unoccupied cabins -- no life safety implications. "
            "Acceptable risk to pull Crew Delta for rotation and allow south line to potentially fail."
        ),
        "check_evacuation_routes": (
            "OAKDALE EVACUATION PLAN:\n"
            "- Primary route: Route 4 SOUTH to County Fairgrounds emergency shelter (15 min drive, 800 capacity).\n"
            "- Route 4 is currently OPEN. CDOT pre-positioned for closure/contraflow if needed.\n"
            "- School buses: 3 available at Oakdale Elementary, 45 min mobilization. Can transport 120 children in one trip.\n"
            "- ADA transport: County paratransit has 2 wheelchair vans, 30 min response. 21 mobility-impaired residents on registry.\n"
            "- Reverse-911 (CodeRED): 4 minutes to reach all registered phones. 87% registration rate.\n"
            "- Total evacuation time estimate: 2 hours for full town.\n"
            "- HAZMAT note: Route 4 Chevron station must be shut down and isolated during evacuation. "
            "Notify Chevron district manager and County HAZMAT team. Underground tanks rated for fire exposure "
            "but vapor release from vents is the primary risk."
        ),
        "check_mutual_aid": (
            "MUTUAL AID AVAILABILITY (per dispatch query at 0930):\n"
            "- County 12 (Mariposa): 2 Type 1 hand crews (20-person each). Response time: 4 hours via Hwy 140.\n"
            "- County 8 (Tuolumne): 1 Type 2 IA crew (18-person). Response time: 6 hours.\n"
            "- CAL FIRE Madera Unit: 1 bulldozer + operator. Response time: 3 hours.\n"
            "- State Mobilization Center (Sacramento): Can activate Type 1 IMT. ETA: 8-12 hours.\n"
            "- Note: All mutual aid requests go through Butte County EOC. Estimated processing time: 30 min.\n"
            "RECOMMENDATION: Request County 12 crews immediately -- they arrive just as wind shift occurs "
            "and can relieve or augment suppression."
        ),
        "check_crew_delta_fatigue": (
            "Crew Delta fatigue assessment (Safety Officer Reyes, 0920 hours):\n"
            "- On duty since 2245 last night (11 consecutive hours). Arrived at Ridge Fire south flank at 2330.\n"
            "- Crew has been on direct attack in steep terrain, Class 3 workload.\n"
            "- 3 members reporting significant fatigue. 1 member (Firefighter Orozco) treated for mild heat exhaustion at 0800.\n"
            "- Crew Superintendent confirms diminished production in last 2 hours.\n"
            "- Per NWCG PMS 310-1 and agency fatigue management guidelines: ROTATION RECOMMENDED.\n"
            "- Hard safety limit: 16 hours (crew reaches this at 1445 today). Performance drop-off is nonlinear after 12 hours.\n"
            "- Redeployment to a NEW fire assignment at 11 hours would be a SAFETY VIOLATION (ref: OSHA 29 CFR 1910.266)."
        ),
    },
}


# ======================================================================
# TASK 3 -- HARD: Cascading Disaster
# ======================================================================

TASK_HARD = {
    "task_id": "hard_cascading_disaster",
    "task_description": (
        "CRITICAL SITUATION: Three active wildfires with cascading threats. "
        "Fire X near power lines (media/political pressure), "
        "Fire Y threatening a school and hospital, "
        "Fire Z appears small and remote but is heading toward a gas pipeline. "
        "You have 2 crews (1 fatigued), 1 helicopter (1 in maintenance), and almost no budget. "
        "Wind shifts 3 times in 12 hours. Red herrings and political pressure will test your judgment. "
        "Lives depend on correct prioritization and sequencing."
    ),
    "max_steps": 20,
    "situation_report": (
        "INCIDENT BRIEFING -- ICS-209 UPDATE #7 -- PRIORITY TRAFFIC\n"
        "Incident Name: Maplewood Complex | Incident #: 2024-NF-2891\n"
        "IC: Deputy Chief Vasquez (acting) | Type 1 Incident -- IMT ordered, ETA 8 hrs\n"
        "Date/Time: 1130 hours local | Operational Period: 0600-1800\n"
        "Location: Sections 4-28, T16N R4E, Angeles NF / Maplewood Valley\n"
        "Jurisdiction: USFS Angeles NF / LA County Fire / City of Maplewood\n"
        "\n"
        "SITUATION SUMMARY -- 3 ACTIVE FIRES:\n"
        "\n"
        "FIRE X -- Powerline Fire: 950 ac, 15% contained. Burning E in mixed conifer at 12 ac/hr. "
        "SCE has de-energized Transmission Line 220 (500kV). 50,000 residential customers without power. "
        "Media and political pressure INTENSE -- County Commissioner demanding resources. "
        "NO LIVES AT IMMEDIATE RISK. This is a property/infrastructure incident.\n"
        "\n"
        "FIRE Y -- Hillside Fire: 200 ac, 0% contained. Burning S through Maplewood Canyon toward populated area. "
        "Canyon effect producing extreme fire behavior. ROS 30 ac/hr, flame lengths 20-40 ft. "
        "DIRECT THREAT TO LIFE: Maplewood Elementary (180 children in session, 1.8km), "
        "St. Mary's Hospital (45 patients incl. 12 ICU/3 ventilator, 2.2km), "
        "Sunset Senior Living (60 elderly, 2.5km), Hillcrest neighborhood (2,400 residents, 3.5km). "
        "NO suppression resources assigned. ZERO PERCENT CONTAINMENT.\n"
        "\n"
        "FIRE Z -- Creek Fire: 45 ac, 0% contained. Appears minor -- remote brush, 10 ac/hr NE. "
        "Initial assessment: low priority. NOTE: Agent should investigate further.\n"
        "\n"
        "RESOURCE STATUS -- CRITICALLY LIMITED:\n"
        "- Crew Foxtrot: 20-person structure protection, AVAILABLE (2 hr on duty), Station 3\n"
        "- Crew Golf: 18-person hotshot, FATIGUED (13 hr on duty, 1 heat casualty), returning from prior assignment\n"
        "- Hawk-3: Helicopter, AVAILABLE, Airbase Foxtrot\n"
        "- Hawk-4: Helicopter, IN MAINTENANCE (est. 3 hr to available), Airbase Foxtrot\n"
        "- Budget: $50,000 remaining of $500,000 allocation. Requesting emergency supplemental.\n"
        "\n"
        "WEATHER -- EXTREME CONDITIONS:\n"
        "N wind 30 km/h, 42C, 8% RH. THREE wind shifts forecast in next 12 hours. "
        "Fire Danger Rating: EXTREME. Red Flag Warning ACTIVE.\n"
        "\n"
        "IC ASSESSMENT: This incident exceeds current resource capability. "
        "Life safety is the SOLE priority. Request mutual aid and state/federal mobilization immediately.\n"
        "ALL decisions must follow ICS priority doctrine: 1) Life Safety, 2) Incident Stabilization, 3) Property."
    ),
    "fires": {
        "fire_x": {
            "fire_id": "fire_x",
            "name": "Powerline Fire",
            "acres": 950.0,
            "containment_percent": 15.0,
            "spread_direction": "E",
            "spread_rate_acres_per_hour": 12.0,
            "terrain": "forest",
            "priority": 2,
            "threats": [
                "SCE Transmission Line 220 (500kV, de-energized) -- 50,000 residential customers without power",
                "Media/political pressure -- 3 news helicopters overhead, County Commissioner demanding priority allocation",
                "Commercial timber ($4.1M est. value, Sections 8-12, private/USFS mixed ownership)",
                "SCE Substations Echo and Foxtrot ($28M replacement value, 1.2km and 2.8km east of fire perimeter)",
            ],
            "crews_assigned": [],
            "aircraft_assigned": [],
        },
        "fire_y": {
            "fire_id": "fire_y",
            "name": "Hillside Fire",
            "acres": 200.0,
            "containment_percent": 0.0,
            "spread_direction": "S",
            "spread_rate_acres_per_hour": 30.0,
            "terrain": "canyon_urban_interface",
            "priority": 2,
            "threats": [
                "Maplewood Elementary School (180 children + 22 staff, IN SESSION, 1.8km south -- est. 2.5 hr at current ROS, <1 hr after wind shift)",
                "St. Mary's Hospital (45 patients: 12 ICU, 3 on mechanical ventilators, 15 post-surgical, 15 general; 50 staff on duty; 2.2km south)",
                "Sunset Senior Living (60 residents: 23 wheelchair-bound, 8 with dementia requiring 1:1 escort, 14 on supplemental oxygen; 2.5km south)",
                "Hillcrest residential neighborhood (800 single-family homes, ~2,400 residents, 3.5km south -- not immediate but SET WARNING status)",
            ],
            "crews_assigned": [],
            "aircraft_assigned": [],
        },
        "fire_z": {
            "fire_id": "fire_z",
            "name": "Creek Fire",
            "acres": 45.0,
            "containment_percent": 0.0,
            "spread_direction": "NE",
            "spread_rate_acres_per_hour": 10.0,
            "terrain": "brush",
            "priority": 4,
            "threats": ["Remote forest land (BLM, no structures, no recreation sites in use)"],
            "crews_assigned": [],
            "aircraft_assigned": [],
        },
    },
    "crews": {
        "crew_foxtrot": {
            "crew_id": "crew_foxtrot",
            "name": "Crew Foxtrot",
            "size": 20,
            "status": "available",
            "hours_on_duty": 2.0,
            "assigned_to": None,
            "location": "Station 3 (15km from Hillside Fire, ~30 min travel via Canyon Rd)",
            "specialty": "structure_protection",
        },
        "crew_golf": {
            "crew_id": "crew_golf",
            "name": "Crew Golf",
            "size": 18,
            "status": "fatigued",
            "hours_on_duty": 13.0,
            "assigned_to": None,
            "location": "Returning from Arrowhead Fire assignment, currently at Station 9 rest area",
            "specialty": "hotshot",
        },
    },
    "aircraft": {
        "heli_3": {
            "aircraft_id": "heli_3",
            "name": "Hawk-3",
            "aircraft_type": "helicopter",
            "status": "available",
            "water_capacity_gallons": 2600,
            "assigned_to": None,
            "location": "Airbase Foxtrot (15 min flight to Hillside Fire, 22 min to Creek Fire)",
        },
        "heli_4": {
            "aircraft_id": "heli_4",
            "name": "Hawk-4",
            "aircraft_type": "helicopter",
            "status": "maintenance",
            "water_capacity_gallons": 2600,
            "assigned_to": None,
            "location": "Airbase Foxtrot -- tail rotor gearbox inspection (maintenance, estimated available in 3 hours)",
        },
    },
    "evac_zones": {
        "zone_school": {
            "zone_id": "zone_school",
            "name": "Maplewood School Area",
            "population": 180,
            "distance_to_nearest_fire_km": 1.8,
            "nearest_fire": "fire_y",
            "is_evacuated": False,
            "has_vulnerable": True,
            "description": (
                "Maplewood Elementary School: 180 children (grades K-5, ages 5-11) + 22 staff. "
                "School is IN SESSION. Principal Dr. Okonkwo notified and standing by for evacuation order. "
                "Fire approaching from Maplewood Canyon to the north -- canyon funneling effect producing "
                "extreme ROS. Distance: 1.8km at last observation (1115 hours). "
                "SINGLE evacuation route: Elm Street south to Maplewood Blvd. "
                "Elm Street is a 2-lane road -- capacity constraint during evacuation. "
                "3 school buses on-site but drivers not present -- dispatch required (45 min mobilization). "
                "ALTERNATE: Maplewood PD can provide 4 patrol cars for immediate small-group transport. "
                "Reunification point: Maplewood Community Center (4km south). "
                "THIS IS THE HIGHEST PRIORITY EVACUATION -- children cannot self-evacuate."
            ),
        },
        "zone_hospital": {
            "zone_id": "zone_hospital",
            "name": "St. Mary's Hospital",
            "population": 95,
            "distance_to_nearest_fire_km": 2.2,
            "nearest_fire": "fire_y",
            "is_evacuated": False,
            "has_vulnerable": True,
            "description": (
                "St. Mary's Hospital: 45 patients + 50 staff on duty. "
                "Patient breakdown: 12 ICU (3 on mechanical ventilators -- transport requires dedicated ambulance + RT each), "
                "15 post-surgical (6 non-ambulatory), 15 general medical, 3 pediatric. "
                "Hospital Incident Commander (Dr. Patel) has activated facility evacuation plan (HICS Level 3). "
                "2.2km from Hillside Fire. "
                "PRIMARY evacuation route: Hospital Dr to Oak Ave south. "
                "CRITICAL: Oak Ave bridge over Maplewood Creek is weight-restricted (15 tons) -- "
                "standard ambulances OK but heavy rescue apparatus cannot cross. "
                "Receiving facility: Valley General Hospital, 45 min transport. "
                "Valley General confirms capacity for 30 patients; overflow to County Medical Center (1.5 hr transport). "
                "Estimated full evacuation time: 3 hours minimum. Ventilator patients most critical -- "
                "battery backup provides 4 hours, must maintain power chain during transport."
            ),
        },
        "zone_senior": {
            "zone_id": "zone_senior",
            "name": "Sunset Senior Living",
            "population": 60,
            "distance_to_nearest_fire_km": 2.5,
            "nearest_fire": "fire_y",
            "is_evacuated": False,
            "has_vulnerable": True,
            "description": (
                "Sunset Senior Living: 60 elderly residents. "
                "Mobility profile: 23 wheelchair-bound, 15 ambulatory with walker/cane, "
                "14 on supplemental oxygen (concentrators -- need vehicle power adapters), "
                "8 with dementia/cognitive impairment requiring 1:1 escort, 22 fully ambulatory. "
                "Facility has 1 transport van (8 passengers). "
                "2.5km from Hillside Fire. Evacuation route: Sunset Dr to Maplewood Blvd south. "
                "Receiving facility: Pinecrest Senior Care (25 min drive, 40 bed capacity) "
                "and Maplewood Community Center (overflow, cots available). "
                "Estimated evacuation time: 2.5 hours with external transport support. "
                "Facility administrator (Ms. Chen) requests National Guard or paratransit assistance."
            ),
        },
        "zone_residential": {
            "zone_id": "zone_residential",
            "name": "Hillcrest Neighborhood",
            "population": 2400,
            "distance_to_nearest_fire_km": 3.5,
            "nearest_fire": "fire_y",
            "is_evacuated": False,
            "has_vulnerable": False,
            "description": (
                "Hillcrest residential neighborhood: 800 homes, ~2,400 residents. "
                "3.5km from Hillside Fire -- not in immediate danger at current ROS. "
                "Issue SET (evacuation warning) status. Residents should prepare to leave. "
                "Multiple evacuation routes available (Hillcrest Ave, Maple Dr, Route 7). "
                "Community has Firewise USA designation -- defensible space generally good. "
                "If fire breaches 2km perimeter, upgrade to GO (mandatory evacuation). "
                "Maplewood PD can manage traffic control for orderly evacuation."
            ),
        },
    },
    "weather": {
        "wind_speed_kmh": 30.0,
        "wind_direction": "N",
        "temperature_celsius": 42.0,
        "humidity_percent": 8.0,
        "forecast_change": (
            "EXTREME / RED FLAG WARNING ACTIVE -- Multiple wind shifts expected:\n"
            "  Shift 1 (T+2 hr): Wind NE 30-40 km/h. Accelerates Hillside Fire toward school/hospital. "
            "Canyon channeling will amplify effective wind speed to 50+ km/h at fire front.\n"
            "  Shift 2 (T+6 hr): Wind E 20-28 km/h. Brief moderation. Hillside Fire spread axis shifts SSW.\n"
            "  Shift 3 (T+10 hr): Wind SE 28-35 km/h. CRITICAL -- pushes Creek Fire directly toward "
            "TransCo gas pipeline corridor. Creek Fire ROS expected to double.\n"
            "Temperature: Holding at 42C through 1800, dropping to 38C overnight.\n"
            "Humidity: Dropping to 5% by 1400 (critical fire weather). Recovery to 15% overnight.\n"
            "Haines Index: 6 (HIGH -- extreme plume-dominated fire behavior possible).\n"
            "NO precipitation expected for 7 days."
        ),
        "fire_danger_rating": "extreme",
    },
    "budget_total": 500000.0,
    "budget_start": 50000.0,  # Almost depleted
    "correct_evacuations": ["zone_school", "zone_hospital", "zone_senior"],
    "correct_crew_deployments": {"crew_foxtrot": "fire_y"},
    "correct_aircraft_deployments": {"heli_3": "fire_y"},
    "critical_actions": [
        "evacuate_school_immediately",
        "evacuate_hospital",
        "evacuate_senior_living",
        "deploy_crew_foxtrot_to_hillside",
        "deploy_heli_to_hillside",
        "discover_pipeline_threat",
        "communicate_pipeline_to_gas_company",
        "request_mutual_aid",
        "do_not_deploy_fatigued_crew",
        "ignore_political_pressure",
        "communicate_status",
    ],
    "dangerous_action_map": {
        "deploy_fatigued_crew_golf": "Crew Golf has been on duty 13 hours -- PAST safety limit. Deploying them risks severe injury or death. MUST rest first.",
        "prioritize_powerline_fire": "Politician/media pressure says Powerline Fire is most important (50K homes without power). But Fire Y threatens LIVES (school, hospital). Power can be restored; lives cannot.",
        "set_backfire_near_hospital": "Setting a backfire near St. Mary's Hospital creates smoke that endangers ICU patients on ventilators. This could kill patients.",
        "ignore_creek_fire": "Creek Fire seems low priority (remote forest) but weather forecast shows wind shifting SE in 10 hours -- fire will reach the TransCo gas pipeline (explosion risk). Must alert gas company.",
        "deploy_all_to_powerline": "Sending all resources to Powerline Fire means Hillside Fire reaches school/hospital unopposed. Catastrophic outcome.",
    },
    "dangerous_action_descriptions": {
        "deploy_fatigued_crew_golf": (
            "WHY THIS IS DANGEROUS: Crew Golf has been on continuous duty for 13 hours -- exceeding the NWCG "
            "work/rest guideline of 2:1 ratio (16 hr max with mandatory 8 hr rest). One crew member was already "
            "treated for heat exhaustion. At 42C and 8% RH with Class 4 workload (canyon firefighting), the risk "
            "of heat stroke, cardiac events, and impaired decision-making is extreme. The 1994 South Canyon Fire "
            "(14 fatalities) and 2013 Yarnell Hill Fire (19 fatalities) both involved crews operating beyond "
            "safe fatigue limits. Deploying Crew Golf is not just a policy violation -- it is potentially lethal "
            "to the crew."
        ),
        "prioritize_powerline_fire": (
            "WHY THIS IS DANGEROUS: The Powerline Fire is the loudest incident (media, politician) but NOT the most "
            "dangerous. SCE has already de-energized the lines (no electrocution risk). Hospitals and critical "
            "facilities have backup generators. 50,000 homes without power is an inconvenience, not a life threat. "
            "Meanwhile, Hillside Fire is 0% contained, moving at 30 ac/hr through a canyon toward 180 children, "
            "45 hospital patients (3 on ventilators), and 60 elderly residents. Diverting the ONLY available crew "
            "and helicopter to Powerline Fire condemns these populations. ICS doctrine is unambiguous: "
            "Life Safety > Incident Stabilization > Property Conservation. Power outages are property."
        ),
        "set_backfire_near_hospital": (
            "WHY THIS IS DANGEROUS: Backfires produce dense smoke (PM2.5 levels >500 ug/m3) within 1-2km. "
            "St. Mary's Hospital has 3 patients on mechanical ventilators and 14 on supplemental oxygen. "
            "Smoke infiltration into the hospital HVAC system would be immediately life-threatening to these "
            "patients. Even ambulatory patients and staff would be at risk. Hospital HVAC is not HEPA-filtered. "
            "Additionally, backfires require experienced burn boss oversight and a safety zone -- neither is "
            "available near the hospital. An escaped backfire would accelerate the threat."
        ),
        "ignore_creek_fire": (
            "WHY THIS IS DANGEROUS: Creek Fire appears to be a low-priority 45-acre brush fire in remote BLM land. "
            "However, the TransCo Pipeline LP-7 (24-inch, 800 PSI high-pressure natural gas transmission line) "
            "runs 6km NE of the current fire position. The weather forecast calls for wind shifting SE at T+10 hours, "
            "which would push the fire directly toward the pipeline corridor. At post-shift ROS of ~20 ac/hr, fire "
            "reaches the pipeline in approximately 3 hours after the shift. The pipeline emergency shutoff requires "
            "a 2-hour sequence -- meaning the gas company must be notified BEFORE the wind shift to have any chance "
            "of safe shutdown. A pipeline rupture and ignition at 800 PSI would produce a jet fire with a 5km "
            "lethal thermal radiation zone. Federal regulation (49 CFR 192) requires notification of any fire "
            "within 3km of a transmission pipeline. This is a HIDDEN threat that requires investigation to discover."
        ),
        "deploy_all_to_powerline": (
            "WHY THIS IS DANGEROUS: With only 1 available crew (Foxtrot) and 1 available helicopter (Hawk-3), "
            "sending both to the Powerline Fire leaves the Hillside Fire completely uncontested. Hillside Fire is "
            "0% contained, burning through a canyon at 30 ac/hr (doubling after wind shift), and heading directly "
            "toward 180 children, 45 hospital patients, and 60 elderly residents. Without any suppression or "
            "evacuation support, the fire reaches the school in under 3 hours. This would be a mass-casualty event."
        ),
    },
    "diagnostic_info": {
        "check_hillside_fire_behavior": (
            "Hillside Fire FBAN Assessment (FBAN Rodriguez, 1100 hours):\n"
            "Fire burning through Maplewood Canyon -- steep V-shaped canyon, 60% slopes, south aspect. "
            "Classic canyon fire behavior: pre-heating of upslope fuels, convective column tilting downcanyon. "
            "Fuel model SH7 (heavy brush, manzanita/chamise). Current ROS: 30 ac/hr. Flame lengths: 20-40 ft. "
            "Spotting observed up to 0.5 km ahead of main front.\n"
            "\n"
            "TIMELINE (from current position):\n"
            "- T+0 to T+2 hr (current wind N 30 km/h): Fire advances S through canyon. Est. ROS 30 ac/hr. "
            "Distance to school: 1.8km. Arrival at school: ~2.5 hours.\n"
            "- T+2 hr (wind shift to NE 35 km/h): Canyon channeling amplifies to 50+ km/h effective. "
            "ROS doubles to 60 ac/hr. Spotting increases to 1km. Fire becomes wind-driven. "
            "Revised school arrival: <1 hour after shift (cumulative ~3 hours from now).\n"
            "- T+3 hr: Fire reaches school zone. T+3.5 hr: Hospital zone. T+4 hr: Senior living zone.\n"
            "\n"
            "FBAN RECOMMENDATION: This fire WILL reach populated areas. Suppression alone cannot stop it "
            "in current conditions. EVACUATE ALL VULNERABLE POPULATIONS IMMEDIATELY. Use aerial suppression "
            "to slow advance and buy evacuation time only."
        ),
        "check_creek_fire_detail": (
            "Creek Fire field recon (Engine 74 drive-by, 1045 hours):\n"
            "45 acres in chamise/sage brush, burning NE at 10 ac/hr. No structures threatened. "
            "Appears to be low-priority -- remote BLM land, no recreation sites in use.\n"
            "\n"
            "*** HIDDEN THREAT -- REQUIRES INVESTIGATION TO DISCOVER ***\n"
            "TransCo Gas Pipeline LP-7 runs through the terrain 6km NE of current fire position. "
            "Pipeline specs: 24-inch diameter, high-pressure natural gas transmission line, "
            "operating pressure 800 PSI (MAOP 1000 PSI). Steel, 1987 vintage, last inline inspection 2021. "
            "Pipeline feeds the San Joaquin regional distribution network (220,000 customers).\n"
            "\n"
            "TIMELINE:\n"
            "- Current: Fire 6km from pipeline, moving NE at 10 ac/hr. Arrival: ~8 hours on current heading.\n"
            "- T+10 hr (wind shift to SE 30 km/h): Fire spread redirects. ROS increases to 20 ac/hr. "
            "Fire-to-pipeline distance along new heading: ~4km. Arrival: ~3 hours after shift (T+13 hr total).\n"
            "- Pipeline emergency shutoff at TransCo Station 12: requires 2-HOUR controlled shutdown sequence "
            "(gradual pressure reduction to prevent water hammer). MUST be initiated BEFORE fire reaches 3km proximity.\n"
            "- Federal regulation 49 CFR 192.615 requires operator notification of any fire within 3km of "
            "transmission pipeline. TransCo Emergency Control Center: must be contacted.\n"
            "\n"
            "FAILURE SCENARIO: Pipeline rupture + ignition produces high-pressure jet fire. "
            "Thermal radiation lethal zone: 300m. Potential BLEVE if pipe segment isolated with gas trapped: "
            "blast radius 500m, thermal 1.5km. Wildfire + pipeline fire interaction could affect 5km radius."
        ),
        "check_powerline_fire_detail": (
            "Powerline Fire assessment (Division Alpha Supervisor Keane, 1100 hours):\n"
            "950 acres, 15% contained. Burning in mixed conifer (TL3/TL5 fuel models) at 12 ac/hr. "
            "Moderate fire behavior -- surface fire with occasional torching of individual trees. No crown run.\n"
            "\n"
            "INFRASTRUCTURE STATUS:\n"
            "- SCE Transmission Line 220 (500kV): DE-ENERGIZED at 0600 hours. No electrocution hazard. "
            "SCE repair crew staged but cannot access until fire is 1km from lines.\n"
            "- 50,000 residential customers without power. SCE activated rolling backup plan.\n"
            "- All hospitals, water treatment, and traffic signals on backup generator power.\n"
            "- SCE estimates 48-72 hour restoration once fire clears corridor.\n"
            "\n"
            "POLITICAL SITUATION:\n"
            "County Commissioner Rodriguez called IC at 0915 and 1045 demanding resource priority. "
            "3 news helicopters and 2 ground camera crews at Powerline Fire. CNN, local affiliates broadcasting live. "
            "Commissioner's office issued press release calling fire response 'inadequate.'\n"
            "\n"
            "TACTICAL ASSESSMENT: This fire is NOT a life-safety threat. It is a significant economic/political "
            "incident but should be deprioritized relative to Hillside Fire. Containment lines on west flank "
            "are holding. Eastern spread toward substations is slow (12 ac/hr in timber). "
            "Substations have fire-resistant perimeter clearing (100ft). "
            "RECOMMENDATION: Maintain monitoring only. Assign mutual aid resources when they arrive in 5 hours."
        ),
        "check_hospital_evacuation": (
            "Hospital Evacuation Assessment (EMS Battalion Chief Nakamura, 1110 hours):\n"
            "St. Mary's Hospital -- HICS Level 3 activated. Dr. Patel (Hospital IC) coordinating.\n"
            "\n"
            "PATIENT MANIFEST:\n"
            "- ICU (12 patients): 3 on mechanical ventilators (battery backup: 4 hours each), "
            "4 on IV drips with pumps, 5 on continuous cardiac monitoring. Each ventilator patient requires "
            "dedicated ambulance + respiratory therapist.\n"
            "- Post-surgical (15 patients): 6 non-ambulatory (recent hip/knee), 9 ambulatory with assistance.\n"
            "- General medical (15 patients): 12 ambulatory, 3 on supplemental O2.\n"
            "- Pediatric (3 patients): 2 ambulatory, 1 infant in NICU-lite (portable isolette available).\n"
            "\n"
            "TRANSPORT REQUIREMENTS:\n"
            "- 3 ALS ambulances for ventilator patients (County has 2 available, mutual aid for 3rd -- ETA 45 min)\n"
            "- 2 BLS ambulances for non-ambulatory surgical patients\n"
            "- 5 wheelchair transport vans for remaining non-ambulatory\n"
            "- 2 buses for ambulatory patients + staff\n"
            "\n"
            "ROUTE ISSUE: Primary evacuation route (Hospital Dr to Oak Ave south) crosses "
            "Maplewood Creek bridge -- WEIGHT RESTRICTED to 15 tons. Standard ambulances (10 ton) OK. "
            "Heavy rescue apparatus (22 ton) CANNOT cross. Alternate route via Elm Street adds 20 minutes "
            "but has no restrictions.\n"
            "\n"
            "RECEIVING FACILITIES:\n"
            "- Valley General Hospital (45 min): Accepts 30 patients (8 ICU beds available)\n"
            "- County Medical Center (1.5 hr): Overflow, unlimited capacity but longer transport\n"
            "\n"
            "ESTIMATED FULL EVACUATION TIME: 3 hours minimum (ICU patients first, 45 min per round trip).\n"
            "CRITICAL: Start evacuation NOW. Every 30-minute delay compresses margin against fire arrival."
        ),
        "check_crew_golf_status": (
            "Crew Golf Safety Assessment (Safety Officer Dominguez, 1115 hours):\n"
            "\n"
            "DUTY HISTORY:\n"
            "- On duty since 2230 last night (Arrowhead Fire assignment, 42 km away).\n"
            "- Total continuous duty: 13 hours. Exceeded 2:1 work/rest guideline (12 hr work requires 6 hr rest).\n"
            "- Crew completed 8 hours of Class 4 workload (direct attack, steep terrain) before demob.\n"
            "- Currently at Station 9 rest area. Crew Superintendent Flores reports crew 'spent.'\n"
            "\n"
            "MEDICAL STATUS:\n"
            "- FF2 Gutierrez: Treated for heat exhaustion at 0930 (IV fluids administered, resting). NOT FIT for duty.\n"
            "- FF1 Park: Reported ankle pain from stumble on steep terrain. Walking but limited.\n"
            "- Remaining 16 members: Fatigued but no medical issues reported.\n"
            "\n"
            "SAFETY OFFICER DETERMINATION:\n"
            "Per NWCG PMS 310-1 and OSHA 29 CFR 1910.266: Crew Golf is NOT deployable. "
            "Minimum 10-hour rest period required before ANY new assignment. "
            "Crew can be available at approximately 2130 hours tonight (earliest).\n"
            "Deploying this crew in current conditions (42C, 8% RH, extreme fire behavior) "
            "would constitute a WILLFUL SAFETY VIOLATION. Ref: NWCG Accident Investigation findings "
            "from South Canyon (1994) and Esperanza (2006) -- fatigue cited as contributing factor.\n"
            "\n"
            "RECOMMENDATION: Allow Crew Golf full rest cycle. They will be fresh and available "
            "for the next operational period (1800 hours onward)."
        ),
        "check_political_situation": (
            "Political/Media Situation Brief (PIO Martinez, 1120 hours):\n"
            "\n"
            "MEDIA PRESENCE:\n"
            "- CNN live broadcast from Powerline Fire overlook (satellite truck at MM 14, Highway 138)\n"
            "- KABC, KNBC, KCBS ground crews at Powerline Fire perimeter\n"
            "- 3 news helicopters orbiting Powerline Fire (HAZARD: deconfliction with firefighting aircraft)\n"
            "- Social media trending: #PowerlineFire, #MayorDoSomething, #50KWithoutPower\n"
            "- NOTE: Media has NOT yet discovered Hillside Fire threat to school/hospital. "
            "When they do, narrative will shift dramatically.\n"
            "\n"
            "POLITICAL PRESSURE:\n"
            "- County Commissioner Rodriguez: 2 phone calls to IC (0915, 1045) demanding 'all available resources' "
            "on Powerline Fire. Threatened to 'go to the Governor' if power not restored by tonight.\n"
            "- SCE CEO called County CAO requesting priority. CAO relayed to Fire Chief.\n"
            "- City of Maplewood mayor (Hillside Fire area) has NOT been briefed yet.\n"
            "\n"
            "IC GUIDANCE:\n"
            "This is a TACTICAL decision, not a political one. ICS-209 priority doctrine is clear: "
            "Life Safety first. Commissioner Rodriguez does not have tactical authority. "
            "Document all contacts in ICS-214 Unit Log. PIO will handle media messaging.\n"
            "DO NOT divert life-safety resources to satisfy political pressure. "
            "If questioned: 'We are prioritizing the protection of human life in accordance with ICS doctrine.'"
        ),
        "check_mutual_aid_options": (
            "Mutual Aid Availability (Dispatch Coordinator Williams, 1125 hours):\n"
            "\n"
            "IMMEDIATE (via County EOC):\n"
            "- LA County Fire: 2 Type 1 strike teams (5 engines each). ETA: 3 hours via I-5.\n"
            "- National Guard 40th Infantry Division: 2 CH-47 Chinook helicopters for evacuation support "
            "(20 litter patients or 33 ambulatory per aircraft). ETA: 3 hours from Los Alamitos.\n"
            "- CAL FIRE San Bernardino Unit: 1 air attack + 2 air tankers (4,000 gal each). ETA: 2 hours.\n"
            "\n"
            "STATE MOBILIZATION CENTER (Sacramento):\n"
            "- 3 Type 1 hand crews (20-person) + 2 Type 2 helicopters. ETA: 5 hours.\n"
            "- Type 1 Incident Management Team (Soberanes Team). ETA: 8-12 hours.\n"
            "\n"
            "FEDERAL (NIFC Boise):\n"
            "- 2 VLAT (DC-10, 12,000 gal retardant each). Currently committed -- request queued.\n"
            "\n"
            "REQUEST PROCESS: All requests through County EOC (Coordinator Williams). "
            "State resources require ROSS order. Federal resources require NIFC prioritization.\n"
            "\n"
            "RECOMMENDATION: Request EVERYTHING immediately. National Guard for evacuation support (3 hr), "
            "CAL FIRE air tankers for Hillside Fire suppression (2 hr), state hand crews for sustained ops (5 hr). "
            "Do not wait -- lead times are long and situation is deteriorating."
        ),
        "check_pipeline_detail": (
            "TransCo Pipeline LP-7 Infrastructure Detail:\n"
            "\n"
            "PIPELINE SPECIFICATIONS:\n"
            "- Operator: TransCo Energy, Western Division\n"
            "- Designation: LP-7 (Los Padres Lateral 7)\n"
            "- Diameter: 24-inch\n"
            "- Material: API 5L X65 steel, fusion-bonded epoxy coating\n"
            "- Operating pressure: 800 PSI (MAOP: 1,000 PSI)\n"
            "- Product: High-pressure natural gas (pipeline quality, 1,050 BTU/scf)\n"
            "- Throughput: 450 MMscf/day\n"
            "- Vintage: 1987, last inline inspection (smart pig) 2021 -- no critical defects found\n"
            "- Cathodic protection: Active, last survey 2023\n"
            "- Depth of cover: 36-48 inches (varies with terrain)\n"
            "- ROW width: 75 feet, cleared of vegetation per NERC/PHMSA requirements\n"
            "\n"
            "EMERGENCY PROCEDURES:\n"
            "- Emergency shutoff: TransCo Station 12 (mainline valve + automated slam-shut)\n"
            "- CONTROLLED shutdown sequence: 2 hours (gradual depressurization to prevent water hammer)\n"
            "- EMERGENCY slam-shut: 15 minutes (but risks pipeline damage and extended outage)\n"
            "- TransCo Emergency Control Center (ECC): 24/7 staffed, Bakersfield CA\n"
            "- Notification requirement: 49 CFR 192.615 -- notify operator of ANY fire within 3km of pipeline\n"
            "\n"
            "FAILURE CONSEQUENCES:\n"
            "- Full-bore rupture at 800 PSI: immediate jet fire, thermal radiation lethal to 300m\n"
            "- Potential BLEVE if segment isolated with trapped gas: blast 500m, thermal 1.5km\n"
            "- Downstream impact: 220,000 gas customers lose service (48-72 hr restoration minimum)\n"
            "- Environmental: Gas release and fire in sensitive watershed area\n"
            "\n"
            "NOTIFICATION STATUS: TransCo HAS NOT been notified of Creek Fire. "
            "This is a federal regulatory requirement that has not yet been fulfilled."
        ),
        "weather_forecast": (
            "NWS Spot Forecast -- UPDATED 1100 hours -- HIGH CONFIDENCE\n"
            "\n"
            "SYNOPSIS: Deep upper-level trough approaching from NW. Strong pressure gradient "
            "driving gusty offshore flow. Multiple wind shifts expected as trough axis passes.\n"
            "\n"
            "DETAILED FORECAST:\n"
            "  1130-1330 (NOW to T+2 hr): N wind 28-35 km/h, gusts to 50 km/h. Temp 42C. RH 8%. "
            "  Extreme fire weather. Haines 6.\n"
            "\n"
            "  1330-1730 (T+2 to T+6 hr): *** FIRST WIND SHIFT *** NE wind 30-42 km/h, gusts to 55 km/h. "
            "  Canyon channeling at Maplewood Canyon will amplify to 50-65 km/h effective. "
            "  Hillside Fire ROS expected to DOUBLE. Temp 42C. RH 5% (CRITICAL). Haines 6.\n"
            "  THIS IS THE MOST DANGEROUS PERIOD FOR HILLSIDE FIRE.\n"
            "\n"
            "  1730-2130 (T+6 to T+10 hr): Wind E 20-28 km/h. Slight moderation. Temp 40C. RH 8%. "
            "  Brief window of reduced fire behavior. Useful for suppression operations.\n"
            "\n"
            "  2130-0330 (T+10 to T+16 hr): *** THIRD WIND SHIFT *** SE wind 28-35 km/h, gusts to 45 km/h. "
            "  Creek Fire area: wind aligns with terrain to push fire NW toward pipeline corridor. "
            "  Creek Fire ROS expected to double to 20+ ac/hr. Temp 38C. RH 10%.\n"
            "  THIS IS THE CRITICAL PERIOD FOR PIPELINE THREAT.\n"
            "\n"
            "  0330+ (T+16 hr): Winds diminish to W 10-15 km/h. Trough passes. Gradual improvement. "
            "  RH recovery to 25% by 0600. Fire weather watch downgraded.\n"
            "\n"
            "KEY TAKEAWAY: Two danger windows -- (1) T+2hr for Hillside/school/hospital, "
            "(2) T+10hr for Creek/pipeline. Plan accordingly."
        ),
        "road_conditions": (
            "Road and Access Conditions Report (CHP / CDOT / County Roads, 1120 hours):\n"
            "\n"
            "HILLSIDE FIRE AREA:\n"
            "- Canyon Road (primary access to Hillside Fire): OPEN but smoke visibility <200m in canyon. "
            "  Flaggers recommended. 15km from Station 3.\n"
            "- Elm Street (school evacuation route): OPEN. 2-lane, capacity ~600 vehicles/hr. "
            "  BOTTLENECK at Elm/Maplewood Blvd intersection (single traffic light, no turn lane).\n"
            "- Hospital Drive / Oak Avenue: OPEN. ***OAK AVE BRIDGE weight limit 15 tons*** -- "
            "  standard ambulances (10 ton) OK, heavy apparatus CANNOT cross. "
            "  ALTERNATE: Elm Street to bypass bridge, adds 20 min to hospital evacuation route.\n"
            "- Sunset Drive (senior living evacuation): OPEN. Good condition.\n"
            "\n"
            "POWERLINE FIRE AREA:\n"
            "- Highway 138: OPEN but CHP considering closure at MM 12-18 due to smoke.\n"
            "- Forest Road 7N23: CLOSED by fallen power lines (SCE de-energized but lines across road).\n"
            "\n"
            "CREEK FIRE AREA:\n"
            "- BLM Road 4S01: OPEN, unpaved, passable for 4WD only.\n"
            "- Pipeline access road (TransCo maintenance road): OPEN, gravel, all-weather.\n"
            "\n"
            "CRITICAL FINDING: Hospital primary evacuation route via Oak Ave bridge has WEIGHT RESTRICTION. "
            "Heavy rescue and large transport vehicles must use alternate route via Elm Street (+20 min). "
            "This affects hospital evacuation timeline. Plan accordingly."
        ),
    },
}


ALL_SCENARIOS = {
    "easy_single_fire": TASK_EASY,
    "medium_two_fires": TASK_MEDIUM,
    "hard_cascading_disaster": TASK_HARD,
}
