"""
Automated Test Suite for TripGenie AI PDF Itinerary Export Feature
Validates:
1. ReportLab buffer generation with complete trip plan data.
2. PDF binary header (%PDF-) and document structure.
3. Live FastAPI endpoint POST /api/export/pdf.
4. Input validation (missing destination error handling).
"""
import sys
import io
import requests
from app.pdf_exporter import build_pdf_buffer

# Ensure utf-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SAMPLE_TRIP = {
    "destination": "Goa",
    "summary": "A customized 5-day itinerary for 4 travelers visiting Goa with an allocated budget of Rs 100,000. Tailored for coastal relaxation and heritage exploration.",
    "days": [
        {
            "day": 1,
            "title": "Arrival & North Goa Coastal Exploration",
            "description": "Arrive at Dabolim Airport or Thivim railway station. Check into your beachfront accommodation in Candolim/Calangute and enjoy the Arabian sunset.",
            "places": ["Baga Beach", "Calangute Beach", "Candolim Beach"],
            "activities": ["Sunset stroll", "Beach shack dinner", "Waterfront photography"],
            "food_recommendations": ["Goan Fish Curry Rice", "Bebinca dessert"],
            "estimated_cost": 20000.0
        },
        {
            "day": 2,
            "title": "Historic Forts & Scenic Ramparts",
            "description": "Visit historic 17th-century Portuguese fortifications and panoramic viewpoints.",
            "places": ["Fort Aguada", "Sinquerim Beach", "Reis Magos Fort"],
            "activities": ["Lighthouse visit", "Coastal rampart walking", "Souvenir shopping"],
            "food_recommendations": ["Prawn Balchao", "Sol Kadi"],
            "estimated_cost": 18000.0
        },
        {
            "day": 3,
            "title": "Old Goa UNESCO Heritage & Panaji Latin Quarter",
            "description": "Marvel at baroque churches in Old Goa and walk through colorful Fontainhas.",
            "places": ["Basilica of Bom Jesus", "Se Cathedral", "Fontainhas Latin Quarter"],
            "activities": ["Heritage walk", "Art gallery visits", "Mandovi river evening cruise"],
            "food_recommendations": ["Portuguese Pork Vindaloo", "Feni tasting"],
            "estimated_cost": 22000.0
        }
    ],
    "budget_breakdown": {
        "user_budget": 100000.0,
        "total_estimated_cost": 78000.0,
        "remaining_budget": 22000.0,
        "budget_utilization_pct": 78.0,
        "accommodation": {"total_cost": 32000.0},
        "food": {"total_cost": 16000.0},
        "activities": {"total_cost": 15000.0},
        "transportation": {"total_cost": 10000.0},
        "miscellaneous": {"total_cost": 5000.0}
    },
    "travel_tips": [
        "Rent a scooter (Rs 400/day) for convenient coastal transport.",
        "Dress respectfully when visiting Old Goa churches and temples.",
        "Always agree on taxi fares upfront or use GoaMiles government app."
    ],
    "packing_tips": [
        "Breathable cotton and linen clothing.",
        "High SPF reef-safe sunscreen and polarized sunglasses.",
        "Waterproof phone pouch and comfortable walking sandals."
    ]
}

SAMPLE_HOTELS = [
    {
        "name": "Santana Beach Resort",
        "area": "Candolim",
        "tier": "boutique",
        "rating": 4.5,
        "price": 3800.0,
        "amenities": ["Direct Beach Access", "Swimming Pool", "Free Breakfast"]
    },
    {
        "name": "Taj Fort Aguada Resort & Spa",
        "area": "Sinquerim",
        "tier": "luxury",
        "rating": 4.8,
        "price": 18500.0,
        "amenities": ["Cliffside Sea Views", "Infinity Pool", "Ayurvedic Spa"]
    }
]

def run_tests():
    print("\n=======================================================")
    print("[TEST SUITE] TRIPGENIE AI PDF EXPORT ENGINE")
    print("=======================================================\n")

    # 1. Test Direct Buffer Generation
    print("--- 1. Testing ReportLab Direct PDF Buffer Generation ---")
    buf = build_pdf_buffer(SAMPLE_TRIP, {"travelers": 4, "days": 3, "budget": 100000}, SAMPLE_HOTELS)
    pdf_bytes = buf.getvalue()
    print(f"[OK] PDF successfully generated! Byte size: {len(pdf_bytes):,} bytes")
    assert len(pdf_bytes) > 5000, "Generated PDF is too small!"
    assert pdf_bytes.startswith(b"%PDF-"), "Generated file does not start with valid PDF magic bytes!"
    print("[OK] Valid PDF header (%PDF-) verified.")

    # 2. Test Live FastAPI Endpoint
    print("\n--- 2. Testing Live API Endpoint POST /api/export/pdf ---")
    api_url = "http://127.0.0.1:8000/api/export/pdf"
    payload = {
        "trip_data": SAMPLE_TRIP,
        "form_data": {"travelers": 4, "days": 3, "budget": 100000},
        "hotels": SAMPLE_HOTELS
    }
    
    res = requests.post(api_url, json=payload, timeout=10)
    print(f"API HTTP Status: {res.status_code}")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    assert "application/pdf" in res.headers.get("content-type", ""), "Content-Type must be application/pdf"
    assert res.content.startswith(b"%PDF-"), "Streamed response does not match PDF signature"
    print(f"[OK] Streamed PDF verified! Content-Type: {res.headers['content-type']}, Size: {len(res.content):,} bytes")
    print(f"[OK] Content-Disposition: {res.headers.get('content-disposition')}")

    # 3. Test Validation Error on Missing Destination
    print("\n--- 3. Testing Missing Destination Error Handling ---")
    invalid_res = requests.post(api_url, json={"trip_data": {}}, timeout=10)
    print(f"Invalid Request Status: {invalid_res.status_code}")
    assert invalid_res.status_code in (400, 422), f"Expected 400 or 422, got {invalid_res.status_code}"
    print(f"[OK] Correctly rejected empty payload: {invalid_res.json()}")

    print("\n=======================================================")
    print("[SUCCESS] ALL PDF EXPORT TESTS PASSED SUCCESSFULLY (100%)!")
    print("=======================================================\n")

if __name__ == "__main__":
    run_tests()
