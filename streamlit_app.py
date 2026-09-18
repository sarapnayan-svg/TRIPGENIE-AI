"""
TripGenie AI — Streamlit Cloud Web Application
Intelligent AI Travel Planner Using Large Language Models (LLM) & RAG.
"""
import os
import sys
from pathlib import Path

# Ensure backend directory is in Python path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="TripGenie AI — Intelligent Travel Planner",
    page_icon="🧞‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for premium look
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .badge-rag {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .card-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Safe imports from TripGenie AI backend
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

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&auto=format&fit=crop&q=80", use_container_width=True)
    st.title("🧞‍♂️ TripGenie AI")
    st.caption("RAG-Grounded Travel Planner with Deterministic Budget Engine")

    # API Key Configuration (Secrets -> Env -> User input)
    anthropic_key = ""
    if "ANTHROPIC_API_KEY" in st.secrets:
        anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    elif os.getenv("ANTHROPIC_API_KEY"):
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    user_api_key = st.text_input(
        "Anthropic API Key",
        value=anthropic_key,
        type="password",
        help="Enter your Claude API key from console.anthropic.com. If left blank, offline RAG fallback will be used."
    )
    if user_api_key:
        os.environ["ANTHROPIC_API_KEY"] = user_api_key

    st.divider()

    # Destination Selection
    dest_options = ["Goa", "Kerala", "Manali", "Jaipur", "Rishikesh"]
    destination = st.selectbox("📍 Select Destination", dest_options, index=0)

    # Travelers & Days
    col_t, col_d = st.columns(2)
    with col_t:
        travelers = st.number_input("👥 Travelers", min_value=1, max_value=20, value=2, step=1)
    with col_d:
        days = st.number_input("📅 Days", min_value=1, max_value=14, value=4, step=1)

    # Budget
    budget = st.number_input("💰 Total Budget (INR ₹)", min_value=2000, max_value=1000000, value=50000, step=5000)

    # Preferences
    travel_style = st.selectbox("🎒 Travel Style", ["budget", "balanced", "luxury"], index=1)
    hotel_tier = st.selectbox("🏨 Hotel Preference", ["hostel", "budget", "standard", "premium", "luxury"], index=2)
    transport_pref = st.selectbox("🚗 Transport Mode", ["public", "rental", "private_cab", "flight_package"], index=1)

    # Curated Activities Multiselect
    dest_key = destination.strip().lower()
    avail_activities = DESTINATION_ACTIVITIES.get(dest_key, GENERIC_ACTIVITIES)
    act_choices = {info["name"]: act_id for act_id, info in avail_activities.items()}
    
    selected_act_names = st.multiselect(
        "🎯 Select Activities",
        options=list(act_choices.keys()),
        default=list(act_choices.keys())[:2] if len(act_choices) >= 2 else list(act_choices.keys())
    )
    selected_act_ids = [act_choices[name] for name in selected_act_names]

    generate_btn = st.button("✨ Generate Grounded Itinerary", type="primary", use_container_width=True)

# ----------------- MAIN CONTENT -----------------
st.markdown('<div class="badge-rag">⚡ RAG Grounded • Sentence-Transformers • Claude 3.5 Sonnet</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-title">Plan Your Perfect Trip to {destination}</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Verifiable travel intelligence: deterministic financial calculations, authentic GPS landmarks, and live meteorological readings without hallucinations.</div>', unsafe_allow_html=True)

if not BACKEND_LOADED:
    st.error(f"Backend module failed to load: {BACKEND_ERROR}")
    st.stop()

# Initialize session state for generated plan
if "trip_plan" not in st.session_state:
    st.session_state["trip_plan"] = None

# Handle Itinerary Generation
if generate_btn or st.session_state["trip_plan"] is None:
    with st.spinner(f"Retrieving verified knowledge chunks & formulating {destination} itinerary..."):
        # 1. RAG Retrieval
        query = f"{destination} trip for {days} days, {travelers} travelers, budget Rs {budget}, hotel: {hotel_tier}, transport: {transport_pref}, style: {travel_style}"
        retrieved_chunks = rag_engine.retrieve(query, destination=destination, k=8)
        
        # 2. LLM Synthesis
        itinerary_data = generate_itinerary(
            destination=destination,
            days=days,
            travelers=travelers,
            budget=budget,
            interests=["sightseeing", "food", "leisure"],
            context_chunks=retrieved_chunks,
            travel_style=travel_style,
            hotel_preference=hotel_tier,
            transport_preference=transport_pref,
            selected_activities=selected_act_ids,
        )
        itinerary_data["sources"] = retrieved_chunks
        st.session_state["trip_plan"] = itinerary_data

trip = st.session_state["trip_plan"]

# ----------------- TABS DISPLAY -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Day-by-Day Plan", 
    "💵 Budget Breakdown", 
    "🏨 Recommended Hotels", 
    "📡 Live Weather", 
    "💬 AI Travel Concierge"
])

