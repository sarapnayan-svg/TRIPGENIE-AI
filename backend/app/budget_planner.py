"""
TripGenie AI — Deterministic Budget Planning Engine.

Provides transparent, deterministic travel cost calculations across:
1. Accommodation (hotel preference & room capacity)
2. Food & Dining (dining tier & traveler count)
3. Activities & Sightseeing (destination catalog & selected experiences)
4. Transportation (public, rental, private cab, flight premium)
5. Miscellaneous & Contingency (entry fees, permits, shopping reserve)

Also evaluates budget health, detects deficits, generates actionable
cost-saving alternatives, and calculates budget-fit optimization parameters.
"""

import math
from typing import Dict, List, Optional, Any


# ---------------------------------------------------------------------------
# DETERMINISTIC UNIT RATES
# ---------------------------------------------------------------------------

HOTEL_RATES_PER_ROOM_NIGHT = {
    "hostel": 900.0,       # Dorm bed / backpacker hostel per bed/person
    "budget": 1600.0,      # Clean budget hotel / guesthouse (double occupancy)
    "standard": 3200.0,    # 3-star comfortable hotel / boutique stay
    "premium": 6800.0,     # 4-star resort / heritage property
    "luxury": 14500.0,     # 5-star beachfront resort / luxury palace
}

FOOD_RATES_PER_PERSON_DAY = {
    "backpacker": 450.0,   # Local dhabas, street delicacies, simple thalis
    "budget": 650.0,       # Casual eateries, beach shacks, standard cafes
    "balanced": 1100.0,    # Popular multi-cuisine restaurants, heritage cafes
    "premium": 2200.0,     # Fine-dining seafood restaurants, upscale lounges
    "luxury": 3800.0,      # 5-star resort dining, gourmet multi-course feasts
}

TRANSPORT_RATES_PER_DAY = {
    "public": {
        "type": "per_person",
        "rate": 250.0,     # Buses, shared auto-rickshaws, metro/ferry
    },
    "rental": {
        "type": "vehicle_rental",
        "scooter_rate": 600.0,  # 2 pax per scooter
        "car_rate": 2200.0,     # 4 pax per hatchback/sedan
        "fuel_per_day": 500.0,
    },
    "private_cab": {
        "type": "private_vehicle",
        "rate_per_cab": 2800.0, # AC sedan/SUV with driver (up to 4 pax)
    },
    "flight_premium": {
        "type": "premium_transit",
        "intercity_flight_per_person": 6500.0,  # Estimated roundtrip flight
        "local_cab_per_day": 3400.0,            # Dedicated premium SUV cab
    },
}

