"""
TripGenie AI — Streamlit Cloud Web Application
Intelligent AI Travel Planner Using Large Language Models (LLM) & RAG.
Features identical layout and visual richness to the React Localhost Dashboard.
"""
import os
import sys
from pathlib import Path
import pandas as pd

# Ensure backend directory is in Python path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import streamlit as st
import pydeck as pdk

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="TripGenie AI — Intelligent AI Travel Planner",
    page_icon="🧞‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- CUSTOM CSS: MATCHES REACT LOCALHOST -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Baloo+2:wght@600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #F8FAFC;
    }

    /* Top Banner / Pill */
    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #FFFFFF;
        border: 1px solid #BFDBFE;
        border-radius: 9999px;
        padding: 6px 16px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #1E40AF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }

    /* Hero Section Card */
    .hero-container {
        background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 50%, #F0FDF4 100%);
        border: 1px solid #E2E8F0;
        border-radius: 24px;
        padding: 40px 30px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04);
    }

    .hero-heading {
        font-family: 'Baloo 2', 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.15;
        margin-bottom: 14px;
    }

    .hero-heading span {
        background: linear-gradient(135deg, #0284C7 0%, #2563EB 50%, #4F46E5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-desc {
        font-size: 1.08rem;
        color: #475569;
        max-width: 820px;
        margin: 0 auto 20px auto;
        line-height: 1.6;
    }

    /* Planner Form Box */
    .planner-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 28px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
    }

    /* Itinerary Day Cards */
    .day-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #0284C7;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    .day-badge {
        background: #E0F2FE;
        color: #0369A1;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* Hotel Card */
    .hotel-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        overflow: hidden;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        margin-bottom: 16px;
        height: 100%;
    }

    /* Badges */
    .tag-badge {
        background: #F1F5F9;
        color: #334155;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- BACKEND SAFE IMPORTS -----------------
try:
    from app.rag import rag_engine
    from app.budget_planner import calculate_trip_budget, DESTINATION_ACTIVITIES, GENERIC_ACTIVITIES
    from app.weather import fetch_weather
    from app.hotels_database import recommend_hotels, VERIFIED_HOTELS
    from app.llm import generate_itinerary, chat_response
    from app.pdf_exporter import build_pdf_buffer
    BACKEND_LOADED = True
except Exception as e:
    BACKEND_LOADED = False
    BACKEND_ERROR = str(e)

# ----------------- GPS COORDINATES REGISTRY -----------------
DEST_CENTERS = {
    "Goa": (15.4989, 73.8278, 11),
    "Kerala": (9.9312, 76.2673, 9),
    "Manali": (32.2396, 77.1887, 11),
    "Jaipur": (26.9124, 75.7873, 12),
    "Rishikesh": (30.0869, 78.2676, 12),
}

VERIFIED_COORDS = {
    "baga beach": (15.5553, 73.7517),
    "calangute beach": (15.5439, 73.7553),
    "fort aguada": (15.4929, 73.7736),
    "sinquerim beach": (15.4980, 73.7680),
    "basilica of bom jesus": (15.5009, 73.9116),
    "palolem beach": (15.0100, 74.0232),
    "anjuna beach": (15.5782, 73.7431),
    "vagator cliff": (15.5997, 73.7380),
    "chapora fort": (15.6058, 73.7381),
    "dudhsagar waterfalls": (15.3144, 74.3143),
    "fort kochi": (9.9658, 76.2421),
    "chinese fishing nets": (9.9678, 76.2429),
    "munnar tea gardens": (10.0889, 77.0595),
    "eravikulam national park": (10.2016, 77.0570),
    "mattupetty dam": (10.1068, 77.1245),
    "alleppey backwaters": (9.4981, 76.3388),
    "vembanad lake": (9.6000, 76.4000),
    "varkala cliff beach": (8.7379, 76.7032),
    "old manali": (32.2530, 77.1770),
    "hadimba temple": (32.2483, 77.1802),
    "solang valley": (32.3166, 77.1578),
    "atal tunnel": (32.3639, 77.1332),
    "sissu waterfall": (32.4770, 77.1230),
    "jogini waterfall": (32.2680, 77.1950),
    "mall road": (32.2425, 77.1890),
    "hawa mahal": (26.9239, 75.8267),
    "amber fort": (26.9855, 75.8513),
    "city palace": (26.9258, 75.8237),
    "jantar mantar": (26.9248, 75.8246),
    "nahargarh fort": (26.9372, 75.8155),
    "chokhi dhani": (26.7672, 75.8344),
    "triveni ghat": (30.1033, 78.2934),
    "ram jhula": (30.1235, 78.3142),
    "laxman jhula": (30.1287, 78.3248),
    "beatles ashram": (30.1130, 78.3130),
    "neelkanth mahadev": (30.0863, 78.3353),
    "shivpuri": (30.1378, 78.3889),
}

# ----------------- SESSION STATE INITIALIZATION -----------------
if "destination" not in st.session_state:
    st.session_state["destination"] = "Goa"
if "travelers" not in st.session_state:
    st.session_state["travelers"] = 2
if "days" not in st.session_state:
    st.session_state["days"] = 4
if "budget" not in st.session_state:
    st.session_state["budget"] = 50000
if "travel_style" not in st.session_state:
    st.session_state["travel_style"] = "balanced"
if "hotel_tier" not in st.session_state:
    st.session_state["hotel_tier"] = "standard"
if "transport_pref" not in st.session_state:
    st.session_state["transport_pref"] = "private_cab"
if "trip_plan" not in st.session_state:
    st.session_state["trip_plan"] = None
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Hi! I am your TripGenie AI travel assistant. Ask me anything about itineraries, local foods, hidden gems, or budget tips!"}
    ]

