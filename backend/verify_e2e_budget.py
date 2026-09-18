"""
End-to-end integration test verifying the Budget Planning Module via live HTTP endpoints.
"""
import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

def test_api():
    print("=" * 70)
    print("🚀 TESTING LIVE FASTAPI /api/plan-trip BUDGET MODULE INTEGRATION")
    print("=" * 70)

    payload = {
        "destination": "Kerala",
        "days": 4,
        "travelers": 2,
        "budget": 30000,
        "interests": ["nature", "relaxation"],
        "travel_style": "balanced",
        "hotel_preference": "luxury",
        "transport_preference": "private_cab",
        "selected_activities": ["houseboat_cruise"]
    }

    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/plan-trip",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))

    bb = data.get("budget_breakdown", {})
    print(f"\nTrip Destination:      {data.get('destination')}")
    print(f"Summary:               {data.get('summary')}")
    print(f"User Budget:           ₹{bb.get('user_budget', 0):,.2f}")
    print(f"Total Estimated:       ₹{bb.get('total_estimated', 0):,.2f}")
    print(f"Remaining:             ₹{bb.get('remaining_budget', 0):,.2f}")
    print(f"Utilization:           {bb.get('utilization_percent', 0)}% ({bb.get('status_label')})")
    print(f"Is Over Budget:        {bb.get('is_over_budget')}")
    print(f"Deficit:               ₹{bb.get('deficit', 0):,.2f}")

    print("\n5-Category Deterministic Breakdown:")
    for cat_name, cat_data in bb.get("categories", {}).items():
        print(f"  • {cat_name.capitalize():15}: ₹{cat_data['amount']:,.2f} ({cat_data.get('percent')}%) — {cat_data.get('calculation_note')}")

    print(f"\nCost-Saving Alternatives ({len(bb.get('cost_saving_alternatives', []))} items):")
    for idx, alt in enumerate(bb.get("cost_saving_alternatives", []), 1):
        print(f"  {idx}. {alt['title']} — Potential Savings: ₹{alt['potential_savings']:,.0f}")
        print(f"     {alt['description']}")

    # Assertions
    assert bb.get("is_over_budget") is True, "Expected over budget condition for luxury hotel with ₹30k budget"
    assert bb.get("deficit") > 0, "Deficit must be > 0"
    assert len(bb.get("cost_saving_alternatives")) > 0, "Expected actionable alternatives"
    assert len(bb.get("categories")) == 5, "Expected all 5 categories"

    print("\n" + "=" * 70)
    print("✅ E2E LIVE BUDGET MODULE INTEGRATION VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_api()
