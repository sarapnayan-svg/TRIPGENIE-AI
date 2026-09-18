import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

/**
 * TripGenie AI — Professional PDF Itinerary Export Engine
 * Generates an elegant, multi-page vector PDF dossier strictly from active trip data.
 * ZERO hardcoded trip information.
 */

// Branded color palette (RGB)
const COLORS = {
  primary: [79, 70, 229],      // Indigo #4f46e5
  primaryDark: [30, 27, 75],   // Deep Indigo #1e1b4b
  secondary: [14, 165, 233],   // Sky #0ea5e9
  accent: [16, 185, 129],      // Emerald #10b981
  slateDark: [15, 23, 42],     // Slate 900 #0f172a
  slateText: [51, 65, 85],     // Slate 700 #334155
  slateMuted: [100, 116, 139], // Slate 500 #64748b
  lightBg: [248, 250, 252],    // Slate 50 #f8fafc
  border: [226, 232, 240],     // Slate 200 #e2e8f0
  white: [255, 255, 255],
  warning: [245, 158, 11],     // Amber #f59e0b
  danger: [225, 29, 72],       // Rose #e11d48
};

/**
 * Format numerical amounts using Indian currency notation (lakhs/thousands formatting)
 * @param {number|string} val
 * @returns {string} e.g. "₹1,00,000"
 */
export function formatINR(val) {
  if (val === undefined || val === null || isNaN(Number(val))) return '₹0';
  return `₹${Math.round(Number(val)).toLocaleString('en-IN')}`;
}

/**
 * Generate and download a client-side vector PDF from active TripGenie plan data
 * @param {Object} params
 * @param {Object} params.tripPlan - Currently active trip plan object
 * @param {Object} [params.formData] - Active form configuration data
 * @param {Object} [params.destinationData] - Destination metadata
 * @param {Array} [params.hotels] - Recommended hotels list
 * @returns {{ success: boolean, filename: string, totalPages: number, doc: jsPDF }}
 */
