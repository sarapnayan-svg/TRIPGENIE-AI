"""
TripGenie AI — Relational Database Models.
Models:
1. User: Credentials, profile information, and account timestamps.
2. Trip: Core trip details (destination, duration, budget, summary).
3. Itinerary: Day-by-day itinerary timeline with places, activities, and food.
4. SavedPlace: Individual saved landmarks with GPS coordinates and notes.
5. UserPreference: User travel style and dietary habits.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    trips = relationship("Trip", back_populates="owner", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    destination = Column(String(100), nullable=False, index=True)
    days_count = Column(Integer, default=5)
    travelers_count = Column(Integer, default=2)
    budget = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)
    budget_breakdown = Column(JSON, nullable=True)
    packing_tips = Column(JSON, nullable=True)
    travel_tips = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    owner = relationship("User", back_populates="trips")
    itinerary_days = relationship(
        "Itinerary",
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="Itinerary.day_number",
    )
    saved_places = relationship("SavedPlace", back_populates="trip", cascade="all, delete-orphan")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    places = Column(JSON, nullable=True)
    activities = Column(JSON, nullable=True)
    food_recommendations = Column(JSON, nullable=True)
    estimated_cost = Column(Float, default=0.0)

    trip = relationship("Trip", back_populates="itinerary_days")


class SavedPlace(Base):
    __tablename__ = "saved_places"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    trip = relationship("Trip", back_populates="saved_places")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    preferred_travel_style = Column(String(50), default="balanced")
    dietary_preference = Column(String(50), default="all")
    favorite_destinations = Column(JSON, default=list)

    user = relationship("User", back_populates="preferences")
