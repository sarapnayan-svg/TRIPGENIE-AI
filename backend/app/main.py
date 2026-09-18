"""
TripGenie AI backend -- Intelligent AI Travel Planner using LLMs + RAG.

Run with:
    uvicorn app.main:app --reload

Endpoints:
    GET  /api/health               -- sanity check & loaded destinations
    GET  /api/destinations         -- destinations covered by the knowledge base
    GET  /api/activities/{dest}    -- available activities catalog for destination
    POST /api/calculate-budget     -- deterministic 5-category budget calculation & alternatives
    POST /api/plan-trip            -- RAG-grounded itinerary generation
    POST /api/chat                 -- RAG-grounded follow-up chat about a trip
"""
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.db_models import User, Trip, Itinerary, SavedPlace, UserPreference
from app.pdf_exporter import build_pdf_buffer
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models import (
    TripRequest, TripResponse, ChatRequest, ChatResponse,
    BudgetEstimateRequest, HotelRecommendRequest, HotelRecommendResponse,
    UserRegister, UserLogin, UserOut, TokenResponse,
    TripSaveRequest, TripListItem, TripDetail,
)
from app.rag import rag_engine
from app.llm import generate_itinerary, chat_response
from app.budget_planner import (
    calculate_trip_budget,
    optimize_budget_parameters,
    DESTINATION_ACTIVITIES,
    GENERIC_ACTIVITIES,
)
from app.weather import fetch_weather
from app.hotels_database import recommend_hotels, VERIFIED_HOTELS

app = FastAPI(title="TripGenie AI", description="RAG-powered travel planner backend with deterministic budget intelligence")


@app.on_event("startup")
def on_startup():
    init_db()

# Production-ready CORS middleware (configurable via CORS_ORIGINS env var)
cors_origins_env = os.getenv("CORS_ORIGINS", "")
allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()] if cors_origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
def api_root():
    """API metadata endpoint for cloud health status and documentation discovery."""
    return {
        "name": "TripGenie AI API",
        "version": "1.0.0",
        "status": "online",
        "health": "/api/health",
        "docs": "/docs",
    }


@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok", "known_destinations": rag_engine.known_destinations()}


@app.get("/api/destinations")
def destinations():
    return {"destinations": rag_engine.known_destinations()}


@app.get("/api/weather")
def get_weather(destination: str):
    """Retrieve real-time meteorological conditions and 5-day forecast."""
    clean = (destination or "").strip()
    if not clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Destination query parameter is required.",
        )
    result = fetch_weather(clean)
    if not result.get("success"):
        raise HTTPException(
            status_code=result.get("status_code", 404),
            detail=result.get("error", "Weather data could not be retrieved."),
        )
    return result


@app.get("/api/activities/{destination}")
def get_activities(destination: str):
    """Retrieve catalog of available activities with real rates for the destination."""
    dest_key = destination.strip().lower()
    catalog = DESTINATION_ACTIVITIES.get(dest_key, GENERIC_ACTIVITIES)
    activities_list = [
        {
            "id": act_id,
            "name": info["name"],
            "cost": info["cost"],
            "category": info["category"],
        }
        for act_id, info in catalog.items()
    ]
    return {"destination": destination, "activities": activities_list}


@app.post("/api/calculate-budget")
def calculate_budget_endpoint(req: BudgetEstimateRequest):
    """Deterministic, transparent 5-category travel budget calculation."""
    if req.budget < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be at least ₹1,000 for realistic trip calculation.",
        )

    report = calculate_trip_budget(
        destination=req.destination,
        days=req.days,
        travelers=req.travelers,
        user_budget=req.budget,
        hotel_preference=req.hotel_preference or "standard",
        transport_preference=req.transport_preference or "private_cab",
        selected_activities=req.selected_activities,
        travel_style=req.travel_style or "balanced",
    )
    return report


