import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

def format_inr(val):
    if val is None or val == "":
        return "₹0"
    try:
        return f"₹{int(float(val)):,}"
    except (ValueError, TypeError):
        return f"₹{val}"

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic 'Page X of Y' footers and headers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Running footer
        page_width, page_height = A4
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.75)
        self.line(36, 32, page_width - 36, 32)
        
        self.drawString(36, 20, "TripGenie AI — RAG-Grounded Intelligent Travel Planner")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_width - 36, 20, page_str)
        self.restoreState()

def build_pdf_buffer(trip_data: dict, form_data: dict = None, hotels: list = None) -> io.BytesIO:
    """
    Builds a professional, print-ready travel itinerary PDF using ReportLab.
    Returns an in-memory BytesIO buffer.
    """
    form_data = form_data or {}
    hotels = hotels or []
    destination = trip_data.get("destination", "Custom Trip")
    days = trip_data.get("days", [])
    summary = trip_data.get("summary", "")
    budget_breakdown = trip_data.get("budget_breakdown", {})
    travel_tips = trip_data.get("travel_tips", [])
    packing_tips = trip_data.get("packing_tips", [])
    
    travelers = form_data.get("travelers", 2)
    duration_days = len(days) if days else form_data.get("days", 4)
    budget = budget_breakdown.get("user_budget", form_data.get("budget", 50000))
    total_est = budget_breakdown.get("total_estimated_cost", budget)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e1b4b"),
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#6366f1"),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    bold_label = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1e293b")
    )
    chip_style = ParagraphStyle(
        'ChipText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.white
    )

    story = []

    # 1. Title Banner Strip
    story.append(Paragraph("TRIPGENIE AI — TRAVEL ITINERARY", title_style))
    story.append(Paragraph(f"Personalized Travel Dossier for <b>{destination}</b> • Generated on {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4f46e5"), spaceBefore=0, spaceAfter=10))

    # 2. Key Metadata Strip Table
    meta_data = [
        [
            Paragraph(f"<b>DESTINATION</b><br/>{destination}", body_style),
            Paragraph(f"<b>DURATION</b><br/>{duration_days} Days / {max(1, duration_days - 1)} Nights", body_style),
            Paragraph(f"<b>TRAVELERS</b><br/>{travelers} Person(s)", body_style),
            Paragraph(f"<b>USER BUDGET</b><br/>{format_inr(budget)}", body_style),
            Paragraph(f"<b>EST. TOTAL</b><br/>{format_inr(total_est)}", body_style),
        ]
    ]
    meta_table = Table(meta_data, colWidths=[105, 105, 105, 105, 105])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. Trip Overview / Summary
    if summary:
        story.append(Paragraph("Executive Summary & Trip Overview", section_heading))
        summary_table = Table([[Paragraph(summary, body_style)]], colWidths=[525])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 10))

    # 4. Budget Breakdown Table
    if budget_breakdown:
        story.append(Paragraph("Financial Budget Breakdown", section_heading))
        
        accom_cost = budget_breakdown.get("accommodation", {}).get("total_cost", budget_breakdown.get("stay", 0))
        food_cost = budget_breakdown.get("food", {}).get("total_cost", budget_breakdown.get("food", 0))
        act_cost = budget_breakdown.get("activities", {}).get("total_cost", budget_breakdown.get("activities", 0))
        trans_cost = budget_breakdown.get("transportation", {}).get("total_cost", budget_breakdown.get("transport", 0))
        misc_cost = budget_breakdown.get("miscellaneous", {}).get("total_cost", 0)

        tot = total_est or 1
        b_rows = [
            [Paragraph("<b>Expense Category</b>", bold_label), Paragraph("<b>Estimated Cost</b>", bold_label), Paragraph("<b>Share</b>", bold_label)],
            [Paragraph("Accommodation (Rooms & Stays)", body_style), Paragraph(format_inr(accom_cost), body_style), Paragraph(f"{(accom_cost / tot) * 100:.1f}%", body_style)],
            [Paragraph("Food & Dining", body_style), Paragraph(format_inr(food_cost), body_style), Paragraph(f"{(food_cost / tot) * 100:.1f}%", body_style)],
            [Paragraph("Sightseeing & Activities", body_style), Paragraph(format_inr(act_cost), body_style), Paragraph(f"{(act_cost / tot) * 100:.1f}%", body_style)],
            [Paragraph("Transportation (Local & Transfers)", body_style), Paragraph(format_inr(trans_cost), body_style), Paragraph(f"{(trans_cost / tot) * 100:.1f}%", body_style)],
            [Paragraph("Contingency & Reserve (7%)", body_style), Paragraph(format_inr(misc_cost), body_style), Paragraph(f"{(misc_cost / tot) * 100:.1f}%", body_style)],
            [Paragraph("<b>Total Estimated Expenditure</b>", bold_label), Paragraph(f"<b>{format_inr(total_est)}</b>", bold_label), Paragraph("<b>100.0%</b>", bold_label)]
        ]
        b_table = Table(b_rows, colWidths=[275, 150, 100])
        b_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f8fafc")),
            ('PADDING', (0, 0), (-1, -1), 4.5),
        ]))
        story.append(b_table)
        story.append(Spacer(1, 10))

    # 5. Day-by-Day Itinerary
    if days:
        story.append(Paragraph("Day-by-Day Comprehensive Itinerary", section_heading))
        for d in days:
            day_num = d.get("day", 1)
            day_title = d.get("title", f"Day {day_num}")
            desc = d.get("description", "")
            places = ", ".join(d.get("places", []))
            activities = ", ".join(d.get("activities", []))
            food = ", ".join(d.get("food_recommendations", []))
            cost = d.get("estimated_cost", None)

            cost_str = f" • Est. Cost: {format_inr(cost)}" if cost else ""
            header_text = f"<b>DAY {day_num}: {day_title}</b>{cost_str}"

            day_elements = [
                [Paragraph(f"<font color='#ffffff'>{header_text}</font>", chip_style)],
                [Paragraph(desc, body_style)]
            ]

            details_text = ""
            if places:
                details_text += f"<b>📍 Places Visited:</b> {places}<br/>"
            if activities:
                details_text += f"<b>🏄 Activities:</b> {activities}<br/>"
            if food:
                details_text += f"<b>🍽️ Food Recommendations:</b> {food}"

            if details_text:
                day_elements.append([Paragraph(details_text, body_style)])

            d_table = Table(day_elements, colWidths=[525])
            d_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, 0), 4),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ]))

            story.append(d_table)
            story.append(Spacer(1, 6))

    # 6. Recommended Hotels (if provided)
    if hotels:
        story.append(Spacer(1, 6))
        story.append(Paragraph("Recommended Stays & Accommodations", section_heading))
        hotel_rows = [
            [Paragraph("<b>Hotel Name</b>", bold_label), Paragraph("<b>Area</b>", bold_label), Paragraph("<b>Tier / Rating</b>", bold_label), Paragraph("<b>Tariff / Night</b>", bold_label)]
        ]
        for h in hotels[:4]:
            h_name = h.get("name", "Verified Hotel")
            h_area = h.get("area", "Prime Location")
            h_rating = f"{h.get('tier', 'Comfort').upper()} • ★ {h.get('rating', '4.5')}"
            h_price = format_inr(h.get("price", 3000))
            hotel_rows.append([
                Paragraph(h_name, body_style),
                Paragraph(h_area, body_style),
                Paragraph(h_rating, body_style),
                Paragraph(h_price, body_style)
            ])

        h_table = Table(hotel_rows, colWidths=[175, 125, 125, 100])
        h_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 4.5),
        ]))
        story.append(h_table)
        story.append(Spacer(1, 10))

    # 7. Travel Tips & Packing
    if travel_tips or packing_tips:
        story.append(Spacer(1, 6))
        story.append(Paragraph("Traveler Advice & Packing Checklist", section_heading))
        
        tips_content = ""
        for t in travel_tips[:5]:
            tips_content += f"• {t}<br/>"
        
        packing_content = ""
        for p in packing_tips[:5]:
            packing_content += f"✔ {p}<br/>"

        tp_table = Table([
            [Paragraph("<b>Verified Travel Tips</b>", bold_label), Paragraph("<b>Packing Checklist</b>", bold_label)],
            [Paragraph(tips_content or "Standard local travel precautions apply.", body_style), Paragraph(packing_content or "Weather appropriate clothing, valid ID.", body_style)]
        ], colWidths=[262, 263])
        tp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(tp_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
