import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import TripForm from './components/TripForm';
import Itinerary from './components/Itinerary';
import Hotels from './components/Hotels';
import Places from './components/Places';
import MapView from './components/MapView';
import BudgetChart from './components/BudgetChart';
import WeatherCard from './components/WeatherCard';
import Packages from './components/Packages';
import ChatBot from './components/ChatBot';
import Footer from './components/Footer';
import AuthModal from './components/AuthModal';
import SavedTripsModal from './components/SavedTripsModal';

import { checkHealth, planTrip, getLiveWeather, getCurrentUser, logoutUser, saveTrip } from './services/api';
import { getDestinationData } from './services/destinationsData';
import { MessageSquare, ArrowUp } from 'lucide-react';

export default function App() {
  const [formData, setFormData] = useState({
    destination: 'Goa',
    travelers: 4,
    days: 5,
    budget: 100000,
    interests: ['beach', 'adventure', 'food'],
    travelStyle: 'balanced',
    hotelPreference: 'standard',
    transportPreference: 'private_cab',
    selectedActivities: ['water_sports', 'sunset_cruise'],
    startDate: '',
    endDate: '',
  });

  const [tripPlan, setTripPlan] = useState(null);
  const [destinationData, setDestinationData] = useState(getDestinationData('Goa'));
  const [weather, setWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState({ online: false, destinations: [] });
  const [currentSection, setCurrentSection] = useState('hero');
  const [showBackToTop, setShowBackToTop] = useState(false);

  // Authentication & Saved Trips State
  const [currentUser, setCurrentUser] = useState(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState('login');
  const [savedTripsModalOpen, setSavedTripsModalOpen] = useState(false);
  const [savedTripsCount, setSavedTripsCount] = useState(0);
  const [isSavingTrip, setIsSavingTrip] = useState(false);
  const [isTripSaved, setIsTripSaved] = useState(false);
  const [pendingSave, setPendingSave] = useState(false);

  // Check backend health & fetch initial weather on mount
  useEffect(() => {
    async function init() {
      // 1. Health check
      const healthRes = await checkHealth();
      if (healthRes.success) {
        setBackendStatus({
          online: true,
          destinations: healthRes.data?.known_destinations || [],
        });
      } else {
        setBackendStatus({ online: false, destinations: [] });
      }

      // 2. Fetch live weather for default destination
      fetchWeather('Goa');

      // 3. Check existing authentication session
      const userRes = await getCurrentUser();
      if (userRes.success && userRes.data) {
        setCurrentUser(userRes.data);
        setSavedTripsCount(userRes.data.saved_trips_count || 0);
      }
    }
    init();

    // Scroll listener for back-to-top button
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 400);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Update destination metadata when destination changes
  useEffect(() => {
    const data = getDestinationData(formData.destination);
    setDestinationData(data);
    fetchWeather(formData.destination);
  }, [formData.destination]);

  const fetchWeather = async (dest) => {
    if (!dest) return;
    setWeatherLoading(true);
    setWeatherError(null);
    const wxRes = await getLiveWeather(dest);
    if (wxRes && wxRes.success) {
      setWeather(wxRes);
      setWeatherError(null);
    } else {
      setWeather(null);
      setWeatherError(wxRes?.error || `Unable to fetch meteorological readings for '${dest}'.`);
    }
    setWeatherLoading(false);
  };

  const handleSelectDestination = (destName) => {
    setFormData((prev) => ({ ...prev, destination: destName, selectedActivities: [] }));
    fetchWeather(destName);
    scrollToSection('planner');
  };

  const handleStartPlanning = () => {
    scrollToSection('planner');
  };

  const scrollToSection = (sectionId) => {
    setCurrentSection(sectionId);
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleSubmitPlan = async (e, overrideData = null) => {
    if (e) e.preventDefault();
    if (loading) return; // Prevent duplicate concurrent submissions
    setError(null);

    const activeData = overrideData || formData;

    // 1. Comprehensive Frontend Validation
    const dest = (activeData.destination || '').trim();
    if (!dest) {
      setError('Please enter a destination to plan your trip.');
      scrollToSection('planner');
      return;
    }

    const days = parseInt(activeData.days, 10);
    if (isNaN(days) || days < 1 || days > 14) {
      setError('Trip duration must be between 1 and 14 days.');
      scrollToSection('planner');
      return;
    }

    const travelers = parseInt(activeData.travelers, 10);
    if (isNaN(travelers) || travelers < 1 || travelers > 20) {
      setError('Travelers count must be between 1 and 20.');
      scrollToSection('planner');
      return;
    }

    const budget = parseInt(activeData.budget, 10);
    if (isNaN(budget) || budget < 2000) {
      setError('Total budget must be at least ₹2,000 for realistic trip planning.');
      scrollToSection('planner');
      return;
    }

    setLoading(true);

    try {
      // 2. Call FastAPI /api/plan-trip with deterministic budget parameters
      const res = await planTrip({
        ...activeData,
        destination: dest,
        days,
        travelers,
        budget,
      });

      if (res.success && res.data) {
        setTripPlan(res.data);
        setIsTripSaved(false);
        setError(null);
        // Refresh weather for planned destination
        fetchWeather(res.data.destination || dest);
        // Smooth scroll to itinerary
        setTimeout(() => scrollToSection('itinerary'), 250);
      } else {
        setError(res.error || 'Failed to generate itinerary. Please try again.');
        scrollToSection('planner');
      }
    } catch (err) {
      setError(`Network or generation error: ${err.message}`);
      scrollToSection('planner');
    } finally {
      setLoading(false);
    }
  };

  // Auth & Saved Trips Handlers
  const handleAuthSuccess = async (user) => {
    setCurrentUser(user);
    setSavedTripsCount(user.saved_trips_count || 0);
    if (pendingSave) {
      setPendingSave(false);
      await handleSaveTrip(user);
    }
  };

  const handleLogout = () => {
    logoutUser();
    setCurrentUser(null);
    setSavedTripsCount(0);
    setIsTripSaved(false);
  };

  const handleSaveTrip = async (overrideUser = null) => {
    const user = overrideUser || currentUser;
    if (!user) {
      setPendingSave(true);
      setAuthModalMode('login');
      setAuthModalOpen(true);
      return;
    }

    if (!tripPlan || isSavingTrip) return;

    setIsSavingTrip(true);
    try {
      const payload = {
        destination: tripPlan.destination || formData.destination,
        days_count: tripPlan.days?.length || formData.days,
        travelers_count: formData.travelers,
        budget: tripPlan.budget_breakdown?.user_budget || formData.budget,
        summary: tripPlan.summary || '',
        budget_breakdown: tripPlan.budget_breakdown,
        packing_tips: tripPlan.packing_tips,
        travel_tips: tripPlan.travel_tips,
        days: tripPlan.days || [],
        saved_places: [],
      };

      const res = await saveTrip(payload);
      if (res.success) {
        setIsTripSaved(true);
        setSavedTripsCount((prev) => prev + 1);
      } else {
        alert(res.error || 'Failed to save trip.');
      }
    } catch (err) {
      alert(err.message || 'Error saving trip.');
    } finally {
      setIsSavingTrip(false);
    }
  };

  const handleOpenSavedTrip = (savedTripDetail) => {
    setTripPlan(savedTripDetail);
    setFormData((prev) => ({
      ...prev,
      destination: savedTripDetail.destination,
      days: savedTripDetail.days_count,
      budget: savedTripDetail.budget,
      travelers: savedTripDetail.travelers_count,
    }));
    setDestinationData(getDestinationData(savedTripDetail.destination));
    fetchWeather(savedTripDetail.destination);
    setIsTripSaved(true);
    setTimeout(() => scrollToSection('itinerary'), 200);
  };

  const handleApplyAlternative = (param) => {
    const updated = { ...formData, ...param };
    setFormData(updated);
    handleSubmitPlan(null, updated);
  };

  const handleAutoOptimizeWithinBudget = () => {
    const optimized = {
      ...formData,
      hotelPreference: formData.travelers <= 2 ? 'budget' : 'standard',
      transportPreference: formData.travelers <= 2 ? 'rental' : 'public',
      travelStyle: 'balanced',
      selectedActivities: [],
    };
    setFormData(optimized);
    handleSubmitPlan(null, optimized);
  };

  const handleSelectPackage = (pkg) => {
    const match = pkg.duration.match(/(\d+)\s*Days?/i);
    const days = match ? parseInt(match[1], 10) : formData.days;
    const budget = pkg.price * formData.travelers;

    setFormData((prev) => ({
      ...prev,
      days,
      budget,
    }));

    scrollToSection('planner');
  };

  return (
    <div className="min-h-screen flex flex-col bg-sand text-ink relative">
      
      {/* 1. Header Component */}
      <Header
        backendStatus={backendStatus}
        onNavClick={scrollToSection}
        currentSection={currentSection}
        currentUser={currentUser}
        onOpenAuthModal={(m) => {
          setAuthModalMode(m || 'login');
          setAuthModalOpen(true);
        }}
        onOpenSavedTrips={() => setSavedTripsModalOpen(true)}
        onLogout={handleLogout}
        savedTripsCount={savedTripsCount}
      />

      <main className="flex-1">
        {/* 2. Hero Section */}
        <Hero
          onSelectDestination={handleSelectDestination}
          onStartPlanning={handleStartPlanning}
        />

        {/* 3. Trip Planning Form & 4. PLAN MY TRIP Button */}
        <TripForm
          formData={formData}
          setFormData={setFormData}
          onSubmit={handleSubmitPlan}
          loading={loading}
          error={error}
          backendStatus={backendStatus}
        />

        {/* 5. Generated Itinerary Section */}
        <Itinerary
          tripPlan={tripPlan}
          formData={formData}
          destinationData={destinationData}
          loading={loading}
          onSaveTrip={tripPlan ? () => handleSaveTrip() : null}
          isSavingTrip={isSavingTrip}
          isTripSaved={isTripSaved}
        />

        {/* 6. Hotels Section */}
        <Hotels
          destinationData={destinationData}
          destinationName={tripPlan?.destination || formData.destination}
          formData={formData}
          tripPlan={tripPlan}
        />

        {/* 7. Places Section */}
        <Places
          destinationData={destinationData}
          destinationName={tripPlan?.destination || formData.destination}
        />

        {/* 8. Map Section */}
        <MapView
          destinationName={tripPlan?.destination || formData.destination}
          itineraryDays={tripPlan?.days}
        />

        {/* 9. Budget Section (Deterministic 5-Category Intelligence) */}
        <BudgetChart
          budgetBreakdown={tripPlan?.budget_breakdown}
          totalBudget={formData.budget}
          travelers={formData.travelers}
          days={formData.days}
          destinationName={tripPlan?.destination || formData.destination}
          onApplyAlternative={handleApplyAlternative}
          onAutoOptimizeWithinBudget={handleAutoOptimizeWithinBudget}
        />

        {/* 10. Weather Section */}
        <WeatherCard
          weather={weather}
          destinationName={tripPlan?.destination || formData.destination}
          bestTimeToVisit={destinationData?.bestTimeToVisit}
          onRefresh={() => fetchWeather(tripPlan?.destination || formData.destination)}
          loading={weatherLoading}
          error={weatherError}
        />

        {/* 11. Packages Section */}
        <Packages
          destinationData={destinationData}
          destinationName={tripPlan?.destination || formData.destination}
          onSelectPackage={handleSelectPackage}
        />
      </main>

      {/* 12. AI Chatbot Section (TripGenie Assistant) */}
      <ChatBot
        tripPlan={tripPlan}
        formData={formData}
        destinationData={destinationData}
        backendStatus={backendStatus}
      />

      {/* Footer */}
      <Footer onNavClick={scrollToSection} />

      {/* Floating Back to Top Button */}
      {showBackToTop && (
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="fixed bottom-6 left-6 z-40 p-3 rounded-full bg-white shadow-card hover:shadow-card-hover border border-sand-dark text-brand-600 hover:text-brand-800 transition-all duration-200"
          aria-label="Back to top"
        >
          <ArrowUp className="w-5 h-5" />
        </button>
      )}

      {/* Authentication Modal (Sign In / Register) */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
        initialMode={authModalMode}
      />

      {/* Saved Trips Modal (View / Open / Delete) */}
      <SavedTripsModal
        isOpen={savedTripsModalOpen}
        onClose={() => setSavedTripsModalOpen(false)}
        onOpenTrip={handleOpenSavedTrip}
        currentUser={currentUser}
      />

    </div>
  );
}
