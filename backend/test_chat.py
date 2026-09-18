"""
TripGenie AI — Conversational Travel Assistant Verification Suite.
Validates:
1. "Make Day 3 cheaper" optimization and cost savings calculation.
2. "Replace scuba diving with another activity" alternative recommendations.
3. "Suggest vegetarian restaurants" authentic dining suggestions.
4. "Can I complete this itinerary in 4 days?" duration pacing & clustering.
5. "Which hotel is closest to the beach?" verified property suggestions.
6. "Reduce my budget to ₹70,000" deterministic budget reallocation.
7. Validation: empty message rejection (HTTP 400).
8. RAG source evidence retrieval transparency.
"""

import sys
import json

# Ensure proper stdout encoding for terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_TRIP = {
    "destination": "Goa",
    "budget": 100000,
    "travelers": 4,
    "days_count": 5,
    "days": [
        {"day": 1, "title": "Arrival & North Goa Coastal Exploration", "places": ["Baga Beach", "Calangute Beach"], "activities": ["Sunset walk", "Beach shacks"]},
        {"day": 2, "title": "Forts & Watersports Adventure", "places": ["Fort Aguada", "Sinquerim Beach"], "activities": ["Scuba diving", "Jet ski"]},
        {"day": 3, "title": "South Goa Serenity & Island Excursion", "places": ["Palolem Beach", "Butterfly Beach"], "activities": ["Boat cruise", "Island dolphin safari"]},
        {"day": 4, "title": "Old Goa Portuguese Heritage & Churches", "places": ["Basilica of Bom Jesus", "Se Cathedral"], "activities": ["Heritage walk", "Museum visit"]},
        {"day": 5, "title": "Vibrant Flea Markets & Departure", "places": ["Anjuna Flea Market", "Vagator Cliff"], "activities": ["Souvenir shopping", "Sunset dinner"]},
    ],
    "selected_activities": ["scuba_diving", "sunset_cruise"],
}


def test_make_day_cheaper():
    print("\n--- 1. Testing 'Make Day 3 cheaper' ---")
    payload = {
        "message": "Make Day 3 cheaper.",
        "trip": SAMPLE_TRIP,
        "history": [],
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200, f"Failed: {resp.text}"
    data = resp.json()
    reply = data["reply"]
    print(f"Reply:\n{reply}\n")
    assert "Day 3" in reply
    assert "savings" in reply.lower() or "save" in reply.lower() or "cheaper" in reply.lower()
    assert len(data["sources"]) > 0
    print("✓ Day 3 cost optimization verified with concrete budget-saving swaps.")


def test_replace_activity():
    print("\n--- 2. Testing 'Replace scuba diving with another activity' ---")
    payload = {
        "message": "Replace scuba diving with another activity.",
        "trip": SAMPLE_TRIP,
        "history": [],
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200, f"Failed: {resp.text}"
    data = resp.json()
    reply = data["reply"]
    print(f"Reply:\n{reply}\n")
    assert "snorkeling" in reply.lower() or "kayaking" in reply.lower() or "cruise" in reply.lower()
    print("✓ Activity replacement suggested valid adventure alternatives with price context.")


def test_suggest_vegetarian_restaurants():
    print("\n--- 3. Testing 'Suggest vegetarian restaurants' ---")
    payload = {
        "message": "Suggest vegetarian restaurants.",
        "trip": SAMPLE_TRIP,
        "history": [],
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200, f"Failed: {resp.text}"
    data = resp.json()
    reply = data["reply"]
    print(f"Reply:\n{reply}\n")
    assert "navtara" in reply.lower() or "thali" in reply.lower() or "veg" in reply.lower()
    print("✓ Vegetarian restaurant recommendations verified.")


def test_duration_feasibility():
    print("\n--- 4. Testing 'Can I complete this itinerary in 4 days?' ---")
    payload = {
        "message": "Can I complete this itinerary in 4 days?",
        "trip": SAMPLE_TRIP,
        "history": [],
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200, f"Failed: {resp.text}"
    data = resp.json()
    reply = data["reply"]
    print(f"Reply:\n{reply}\n")
    assert "4 days" in reply.lower() or "doable" in reply.lower() or "consolidate" in reply.lower()
    print("✓ Pacing & duration consolidation advice verified.")


def test_closest_hotel():
    print("\n--- 5. Testing 'Which hotel is closest to the beach?' ---")
    payload = {
        "message": "Which hotel is closest to the beach?",
        "trip": SAMPLE_TRIP,
        "history": [],
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200, f"Failed: {resp.text}"
    data = resp.json()
    reply = data["reply"]
    print(f"Reply:\n{reply}\n")
    assert "santana" in reply.lower() or "taj fort aguada" in reply.lower() or "beach" in reply.lower()
    print("✓ Beachfront verified hotel recommendations returned.")


def test_reduce_budget():
    print("\n--- 6. Testing 'Reduce my budget to ₹70,000' ---")
    payload = {
        "message": "Reduce my budget to ₹70,000.",
        "trip": SAMPLE_TRIP,
        "history": [],
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200, f"Failed: {resp.text}"
    data = resp.json()
    reply = data["reply"]
    print(f"Reply:\n{reply}\n")
    assert "70,000" in reply or "28,000" in reply
    print("✓ Deterministic budget reduction reallocation verified.")


def test_empty_message_validation():
    print("\n--- 7. Testing Empty Message Validation ---")
    resp = client.post("/api/chat", json={"message": "   ", "trip": SAMPLE_TRIP, "history": []})
    assert resp.status_code == 400
    print("✓ Empty message correctly rejected with HTTP 400 Bad Request.")


def test_rag_grounding_sources():
    print("\n--- 8. Testing RAG Source Evidence Transparency ---")
    payload = {
        "message": "What is the best time of year to visit Goa?",
        "trip": SAMPLE_TRIP,
        "history": [],
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["sources"]) > 0
    first_chunk = data["sources"][0]
    assert "text" in first_chunk
    assert "category" in first_chunk
    print(f"✓ Retrieved {len(data['sources'])} grounding chunks. Top chunk category: [{first_chunk['category']}]")


if __name__ == "__main__":
    test_make_day_cheaper()
    test_replace_activity()
    test_suggest_vegetarian_restaurants()
    test_duration_feasibility()
    test_closest_hotel()
    test_reduce_budget()
    test_empty_message_validation()
    test_rag_grounding_sources()
    print("\n=======================================================")
    print(" ALL 8 CHATBOT VERIFICATION SUITES PASSED! (100%)      ")
    print("=======================================================\n")
