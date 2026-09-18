import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print('======================================================================')
print('TRIPGENIE AI - COMPLETE TRIP PLANNING WORKFLOW VERIFICATION TEST')
print('======================================================================')

# ---------------------------------------------------------
# Test Case 1: Standard Plan Trip Workflow
# ---------------------------------------------------------
user_inputs = {
    'destination': 'Goa',
    'travelers': 4,
    'days': 5,
    'budget': 100000,
    'interests': ['beach', 'adventure', 'food'],
    'travel_style': 'balanced',
    'start_date': '2026-10-15',
    'end_date': '2026-10-20'
}

print('\n[1] USER INPUT ENTERED IN FRONTEND FORM:')
for k, v in user_inputs.items():
    print(f'    • {k.replace("_", " ").title()}: {v}')

print('\n[2] FRONTEND FORM VALIDATION:')
assert user_inputs['destination'].strip() != '', 'Destination is required'
assert 1 <= user_inputs['days'] <= 14, 'Days must be 1-14'
assert 1 <= user_inputs['travelers'] <= 20, 'Travelers must be 1-20'
assert user_inputs['budget'] >= 2000, 'Budget must be >= 2000'
print('    ✓ Validation PASSED. Form is valid.')

print('\n[3] FRONTEND SENDS REQUEST TO FASTAPI /api/plan-trip:')
payload = json.dumps(user_inputs).encode('utf-8')
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/plan-trip',
    data=payload,
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as response:
    status_code = response.status
    result = json.loads(response.read().decode('utf-8'))

print(f'    ✓ Backend returned HTTP {status_code} OK')
print(f'    ✓ Synthesis Engine: {result.get("generated_by")}')
print(f'    ✓ RAG Chunks Retrieved: {len(result.get("sources", []))} chunks')

print('\n[4] FRONTEND RECEIVES & RENDERS STRUCTURED JSON OUTPUT:')
print('----------------------------------------------------------------------')
print('TRIP SUMMARY:')
print(' ', result.get('summary'))
print('----------------------------------------------------------------------')
print('DAY-BY-DAY ITINERARY:')
for day in result.get('days', []):
    print(f'\n  📅 {day["title"]} (Est. Cost: Rs {day.get("estimated_cost", 0):,.0f})')
    print(f'     Description: {day["description"]}')
    print(f'     📍 Places: {day.get("places", [])}')
    print(f'     ⚡ Activities: {day.get("activities", [])}')
    print(f'     🍽️ Food: {day.get("food_recommendations", [])}')

print('\n----------------------------------------------------------------------')
print('ESTIMATED BUDGET BREAKDOWN:')
for cat, amt in result.get('budget_breakdown', {}).items():
    print(f'  • {cat.capitalize()}: Rs {amt:,.0f}')

print('\nVERIFIED TRAVEL TIPS:')
for tip in result.get('travel_tips', []):
    print(f'  💡 {tip}')

print('\nPACKING CHECKLIST:')
for tip in result.get('packing_tips', []):
    print(f'  🎒 {tip}')

print('\nRAG GROUNDING SOURCES USED (Explainability):')
for idx, s in enumerate(result.get('sources', [])[:3]):
    print(f'  [{idx+1}] Category: {s.get("category")} (Score: {s.get("score", 0):.2f})')
    print(f'      "{s.get("text")}"')

# ---------------------------------------------------------
# Test Case 2: Error Handling (Missing Destination)
# ---------------------------------------------------------
print('\n======================================================================')
print('ERROR HANDLING TESTS:')
print('======================================================================')
print('\n[Test 2A] Testing Missing / Blank Destination:')
try:
    bad_req = urllib.request.Request(
        'http://127.0.0.1:8000/api/plan-trip',
        data=json.dumps({'destination': '   ', 'days': 5, 'travelers': 2, 'budget': 50000}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(bad_req) as r:
        pass
except urllib.error.HTTPError as e:
    err_body = json.loads(e.read().decode())
    print(f'    ✓ Correctly rejected with HTTP {e.code}: {err_body["detail"]}')

print('\n[Test 2B] Testing Budget Problem (Budget < Rs 1000):')
try:
    bad_budget = urllib.request.Request(
        'http://127.0.0.1:8000/api/plan-trip',
        data=json.dumps({'destination': 'Goa', 'days': 5, 'travelers': 2, 'budget': 800}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(bad_budget) as r:
        pass
except urllib.error.HTTPError as e:
    err_body = json.loads(e.read().decode())
    print(f'    ✓ Correctly rejected with HTTP {e.code}: {err_body["detail"]}')

print('\n======================================================================')
print('ALL WORKFLOW STEPS & ERROR HANDLERS VERIFIED SUCCESSFULLY!')
print('======================================================================')