@app.post("/api/plan-trip", response_model=TripResponse)
def plan_trip(req: TripRequest):
    # 1. Input Validation
    clean_dest = req.destination.strip()
    if not clean_dest:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Destination field is required and cannot be empty.",
        )

    if req.budget < 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total budget must be at least ₹2,000 to formulate a viable itinerary.",
        )

    # 2. Fuzzy / Substring Destination Normalization
    matched_dest = None
    known = rag_engine.known_destinations()
    for d in known:
        if d.lower() == clean_dest.lower() or d.lower() in clean_dest.lower() or clean_dest.lower() in d.lower():
            matched_dest = d
            break

    target_dest = matched_dest if matched_dest else clean_dest

    # 3. RAG Retrieval
    query = (
        f"{target_dest} trip for {req.days} days, {req.travelers} travelers, budget Rs {req.budget}, "
        f"hotel: {req.hotel_preference or 'standard'}, transport: {req.transport_preference or 'private_cab'}, "
        f"interests: {', '.join(req.interests) if req.interests else 'sightseeing'}, style: {req.travel_style}"
    )
    chunks = rag_engine.retrieve(query, destination=target_dest, k=8)

    # 4. LLM / RAG Itinerary Synthesis with Deterministic Budget Engine
    try:
        result = generate_itinerary(
            destination=target_dest,
            days=req.days,
            travelers=req.travelers,
            budget=req.budget,
            interests=req.interests,
            context_chunks=chunks,
            travel_style=req.travel_style,
            hotel_preference=req.hotel_preference,
            transport_preference=req.transport_preference,
            selected_activities=req.selected_activities,
            start_date=req.start_date,
            end_date=req.end_date,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Itinerary generation encountered an error: {str(e)}",
        )

    result["sources"] = chunks
    return result


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat message cannot be empty.",
        )

    destination = (req.trip or {}).get("destination", "").strip()
    search_query = f"{destination} {req.message.strip()}" if destination and destination.lower() not in req.message.lower() else req.message.strip()
    chunks = rag_engine.retrieve(search_query, destination=destination, k=5)

    history = [{"role": m.role, "content": m.content} for m in req.history]

    try:
        reply = chat_response(
            message=req.message.strip(),
            trip_context=req.trip or {},
            context_chunks=chunks,
            history=history,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Chat generation encountered an error: {str(e)}",
        )

    return {"reply": reply, "sources": chunks}


@app.get("/api/hotels")
def get_hotels(destination: Optional[str] = None):
    """Retrieve catalog of verified hotels, optionally filtered by destination."""
    if destination:
        dest_clean = destination.strip().lower()
        hotels = [
            h for h in VERIFIED_HOTELS
            if dest_clean in h["destination"].lower() or h["destination"].lower() in dest_clean
        ]
        return {"destination": destination, "total": len(hotels), "hotels": hotels}
    return {"total": len(VERIFIED_HOTELS), "hotels": VERIFIED_HOTELS}


@app.post("/api/hotels/recommend", response_model=HotelRecommendResponse)
def recommend_hotels_endpoint(req: HotelRecommendRequest):
    """
    Intelligent hotel recommendation engine considering destination, budget,
    travelers, duration, preferred area, tier, and proximity to itinerary attractions.
    Guarantees authentic verified rates and guest ratings (zero fabrication).
    """
    dest_clean = (req.destination or "").strip()
    if not dest_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Destination is required to recommend hotels.",
        )

    recommendations = recommend_hotels(
        destination=dest_clean,
        budget=req.budget or 30000.0,
        travelers=req.travelers or 2,
        duration=req.duration or 3,
        preferred_area=req.preferred_area,
        tier=req.tier,
        preferences=req.preferences,
        itinerary_places=req.itinerary_places,
        sort_by=req.sort_by or "recommended",
    )
    return recommendations


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/register", response_model=TokenResponse)
def register(req: UserRegister, db: Session = Depends(get_db)):
    """Register a new user, hash password with bcrypt, and return JWT token."""
    email_clean = req.email.strip().lower()
    if not email_clean or "@" not in email_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid email address is required.",
        )

    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please sign in.",
        )

    if len(req.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )

    hashed = hash_password(req.password)
    user = User(
        email=email_clean,
        full_name=req.full_name.strip(),
        hashed_password=hashed,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize default preferences
    pref = UserPreference(user_id=user.id)
    db.add(pref)
    db.commit()

    token = create_access_token({"sub": str(user.id)})
    user_out = UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
        saved_trips_count=0,
    )
    return TokenResponse(access_token=token, token_type="bearer", user=user_out)


@app.post("/api/auth/login", response_model=TokenResponse)
def login(req: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user credentials and issue JWT token."""
    email_clean = req.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Please try again.",
        )

    trips_count = db.query(Trip).filter(Trip.user_id == user.id).count()
    token = create_access_token({"sub": str(user.id)})
    user_out = UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
        saved_trips_count=trips_count,
    )
    return TokenResponse(access_token=token, token_type="bearer", user=user_out)


@app.get("/api/auth/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get profile and trip count of the currently authenticated user."""
    trips_count = db.query(Trip).filter(Trip.user_id == current_user.id).count()
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        saved_trips_count=trips_count,
    )


# ==================== SAVED TRIPS ENDPOINTS ====================

