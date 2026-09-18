import React, { useState, useEffect } from 'react';
import {
  X,
  Calendar,
  Wallet,
  Users,
  MapPin,
  Trash2,
  ExternalLink,
  Loader2,
  Bookmark,
  Sparkles,
  ArrowRight,
} from 'lucide-react';
import { getSavedTrips, getTripById, deleteTrip } from '../services/api';

export default function SavedTripsModal({ isOpen, onClose, onOpenTrip, currentUser }) {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState(null);
  const [error, setError] = useState(null);

  const fetchTrips = async () => {
    if (!isOpen) return;
    setLoading(true);
    setError(null);
    const res = await getSavedTrips();
    if (res.success) {
      setTrips(res.data);
    } else {
      setError(res.error || 'Failed to load saved trips.');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchTrips();
  }, [isOpen]);

  if (!isOpen) return null;

  const handleOpenTrip = async (tripId) => {
    setActionLoadingId(tripId);
    try {
      const res = await getTripById(tripId);
      if (res.success && res.data) {
        onOpenTrip(res.data);
        onClose();
      } else {
        alert(res.error || 'Could not load trip details.');
      }
    } catch (err) {
      alert(err.message || 'Error loading trip.');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDeleteTrip = async (e, tripId) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this saved trip?')) return;

    setActionLoadingId(tripId);
    try {
      const res = await deleteTrip(tripId);
      if (res.success) {
        setTrips((prev) => prev.filter((t) => t.id !== tripId));
      } else {
        alert(res.error || 'Failed to delete trip.');
      }
    } catch (err) {
      alert(err.message || 'Error deleting trip.');
    } finally {
      setActionLoadingId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl border border-sand-dark relative max-h-[85vh] flex flex-col animate-in zoom-in-95 duration-200">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-sand-dark">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-brand-50 border border-brand-200 text-brand-700 flex items-center justify-center text-xl shadow-sm">
              <Bookmark className="w-5 h-5 text-brand-600 fill-brand-100" />
            </div>
            <div>
              <h3 className="font-display font-extrabold text-xl text-ink">
                My Saved Trips
              </h3>
              <p className="text-xs text-ink-muted">
                {currentUser?.full_name ? `${currentUser.full_name}'s saved itineraries` : 'Your saved itineraries in PostgreSQL'}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-ink-muted hover:text-ink p-1.5 rounded-full hover:bg-sand transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto py-5 space-y-4 pr-1">
          {loading ? (
            <div className="py-16 text-center text-ink-muted flex flex-col items-center justify-center gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-brand-600" />
              <span className="text-sm font-medium">Retrieving your saved itineraries...</span>
            </div>
          ) : error ? (
            <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-sm text-rose-800 text-center">
              {error}
            </div>
          ) : trips.length === 0 ? (
            <div className="py-16 text-center max-w-md mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-sand flex items-center justify-center mx-auto mb-3 text-ink-muted">
                <Bookmark className="w-7 h-7 text-ink-muted" />
              </div>
              <h4 className="font-display font-bold text-base text-ink">No saved trips yet</h4>
              <p className="text-xs text-ink-muted mt-1 mb-5">
                Generate an itinerary using the trip planner and click "⭐ Save Trip" to persist it to your account!
              </p>
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-xl bg-brand-600 text-white font-bold text-xs hover:bg-brand-700 transition-colors shadow-sm"
              >
                Plan a Trip Now
              </button>
            </div>
          ) : (
            trips.map((trip) => {
              const isActionLoading = actionLoadingId === trip.id;
              const dateStr = trip.created_at
                ? new Date(trip.created_at).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })
                : 'Recent';

              return (
                <div
                  key={trip.id}
                  onClick={() => handleOpenTrip(trip.id)}
                  className="group bg-sand/40 hover:bg-white rounded-2xl p-4 sm:p-5 border border-sand-dark/80 hover:border-brand-300 hover:shadow-card transition-all duration-200 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded-md bg-brand-50 text-brand-700 text-xs font-extrabold border border-brand-200">
                        {trip.destination}
                      </span>
                      <span className="text-[11px] text-ink-muted font-medium">
                        Saved on {dateStr}
                      </span>
                    </div>

                    <h4 className="font-display font-bold text-base text-ink group-hover:text-brand-600 transition-colors">
                      {trip.days_count}-Day Trip to {trip.destination}
                    </h4>

                    {trip.summary && (
                      <p className="text-xs text-ink-muted line-clamp-1 leading-relaxed">
                        {trip.summary}
                      </p>
                    )}

                    <div className="flex flex-wrap items-center gap-3 pt-1 text-xs text-ink">
                      <span className="inline-flex items-center gap-1 text-ink-muted font-medium">
                        <Users className="w-3.5 h-3.5 text-brand-500" />
                        {trip.travelers_count} Guests
                      </span>
                      <span>•</span>
                      <span className="inline-flex items-center gap-1 font-bold text-ink">
                        <Wallet className="w-3.5 h-3.5 text-emerald-600" />
                        ₹{Math.round(trip.budget).toLocaleString('en-IN')}
                      </span>
                      <span>•</span>
                      <span className="text-ink-muted">
                        {trip.days_total || trip.days_count} Itinerary Days
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2.5 self-end sm:self-center flex-shrink-0">
                    <button
                      onClick={(e) => handleDeleteTrip(e, trip.id)}
                      disabled={isActionLoading}
                      className="p-2.5 rounded-xl bg-white hover:bg-rose-50 text-ink-muted hover:text-rose-600 border border-sand-dark transition-all disabled:opacity-50"
                      title="Delete trip"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>

                    <button
                      onClick={() => handleOpenTrip(trip.id)}
                      disabled={isActionLoading}
                      className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white text-xs font-bold shadow-sm transition-all disabled:opacity-50"
                    >
                      {isActionLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <span>Open Trip</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </>
                      )}
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Modal Footer */}
        <div className="pt-4 border-t border-sand-dark flex items-center justify-between text-xs text-ink-muted">
          <span>{trips.length} saved {trips.length === 1 ? 'itinerary' : 'itineraries'}</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-sand hover:bg-sand-dark text-ink font-bold text-xs transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