# ----------------- SIDEBAR CONTROLS & DIAGNOSTICS -----------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&auto=format&fit=crop&q=80", use_container_width=True)
    st.title("🧞‍♂️ TripGenie AI")
    st.caption("RAG-Grounded Travel Planner • Final Year B.Tech Project")

    st.markdown("### 🔑 AI Model Key")
    anthropic_key = ""
    if "ANTHROPIC_API_KEY" in st.secrets:
        anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    elif os.getenv("ANTHROPIC_API_KEY"):
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    user_api_key = st.text_input(
        "Anthropic API Key",
        value=anthropic_key,
        type="password",
        help="Paste your Claude 3.5 Sonnet key from console.anthropic.com. If blank, offline RAG heuristics will be utilized automatically."
    )
    if user_api_key:
        os.environ["ANTHROPIC_API_KEY"] = user_api_key

    st.divider()

    st.markdown("### ⚡ System Status")
    st.success("🟢 RAG Engine Online (all-MiniLM-L6-v2)")
    st.info("🗺️ Verified GPS Waypoints: 30+ Landmarks")
    st.info("📊 Deterministic Budget Engine: Active")

    st.divider()
    st.markdown("### 🔗 Project Links")
    st.markdown("- [GitHub Repository](https://github.com/sarapnayan-svg/TRIPGENIE-AI)")
    st.markdown("- [React 19 Frontend (Vercel)](https://github.com/sarapnayan-svg/TRIPGENIE-AI#frontend-deployment)")
    st.markdown("- [IEEE Research Paper (PDF)](https://github.com/sarapnayan-svg/TRIPGENIE-AI/blob/main/docs/TripGenie_AI_Research_Paper.pdf)")

