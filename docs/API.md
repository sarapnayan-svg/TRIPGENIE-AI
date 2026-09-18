# API Documentation — TripGenie AI

TripGenie AI provides a RESTful API powered by FastAPI. All requests and responses use JSON (except binary PDF exports).

---

## 1. System & Health Endpoints

### 1.1 Root Metadata
- **Method**: `GET`
- **Path**: `/`
- **Purpose**: System discovery and API documentation reference.
- **Request**: None
- **Response** (`200 OK`):
  ```json
  {
    "name": "TripGenie AI API",
    "version": "1.0.0",
    "status": "online",
    "health": "/api/health",
    "docs": "/docs"
  }
  ```

### 1.2 Health Check
- **Method**: `GET`
- **Path**: `/health` and `/api/health`
- **Purpose**: Sanity check for load balancers and container orchestrators.
- **Request**: None
- **Response** (`200 OK`):
  ```json
  {
    "status": "ok",
    "known_destinations": ["Goa", "Jaipur", "Kerala", "Manali", "Rishikesh"]
  }
  ```

---

## 2. Travel Planning & Intelligence

### 2.1 Get Known Destinations
- **Method**: `GET`
- **Path**: `/api/destinations`
- **Purpose**: Retrieve list of unique destinations covered in the RAG vector store.
- **Response** (`200 OK`):
  ```json
  {
    "destinations": ["Goa", "Jaipur", "Kerala", "Manali", "Rishikesh"]
  }
  ```

### 2.2 Live Meteorological Forecast
- **Method**: `GET`
- **Path**: `/api/weather`
- **Query Parameters**:
  - `destination` (string, required): Name of city/region (e.g. `Goa`)
- **Response** (`200 OK`):
  ```json
  {
    "success": true,
    "destination": "Goa",
    "place": "Panaji, Goa, India",
    "temperature": 28,
    "feels_like": 33,
    "condition": "Partly Cloudy",
    "icon": "⛅",
    "humidity": 78,
    "wind_speed": 12,
    "forecast": [
      { "day": "Sat", "date": "19 Sep", "temp_max": 30, "temp_min": 25, "condition": "Passing Showers", "rain_chance": 65 }
    ],
    "source": "Open-Meteo Global Meteorological Model (WMO Station Data)",
    "is_ai_generated": false
  }
  ```
- **Errors**: `400 Bad Request` (missing destination), `404 Not Found` (unknown coordinates).

### 2.3 Destination Activities Catalog
- **Method**: `GET`
- **Path**: `/api/activities/{destination}`
- **Purpose**: Retrieve verified activity options and per-person rates for a destination.
- **Response** (`200 OK`):
  ```json
  {
    "destination": "Goa",
    "activities": [
      { "id": "water_sports", "name": "Baga Beach 5-in-1 Water Sports Combo", "cost": 1500, "category": "adventure" },
      { "id": "sunset_cruise", "name": "Mandovi River Sunset Cruise", "cost": 500, "category": "leisure" }
    ]
  }
  ```

### 2.4 Deterministic Budget Calculation
- **Method**: `POST`
- **Path**: `/api/calculate-budget`
- **Purpose**: Compute transparent 5-category budget breakdown and optimization suggestions.
- **Request Body**:
  ```json
  {
    "destination": "Goa",
    "days": 4,
    "travelers": 2,
    "budget": 45000,
    "hotel_preference": "standard",
    "transport_preference": "rental",
    "selected_activities": ["water_sports"],
    "travel_style": "balanced"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "user_budget": 45000.0,
    "total_estimated": 27606.0,
    "remaining_budget": 17394.0,
    "utilization_percent": 61.3,
    "status": "within_budget",
    "status_label": "Comfortably Within Budget",
    "is_over_budget": false,
    "deficit": 0.0,
    "categories": {
      "accommodation": { "amount": 9600.0, "percent": 34.8, "tier": "standard" },
      "food": { "amount": 8800.0, "percent": 31.9, "tier": "balanced" },
      "activities": { "amount": 3000.0, "percent": 10.9, "itemized": [...] },
      "transportation": { "amount": 4400.0, "percent": 15.9, "tier": "rental" },
      "miscellaneous": { "amount": 1806.0, "percent": 6.5 }
    },
    "cost_saving_alternatives": [],
    "per_person_estimated": 13803.0,
    "per_day_estimated": 6901.5
  }
  ```
- **Errors**: `400 Bad Request` (budget < ₹1,000).

### 2.5 Generate RAG-Grounded Itinerary
- **Method**: `POST`
- **Path**: `/api/plan-trip`
- **Purpose**: Formulate day-by-day travel plan using semantic RAG chunks and Anthropic Claude.
- **Request Body**:
  ```json
  {
    "destination": "Goa",
    "days": 4,
    "travelers": 2,
    "budget": 50000,
    "interests": ["beach", "adventure", "food"],
    "travel_style": "balanced",
    "hotel_preference": "standard",
    "transport_preference": "rental",
    "selected_activities": ["water_sports"],
    "start_date": "2026-10-15",
    "end_date": "2026-10-18"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "destination": "Goa",
    "summary": "Tailored 4-day coastal exploration...",
    "days": [
      {
        "day": 1,
        "title": "North Goa Beach Arrival & Sunset",
        "description": "...",
        "places": ["Calangute Beach", "Baga Beach"],
        "activities": ["Water Sports Combo", "Beachside Dinner"],
        "food_recommendations": ["Britto's Shack", "Fisherman's Wharf"],
        "estimated_cost": 5500.0
      }
    ],
    "budget_breakdown": { ... },
    "travel_tips": ["Rent a two-wheeler for convenient transit", "..."],
    "packing_tips": ["Light cottons", "Sunscreen SPF 50+", "..."],
    "sources": [
      {
        "id": "goa_attraction_baga",
        "destination": "Goa",
        "category": "attractions",
        "text": "Baga Beach is known for water sports...",
        "score": 0.842
      }
    ]
  }
  ```
