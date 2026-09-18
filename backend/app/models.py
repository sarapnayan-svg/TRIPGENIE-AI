from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class TripRequest(BaseModel):
    destination: str = Field(..., min_length=1, examples=["Goa"])
    days: int = Field(..., ge=1, le=14)
    travelers: int = Field(..., ge=1, le=20)
    budget: int = Field(..., ge=1000)
    interests: List[str] = Field(default_factory=list, examples=[["beach", "food", "adventure"]])
    travel_style: Optional[str] = "balanced"
    hotel_preference: Optional[str] = "standard"  # hostel, budget, standard, premium, luxury
    transport_preference: Optional[str] = "private_cab"  # public, rental, private_cab, flight_premium
    selected_activities: Optional[List[str]] = Field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ItineraryDay(BaseModel):
    day: int
    title: str
    description: str
    places: List[str] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)
    food_recommendations: List[str] = Field(default_factory=list)
    estimated_cost: Optional[float] = None


class BudgetBreakdown(BaseModel):
    # Preserved legacy fields for backward compatibility
    stay: float
    food: float
    activities: float
    transport: float
    
    # Comprehensive 5-category deterministic fields
    accommodation: Optional[float] = None
    transportation: Optional[float] = None
    miscellaneous: Optional[float] = 0.0
    total_estimated: Optional[float] = None
    user_budget: Optional[float] = None
    remaining_budget: Optional[float] = None
    utilization_percent: Optional[float] = None
    status: Optional[str] = "within_budget"
    status_label: Optional[str] = "Within Budget"
    is_over_budget: Optional[bool] = False
    deficit: Optional[float] = 0.0
    cost_saving_alternatives: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    cost_saving_tips: Optional[List[str]] = Field(default_factory=list)
    categories: Optional[Dict[str, Any]] = None


class TripResponse(BaseModel):
    destination: str
    days: List[ItineraryDay]
    budget_breakdown: BudgetBreakdown
    packing_tips: List[str]
    travel_tips: List[str] = Field(default_factory=list)
    summary: str
    sources: List[Dict]  # retrieved chunks used to ground this itinerary, for transparency
    generated_by: Optional[str] = "TripGenie RAG Engine"


class BudgetEstimateRequest(BaseModel):
    destination: str = Field(..., min_length=1, examples=["Goa"])
    days: int = Field(..., ge=1, le=14)
    travelers: int = Field(..., ge=1, le=20)
    budget: float = Field(..., ge=1000)
    hotel_preference: Optional[str] = "standard"
    transport_preference: Optional[str] = "private_cab"
    selected_activities: Optional[List[str]] = Field(default_factory=list)
    travel_style: Optional[str] = "balanced"


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    trip: Optional[Dict] = None
    history: List[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    sources: List[Dict]


class HotelRecommendRequest(BaseModel):
    destination: str = Field(..., min_length=1, examples=["Goa"])
    budget: Optional[float] = Field(default=30000.0, ge=1000)
    travelers: Optional[int] = Field(default=2, ge=1, le=50)
    duration: Optional[int] = Field(default=3, ge=1, le=30)
    preferred_area: Optional[str] = None
    tier: Optional[str] = None
    sort_by: Optional[str] = "recommended"
    itinerary_places: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    preferences: Optional[List[str]] = Field(default_factory=list)


class HotelRecommendResponse(BaseModel):
    destination: str
    total_found: int
    target_nightly_room_budget: float
    recommended_rooms: int
    recommended_nights: int
    hotels: List[Dict[str, Any]]
    verified_source: Optional[str] = "TripGenie Verified Hotel Catalog"


# ==================== AUTH & SAVED TRIPS SCHEMAS ====================

class UserRegister(BaseModel):
    email: str = Field(..., min_length=3, max_length=255, examples=["traveler@example.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["securePass123"])
    full_name: str = Field(..., min_length=1, max_length=255, examples=["Nayan Sarap"])


class UserLogin(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1)


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: Optional[Any] = None
    saved_trips_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TripSaveRequest(BaseModel):
    destination: str = Field(..., min_length=1)
    days_count: Optional[int] = 5
    travelers_count: Optional[int] = 2
    budget: float = Field(..., ge=1000)
    summary: Optional[str] = None
    budget_breakdown: Optional[Dict[str, Any]] = None
    packing_tips: Optional[List[str]] = Field(default_factory=list)
    travel_tips: Optional[List[str]] = Field(default_factory=list)
    days: List[Dict[str, Any]] = Field(default_factory=list)
    saved_places: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class TripListItem(BaseModel):
    id: int
    destination: str
    days_count: int
    travelers_count: int
    budget: float
    summary: Optional[str] = None
    created_at: Optional[Any] = None
    days_total: Optional[int] = 0
    places_count: Optional[int] = 0


class TripDetail(BaseModel):
    id: int
    destination: str
    days_count: int
    travelers_count: int
    budget: float
    summary: Optional[str] = None
    budget_breakdown: Optional[Dict[str, Any]] = None
    packing_tips: Optional[List[str]] = Field(default_factory=list)
    travel_tips: Optional[List[str]] = Field(default_factory=list)
    days: List[Dict[str, Any]] = Field(default_factory=list)
    saved_places: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: Optional[Any] = None


