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
            "threats": ["Highway 89", "Ranch property (3 homes)"],
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
            "location": "Station 5 (8km away)",
            "specialty": "general",
        },
        "crew_bravo": {
            "crew_id": "crew_bravo",
            "name": "Crew Bravo",
            "size": 20,
            "status": "available",
            "hours_on_duty": 0.0,
            "assigned_to": None,
            "location": "Station 12 (15km away)",
            "specialty": "hotshot",
        },
        "crew_charlie": {
            "crew_id": "crew_charlie",
            "name": "Crew Charlie",
            "size": 15,
            "status": "available",
            "hours_on_duty": 2.0,
            "assigned_to": None,
            "location": "Station 5 (8km away)",
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
            "location": "Airbase Delta",
        },
        "tanker_1": {
            "aircraft_id": "tanker_1",
            "name": "Tanker-10",
            "aircraft_type": "air_tanker",
            "status": "available",
            "water_capacity_gallons": 8000,
            "assigned_to": None,
            "location": "Airbase Delta",
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
            "description": "3 ranch homes with 12 residents, 3km east of Cedar Fire.",
        },
    },
    "weather": {
        "wind_speed_kmh": 15.0,
        "wind_direction": "W",
        "temperature_celsius": 34.0,
        "humidity_percent": 22.0,
        "forecast_change": "Wind steady, no major changes expected in next 6 hours.",
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
    "diagnostic_info": {
        "check_fire_behavior": "Cedar Fire burning in dry grass, moderate rate of spread. Terrain is flat -- no canyon effect. Expected to reach highway in ~6 hours at current rate without intervention.",
        "check_weather_detail": "Stable high pressure system. Wind 15 km/h from west. No lightning forecast. Relative humidity will drop to 18% by afternoon.",
        "check_road_access": "Highway 89 is open. Crew access via Forest Road 12 from the south is clear. Good staging area at mile marker 47.",
        "check_structures": "3 ranch homes at Pine Ranch, all wood-frame. Defensible space is minimal. Structure protection recommended if fire advances past 1.5km.",
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
            "threats": ["Timber resources", "Wildlife habitat", "Remote cabins (unoccupied)"],
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
            "threats": ["Oakdale town (500 residents)", "Elementary school", "Gas station on Route 4"],
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
            "location": "Ridge Fire front line",
            "specialty": "general",
        },
        "crew_echo": {
            "crew_id": "crew_echo",
            "name": "Crew Echo",
            "size": 20,
            "status": "available",
            "hours_on_duty": 1.0,
            "assigned_to": None,
            "location": "Station 7 (20km from Valley Fire)",
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
            "location": "Airbase Echo",
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
            "description": "Town of 500 with elementary school (120 children). Gas station with underground fuel tanks on Route 4. 2.5km from Valley Fire, wind shifting toward town in ~4 hours.",
        },
        "zone_cabins": {
            "zone_id": "zone_cabins",
            "name": "Mountain Cabins",
            "population": 0,
            "distance_to_nearest_fire_km": 4.0,
            "nearest_fire": "fire_ridge",
            "is_evacuated": False,
            "has_vulnerable": False,
            "description": "Seasonal cabins, currently unoccupied. No immediate risk.",
        },
    },
    "weather": {
        "wind_speed_kmh": 25.0,
        "wind_direction": "NW",
        "temperature_celsius": 38.0,
        "humidity_percent": 14.0,
        "forecast_change": "WARNING: Wind shifting to W at 30 km/h in ~4 hours. This will push Valley Fire directly toward Oakdale. Temperature rising to 42°C.",
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
    "diagnostic_info": {
        "check_valley_fire_behavior": "Valley Fire burning fast in dry grass with urban interface. At current spread rate (25 ac/hr) and with wind shift in 4 hours, fire will reach Oakdale outskirts in ~5 hours. After wind shift, estimated arrival drops to ~2 hours.",
        "check_ridge_fire_behavior": "Ridge Fire is partially contained (30%). Burning slowly in timber (8 ac/hr). Containment lines holding on south flank. Losing Crew Delta would risk losing south containment line, but fire is not threatening lives.",
        "check_evacuation_routes": "Oakdale evacuation via Route 4 south (away from fire). Estimated evacuation time: 2 hours for full town. School bus available for children. Route 4 gas station should be shut down during evacuation.",
        "check_mutual_aid": "Neighboring County 12 has 2 crews available. Response time: 4 hours. County 8 has 1 crew, response time: 6 hours.",
        "check_crew_delta_fatigue": "Crew Delta has been on Ridge Fire for 11 hours. Safety protocols recommend rotation after 12 hours. Performance degraded. Risk of injury increases significantly after 14 hours.",
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
            "threats": ["Regional power grid (serves 50,000 homes)", "Media scrutiny", "Timber"],
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
                "Maplewood Elementary School (180 children)",
                "St. Mary's Hospital (45 patients, 12 in ICU)",
                "Senior living facility (60 residents)",
                "Residential neighborhood (800 homes)",
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
            "threats": ["Remote forest land"],
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
            "location": "Station 3 (15km from Hillside Fire)",
            "specialty": "structure_protection",
        },
        "crew_golf": {
            "crew_id": "crew_golf",
            "name": "Crew Golf",
            "size": 18,
            "status": "fatigued",
            "hours_on_duty": 13.0,
            "assigned_to": None,
            "location": "Returning from previous assignment",
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
            "location": "Airbase Foxtrot",
        },
        "heli_4": {
            "aircraft_id": "heli_4",
            "name": "Hawk-4",
            "aircraft_type": "helicopter",
            "status": "maintenance",
            "water_capacity_gallons": 2600,
            "assigned_to": None,
            "location": "Airbase Foxtrot (maintenance, available in 3 hours)",
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
            "description": "Elementary school with 180 children. Fire approaching from canyon -- fast spread expected. Only 1 evacuation route via Elm Street. School buses available but need 45 min to mobilize.",
        },
        "zone_hospital": {
            "zone_id": "zone_hospital",
            "name": "St. Mary's Hospital",
            "population": 95,
            "distance_to_nearest_fire_km": 2.2,
            "nearest_fire": "fire_y",
            "is_evacuated": False,
            "has_vulnerable": True,
            "description": "Hospital with 45 patients (12 ICU, 3 on ventilators). Evacuation requires ambulances and is extremely complex. 2.2km from Hillside Fire.",
        },
        "zone_senior": {
            "zone_id": "zone_senior",
            "name": "Sunset Senior Living",
            "population": 60,
            "distance_to_nearest_fire_km": 2.5,
            "nearest_fire": "fire_y",
            "is_evacuated": False,
            "has_vulnerable": True,
            "description": "Senior living facility, 60 elderly residents (many with mobility issues). 2.5km from Hillside Fire.",
        },
        "zone_residential": {
            "zone_id": "zone_residential",
            "name": "Hillcrest Neighborhood",
            "population": 2400,
            "distance_to_nearest_fire_km": 3.5,
            "nearest_fire": "fire_y",
            "is_evacuated": False,
            "has_vulnerable": False,
            "description": "800 homes with ~2400 residents. 3.5km from Hillside Fire. Not immediate danger but should prepare.",
        },
    },
    "weather": {
        "wind_speed_kmh": 30.0,
        "wind_direction": "N",
        "temperature_celsius": 42.0,
        "humidity_percent": 8.0,
        "forecast_change": "EXTREME: Wind shifting to NE in 2 hours (pushes Hillside Fire faster toward school/hospital). Second shift to E in 6 hours. Third shift to SE in 10 hours (pushes Creek Fire toward gas pipeline). Temperature holding at 42°C. Humidity dropping to 5%.",
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
    "diagnostic_info": {
        "check_hillside_fire_behavior": "Hillside Fire burning in canyon -- extreme fire behavior expected. Canyon effect will accelerate flames. At 30 ac/hr, fire reaches school in ~2.5 hours. After wind shift (2 hours), spread rate could double to 60 ac/hr, reaching school in under 1 hour.",
        "check_creek_fire_detail": "Creek Fire appears minor at 45 acres in remote brush. HOWEVER: TransCo gas pipeline runs 6km NE of current fire location. At current spread (10 ac/hr NE), fire reaches pipeline vicinity in ~8 hours. Weather forecast shows wind shifting SE in 10 hours which would push fire directly at pipeline. Pipeline carries high-pressure natural gas -- fire contact could cause explosion affecting 5km radius.",
        "check_powerline_fire_detail": "Powerline Fire is large (950 acres) but burning slowly in timber. Containment lines at 15%. Power company has already de-energized affected lines -- no electrocution risk. Power outage affects 50,000 homes but backup generators running at hospitals and critical facilities. No lives at immediate risk.",
        "check_hospital_evacuation": "Hospital evacuation requires: 3 ambulances for ICU (ventilator patients), 5 transport vans for mobile patients. Estimated time: 3 hours minimum. Nearest receiving hospital is 45 minutes away. ICU patients at highest risk during transport.",
        "check_crew_golf_status": "Crew Golf has been working 13 hours. Multiple members reporting exhaustion. One member treated for heat stress 2 hours ago. Safety officer recommends 10-hour rest before redeployment. Deploying now violates OSHA wildfire safety regulations.",
        "check_political_situation": "County Commissioner called demanding resources on Powerline Fire -- media cameras at Powerline Fire, news helicopters overhead. Commissioner worried about re-election impact of prolonged blackout. THIS IS NOT A TACTICAL DECISION -- do not let political pressure override life safety priorities.",
        "check_mutual_aid_options": "State mobilization center can dispatch 3 crews + 2 helicopters. ETA: 5 hours. National Guard can provide evacuation support. ETA: 3 hours. Request must go through Emergency Operations Center.",
        "check_pipeline_detail": "TransCo Pipeline LP-7: 24-inch high-pressure natural gas, operating at 800 PSI. Emergency shutoff valve at Station 12 (requires 2-hour shutdown sequence). Gas company emergency line: must be notified of any fire within 3km of pipeline per federal regulation.",
    },
}


ALL_SCENARIOS = {
    "easy_single_fire": TASK_EASY,
    "medium_two_fires": TASK_MEDIUM,
    "hard_cascading_disaster": TASK_HARD,
}