- **Errors**: `400 Bad Request` (missing destination or budget < ₹2,000), `502 Bad Gateway` (LLM API communication failure).

### 2.6 RAG-Grounded Conversational Chat
- **Method**: `POST`
- **Path**: `/api/chat`
- **Purpose**: Answer travel queries grounded in the vector knowledge base and current itinerary.
- **Request Body**:
  ```json
  {
    "message": "What is the best time to visit Fort Aguada?",
    "trip": { "destination": "Goa" },
    "history": [
      { "role": "user", "content": "I am traveling to Goa." },
      { "role": "assistant", "content": "Welcome! How can I help you?" }
    ]
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "reply": "Fort Aguada is open daily from 9:30 AM to 5:30 PM. The ideal time to visit is late afternoon around 4:00 PM for panoramic Arabian Sea views and sunset.",
    "sources": [ ... ]
  }
  ```

---

## 3. Hotel Intelligence Endpoints

### 3.1 Get Verified Hotels Catalog
- **Method**: `GET`
- **Path**: `/api/hotels`
- **Query Parameters**: `destination` (optional)
- **Response** (`200 OK`):
  ```json
  {
    "destination": "Goa",
    "total": 12,
    "hotels": [
      {
        "id": "taj_fort_aguada",
        "name": "Taj Fort Aguada Resort & Spa",
        "destination": "Goa",
        "area": "Sinquerim",
        "tier": "luxury",
        "price_per_night": 18500,
        "rating": 4.8,
        "reviews": 3200,
        "amenities": ["Infinity Pool", "Private Beach Access", "Spa", "Fine Dining"],
        "is_verified_database_record": true
      }
    ]
  }
  ```

### 3.2 Hotel Recommendations with Proximity Scoring
- **Method**: `POST`
- **Path**: `/api/hotels/recommend`
- **Purpose**: Match verified properties against budget allocation and physical proximity to planned itinerary sights.
- **Request Body**:
  ```json
  {
    "destination": "Goa",
    "budget": 50000,
    "travelers": 2,
    "duration": 4,
    "preferred_area": "Candolim",
    "tier": "standard",
    "sort_by": "recommended",
    "itinerary_places": [
      { "name": "Aguada Fort", "lat": 15.4929, "lng": 73.7736 }
    ]
  }
  ```
- **Response** (`200 OK`): Returns prioritized list of matching properties with `distance_to_itinerary_km` and `is_within_accommodation_budget` tags.

---

## 4. User Authentication & Saved Trips

### 4.1 User Registration
- **Method**: `POST`
- **Path**: `/api/auth/register`
- **Request**:
  ```json
  { "email": "traveler@example.com", "password": "securepassword", "full_name": "Sara Patel" }
  ```
- **Response** (`200 OK`): Returns JWT Bearer token and user object.
- **Errors**: `400 Bad Request` (duplicate email or password < 6 characters).

### 4.2 User Login
- **Method**: `POST`
- **Path**: `/api/auth/login`
- **Request**:
  ```json
  { "email": "traveler@example.com", "password": "securepassword" }
  ```
- **Response** (`200 OK`): Returns JWT Bearer token and user profile.
- **Errors**: `401 Unauthorized` (invalid credentials).

### 4.3 Current User Profile
- **Method**: `GET`
- **Path**: `/api/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (`200 OK`): User object with `saved_trips_count`.

### 4.4 Save Trip
- **Method**: `POST`
- **Path**: `/api/trips`
- **Headers**: `Authorization: Bearer <token>`
- **Request**: Trip detail payload including day itineraries and budget breakdown.
- **Response** (`200 OK`): Saved trip record with unique database ID.

### 4.5 List Saved Trips
- **Method**: `GET`
- **Path**: `/api/trips`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (`200 OK`): Array of user's saved trips ordered newest first.

### 4.6 Get Saved Trip Detail
- **Method**: `GET`
- **Path**: `/api/trips/{trip_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (`200 OK`): Full trip plan with day-by-day itineraries.

### 4.7 Delete Saved Trip
- **Method**: `DELETE`
- **Path**: `/api/trips/{trip_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (`200 OK`): `{"status": "deleted", "id": 12}`

---

## 5. Export Endpoint

### 5.1 Backend PDF Streaming (Optional Server-Side Export)
- **Method**: `POST`
- **Path**: `/api/export/pdf`
- **Request**: JSON containing `trip_data`, `form_data`, and `hotels`.
- **Response** (`200 OK`): Streams binary `application/pdf` with `Content-Disposition: attachment; filename=TripGenie_<Destination>_Itinerary.pdf`.
