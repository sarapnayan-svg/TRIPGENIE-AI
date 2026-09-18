"""
TripGenie AI — User Authentication & Saved Trips Verification Suite.
Validates:
1. User Registration (200 OK + JWT issuance).
2. Duplicate email rejection (HTTP 400).
3. Short password rejection (HTTP 400).
4. Password hashing security (bcrypt hash verification, zero plaintext).
5. User Login with valid / invalid credentials.
6. Profile retrieval (/api/auth/me).
7. Save generated trip (/api/trips).
8. List saved trips (/api/trips).
9. Authorization security: User B cannot access User A's trip (HTTP 403).
10. Delete saved trip (/api/trips/{id}).
11. Anonymous travel planning preservation (no token required).
"""

import sys
import uuid

# Ensure proper stdout encoding for terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal
from app.db_models import User
import bcrypt

client = TestClient(app)

# Initialize database tables
init_db()

unique_id = uuid.uuid4().hex[:6]
USER_A_EMAIL = f"traveler_a_{unique_id}@example.com"
USER_B_EMAIL = f"traveler_b_{unique_id}@example.com"
PASSWORD_A = "SecureTrip123!"
PASSWORD_B = "AnotherSecure456!"


def test_registration_and_security():
    print("\n--- 1. Testing Registration & Password Hashing Security ---")
    
    # Register User A
    resp = client.post(
        "/api/auth/register",
        json={"email": USER_A_EMAIL, "password": PASSWORD_A, "full_name": "Alice Explorer"},
    )
    assert resp.status_code == 200, f"Registration failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == USER_A_EMAIL
    assert data["user"]["full_name"] == "Alice Explorer"
    token_a = data["access_token"]
    user_a_id = data["user"]["id"]
    print("✓ User A registered successfully with JWT token.")

    # Security check: verify database record has bcrypt hash, NOT plaintext
    db = SessionLocal()
    user_record = db.query(User).filter(User.id == user_a_id).first()
    assert user_record is not None
    assert user_record.hashed_password != PASSWORD_A, "SECURITY FAULT: Plaintext password stored!"
    assert user_record.hashed_password.startswith("$2b$") or user_record.hashed_password.startswith("$2a$"), "Not a bcrypt hash"
    assert bcrypt.checkpw(PASSWORD_A.encode("utf-8"), user_record.hashed_password.encode("utf-8")), "Hash mismatch"
    db.close()
    print("✓ Security verified: Password is securely hashed with bcrypt salt.")

    # Duplicate registration check
    dup_resp = client.post(
        "/api/auth/register",
        json={"email": USER_A_EMAIL, "password": "differentPassword123", "full_name": "Imposter"},
    )
    assert dup_resp.status_code == 400, "Duplicate email was not rejected"
    print("✓ Duplicate email correctly rejected with HTTP 400.")

    # Password length check (< 6 chars)
    short_resp = client.post(
        "/api/auth/register",
        json={"email": f"short_{unique_id}@example.com", "password": "123", "full_name": "Shorty"},
    )
    assert short_resp.status_code in [400, 422], "Short password was not rejected"
    print("✓ Short password (< 6 chars) rejected with HTTP 400/422.")

    return token_a, user_a_id


