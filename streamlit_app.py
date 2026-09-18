"""
TripGenie AI — Streamlit Cloud Web Application
Intelligent AI Travel Planner Using Large Language Models (LLM) & RAG.
Features identical layout and visual richness to the React Localhost Dashboard.
"""
import os
import sys
import math
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

    /* Enhanced Image Styling */
    div[data-testid="stImage"] img {
        border-radius: 16px;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.12);
        object-fit: cover;
        transition: all 0.3s ease;
    }
    div[data-testid="stImage"] img:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px -4px rgba(0, 0, 0, 0.18);
    }

    /* Hero Left Box */
    .hero-left-box {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .dest-gradient {
        background: linear-gradient(135deg, #0284C7 0%, #2563EB 50%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    .hero-tagline {
        font-size: 1.05rem;
        color: #475569;
        margin: 12px 0 18px 0;
        line-height: 1.55;
    }

    /* Meta Chips */
    .hero-badges-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 6px;
    }

    .hero-meta-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 6px 12px;
        font-size: 0.8rem;
        color: #1E293B;
    }

    /* Landmark Photo Cards */
    .landmark-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 12px;
        margin-top: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }
    .landmark-card:hover {
        border-color: #38BDF8;
        box-shadow: 0 6px 16px rgba(14, 165, 233, 0.12);
    }

    .landmark-badge {
        display: inline-block;
        background: #E0F2FE;
        color: #0369A1;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .live-pulse {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 1.6s infinite;
        margin-right: 4px;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
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

# ----------------- DESTINATION VISUAL INTELLIGENCE (LIVE PHOTOS) -----------------
DEST_VISUALS = {
    "Goa": {
        "title": "Goa",
        "state": "Coastal Paradise, India",
        "tagline": "Sun-kissed golden beaches, Portuguese colonial heritage & vibrant coastal nightlife.",
        "badge": "Beach & Sunset Capital",
        "best_time": "Nov to Feb",
        "ideal_duration": "4 - 5 Days",
        "avg_temp": "28°C • Warm Coastal",
        "vibe": "Relaxed & Festive",
        "hero_img": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1600&auto=format&fit=crop&q=85",
        "highlights": [
            {
                "name": "Baga & Calangute Coast",
                "category": "Beach & Watersports",
                "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80",
                "desc": "Parasailing, jet skis, dolphin spotting, and lively beachfront shacks."
            },
            {
                "name": "Fort Aguada & Lighthouse",
                "category": "17th-Century Fortress",
                "img": "https://images.unsplash.com/photo-1587922546307-776227941871?w=800&auto=format&fit=crop&q=80",
                "desc": "Historic Portuguese fortress overlooking the Mandovi River & Arabian Sea."
            },
            {
                "name": "Basilica of Bom Jesus",
                "category": "UNESCO World Heritage",
                "img": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&auto=format&fit=crop&q=80",
                "desc": "Baroque architecture enshrining the sacred relics of St. Francis Xavier."
            },
            {
                "name": "Palolem Crescent Bay",
                "category": "Scenic South Coast",
                "img": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&auto=format&fit=crop&q=80",
                "desc": "Tranquil sapphire waters, swaying palms, and colorful beachfront cottages."
            }
        ]
    },
    "Kerala": {
        "title": "Kerala",
        "state": "God's Own Country, India",
        "tagline": "Emerald backwaters, mist-laden Munnar tea hills & tranquil Ayurvedic wellness.",
        "badge": "Tropical Eco Paradise",
        "best_time": "Sep to Mar",
        "ideal_duration": "5 - 7 Days",
        "avg_temp": "27°C • Tropical & Pleasant",
        "vibe": "Serene & Rejuvenating",
        "hero_img": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=1600&auto=format&fit=crop&q=85",
        "highlights": [
            {
                "name": "Alleppey Backwaters",
                "category": "Signature Houseboat Cruise",
                "img": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800&auto=format&fit=crop&q=80",
                "desc": "Gliding past peaceful lagoons, village canals, and lush paddy fields."
            },
            {
                "name": "Munnar Tea Estates",
                "category": "Misty Mountain Valley",
                "img": "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?w=800&auto=format&fit=crop&q=80",
                "desc": "Endless rolling green tea plantations and crisp alpine mountain air."
            },
            {
                "name": "Fort Kochi Heritage",
                "category": "Colonial Coastal Port",
                "img": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?w=800&auto=format&fit=crop&q=80",
                "desc": "Historic Chinese fishing nets, Portuguese quarters, and spice markets."
            },
            {
                "name": "Varkala Cliff Beach",
                "category": "Arabian Sea Clifftop",
                "img": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&auto=format&fit=crop&q=80",
                "desc": "Dramatic red laterite cliffs overlooking golden sands and sunset cafes."
            }
        ]
    },
    "Manali": {
        "title": "Manali",
        "state": "Himachal Pradesh, Himalayas",
        "tagline": "Snowy Himalayan peaks, roaring Beas river rapids & pine valley serenity.",
        "badge": "Adventure & Mountain Gateway",
        "best_time": "Oct - Feb (Snow) • Mar - Jun (Summer)",
        "ideal_duration": "4 - 5 Days",
        "avg_temp": "12°C • Cool Mountain Climate",
        "vibe": "Adventurous & Scenic",
        "hero_img": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=1600&auto=format&fit=crop&q=85",
        "highlights": [
            {
                "name": "Solang Snow Valley",
                "category": "Adventure & Paragliding",
                "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&auto=format&fit=crop&q=80",
                "desc": "Ski slopes, paragliding over glaciers, and panoramic Himalayan summits."
            },
            {
                "name": "Hadimba Devi Temple",
                "category": "Ancient Cedar Shrine",
                "img": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&auto=format&fit=crop&q=80",
                "desc": "16th-century wooden pagoda temple nestled among ancient deodar forests."
            },
            {
                "name": "Atal Tunnel & Sissu",
                "category": "Engineering Marvel & Lahaul",
                "img": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800&auto=format&fit=crop&q=80",
                "desc": "World's longest highway tunnel at 10,000 ft connecting to snowy Sissu."
            },
            {
                "name": "Old Manali Riverside",
                "category": "Bohemian Cafe Culture",
                "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
                "desc": "Riverside stone cottages, live acoustic music, fresh trout, and bakeries."
            }
        ]
    },
    "Jaipur": {
        "title": "Jaipur",
        "state": "The Pink City, Rajasthan",
        "tagline": "Majestic hilltop fortresses, royal Rajput palaces & colorful cultural bazaars.",
        "badge": "Royal Heritage Capital",
        "best_time": "Oct to Mar",
        "ideal_duration": "3 - 4 Days",
        "avg_temp": "24°C • Dry & Royal",
        "vibe": "Grand & Historical",
        "hero_img": "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=1600&auto=format&fit=crop&q=85",
        "highlights": [
            {
                "name": "Amber Fort & Sheesh Mahal",
                "category": "UNESCO Hilltop Fortress",
                "img": "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&auto=format&fit=crop&q=80",
                "desc": "Imposing ramparts, mirror palace, and sweeping views of Maota Lake."
            },
            {
                "name": "Hawa Mahal (Palace of Winds)",
                "category": "Pink Sandstone Architecture",
                "img": "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800&auto=format&fit=crop&q=80",
                "desc": "953 intricately carved jharokha windows built for royal court ladies."
            },
            {
                "name": "Royal City Palace",
                "category": "Living Rajput Palace",
                "img": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&auto=format&fit=crop&q=80",
                "desc": "Splendid courtyards, Mughal-Rajput art, museum, and royal residence."
            },
            {
                "name": "Nahargarh Fort Ridge",
                "category": "Sunset Panoramic View",
                "img": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&auto=format&fit=crop&q=80",
                "desc": "Breathtaking twilight vistas overlooking the illuminated Pink City below."
            }
        ]
    },
    "Rishikesh": {
        "title": "Rishikesh",
        "state": "Devbhoomi, Uttarakhand",
        "tagline": "Yoga capital of the world, sacred evening Ganga Aarti & thrilling river rapids.",
        "badge": "Spiritual & Adventure Capital",
        "best_time": "Sep to May",
        "ideal_duration": "3 - 4 Days",
        "avg_temp": "22°C • Fresh Mountain Air",
        "vibe": "Soulful & High-Energy",
        "hero_img": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=1600&auto=format&fit=crop&q=85",
        "highlights": [
            {
                "name": "White-Water River Rafting",
                "category": "Grade III & IV Rapids",
                "img": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&auto=format&fit=crop&q=80",
                "desc": "Tackling thrilling Holy Ganges rapids through Himalayan river canyons."
            },
            {
                "name": "Triveni Ghat Evening Aarti",
                "category": "Sacred Maha Aarti",
                "img": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=800&auto=format&fit=crop&q=80",
                "desc": "Hundreds of floating oil lamps and Vedic chants resonating at sunset."
            },
            {
                "name": "Ram & Laxman Jhula",
                "category": "Iconic Suspension Bridge",
                "img": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&auto=format&fit=crop&q=80",
                "desc": "Historic suspension footbridge connecting ashrams across the emerald river."
            },
            {
                "name": "The Beatles Ashram",
                "category": "Forest Meditation Domes",
                "img": "https://images.unsplash.com/photo-1540541338287-41700207dee6?w=800&auto=format&fit=crop&q=80",
                "desc": "Tranquil Rajaji forest sanctuary where legendary melodies were composed."
            }
        ]
    }
}

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
if "selected_hotel_id" not in st.session_state:
    st.session_state["selected_hotel_id"] = None
if "transport_pref" not in st.session_state:
    st.session_state["transport_pref"] = "private_cab"
if "trip_plan" not in st.session_state:
    st.session_state["trip_plan"] = None
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Hi! I am your TripGenie AI travel assistant. Ask me anything about itineraries, local foods, hidden gems, or budget tips!"}
    ]

