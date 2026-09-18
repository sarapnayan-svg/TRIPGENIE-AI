import React, { useState, useMemo, useRef, useEffect } from 'react';
import { 
  MapPin, Users, Calendar, IndianRupee, Heart, Compass, 
  Sparkles, Check, AlertCircle, Loader2, Clock, ShieldCheck,
  Building2, Car, Activity, TrendingDown, AlertTriangle, CheckCircle2
} from 'lucide-react';
import { KNOWN_DESTINATIONS } from '../services/destinationsData';

const INTEREST_OPTIONS = [
  { id: 'beach', label: 'Beach & Sun', emoji: '🏖️' },
  { id: 'adventure', label: 'Adventure Sports', emoji: '🚤' },
  { id: 'food', label: 'Food & Culinary', emoji: '🍜' },
  { id: 'culture', label: 'Culture & Heritage', emoji: '🏛️' },
  { id: 'shopping', label: 'Local Shopping', emoji: '🛍️' },
  { id: 'nightlife', label: 'Nightlife & Lounges', emoji: '🌃' },
  { id: 'nature', label: 'Nature & Scenic', emoji: '🌄' },
  { id: 'relaxation', label: 'Relaxation & Spa', emoji: '💆' },
];

const TRAVEL_STYLES = [
  { id: 'backpacker', label: 'Backpacker / Budget', desc: 'Hostels, public transit, street food' },
  { id: 'balanced', label: 'Balanced Comfort', desc: '3-star resorts, private cabs, popular cafes' },
  { id: 'luxury', label: 'Luxury Resort', desc: '5-star beachfront stays, fine dining, spa' },
  { id: 'family', label: 'Family Friendly', desc: 'Spacious suites, relaxed pace, kids friendly' },
  { id: 'romantic', label: 'Romantic Couple', desc: 'Secluded villas, sunset views, candlelight' },
];

const HOTEL_OPTIONS = [
  { id: 'hostel', label: 'Hostel / Dorm', priceBadge: '₹900/bed', desc: 'Backpacker hostels & social dorms' },
  { id: 'budget', label: 'Budget Guesthouse', priceBadge: '₹1,600/room', desc: 'Clean 2-star guesthouses' },
  { id: 'standard', label: 'Standard 3★', priceBadge: '₹3,200/room', desc: 'Comfortable boutique stays' },
  { id: 'premium', label: 'Premium 4★', priceBadge: '₹6,800/room', desc: 'Scenic resorts & heritage havelis' },
  { id: 'luxury', label: 'Luxury 5★', priceBadge: '₹14,500/room', desc: 'Beachfront villas & 5★ palaces' },
];

const TRANSPORT_OPTIONS = [
  { id: 'public', label: 'Public Transit', priceBadge: '₹250/day/pax', desc: 'Buses, metro, shared autos' },
  { id: 'rental', label: 'Scooter / Car Rental', priceBadge: 'From ₹600/day', desc: 'Self-drive rental + fuel' },
  { id: 'private_cab', label: 'Private AC Cab', priceBadge: '₹2,800/day', desc: 'Dedicated car & chauffeur' },
  { id: 'flight_premium', label: 'Flight + SUV Cab', priceBadge: '₹6,500 + SUV', desc: 'Fast flights + luxury SUV' },
];

