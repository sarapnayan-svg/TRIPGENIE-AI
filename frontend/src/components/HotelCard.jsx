import React from 'react';
import { Star, MapPin, Check, ExternalLink, ShieldCheck, Compass, Sparkles } from 'lucide-react';

export default function HotelCard({ hotel, destinationName }) {
  if (!hotel) return null;

  const tierColors = {
    hostel: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    budget: 'bg-sky-50 text-sky-700 border-sky-200',
    standard: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    premium: 'bg-purple-50 text-purple-700 border-purple-200',
    luxury: 'bg-amber-50 text-amber-800 border-amber-300',
  };

  const tierLabels = {
    hostel: '🎒 Social Hostel',
    budget: '🏷️ Budget Friendly',
    standard: '⭐ 3★ Comfort',
    premium: '✨ 4★ Boutique',
    luxury: '👑 5★ Luxury',
  };

  const hotelTier = (hotel.tier || 'standard').toLowerCase();
  const tierBadgeClass = tierColors[hotelTier] || tierColors.standard;
  const tierLabel = tierLabels[hotelTier] || hotel.tier;

  const pricePerNight = hotel.price_per_night || hotel.pricePerNight || 0;
  const totalStay = hotel.total_stay_estimated;
  const roomsNeeded = hotel.rooms_needed || 1;
  const nights = hotel.nights || 1;
  const proximityNote = hotel.proximity_note || (hotel.distance_to_itinerary_km ? `${hotel.distance_to_itinerary_km} km from ${hotel.closest_itinerary_place}` : null);

  const bookingLink = hotel.booking_url || `https://www.google.com/travel/hotels/${encodeURIComponent((hotel.name || '') + ' ' + (destinationName || ''))}`;

  return (
    <div className="group bg-white rounded-3xl overflow-hidden border border-sand-dark shadow-sm hover:shadow-card-hover transition-all duration-300 flex flex-col relative">
      {/* Top Image Section */}
      <div className="relative h-52 overflow-hidden bg-sand-dark">
        <img
          src={hotel.image_url || hotel.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80'}
          alt={hotel.name || 'Hotel property'}
          onError={(e) => {
            e.currentTarget.onerror = null;
            e.currentTarget.src = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80';
          }}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />

        {/* Tier Badge */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5">
          <span className={`px-3 py-1 rounded-full text-xs font-bold shadow-sm border backdrop-blur-md bg-white/95 ${tierBadgeClass}`}>
            {tierLabel}
          </span>
          {hotel.is_verified_database_record && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-900/80 backdrop-blur-md text-emerald-300 border border-emerald-500/30 shadow-sm">
              <ShieldCheck className="w-3 h-3 text-emerald-400" />
              <span>Verified Rate</span>
            </span>
          )}
        </div>

        {/* Proximity / Location Flag */}
        {proximityNote && (
          <div className="absolute bottom-3 left-3 right-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-ink/80 backdrop-blur-md text-white text-xs font-semibold shadow-md max-w-full truncate">
              <Compass className="w-3.5 h-3.5 text-brand-400 flex-shrink-0 animate-pulse" />
              <span className="truncate">{proximityNote}</span>
            </div>
          </div>
        )}
      </div>

      {/* Hotel Content */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        <div>
          {/* Rating, Reviews & Star */}
          <div className="flex items-center justify-between gap-2 mb-2">
            <div className="flex items-center gap-1.5 bg-amber-50 px-2.5 py-1 rounded-lg border border-amber-200">
              <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
              <span className="text-xs font-extrabold text-ink">{hotel.rating?.toFixed(1) || '4.5'}</span>
              {hotel.reviews_count && (
                <span className="text-[11px] text-ink-muted">({hotel.reviews_count.toLocaleString()} reviews)</span>
              )}
            </div>

            {hotel.is_within_accommodation_budget && (
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                ✓ Within Target Budget
              </span>
            )}
          </div>

          {/* Hotel Name */}
          <h3 className="font-display font-bold text-lg text-ink line-clamp-1 group-hover:text-brand-600 transition-colors">
            {hotel.name}
          </h3>

          {/* Area / Address */}
          <div className="flex items-center gap-1 text-xs text-ink-muted mt-1 mb-3">
            <MapPin className="w-3.5 h-3.5 text-brand-500 flex-shrink-0" />
            <span className="truncate">{hotel.area || hotel.location || destinationName}</span>
          </div>

          {/* AI Curator Note / Verified Database Distinction */}
          {hotel.curator_note && (
            <div className="p-2.5 rounded-xl bg-sand/60 border border-sand-dark/60 text-xs text-ink-muted mb-3.5 leading-relaxed flex items-start gap-2">
              <Sparkles className="w-3.5 h-3.5 text-brand-500 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-ink text-[11px] block mb-0.5">Curator Insight:</span>
                <span className="italic">{hotel.curator_note}</span>
              </div>
            </div>
          )}

          {/* Amenities Chips */}
          <div className="flex flex-wrap gap-1.5 mb-4">
            {(hotel.amenities || []).slice(0, 4).map((amenity, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-sand text-[11px] font-medium text-ink-muted border border-sand-dark/40"
              >
                <Check className="w-3 h-3 text-brand-500" />
                {amenity}
              </span>
            ))}
            {(hotel.amenities || []).length > 4 && (
              <span className="px-2 py-1 rounded-lg bg-sand text-[10px] font-bold text-ink-muted">
                +{hotel.amenities.length - 4} more
              </span>
            )}
          </div>
        </div>

        {/* Pricing & Booking Footer */}
        <div className="pt-3.5 border-t border-sand-dark flex items-end justify-between gap-3">
          <div>
            <div className="flex items-baseline gap-1">
              <span className="font-display font-black text-xl text-ink">
                ₹{Math.round(pricePerNight).toLocaleString('en-IN')}
              </span>
              <span className="text-[11px] text-ink-muted font-medium">/ night</span>
            </div>
            {totalStay && (
              <div className="text-[10px] text-ink-muted font-medium">
                Est. ₹{Math.round(totalStay).toLocaleString('en-IN')} total ({nights}N • {roomsNeeded}R)
              </div>
            )}
          </div>

          <a
            href={bookingLink}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`View deal for ${hotel.name || 'hotel'} on external booking partner`}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white font-bold text-xs shadow-sm shadow-brand-500/20 hover:shadow-md transition-all duration-200 flex-shrink-0 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <span>View Deal</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
}
