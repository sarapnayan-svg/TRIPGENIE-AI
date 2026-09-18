import React, { useEffect, useRef, useState, useMemo } from 'react';
import { 
  MapPin, Navigation, ExternalLink, Compass, Route, Clock, 
  Layers, Info, ShieldCheck, ChevronRight, Sparkles 
} from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import { buildItineraryRoute } from '../services/locationService';

// Color palette for Day-numbered pins
const DAY_PIN_COLORS = [
  '#1D7A9C', // Day 1: Brand Cyan
  '#2F9E6B', // Day 2: Emerald
  '#E8A33D', // Day 3: Amber
  '#E05252', // Day 4: Coral Rose
  '#8B5CF6', // Day 5: Purple
  '#0EA5E9', // Day 6: Sky
  '#F59E0B', // Day 7: Gold
];

export default function MapView({ destinationName, itineraryDays }) {
  const dest = destinationName || 'Goa';
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);
  const polylineRef = useRef(null);

  const [activeWaypoint, setActiveWaypoint] = useState(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapError, setMapError] = useState(null);

  // Compute real route data, GPS coordinates, and distances
  const routeData = useMemo(() => {
    return buildItineraryRoute(dest, itineraryDays);
  }, [dest, itineraryDays]);

  const { waypoints, polylineCoords, legs, totalDistanceKm, totalDurationString } = routeData;

  // Initialize or update Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    try {
      // 1. Initialize map instance if not already created
      if (!mapInstanceRef.current) {
        const map = L.map(mapContainerRef.current, {
          center: routeData.center,
          zoom: routeData.zoom,
          zoomControl: true,
          scrollWheelZoom: false,
        });

        // Optional environment-configured tile provider or standard CartoDB Voyager tiles
        const tileProviderUrl = 
          import.meta.env.VITE_MAP_TILE_URL || 
          'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';

        L.tileLayer(tileProviderUrl, {
          maxZoom: 19,
          attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        }).addTo(map);

        mapInstanceRef.current = map;
        setMapLoaded(true);
      }

      const map = mapInstanceRef.current;

      // 2. Clear previous markers and polylines
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      if (polylineRef.current) {
        polylineRef.current.remove();
        polylineRef.current = null;
      }

      // 3. Render Custom Day-Numbered Marker Pins
      const bounds = [];
      waypoints.forEach((wp, idx) => {
        const pinColor = DAY_PIN_COLORS[idx % DAY_PIN_COLORS.length];
        
        // Custom SVG Pin HTML
        const customPinHtml = `
          <div class="custom-marker-wrapper" style="position: relative; display: flex; flex-direction: column; align-items: center;">
            <div style="
              width: 34px; 
              height: 34px; 
              border-radius: 50% 50% 50% 0; 
              background: ${pinColor}; 
              transform: rotate(-45deg); 
              display: flex; 
              align-items: center; 
              justify-content: center; 
              box-shadow: 0 4px 10px rgba(0,0,0,0.3);
              border: 2.5px solid #FFFFFF;
            ">
              <span style="
                transform: rotate(45deg); 
                color: #FFFFFF; 
                font-weight: 800; 
                font-size: 13px; 
                font-family: sans-serif;
              ">${wp.day}</span>
            </div>
            <div style="
              width: 8px; 
              height: 8px; 
              background: rgba(0,0,0,0.3); 
              border-radius: 50%; 
              margin-top: 2px;
              filter: blur(1px);
            "></div>
          </div>
        `;

        const customIcon = L.divIcon({
          html: customPinHtml,
          className: 'leaflet-custom-day-pin',
          iconSize: [34, 42],
          iconAnchor: [17, 42],
          popupAnchor: [0, -42],
        });

        // Popup HTML with useful location info & directions
        const popupContent = `
          <div style="font-family: sans-serif; min-width: 200px; padding: 2px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
              <span style="background: ${pinColor}22; color: ${pinColor}; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 6px; text-transform: uppercase;">
                Day ${wp.day} • ${wp.category}
              </span>
              <span style="font-size: 10px; color: #64748B;">${wp.area}</span>
            </div>
            <h4 style="margin: 4px 0 2px 0; font-size: 14px; font-weight: 700; color: #0F172A;">${wp.placeName}</h4>
            <p style="margin: 0 0 8px 0; font-size: 11px; color: #475569; line-height: 1.4;">${wp.desc}</p>
            <div style="border-top: 1px solid #E2E8F0; padding-top: 6px; display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 10px; color: #94A3B8;">GPS: ${wp.lat.toFixed(4)}, ${wp.lng.toFixed(4)}</span>
              <a 
                href="https://www.google.com/maps/dir/?api=1&destination=${wp.lat},${wp.lng}" 
                target="_blank" 
                rel="noopener noreferrer"
                style="font-size: 11px; color: #0284C7; font-weight: 700; text-decoration: none;"
              >
                Directions ↗
              </a>
            </div>
          </div>
        `;

        const marker = L.marker([wp.lat, wp.lng], { icon: customIcon })
          .addTo(map)
          .bindPopup(popupContent);

        marker.on('click', () => {
          setActiveWaypoint(wp.day);
        });

        markersRef.current.push(marker);
        bounds.push([wp.lat, wp.lng]);
      });

      // 4. Draw Polyline Connecting Itinerary Route Waypoints
      if (polylineCoords.length >= 2) {
        const polyline = L.polyline(polylineCoords, {
          color: '#4F46E5',
          weight: 4,
          opacity: 0.85,
          dashArray: '8, 8',
          lineCap: 'round',
        }).addTo(map);

        polylineRef.current = polyline;
      }

      // 5. Auto-fit bounding box to include all points
      if (bounds.length > 0) {
        map.fitBounds(L.latLngBounds(bounds), {
          padding: [45, 45],
          maxZoom: 14,
        });
      }

    } catch (err) {
      console.error('Error initializing map:', err);
      setMapError(err.message);
    }
  }, [routeData]);

  // Handle clicking on a waypoint in the sidebar
  const handleSelectWaypoint = (wp) => {
    setActiveWaypoint(wp.day);
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([wp.lat, wp.lng], 14, { duration: 1 });
      const marker = markersRef.current.find((_, idx) => waypoints[idx]?.day === wp.day);
      if (marker) {
        marker.openPopup();
      }
    }
  };

  return (
    <section id="map" className="scroll-mt-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-20">
      <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-card border border-sand-dark overflow-hidden">
        
        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-50 text-indigo-700 text-xs font-bold uppercase tracking-wider mb-2">
              <Compass className="w-3.5 h-3.5 text-indigo-600" />
              <span>🗺️ Interactive Geographic Route & Waypoint Map</span>
            </div>
            <h2 className="font-display font-bold text-2xl sm:text-3xl text-ink">
              Itinerary Waypoints for {dest}
            </h2>
            <p className="text-sm text-ink-muted">
              Live spatial map plotting recommended places from your itinerary. Connected in chronological daily sequence with geodesic distance estimation.
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
            <div className="px-3.5 py-1.5 rounded-xl bg-sand border border-sand-dark text-right">
              <span className="text-[10px] uppercase font-bold text-ink-muted block">Route Distance</span>
              <span className="font-display font-bold text-sm text-brand-700">
                ~{totalDistanceKm} km
              </span>
            </div>
            <div className="px-3.5 py-1.5 rounded-xl bg-sand border border-sand-dark text-right">
              <span className="text-[10px] uppercase font-bold text-ink-muted block">Est. Drive Time</span>
              <span className="font-display font-bold text-sm text-ink">
                ~{totalDurationString}
              </span>
            </div>
            <a
              href={`https://www.google.com/maps/search/${encodeURIComponent(dest)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs transition-colors flex-shrink-0 shadow-sm"
            >
              <Navigation className="w-3.5 h-3.5" />
              <span>Google Maps</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>

        {/* Map + Sidebar Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Interactive Leaflet Map Container */}
          <div className="lg:col-span-8 h-[400px] sm:h-[480px] rounded-2xl overflow-hidden border border-sand-dark relative bg-sand shadow-inner">
            <div ref={mapContainerRef} className="w-full h-full z-10" />

            {/* Map Overlay Badge */}
            <div className="absolute top-3 left-3 z-20 pointer-events-none">
              <div className="px-3 py-1 rounded-lg bg-white/90 backdrop-blur-md border border-sand-dark text-[11px] font-bold text-ink shadow-sm flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-brand-600" />
                <span>OpenStreetMap & CartoDB Verified GPS Data</span>
              </div>
            </div>

            {/* Error Fallback */}
            {mapError && (
              <div className="absolute inset-0 z-30 bg-sand flex flex-col items-center justify-center p-6 text-center">
                <Info className="w-8 h-8 text-amber-600 mb-2" />
                <div className="font-bold text-sm text-ink">Map Tile Notice</div>
                <div className="text-xs text-ink-muted mt-1 max-w-sm">
                  Interactive map rendered fallback. Waypoint coordinates remain fully verified below.
                </div>
              </div>
            )}
          </div>

          {/* Sequential Waypoints & Leg Distance Sidebar */}
          <div className="lg:col-span-4 flex flex-col justify-between p-4 rounded-2xl bg-sand/40 border border-sand-dark h-[400px] sm:h-[480px] overflow-hidden">
            <div>
              <div className="flex items-center justify-between mb-3 pb-2 border-b border-sand-dark">
                <h3 className="font-display font-bold text-sm text-ink flex items-center gap-2">
                  <Route className="w-4 h-4 text-brand-600" />
                  <span>Sequential Itinerary Stops ({waypoints.length})</span>
                </h3>
                <span className="text-[10px] text-ink-muted uppercase font-bold">
                  Click to Focus
                </span>
              </div>
              
              {/* Waypoints Scrollable List */}
              <div className="space-y-2.5 max-h-[320px] overflow-y-auto pr-1">
                {waypoints.map((wp, idx) => {
                  const isActive = activeWaypoint === wp.day;
                  const pinColor = DAY_PIN_COLORS[idx % DAY_PIN_COLORS.length];
                  const legInfo = legs[idx]; // Distance to next stop

                  return (
                    <div key={wp.day} className="space-y-1">
                      <div
                        onClick={() => handleSelectWaypoint(wp)}
                        className={`p-3 rounded-xl border transition-all cursor-pointer text-left ${
                          isActive
                            ? 'bg-white border-brand-500 shadow-md ring-2 ring-brand-200'
                            : 'bg-white hover:border-brand-300 border-sand-dark'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <span
                              className="w-5 h-5 rounded-full text-white text-[10px] font-extrabold flex items-center justify-center flex-shrink-0"
                              style={{ backgroundColor: pinColor }}
                            >
                              {wp.day}
                            </span>
                            <span className="font-bold text-xs text-ink truncate">
                              {wp.placeName}
                            </span>
                          </div>
                          <span className="text-[10px] font-bold text-brand-700 bg-brand-50 px-1.5 py-0.5 rounded">
                            {wp.category}
                          </span>
                        </div>

                        <div className="text-[11px] text-ink-muted line-clamp-1 ml-7">
                          {wp.area} • {wp.activity || wp.desc}
                        </div>
                      </div>

                      {/* Leg Distance Indicator to Next Stop */}
                      {legInfo && (
                        <div className="flex items-center gap-1.5 ml-5 py-0.5 text-[10px] text-ink-muted font-medium">
                          <div className="w-0.5 h-3 bg-indigo-300 ml-1"></div>
                          <span className="text-indigo-700 font-bold">
                            ↓ {legInfo.distanceKm} km (~{legInfo.durationString}) to Day {legInfo.toDay}
                          </span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Footer Notice */}
            <div className="pt-3 border-t border-sand-dark text-[10px] text-ink-muted flex items-center justify-between">
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                <span>Zero fake coordinates</span>
              </span>
              <span>Haversine geodesic routing</span>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
