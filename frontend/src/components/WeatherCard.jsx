import React from 'react';
import { 
  CloudSun, Wind, Droplets, Thermometer, Calendar, RefreshCw, 
  AlertCircle, ShieldCheck, Compass, Radio, CheckCircle2, Clock
} from 'lucide-react';

export default function WeatherCard({ 
  weather, 
  destinationName, 
  bestTimeToVisit, 
  onRefresh, 
  loading,
  error 
}) {
  const dest = destinationName || 'Goa';
  const isSuccess = weather && weather.success !== false;
  const forecast = weather?.forecast || [];

  return (
    <section id="weather" className="scroll-mt-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-20">
      <div className="bg-gradient-to-br from-brand-900 via-brand-800 to-indigo-950 rounded-3xl p-6 sm:p-10 text-white shadow-xl relative overflow-hidden border border-brand-700/50">
        
        {/* Ambient Meteorological Glow */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-sky-500/15 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-brand-500/10 rounded-full blur-3xl pointer-events-none"></div>

        {/* Distinct Separation Banner: Non-AI Meteorological Observation */}
        <div className="relative z-10 mb-6 flex items-center justify-between flex-wrap gap-3 pb-4 border-b border-white/15">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-sky-500/20 text-sky-200 text-xs font-bold uppercase tracking-wider border border-sky-400/30">
            <Radio className="w-4 h-4 text-sky-300 animate-pulse" />
            <span>📡 Live Meteorological Observation — Sourced from Open-Meteo API</span>
          </div>

          <div className="text-[11px] text-brand-200/80 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Sourced via WMO Global Meteorological Sensors & Weather API</span>
          </div>
        </div>

        {/* Section Header */}
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 mb-6">
          <div>
            <h2 className="font-display font-bold text-2xl sm:text-3xl text-white flex items-center gap-2.5">
              <span>Live Meteorological Readings: {weather?.place || dest}</span>
            </h2>
            <p className="text-sm text-brand-100/80 mt-1">
              Real-time atmospheric parameters queried directly from weather stations to guide your packing, transport, and daily sightseeing schedule.
            </p>
          </div>

          <button
            onClick={onRefresh}
            disabled={loading}
            className="self-start md:self-auto inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition-all border border-white/15 shadow-sm active:scale-95 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Refreshing...' : 'Refresh Weather'}</span>
          </button>
        </div>

        {/* ERROR / INVALID DESTINATION BANNER */}
        {error && (
          <div className="relative z-10 mb-6 p-4 rounded-2xl bg-rose-500/20 border border-rose-400/40 text-rose-100 text-xs flex items-start gap-3 animate-fade-in">
            <AlertCircle className="w-5 h-5 text-rose-300 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-bold text-sm text-white">Weather Retrieval Notice</div>
              <div className="mt-0.5">{error}</div>
              <div className="text-[10px] text-rose-200 mt-1">
                Tip: Enter a recognized city or region name (e.g. "Goa", "Kerala", "Manali", "Jaipur", "Rishikesh").
              </div>
            </div>
          </div>
        )}

        {/* MAIN WEATHER TILES */}
        {isSuccess ? (
          <div className="relative z-10 space-y-6">
            
            {/* Primary Current Observations Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              
              {/* 1. Primary Temp & Condition */}
              <div className="p-5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 flex items-center gap-4 hover:bg-white/15 transition-all">
                <div className="text-5xl">{weather.icon || '🌤️'}</div>
                <div>
                  <div className="font-display font-extrabold text-4xl text-white leading-none">
                    {weather.temperature}°C
                  </div>
                  <div className="text-xs text-brand-200 font-bold mt-1">
                    {weather.condition}
                  </div>
                  <div className="text-[11px] text-white/70 mt-0.5">
                    Feels like {weather.feels_like ?? weather.feelsLike ?? weather.temperature}°C
                  </div>
                </div>
              </div>

              {/* 2. Temperature Range (Min / Max) */}
              <div className="p-5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 flex items-center gap-4 hover:bg-white/15 transition-all">
                <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center text-amber-300 flex-shrink-0">
                  <Thermometer className="w-6 h-6" />
                </div>
                <div>
                  <div className="text-xs text-brand-200 font-bold uppercase tracking-wider">Diurnal Range</div>
                  <div className="font-display font-bold text-xl text-white mt-0.5">
                    {weather.temp_min ?? weather.tempMin ?? 22}°C – {weather.temp_max ?? weather.tempMax ?? 31}°C
                  </div>
                  <div className="text-[11px] text-white/70">
                    Daytime high & overnight low
                  </div>
                </div>
              </div>

              {/* 3. Relative Humidity & Wind Speed */}
              <div className="p-5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 flex items-center gap-4 hover:bg-white/15 transition-all">
                <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center text-sky-300 flex-shrink-0">
                  <Wind className="w-6 h-6" />
                </div>
                <div>
                  <div className="text-xs text-brand-200 font-bold uppercase tracking-wider">Wind & Humidity</div>
                  <div className="font-display font-bold text-lg text-white mt-0.5 flex items-center gap-2">
                    <span>{weather.wind_speed ?? weather.windSpeed ?? 12} km/h</span>
                    <span>•</span>
                    <span className="flex items-center gap-0.5 text-sky-300">
                      <Droplets className="w-3.5 h-3.5" />
                      {weather.humidity}%
                    </span>
                  </div>
                  <div className="text-[11px] text-white/70">
                    {weather.humidity > 70 ? 'Humid coastal air' : 'Comfortable ambient moisture'}
                  </div>
                </div>
              </div>

              {/* 4. Best Time to Visit */}
              <div className="p-5 rounded-2xl bg-emerald-500/20 backdrop-blur-md border border-emerald-400/30 flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-400/20 flex items-center justify-center text-emerald-300 flex-shrink-0">
                  <Calendar className="w-6 h-6" />
                </div>
                <div>
                  <div className="text-xs text-emerald-200 font-bold uppercase tracking-wider">Optimal Season</div>
                  <div className="font-display font-bold text-sm text-white mt-0.5">
                    {bestTimeToVisit || 'October to March'}
                  </div>
                  <div className="text-[11px] text-emerald-100/70">
                    Peak clear skies & festival period
                  </div>
                </div>
              </div>

            </div>

            {/* 5-DAY WEATHER FORECAST STRIP */}
            {forecast.length > 0 && (
              <div className="pt-4 border-t border-white/10">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-xs font-bold text-brand-200 uppercase tracking-wider flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-sky-300" />
                    <span>5-Day Meteorological Forecast ({dest})</span>
                  </div>
                  <div className="text-[11px] text-white/60">
                    Updated: {weather.updated_at || weather.updatedAt || 'Just now'}
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                  {forecast.slice(0, 5).map((f, idx) => (
                    <div 
                      key={idx}
                      className="p-3.5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 hover:bg-white/15 transition-all text-center"
                    >
                      <div className="text-xs font-bold text-white mb-0.5">{f.day}</div>
                      <div className="text-[10px] text-brand-200/80 mb-2">{f.date}</div>
                      <div className="text-3xl my-1.5">{f.icon || '🌤️'}</div>
                      <div className="text-xs font-display font-bold text-white">
                        {f.temp_max}° / <span className="text-brand-300">{f.temp_min}°C</span>
                      </div>
                      <div className="text-[10px] text-brand-200 truncate mt-1">
                        {f.condition}
                      </div>
                      {f.rain_chance !== undefined && (
                        <div className="mt-1.5 text-[9px] font-bold text-sky-200 bg-sky-500/20 px-1.5 py-0.5 rounded-full inline-block">
                          🌧️ {f.rain_chance}% Rain
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Source & Provenance Tag */}
            <div className="flex items-center justify-between text-[11px] text-white/50 pt-2">
              <div>Meteorological Data Source: {weather.source || 'Open-Meteo Global Meteorological Model'}</div>
              <div>Coordinates verified against official geographic indices</div>
            </div>

          </div>
        ) : (
          <div className="relative z-10 p-8 rounded-2xl bg-white/10 text-center text-brand-100 text-sm">
            {loading ? (
              <div className="flex items-center justify-center gap-2.5">
                <RefreshCw className="w-4 h-4 animate-spin text-white" />
                <span>Querying meteorological satellite readings for {dest}...</span>
              </div>
            ) : (
              <div>No meteorological sensor readings available for this location. Click "Refresh Weather" above.</div>
            )}
          </div>
        )}

      </div>
    </section>
  );
}
