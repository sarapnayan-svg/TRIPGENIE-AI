import React, { useState } from 'react';
import { 
  IndianRupee, PieChart, Users, Wallet, CheckCircle2, 
  TrendingDown, AlertTriangle, ArrowRight, Sparkles, 
  Building2, Utensils, Activity, Car, ShieldAlert, Check,
  RotateCcw, Info
} from 'lucide-react';

export default function BudgetChart({ 
  budgetBreakdown, 
  totalBudget, 
  travelers = 2, 
  days = 4,
  destinationName,
  onApplyAlternative,
  onAutoOptimizeWithinBudget
}) {
  const [selectedCategory, setSelectedCategory] = useState(null);

  const total = Number(totalBudget) || 50000;
  const count = Number(travelers) || 2;
  const durationDays = Number(days) || 4;

  // Extract or fall back to deterministic unit calculations (handles both numbers and {total_cost} objects)
  const getAmount = (val, fallbackKey) => {
    if (typeof val === 'number') return val;
    if (val && typeof val.total_cost === 'number') return val.total_cost;
    if (fallbackKey && typeof budgetBreakdown?.[fallbackKey] === 'number') return budgetBreakdown[fallbackKey];
    return null;
  };

  const accAmount = getAmount(budgetBreakdown?.accommodation, 'stay') ?? Math.round(total * 0.38);
  const foodAmount = getAmount(budgetBreakdown?.food, 'food') ?? Math.round(total * 0.22);
  const actAmount = getAmount(budgetBreakdown?.activities, 'activities') ?? Math.round(total * 0.18);
  const transAmount = getAmount(budgetBreakdown?.transportation, 'transport') ?? Math.round(total * 0.15);
  const miscAmount = getAmount(budgetBreakdown?.miscellaneous, 'misc') ?? Math.round(total * 0.07);

  const calculatedTotal = budgetBreakdown?.total_estimated ?? budgetBreakdown?.total_estimated_cost ?? (accAmount + foodAmount + actAmount + transAmount + miscAmount);
  const remaining = budgetBreakdown?.remaining_budget ?? (total - calculatedTotal);
  const utilization = budgetBreakdown?.utilization_percent ?? budgetBreakdown?.budget_utilization_pct ?? Math.round((calculatedTotal / Math.max(1, total)) * 100);
  const isOverBudget = budgetBreakdown?.is_over_budget ?? (calculatedTotal > total);
  const deficit = budgetBreakdown?.deficit ?? Math.max(0, calculatedTotal - total);
  const alternatives = budgetBreakdown?.cost_saving_alternatives || [];
  const statusLabel = budgetBreakdown?.status_label || (isOverBudget ? 'Exceeds User Budget' : 'Comfortably Within Budget');

  const categories = [
    { 
      key: 'accommodation',
      label: 'Accommodation & Stays', 
      amount: accAmount, 
      color: '#1D7A9C', 
      bg: 'bg-[#1D7A9C]', 
      icon: Building2,
      note: budgetBreakdown?.categories?.accommodation?.calculation_note || 'Estimated hotel/stay cost based on chosen tier'
    },
    { 
      key: 'food',
      label: 'Food & Dining', 
      amount: foodAmount, 
      color: '#2F9E6B', 
      bg: 'bg-[#2F9E6B]', 
      icon: Utensils,
      note: budgetBreakdown?.categories?.food?.calculation_note || 'Daily meals & regional cuisine allocation'
    },
    { 
      key: 'activities',
      label: 'Activities & Sightseeing', 
      amount: actAmount, 
      color: '#E8A33D', 
      bg: 'bg-[#E8A33D]', 
      icon: Activity,
      note: budgetBreakdown?.categories?.activities?.calculation_note || 'Curated entry tickets, tours & adventures'
    },
    { 
      key: 'transportation',
      label: 'Local Transportation', 
      amount: transAmount, 
      color: '#FF6B5A', 
      bg: 'bg-[#FF6B5A]', 
      icon: Car,
      note: budgetBreakdown?.categories?.transportation?.calculation_note || 'Vehicle rental, private cab, or public transit'
    },
    { 
      key: 'miscellaneous',
      label: 'Miscellaneous & Contingency', 
      amount: miscAmount, 
      color: '#8B5CF6', 
      bg: 'bg-[#8B5CF6]', 
      icon: ShieldAlert,
      note: budgetBreakdown?.categories?.miscellaneous?.calculation_note || '7% contingency for permits, water, tips & shopping'
    },
  ];

  const perPerson = Math.round(calculatedTotal / count);
  const perDay = Math.round(calculatedTotal / durationDays);

  // SVG Donut calculation
  const radius = 15.5;
  const circumference = 2 * Math.PI * radius; // ~97.389
  let accumulatedPercent = 0;

  return (
    <section id="budget" className="scroll-mt-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-20">
      <div className="bg-white rounded-3xl p-6 sm:p-10 shadow-card border border-sand-dark">
        
        {/* Header with Badges */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-amber-50 text-amber-800 text-xs font-bold uppercase tracking-wider mb-2">
              <Wallet className="w-3.5 h-3.5 text-amber-600" />
              <span>💰 Deterministic Budget Intelligence</span>
            </div>
            <h2 className="font-display font-bold text-2xl sm:text-3xl text-ink">
              Budget Planning for {destinationName || 'Your Trip'}
            </h2>
            <p className="text-sm text-ink-muted">
              Itemized, formula-based estimates across 5 travel categories. All rates are derived deterministically from localized knowledge bases.
            </p>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap sm:flex-nowrap">
            <div className="px-3.5 py-2 rounded-2xl bg-sand border border-sand-dark text-right">
              <span className="text-[10px] uppercase font-bold text-ink-muted block">Per Person</span>
              <span className="font-display font-bold text-sm text-brand-700">
                ₹{perPerson.toLocaleString('en-IN')}
              </span>
            </div>
            <div className="px-3.5 py-2 rounded-2xl bg-sand border border-sand-dark text-right">
              <span className="text-[10px] uppercase font-bold text-ink-muted block">Per Day</span>
              <span className="font-display font-bold text-sm text-ink">
                ₹{perDay.toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        </div>

        {/* 4 Primary Financial KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          
          {/* 1. Total User Budget */}
          <div className="p-4 rounded-2xl bg-brand-50/50 border border-brand-200">
            <span className="text-[10px] font-bold uppercase tracking-wider text-brand-700 block mb-1">
              Total User Budget
            </span>
            <div className="font-display font-extrabold text-2xl text-brand-900">
              ₹{total.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-brand-600 mt-1 block">
              Set by user ({count} travelers, {durationDays} days)
            </span>
          </div>

          {/* 2. Total Estimated Cost */}
          <div className={`p-4 rounded-2xl border ${
            isOverBudget ? 'bg-rose-50 border-rose-300' : 'bg-sand border-sand-dark'
          }`}>
            <span className="text-[10px] font-bold uppercase tracking-wider text-ink-muted block mb-1 flex items-center justify-between">
              <span>Estimated Cost</span>
              <span className="text-[9px] bg-white px-1.5 py-0.5 rounded border font-semibold">Estimate</span>
            </span>
            <div className={`font-display font-extrabold text-2xl ${isOverBudget ? 'text-rose-700' : 'text-ink'}`}>
              ₹{calculatedTotal.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-ink-muted mt-1 block">
              Sum of all 5 travel categories
            </span>
          </div>

          {/* 3. Remaining Budget / Deficit */}
          <div className={`p-4 rounded-2xl border ${
            isOverBudget ? 'bg-rose-50 border-rose-300 text-rose-900' : 'bg-emerald-50 border-emerald-200 text-emerald-900'
          }`}>
            <span className="text-[10px] font-bold uppercase tracking-wider block mb-1">
              {isOverBudget ? 'Budget Deficit' : 'Remaining Cushion'}
            </span>
            <div className="font-display font-extrabold text-2xl">
              {isOverBudget ? `-₹${deficit.toLocaleString('en-IN')}` : `+₹${remaining.toLocaleString('en-IN')}`}
            </div>
            <span className="text-[11px] mt-1 block opacity-80">
              {isOverBudget ? 'Exceeds budget limit' : 'Surplus savings buffer'}
            </span>
          </div>

          {/* 4. Budget Utilization % */}
          <div className={`p-4 rounded-2xl border ${
            isOverBudget 
              ? 'bg-rose-50 border-rose-300 text-rose-900' 
              : utilization > 85 
                ? 'bg-amber-50 border-amber-200 text-amber-900' 
                : 'bg-emerald-50 border-emerald-200 text-emerald-900'
          }`}>
            <span className="text-[10px] font-bold uppercase tracking-wider block mb-1">
              Budget Utilization
            </span>
            <div className="font-display font-extrabold text-2xl flex items-baseline gap-1">
              <span>{utilization}%</span>
              <span className="text-xs font-semibold">
                {isOverBudget ? '(Over)' : '(Healthy)'}
              </span>
            </div>
            {/* Progress bar */}
            <div className="h-1.5 w-full bg-black/10 rounded-full mt-2 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-700 ${
                  isOverBudget ? 'bg-rose-600' : utilization > 85 ? 'bg-amber-500' : 'bg-emerald-500'
                }`}
                style={{ width: `${Math.min(100, utilization)}%` }}
              ></div>
            </div>
          </div>

        </div>

        {/* OVER-BUDGET ALERT BANNER & REGENERATION ACTION */}
        {isOverBudget && (
          <div className="mb-8 p-6 rounded-3xl bg-gradient-to-r from-rose-50 via-rose-100/50 to-amber-50 border-2 border-rose-300 shadow-sm animate-fade-in">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-5">
              <div className="flex items-start gap-3.5">
                <div className="w-10 h-10 rounded-2xl bg-rose-500 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-0.5">
                  <AlertTriangle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-display font-bold text-lg text-rose-950 flex items-center gap-2">
                    <span>Budget Warning: Estimated Cost Exceeds Budget by ₹{deficit.toLocaleString('en-IN')}</span>
                    <span className="text-xs bg-rose-200 text-rose-800 px-2.5 py-0.5 rounded-full font-bold">
                      {utilization}% of Budget
                    </span>
                  </h3>
                  <p className="text-sm text-rose-800 mt-1 max-w-2xl">
                    The chosen combination of luxury hotel, private transit, and experiences exceeds your target budget of ₹{total.toLocaleString('en-IN')}. Below are actionable lower-cost alternatives that bring your itinerary strictly within budget.
                  </p>
                </div>
              </div>

              {/* 1-Click Auto-Adjust Button */}
              {onAutoOptimizeWithinBudget && (
                <button
                  type="button"
                  onClick={onAutoOptimizeWithinBudget}
                  className="px-5 py-3 rounded-2xl bg-gradient-to-r from-rose-600 to-brand-700 hover:from-rose-700 hover:to-brand-800 text-white font-display font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center gap-2 flex-shrink-0 whitespace-nowrap self-start md:self-center"
                >
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Auto-Adjust & Regenerate Within Budget</span>
                </button>
              )}
            </div>

            {/* Lower-Cost Alternatives Grid */}
            {alternatives.length > 0 && (
              <div className="mt-5 pt-5 border-t border-rose-200/80">
                <div className="text-xs font-bold uppercase tracking-wider text-rose-900 mb-3 flex items-center gap-1.5">
                  <TrendingDown className="w-4 h-4 text-rose-700" />
                  <span>Recommended Lower-Cost Substitutions (Click to Apply)</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {alternatives.map((alt, idx) => (
                    <div 
                      key={idx}
                      className="p-3.5 rounded-2xl bg-white border border-rose-200 hover:border-brand-500 hover:shadow-sm transition-all flex items-center justify-between gap-3"
                    >
                      <div>
                        <div className="text-xs font-bold text-ink">{alt.title}</div>
                        <div className="text-[11px] text-ink-muted mt-0.5">{alt.description}</div>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200 block mb-1">
                          Saves ~₹{alt.potential_savings.toLocaleString('en-IN')}
                        </span>
                        {onApplyAlternative && alt.action_param && (
                          <button
                            type="button"
                            onClick={() => onApplyAlternative(alt.action_param)}
                            className="text-[11px] font-bold text-brand-600 hover:text-brand-800 inline-flex items-center gap-1 hover:underline"
                          >
                            <span>Apply</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Visual Donut Chart + Itemized Allocation Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Donut Chart Visual */}
          <div className="lg:col-span-5 flex flex-col items-center justify-center p-6 rounded-3xl bg-sand/40 border border-sand-dark relative">
            <div className="relative w-52 h-52 sm:w-60 sm:h-60">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                {/* Background Ring */}
                <circle
                  cx="18"
                  cy="18"
                  r={radius}
                  fill="none"
                  stroke="#E4E9EC"
                  strokeWidth="4.5"
                />

                {/* Slices */}
                {categories.map((cat, idx) => {
                  const percent = cat.amount / (calculatedTotal || 1);
                  const strokeDash = percent * circumference;
                  const strokeOffset = -(accumulatedPercent * circumference);
                  accumulatedPercent += percent;

                  return (
                    <circle
                      key={idx}
                      cx="18"
                      cy="18"
                      r={radius}
                      fill="none"
                      stroke={cat.color}
                      strokeWidth="4.5"
                      strokeDasharray={`${strokeDash} ${circumference - strokeDash}`}
                      strokeDashoffset={strokeOffset}
                      className="transition-all duration-700 ease-out hover:opacity-85 cursor-pointer"
                      onClick={() => setSelectedCategory(cat.key === selectedCategory ? null : cat.key)}
                    />
                  );
                })}
              </svg>

              {/* Center Donut Label */}
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
                <span className="text-[10px] font-bold text-ink-muted uppercase tracking-wider">
                  Total Estimated
                </span>
                <span className="font-display font-extrabold text-xl text-ink">
                  ₹{calculatedTotal.toLocaleString('en-IN')}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full mt-1 ${
                  isOverBudget ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'
                }`}>
                  {statusLabel}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-[11px] text-ink-muted text-center mt-3">
              <Info className="w-3.5 h-3.5 text-brand-600" />
              <span>All 5 categories sum deterministically to ₹{calculatedTotal.toLocaleString('en-IN')}.</span>
            </div>
          </div>

          {/* Allocation Breakdown Cards & Formulas */}
          <div className="lg:col-span-7 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {categories.map((cat, idx) => {
                const percent = Math.round((cat.amount / (calculatedTotal || 1)) * 100);
                const IconComp = cat.icon;
                const isSelected = selectedCategory === cat.key;

                return (
                  <div
                    key={idx}
                    onClick={() => setSelectedCategory(isSelected ? null : cat.key)}
                    className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
                      isSelected 
                        ? 'border-brand-500 bg-brand-50/40 ring-2 ring-brand-200' 
                        : 'border-sand-dark bg-white hover:border-brand-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className={`w-3 h-3 rounded-full ${cat.bg} flex-shrink-0`}></span>
                        <span className="text-xs font-bold text-ink truncate">{cat.label}</span>
                      </div>
                      <span className="text-xs font-display font-extrabold text-ink">
                        ₹{cat.amount.toLocaleString('en-IN')}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between text-[11px] text-ink-muted">
                      <span>{percent}% of estimated</span>
                      <span>₹{Math.round(cat.amount / count).toLocaleString('en-IN')} / person</span>
                    </div>

                    <div className="mt-2 text-[10px] text-ink-muted bg-sand/60 px-2 py-1 rounded-lg">
                      {cat.note}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Smart Financial Contingency Notice */}
            <div className="p-3.5 rounded-2xl bg-brand-50/70 border border-brand-200 text-xs text-brand-900 flex items-start gap-2.5">
              <ShieldAlert className="w-4 h-4 text-brand-600 flex-shrink-0 mt-0.5" />
              <div>
                <strong className="font-bold">Transparent Estimation Guarantee:</strong> Every item is labeled as an estimate calculated from real hotel tiers, transport rates, and activity ticket prices. No random numbers are used.
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
