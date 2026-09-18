"""
TripGenie AI — Hotel Recommendation Module Verification Suite.
Validates:
1. Catalog integrity (no missing fields, non-negative tariffs, valid GPS bounds, ratings).
2. Haversine spatial proximity calculation to itinerary attractions.
3. Target nightly room budget calculation.
4. Sorting mechanisms (recommended, proximity, price_asc, rating).
5. Area and Tier filtering.
6. FastAPI endpoints (/api/hotels and /api/hotels/recommend).
"""

import sys
import math

# Ensure proper stdout encoding for terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.hotels_database import VERIFIED_HOTELS, recommend_hotels, haversine_km
from fastapi.testclient import TestClient
from app.main import app


def test_catalog_integrity():
    print("\n--- 1. Testing Hotel Catalog Integrity ---")
    assert len(VERIFIED_HOTELS) >= 20, f"Expected >= 20 verified hotels, found {len(VERIFIED_HOTELS)}"
    
    destinations = set()
    for h in VERIFIED_HOTELS:
        assert h["id"], "Hotel missing 'id'"
        assert h["name"], "Hotel missing 'name'"
        assert h["destination"], "Hotel missing 'destination'"
        assert h["price_per_night"] > 0, f"Invalid tariff for {h['name']}"
        assert 1.0 <= h["rating"] <= 5.0, f"Invalid rating for {h['name']}"
        assert h["reviews_count"] >= 100, f"Review count suspiciously low for {h['name']}"
        assert len(h["amenities"]) >= 3, f"Insufficient amenities for {h['name']}"
        assert "lat" in h["coordinates"] and "lng" in h["coordinates"], f"Missing coords for {h['name']}"
        assert 8.0 <= h["coordinates"]["lat"] <= 35.0, f"Out of India lat bounds for {h['name']}"
        assert 68.0 <= h["coordinates"]["lng"] <= 90.0, f"Out of India lng bounds for {h['name']}"
        destinations.add(h["destination"])

    print(f"✓ Total Verified Hotels: {len(VERIFIED_HOTELS)}")
    print(f"✓ Destinations Covered: {sorted(list(destinations))}")


def test_haversine_accuracy():
    print("\n--- 2. Testing Haversine Distance Accuracy ---")
    # Calangute Beach (15.5439, 73.7553) to Baga Beach (15.5553, 73.7517)
    # Expected real-world distance ~ 1.3 - 1.4 km
    d = haversine_km(15.5439, 73.7553, 15.5553, 73.7517)
    print(f"Calangute to Baga: {d} km")
    assert 1.1 <= d <= 1.6, f"Haversine calculation unexpected: {d} km"
    print("✓ Haversine calculation verified against GPS ground truth.")


def test_recommendation_engine():
    print("\n--- 3. Testing Recommendation Engine with Itinerary Proximity ---")
    itinerary_places = [
        {"name": "Baga Beach", "lat": 15.5553, "lng": 73.7517},
        {"name": "Fort Aguada", "lat": 15.4920, "lng": 73.7737},
    ]

    res = recommend_hotels(
        destination="Goa",
        budget=40000.0,
        travelers=4,
        duration=4,
        preferred_area=None,
        tier=None,
        itinerary_places=itinerary_places,
        sort_by="recommended",
    )

    assert res["total_found"] > 0, "No hotels found for Goa"
    assert res["recommended_rooms"] == 2, f"Expected 2 rooms for 4 travelers, got {res['recommended_rooms']}"
    assert res["recommended_nights"] == 3, f"Expected 3 nights for 4-day trip, got {res['recommended_nights']}"

    # Target nightly room budget = (40000 * 0.40) / (3 * 2) = 16000 / 6 = 2666.67
    expected_target = round((40000.0 * 0.40) / (3 * 2), 2)
    assert abs(res["target_nightly_room_budget"] - expected_target) < 1.0

    print(f"✓ Recommended Rooms: {res['recommended_rooms']} | Nights: {res['recommended_nights']}")
    print(f"✓ Target Nightly Room Budget: ₹{res['target_nightly_room_budget']:,.2f}")

    # Verify proximity calculation on top hotel
    top_hotel = res["hotels"][0]
    print(f"✓ Top Hotel: {top_hotel['name']}")
    print(f"  Area: {top_hotel['area']} | Tier: {top_hotel['tier'].upper()}")
    print(f"  Tariff: ₹{top_hotel['price_per_night']:,}/night | Total Stay: ₹{top_hotel['total_stay_estimated']:,}")
    print(f"  Proximity: {top_hotel.get('proximity_note')}")
    assert "distance_to_itinerary_km" in top_hotel
    assert top_hotel["distance_to_itinerary_km"] > 0