# TAB 1: ITINERARY
with tab1:
    st.markdown(f"### 🌴 {trip.get('destination', destination)} Itinerary Summary")
    st.info(trip.get("summary", f"A curated {days}-day expedition crafted for {travelers} travelers."))

    # Export PDF Button
    try:
        pdf_buf = build_pdf_buffer(trip, {"destination": destination, "days": days, "travelers": travelers, "budget": budget}, [])
        st.download_button(
            label="📄 Download Trip Dossier (PDF)",
            data=pdf_buf,
            file_name=f"TripGenie_{destination}_{days}Days_Itinerary.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        pass

    # Render Days
    for d in trip.get("days", []):
        day_num = d.get("day", 1)
        day_title = d.get("title", f"Day {day_num}")
        with st.expander(f"📌 Day {day_num}: {day_title}", expanded=True):
            st.write(d.get("description", ""))
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**📍 Key Sights:**")
                for p in d.get("places", []):
                    st.markdown(f"- {p}")
            with c2:
                st.markdown("**🏄 Activities:**")
                for a in d.get("activities", []):
                    st.markdown(f"- {a}")
            with c3:
                st.markdown("**🍽️ Dining Recommendations:**")
                for f in d.get("food_recommendations", []):
                    st.markdown(f"- {f}")
            
            if d.get("estimated_cost"):
                st.caption(f"Estimated Daily Expense: ₹{int(d.get('estimated_cost')):,}")

    # RAG Grounding Evidence Expander
    sources = trip.get("sources", [])
    if sources:
        with st.expander(f"🛡️ Retrieved Knowledge Base Evidence ({len(sources)} Chunks)", expanded=False):
            st.caption("These document chunks were retrieved via cosine similarity using sentence-transformers/all-MiniLM-L6-v2 to eliminate hallucinations:")
            for s in sources:
                st.markdown(f"**[{s.get('category', 'General').upper()}] {s.get('place_name', destination)}** *(Similarity: {round(s.get('score', 0)*100, 1)}%)*")
                st.markdown(f"> *\"{s.get('text', '')}\"*")

# TAB 2: BUDGET BREAKDOWN
with tab2:
    st.markdown("### 💰 Deterministic 5-Category Budget Allocation")
    
    # Run deterministic calculation
    budget_report = calculate_trip_budget(
        destination=destination,
        days=days,
        travelers=travelers,
        user_budget=budget,
        hotel_preference=hotel_tier,
        transport_preference=transport_pref,
        selected_activities=selected_act_ids,
        travel_style=travel_style,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("User Budget", f"₹{budget_report['user_budget']:,.0f}")
    m2.metric("Total Estimated", f"₹{budget_report['total_estimated']:,.0f}")
    m3.metric("Remaining Cushion", f"₹{budget_report['remaining_budget']:,.0f}")
    m4.metric("Budget Utilization", f"{budget_report['utilization_percent']}%", budget_report['status_label'])

    cats = budget_report.get("categories", {})
    st.markdown("#### Itemized Category Breakdown")
    for cat_key, info in cats.items():
        st.write(f"**{cat_key.capitalize()}**: ₹{info['amount']:,.0f} ({info.get('percent', 0)}%) — *{info.get('calculation_note', '')}*")
        st.progress(min(1.0, info.get('percent', 0) / 100.0))

    if budget_report.get("is_over_budget"):
        st.warning("⚠️ Trip exceeds allocated budget! Consider these auto-generated alternatives:")
        for alt in budget_report.get("cost_saving_alternatives", []):
            st.markdown(f"- **{alt['category']}**: {alt['suggestion']} *(Savings: ₹{alt['potential_savings']:,})*")

# TAB 3: HOTELS
with tab3:
    st.markdown(f"### 🏨 Verified Hotel Intelligence in {destination}")
    hotels_res = recommend_hotels(
        destination=destination,
        budget=budget,
        travelers=travelers,
        duration=days,
        tier=hotel_tier,
        sort_by="recommended"
    )
    hotels = hotels_res.get("hotels", [])
    
    if hotels:
        h_cols = st.columns(min(3, len(hotels)))
        for idx, hotel in enumerate(hotels[:6]):
            col = h_cols[idx % 3]
            with col:
                st.markdown(f"""
                <div class="card-box">
                    <h4>{hotel.get('name')}</h4>
                    <p><b>Area:</b> {hotel.get('area', destination)} | <b>Tier:</b> {hotel.get('tier', 'standard').capitalize()}</p>
                    <p>⭐ <b>{hotel.get('rating', 4.5)}/5.0</b> ({hotel.get('reviews_count', 1200):,} reviews)</p>
                    <p><b>₹{hotel.get('price_per_night', 3500):,}</b> / night</p>
                    <p><small>{hotel.get('curator_note', '')}</small></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hotels matched your exact filters. Showing destination catalog properties.")

# TAB 4: LIVE WEATHER
with tab4:
    st.markdown(f"### 📡 Live Meteorological Observations ({destination})")
    wx = fetch_weather(destination)
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

# TAB 5: AI CHAT
with tab5:
    st.markdown("### 💬 Ask TripGenie AI (Grounded Concierge)")
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hi! I'm your TripGenie AI concierge for {destination}. Ask me anything about sightseeing, seafood spots, timings, or transport!"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question about your trip..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching RAG knowledge base..."):
                chat_chunks = rag_engine.retrieve(f"{destination} {prompt}", destination=destination, k=4)
                reply = chat_response(
                    message=prompt,
                    trip_context=trip,
                    context_chunks=chat_chunks,
                    history=st.session_state.messages[:-1]
                )
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
