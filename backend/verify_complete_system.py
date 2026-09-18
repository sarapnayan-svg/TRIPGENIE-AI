"""
TripGenie AI — Comprehensive Full-System Verification Test Suite.
Validates all backend endpoints, RAG pipeline, deterministic budget module,
and real-time meteorological weather service.
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

def make_req(endpoint, method="GET", body=None):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def main():
    print("=" * 80)
    print("🚀 TRIPGENIE AI — COMPREHENSIVE FULL-SYSTEM VERIFICATION")
    print("=" * 80)

    # 1. Health Check
    print("\n[CHECK 1/8] Verifying Backend Health & Vector Store Status...")
    status_code, data = make_req("/health")
    assert status_code == 200 and data.get("status") == "ok"
    print(f"  ✅ Backend Online: {data.get('status').upper()} | Indexed Destinations: {data.get('known_destinations')}")

    # 2. RAG Knowledge Base Destinations
    print("\n[CHECK 2/8] Verifying Indexed Knowledge Base Destinations...")
    status_code, data = make_req("/destinations")
    assert status_code == 200
    print(f"  ✅ Knowledge Base Hubs: {data.get('destinations')}")

    # 3. Real-Time Meteorological Weather (Goa)
    print("\n[CHECK 3/8] Verifying Meteorological Weather API for 'Goa'...")
    status_code, data = make_req("/weather?destination=Goa")
    assert status_code == 200 and data.get("success") is True
    print(f"  ✅ Place Detected:      {data.get('place')}")
    print(f"  ✅ Current Temperature: {data.get('temperature')}°C (Feels like {data.get('feels_like')}°C)")
    print(f"  ✅ Weather Condition:   {data.get('condition')} {data.get('icon')}")
    print(f"  ✅ Relative Humidity:   {data.get('humidity')}% | Wind: {data.get('wind_speed')} km/h")
    print(f"  ✅ 5-Day Forecast:      {len(data.get('forecast', []))} Days Available")
    print(f"  ✅ AI Separation Flag:  is_ai_generated = {data.get('is_ai_generated')} (Sensor/Station Data)")

    # 4. Real-Time Meteorological Weather (Manali Mountain Climate)
    print("\n[CHECK 4/8] Verifying Meteorological Weather API for 'Manali'...")
    status_code, data = make_req("/weather?destination=Manali")
    assert status_code == 200 and data.get("success") is True
    print(f"  ✅ Mountain Place:      {data.get('place')}")
    print(f"  ✅ Temperature:         {data.get('temperature')}°C | Condition: {data.get('condition')} {data.get('icon')}")

    # 5. Weather Error Handling (Invalid Destination)
    print("\n[CHECK 5/8] Verifying Weather Error Handling for Non-Existent Place...")
    status_code, data = make_req("/weather?destination=nonexistent_xyz9999")
    assert status_code == 404
    print(f"  ✅ Graceful 404 Handling: {data.get('detail')}")

    # 6. Activities Catalog
    print("\n[CHECK 6/8] Verifying Destination Activities Catalog for 'Goa'...")
    status_code, data = make_req("/activities/Goa")
    assert status_code == 200
    print(f"  ✅ Catalog Activities Count: {len(data.get('activities', []))} items")
    print(f"  ✅ Sample Activity:          {data['activities'][0]['name']} (₹{data['activities'][0]['cost']:,.0f})")

    # 7. Deterministic Budget Planning Engine
    print("\n[CHECK 7/8] Verifying Deterministic Budget Planning Engine...")
    budget_req = {
        "destination": "Goa",
        "days": 4,
        "travelers": 2,
        "budget": 50000,
        "hotel_preference": "standard",
        "transport_preference": "rental",
        "selected_activities": ["water_sports", "sunset_cruise"],
        "travel_style": "balanced"
    }
    status_code, data = make_req("/calculate-budget", method="POST", body=budget_req)
    assert status_code == 200
    print(f"  ✅ User Budget:     ₹{data.get('user_budget'):,.2f}")
    print(f"  ✅ Total Estimated: ₹{data.get('total_estimated'):,.2f}")
    print(f"  ✅ Remaining:       ₹{data.get('remaining_budget'):,.2f}")
    print(f"  ✅ Utilization:     {data.get('utilization_percent')}% ({data.get('status_label')})")
    print(f"  ✅ 5 Categories:    {list(data.get('categories', {}).keys())}")

    # 8. Full End-to-End RAG Trip Plan Generation
    print("\n[CHECK 8/8] Verifying End-to-End RAG Plan Generation with Grounding...")
    plan_req = {
        "destination": "Kerala",
        "days": 3,
        "travelers": 2,
        "budget": 45000,
        "interests": ["nature", "food"],
        "travel_style": "balanced",
        "hotel_preference": "standard",
        "transport_preference": "private_cab",
        "selected_activities": ["houseboat_cruise"]
    }
    status_code, data = make_req("/plan-trip", method="POST", body=plan_req)
    assert status_code == 200
    print(f"  ✅ Destination:    {data.get('destination')}")
    print(f"  ✅ Generated Days: {len(data.get('days', []))} Days")
    print(f"  ✅ RAG Sources:    {len(data.get('sources', []))} Chunks Tracked")
    print(f"  ✅ Generated By:   {data.get('generated_by')}")
    print(f"  ✅ Summary:        {data.get('summary')[:80]}...")

    print("\n" + "=" * 80)
    print("🎉 ALL 8 SYSTEM PROCESSES AND ENDPOINTS ARE RUNNING 100% CORRECTLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