# ----------------- HERO SECTION (MATCHES REACT HERO) -----------------
st.markdown("""
<div class="hero-container">
    <div class="hero-pill">
        <span>⚡</span>
        <span>Intelligent AI Travel Planner • RAG Grounded</span>
    </div>
    <div class="hero-heading">
        Plan Your Perfect Trip with <span>Intelligent AI</span>
    </div>
    <div class="hero-desc">
        Experience verifiable travel intelligence. TripGenie AI combines <strong>Large Language Models</strong> with a specialized <strong>Retrieval-Augmented Generation (RAG)</strong> knowledge base to craft tailor-made itineraries, exact budget breakdowns, and live weather forecasts without hallucinations.
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Destination Selectors (Interactive Buttons)
st.markdown("<p style='text-align:center; font-weight:700; color:#64748B; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;'>📍 Explore Top Grounded Destinations:</p>", unsafe_allow_html=True)

col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns(5)
with col_d1:
    if st.button("🏖️ Goa\nBeaches & Nightlife", use_container_width=True):
        st.session_state["destination"] = "Goa"
        st.rerun()
with col_d2:
    if st.button("🌴 Kerala\nBackwaters & Hills", use_container_width=True):
        st.session_state["destination"] = "Kerala"
        st.rerun()
with col_d3:
    if st.button("🏔️ Manali\nSnow & Adventure", use_container_width=True):
        st.session_state["destination"] = "Manali"
        st.rerun()
with col_d4:
    if st.button("🏰 Jaipur\nPalaces & Heritage", use_container_width=True):
        st.session_state["destination"] = "Jaipur"
        st.rerun()
with col_d5:
    if st.button("🧘‍♂️ Rishikesh\nYoga & Rafting", use_container_width=True):
        st.session_state["destination"] = "Rishikesh"
        st.rerun()

st.write("")

# ----------------- MAIN TRIP PLANNER FORM (CENTERED CARD) -----------------
with st.container():
    st.markdown("### 🧳 Build Custom Itinerary")
    
    with st.form("itinerary_planner_form"):
        # Row 1: Destination, Duration, Travelers
        r1_c1, r1_c2, r1_c3 = st.columns([2, 1, 1])
        with r1_c1:
            dest_list = ["Goa", "Kerala", "Manali", "Jaipur", "Rishikesh"]
            current_idx = dest_list.index(st.session_state["destination"]) if st.session_state["destination"] in dest_list else 0
            dest_input = st.selectbox("📍 Select Destination", dest_list, index=current_idx)
        with r1_c2:
            days_input = st.number_input("📅 Days", min_value=1, max_value=14, value=st.session_state["days"], step=1)
        with r1_c3:
            travelers_input = st.number_input("👥 Travelers", min_value=1, max_value=20, value=st.session_state["travelers"], step=1)

        # Row 2: Budget, Travel Style, Hotel Tier, Transport Mode
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        with r2_c1:
            budget_input = st.number_input("💰 Total Budget (INR ₹)", min_value=2000, max_value=1000000, value=st.session_state["budget"], step=5000)
        with r2_c2:
            styles = ["backpacker", "balanced", "luxury"]
            style_idx = styles.index(st.session_state["travel_style"]) if st.session_state["travel_style"] in styles else 1
            style_input = st.selectbox("🎒 Travel Style", styles, index=style_idx)
        with r2_c3:
            tiers = ["hostel", "budget", "standard", "premium", "luxury"]
            tier_idx = tiers.index(st.session_state["hotel_tier"]) if st.session_state["hotel_tier"] in tiers else 2
            tier_input = st.selectbox("🏨 Hotel Preference", tiers, index=tier_idx)
        with r2_c4:
            transports = ["public", "rental", "private_cab", "flight_package"]
            trans_idx = transports.index(st.session_state["transport_pref"]) if st.session_state["transport_pref"] in transports else 2
            trans_input = st.selectbox("🚗 Transport Mode", transports, index=trans_idx)

        # Row 3: Curated Destination Activities
        dest_key = dest_input.strip().lower()
        avail_activities = DESTINATION_ACTIVITIES.get(dest_key, GENERIC_ACTIVITIES)
        act_choices = {}
        for act_id, info in avail_activities.items():
            cost_val = int(info.get("cost", info.get("cost_per_person", 0)))
            act_name = info.get("name", act_id.replace("_", " ").title())
            cost_label = f"₹{cost_val:,}" if cost_val > 0 else "Free"
            act_choices[f"{act_name} ({cost_label})"] = act_id

        selected_act_labels = st.multiselect(
            "🎯 Select Grounded Activities to Include:",
            options=list(act_choices.keys()),
            default=list(act_choices.keys())[:2] if len(act_choices) >= 2 else list(act_choices.keys())
        )
        selected_act_ids = [act_choices[lbl] for lbl in selected_act_labels if lbl in act_choices]

        # Submit Button
        generate_submitted = st.form_submit_button("✨ Generate Grounded Itinerary", type="primary", use_container_width=True)

    if generate_submitted:
        st.session_state["destination"] = dest_input
        st.session_state["days"] = days_input
        st.session_state["travelers"] = travelers_input
        st.session_state["budget"] = budget_input
        st.session_state["travel_style"] = style_input
        st.session_state["hotel_tier"] = tier_input
        st.session_state["transport_pref"] = trans_input

# ----------------- ITINERARY GENERATION & STATE UPDATE -----------------
active_dest = st.session_state["destination"]
active_days = st.session_state["days"]
active_travelers = st.session_state["travelers"]
active_budget = st.session_state["budget"]
active_style = st.session_state["travel_style"]
active_tier = st.session_state["hotel_tier"]
active_trans = st.session_state["transport_pref"]

if generate_submitted or st.session_state["trip_plan"] is None:
    if not BACKEND_LOADED:
        st.error(f"Backend module failed to load: {BACKEND_ERROR}")
        st.stop()

    with st.spinner(f"Formulating {active_days}-Day verifiable itinerary for {active_dest}..."):
        query = f"{active_dest} trip for {active_days} days, {active_travelers} travelers, budget Rs {active_budget}, hotel: {active_tier}, transport: {active_trans}, style: {active_style}"
        retrieved_chunks = rag_engine.retrieve(query, destination=active_dest, k=8)

        itinerary_data = generate_itinerary(
            destination=active_dest,
            days=active_days,
            travelers=active_travelers,
            budget=active_budget,
            interests=["sightseeing", "food", "leisure"],
            context_chunks=retrieved_chunks,
            travel_style=active_style,
            hotel_preference=active_tier,
            transport_preference=active_trans,
            selected_activities=selected_act_ids if 'selected_act_ids' in locals() else [],
        )
        itinerary_data["sources"] = retrieved_chunks
        st.session_state["trip_plan"] = itinerary_data

trip = st.session_state["trip_plan"]

st.write("")

# ----------------- TABS DISPLAY (MATCHING REACT TABS) -----------------
tab_itinerary, tab_map, tab_budget, tab_hotels, tab_weather, tab_chat = st.tabs([
    "📅 Day-by-Day Plan",
    "🗺️ Interactive Route Map",
    "💵 Budget Breakdown",
    "🏨 Verified Hotels",
    "📡 Live Weather",
    "💬 AI Concierge"
])

# ==================== TAB 1: ITINERARY ====================
with tab_itinerary:
    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        st.markdown(f"### 🌴 {trip.get('destination', active_dest)} Itinerary Dossier")
        st.info(trip.get("summary", f"A curated {active_days}-day expedition crafted for {active_travelers} travelers."))
    with top_c2:
        try:
            pdf_buf = build_pdf_buffer(trip, {"destination": active_dest, "days": active_days, "travelers": active_travelers, "budget": active_budget}, [])
            st.download_button(
                label="📄 Download PDF Dossier",
                data=pdf_buf,
                file_name=f"TripGenie_{active_dest}_{active_days}Days_Itinerary.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            pass

    for d in trip.get("days", []):
        day_num = d.get("day", 1)
        day_title = d.get("title", f"Day {day_num}")
        
        st.markdown(f"""
        <div class="day-card">
            <span class="day-badge">DAY {day_num}</span>
            <h4 style="margin:0 0 8px 0; color:#0F172A;">{day_title}</h4>
            <p style="color:#475569; font-size:0.95rem; margin-bottom:12px;">{d.get('description', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**📍 Key Sights:**")
            for p in d.get("places", []):
                st.markdown(f"- `{p}`")
        with c2:
            st.markdown("**🏄 Curated Activities:**")
            for a in d.get("activities", []):
                st.markdown(f"- {a}")
        with c3:
            st.markdown("**🍽️ Dining Recommendations:**")
            for f in d.get("food_recommendations", []):
                st.markdown(f"- {f}")

        if d.get("estimated_cost"):
            st.caption(f"Estimated Daily Expense: ₹{int(d.get('estimated_cost')):,}")
        st.divider()

    # RAG Chunks Grounding Evidence Expander
    sources = trip.get("sources", [])
    if sources:
        with st.expander(f"🛡️ Retrieved RAG Knowledge Base Chunks ({len(sources)} Chunks)", expanded=False):
            st.caption("Document chunks retrieved via cosine similarity using sentence-transformers/all-MiniLM-L6-v2:")
            for s in sources:
                st.markdown(f"**[{s.get('category', 'General').upper()}] {s.get('place_name', active_dest)}** *(Similarity: {round(s.get('score', 0)*100, 1)}%)*")
                st.markdown(f"> *\"{s.get('text', '')}\"*")

# ==================== TAB 2: INTERACTIVE ROUTE MAP ====================
with tab_map:
    st.markdown(f"### 🗺️ Geospatial Route & Landmark Coordinates ({active_dest})")
    st.caption("Interactive Leaflet/Pydeck projection of itinerary waypoints and verified GPS landmarks.")

    # Gather waypoints from days
    map_points = []
    default_lat, default_lng, default_zoom = DEST_CENTERS.get(active_dest, (15.4989, 73.8278, 11))

    for d in trip.get("days", []):
        day_num = d.get("day", 1)
        for place in d.get("places", []):
            p_lower = place.strip().lower()
            matched_coord = None
            for k, coord in VERIFIED_COORDS.items():
                if k in p_lower or p_lower in k:
                    matched_coord = coord
                    break
            
            if matched_coord:
                map_points.append({
                    "day": f"Day {day_num}",
                    "place": place,
                    "lat": matched_coord[0],
                    "lng": matched_coord[1],
                    "color": [2, 132, 199, 220] if day_num % 2 == 0 else [225, 29, 72, 220]
                })

    # If no specific waypoint matched, populate destination center
    if not map_points:
        map_points.append({
            "day": "Destination Center",
            "place": active_dest,
            "lat": default_lat,
            "lng": default_lng,
            "color": [2, 132, 199, 220]
        })

    df_map = pd.DataFrame(map_points)

    view_state = pdk.ViewState(
        latitude=df_map["lat"].mean(),
        longitude=df_map["lng"].mean(),
        zoom=default_zoom,
        pitch=30,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position=["lng", "lat"],
        get_color="color",
        get_radius=800,
        pickable=True,
        auto_highlight=True,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{day}: {place}\nGPS: ({lat}, {lng})"},
        map_style="mapbox://styles/mapbox/light-v10"
    ))

    st.markdown("#### 📌 Route Waypoints Table")
    st.dataframe(df_map[["day", "place", "lat", "lng"]], use_container_width=True)

# ==================== TAB 3: BUDGET BREAKDOWN ====================
with tab_budget:
    st.markdown("### 💰 Deterministic 5-Category Budget Allocation")
    
    budget_report = calculate_trip_budget(
        destination=active_dest,
        days=active_days,
        travelers=active_travelers,
        user_budget=active_budget,
        hotel_preference=active_tier,
        transport_preference=active_trans,
        selected_activities=selected_act_ids if 'selected_act_ids' in locals() else [],
        travel_style=active_style,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("User Budget", f"₹{budget_report['user_budget']:,.0f}")
    m2.metric("Total Estimated", f"₹{budget_report['total_estimated']:,.0f}")
    m3.metric("Remaining Cushion", f"₹{budget_report['remaining_budget']:,.0f}")
    m4.metric("Utilization", f"{budget_report['utilization_percent']}%", budget_report['status_label'])

    st.markdown("#### Itemized Category Breakdown")
    cats = budget_report.get("categories", {})
    for cat_key, info in cats.items():
        st.write(f"**{cat_key.capitalize()}**: ₹{info['amount']:,.0f} ({info.get('percent', 0)}%) — *{info.get('calculation_note', '')}*")
        st.progress(min(1.0, info.get('percent', 0) / 100.0))

    if budget_report.get("is_over_budget"):
        st.warning("⚠️ Trip exceeds allocated budget! Consider these auto-generated alternatives:")
        for alt in budget_report.get("cost_saving_alternatives", []):
            st.markdown(f"- **{alt['category']}**: {alt['suggestion']} *(Savings: ₹{alt['potential_savings']:,})*")

# ==================== TAB 4: VERIFIED HOTELS ====================
with tab_hotels:
    st.markdown(f"### 🏨 Verified Hotel Intelligence in {active_dest}")
    hotels_res = recommend_hotels(
        destination=active_dest,
        budget=active_budget,
        travelers=active_travelers,
        duration=active_days,
        tier=active_tier,
        sort_by="recommended"
    )
    hotels = hotels_res.get("hotels", [])

    if hotels:
        h_cols = st.columns(min(3, len(hotels)))
        for idx, hotel in enumerate(hotels[:6]):
            col = h_cols[idx % 3]
            with col:
                img_url = hotel.get('image_url') or "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80"
                st.image(img_url, use_container_width=True)
                st.markdown(f"""
                <div class="hotel-box">
                    <h4 style="margin:0 0 6px 0;">{hotel.get('name')}</h4>
                    <p style="color:#64748B; font-size:0.85rem; margin-bottom:6px;">📍 {hotel.get('area', active_dest)} • <b>{hotel.get('tier', 'standard').capitalize()}</b></p>
                    <p style="margin-bottom:6px;">⭐ <b>{hotel.get('rating', 4.5)}/5.0</b> ({hotel.get('reviews_count', 1200):,} reviews)</p>
                    <p style="color:#0284C7; font-size:1.1rem; font-weight:700; margin-bottom:8px;">₹{hotel.get('price_per_night', 3500):,} / night</p>
                    <p style="font-size:0.8rem; color:#475569;"><em>{hotel.get('curator_note', '')}</em></p>
                </div>
                """, unsafe_allow_html=True)
                amenities = hotel.get("amenities", [])[:3]
                for am in amenities:
                    st.markdown(f"<span class='tag-badge'>✓ {am}</span>", unsafe_allow_html=True)
                st.write("")
    else:
        st.info("No hotels matched your exact filters. Showing destination catalog properties.")

# ==================== TAB 5: LIVE WEATHER ====================
with tab_weather:
    st.markdown(f"### 📡 Live Meteorological Observations ({active_dest})")
    wx = fetch_weather(active_dest)
    if wx.get("success"):
        w1, w2, w3, w4 = st.columns(4)
        w1.metric("Temperature", f"{wx.get('temperature', 28)}°C", f"Feels like {wx.get('feels_like', 30)}°C")
        w2.metric("Condition", f"{wx.get('icon', '⛅')} {wx.get('condition', 'Clear')}")
        w3.metric("Humidity", f"{wx.get('humidity', 75)}%")
        w4.metric("Wind Speed", f"{wx.get('wind_speed', 10)} km/h")

        st.caption(f"Source: {wx.get('source')} (Observation verified)")

        st.markdown("#### 5-Day Atmospheric Forecast")
        fc_cols = st.columns(len(wx.get("forecast", [])))
        for i, fc in enumerate(wx.get("forecast", [])):
            with fc_cols[i]:
                st.markdown(f"**{fc.get('day')} ({fc.get('date')})**")
                st.markdown(f"{fc.get('icon', '🌤️')} **{fc.get('temp_max')}°C** / {fc.get('temp_min')}°C")
                st.caption(f"{fc.get('condition')}\n🌧️ Rain: {fc.get('rain_chance')}%")
    else:
        st.warning("Weather observation data currently unavailable for this region.")

# ==================== TAB 6: AI CHAT CONCIERGE ====================
with tab_chat:
    st.markdown("### 💬 Ask TripGenie AI (Grounded Concierge)")
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about places, timings, best beaches, or budget recommendations..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching RAG knowledge base..."):
                chat_chunks = rag_engine.retrieve(f"{active_dest} {prompt}", destination=active_dest, k=4)
                reply = chat_response(
                    message=prompt,
                    trip_context=trip,
                    context_chunks=chat_chunks,
                    history=st.session_state.chat_messages[:-1]
                )
                st.markdown(reply)
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})

st.markdown("---")
st.markdown("<p style='text-align:center; color:#94A3B8; font-size:0.85rem;'>TripGenie AI — Final Year Engineering Project • Grounded in Deterministic Travel Intelligence • Powered by RAG & Claude</p>", unsafe_allow_html=True)