@app.post("/api/trips", response_model=TripDetail)
def save_trip(
    req: TripSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save an AI-generated trip to the user's account."""
    new_trip = Trip(
        user_id=current_user.id,
        destination=req.destination.strip(),
        days_count=req.days_count or len(req.days) or 5,
        travelers_count=req.travelers_count or 2,
        budget=req.budget,
        summary=req.summary,
        budget_breakdown=req.budget_breakdown,
        packing_tips=req.packing_tips,
        travel_tips=req.travel_tips,
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    # Save day-by-day itineraries
    for idx, day_data in enumerate(req.days):
        itin = Itinerary(
            trip_id=new_trip.id,
            day_number=day_data.get("day", idx + 1),
            title=day_data.get("title", f"Day {idx + 1}"),
            description=day_data.get("description", ""),
            places=day_data.get("places", []),
            activities=day_data.get("activities", []),
            food_recommendations=day_data.get("food_recommendations", []),
            estimated_cost=float(day_data.get("estimated_cost", 0.0) or 0.0),
        )
        db.add(itin)

    # Save landmark places
    for p in req.saved_places or []:
        sp = SavedPlace(
            trip_id=new_trip.id,
            name=p.get("name") or p.get("placeName", "Place"),
            category=p.get("category", "Attraction"),
            area=p.get("area", req.destination),
            lat=p.get("lat"),
            lng=p.get("lng"),
            notes=p.get("notes") or p.get("desc"),
        )
        db.add(sp)

    db.commit()
    db.refresh(new_trip)

    return _format_trip_detail(new_trip)


@app.get("/api/trips", response_model=List[TripListItem])
def list_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all saved trips for the authenticated user, ordered newest first."""
    trips = (
        db.query(Trip)
        .filter(Trip.user_id == current_user.id)
        .order_by(Trip.created_at.desc())
        .all()
    )

    items = []
    for t in trips:
        items.append(
            TripListItem(
                id=t.id,
                destination=t.destination,
                days_count=t.days_count,
                travelers_count=t.travelers_count,
                budget=t.budget,
                summary=t.summary,
                created_at=t.created_at.isoformat() if t.created_at else None,
                days_total=len(t.itinerary_days),
                places_count=len(t.saved_places),
            )
        )
    return items


@app.get("/api/trips/{trip_id}", response_model=TripDetail)
def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full details of a saved trip. Enforces strict ownership authorization."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found.",
        )

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to view this trip.",
        )

    return _format_trip_detail(trip)


@app.delete("/api/trips/{trip_id}")
def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a saved trip. Enforces strict ownership authorization."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found.",
        )

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to delete this trip.",
        )

    db.delete(trip)
    db.commit()
    return {"success": True, "message": "Trip deleted successfully."}


def _format_trip_detail(trip: Trip) -> TripDetail:
    """Helper to convert SQLAlchemy Trip model into Pydantic TripDetail."""
    days_data = []
    for itin in trip.itinerary_days:
        days_data.append({
            "day": itin.day_number,
            "title": itin.title,
            "description": itin.description or "",
            "places": itin.places or [],
            "activities": itin.activities or [],
            "food_recommendations": itin.food_recommendations or [],
            "estimated_cost": itin.estimated_cost or 0.0,
        })

    places_data = []
    for sp in trip.saved_places:
        places_data.append({
            "id": sp.id,
            "name": sp.name,
            "category": sp.category,
            "area": sp.area,
            "lat": sp.lat,
            "lng": sp.lng,
            "notes": sp.notes,
        })

    return TripDetail(
        id=trip.id,
        destination=trip.destination,
        days_count=trip.days_count,
        travelers_count=trip.travelers_count,
        budget=trip.budget,
        summary=trip.summary,
        budget_breakdown=trip.budget_breakdown,
        packing_tips=trip.packing_tips or [],
        travel_tips=trip.travel_tips or [],
        days=days_data,
        saved_places=places_data,
        created_at=trip.created_at.isoformat() if trip.created_at else None,
    )


# ==================== PDF EXPORT ENDPOINT ====================

@app.post("/api/export/pdf")
def export_trip_pdf_endpoint(payload: Dict[str, Any]):
    """
    Export a generated travel plan as a professional vector PDF.
    Accepts trip_data, form_data, and hotels, and streams the PDF document.
    """
    trip_data = payload.get("trip_data") or payload.get("tripPlan") or payload
    form_data = payload.get("form_data") or payload.get("formData") or {}
    hotels = payload.get("hotels") or []

    destination = trip_data.get("destination")
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Destination is required to generate a travel dossier PDF.",
        )

    try:
        pdf_buffer = build_pdf_buffer(trip_data, form_data, hotels)
        dest_clean = destination.replace(" ", "_")
        filename = f"TripGenie_{dest_clean}_Itinerary.pdf"

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate travel itinerary PDF: {str(e)}"
        )


# ==================== STATIC REACT SPA MOUNT ====================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="static_assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Pass through API and docs endpoints
        if full_path.startswith("api") or full_path.startswith("docs") or full_path == "openapi.json":
            raise HTTPException(status_code=404, detail="API route not found")

        candidate_file = FRONTEND_DIST / full_path
        if full_path and candidate_file.exists() and candidate_file.is_file():
            return FileResponse(candidate_file)

        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def fallback_root():
        return {
            "name": "TripGenie AI API",
            "version": "1.0.0",
            "status": "online",
            "health": "/api/health",
            "docs": "/docs",
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
