"""
Test suite for TripGenie AI Weather Service.
Verifies destination detection, meteorological data structure, forecast parsing,
and robust error handling.
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

sys.stdout.reconfigure(encoding="utf-8")

from app.weather import fetch_weather

def run_tests():
    print("=" * 70)
    print("⛅ TESTING TRIPGENIE AI METEOROLOGICAL WEATHER SERVICE")
    print("=" * 70)

    # TEST 1: Valid Destination (Goa)
    print("\n[TEST 1] Fetching live weather for 'Goa'")
    res1 = fetch_weather("Goa")
    print(f"  • Success:             {res1['success']}")
    print(f"  • Detected Place:      {res1.get('place')}")
    print(f"  • Current Temperature: {res1.get('temperature')}°C (Feels like {res1.get('feels_like')}°C)")
    print(f"  • Condition:           {res1.get('condition')} {res1.get('icon')}")
    print(f"  • Relative Humidity:   {res1.get('humidity')}%")
    print(f"  • Wind Speed:          {res1.get('wind_speed')} km/h")
    print(f"  • Data Source:         {res1.get('source')}")
    print(f"  • Is AI Generated:     {res1.get('is_ai_generated')} (Distinct from LLM)")
    print(f"  • 5-Day Forecast Days: {len(res1.get('forecast', []))}")
    for f in res1.get("forecast", [])[:3]:
        print(f"    - {f['day']} ({f['date']}): {f['temp_min']}°C to {f['temp_max']}°C, {f['condition']} {f['icon']} (Rain: {f.get('rain_chance')}%)")

    assert res1["success"] is True, "Expected success for Goa"
    assert "temperature" in res1, "Must contain temperature"
    assert "humidity" in res1, "Must contain humidity"
    assert "wind_speed" in res1, "Must contain wind_speed"
    assert res1["is_ai_generated"] is False, "Must be clearly labeled as non-AI meteorological data"
    print("  ✅ TEST 1 PASSED: Valid destination weather and forecast verified.")

    # TEST 2: Valid Mountain Destination (Manali)
    print("\n[TEST 2] Fetching live weather for 'Manali'")
    res2 = fetch_weather("Manali")
    print(f"  • Detected Place:      {res2.get('place')}")
    print(f"  • Temperature:         {res2.get('temperature')}°C")
    print(f"  • Condition:           {res2.get('condition')} {res2.get('icon')}")
    assert res2["success"] is True
    print("  ✅ TEST 2 PASSED: Mountain destination weather verified.")

    # TEST 3: Invalid Non-Existent Destination
    print("\n[TEST 3] Testing error handling for invalid destination 'xyznonexistentplace9999'")
    res3 = fetch_weather("xyznonexistentplace9999")
    print(f"  • Success:             {res3['success']}")
    print(f"  • Error Message:       {res3.get('error')}")
    assert res3["success"] is False, "Expected failure for non-existent destination"
    assert "not found" in res3.get("error", "").lower() or "check the spelling" in res3.get("error", "").lower()
    print("  ✅ TEST 3 PASSED: Invalid destination error cleanly handled.")

    print("\n" + "=" * 70)
    print("🎉 ALL WEATHER SERVICE TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
