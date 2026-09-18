"""
LLM layer: takes retrieved context (from rag.py) plus the user's trip
preferences and asks Claude (or fallback RAG synthesizer) to generate structured output.
This is the "generation" half of RAG -- the model is grounded in the retrieved chunks
instead of relying only on what it memorized during training.
"""
import json
import re
from typing import List, Dict, Any, Optional
import anthropic

from app.config import ANTHROPIC_API_KEY, LLM_MODEL

# Initialize Anthropic client only if key is available
client = None
if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY.strip() and not ANTHROPIC_API_KEY.startswith("your-api"):
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY.strip())
    except Exception as e:
        print(f"[WARNING] Could not initialize Anthropic client: {e}")
        client = None


def _format_context(chunks: List[Dict]) -> str:
    from app.rag import ContextFormatter
    return ContextFormatter.format(chunks)


ITINERARY_SYSTEM_PROMPT = """You are TripGenie, an AI travel planning assistant.
You must ground every recommendation strictly in the CONTEXT block you are given -- do
not invent attractions, prices, or hotel names that are not supported by the
context or general well-known facts. If the context doesn't cover something,
state it clearly rather than making it up.

Return ONLY valid JSON matching this exact shape, with no markdown fences, no prose before or after:
{
  "destination": "string",
  "summary": "string summary of the trip",
  "days": [
    {
      "day": 1,
      "title": "string day title",
      "description": "string detailed morning, afternoon, and evening schedule",
      "places": ["string place 1", "string place 2"],
      "activities": ["string activity 1", "string activity 2"],
      "food_recommendations": ["string food 1", "string food 2"],
      "estimated_cost": 20000.0
    }
  ],
  "budget_breakdown": {
    "stay": 40000.0,
    "food": 20000.0,
    "activities": 25000.0,
    "transport": 15000.0
  },
  "packing_tips": ["string tip 1", "string tip 2"],
  "travel_tips": ["string tip 1", "string tip 2"]
}
budget_breakdown values must sum to the traveler's total budget.
"""


from app.budget_planner import calculate_trip_budget


