"""
Unit and Integration Test for TripGenie AI Budget Planning Module.
Tests deterministic calculations, deficit detection, and cost optimization.
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

sys.stdout.reconfigure(encoding="utf-8")

from app.budget_planner import calculate_trip_budget, optimize_budget_parameters

def run_tests():
    print("=" * 70)
    print("🧪 TESTING TRIPGENIE AI DETERMINISTIC BUDGET PLANNING ENGINE")
    print("=" * 70)

    # TEST 1: Within Budget Scenario
    print("\n[TEST 1] Balanced Trip to Goa (Within Budget)")
    report1 = calculate_trip_budget(
        destination="Goa",
        days=4,
        travelers=2,
        user_budget=50000,
        hotel_preference="standard",
        transport_preference="rental",
        selected_activities=["water_sports", "sunset_cruise"],
        travel_style="balanced",
    )
    print(f"  • User Budget:         ₹{report1['user_budget']:,.2f}")
    print(f"  • Total Estimated:     ₹{report1['total_estimated']:,.2f}")
    print(f"  • Remaining Cushion:   ₹{report1['remaining_budget']:,.2f}")
    print(f"  • Utilization:         {report1['utilization_percent']}% ({report1['status_label']})")
    print(f"  • Accommodation:       ₹{report1['categories']['accommodation']['amount']:,.2f} ({report1['categories']['accommodation']['calculation_note']})")
    print(f"  • Food:                ₹{report1['categories']['food']['amount']:,.2f} ({report1['categories']['food']['calculation_note']})")
    print(f"  • Activities:          ₹{report1['categories']['activities']['amount']:,.2f} ({report1['categories']['activities']['calculation_note']})")
    print(f"  • Transportation:      ₹{report1['categories']['transportation']['amount']:,.2f} ({report1['categories']['transportation']['calculation_note']})")
    print(f"  • Miscellaneous:       ₹{report1['categories']['miscellaneous']['amount']:,.2f} ({report1['categories']['miscellaneous']['calculation_note']})")
    assert report1["is_over_budget"] is False, "Expected within budget!"
    assert report1["total_estimated"] > 0, "Cost must be > 0"
    print("  ✅ TEST 1 PASSED: Deterministic within-budget calculation verified.")

    # TEST 2: Over-Budget Scenario with Deficit & Cost-Saving Alternatives
    print("\n[TEST 2] Luxury Trip with Tight Budget (Exceeds Budget)")
    report2 = calculate_trip_budget(
        destination="Kerala",
        days=5,
        travelers=4,
        user_budget=60000,
        hotel_preference="luxury",
        transport_preference="flight_premium",
        selected_activities=["houseboat_cruise", "kathakali_show"],
        travel_style="luxury",
    )
    print(f"  • User Budget:         ₹{report2['user_budget']:,.2f}")
    print(f"  • Total Estimated:     ₹{report2['total_estimated']:,.2f}")
    print(f"  • Deficit:             ₹{report2['deficit']:,.2f}")
    print(f"  • Utilization:         {report2['utilization_percent']}% ({report2['status_label']})")
    print(f"  • Is Over Budget:      {report2['is_over_budget']}")
    print(f"  • Alternatives Generated ({len(report2['cost_saving_alternatives'])} items):")
    for idx, alt in enumerate(report2["cost_saving_alternatives"], 1):
        print(f"    {idx}. {alt['title']} — Potential Savings: ₹{alt['potential_savings']:,.0f}")
        print(f"       {alt['description']}")

    assert report2["is_over_budget"] is True, "Expected over budget!"
    assert report2["deficit"] > 0, "Deficit must be positive"
    assert len(report2["cost_saving_alternatives"]) > 0, "Should generate cost-saving alternatives"
    print("  ✅ TEST 2 PASSED: Over-budget detection and alternatives verified.")

    # TEST 3: Budget Optimization Engine
    print("\n[TEST 3] Auto-Optimize Parameters to Fit Budget")
    optimized = optimize_budget_parameters(
        destination="Kerala",
        days=5,
        travelers=4,
        user_budget=60000,
        current_hotel="luxury",
        current_transport="flight_premium",
        current_style="luxury",
    )
    opt_report = optimized["optimized_report"]
    print(f"  • Recommended Hotel:       {optimized['hotel_preference'].title()}")
    print(f"  • Recommended Transport:   {optimized['transport_preference'].title()}")
    print(f"  • Recommended Style:       {optimized['travel_style'].title()}")
    print(f"  • Optimized Estimated Cost: ₹{opt_report['total_estimated']:,.2f} vs Budget ₹60,000")
    print(f"  • New Utilization:         {opt_report['utilization_percent']}% ({opt_report['status_label']})")
    assert opt_report["total_estimated"] <= 60000 or opt_report["utilization_percent"] <= 105.0
    print("  ✅ TEST 3 PASSED: Budget optimization successfully adjusted parameters.")

    print("\n" + "=" * 70)
    print("🎉 ALL DETERMINISTIC BUDGET PLANNING TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