# Real Destination Activities Catalog (Rate per person)
DESTINATION_ACTIVITIES = {
    "goa": {
        "scuba_diving": {"name": "Grande Island Scuba Diving & Dolphin Boat", "cost": 2500.0, "category": "adventure"},
        "water_sports": {"name": "Baga Beach 5-in-1 Water Sports Combo", "cost": 1500.0, "category": "adventure"},
        "spice_plantation": {"name": "Sahakari Spice Farm Tour & Goan Lunch", "cost": 600.0, "category": "culture"},
        "sunset_cruise": {"name": "Mandovi River Sunset Cultural Cruise", "cost": 500.0, "category": "relaxation"},
        "fort_tour": {"name": "Fort Aguada & Chapora Heritage Walk", "cost": 300.0, "category": "culture"},
        "beach_leisure": {"name": "North & South Goa Beach Exploration", "cost": 0.0, "category": "nature"},
    },
    "kerala": {
        "houseboat_cruise": {"name": "Alleppey Backwaters Houseboat Day Cruise", "cost": 3000.0, "category": "relaxation"},
        "shikara_ride": {"name": "Vembanad Lake Sunset Shikara Canoe Ride", "cost": 600.0, "category": "nature"},
        "kathakali_show": {"name": "Kochi Cultural Center Kathakali & Kalaripayattu", "cost": 500.0, "category": "culture"},
        "eravikulam_safari": {"name": "Eravikulam National Park Nilgiri Tahr Safari", "cost": 250.0, "category": "nature"},
        "tea_factory_tour": {"name": "Tata Tea Museum & Plantation Walking Tour", "cost": 200.0, "category": "culture"},
        "fort_kochi_walk": {"name": "Fort Kochi Chinese Fishing Nets Heritage Trail", "cost": 0.0, "category": "culture"},
    },
    "manali": {
        "paragliding": {"name": "Solang Valley Tandem Paragliding", "cost": 2500.0, "category": "adventure"},
        "atal_tunnel_tour": {"name": "Atal Tunnel & Sissu Lahaul Valley Excursion", "cost": 1200.0, "category": "adventure"},
        "river_rafting": {"name": "Beas River White-Water Rafting (14km)", "cost": 1200.0, "category": "adventure"},
        "jogini_trek": {"name": "Jogini Waterfall & Apple Orchard Trek", "cost": 0.0, "category": "nature"},
        "hadimba_temple": {"name": "Hadimba Devi Temple & Cedar Woods", "cost": 50.0, "category": "culture"},
        "old_manali_walk": {"name": "Old Manali Bohemian Market & River Walk", "cost": 0.0, "category": "relaxation"},
    },
    "jaipur": {
        "chokhi_dhani": {"name": "Chokhi Dhani Ethnic Resort Village Feast", "cost": 1100.0, "category": "culture"},
        "city_palace_museum": {"name": "City Palace & Jantar Mantar Observatory Tour", "cost": 700.0, "category": "culture"},
        "amber_fort_tour": {"name": "Amber Fort Guided Tour & Maota Lake View", "cost": 500.0, "category": "culture"},
        "hawa_mahal_bazaar": {"name": "Hawa Mahal Entry & Johari Bazaar Walk", "cost": 200.0, "category": "shopping"},
        "nahargarh_sunset": {"name": "Nahargarh Fort Hilltop Sunset Ramparts", "cost": 100.0, "category": "nature"},
        "patrika_gate": {"name": "Jawahar Circle & Patrika Gate Photography", "cost": 0.0, "category": "culture"},
    },
    "rishikesh": {
        "bungee_jumping": {"name": "Mohan Chatti Bungee Jump (83m India's Highest)", "cost": 3500.0, "category": "adventure"},
        "ganges_rafting": {"name": "Shivpuri to Rishikesh Grade III River Rafting", "cost": 1200.0, "category": "adventure"},
        "beatles_ashram": {"name": "The Beatles Ashram (Chaurasi Kutia) Art Tour", "cost": 150.0, "category": "culture"},
        "neelkanth_temple": {"name": "Neelkanth Mahadev Mountain Excursion", "cost": 300.0, "category": "culture"},
        "triveni_ghat_aarti": {"name": "Triveni Ghat Evening Maha Ganga Aarti", "cost": 0.0, "category": "relaxation"},
        "waterfall_nature_hike": {"name": "Patna / Neer Garh Cascading Waterfall Hike", "cost": 50.0, "category": "nature"},
    },
}

# Generic Activities catalog for unspecified destinations
GENERIC_ACTIVITIES = {
    "city_sightseeing": {"name": "Guided City Landmark & Heritage Tour", "cost": 600.0, "category": "culture"},
    "museum_entry": {"name": "Premier Regional Museum & Art Gallery", "cost": 250.0, "category": "culture"},
    "nature_park": {"name": "Botanical Gardens & Nature Sanctuary", "cost": 200.0, "category": "nature"},
    "scenic_viewpoint": {"name": "Hilltop Panoramic Viewpoint & Cable Car", "cost": 450.0, "category": "adventure"},
    "cultural_performance": {"name": "Traditional Evening Folk Dance & Music Show", "cost": 500.0, "category": "culture"},
    "walking_tour": {"name": "Historic Old Quarter Walking Tour", "cost": 0.0, "category": "culture"},
}


# ---------------------------------------------------------------------------
# CORE DETERMINISTIC BUDGET CALCULATION ENGINE
# ---------------------------------------------------------------------------