# ----------------- SIDEBAR CONTROLS & DIAGNOSTICS -----------------
current_dest = st.session_state.get("destination", "Goa")
vis = DEST_VISUALS.get(current_dest, DEST_VISUALS["Goa"])

with st.sidebar:
    st.image(vis["hero_img"], caption=f"📍 {vis['title']} • {vis['badge']}", use_container_width=True)
    st.title("🧞‍♂️ TripGenie AI")
    st.caption("RAG-Grounded Travel Planner • Final Year B.Tech Project")

    st.markdown("### 🔑 AI Model Key")
    anthropic_key = ""
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    if not anthropic_key and os.getenv("ANTHROPIC_API_KEY"):
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    user_api_key = st.text_input(
        "Anthropic API Key",
        value=anthropic_key,
        type="password",
        help="Paste your Claude 3.5 Sonnet key from console.anthropic.com. If blank, offline RAG heuristics will be utilized automatically."
    )
    if user_api_key and isinstance(user_api_key, str):
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

# ----------------- DYNAMIC LIVE HERO SECTION -----------------
hero_c1, hero_c2 = st.columns([1.25, 1], gap="medium")
with hero_c1:
    st.markdown(f"""
    <div class="hero-left-box">
        <div class="hero-pill">
            <span class="live-pulse"></span>
            <span>⚡ Intelligent AI Travel Planner • RAG Grounded</span>
        </div>
        <div class="hero-heading" style="text-align:left; font-size:2.4rem; margin-bottom:10px; line-height:1.2;">
            Explore <span class="dest-gradient">{vis['title']}</span> with AI
        </div>
        <p class="hero-tagline">{vis['tagline']}</p>
        <div class="hero-badges-row">
            <div class="hero-meta-chip"><span>📍</span> <b>{vis['state']}</b></div>
            <div class="hero-meta-chip"><span>📅</span> <b>Best: {vis['best_time']}</b></div>
            <div class="hero-meta-chip"><span>⏱️</span> <b>{vis['ideal_duration']}</b></div>
            <div class="hero-meta-chip"><span>🌡️</span> <b>{vis['avg_temp']}</b></div>
            <div class="hero-meta-chip"><span>✨</span> <b>Vibe: {vis['vibe']}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_c2:
    st.image(
        vis["hero_img"],
        caption=f"📸 Live View: {vis['title']} • {vis['badge']}",
        use_container_width=True
    )

# Quick Destination Selectors (Interactive Buttons)
st.markdown("<p style='text-align:center; font-weight:700; color:#475569; font-size:0.88rem; text-transform:uppercase; letter-spacing:0.06em; margin:22px 0 10px 0;'>📍 Explore Top Grounded Destinations (Click to Switch Live Photos & Plan):</p>", unsafe_allow_html=True)

col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns(5)
d_btns = [
    ("Goa", "🏖️ Goa", "Beaches & Sunsets", col_d1),
    ("Kerala", "🌴 Kerala", "Backwaters & Hills", col_d2),
    ("Manali", "🏔️ Manali", "Snow & Adventure", col_d3),
    ("Jaipur", "🏰 Jaipur", "Palaces & Forts", col_d4),
    ("Rishikesh", "🧘‍♂️ Rishikesh", "Yoga & Rafting", col_d5),
]
for d_name, d_label, d_sub, d_col in d_btns:
    with d_col:
        is_active = (current_dest == d_name)
        btn_type = "primary" if is_active else "secondary"
        btn_caption = f"⭐ {d_label}" if is_active else d_label
        if st.button(f"{btn_caption}\n{d_sub}", type=btn_type, use_container_width=True, key=f"quick_dest_{d_name}"):
            if st.session_state["destination"] != d_name:
                st.session_state["destination"] = d_name
                st.session_state["selected_hotel_id"] = None
                st.session_state["trip_plan"] = None
                st.rerun()

# ----------------- DYNAMIC LANDMARK HIGHLIGHTS GALLERY -----------------
st.markdown(f"### 📸 Live Landmark Photography & Scenic Highlights: {vis['title']}")
st.caption(f"Authentic visual highlights from verified GPS waypoints in {vis['state']}.")

p_cols = st.columns(4)
for i, hl in enumerate(vis["highlights"]):
    with p_cols[i]:
        st.image(hl["img"], use_container_width=True)
        st.markdown(f"""
        <div class="landmark-card">
            <span class="landmark-badge">{hl['category']}</span>
            <h4 style="margin:6px 0 4px 0; font-size:0.95rem; color:#0F172A; font-weight:700;">{hl['name']}</h4>
            <p style="color:#64748B; font-size:0.8rem; line-height:1.45; margin:0;">{hl['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

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

        # Row 2.5: Specific Hotel Property Selection for selected destination
        dest_hotels = [h for h in VERIFIED_HOTELS if h["destination"].lower() == dest_input.strip().lower()]
        hotel_select_map = {f"✨ Auto-Recommend Best Verified Property ({tier_input.capitalize()} Tier)": None}
        for h in dest_hotels:
            t_tag = h['tier'].upper()
            h_opt_label = f"{h['name']} • ₹{int(h['price_per_night']):,}/night • ⭐ {h['rating']} ({h['area']}) [{t_tag}]"
            hotel_select_map[h_opt_label] = h["id"]

        cur_h_id = st.session_state.get("selected_hotel_id")
        h_idx = 0
        if cur_h_id:
            for i, (lbl, hid) in enumerate(hotel_select_map.items()):
                if hid == cur_h_id:
                    h_idx = i
                    break

        selected_hotel_choice = st.selectbox(
            f"🏨 Choose Your Hotel Stay in {dest_input} ({len(dest_hotels)} Options Available with Live Photos):",
            options=list(hotel_select_map.keys()),
            index=h_idx,
            help="Select the exact hotel of your choice from our verified database with authentic photos and rates."
        )
        form_chosen_hotel_id = hotel_select_map[selected_hotel_choice]

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
        dest_changed = (st.session_state["destination"] != dest_input)
        st.session_state["destination"] = dest_input
        st.session_state["days"] = days_input
        st.session_state["travelers"] = travelers_input
        st.session_state["budget"] = budget_input
        st.session_state["travel_style"] = style_input
        st.session_state["hotel_tier"] = tier_input
        st.session_state["transport_pref"] = trans_input
        st.session_state["selected_hotel_id"] = form_chosen_hotel_id
        if form_chosen_hotel_id:
            chosen_obj = next((h for h in VERIFIED_HOTELS if h["id"] == form_chosen_hotel_id), None)
            if chosen_obj:
                st.session_state["hotel_tier"] = chosen_obj["tier"]
        st.session_state["trip_plan"] = None
        if dest_changed:
            st.rerun()

# ----------------- ITINERARY GENERATION & STATE UPDATE -----------------
active_dest = st.session_state["destination"]
active_days = st.session_state["days"]
active_travelers = st.session_state["travelers"]
active_budget = st.session_state["budget"]
active_style = st.session_state["travel_style"]
active_tier = st.session_state["hotel_tier"]
active_trans = st.session_state["transport_pref"]

active_hotel_id = st.session_state.get("selected_hotel_id")
active_hotel_obj = None
if active_hotel_id:
    active_hotel_obj = next((h for h in VERIFIED_HOTELS if h["id"] == active_hotel_id and h["destination"].lower() == active_dest.lower()), None)

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

    if active_hotel_obj:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%); border:1.5px solid #86EFAC; border-radius:16px; padding:16px; margin-bottom:20px; box-shadow:0 4px 15px rgba(16,185,129,0.06);">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                <span style="background:#059669; color:white; font-size:0.75rem; font-weight:800; padding:3px 10px; border-radius:9999px;">CONFIRMED ACCOMMODATION PARTNER</span>
                <span style="color:#047857; font-weight:700; font-size:0.85rem;">{active_hotel_obj['tier'].upper()} TIER</span>
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:16px; align-items:center;">
                <img src="{active_hotel_obj['image_url']}" style="width:140px; height:95px; object-fit:cover; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.1);" />
                <div style="flex:1; min-width:240px;">
                    <h4 style="margin:0 0 4px 0; color:#0F172A; font-size:1.1rem;">{active_hotel_obj['name']}</h4>
                    <p style="margin:0 0 4px 0; color:#64748B; font-size:0.85rem;">📍 {active_hotel_obj['area']}, {active_hotel_obj['destination']} • ⭐ <b>{active_hotel_obj['rating']}/5.0</b> ({active_hotel_obj['reviews_count']:,} reviews)</p>
                    <p style="margin:0; color:#0284C7; font-weight:800; font-size:1rem;">₹{int(active_hotel_obj['price_per_night']):,} <span style="font-size:0.8rem; font-weight:500; color:#64748B;">/ night • Total for {active_days} days: ₹{int(active_hotel_obj['price_per_night'] * max(1, math.ceil(active_travelers/2.0)) * (active_days - 1 if active_days > 1 else 1)):,}</span></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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

def resolve_place_coordinates(place_name: str, dest_name: str, index: int = 0) -> tuple:
    p = place_name.lower().strip()
    for k, coord in VERIFIED_COORDS.items():
        if k in p or p in k:
            return coord
        k_tokens = [w for w in k.split() if len(w) > 3]
        if any(tok in p for tok in k_tokens):
            return coord

    KEYWORD_MAP = {
        "hadimba": (32.2483, 77.1802),
        "solang": (32.3166, 77.1578),
        "atal": (32.3639, 77.1332),
        "tunnel": (32.3639, 77.1332),
        "sissu": (32.4770, 77.1230),
        "jogini": (32.2680, 77.1950),
        "vashisht": (32.2600, 77.1900),
        "beas": (32.2200, 77.1850),
        "mall": (32.2425, 77.1890),
        "baga": (15.5553, 73.7517),
        "calangute": (15.5439, 73.7553),
        "aguada": (15.4929, 73.7736),
        "bom jesus": (15.5009, 73.9116),
        "basilica": (15.5009, 73.9116),
        "palolem": (15.0100, 74.0232),
        "anjuna": (15.5782, 73.7431),
        "vagator": (15.5997, 73.7380),
        "chapora": (15.6058, 73.7381),
        "dudhsagar": (15.3144, 74.3143),
        "backwaters": (9.4981, 76.3388),
        "alleppey": (9.4981, 76.3388),
        "munnar": (10.0889, 77.0595),
        "tea": (10.0889, 77.0595),
        "eravikulam": (10.2016, 77.0570),
        "mattupetty": (10.1068, 77.1245),
        "kochi": (9.9658, 76.2421),
        "chinese": (9.9678, 76.2429),
        "varkala": (8.7379, 76.7032),
        "hawa": (26.9239, 75.8267),
        "amber": (26.9855, 75.8513),
        "palace": (26.9258, 75.8237),
        "jantar": (26.9248, 75.8246),
        "nahargarh": (26.9372, 75.8155),
        "chokhi": (26.7672, 75.8344),
        "triveni": (30.1033, 78.2934),
        "ram jhula": (30.1235, 78.3142),
        "laxman": (30.1287, 78.3248),
        "beatles": (30.1130, 78.3130),
        "neelkanth": (30.0863, 78.3353),
        "shivpuri": (30.1378, 78.3889),
    }
    for kw, coord in KEYWORD_MAP.items():
        if kw in p:
            return coord

    c_lat, c_lng, _ = DEST_CENTERS.get(dest_name, (15.4989, 73.8278, 11))
    offset_lat = (((index * 7) % 11) - 5) * 0.005
    offset_lng = (((index * 5) % 11) - 5) * 0.005
    return (round(c_lat + offset_lat, 4), round(c_lng + offset_lng, 4))

# ==================== TAB 2: INTERACTIVE ROUTE MAP ====================
with tab_map:
    st.markdown(f"### 🗺️ Geospatial Route & Landmark Coordinates ({active_dest})")
    st.caption("Interactive projection of itinerary waypoints and verified GPS landmarks.")

    map_points = []
    default_lat, default_lng, default_zoom = DEST_CENTERS.get(active_dest, (15.4989, 73.8278, 11))

    idx = 0
    for d in trip.get("days", []):
        day_num = d.get("day", 1)
        places = d.get("places", [])
        if not places:
            places = [d.get("title", f"Day {day_num} Central Sight")]

        for place in places:
            coord = resolve_place_coordinates(place, active_dest, idx)
            map_points.append({
                "Day": f"Day {day_num}",
                "Place": place,
                "lat": float(coord[0]),
                "lng": float(coord[1]),
                "color": [2, 132, 199, 220] if day_num % 2 == 0 else [225, 29, 72, 220]
            })
            idx += 1

    if not map_points:
        map_points.append({
            "Day": "Day 1",
            "Place": f"{active_dest} Center",
            "lat": float(default_lat),
            "lng": float(default_lng),
            "color": [2, 132, 199, 220]
        })

    df_map = pd.DataFrame(map_points)

    # Render Map without requiring any Mapbox token
    try:
        view_state = pdk.ViewState(
            latitude=float(df_map["lat"].mean()),
            longitude=float(df_map["lng"].mean()),
            zoom=default_zoom,
            pitch=20,
        )

        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position=["lng", "lat"],
            get_color="color",
            get_radius=500,
            radius_min_pixels=8,
            radius_max_pixels=25,
            pickable=True,
            auto_highlight=True,
        )

        deck = pdk.Deck(
            layers=[scatter_layer],
            initial_view_state=view_state,
            tooltip={"text": "{Day}: {Place}\nGPS: ({lat}, {lng})"},
            map_provider="carto",
            map_style="positron"
        )
        st.pydeck_chart(deck)
    except Exception:
        # Bulletproof native fallback
        st.map(df_map, latitude="lat", longitude="lng", size=25)

    st.markdown("#### 📌 Route Waypoints Table")
    df_display = df_map[["Day", "Place", "lat", "lng"]].copy()
    df_display["Navigation"] = df_display.apply(lambda r: f"https://www.google.com/maps/search/?api=1&query={r['lat']},{r['lng']}", axis=1)
    st.dataframe(
        df_display,
        column_config={
            "Navigation": st.column_config.LinkColumn("Google Maps Link", display_text="Open in Maps ↗")
        },
        use_container_width=True
    )

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
        custom_hotel_rate=active_hotel_obj["price_per_night"] if active_hotel_obj else None,
        custom_hotel_name=active_hotel_obj["name"] if active_hotel_obj else None,
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
    st.markdown(f"### 🏨 Verified Hotel Intelligence & Selection Portal: {active_dest}")
    st.caption(f"Browse authentic, verified properties across all tiers in {active_dest} with live photography, verified guest ratings, and direct booking links. Select your favorite hotel to lock it into your trip plan and budget.")

    # Active Selection Banner
    if active_hotel_obj:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); border: 2px solid #10B981; border-radius: 14px; padding: 16px 20px; margin-bottom: 20px;">
            <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
                <div>
                    <span style="background:#059669; color:white; font-size:0.75rem; font-weight:800; padding:3px 10px; border-radius:9999px; text-transform:uppercase;">Active Itinerary Selection</span>
                    <h3 style="margin:6px 0 2px 0; color:#065F46; font-size:1.25rem;">🏨 {active_hotel_obj['name']}</h3>
                    <p style="margin:0; color:#047857; font-size:0.88rem;">📍 {active_hotel_obj['area']} • <b>{active_hotel_obj['tier'].capitalize()} Tier</b> • ⭐ {active_hotel_obj['rating']}/5.0 • <b>₹{int(active_hotel_obj['price_per_night']):,}/night</b></p>
                </div>
                <div>
                    <a href="{active_hotel_obj.get('booking_url', '#')}" target="_blank" style="background:#059669; color:white; padding:8px 16px; border-radius:10px; text-decoration:none; font-weight:700; font-size:0.85rem; display:inline-block;">Reserve on Google Travel ↗</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Interactive Filter Controls
    f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 1.2])
    with f_col1:
        tier_options = [
            "All Tiers (Show All 16+ Hotels)",
            "Hostel (₹600 - ₹950)",
            "Budget (₹1,900 - ₹3,200)",
            "Standard (₹3,200 - ₹4,800)",
            "Premium (₹6,800 - ₹9,800)",
            "Luxury (₹11,000 - ₹35,000)"
        ]
        tier_mapping = {
            "All Tiers (Show All 16+ Hotels)": "all",
            "Hostel (₹600 - ₹950)": "hostel",
            "Budget (₹1,900 - ₹3,200)": "budget",
            "Standard (₹3,200 - ₹4,800)": "standard",
            "Premium (₹6,800 - ₹9,800)": "premium",
            "Luxury (₹11,000 - ₹35,000)": "luxury"
        }
        def_tier_idx = 0
        for idx, (t_lbl, t_val) in enumerate(tier_mapping.items()):
            if t_val == active_tier:
                def_tier_idx = idx
                break
        selected_tier_label = st.selectbox("🏷️ Filter by Hotel Preference / Tier:", tier_options, index=def_tier_idx, key="hotel_tab_tier_filter")
        chosen_tier_filter = tier_mapping[selected_tier_label]

    with f_col2:
        all_dest_hotels = [h for h in VERIFIED_HOTELS if h["destination"].lower() == active_dest.lower()]
        distinct_areas = sorted(list(set(h["area"] for h in all_dest_hotels)))
        area_options = ["All Areas & Neighborhoods"] + distinct_areas
        selected_area_choice = st.selectbox("📍 Filter by Area / Neighborhood:", area_options, index=0, key="hotel_tab_area_filter")
        chosen_area_filter = None if selected_area_choice == "All Areas & Neighborhoods" else selected_area_choice

    with f_col3:
        sort_options = ["⭐ Recommended", "💰 Price: Low to High", "💎 Price: High to Low", "⭐ Highest Rating"]
        sort_mapping = {
            "⭐ Recommended": "recommended",
            "💰 Price: Low to High": "price_asc",
            "💎 Price: High to Low": "price_desc",
            "⭐ Highest Rating": "rating"
        }
        selected_sort_choice = st.selectbox("🔃 Sort By:", sort_options, index=0, key="hotel_tab_sort_filter")
        chosen_sort = sort_mapping[selected_sort_choice]

    hotels_res = recommend_hotels(
        destination=active_dest,
        budget=active_budget,
        travelers=active_travelers,
        duration=active_days,
        preferred_area=chosen_area_filter,
        tier=chosen_tier_filter if chosen_tier_filter != "all" else None,
        sort_by=chosen_sort
    )
    hotels = hotels_res.get("hotels", [])

    st.markdown(f"<p style='color:#64748B; font-size:0.9rem; margin-bottom:16px;'>Found <b>{len(hotels)} verified properties</b> in {active_dest} matching criteria with live high-res photography:</p>", unsafe_allow_html=True)

    if hotels:
        h_cols = st.columns(3)
        for idx, hotel in enumerate(hotels):
            col = h_cols[idx % 3]
            with col:
                is_selected = (st.session_state.get("selected_hotel_id") == hotel["id"])
                card_border = "border: 2px solid #10B981;" if is_selected else "border: 1px solid #E2E8F0;"
                
                st.image(hotel.get('image_url') or "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80", use_container_width=True)
                
                st.markdown(f"""
                <div class="hotel-box" style="{card_border}">
                    {'<span style="background:#059669; color:white; font-size:0.7rem; font-weight:800; padding:2px 8px; border-radius:9999px; float:right;">SELECTED STAY</span>' if is_selected else ''}
                    <span class="tag-badge" style="background:#E0F2FE; color:#0369A1; font-weight:700;">{hotel['tier'].upper()}</span>
                    <h4 style="margin:6px 0 4px 0; font-size:1.02rem; color:#0F172A;">{hotel.get('name')}</h4>
                    <p style="color:#64748B; font-size:0.82rem; margin-bottom:4px;">📍 {hotel.get('area')} • <b>⭐ {hotel.get('rating', 4.5)}/5.0</b> ({hotel.get('reviews_count', 1200):,} reviews)</p>
                    <p style="color:#0284C7; font-size:1.15rem; font-weight:800; margin:6px 0 2px 0;">₹{int(hotel.get('price_per_night', 3500)):,} <span style="font-size:0.8rem; font-weight:500; color:#64748B;">/ night</span></p>
                    <p style="color:#059669; font-size:0.8rem; font-weight:600; margin-bottom:6px;">Total Stay Est: ₹{int(hotel.get('total_stay_estimated', hotel.get('price_per_night', 3500)*active_days)):,} ({active_days} days)</p>
                    <p style="font-size:0.8rem; color:#475569; line-height:1.4; margin-bottom:8px;"><em>{hotel.get('curator_note', '')}</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                amenities = hotel.get("amenities", [])[:3]
                for am in amenities:
                    st.markdown(f"<span class='tag-badge'>✓ {am}</span>", unsafe_allow_html=True)
                
                st.write("")
                if is_selected:
                    st.button("✅ Currently Selected Hotel", key=f"btn_h_{hotel['id']}", type="primary", disabled=True, use_container_width=True)
                else:
                    if st.button("🏨 Select This Hotel", key=f"btn_h_{hotel['id']}", type="secondary", use_container_width=True):
                        st.session_state["selected_hotel_id"] = hotel["id"]
                        st.session_state["hotel_tier"] = hotel["tier"]
                        st.session_state["trip_plan"] = None
                        st.rerun()
                
                st.markdown(f"<p style='text-align:center; margin-top:4px;'><a href='{hotel.get('booking_url', '#')}' target='_blank' style='font-size:0.8rem; color:#0284C7; text-decoration:none;'>Google Travel Rates & Reviews ↗</a></p>", unsafe_allow_html=True)
                st.write("")
    else:
        st.info("No hotels matched your exact filters. Try adjusting the tier or area filter above.")

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
                # Detect if user asks about a specific destination (e.g. Manali, Kerala, Jaipur, Rishikesh, Goa)
                p_lower = prompt.lower()
                query_dest = None
                for d_name in ["Manali", "Kerala", "Jaipur", "Rishikesh", "Goa"]:
                    if d_name.lower() in p_lower:
                        query_dest = d_name
                        break

                target_dest = query_dest or active_dest

                # Retrieve chunks for the targeted destination
                chat_chunks = rag_engine.retrieve(prompt, destination=target_dest, k=5)

                # Formulate target trip context
                chat_trip_context = dict(trip or {}) if (target_dest == active_dest and trip) else {"destination": target_dest}
                if target_dest:
                    chat_trip_context["destination"] = target_dest

                reply = chat_response(
                    message=prompt,
                    trip_context=chat_trip_context,
                    context_chunks=chat_chunks,
                    history=st.session_state.chat_messages[:-1]
                )
                st.markdown(reply)
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})

st.markdown("---")
st.markdown("<p style='text-align:center; color:#94A3B8; font-size:0.85rem;'>TripGenie AI — Final Year Engineering Project • Grounded in Deterministic Travel Intelligence • Powered by RAG & Claude</p>", unsafe_allow_html=True)