const DESTINATION_ACTIVITIES_MAP = {
  goa: [
    { id: 'scuba_diving', label: 'Grande Island Scuba Diving', price: '₹2,500', costNum: 2500, emoji: '🤿' },
    { id: 'water_sports', label: '5-in-1 Water Sports Combo', price: '₹1,500', costNum: 1500, emoji: '🚤' },
    { id: 'spice_plantation', label: 'Spice Plantation & Lunch', price: '₹600', costNum: 600, emoji: '🌿' },
    { id: 'sunset_cruise', label: 'Mandovi Sunset River Cruise', price: '₹500', costNum: 500, emoji: '⛵' },
    { id: 'fort_tour', label: 'Fort Aguada Heritage Tour', price: '₹300', costNum: 300, emoji: '🏰' },
    { id: 'beach_leisure', label: 'Free Sunset & Beach Stroll', price: 'Free', costNum: 0, emoji: '🏖️' },
  ],
  kerala: [
    { id: 'houseboat_cruise', label: 'Alleppey Houseboat Cruise', price: '₹3,000', costNum: 3000, emoji: '🛶' },
    { id: 'shikara_ride', label: 'Vembanad Shikara Boat Ride', price: '₹600', costNum: 600, emoji: '🚣' },
    { id: 'kathakali_show', label: 'Kathakali Dance & Martial Arts', price: '₹500', costNum: 500, emoji: '🎭' },
    { id: 'eravikulam_safari', label: 'Eravikulam Wildlife Safari', price: '₹250', costNum: 250, emoji: '🦌' },
    { id: 'tea_factory_tour', label: 'Munnar Tea Factory & Museum', price: '₹200', costNum: 200, emoji: '🍵' },
    { id: 'fort_kochi_walk', label: 'Fort Kochi Heritage Trail', price: 'Free', costNum: 0, emoji: '🏛️' },
  ],
  manali: [
    { id: 'paragliding', label: 'Solang Valley Paragliding', price: '₹2,500', costNum: 2500, emoji: '🪂' },
    { id: 'atal_tunnel_tour', label: 'Atal Tunnel & Sissu Excursion', price: '₹1,200', costNum: 1200, emoji: '🏔️' },
    { id: 'river_rafting', label: 'Beas River White-Water Rafting', price: '₹1,200', costNum: 1200, emoji: '🚣' },
    { id: 'jogini_trek', label: 'Jogini Waterfall Pine Hike', price: 'Free', costNum: 0, emoji: '🌲' },
    { id: 'hadimba_temple', label: 'Hadimba Devi Temple Visit', price: '₹50', costNum: 50, emoji: '🛕' },
  ],
  jaipur: [
    { id: 'chokhi_dhani', label: 'Chokhi Dhani Folk Village Feast', price: '₹1,100', costNum: 1100, emoji: '🎪' },
    { id: 'city_palace_museum', label: 'City Palace & Observatory Tour', price: '₹700', costNum: 700, emoji: '👑' },
    { id: 'amber_fort_tour', label: 'Amber Fort Guided Heritage Tour', price: '₹500', costNum: 500, emoji: '🏰' },
    { id: 'hawa_mahal_bazaar', label: 'Hawa Mahal & Johari Bazaar', price: '₹200', costNum: 200, emoji: '🛍️' },
    { id: 'nahargarh_sunset', label: 'Nahargarh Fort Hilltop Sunset', price: '₹100', costNum: 100, emoji: '🌅' },
  ],
  rishikesh: [
    { id: 'bungee_jumping', label: 'Mohan Chatti Bungee Jump', price: '₹3,500', costNum: 3500, emoji: '🪢' },
    { id: 'ganges_rafting', label: '16km Ganges White-Water Rafting', price: '₹1,200', costNum: 1200, emoji: '🌊' },
    { id: 'beatles_ashram', label: 'The Beatles Ashram Art Tour', price: '₹150', costNum: 150, emoji: '🧘' },
    { id: 'neelkanth_temple', label: 'Neelkanth Mahadev Mountain Tour', price: '₹300', costNum: 300, emoji: '⛰️' },
    { id: 'triveni_ghat_aarti', label: 'Triveni Ghat Evening Maha Aarti', price: 'Free', costNum: 0, emoji: '🪔' },
  ],
};

const BUDGET_PRESETS = [
  { label: '₹35,000', value: 35000 },
  { label: '₹65,000', value: 65000 },
  { label: '₹1,00,000', value: 100000 },
  { label: '₹1,75,000', value: 175000 },
];