def calculate_trip_budget(
    destination: str,
    days: int,
    travelers: int,
    user_budget: float,
    hotel_preference: str = "standard",
    transport_preference: str = "private_cab",
    selected_activities: Optional[List[str]] = None,
    travel_style: str = "balanced",
    custom_hotel_rate: Optional[float] = None,
    custom_hotel_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calculate deterministic, itemized travel expenses across 5 categories.
    No random numbers. All values strictly computed from unit rate tables.
    """
    days = max(1, int(days))
    travelers = max(1, int(travelers))
    user_budget = float(user_budget)
    nights = max(1, days - 1) if days > 1 else 1

    dest_key = destination.strip().lower()

    # 1. ACCOMMODATION CALCULATION
    hotel_tier = hotel_preference.lower() if hotel_preference in HOTEL_RATES_PER_ROOM_NIGHT else "standard"
    base_hotel_rate = float(custom_hotel_rate) if custom_hotel_rate is not None and custom_hotel_rate > 0 else HOTEL_RATES_PER_ROOM_NIGHT[hotel_tier]
    hotel_label = f" ({custom_hotel_name})" if custom_hotel_name else ""

    if hotel_tier == "hostel":
        # Per person bed calculation
        accommodation_cost = round(base_hotel_rate * travelers * nights, 2)
        rooms_count = travelers
        accommodation_note = f"₹{base_hotel_rate:,.0f}/bed/night × {travelers} beds × {nights} nights{hotel_label}"
    else:
        # 2 travelers per room standard
        rooms_count = math.ceil(travelers / 2.0)
        accommodation_cost = round(base_hotel_rate * rooms_count * nights, 2)
        accommodation_note = f"₹{base_hotel_rate:,.0f}/room/night × {rooms_count} rooms × {nights} nights{hotel_label}"

    # 2. FOOD CALCULATION
    style_key = travel_style.lower() if travel_style in FOOD_RATES_PER_PERSON_DAY else "balanced"
    daily_food_rate = FOOD_RATES_PER_PERSON_DAY[style_key]
    food_cost = round(daily_food_rate * travelers * days, 2)
    food_note = f"₹{daily_food_rate:,.0f}/person/day × {travelers} travelers × {days} days"

    # 3. ACTIVITIES CALCULATION
    dest_catalog = DESTINATION_ACTIVITIES.get(dest_key, GENERIC_ACTIVITIES)
    activities_cost = 0.0
    itemized_activities = []

    if selected_activities and len(selected_activities) > 0:
        for act_id in selected_activities:
            act_info = dest_catalog.get(act_id)
            if not act_info:
                # Check other destination catalogs as fallback
                for d_cat in DESTINATION_ACTIVITIES.values():
                    if act_id in d_cat:
                        act_info = d_cat[act_id]
                        break
            if not act_info:
                act_info = GENERIC_ACTIVITIES.get(act_id, {"name": act_id.replace("_", " ").title(), "cost": 500.0})

            cost_per_person = act_info.get("cost", 500.0)
            total_act = round(cost_per_person * travelers, 2)
            activities_cost += total_act
            itemized_activities.append({
                "id": act_id,
                "name": act_info["name"],
                "cost_per_person": cost_per_person,
                "total_cost": total_act,
            })
    else:
        # Curate top 3 default activities from destination catalog
        default_keys = list(dest_catalog.keys())[:3]
        for act_id in default_keys:
            act_info = dest_catalog[act_id]
            cost_per_person = act_info.get("cost", 400.0)
            total_act = round(cost_per_person * travelers, 2)
            activities_cost += total_act
            itemized_activities.append({
                "id": act_id,
                "name": act_info["name"],
                "cost_per_person": cost_per_person,
                "total_cost": total_act,
            })

    activities_cost = round(activities_cost, 2)
    activities_note = f"{len(itemized_activities)} curated activities for {travelers} travelers"

    # 4. TRANSPORTATION CALCULATION
    t_pref = transport_preference.lower() if transport_preference in TRANSPORT_RATES_PER_DAY else "private_cab"
    t_config = TRANSPORT_RATES_PER_DAY[t_pref]

    if t_pref == "public":
        transport_cost = round(t_config["rate"] * travelers * days, 2)
        transport_note = f"₹{t_config['rate']:,.0f}/person/day × {travelers} travelers × {days} days"
    elif t_pref == "rental":
        if travelers <= 2:
            scooters = math.ceil(travelers / 2.0)
            transport_cost = round((scooters * t_config["scooter_rate"] + t_config["fuel_per_day"]) * days, 2)
            transport_note = f"{scooters} scooter(s) @ ₹{t_config['scooter_rate']:,.0f}/day + fuel ₹{t_config['fuel_per_day']:,.0f}/day × {days} days"
        else:
            cars = math.ceil(travelers / 4.0)
            transport_cost = round((cars * t_config["car_rate"] + t_config["fuel_per_day"]) * days, 2)
            transport_note = f"{cars} rental car(s) @ ₹{t_config['car_rate']:,.0f}/day + fuel ₹{t_config['fuel_per_day']:,.0f}/day × {days} days"
    elif t_pref == "flight_premium":
        flights_cost = t_config["intercity_flight_per_person"] * travelers
        cabs_count = math.ceil(travelers / 4.0)
        cabs_cost = cabs_count * t_config["local_cab_per_day"] * days
        transport_cost = round(flights_cost + cabs_cost, 2)
        transport_note = f"Roundtrip flights (₹{t_config['intercity_flight_per_person']:,.0f} × {travelers}) + {cabs_count} SUV cab(s) for {days} days"
    else:  # private_cab
        cabs_count = math.ceil(travelers / 4.0)
        daily_cab_rate = t_config["rate_per_cab"]
        transport_cost = round(cabs_count * daily_cab_rate * days, 2)
        transport_note = f"{cabs_count} dedicated AC cab(s) @ ₹{daily_cab_rate:,.0f}/day × {days} days"

    # 5. MISCELLANEOUS (7% Contingency Reserve)
    subtotal = accommodation_cost + food_cost + activities_cost + transport_cost
    miscellaneous_cost = round(subtotal * 0.07, 2)
    miscellaneous_note = "7% reserve for entry permits, bottled water, tips, and local shopping"

    # TOTALS & BUDGET HEALTH
    total_estimated = round(subtotal + miscellaneous_cost, 2)
    remaining_budget = round(user_budget - total_estimated, 2)
    utilization_percent = round((total_estimated / max(1.0, user_budget)) * 100.0, 1)

    # Status classification
    if utilization_percent <= 85.0:
        status = "within_budget"
        status_label = "Comfortably Within Budget"
    elif utilization_percent <= 100.0:
        status = "tight_budget"
        status_label = "Balanced / Near Budget Limit"
    else:
        status = "exceeded_budget"
        status_label = "Exceeds User Budget"

    # 6. LOWER-COST ALTERNATIVES & RECOMMENDATIONS (WHEN OVER BUDGET)
    alternatives = []
    cost_saving_tips = []

    if status == "exceeded_budget":
        deficit = round(total_estimated - user_budget, 2)

        # Alternative 1: Downgrade Hotel Tier
        if hotel_tier in ["luxury", "premium"]:
            target_tier = "standard" if hotel_tier == "luxury" else "budget"
            alt_room_rate = HOTEL_RATES_PER_ROOM_NIGHT[target_tier]
            alt_rooms = math.ceil(travelers / 2.0)
            alt_acc_cost = alt_room_rate * alt_rooms * nights
            savings = round(accommodation_cost - alt_acc_cost, 2)
            if savings > 0:
                alternatives.append({
                    "category": "accommodation",
                    "title": f"Switch Stays to {target_tier.title()} Accommodations",
                    "potential_savings": savings,
                    "description": f"Switching from {hotel_tier.title()} to {target_tier.title()} rooms saves approximately ₹{savings:,.0f}.",
                    "action_param": {"hotel_preference": target_tier},
                })
        elif hotel_tier == "standard":
            alt_room_rate = HOTEL_RATES_PER_ROOM_NIGHT["budget"]
            alt_rooms = math.ceil(travelers / 2.0)
            alt_acc_cost = alt_room_rate * alt_rooms * nights
            savings = round(accommodation_cost - alt_acc_cost, 2)
            if savings > 0:
                alternatives.append({
                    "category": "accommodation",
                    "title": "Switch to Clean Budget Stays & Guesthouses",
                    "potential_savings": savings,
                    "description": f"Choosing verified guesthouses reduces accommodation cost by ₹{savings:,.0f}.",
                    "action_param": {"hotel_preference": "budget"},
                })

        # Alternative 2: Switch Transport Mode
        if t_pref == "flight_premium":
            savings = round(transport_cost - (math.ceil(travelers / 4.0) * 2800.0 * days), 2)
            alternatives.append({
                "category": "transportation",
                "title": "Book Train / Road Travel + Local Private Cab",
                "potential_savings": savings,
                "description": f"Replacing flight packages with standard transport saves up to ₹{savings:,.0f}.",
                "action_param": {"transport_preference": "private_cab"},
            })
        elif t_pref == "private_cab":
            # Switch to rental or public
            alt_t_cost = round(250.0 * travelers * days, 2)
            savings = round(transport_cost - alt_t_cost, 2)
            alternatives.append({
                "category": "transportation",
                "title": "Use Local Shared Transit & Scooters",
                "potential_savings": savings,
                "description": f"Using local transit instead of a dedicated cab saves ₹{savings:,.0f}.",
                "action_param": {"transport_preference": "rental" if travelers <= 2 else "public"},
            })

        # Alternative 3: Activity Optimization
        if activities_cost > 0:
            free_act_savings = round(activities_cost * 0.50, 2)
            alternatives.append({
                "category": "activities",
                "title": "Prioritize Scenic Viewpoints & Cultural Walks",
                "potential_savings": free_act_savings,
                "description": f"Substituting ticketed adventures with panoramic nature trails saves ₹{free_act_savings:,.0f}.",
                "action_param": {"travel_style": "backpacker"},
            })

        # Alternative 4: Dining Optimization
        if style_key in ["luxury", "premium"]:
            alt_food_rate = FOOD_RATES_PER_PERSON_DAY["balanced"]
            savings = round(food_cost - (alt_food_rate * travelers * days), 2)
            alternatives.append({
                "category": "food",
                "title": "Mix Fine Dining with Authentic Local Eateries",
                "potential_savings": savings,
                "description": f"Dining at local family eateries and cafes saves approx ₹{savings:,.0f}.",
                "action_param": {"travel_style": "balanced"},
            })

        cost_saving_tips.append(
            f"Your current itinerary is ₹{deficit:,.0f} over budget ({utilization_percent}% utilization). "
            f"Applying the suggestions above can bring your total expenditure within your ₹{user_budget:,.0f} limit."
        )
    else:
        cost_saving_tips.append(
            f"Your estimated expenditure of ₹{total_estimated:,.0f} fits comfortably within your ₹{user_budget:,.0f} budget "
            f"with a remaining cushion of ₹{remaining_budget:,.0f}."
        )

    # Return comprehensive structured budget report
    return {
        "user_budget": user_budget,
        "total_estimated": total_estimated,
        "remaining_budget": remaining_budget,
        "utilization_percent": utilization_percent,
        "status": status,
        "status_label": status_label,
        "is_over_budget": status == "exceeded_budget",
        "deficit": max(0.0, round(total_estimated - user_budget, 2)),
        "categories": {
            "accommodation": {
                "amount": accommodation_cost,
                "percent": round((accommodation_cost / max(1.0, total_estimated)) * 100.0, 1),
                "calculation_note": accommodation_note,
                "tier": hotel_tier,
            },
            "food": {
                "amount": food_cost,
                "percent": round((food_cost / max(1.0, total_estimated)) * 100.0, 1),
                "calculation_note": food_note,
                "tier": style_key,
            },
            "activities": {
                "amount": activities_cost,
                "percent": round((activities_cost / max(1.0, total_estimated)) * 100.0, 1),
                "calculation_note": activities_note,
                "itemized": itemized_activities,
            },
            "transportation": {
                "amount": transport_cost,
                "percent": round((transport_cost / max(1.0, total_estimated)) * 100.0, 1),
                "calculation_note": transport_note,
                "tier": t_pref,
            },
            "miscellaneous": {
                "amount": miscellaneous_cost,
                "percent": round((miscellaneous_cost / max(1.0, total_estimated)) * 100.0, 1),
                "calculation_note": miscellaneous_note,
            },
        },
        "cost_saving_alternatives": alternatives,
        "cost_saving_tips": cost_saving_tips,
        "per_person_estimated": round(total_estimated / travelers, 2),
        "per_day_estimated": round(total_estimated / days, 2),
    }


def optimize_budget_parameters(
    destination: str,
    days: int,
    travelers: int,
    user_budget: float,
    current_hotel: str,
    current_transport: str,
    current_style: str,
) -> Dict[str, str]:
    """
    Find optimal parameters that fit strictly within the user's budget.
    Iterates from current down to economical tiers.
    """
    hotel_order = ["luxury", "premium", "standard", "budget", "hostel"]
    transport_order = ["flight_premium", "private_cab", "rental", "public"]
    style_order = ["luxury", "premium", "balanced", "budget", "backpacker"]

    h_idx = hotel_order.index(current_hotel) if current_hotel in hotel_order else 2
    t_idx = transport_order.index(current_transport) if current_transport in transport_order else 1
    s_idx = style_order.index(current_style) if current_style in style_order else 2

    # Step down tiers until budget fits
    for h in hotel_order[h_idx:]:
        for t in transport_order[t_idx:]:
            for s in style_order[s_idx:]:
                report = calculate_trip_budget(
                    destination=destination,
                    days=days,
                    travelers=travelers,
                    user_budget=user_budget,
                    hotel_preference=h,
                    transport_preference=t,
                    travel_style=s,
                )
                if not report["is_over_budget"]:
                    return {
                        "hotel_preference": h,
                        "transport_preference": t,
                        "travel_style": s,
                        "optimized_report": report,
                    }

    # If still tight, use the most economical tiers
    return {
        "hotel_preference": "hostel" if travelers <= 2 else "budget",
        "transport_preference": "public",
        "travel_style": "backpacker",
        "optimized_report": calculate_trip_budget(
            destination=destination,
            days=days,
            travelers=travelers,
            user_budget=user_budget,
            hotel_preference="hostel" if travelers <= 2 else "budget",
            transport_preference="public",
            travel_style="backpacker",
        ),
    }