def test_login(token_a):
    print("\n--- 2. Testing Login & Profile Retrieval ---")
    
    # Valid Login
    login_resp = client.post(
        "/api/auth/login",
        json={"email": USER_A_EMAIL, "password": PASSWORD_A},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    assert "access_token" in login_data
    print("✓ Login succeeded with valid credentials.")

    # Invalid Password Login
    bad_login = client.post(
        "/api/auth/login",
        json={"email": USER_A_EMAIL, "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401, "Invalid password did not return HTTP 401"
    print("✓ Invalid password correctly rejected with HTTP 401 Unauthorized.")

    # Profile (/api/auth/me) with Bearer token
    headers = {"Authorization": f"Bearer {token_a}"}
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200, f"Profile fetch failed: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["email"] == USER_A_EMAIL
    assert me_data["full_name"] == "Alice Explorer"
    print(f"✓ Profile retrieved: {me_data['full_name']} ({me_data['email']})")


def test_trip_save_and_authorization(token_a):
    print("\n--- 3. Testing Trip Persistence & Ownership Authorization ---")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    sample_trip_payload = {
        "destination": "Goa",
        "days_count": 3,
        "travelers_count": 2,
        "budget": 45000.0,
        "summary": "3-day luxury beach and Portuguese fort getaway in Goa.",
        "budget_breakdown": {"stay": 18000, "food": 9000, "activities": 11250, "transport": 6750},
        "days": [
            {
                "day": 1,
                "title": "Day 1: North Goa Coastal Vibe",
                "description": "Arrive and explore Calangute and Baga.",
                "places": ["Calangute Beach", "Baga Beach"],
                "activities": ["Beach shacks", "Sunset stroll"],
                "food_recommendations": ["Goan Prawn Curry"],
                "estimated_cost": 15000.0,
            },
            {
                "day": 2,
                "title": "Day 2: Historic Aguada Fort",
                "description": "Visit historic 17th-century lighthouse fortress.",
                "places": ["Fort Aguada", "Sinquerim Beach"],
                "activities": ["Lighthouse photography", "Water sports"],
                "food_recommendations": ["Bebinca"],
                "estimated_cost": 15000.0,
            },
            {
                "day": 3,
                "title": "Day 3: Old Goa Heritage Churches",
                "description": "UNESCO World Heritage churches and departure.",
                "places": ["Basilica of Bom Jesus", "Se Cathedral"],
                "activities": ["Baroque architecture walk"],
                "food_recommendations": ["Traditional Fish Thali"],
                "estimated_cost": 15000.0,
            },
        ],
        "saved_places": [
            {"name": "Fort Aguada", "category": "Heritage", "lat": 15.4929, "lng": 73.7736},
            {"name": "Baga Beach", "category": "Beach", "lat": 15.5553, "lng": 73.7517},
        ],
    }

    # Save Trip under User A
    save_resp = client.post("/api/trips", json=sample_trip_payload, headers=headers_a)
    assert save_resp.status_code == 200, f"Trip save failed: {save_resp.text}"
    saved_trip = save_resp.json()
    trip_id = saved_trip["id"]
    assert trip_id > 0
    assert saved_trip["destination"] == "Goa"
    assert len(saved_trip["days"]) == 3
    assert len(saved_trip["saved_places"]) == 2
    print(f"✓ Trip saved successfully under User A (Trip ID: {trip_id}).")

    # List Trips for User A
    list_resp = client.get("/api/trips", headers=headers_a)
    assert list_resp.status_code == 200
    trips_list = list_resp.json()
    assert len(trips_list) >= 1
    assert any(t["id"] == trip_id for t in trips_list)
    print(f"✓ Trips listed for User A: {len(trips_list)} trip(s) found.")

    # Retrieve Trip Detail
    detail_resp = client.get(f"/api/trips/{trip_id}", headers=headers_a)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == trip_id
    assert detail["destination"] == "Goa"
    print("✓ Full Trip details retrieved successfully.")

    # --- Register User B and verify strict authorization boundaries ---
    reg_b = client.post(
        "/api/auth/register",
        json={"email": USER_B_EMAIL, "password": PASSWORD_B, "full_name": "Bob Intruder"},
    )
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B attempts to access User A's trip
    unauthorized_get = client.get(f"/api/trips/{trip_id}", headers=headers_b)
    assert unauthorized_get.status_code == 403, f"Expected 403, got {unauthorized_get.status_code}"
    print("✓ Authorization security verified: User B cannot access User A's trip (HTTP 403).")

    # User B attempts to delete User A's trip
    unauthorized_delete = client.delete(f"/api/trips/{trip_id}", headers=headers_b)
    assert unauthorized_delete.status_code == 403, f"Expected 403, got {unauthorized_delete.status_code}"
    print("✓ Authorization security verified: User B cannot delete User A's trip (HTTP 403).")

    # User A deletes their own trip
    delete_resp = client.delete(f"/api/trips/{trip_id}", headers=headers_a)
    assert delete_resp.status_code == 200
    print("✓ User A successfully deleted their own trip.")

    # Confirm trip is gone
    not_found_resp = client.get(f"/api/trips/{trip_id}", headers=headers_a)
    assert not_found_resp.status_code == 404
    print("✓ Deleted trip confirmed 404 Not Found.")


def test_anonymous_planning_preservation():
    print("\n--- 4. Testing Preservation of Anonymous Planning ---")
    
    # 1. Health check without token
    h = client.get("/api/health")
    assert h.status_code == 200
    
    # 2. Destinations without token
    d = client.get("/api/destinations")
    assert d.status_code == 200
    assert "destinations" in d.json()

    # 3. Budget calculation without token
    b_payload = {
        "destination": "Goa",
        "days": 4,
        "travelers": 2,
        "budget": 40000,
    }
    b = client.post("/api/calculate-budget", json=b_payload)
    assert b.status_code == 200
    assert "total_estimated" in b.json()

    print("✓ Anonymous trip planning is completely unblocked and functioning 100%.")


if __name__ == "__main__":
    t_a, u_a_id = test_registration_and_security()
    test_login(t_a)
    test_trip_save_and_authorization(t_a)
    test_anonymous_planning_preservation()
    print("\n=======================================================")
    print(" ALL AUTH & SAVED TRIPS VERIFICATION TESTS PASSED!     ")
    print("=======================================================\n")