def test_sorting_and_filtering():
    print("\n--- 4. Testing Sorting and Tier/Area Filtering ---")
    itinerary_places = [{"name": "Fort Aguada", "lat": 15.4920, "lng": 73.7737}]

    # Sort by Proximity
    res_prox = recommend_hotels(
        destination="Goa",
        budget=50000.0,
        itinerary_places=itinerary_places,
        sort_by="proximity",
    )
    dists = [h["distance_to_itinerary_km"] for h in res_prox["hotels"]]
    assert dists == sorted(dists), "Hotels not sorted in ascending proximity"
    closest = res_prox["hotels"][0]
    print(f"✓ Closest to Fort Aguada: {closest['name']} ({closest['distance_to_itinerary_km']} km)")

    # Sort by Price Ascending
    res_price = recommend_hotels(destination="Goa", budget=50000.0, sort_by="price_asc")
    prices = [h["price_per_night"] for h in res_price["hotels"]]
    assert prices == sorted(prices), "Hotels not sorted in ascending price"
    print(f"✓ Cheapest property: {res_price['hotels'][0]['name']} (₹{res_price['hotels'][0]['price_per_night']}/night)")

    # Filter by Tier: Hostel
    res_hostel = recommend_hotels(destination="Goa", budget=20000.0, tier="hostel")
    for h in res_hostel["hotels"]:
        assert h["tier"] == "hostel", f"Expected hostel tier, found {h['tier']}"
    print(f"✓ Tier filter 'hostel' correctly returned {len(res_hostel['hotels'])} hostels.")

    # Filter by Area: Candolim
    res_area = recommend_hotels(destination="Goa", budget=30000.0, preferred_area="Candolim")
    for h in res_area["hotels"]:
        assert "candolim" in h["area"].lower() or "sinquerim" in h["area"].lower()
    print(f"✓ Area filter 'Candolim' correctly returned {len(res_area['hotels'])} properties.")


def test_api_endpoints():
    print("\n--- 5. Testing FastAPI Endpoints ---")
    client = TestClient(app)

    # 1. GET /api/hotels
    resp = client.get("/api/hotels?destination=Kerala")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    print(f"✓ GET /api/hotels?destination=Kerala returned {data['total']} hotels.")

    # 2. POST /api/hotels/recommend
    payload = {
        "destination": "Goa",
        "budget": 35000,
        "travelers": 2,
        "duration": 3,
        "preferred_area": "Anjuna",
        "tier": "standard",
        "sort_by": "recommended",
        "itinerary_places": [{"name": "Anjuna Beach", "lat": 15.5828, "lng": 73.7431}],
    }
    resp = client.post("/api/hotels/recommend", json=payload)
    assert resp.status_code == 200, f"Failed: {resp.text}"
    rec_data = resp.json()
    assert rec_data["total_found"] > 0
    assert rec_data["verified_source"] == "TripGenie Verified Hotel Catalog"
    print(f"✓ POST /api/hotels/recommend returned {rec_data['total_found']} verified recommendations.")


if __name__ == "__main__":
    test_catalog_integrity()
    test_haversine_accuracy()
    test_recommendation_engine()
    test_sorting_and_filtering()
    test_api_endpoints()
    print("\n=======================================================")
    print(" ALL 5 HOTEL MODULE VERIFICATION SUITES PASSED! (100%) ")
    print("=======================================================\n")