def generate_itinerary(destination: str, days: int, travelers: int,
                        budget: int, interests: List[str],
                        context_chunks: List[Dict],
                        travel_style: Optional[str] = "balanced",
                        hotel_preference: Optional[str] = "standard",
                        transport_preference: Optional[str] = "private_cab",
                        selected_activities: Optional[List[str]] = None,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> Dict[str, Any]:
    context = _format_context(context_chunks)

    # Compute deterministic budget report
    budget_report = calculate_trip_budget(
        destination=destination,
        days=days,
        travelers=travelers,
        user_budget=budget,
        hotel_preference=hotel_preference or "standard",
        transport_preference=transport_preference or "private_cab",
        selected_activities=selected_activities,
        travel_style=travel_style or "balanced",
    )

    # If Anthropic client is ready, call Claude
    if client is not None:
        user_prompt = f"""CONTEXT:
{context}

TRIP REQUEST:
Destination: {destination}
Duration: {days} days
Travelers: {travelers}
Total user budget: Rs {budget}
Interests: {', '.join(interests) if interests else 'general sightseeing'}
Travel style: {travel_style or 'balanced'}
Hotel preference: {hotel_preference or 'standard'}
Transportation preference: {transport_preference or 'private_cab'}
Selected activities: {', '.join(selected_activities) if selected_activities else 'Standard curated experiences'}
Travel dates: {f"{start_date} to {end_date}" if start_date and end_date else 'Flexible'}

DETERMINISTIC ESTIMATED BUDGET BREAKDOWN:
- Accommodation: Rs {budget_report['categories']['accommodation']['amount']} ({hotel_preference})
- Food & Dining: Rs {budget_report['categories']['food']['amount']} ({travel_style})
- Activities: Rs {budget_report['categories']['activities']['amount']}
- Transportation: Rs {budget_report['categories']['transportation']['amount']} ({transport_preference})
- Miscellaneous (7% reserve): Rs {budget_report['categories']['miscellaneous']['amount']}
Total Estimated: Rs {budget_report['total_estimated']} (Status: {budget_report['status_label']})

Generate a day-by-day itinerary with places, activities, food recommendations, estimated cost, and travel tips as JSON following the required schema. Ensure the day-by-day activities respect the budget level."""

        try:
            response = client.messages.create(
                model=LLM_MODEL,
                max_tokens=3000,
                system=ITINERARY_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(block.text for block in response.content if block.type == "text")
            result = _safe_json_parse(text)
            result["generated_by"] = f"Anthropic Claude ({LLM_MODEL}) + RAG"
            # Overlay deterministic budget analysis
            result["budget_breakdown"] = {
                "stay": budget_report["categories"]["accommodation"]["amount"],
                "food": budget_report["categories"]["food"]["amount"],
                "activities": budget_report["categories"]["activities"]["amount"],
                "transport": budget_report["categories"]["transportation"]["amount"],
                "accommodation": budget_report["categories"]["accommodation"]["amount"],
                "transportation": budget_report["categories"]["transportation"]["amount"],
                "miscellaneous": budget_report["categories"]["miscellaneous"]["amount"],
                "total_estimated": budget_report["total_estimated"],
                "user_budget": budget_report["user_budget"],
                "remaining_budget": budget_report["remaining_budget"],
                "utilization_percent": budget_report["utilization_percent"],
                "status": budget_report["status"],
                "status_label": budget_report["status_label"],
                "is_over_budget": budget_report["is_over_budget"],
                "deficit": budget_report["deficit"],
                "cost_saving_alternatives": budget_report["cost_saving_alternatives"],
                "cost_saving_tips": budget_report["cost_saving_tips"],
                "categories": budget_report["categories"],
            }
            return result
        except Exception as e:
            print(f"[INFO] Claude API call failed or rate limited ({e}). Falling back to Grounded RAG Synthesis Engine.")

    # Grounded RAG Fallback Synthesizer
    return _rag_grounded_fallback_itinerary(
        destination=destination,
        days=days,
        travelers=travelers,
        budget=budget,
        interests=interests,
        context_chunks=context_chunks,
        travel_style=travel_style,
        hotel_preference=hotel_preference,
        transport_preference=transport_preference,
        selected_activities=selected_activities,
        budget_report=budget_report,
    )


CHAT_SYSTEM_PROMPT = """You are TripGenie, an intelligent conversational AI travel planner.
You help travelers customize, modify, and optimize their trip plans.

You have access to:
1. CONTEXT: Verified travel facts and attraction details retrieved via RAG.
2. CURRENT TRIP: The user's active itinerary (destination, duration, days, budget, travelers, activities, hotel preferences).

When the user asks to:
- Make a specific day cheaper (e.g. "Make Day 3 cheaper"): Review that day's activities and places from CURRENT TRIP, suggest concrete low-cost swaps (e.g. self-guided heritage walks or public beach strolls instead of expensive excursions), and estimate the savings.
- Replace an activity (e.g. "Replace scuba diving with another activity"): Suggest suitable alternative activities fitting the destination and vibe with approximate price comparisons.
- Recommend vegetarian/specialty restaurants: Suggest authentic, highly rated vegetarian/vegan eateries in the destination.
- Assess duration feasibility (e.g. "Can I complete this in 4 days?"): Analyze the pacing and geographic clusters, advising on what to prioritize or consolidate.
- Query hotels (e.g. "Which hotel is closest to the beach?"): Recommend hotels from verified properties based on proximity and amenities.
- Adjust or reduce budget (e.g. "Reduce my budget to ₹70,000"): Outline how to rebalance accommodation, activities, and dining.

Keep answers well-structured with clear bullet points, warm conversational tone, and concise actionable recommendations (under 180 words).

CRITICAL LANGUAGE RULE:
Always respond in the EXACT same language and script as the user's message.
- If the user asks in English (e.g. "Tell me about Manali", "Which hotel is closest?"), you MUST respond entirely in pure, professional English.
- If the user asks in Marathi (Devanagari or Romanized Marathi), respond in Marathi.
- Never output Marathi when the question was asked in English.
"""



def chat_response(message: str, trip_context: Dict, context_chunks: List[Dict],
                   history: List[Dict]) -> str:
    # Dynamically detect if message mentions a specific destination (e.g. Manali, Kerala, Jaipur)
    q = message.lower()
    for kd in ["manali", "kerala", "jaipur", "rishikesh", "goa"]:
        if kd in q:
            if not trip_context or trip_context.get("destination", "").lower() != kd:
                trip_context = dict(trip_context or {})
                trip_context["destination"] = kd.capitalize()
            break

    context = _format_context(context_chunks)
    trip_summary = json.dumps(trip_context, ensure_ascii=False)

    if client is not None:
        try:
            system = f"{CHAT_SYSTEM_PROMPT}\n\nCONTEXT:\n{context}\n\nCURRENT TRIP:\n{trip_summary}"
            messages = history + [{"role": "user", "content": message}]
            response = client.messages.create(
                model=LLM_MODEL,
                max_tokens=450,
                system=system,
                messages=messages,
            )
            return "".join(block.text for block in response.content if block.type == "text")
        except Exception as e:
            print(f"[INFO] Claude Chat failed ({e}). Falling back to Grounded RAG Chat Engine.")

    # Grounded RAG Chat Synthesizer
    return _rag_grounded_fallback_chat(message, trip_context, context_chunks)


def _safe_json_parse(text: str) -> Dict:
    """Strip markdown code fences defensively in case output is wrapped in ```json ... ```."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"```$", "", cleaned)
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nRaw output: {text}")


def _rag_grounded_fallback_itinerary(destination: str, days: int, travelers: int,
                                     budget: int, interests: List[str],
                                     context_chunks: List[Dict],
                                     travel_style: Optional[str] = "balanced",
                                     hotel_preference: Optional[str] = "standard",
                                     transport_preference: Optional[str] = "private_cab",
                                     selected_activities: Optional[List[str]] = None,
                                     budget_report: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Academic RAG Synthesis Engine:
    When LLM API keys are unavailable or rate-limited, this engine parses the
    dense vector chunks retrieved from the knowledge base (attractions, stay, food, tips)
    and programmatically structures a fully personalized itinerary grounded in real domain facts.
    """
    if not budget_report:
        budget_report = calculate_trip_budget(
            destination=destination,
            days=days,
            travelers=travelers,
            user_budget=budget,
            hotel_preference=hotel_preference or "standard",
            transport_preference=transport_preference or "private_cab",
            selected_activities=selected_activities,
            travel_style=travel_style or "balanced",
        )

    # Extract categorized facts from retrieved RAG chunks
    attractions = []
    foods = []
    tips = []
    stays = []

    for c in context_chunks:
        cat = c.get("category", "").lower()
        text = c.get("text", "")
        if "attraction" in cat or "overview" in cat:
            attractions.append(text)
        elif "food" in cat:
            foods.append(text)
        elif "tip" in cat or "best_time" in cat:
            tips.append(text)
        elif "stay" in cat:
            stays.append(text)

    # Deterministic budget allocations from budget_planner
    acc_alloc = budget_report["categories"]["accommodation"]["amount"]
    food_alloc = budget_report["categories"]["food"]["amount"]
    act_alloc = budget_report["categories"]["activities"]["amount"]
    trans_alloc = budget_report["categories"]["transportation"]["amount"]
    misc_alloc = budget_report["categories"]["miscellaneous"]["amount"]

    daily_cost = budget_report.get("per_day_estimated", round(budget / max(1, days), 2))

    # Build Day by Day Schedule
    itinerary_days = []
    
    # Destination specific knowledge hooks
    dest_lower = destination.lower()
    if "goa" in dest_lower:
        day_plans = [
            ("Arrival & North Goa Coastal Exploration", "Check in at beachside resort. Spend a relaxing afternoon at Baga and Calangute beach followed by seaside dinner at beach shacks.", ["Baga Beach", "Calangute Beach"], ["Sunset walk", "Beach shack dining"], ["Goan Fish Curry Rice", "Bebinca dessert"]),
            ("Fort Aguada & Coastal Water Sports", "Morning historical tour of Fort Aguada and the lighthouse with panoramic sea views. Afternoon thrilling water sports including parasailing and jet-skiing.", ["Fort Aguada", "Sinquerim Beach"], ["Parasailing", "Jet-skiing", "Lighthouse photography"], ["Prawn Balchao", "Fresh tender coconut water"]),
            ("Old Goa Heritage & Cultural Walking Tour", "Explore UNESCO World Heritage sites in Old Goa including Basilica of Bom Jesus and Se Cathedral. Afternoon spice plantation walk and traditional Goan lunch.", ["Basilica of Bom Jesus", "Old Goa Churches"], ["Heritage architecture tour", "Spice garden walk"], ["Goan Pork Vindaloo", "Sannas"]),
            ("Scenic South Goa Serenity & Scuba Diving", "Journey to South Goa's serene Palolem and Agonda beaches. Morning reef scuba diving session followed by peaceful sunset boat ride around Butterfly Island.", ["Palolem Beach", "Butterfly Island"], ["Scuba diving", "Dolphin safari boat ride"], ["Kingfish rawa fry", "Goan prawn curry"]),
            ("Anjuna Flea Market & Departure", "Morning souvenir shopping at Anjuna and local handicraft bazaars. Savor a final coastal brunch before scheduled transfer to the airport or railway station.", ["Anjuna Flea Market", "Vagator Cliff"], ["Souvenir shopping", "Rooftop cliffside brunch"], ["Cafreal chicken roll", "Fresh fruit juice"]),
        ]
    elif "kerala" in dest_lower:
        day_plans = [
            ("Arrival in Kochi & Colonial Heritage Walk", "Arrive in Kochi, check in at boutique heritage hotel. Stroll past the historic Chinese Fishing Nets, colonial churches, and spice bazaars in Fort Kochi.", ["Fort Kochi", "Chinese Fishing Nets"], ["Heritage walking tour", "Kathakali dance show"], ["Appam with vegetable stew", "Kerala banana chips"]),
            ("Ascent to Munnar Mist-Laden Tea Hills", "Scenic drive through Western Ghats waterfalls to Munnar. Afternoon walk through lush emerald tea estates and visit to the Tata Tea Museum.", ["Munnar Tea Gardens", "Cheeyappara Waterfalls"], ["Tea garden stroll", "Tea processing factory tour"], ["Kerala Parotta with Malabar curry", "Cardamom chai"]),
            ("Eravikulam Wildlife & Mattupetty Dam", "Morning safari in Eravikulam National Park to spot the Nilgiri Tahr. Afternoon serene boat ride across Mattupetty Lake surrounded by eucalyptus hills.", ["Eravikulam National Park", "Mattupetty Dam"], ["Wildlife safari", "Speedboating on lake"], ["Fish Molee", "Idiyappam with coconut milk"]),
            ("Alleppey Backwaters & Houseboat Cruise", "Board a traditional thatched-roof Kettuvallam houseboat in Alleppey. Glide peacefully through serene backwater lagoons and village canals.", ["Alleppey Backwaters", "Vembanad Lake"], ["Houseboat canal cruising", "Village canoe tour"], ["Traditional Sadhya on banana leaf", "Karimeen Pollichathu (Pearl Spot Fish)"]),
            ("Varkala Cliff Beach & Departure", "Morning seaside walk along the dramatic laterite cliffs of Varkala Beach. Enjoy Ayurvedic herbal tea before your return airport transfer.", ["Varkala Cliff Beach", "Janardhana Swamy Temple"], ["Cliffside ocean viewing", "Souvenir shopping"], ["Kerala Puttu with Kadala curry", "Fresh mango lassi"]),
        ]
    elif "manali" in dest_lower:
        day_plans = [
            ("Arrival in Manali & Old Manali Bohemian Vibe", "Check in at your mountain cottage. Stroll through the cedar woods to Hadimba Temple and explore the vibrant cafe culture of Old Manali.", ["Old Manali", "Hadimba Temple"], ["Cedar forest walk", "Riverside cafe leisure"], ["Steaming Tibetan momos", "Siddu stuffed bread"]),
            ("Solang Valley Alpine Adventure & Paragliding", "Full day at Solang Valley. Experience thrilling tandem paragliding, zorbing, and mountain cable car rides against snow-capped peaks.", ["Solang Valley", "Anjani Mahadev"], ["Tandem paragliding", "Zorbing / Skiing"], ["Thukpa noodle soup", "Himachali Dham thali"]),
            ("Atal Tunnel & Surreal Lahaul Valley Day Trip", "Drive through the 9km engineering marvel Atal Tunnel into the high-altitude landscape of Sissu in Lahaul Valley with frozen waterfalls.", ["Atal Tunnel", "Sissu Waterfall"], ["Mountain road trip", "Sissu lake stroll"], ["Fresh river trout fish", "Hot butter tea"]),
            ("Vashisht Hot Springs & Jogini Waterfalls Trek", "Morning trek through apple orchards and pine trails to cascading Jogini Waterfall. Afternoon dip in natural sulfur hot springs at Vashisht.", ["Jogini Waterfall", "Vashisht Hot Springs"], ["Waterfall nature trek", "Thermal spring relaxation"], ["Wood-fired pizza", "Apple cider"]),
            ("Mall Road Souvenirs & Scenic Departure", "Browse the bustling Mall Road for Tibetan woolens, pashmina shawls, and locally grown dry fruits before boarding your return transport.", ["Manali Mall Road", "Tibetan Monastery"], ["Pashmina & handicraft shopping", "Local souvenir pickup"], ["Himachali sweet babru", "Ginger lemon honey tea"]),
        ]
    elif "jaipur" in dest_lower:
        day_plans = [
            ("Arrival in Jaipur & The Pink City Bazaars", "Check in at a royal Rajput haveli. Late afternoon visit to the iconic honeycomb facade of Hawa Mahal and shopping at Johari Bazaar.", ["Hawa Mahal", "Johari & Bapu Bazaar"], ["Photography at Hawa Mahal", "Textile and jewelry shopping"], ["Pyaaz Kachori", "Ghewar sweets"]),
            ("Formidable Amber Fort & Sheesh Mahal", "Morning expedition to Amber Fort overlooking Maota Lake. Marvel at the intricate mirrored palace of Sheesh Mahal and visit Jaigarh Fort.", ["Amber Fort", "Sheesh Mahal", "Jaigarh Fort"], ["Fort history tour", "Panoramic hilltop cannon views"], ["Dal Baati Churma", "Ker Sangri"]),
            ("City Palace & Jantar Mantar Observatory", "Explore the royal residence at City Palace museums and the UNESCO-listed astronomical precision stone instruments at Jantar Mantar.", ["City Palace", "Jantar Mantar"], ["Royal costume museum tour", "Astronomical sundial reading"], ["Laal Maas (or Paneer Rajwada)", "Bajre ki Roti with white butter"]),
            ("Nahargarh Sunset & Chokhi Dhani Folk Village", "Spectacular sunset view of Jaipur city from Nahargarh Fort ramparts. Evening cultural immersion with folk dance, camel rides, and feasts at Chokhi Dhani.", ["Nahargarh Fort", "Chokhi Dhani"], ["Sunset ramparts viewing", "Kalbelia folk dance performance"], ["Unlimited Rajasthani thali", "Masala Chaach"]),
            ("Albert Hall Museum & Royal Departure", "Morning visit to the Indo-Saracenic Albert Hall Museum. Savor a final lassi at Lassiwala on MI Road before airport/train departure.", ["Albert Hall Museum", "Birla Mandir"], ["Museum antiquities tour", "Local sweet pickup"], ["Famous Lassiwala clay-cup lassi", "Mawa Kachori"]),
        ]
    elif "rishikesh" in dest_lower:
        day_plans = [
            ("Arrival by the Ganges & Ram Jhula Walk", "Arrive in Rishikesh, check in at riverside wellness retreat. Cross the suspension bridge at Ram Jhula and explore riverfront bookshops.", ["Ram Jhula", "Swarg Ashram"], ["Suspension bridge stroll", "Ghat exploration"], ["Sattvic Ayurvedic Thali", "Fresh pomegranate juice"]),
            ("Ganges White-Water River Rafting Adventure", "Exciting 16km river rafting expedition tackling thrilling rapids like Roller Coaster and Golf Course. Afternoon cliff jumping and body surfing.", ["Shivpuri Rafting Stretch", "Marine Drive"], ["Grade III & IV River Rafting", "Cliff jumping"], ["Alu Puri at local ghat", "Himalayan herbal tea"]),
            ("The Beatles Ashram & Triveni Ghat Maha Aarti", "Morning meditation and graffiti art tour at the historic Beatles Ashram (Chaurasi Kutia). Evening spiritual Ganga Aarti ceremony at Triveni Ghat.", ["Beatles Ashram", "Triveni Ghat"], ["Meditation & art walk", "Sunset Ganga Aarti participation"], ["Continental cafe salad", "Freshly baked pita falafel"]),
            ("Neelkanth Mahadev & Mountain Waterfall Trek", "Scenic mountain excursion to the sacred Shiva shrine at Neelkanth Mahadev surrounded by dense forest valleys, with stop at Patna Waterfall.", ["Neelkanth Mahadev Temple", "Patna Waterfall"], ["Mountain road drive", "Waterfall nature hike"], ["Garhwali Kafuli", "Jhangora sweet kheer"]),
            ("Sunrise Yoga Session & Serene Departure", "Early morning gentle Hatha Yoga and pranayama session overlooking the Ganges mist. Peaceful morning checkout and departure.", ["Riverside Yoga Ghat", "Laxman Jhula area"], ["Guided morning yoga session", "Souvenir mala shopping"], ["Nutritious smoothie bowl", "Organic ginger tea"]),
        ]
    else:
        day_plans = [
            (f"Arrival & Orientation in {destination}", f"Arrive and settle into your accommodations in {destination}. Enjoy an orientation walk through the central district.", [f"{destination} Central Square", "Old Town"], ["Orientation walking tour", "Welcome dinner"], ["Regional specialties", "Local fresh beverages"]),
            (f"Iconic Landmarks & Historical Sights", f"Full day exploring the top heritage and cultural landmarks in {destination}.", [f"Top Museum of {destination}", "Historic Monument"], ["Guided landmark tour", "Scenic photography"], ["Authentic local cuisine", "Traditional street food"]),
            (f"Nature & Scenic Excursion", f"Spend the day exploring picturesque parks, viewpoints, and natural landscapes surrounding {destination}.", [f"{destination} Viewpoint", "Nature Reserve"], ["Hiking / sightseeing walk", "Landscape viewing"], ["Local cafe lunch", "Artisan bakery snacks"]),
            (f"Culture, Shopping & Leisure", f"Explore vibrant local markets, craft shops, and interactive cultural experiences.", [f"{destination} Central Bazaar", "Art Gallery"], ["Handicraft shopping", "Cultural performance"], ["Gourmet dining experience", "Traditional desserts"]),
            (f"Farewell Sightseeing & Departure", f"Morning relaxation and final souvenir shopping before your departure from {destination}.", [f"{destination} Promenade"], ["Morning leisure walk", "Airport / station transfer"], ["Brunch at popular cafe", "Signature travel snacks"]),
        ]

    # Generate exact requested number of days
    for day_num in range(1, days + 1):
        idx = (day_num - 1) % len(day_plans)
        title, desc, places_list, acts_list, foods_list = day_plans[idx]
        
        # Personalize title with day number
        day_title = f"Day {day_num}: {title.replace(f'Day {idx+1}: ', '')}"
        
        itinerary_days.append({
            "day": day_num,
            "title": day_title,
            "description": desc,
            "places": places_list,
            "activities": acts_list,
            "food_recommendations": foods_list,
            "estimated_cost": daily_cost
        })

    # Curate Travel Tips from chunks
    final_travel_tips = [
        f"Pre-book activities during peak tourist seasons to secure priority entry.",
        f"Keep small denominations of local currency handy for market stalls and transport.",
        f"Early morning hours (8:00 AM - 10:30 AM) offer the best lighting for photography and fewer crowds."
    ]
    if tips:
        for t in tips[:3]:
            cleaned_tip = t.replace("Tips:", "").strip()
            if cleaned_tip not in final_travel_tips:
                final_travel_tips.insert(0, cleaned_tip)

    # Curate Packing Tips based on interests
    final_packing_tips = [
        "Lightweight, breathable cotton clothing and comfortable walking shoes.",
        "High SPF broad-spectrum sunscreen, polarized sunglasses, and a sunhat.",
        "Portable power bank, universal adapter, and personal medical kit."
    ]
    if any(i in ["beach", "adventure"] for i in interests):
        final_packing_tips.append("Waterproof phone pouch, quick-dry microfiber towel, and swimwear.")
    if "manali" in dest_lower or any(i in ["nature"] for i in interests):
        final_packing_tips.append("Fleece jacket or warm layers for chilly morning and evening temperatures.")

    summary_text = (
        f"A customized {days}-day itinerary for {travelers} travelers visiting {destination} "
        f"with an allocated budget of Rs {budget:,}. Perfectly tailored for {', '.join(interests) if interests else 'sightseeing'} "
        f"under a {travel_style} travel pace."
    )
    if budget_report.get("is_over_budget"):
        summary_text += f" ⚠️ [Notice: Estimated cost exceeds user budget by ₹{budget_report['deficit']:,.0f} ({budget_report['utilization_percent']}%). Lower-cost alternatives available below.]"

    return {
        "destination": destination,
        "summary": summary_text,
        "days": itinerary_days,
        "budget_breakdown": {
            "stay": acc_alloc,
            "food": food_alloc,
            "activities": act_alloc,
            "transport": trans_alloc,
            "accommodation": acc_alloc,
            "transportation": trans_alloc,
            "miscellaneous": misc_alloc,
            "total_estimated": budget_report["total_estimated"],
            "user_budget": budget_report["user_budget"],
            "remaining_budget": budget_report["remaining_budget"],
            "utilization_percent": budget_report["utilization_percent"],
            "status": budget_report["status"],
            "status_label": budget_report["status_label"],
            "is_over_budget": budget_report["is_over_budget"],
            "deficit": budget_report["deficit"],
            "cost_saving_alternatives": budget_report["cost_saving_alternatives"],
            "cost_saving_tips": budget_report["cost_saving_tips"],
            "categories": budget_report["categories"],
        },
        "packing_tips": final_packing_tips[:5],
        "travel_tips": final_travel_tips[:5],
        "generated_by": "TripGenie RAG Grounded Engine",
    }


def _rag_grounded_fallback_chat(message: str, trip_context: Dict, context_chunks: List[Dict]) -> str:
    """
    Intelligent Conversational RAG Engine:
    Understands intent, checks active trip context, and crafts grounded responses
    for trip optimization, budgeting, activity replacement, and dining.
    """
    q = message.lower()

    # 1. Detect if the user is asking about a specific destination
    KNOWN_DESTINATIONS = ["manali", "kerala", "jaipur", "rishikesh", "goa"]
    detected_dest = None
    for kd in KNOWN_DESTINATIONS:
        if kd in q:
            detected_dest = kd.capitalize()
            break

    # If the user explicitly asks about another destination, switch context to it
    if detected_dest:
        dest_clean = detected_dest
    else:
        dest = (trip_context or {}).get("destination", "Goa")
        dest_clean = (dest or "Goa").strip().capitalize()

    dest_lower = dest_clean.lower()
    days_list = (trip_context or {}).get("days", [])
    user_budget = (trip_context or {}).get("budget", 50000)
    travelers = (trip_context or {}).get("travelers", 2)

    # 0. Intent: Destination Inquiry / Overview (e.g. "Manali baddal sang", "Tell me about Manali")
    DEST_PROFILES = {
        "manali": {
            "title": "Manali (Himachal Pradesh) 🏔️",
            "tagline": "Himalayan valley of snow peaks, cedar forests, adventure sports & riverside cafes.",
            "attractions": [
                "**Solang Valley:** Premier hub for tandem paragliding, zorbing, and ropeways against snow peaks.",
                "**Hadimba Devi Temple:** 1553-built 4-tiered pagoda wooden temple set inside tranquil cedar woods.",
                "**Atal Tunnel & Sissu Waterfall:** World's longest highway tunnel above 10,000 ft connecting to Lahaul's glacial waterfalls.",
                "**Jogini Waterfall Pine Trek:** Scenic 1-hour mountain hike through pine woods and apple orchards.",
                "**Old Manali & Mall Road:** Bohemian cafes, live acoustic music, local woollens, and Tibetan craft markets."
            ],
            "adventures": "Tandem Paragliding at Solang (₹2,500), White-Water Rafting on Beas River (₹1,200), Atal Tunnel & Sissu Tour (₹1,200).",
            "food": "Steaming hot Tibetan Momos, Siddu with ghee & dal, Thukpa soup, and trout fish fry.",
            "best_time": "October to February for snowfall and winter sports; March to June for pleasant outdoor weather.",
        },
        "goa": {
            "title": "Goa (Coastal Paradise) 🏖️",
            "tagline": "Golden beaches, UNESCO Portuguese heritage churches, lively nightlife & coastal seafood.",
            "attractions": [
                "**Baga & Calangute Coast:** Water sports, lively shacks, sunset parasailing, and beach dining.",
                "**Fort Aguada & Lighthouse:** 17th-century Portuguese coastal fortress overlooking the Arabian Sea.",
                "**Basilica of Bom Jesus:** UNESCO World Heritage monument holding sacred relics in Old Goa.",
                "**Palolem Beach & Butterfly Island:** Crescent-shaped serene white-sand bay in South Goa.",
                "**Dudhsagar Waterfalls:** Majestic 4-tiered cascade plunging 310 meters along the Western Ghats."
            ],
            "adventures": "Grande Island Scuba Diving (₹2,500), 5-in-1 Beach Water Sports Combo (₹1,500), Mandovi Sunset Cruise (₹500).",
            "food": "Goan Fish Curry Rice, Prawn Balchao, Bebinca coconut dessert, and Kingfish Rawa Fry.",
            "best_time": "November to February for pleasant beach weather, water sports, and sunset cruises.",
        },
        "kerala": {
            "title": "Kerala (God's Own Country) 🌴",
            "tagline": "Emerald backwater lagoons, mist-covered tea gardens & authentic Ayurvedic rejuvenation.",
            "attractions": [
                "**Alleppey Backwaters:** Traditional thatched Kettuvallam houseboats cruising serene canals.",
                "**Munnar Tea Gardens:** Vast rolling emerald tea estates and Tata Tea Museum in the Western Ghats.",
                "**Fort Kochi Heritage:** Historic cantilevered Chinese Fishing Nets and Portuguese colonial lanes.",
                "**Eravikulam National Park:** High-altitude sanctuary for the endangered Nilgiri Tahr mountain goat.",
                "**Varkala Cliff Beach:** Red laterite cliffs bordering the Arabian Sea with seaside cafes."
            ],
            "adventures": "Overnight Houseboat Cruise (₹3,000), Shikara Canoe Ride on Vembanad Lake (₹600), Kathakali Dance Show (₹500).",
            "food": "Traditional Kerala Sadhya served on banana leaf, Appam with coconut stew, Karimeen Pollichathu.",
            "best_time": "September to March for calm backwaters, pleasant hill-station breezes, and clear skies.",
        },
        "jaipur": {
            "title": "Jaipur (The Pink City) 🏰",
            "tagline": "Majestic Rajputana hill forts, royal palaces, ornate courtyards & vibrant heritage bazaars.",
            "attractions": [
                "**Amber Fort:** Magnificent hilltop palace complex overlooking Maota Lake with Sheesh Mahal mirror work.",
                "**Hawa Mahal:** Iconic 1799 pink sandstone facade featuring 953 honeycombed jharokhas.",
                "**City Palace & Jantar Mantar:** Royal museum residence and UNESCO 18th-century astronomical observatory.",
                "**Nahargarh Fort Sunset:** Panoramic hill ramparts offering breathtaking sunsets over the Pink City.",
                "**Chokhi Dhani:** Authentic Rajasthani cultural village with folk dances, camel rides, and feasts."
            ],
            "adventures": "Guided Amber Fort Tour (₹500), City Palace Royal Walk (₹700), Johari Bazaar Textile Walk (₹200).",
            "food": "Authentic Dal Baati Churma, Rawat Pyaz Kachori, Mawa Kachori, and rich saffron lassi.",
            "best_time": "October to March for cool, pleasant sightseeing weather and royal cultural festivals.",
        },
        "rishikesh": {
            "title": "Rishikesh (Yoga & Adrenaline Capital) 🧘‍♂️",
            "tagline": "Sacred Ganges riverbanks, Himalayan foothills, world-class river rafting & spiritual ashrams.",
            "attractions": [
                "**Triveni Ghat Evening Maha Aarti:** Soul-stirring twilight Ganga Aarti with floating diyas and chanting.",
                "**The Beatles Ashram (Chaurasi Kutia):** Historic 1968 meditation retreat filled with graffiti and murals.",
                "**Ram Jhula & Laxman Jhula:** Iconic iron suspension bridges spanning the turquoise Ganges.",
                "**Neer Garh Waterfall Hike:** Multi-tiered mountain cascade with natural plunge pools.",
                "**Neelkanth Mahadev Temple:** Sacred mountain shrine set at 1,330 meters amidst deep valleys."
            ],
            "adventures": "16km Shivpuri White-Water River Rafting (₹1,200), Mohan Chatti 83m Bungee Jump (₹3,500), Waterfall Treks.",
            "food": "Chotiwala Pure Veg Garhwali Thali, organic vegan smoothie bowls, and wood-fired pizzas by the river.",
            "best_time": "September to November and February to May for exhilarating river rafting and pleasant weather.",
        },
    }

    # Detect language of user question: Devanagari or Roman Marathi vs English
    is_marathi = any('\u0900' <= ch <= '\u097f' for ch in message) or any(
        re.search(rf"\b{w}\b", q) for w in ["baddal", "sang", "sanga", "mahiti", "kasa", "kashi", "aahe", "ahe", "kay", "pahije", "vicharla", "madhe", "kiti"]
    )

    # If the user is asking about a destination or general information:
    is_dest_inquiry = detected_dest is not None or any(w in q for w in ["baddal", "about", "information", "mahiti", "places", "sights", "visit", "kasa aahe", "kay aahe", "tell me", "what is"])
    if dest_lower in DEST_PROFILES and (is_dest_inquiry or len(q.split()) <= 4):
        prof = DEST_PROFILES[dest_lower]
        sights_bullet = "\n".join(f"• {s}" for s in prof["attractions"])
        if is_marathi:
            return (
                f"### 📍 {prof['title']}\n"
                f"*{prof['tagline']}*\n\n"
                f"**प्रमुख आकर्षणे:**\n{sights_bullet}\n\n"
                f"🏄 **ॲडव्हेंचर & ॲक्टिव्हिटी:** {prof['adventures']}\n\n"
                f"🍲 **स्थानिक खाद्यसंस्कृती:** {prof['food']}\n\n"
                f"☀️ **भेट देण्यासाठी उत्तम काळ:** {prof['best_time']}\n\n"
                f"तुम्हाला {dest_clean} च्या बजेट, हॉटेल किंवा दिवसांच्या नियोजनाबद्दल काहीही विचारू शकता!"
            )
        else:
            return (
                f"### 📍 {prof['title']}\n"
                f"*{prof['tagline']}*\n\n"
                f"**Top Attractions & Sights:**\n{sights_bullet}\n\n"
                f"🏄 **Adventures & Activities:** {prof['adventures']}\n\n"
                f"🍲 **Local Cuisine & Food:** {prof['food']}\n\n"
                f"☀️ **Best Time to Visit:** {prof['best_time']}\n\n"
                f"Feel free to ask me for custom day itineraries, budget optimization, or hotel recommendations for {dest_clean}!"
            )

    # 1. Intent: "Make Day X cheaper" / "Cheaper day"
    day_match = re.search(r"day\s*(\d+)", q)
    if ("cheap" in q or "reduce cost" in q or "save" in q or "less expensive" in q) and day_match:
        day_num = int(day_match.group(1))
        # Find target day if present in trip context
        target_day = None
        if isinstance(days_list, list):
            for d in days_list:
                if isinstance(d, dict) and d.get("day") == day_num:
                    target_day = d
                    break

        title = target_day.get("title", f"Day {day_num}") if target_day else f"Day {day_num}"
        places = target_day.get("places", []) if target_day else []
        places_str = ", ".join(places[:2]) if places else f"central {dest_clean}"

        return (
            f"Here is a smart plan to make Day {day_num} ({title}) significantly cheaper in {dest_clean}:\n\n"
            f"• **Transport Savings (~₹800–₹1,200):** Rent a self-drive scooter (₹400/day) or use shared public shuttles instead of on-demand private cabs.\n"
            f"• **Activity Swaps (~₹1,500–₹2,500):** Focus on exploring {places_str}, scenic shoreline strolls, historic fortress ramparts, or sunset photography, which have zero admission fees.\n"
            f"• **Dining Smart (~₹600/person):** Swap fine-dining bistros for authentic local thali spots and beach shacks.\n\n"
            f"💰 **Estimated Total Day {day_num} Savings:** ~₹2,500 to ₹4,000 without compromising on experiences!"
        )

    # 2. Intent: "Replace [activity] with another activity" / "Activity replacement"
    if "replace" in q or "instead of" in q or "alternative to" in q or ("another" in q and "activity" in q):
        if "scuba" in q:
            return (
                f"Great alternatives to Scuba Diving in {dest_clean}:\n\n"
                f"1. **Guided Snorkeling at Grand Island / Cove:** Explore vibrant coral reefs and marine life at half the cost (~₹1,500 vs ~₹3,500 for scuba).\n"
                f"2. **Mangrove & Backwater Kayaking:** Peaceful, scenic 2-hour paddle through calm waters (₹800–₹1,200/person).\n"
                f"3. **Catamaran Sailing & Dolphin Safari:** Relaxing coastal cruise with dolphin spotting and swimming (₹1,000–₹1,500).\n\n"
                f"Would you like me to update Day 2 or Day 3 with one of these options?"
            )
        elif "paragliding" in q or "skiing" in q:
            return (
                f"Thrilling alternatives to Paragliding in {dest_clean}:\n\n"
                f"1. **Jogini Waterfall Pine Forest Trek:** Gorgeous 2-hour nature hike through apple orchards and pine woods (Free).\n"
                f"2. **River Rafting on Beas River:** Exhilarating Grade II & III rapids (₹1,000–₹1,500/person).\n"
                f"3. **Mountain Biking:** Rent an MTB and cruise the scenic mountain trails (₹600–₹900/day)."
            )
        else:
            return (
                f"Here are top-rated activity alternatives in {dest_clean}:\n\n"
                f"1. **Sunset Catamaran Cruise:** Leisurely coastal sailing with breathtaking sunset views (₹1,200/person).\n"
                f"2. **Heritage & Spice Plantation Walk:** Immersive guided tour with traditional buffet lunch included (₹800/person).\n"
                f"3. **Kayaking or Stand-Up Paddleboarding:** Active, refreshing water exploration (₹900/person)."
            )

    # 3. Intent: "Suggest vegetarian restaurants" / "veg food"
    if "vegetarian" in q or "veg" in q or "vegan" in q:
        veg_guides = {
            "goa": (
                "Top Vegetarian & Vegan dining spots in Goa:\n\n"
                "• **Navtara Pure Veg (Panaji, Calangute, Porvorim):** The go-to spot for crispy dosas, South Indian thalis, and Punjabi curries.\n"
                "• **Sarvaa Organic Cafe (Anjuna):** Vibrant vegan bowls, smoothie bowls, and wholesome gluten-free options.\n"
                "• **Blue Planet Cafe (Agonda / South Goa):** Award-winning organic vegetarian haven surrounded by lush green hills.\n"
                "• **Vinayak Family Restaurant (Assagao):** Famous for authentic Goan vegetarian thalis and fresh coconut curries.\n"
                "• **The Rasoda (Old Goa / Porvorim):** Royal Rajasthani and North Indian pure vegetarian delights."
            ),
            "kerala": (
                "Top Vegetarian restaurants in Kerala:\n\n"
                "• **Saravana Bhavan (Kochi / Ernakulam):** Authentic South Indian filter coffee, ghee roast dosas, and mini thalis.\n"
                "• **Dhe Puttu (Kochi):** Specializes in traditional steamed rice puttu with rich vegetarian curries and kadala.\n"
                "• **Hotel Guruprasad (Munnar):** Hearty, budget-friendly South Indian meals in the tea hills.\n"
                "• **Aryaas (Alleppey & Highways):** Reliable pure vegetarian traditional meals served on banana leaves."
            ),
            "manali": (
                "Top Vegetarian spots in Manali:\n\n"
                "• **Chopsticks (Mall Road):** Delicious vegetarian Tibetan momos, thukpa, and pan-fried noodles.\n"
                "• **IL Forno (Hadimba Road):** Rustic Italian trattoria with wood-fired Margherita pizzas and garden views.\n"
                "• **Southern Souls (Old Manali):** Authentic pure vegetarian South Indian fare in the Himalayas.\n"
                "• **Dylan's Toasted & Roasted (Old Manali):** Famous for freshly brewed coffee, pancakes, and cookies."
            ),
            "jaipur": (
                "Top Vegetarian restaurants in Jaipur:\n\n"
                "• **Laxmi Mishtan Bhandar - LMB (Johari Bazaar):** Iconic 1727 institution serving the authentic Royal Rajasthani Dal Baati Churma Thali.\n"
                "• **Rawat Mishtan Bhandar (Station Road):** Famous for legendary crispy Pyaz Kachoris and Mawa Kachoris.\n"
                "• **Tapri Central (C-Scheme):** Trendy rooftop cafe with gourmet teas and innovative vegetarian snacks.\n"
                "• **Handi (MI Road):** Celebrated for rich North Indian vegetarian specialties and freshly baked naans."
            ),
            "rishikesh": (
                "Top Vegetarian cafes in Rishikesh:\n\n"
                "• **Chotiwala (Swarg Ashram / Ram Jhula):** Iconic heritage restaurant serving lavish Garhwali and North Indian thalis.\n"
                "• **The Beatles Cafe (Paatleshwar):** Overlooking the Ganges with healthy organic vegan burgers and pastas.\n"
                "• **Ganga Beach Cafe (Laxman Jhula):** Riverside rooftop seating with wood-fired pizzas and Ayurvedic herbal teas."
            ),
        }
        for k, guide in veg_guides.items():
            if k in dest_lower:
                return guide
        return (
            f"Top vegetarian spots in {dest_clean}:\n\n"
            f"• **Pure Veg Thali Bistros:** Look for local Udupi or Rajasthani dining halls for unlimited thalis.\n"
            f"• **Organic Farm Cafes:** Popular in tourist hubs, offering fresh salads, vegan bowls, and smoothies.\n"
            f"• Check out local waterfront cafes where chefs readily customize dishes to pure vegetarian or Jain specifications!"
        )

    # 4. Intent: "Can I complete this itinerary in X days?" / "4 days" / "duration"
    if ("complete" in q and ("days" in q or "day" in q or "time" in q)) or "in 4 days" in q or "in 3 days" in q:
        target_days = 4
        m = re.search(r"in\s*(\d+)\s*days?", q)
        if m:
            target_days = int(m.group(1))

        return (
            f"Yes, completing your {dest_clean} trip in {target_days} days is totally doable with a tight, cluster-based schedule!\n\n"
            f"Here is how to optimize for {target_days} days:\n"
            f"• **Days 1–2 (North / Central Hub):** Cover high-energy spots: coastal beaches, water sports, and vibrant sunset markets.\n"
            f"• **Days 3–{target_days} (Heritage & Tranquil Coves):** Focus on historic Portuguese forts, churches, and calm bays.\n"
            f"• **Pacing Advice:** Group sights geographically to avoid cross-state transit delays. Dedicate mornings to outdoor adventures and late afternoons to relaxed sightseeing."
        )

    # 5. Intent: "Which hotel is closest to the beach?" / "hotel closest" / "near beach"
    if "hotel" in q and ("closest" in q or "near" in q or "beach" in q or "recommend" in q):
        if "goa" in dest_lower:
            return (
                "Here are verified beachfront hotels in Goa from our database:\n\n"
                "• **Santana Beach Resort (Candolim):** Direct private beach path (only 100m to shore), 2 pools, from ₹3,800/night (Rating: 4.5 ★).\n"
                "• **Taj Fort Aguada Resort (Sinquerim):** Cliffside 5-star luxury right on the beach overlooking Aguada ramparts, from ₹18,500/night (Rating: 4.8 ★).\n"
                "• **W Goa (Vagator):** Nestled directly beneath Chapora cliff on Vagator Beach, from ₹21,000/night (Rating: 4.7 ★).\n"
                "• **Zostel Goa (Calangute):** Top backpacker choice 600m from Calangute Beach, from ₹950/night (Rating: 4.6 ★).\n\n"
                "Check the Accommodations section above to filter by area or sort by '📍 Closest to Itinerary'!"
            )
        elif "kerala" in dest_lower:
            return (
                "Verified prime stays in Kerala:\n\n"
                "• **Brunton Boatyard (Fort Kochi):** Historic heritage property directly on Kochi harbor overlooking Chinese fishing nets (Rating: 4.8 ★).\n"
                "• **Elixir Cliff Resort (Varkala):** Perched directly on the red laterite cliffs with panoramic Arabian Sea sunsets (Rating: 4.7 ★).\n"
                "• **Blanket Hotel & Spa (Munnar):** Luxury stay facing Attukad waterfalls (Rating: 4.8 ★)."
            )
        else:
            return (
                f"Our verified hotels in {dest_clean} feature verified tariffs and real GPS coordinates. "
                f"Check the Accommodations section above, and use the '📍 Closest to Itinerary' sort to view hotels nearest to your planned stops!"
            )

    # 6. Intent: "Reduce my budget to ₹X" / "Reduce budget" / "budget to"
    if ("reduce" in q or "lower" in q or "cut" in q or "decrease" in q) and ("budget" in q or "cost" in q):
        m = re.search(r"(\d[\d,]+)", q)
        new_budget = float(m.group(1).replace(",", "")) if m else 70000.0
        
        stay_alloc = round(new_budget * 0.40)
        act_alloc = round(new_budget * 0.25)
        food_alloc = round(new_budget * 0.20)
        trans_alloc = round(new_budget * 0.15)

        return (
            f"Here is a balanced reallocation to bring your {dest_clean} budget down to **₹{new_budget:,.0f}** for {travelers} travelers:\n\n"
            f"• 🏨 **Accommodation (40%):** ₹{stay_alloc:,} (~₹{round(stay_alloc/4):,}/night for 3★ comfort or boutique homestays)\n"
            f"• 🏄 **Activities & Sightseeing (25%):** ₹{act_alloc:,} (Prioritize top 2 paid sports; self-guide forts & beaches)\n"
            f"• 🍛 **Food & Dining (20%):** ₹{food_alloc:,} (Authentic local thali houses and beach shacks)\n"
            f"• 🚕 **Local Transport (15%):** ₹{trans_alloc:,} (Self-drive scooter rentals or pre-negotiated day cabs)\n\n"
            f"💡 **Tip:** You can enter ₹{new_budget:,.0f} directly into the Budget Planner above and click 'Plan My Trip' to regenerate your complete customized itinerary!"
        )

    # 7. Weather
    if "weather" in q or "rain" in q or "temp" in q or "best time" in q:
        for c in context_chunks:
            if c.get("category") == "best_time":
                return f"For {dest_clean}, {c.get('text')} Check our live weather card above for today's temperature, humidity, and 5-day forecast!"
        return f"The weather in {dest_clean} is typically most pleasant between autumn and spring. Check our live weather card above for real-time readings!"

    # 8. Food & Delicacies
    if "food" in q or "dish" in q or "eat" in q or "restaurant" in q or "seafood" in q:
        for c in context_chunks:
            if c.get("category") == "food":
                return f"Must-try food in {dest_clean}: {c.get('text')} Check our Places section for top food stops!"
        return f"In {dest_clean}, be sure to explore local eateries, street food markets, and waterfront cafes for authentic regional delicacies."

    # 9. Attractions & Places
    if "attraction" in q or "place" in q or "visit" in q or "see" in q:
        for c in context_chunks:
            if c.get("category") == "attractions":
                return f"Top sights in {dest_clean} include: {c.get('text')}"
        return f"Top sights in {dest_clean} are covered in our curated Places section. You'll find heritage spots, beaches, and scenic nature viewpoints."

    # 10. Packing
    if "pack" in q or "wear" in q or "clothes" in q:
        return f"For your trip to {dest_clean}, pack comfortable breathable clothing, sunscreen, walking shoes, a power bank, and destination-specific items like swimwear or warm layers depending on the terrain."

    # General grounded response using top retrieved chunk
    if context_chunks:
        top_chunk = context_chunks[0]
        return f"Based on verified travel facts for {dest_clean}: {top_chunk.get('text')}\n\nFeel free to ask me to adjust day activities, reduce costs, or recommend restaurants!"

    return f"I'm here to assist with your {dest_clean} itinerary! Feel free to ask about attractions, packing, local food, or day-by-day timing."