export default function TripForm({ formData, setFormData, onSubmit, loading, error, backendStatus }) {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const suggestionsRef = useRef(null);

  // Close suggestions dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Active activities catalog based on chosen destination
  const destKey = (formData.destination || 'goa').toLowerCase().trim();
  const availableActivities = DESTINATION_ACTIVITIES_MAP[destKey] || DESTINATION_ACTIVITIES_MAP['goa'];

  const handleInterestToggle = (id) => {
    const current = formData.interests || [];
    if (current.includes(id)) {
      setFormData({ ...formData, interests: current.filter((item) => item !== id) });
    } else {
      setFormData({ ...formData, interests: [...current, id] });
    }
  };

  const handleActivityToggle = (actId) => {
    const current = formData.selectedActivities || [];
    if (current.includes(actId)) {
      setFormData({ ...formData, selectedActivities: current.filter((id) => id !== actId) });
    } else {
      setFormData({ ...formData, selectedActivities: [...current, actId] });
    }
  };

  const handleStartDateChange = (e) => {
    const startDate = e.target.value;
    let days = formData.days;
    if (formData.endDate && startDate) {
      const start = new Date(startDate);
      const end = new Date(formData.endDate);
      const diffTime = end - start;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      if (diffDays >= 1 && diffDays <= 14) {
        days = diffDays;
      }
    }
    setFormData({ ...formData, startDate, days });
  };

  const handleEndDateChange = (e) => {
    const endDate = e.target.value;
    let days = formData.days;
    if (formData.startDate && endDate) {
      const start = new Date(formData.startDate);
      const end = new Date(endDate);
      const diffTime = end - start;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      if (diffDays >= 1 && diffDays <= 14) {
        days = diffDays;
      }
    }
    setFormData({ ...formData, endDate, days });
  };

  // Instant reactive preliminary budget calculation
  const liveBudgetCalc = useMemo(() => {
    const budget = Number(formData.budget) || 50000;
    const days = Math.max(1, Number(formData.days) || 4);
    const travelers = Math.max(1, Number(formData.travelers) || 2);
    const nights = Math.max(1, days - 1);

    // Hotel
    const hotelTier = formData.hotelPreference || 'standard';
    const hotelRates = { hostel: 900, budget: 1600, standard: 3200, premium: 6800, luxury: 14500 };
    const hotelRate = hotelRates[hotelTier] || 3200;
    const rooms = hotelTier === 'hostel' ? travelers : Math.ceil(travelers / 2);
    const accCost = hotelRate * rooms * nights;

    // Food
    const styleRates = { backpacker: 450, balanced: 1100, luxury: 3800, family: 1200, romantic: 2200 };
    const foodRate = styleRates[formData.travelStyle] || 1100;
    const foodCost = foodRate * travelers * days;

    // Transport
    const trans = formData.transportPreference || 'private_cab';
    let transCost = 0;
    if (trans === 'public') transCost = 250 * travelers * days;
    else if (trans === 'rental') transCost = (travelers <= 2 ? 1100 : 2700) * days;
    else if (trans === 'flight_premium') transCost = 6500 * travelers + 3400 * days;
    else transCost = Math.ceil(travelers / 4) * 2800 * days;

    // Activities
    let actCost = 0;
    const selected = formData.selectedActivities || [];
    if (selected.length > 0) {
      selected.forEach((id) => {
        const item = availableActivities.find((a) => a.id === id);
        if (item) actCost += item.costNum * travelers;
      });
    } else {
      actCost = 500 * travelers * Math.min(3, days);
    }

    const subtotal = accCost + foodCost + transCost + actCost;
    const misc = Math.round(subtotal * 0.07);
    const totalEst = subtotal + misc;
    const remaining = budget - totalEst;
    const util = Math.round((totalEst / Math.max(1, budget)) * 100);

    return {
      totalEst,
      remaining,
      util,
      isOver: totalEst > budget,
      deficit: Math.max(0, totalEst - budget),
    };
  }, [formData, availableActivities]);

  return (
    <section id="planner" className="scroll-mt-24 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mb-20">
      <div className="bg-white rounded-3xl p-6 sm:p-10 shadow-card border border-sand-dark relative overflow-hidden">
        
        {/* Decorative Top Accent Bar */}
        <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-brand-600 via-brand-400 to-amber-400"></div>

        <div className="mb-8">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-brand-50 text-brand-700 text-xs font-bold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Travel Parameter Generator</span>
          </div>
          <h2 className="font-display font-bold text-2xl sm:text-3xl text-ink">
            Configure Your Custom Travel Profile
          </h2>
          <p className="text-sm text-ink-muted">
            Configure your destination, budget, hotel, transit, and experiences. Our deterministic budget engine and RAG pipeline ground generation in verified knowledge.
          </p>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3 animate-fade-in">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-bold">Generation Notice</div>
              <div>{error}</div>
              {error.includes('knowledge base') && (
                <div className="mt-2 text-xs text-rose-700">
                  Tip: The academic knowledge base features pre-embedded ground truth for:{' '}
                  <strong>Goa, Kerala, Manali, Jaipur, Rishikesh</strong>.
                </div>
              )}
            </div>
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-8">
          
          {/* Row 1: Destination & Travelers */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            
            {/* Destination Input */}
            <div className="md:col-span-7 relative" ref={suggestionsRef}>
              <label htmlFor="destination-input" className="block text-xs font-bold text-ink uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-brand-600" />
                <span>Destination</span>
                <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="destination-input"
                  type="text"
                  placeholder="Where do you want to go? (e.g. Goa, Kerala, Manali)"
                  value={formData.destination}
                  onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                  onFocus={() => setShowSuggestions(true)}
                  aria-required="true"
                  aria-invalid={!formData.destination?.trim()}
                  className={`w-full pl-11 pr-4 py-3.5 rounded-2xl border text-ink font-semibold transition-all focus:ring-2 focus:ring-brand-100 ${
                    !formData.destination?.trim()
                      ? 'border-rose-300 focus:border-rose-500'
                      : 'border-sand-dark focus:border-brand-500'
                  }`}
                  required
                />
                <MapPin className="absolute left-4 top-4 w-4 h-4 text-ink-muted" />
              </div>
              {!formData.destination?.trim() && (
                <div className="mt-1.5 text-xs text-rose-600 font-medium flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>Please specify a destination.</span>
                </div>
              )}

              {/* Suggestions Dropdown */}
              {showSuggestions && (
                <div className="absolute z-30 left-0 right-0 mt-2 p-2 bg-white rounded-2xl shadow-card-hover border border-sand-dark animate-fade-in">
                  <div className="text-[11px] font-bold text-ink-muted uppercase px-3 py-1">
                    Featured Knowledge Bases
                  </div>
                  <div className="grid grid-cols-2 gap-1 mt-1">
                    {KNOWN_DESTINATIONS.map((dest) => (
                      <button
                        key={dest.name}
                        type="button"
                        onClick={() => {
                          setFormData({ ...formData, destination: dest.name });
                          setShowSuggestions(false);
                        }}
                        className="p-2 rounded-xl text-left hover:bg-sand flex items-center gap-2 text-xs font-bold text-ink transition-colors"
                      >
                        <span className="text-base">{dest.tag.split(' ')[0]}</span>
                        <div className="truncate">
                          <div>{dest.name}</div>
                          <div className="text-[10px] text-ink-muted font-normal">{dest.state}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Travelers Stepper */}
            <div className="md:col-span-5">
              <label className="block text-xs font-bold text-ink uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Users className="w-4 h-4 text-brand-600" />
                <span>Number of Travelers</span>
              </label>
              <div className="flex items-center justify-between p-2.5 rounded-2xl border border-sand-dark bg-white">
                <button
                  type="button"
                  aria-label="Decrease number of travelers"
                  disabled={formData.travelers <= 1}
                  onClick={() => setFormData({ ...formData, travelers: Math.max(1, (formData.travelers || 1) - 1) })}
                  className="w-10 h-10 rounded-xl bg-sand hover:bg-sand-dark disabled:opacity-40 font-bold text-ink flex items-center justify-center transition-colors"
                >
                  -
                </button>
                <div className="text-center font-display font-bold text-lg text-ink" aria-live="polite">
                  {formData.travelers} {formData.travelers === 1 ? 'Traveler' : 'Travelers'}
                </div>
                <button
                  type="button"
                  aria-label="Increase number of travelers"
                  disabled={formData.travelers >= 20}
                  onClick={() => setFormData({ ...formData, travelers: Math.min(20, (formData.travelers || 1) + 1) })}
                  className="w-10 h-10 rounded-xl bg-sand hover:bg-sand-dark disabled:opacity-40 font-bold text-ink flex items-center justify-center transition-colors"
                >
                  +
                </button>
              </div>
            </div>

          </div>

          {/* Row 2: Duration & Total Budget */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
            
            {/* Duration Slider */}
            <div className="md:col-span-5">
              <div className="flex items-center justify-between mb-2">
                <label htmlFor="duration-slider" className="text-xs font-bold text-ink uppercase tracking-wider flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-brand-600" />
                  <span>Duration ({formData.days} Days)</span>
                </label>
                <span className="text-xs font-bold text-brand-700 bg-brand-50 px-2 py-0.5 rounded-md">
                  {formData.days} Days / {Math.max(1, formData.days - 1)} Nights
                </span>
              </div>
              <input
                id="duration-slider"
                type="range"
                min="1"
                max="14"
                aria-label="Duration in days"
                aria-valuemin="1"
                aria-valuemax="14"
                aria-valuenow={formData.days}
                value={formData.days}
                onChange={(e) => setFormData({ ...formData, days: parseInt(e.target.value) || 1 })}
                className="w-full accent-brand-600 h-2 bg-sand-dark rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[11px] text-ink-muted mt-1">
                <span>1 Day</span>
                <span>7 Days</span>
                <span>14 Days (Max)</span>
              </div>
            </div>

            {/* Budget Input & Presets */}
            <div className="md:col-span-7">
              <label htmlFor="total-budget" className="block text-xs font-bold text-ink uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <IndianRupee className="w-4 h-4 text-brand-600" />
                <span>Total Budget (INR)</span>
                <span className="text-rose-500">*</span>
              </label>
              <div className="relative mb-2">
                <span className="absolute left-4 top-3.5 text-ink-muted font-bold">₹</span>
                <input
                  id="total-budget"
                  type="number"
                  min="2000"
                  step="1000"
                  aria-label="Total trip budget in INR"
                  aria-invalid={formData.budget < 2000}
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: parseInt(e.target.value) || 0 })}
                  className={`w-full pl-9 pr-4 py-3 rounded-xl border font-bold transition-all focus:ring-2 focus:ring-brand-100 ${
                    formData.budget < 2000
                      ? 'border-rose-300 focus:border-rose-500 text-rose-800'
                      : 'border-sand-dark focus:border-brand-500 text-ink'
                  }`}
                />
              </div>
              {formData.budget < 2000 && (
                <div className="mb-2 text-xs text-rose-600 font-medium flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>Minimum budget is ₹2,000 for realistic trip calculation.</span>
                </div>
              )}
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-[11px] text-ink-muted font-semibold">Quick Presets:</span>
                {BUDGET_PRESETS.map((preset) => (
                  <button
                    key={preset.label}
                    type="button"
                    onClick={() => setFormData({ ...formData, budget: preset.value })}
                    className={`px-2.5 py-1 rounded-lg text-xs font-bold border transition-all ${
                      formData.budget === preset.value
                        ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                        : 'bg-sand hover:bg-sand-dark text-ink border-sand-dark'
                    }`}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>

          </div>

          {/* Row 3: Hotel Preference Selector */}
          <div>
            <label className="block text-xs font-bold text-ink uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Building2 className="w-4 h-4 text-brand-600" />
              <span>Hotel & Accommodation Preference</span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
              {HOTEL_OPTIONS.map((hotel) => {
                const isSelected = (formData.hotelPreference || 'standard') === hotel.id;
                return (
                  <button
                    key={hotel.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, hotelPreference: hotel.id })}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      isSelected
                        ? 'bg-brand-50 border-brand-500 ring-2 ring-brand-200 text-brand-900 shadow-sm'
                        : 'bg-white hover:bg-sand text-ink border-sand-dark'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold">{hotel.label}</span>
                      <span className="text-[10px] font-bold text-brand-700 bg-brand-100/60 px-1.5 py-0.5 rounded">
                        {hotel.priceBadge}
                      </span>
                    </div>
                    <div className="text-[10px] text-ink-muted line-clamp-2">{hotel.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Row 4: Transportation Preference Selector */}
          <div>
            <label className="block text-xs font-bold text-ink uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Car className="w-4 h-4 text-brand-600" />
              <span>Transportation Preference</span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
              {TRANSPORT_OPTIONS.map((trans) => {
                const isSelected = (formData.transportPreference || 'private_cab') === trans.id;
                return (
                  <button
                    key={trans.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, transportPreference: trans.id })}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      isSelected
                        ? 'bg-brand-50 border-brand-500 ring-2 ring-brand-200 text-brand-900 shadow-sm'
                        : 'bg-white hover:bg-sand text-ink border-sand-dark'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold">{trans.label}</span>
                      <span className="text-[10px] font-bold text-brand-700 bg-brand-100/60 px-1.5 py-0.5 rounded">
                        {trans.priceBadge}
                      </span>
                    </div>
                    <div className="text-[10px] text-ink-muted line-clamp-2">{trans.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Row 5: Specific Destination Activities (With Real Pricing) */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-xs font-bold text-ink uppercase tracking-wider flex items-center gap-1.5">
                <Activity className="w-4 h-4 text-emerald-600" />
                <span>Curated Experiences & Activities ({formData.destination || 'Destination'})</span>
              </label>
              <span className="text-[11px] text-ink-muted">
                {(formData.selectedActivities || []).length} selected
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {availableActivities.map((act) => {
                const isSelected = (formData.selectedActivities || []).includes(act.id);
                return (
                  <button
                    key={act.id}
                    type="button"
                    onClick={() => handleActivityToggle(act.id)}
                    className={`p-3 rounded-xl border text-left flex items-center justify-between gap-2 transition-all ${
                      isSelected
                        ? 'bg-emerald-50 border-emerald-500 ring-2 ring-emerald-200 text-emerald-900 shadow-sm'
                        : 'bg-white hover:bg-sand text-ink border-sand-dark'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <span className="text-base">{act.emoji}</span>
                      <span className="text-xs font-bold truncate">{act.label}</span>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                        {act.price}
                      </span>
                      {isSelected && <Check className="w-3.5 h-3.5 text-emerald-600" />}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Row 6: Travel Style & Dates */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Travel Style */}
            <div className="lg:col-span-7">
              <label className="block text-xs font-bold text-ink uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Compass className="w-4 h-4 text-brand-600" />
                <span>Travel Style & Pace</span>
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {TRAVEL_STYLES.map((style) => {
                  const selected = (formData.travelStyle || 'balanced') === style.id;
                  return (
                    <button
                      key={style.id}
                      type="button"
                      onClick={() => setFormData({ ...formData, travelStyle: style.id })}
                      className={`p-2.5 rounded-xl border text-left transition-all ${
                        selected
                          ? 'bg-brand-50 border-brand-500 ring-2 ring-brand-200 text-brand-900'
                          : 'bg-white hover:bg-sand text-ink border-sand-dark'
                      }`}
                    >
                      <div className="text-xs font-bold">{style.label}</div>
                      <div className="text-[10px] text-ink-muted line-clamp-1">{style.desc}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Travel Dates */}
            <div className="lg:col-span-5 p-3.5 rounded-2xl bg-sand/50 border border-sand-dark">
              <div className="text-xs font-bold text-ink uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-brand-600" />
                <span>Optional Travel Dates</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] text-ink-muted mb-0.5">Start</label>
                  <input
                    type="date"
                    value={formData.startDate || ''}
                    onChange={handleStartDateChange}
                    className="w-full px-2.5 py-1.5 rounded-lg border border-sand-dark bg-white text-ink text-xs font-medium focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-ink-muted mb-0.5">End</label>
                  <input
                    type="date"
                    value={formData.endDate || ''}
                    onChange={handleEndDateChange}
                    className="w-full px-2.5 py-1.5 rounded-lg border border-sand-dark bg-white text-ink text-xs font-medium focus:border-brand-500"
                  />
                </div>
              </div>
            </div>

          </div>

          {/* Row 7: Interests */}
          <div>
            <label className="block text-xs font-bold text-ink uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Heart className="w-4 h-4 text-rose-500" />
              <span>Interests (Select all that apply)</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {INTEREST_OPTIONS.map((interest) => {
                const active = (formData.interests || []).includes(interest.id);
                return (
                  <button
                    key={interest.id}
                    type="button"
                    onClick={() => handleInterestToggle(interest.id)}
                    className={`px-3 py-2 rounded-xl border text-xs font-semibold flex items-center gap-2 transition-all ${
                      active
                        ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                        : 'bg-white hover:bg-sand text-ink border-sand-dark'
                    }`}
                  >
                    <span>{interest.emoji}</span>
                    <span className="truncate">{interest.label}</span>
                    {active && <Check className="w-3.5 h-3.5 ml-auto flex-shrink-0" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Live Deterministic Budget Estimation Strip */}
          <div className={`p-4 rounded-2xl border transition-all ${
            liveBudgetCalc.isOver
              ? 'bg-rose-50/70 border-rose-200'
              : liveBudgetCalc.util > 85
                ? 'bg-amber-50/70 border-amber-200'
                : 'bg-emerald-50/70 border-emerald-200'
          }`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                {liveBudgetCalc.isOver ? (
                  <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0" />
                ) : (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                )}
                <div>
                  <div className="text-xs font-bold text-ink flex items-center gap-2">
                    <span>Live Deterministic Estimate:</span>
                    <span className="font-display text-sm font-extrabold text-ink">
                      ₹{liveBudgetCalc.totalEst.toLocaleString('en-IN')}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      liveBudgetCalc.isOver
                        ? 'bg-rose-200 text-rose-800'
                        : 'bg-emerald-200 text-emerald-800'
                    }`}>
                      {liveBudgetCalc.util}% Utilization
                    </span>
                  </div>
                  <div className="text-[11px] text-ink-muted">
                    {liveBudgetCalc.isOver ? (
                      <span className="text-rose-700 font-semibold">
                        Estimated cost exceeds total budget by ₹{liveBudgetCalc.deficit.toLocaleString('en-IN')}. Consider adjusting hotel or transit tier below.
                      </span>
                    ) : (
                      <span className="text-emerald-800">
                        Remaining buffer: ₹{liveBudgetCalc.remaining.toLocaleString('en-IN')} across {formData.travelers} travelers for {formData.days} days.
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full sm:w-48">
                <div className="h-2 rounded-full bg-black/10 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      liveBudgetCalc.isOver
                        ? 'bg-rose-500'
                        : liveBudgetCalc.util > 85
                          ? 'bg-amber-500'
                          : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, liveBudgetCalc.util)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Section: PLAN MY TRIP Button */}
          <div className="pt-4 border-t border-sand-dark">
            <button
              type="submit"
              disabled={loading}
              aria-busy={loading}
              className={`w-full py-4 sm:py-5 rounded-2xl text-white font-display font-extrabold text-lg sm:text-xl shadow-glow hover:shadow-card-hover transform hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 flex items-center justify-center gap-3 ${
                loading
                  ? 'bg-brand-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-brand-700 via-brand-600 to-indigo-600 hover:from-brand-800 hover:to-indigo-700'
              }`}
            >
              {loading ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin text-white" />
                  <span>Retrieving RAG Chunks & Calculating Budget...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-6 h-6 text-amber-300" />
                  <span>PLAN MY TRIP →</span>
                </>
              )}
            </button>
            <p className="text-center text-xs text-ink-muted mt-2.5">
              Generates RAG-grounded daily activities respecting your ₹{formData.budget.toLocaleString('en-IN')} budget.
            </p>
          </div>

        </form>
      </div>
    </section>
  );
}