export function generateTripPDF({ tripPlan, formData = {}, destinationData = {}, hotels = [] }) {
  if (!tripPlan) {
    throw new Error('No active trip plan available to generate PDF.');
  }

  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 14;
  const contentWidth = pageWidth - margin * 2;
  let cursorY = margin;

  // Helper: check space and add page if needed
  const ensureSpace = (neededHeight) => {
    if (cursorY + neededHeight > pageHeight - 16) {
      doc.addPage();
      cursorY = margin + 4;
      return true;
    }
    return false;
  };

  // Helper: section header with accent bar
  const drawSectionHeader = (title, iconText = '') => {
    ensureSpace(16);
    cursorY += 4;
    doc.setFillColor(...COLORS.primary);
    doc.roundedRect(margin, cursorY, 3.5, 7, 1, 1, 'F');

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(12);
    doc.setTextColor(...COLORS.slateDark);
    doc.text(`${iconText ? iconText + ' ' : ''}${title}`, margin + 6, cursorY + 5.5);

    cursorY += 10;
  };

  // -------------------------------------------------------------
  // Extract Dynamic Active Data (ZERO hardcoded fallback values)
  // -------------------------------------------------------------
  const destName = (tripPlan.destination || formData.destination || '').trim();
  const durationDays = tripPlan.days?.length || formData.days || tripPlan.days_count || 0;
  const travelersCount = formData.travelers || tripPlan.travelers || tripPlan.travelers_count || 0;
  const targetBudget = tripPlan.budget_breakdown?.user_budget || formData.budget || tripPlan.budget || 0;
  const travelStyle = formData.travelStyle || tripPlan.travel_style || '';

  // -------------------------------------------------------------
  // 1. BRAND HEADER & COVER BANNER
  // -------------------------------------------------------------
  const headerHeight = 36;
  doc.setFillColor(...COLORS.primaryDark);
  doc.rect(0, 0, pageWidth, headerHeight, 'F');

  // Decorative accent line
  doc.setFillColor(...COLORS.primary);
  doc.rect(0, headerHeight - 1.5, pageWidth, 1.5, 'F');

  // Logo / Title
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(22);
  doc.setTextColor(...COLORS.white);
  doc.text('TRIPGENIE AI', margin, 16);

  // Subtitle
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9.5);
  doc.setTextColor(203, 213, 225); // Slate 300
  doc.text('Intelligent Personalized Travel Itinerary & Tour Dossier', margin, 23);

  // Destination Pill Badge (only if destination exists)
  if (destName) {
    const destBadgeText = destName.toUpperCase();
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    const pillWidth = doc.getTextWidth(destBadgeText) + 16;
    const pillX = pageWidth - margin - pillWidth;

    doc.setFillColor(...COLORS.primary);
    doc.roundedRect(pillX, 10, pillWidth, 9, 3, 3, 'F');
    doc.setTextColor(...COLORS.white);
    doc.text(destBadgeText, pillX + 8, 16);
  }

  // RAG Tagline
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(7.5);
  doc.setTextColor(148, 163, 184);
  doc.text('RAG-Grounded AI Travel Planner', pageWidth - margin - 52, 26);

  cursorY = headerHeight + 6;

  // -------------------------------------------------------------
  // 2. TRIP ESSENTIALS METADATA STRIP
  // -------------------------------------------------------------
  const metaItems = [
    { label: 'DESTINATION', val: destName || 'Not specified' },
    { label: 'DURATION', val: durationDays > 0 ? `${durationDays} Days / ${Math.max(1, durationDays - 1)} Nights` : 'Not specified' },
    { label: 'TRAVELERS', val: travelersCount > 0 ? `${travelersCount} Person(s)` : 'Not specified' },
    { label: 'TARGET BUDGET', val: targetBudget > 0 ? formatINR(targetBudget) : 'Not specified' },
  ];
  if (travelStyle) {
    metaItems.push({ label: 'TRAVEL STYLE', val: String(travelStyle).toUpperCase() });
  }

  const colWidth = contentWidth / metaItems.length;
  doc.setFillColor(...COLORS.lightBg);
  doc.setDrawColor(...COLORS.border);
  doc.roundedRect(margin, cursorY, contentWidth, 16, 2, 2, 'FD');

  metaItems.forEach((item, idx) => {
    const x = margin + idx * colWidth;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(6.5);
    doc.setTextColor(...COLORS.slateMuted);
    doc.text(item.label, x + 4, cursorY + 5.5);

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8.5);
    doc.setTextColor(...COLORS.slateDark);
    doc.text(item.val, x + 4, cursorY + 11.5);

    if (idx < metaItems.length - 1) {
      doc.setDrawColor(...COLORS.border);
      doc.line(x + colWidth, cursorY + 2, x + colWidth, cursorY + 14);
    }
  });

  cursorY += 21;

  // -------------------------------------------------------------
  // 3. EXECUTIVE TRIP SUMMARY
  // -------------------------------------------------------------
  if (tripPlan.summary && tripPlan.summary.trim()) {
    drawSectionHeader('Trip Overview & Highlights');

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(...COLORS.slateText);

    const splitSummary = doc.splitTextToSize(tripPlan.summary.trim(), contentWidth - 8);
    const boxHeight = splitSummary.length * 4.4 + 6;
    ensureSpace(boxHeight);

    doc.setFillColor(248, 250, 252);
    doc.setDrawColor(226, 232, 240);
    doc.roundedRect(margin, cursorY, contentWidth, boxHeight, 2, 2, 'FD');

    doc.text(splitSummary, margin + 4, cursorY + 5.5);
    cursorY += boxHeight + 4;
  }

  // -------------------------------------------------------------
  // 4. FINANCIAL BUDGET BREAKDOWN
  // -------------------------------------------------------------
  const bb = tripPlan.budget_breakdown;
  if (bb) {
    drawSectionHeader('Financial Budget Breakdown (Deterministic Analysis)');

    const getVal = (field, fallbackKey) => {
      if (typeof field === 'number') return field;
      if (field && typeof field.total_cost === 'number') return field.total_cost;
      if (fallbackKey && typeof bb[fallbackKey] === 'number') return bb[fallbackKey];
      return 0;
    };

    const accomVal = getVal(bb.accommodation, 'stay');
    const foodVal = getVal(bb.food, 'food');
    const actVal = getVal(bb.activities, 'activities');
    const transVal = getVal(bb.transportation, 'transport');
    const miscVal = getVal(bb.miscellaneous, 'misc');
    const totalEst = bb.total_estimated || bb.total_estimated_cost || (accomVal + foodVal + actVal + transVal + miscVal);
    const userBud = bb.user_budget || targetBudget || totalEst;
    const remBud = bb.remaining_budget !== undefined ? bb.remaining_budget : (userBud - totalEst);
    const utilPct = bb.utilization_percent || bb.budget_utilization_pct || (userBud > 0 ? (totalEst / userBud) * 100 : 100);

    const budgetTableData = [
      ['Accommodation (Stays & Rooms)', formatINR(accomVal), `${((accomVal / (totalEst || 1)) * 100).toFixed(1)}%`],
      ['Food & Regional Dining', formatINR(foodVal), `${((foodVal / (totalEst || 1)) * 100).toFixed(1)}%`],
      ['Sightseeing & Curated Activities', formatINR(actVal), `${((actVal / (totalEst || 1)) * 100).toFixed(1)}%`],
      ['Local & Intercity Transportation', formatINR(transVal), `${((transVal / (totalEst || 1)) * 100).toFixed(1)}%`],
      ['Contingency Reserve & Miscellaneous', formatINR(miscVal), `${((miscVal / (totalEst || 1)) * 100).toFixed(1)}%`],
    ];

    autoTable(doc, {
      startY: cursorY,
      margin: { left: margin, right: margin },
      head: [['Expense Category', 'Estimated Allocation', '% of Total']],
      body: budgetTableData,
      theme: 'striped',
      headStyles: {
        fillColor: COLORS.primaryDark,
        textColor: COLORS.white,
        fontStyle: 'bold',
        fontSize: 8.5,
        cellPadding: 2.5,
      },
      bodyStyles: {
        fontSize: 8,
        textColor: COLORS.slateDark,
        cellPadding: 2.2,
      },
      columnStyles: {
        0: { cellWidth: 92 },
        1: { cellWidth: 52, fontStyle: 'bold', halign: 'right' },
        2: { cellWidth: 38, halign: 'right', textColor: COLORS.slateMuted },
      },
      styles: { overflow: 'linebreak' },
    });

    cursorY = doc.lastAutoTable.finalY + 3;

    // KPI Summary Bar
    ensureSpace(14);
    const kpiWidth = contentWidth / 4;
    doc.setFillColor(...COLORS.lightBg);
    doc.setDrawColor(...COLORS.border);
    doc.roundedRect(margin, cursorY, contentWidth, 11, 2, 2, 'FD');

    const kpis = [
      { l: 'TOTAL ESTIMATED', v: formatINR(totalEst), c: COLORS.primary },
      { l: 'ALLOCATED BUDGET', v: formatINR(userBud), c: COLORS.slateDark },
      { l: remBud >= 0 ? 'REMAINING CUSHION' : 'BUDGET DEFICIT', v: formatINR(remBud), c: remBud >= 0 ? COLORS.accent : COLORS.danger },
      { l: 'BUDGET UTILIZATION', v: `${utilPct.toFixed(1)}%`, c: utilPct <= 100 ? COLORS.accent : COLORS.danger },
    ];

    kpis.forEach((kpi, idx) => {
      const kx = margin + idx * kpiWidth;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(6);
      doc.setTextColor(...COLORS.slateMuted);
      doc.text(kpi.l, kx + 3, cursorY + 4);

      doc.setFont('helvetica', 'bold');
      doc.setFontSize(8.5);
      doc.setTextColor(...kpi.c);
      doc.text(kpi.v, kx + 3, cursorY + 8.5);

      if (idx < 3) {
        doc.setDrawColor(...COLORS.border);
        doc.line(kx + kpiWidth, cursorY + 2, kx + kpiWidth, cursorY + 9);
      }
    });

    cursorY += 15;
  }

  // -------------------------------------------------------------
  // 5. DAY-BY-DAY DETAILED ITINERARY TIMELINE
  // -------------------------------------------------------------
  const days = Array.isArray(tripPlan.days) ? tripPlan.days : [];
  if (days.length > 0) {
    drawSectionHeader('Day-by-Day Comprehensive Itinerary');

    days.forEach((dayObj, dIdx) => {
      ensureSpace(34);

      const dayTitle = dayObj.title || `Day ${dayObj.day || dIdx + 1}`;
      const dayCostText = dayObj.estimated_cost ? formatINR(dayObj.estimated_cost) : '';

      // Day Title Header Bar
      doc.setFillColor(...COLORS.primary);
      doc.roundedRect(margin, cursorY, contentWidth, 7, 1.5, 1.5, 'F');

      doc.setFont('helvetica', 'bold');
      doc.setFontSize(9);
      doc.setTextColor(...COLORS.white);
      doc.text(`DAY ${dayObj.day || dIdx + 1}:  ${dayTitle}`, margin + 3, cursorY + 4.8);

      if (dayCostText) {
        doc.setFontSize(8);
        const costStr = `Est: ${dayCostText}`;
        doc.text(costStr, pageWidth - margin - doc.getTextWidth(costStr) - 3, cursorY + 4.8);
      }

      cursorY += 9;

      // Day Narrative Description
      if (dayObj.description) {
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8.5);
        doc.setTextColor(...COLORS.slateDark);
        const splitDesc = doc.splitTextToSize(dayObj.description, contentWidth - 4);
        ensureSpace(splitDesc.length * 4);
        doc.text(splitDesc, margin + 2, cursorY);
        cursorY += splitDesc.length * 4 + 2;
      }

      // Details: Places | Activities | Food
      const placesList = Array.isArray(dayObj.places) ? dayObj.places.join(' • ') : '';
      const activitiesList = Array.isArray(dayObj.activities) ? dayObj.activities.join(' • ') : '';
      const foodList = Array.isArray(dayObj.food_recommendations) ? dayObj.food_recommendations.join(' • ') : '';

      const bulletItems = [];
      if (placesList) bulletItems.push({ tag: 'Places Visited', text: placesList, color: COLORS.secondary });
      if (activitiesList) bulletItems.push({ tag: 'Scheduled Activities', text: activitiesList, color: COLORS.primary });
      if (foodList) bulletItems.push({ tag: 'Culinary Recommendations', text: foodList, color: COLORS.warning });

      bulletItems.forEach((b) => {
        const fullLine = `${b.tag}: ${b.text}`;
        const splitLine = doc.splitTextToSize(fullLine, contentWidth - 6);
        ensureSpace(splitLine.length * 3.8 + 2);

        doc.setFillColor(...b.color);
        doc.circle(margin + 3, cursorY - 1, 0.8, 'F');

        doc.setFont('helvetica', 'bold');
        doc.setFontSize(7.5);
        doc.setTextColor(...b.color);
        doc.text(`${b.tag}: `, margin + 6, cursorY);

        const tagOffset = doc.getTextWidth(`${b.tag}: `);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...COLORS.slateDark);
        doc.text(doc.splitTextToSize(b.text, contentWidth - 6 - tagOffset), margin + 6 + tagOffset, cursorY);

        cursorY += splitLine.length * 3.8 + 1;
      });

      doc.setDrawColor(...COLORS.border);
      doc.line(margin, cursorY + 1, pageWidth - margin, cursorY + 1);
      cursorY += 5;
    });
  }

  // -------------------------------------------------------------
  // 6. RECOMMENDED HOTELS & ACCOMMODATIONS
  // -------------------------------------------------------------
  const hotelList = (Array.isArray(hotels) && hotels.length > 0)
    ? hotels
    : (Array.isArray(tripPlan.hotels) && tripPlan.hotels.length > 0)
    ? tripPlan.hotels
    : (Array.isArray(destinationData?.hotels) && destinationData.hotels.length > 0)
    ? destinationData.hotels
    : [];

  if (hotelList.length > 0) {
    ensureSpace(35);
    drawSectionHeader('Recommended Accommodations & Stays');

    const hotelRows = hotelList.slice(0, 5).map((h) => {
      const priceVal = h.price ?? h.price_per_night ?? h.pricePerNight;
      const priceStr = priceVal ? `${formatINR(priceVal)}/night` : '-';
      const ratingVal = h.rating;
      const reviewCount = h.reviews ?? h.reviews_count;
      const ratingStr = ratingVal ? `★ ${ratingVal}${reviewCount ? ` (${reviewCount})` : ''}` : '-';
      const amenitiesStr = Array.isArray(h.amenities) && h.amenities.length > 0
        ? h.amenities.slice(0, 3).join(', ')
        : '-';
      const locationStr = h.area || h.location || '-';
      const tierStr = (h.tier || h.category || '-').toUpperCase();

      return [
        h.name || '-',
        locationStr,
        tierStr,
        ratingStr,
        priceStr,
        amenitiesStr,
      ];
    });

    autoTable(doc, {
      startY: cursorY,
      margin: { left: margin, right: margin },
      head: [['Property Name', 'Location / Area', 'Tier / Type', 'Rating', 'Est. Tariff', 'Top Amenities']],
      body: hotelRows,
      theme: 'grid',
      headStyles: {
        fillColor: COLORS.primaryDark,
        textColor: COLORS.white,
        fontStyle: 'bold',
        fontSize: 7.5,
        cellPadding: 2,
      },
      bodyStyles: {
        fontSize: 7,
        textColor: COLORS.slateDark,
        cellPadding: 2,
      },
      columnStyles: {
        0: { cellWidth: 42, fontStyle: 'bold' },
        1: { cellWidth: 28 },
        2: { cellWidth: 24 },
        3: { cellWidth: 22, textColor: [217, 119, 6] },
        4: { cellWidth: 24, fontStyle: 'bold', halign: 'right' },
        5: { cellWidth: 42, fontSize: 6.5, textColor: COLORS.slateMuted },
      },
    });

    cursorY = doc.lastAutoTable.finalY + 6;
  }

  // -------------------------------------------------------------
  // 7. KEY PLACES & ATTRACTIONS
  // -------------------------------------------------------------
  const destPlaces = Array.isArray(destinationData?.places) ? destinationData.places : [];
  const itineraryPlaces = [...new Set(days.flatMap((d) => d.places || []))];

  if (destPlaces.length > 0 || itineraryPlaces.length > 0) {
    ensureSpace(35);
    drawSectionHeader('Key Places & Must-Visit Attractions');

    let placeRows = [];
    let placeHeaders = [];
    let placeColStyles = {};

    if (destPlaces.length > 0) {
      placeHeaders = [['Attraction / Site Name', 'Category', 'Best Timing', 'Entry Fee', 'Highlights']];
      placeRows = destPlaces.slice(0, 6).map((p) => {
        const feeStr = p.entryFee !== undefined ? (p.entryFee === 0 ? 'Free' : formatINR(p.entryFee)) : '-';
        return [
          p.name || '-',
          p.category || 'Sightseeing',
          p.bestTimeToVisit || '-',
          feeStr,
          p.highlights || '-',
        ];
      });
      placeColStyles = {
        0: { cellWidth: 42, fontStyle: 'bold' },
        1: { cellWidth: 28 },
        2: { cellWidth: 26 },
        3: { cellWidth: 22, halign: 'right' },
        4: { cellWidth: 64, fontSize: 6.5, textColor: COLORS.slateMuted },
      };
    } else {
      placeHeaders = [['Attraction / Site Name', 'Scheduled Day(s)']];
      placeRows = itineraryPlaces.map((placeName) => {
        const scheduledDays = days
          .filter((d) => (d.places || []).includes(placeName))
          .map((d) => `Day ${d.day}`)
          .join(', ');
        return [placeName, scheduledDays || 'Scheduled in itinerary'];
      });
      placeColStyles = {
        0: { cellWidth: 80, fontStyle: 'bold' },
        1: { cellWidth: 102 },
      };
    }

    autoTable(doc, {
      startY: cursorY,
      margin: { left: margin, right: margin },
      head: placeHeaders,
      body: placeRows,
      theme: 'grid',
      headStyles: {
        fillColor: COLORS.primaryDark,
        textColor: COLORS.white,
        fontStyle: 'bold',
        fontSize: 7.5,
        cellPadding: 2,
      },
      bodyStyles: {
        fontSize: 7,
        textColor: COLORS.slateDark,
        cellPadding: 2,
      },
      columnStyles: placeColStyles,
    });

    cursorY = doc.lastAutoTable.finalY + 6;
  }

  // -------------------------------------------------------------
  // 8. CURATED ACTIVITIES & EXPERIENCES
  // -------------------------------------------------------------
  const allActivities = days.flatMap((d) =>
    (d.activities || []).map((act) => ({
      day: d.day,
      activity: act,
    }))
  );
  const selectedActs = Array.isArray(formData.selectedActivities) ? formData.selectedActivities : [];

  if (allActivities.length > 0 || selectedActs.length > 0) {
    ensureSpace(35);
    drawSectionHeader('Curated Activities & Experiences');

    const activityRows = [];
    allActivities.forEach((item) => {
      activityRows.push([`Day ${item.day}`, item.activity, 'Scheduled Itinerary']);
    });
    selectedActs.forEach((act) => {
      const formatted = act.replace(/_/g, ' ').toUpperCase();
      if (!allActivities.some((a) => a.activity.toLowerCase() === act.toLowerCase())) {
        activityRows.push(['Special Interest', formatted, 'User Selected']);
      }
    });

    autoTable(doc, {
      startY: cursorY,
      margin: { left: margin, right: margin },
      head: [['Schedule / Phase', 'Activity / Experience', 'Type']],
      body: activityRows,
      theme: 'striped',
      headStyles: {
        fillColor: COLORS.primaryDark,
        textColor: COLORS.white,
        fontStyle: 'bold',
        fontSize: 7.5,
        cellPadding: 2,
      },
      bodyStyles: {
        fontSize: 7,
        textColor: COLORS.slateDark,
        cellPadding: 2,
      },
      columnStyles: {
        0: { cellWidth: 34, fontStyle: 'bold' },
        1: { cellWidth: 114 },
        2: { cellWidth: 34, textColor: COLORS.slateMuted },
      },
    });

    cursorY = doc.lastAutoTable.finalY + 6;
  }

  // -------------------------------------------------------------
  // 9 & 10. ACTIONABLE TRAVEL TIPS & PACKING GUIDELINES
  // -------------------------------------------------------------
  const travelTips = Array.isArray(tripPlan.travel_tips) ? tripPlan.travel_tips : [];
  const packingTips = Array.isArray(tripPlan.packing_tips) ? tripPlan.packing_tips : [];

  if (travelTips.length > 0 || packingTips.length > 0) {
    ensureSpace(35);
    drawSectionHeader('Actionable Travel Tips & Packing Guidelines');

    const maxItems = Math.max(travelTips.length, packingTips.length);
    const tipsTableData = [];

    for (let i = 0; i < maxItems; i++) {
      const t = travelTips[i] ? `• ${travelTips[i]}` : '';
      const p = packingTips[i] ? `[x] ${packingTips[i]}` : '';
      tipsTableData.push([t, p]);
    }

    autoTable(doc, {
      startY: cursorY,
      margin: { left: margin, right: margin },
      head: [['Local Etiquette, Safety & Transport Tips', 'Packing Essentials & Checklist']],
      body: tipsTableData,
      theme: 'plain',
      headStyles: {
        fillColor: [241, 245, 249],
        textColor: COLORS.slateDark,
        fontStyle: 'bold',
        fontSize: 8,
        cellPadding: 2.5,
      },
      bodyStyles: {
        fontSize: 7.5,
        textColor: COLORS.slateText,
        cellPadding: 1.8,
      },
      columnStyles: {
        0: { cellWidth: 91 },
        1: { cellWidth: 91 },
      },
    });

    cursorY = doc.lastAutoTable.finalY + 6;
  }

  // -------------------------------------------------------------
  // RUNNING FOOTERS & PAGE NUMBERING (Vector Pass)
  // -------------------------------------------------------------
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);

    // Bottom divider line
    doc.setDrawColor(...COLORS.border);
    doc.line(margin, pageHeight - 11, pageWidth - margin, pageHeight - 11);

    // Left: Branding & Grounding
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    doc.setTextColor(...COLORS.slateMuted);
    const footerDest = destName ? ` | ${destName}` : '';
    doc.text(
      `TripGenie AI — RAG-Grounded Travel Planner${footerDest}`,
      margin,
      pageHeight - 6.5
    );

    // Right: Page X of Y
    const pageStr = `Page ${i} of ${totalPages}`;
    doc.text(pageStr, pageWidth - margin - doc.getTextWidth(pageStr), pageHeight - 6.5);
  }

  // -------------------------------------------------------------
  // TRIGGER DOWNLOAD
  // -------------------------------------------------------------
  const sanitizedDest = (destName || 'Trip').replace(/[^a-zA-Z0-9_-]/g, '_');
  const filename = `TripGenie_${sanitizedDest}_${durationDays}Days_Itinerary.pdf`;
  doc.save(filename);

  return { success: true, filename, totalPages, doc };
}
