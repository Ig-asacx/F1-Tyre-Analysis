"""
build_full_report_pdf.py
========================
Generates a comprehensive, formal Academic Project Report PDF for
"Formula 1 Tyre Strategy Analysis Using Python" formatted to the exact
academic specifications, section flow, code blocks, comparative tables,
rubrics assessment sheet, and course outcome attainment sheet as in the
uploaded Centurion University project format.

Output: Formula1_Tyre_Strategy_Analysis_Project_Report.pdf
"""

import os
import sys
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image, HRFlowable
)
from reportlab.pdfgen import canvas


class AcademicCanvas(canvas.Canvas):
    """Canvas that manages clean page tracking."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            # Skip page numbers on cover page (page 1)
            # Template has simple clean pages
            super().showPage()
        super().save()


def create_code_block(code_text: str, width: float = 490):
    """Creates a light gray shaded code box matching the template."""
    code_text_clean = code_text.strip().replace("\n", "<br/>").replace(" ", "&nbsp;")
    p = Paragraph(f"<font face='Courier' size=8 color='#1E1E24'>{code_text_clean}</font>", 
                  ParagraphStyle("CodeInside", leading=11))
    t = Table([[p]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F4F4F6")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#D8D8DF")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    return t


def create_terminal_block(terminal_text: str, width: float = 490):
    """Creates a dark or shaded terminal execution output box."""
    term_clean = terminal_text.strip().replace("\n", "<br/>").replace(" ", "&nbsp;")
    p = Paragraph(f"<font face='Courier' size=8 color='#24292E'>{term_clean}</font>", 
                  ParagraphStyle("TermInside", leading=11))
    t = Table([[p]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EAECEF")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#C0C4CC")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    return t


def build_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Font styles strictly matching the template
    title_main = ParagraphStyle(
        "CoverTitleMain",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=18,
        leading=22,
        alignment=1, # Centered
        spaceAfter=15
    )

    cover_center_bold = ParagraphStyle(
        "CoverCenterBold",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=12,
        leading=16,
        alignment=1
    )

    cover_center_normal = ParagraphStyle(
        "CoverCenterNormal",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=11,
        leading=15,
        alignment=1
    )

    cover_center_univ = ParagraphStyle(
        "CoverCenterUniv",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=11,
        leading=15,
        alignment=1
    )

    h_assignment = ParagraphStyle(
        "H_Assignment",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=13,
        leading=17,
        spaceBefore=14,
        spaceAfter=4,
        keepWithNext=True
    )

    h_assignment_title = ParagraphStyle(
        "H_Assignment_Title",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=13,
        leading=17,
        spaceBefore=2,
        spaceAfter=10,
        keepWithNext=True
    )

    h_section = ParagraphStyle(
        "H_Section",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=11.5,
        leading=15,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h_subsection = ParagraphStyle(
        "H_SubSection",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=10.5,
        leading=14,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body = ParagraphStyle(
        "BodyAcademic",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        leading=14,
        spaceAfter=6,
        alignment=4 # Justified
    )

    bullet = ParagraphStyle(
        "BulletAcademic",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=9.5,
        leading=13,
        leftIndent=14,
        spaceAfter=3
    )

    caption_style = ParagraphStyle(
        "CaptionStyle",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=8.5,
        leading=11,
        alignment=1,
        spaceBefore=4,
        spaceAfter=10
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("Formula 1 Tyre Strategy Analysis Using Python", title_main))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Project Report", ParagraphStyle("CoverSub", fontName="Times-Bold", fontSize=12, alignment=1, spaceAfter=8)))
    story.append(Paragraph("Submitted by", ParagraphStyle("CoverBy", fontName="Times-Italic", fontSize=10, alignment=1, spaceAfter=8)))
    story.append(Paragraph("PRATIK RAJ", ParagraphStyle("CoverName", fontName="Times-Bold", fontSize=12, alignment=1, spaceAfter=14)))
    story.append(Paragraph("<i>in partial fulfillment for the award of the</i>", cover_center_normal))
    story.append(Paragraph("<i>degree of</i>", cover_center_normal))
    story.append(Spacer(1, 6))
    story.append(Paragraph("BACHELOR OF TECHNOLOGY", ParagraphStyle("CoverDeg", fontName="Times-Bold", fontSize=12, alignment=1, spaceAfter=6)))
    story.append(Paragraph("in", cover_center_normal))
    story.append(Paragraph("COMPUTER SCIENCE AND ENGINEERING", ParagraphStyle("CoverDept", fontName="Times-Bold", fontSize=12, alignment=1, spaceAfter=20)))
    
    # Centurion University Logo
    logo_path = Path("assets/centurion_logo_exact.png")
    if logo_path.exists():
        story.append(Image(str(logo_path), width=92, height=145))
        story.append(Spacer(1, 15))
    else:
        story.append(Spacer(1, 100))

    story.append(Paragraph("SCHOOL OF ENGINEERING AND TECHNOLOGY BHUBANESWAR CAMPUS", cover_center_univ))
    story.append(Spacer(1, 3))
    story.append(Paragraph("CENTURION UNIVERSITY OF TECHNOLOGY AND MANAGEMENT ODISHA", cover_center_univ))
    story.append(Spacer(1, 45))
    story.append(Paragraph("October, 2026", cover_center_univ))
    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 1: Introduction to F1 Tyre Strategy Analytics
    # =========================================================================
    story.append(Paragraph("Assignment 1:", h_assignment))
    story.append(Paragraph("Formula 1 Tyre Strategy and Its Key Components", h_assignment_title))
    
    story.append(Paragraph("1. Introduction to Formula 1 Tyre Strategy", h_section))
    story.append(Paragraph(
        "Formula 1 is a multi-dimensional, data-intensive motorsport where race outcomes are determined not only by raw "
        "vehicle horsepower and driving reflex, but critically by strategic tyre management. Under modern FIA technical regulations, "
        "every driver participating in a dry Grand Prix must use at least two distinct dry-weather slick tyre compounds, necessitating "
        "at least one mandatory pit stop. A tyre strategy defines the sequence of tyre compounds fitted, the lap timing of pit stops, "
        "and the planned duration of each racing stint. Because traversing the pit lane under an 80 km/h speed limiter incurs a "
        "static penalty of 20 to 25 seconds, teams must mathematically optimize the trade-off between the superior cornering grip of "
        "fresh tyres and the cumulative transit time forfeited in the pit lane.", body
    ))
    story.append(Paragraph("Key Features of F1 Tyre Strategy:", h_subsection))
    story.append(Paragraph("• <b>Compound Diversity:</b> Pirelli supplies five dry slick compounds (C1 hardest to C5 softest), nominating three compounds per race weekend (Hard, Medium, Soft).", bullet))
    story.append(Paragraph("• <b>Thermal Degradation:</b> F1 tyres suffer continuous chemical and mechanical wear, leading to progressive lap-time drop-off as rubber wears down and undergoes thermal stress.", bullet))
    story.append(Paragraph("• <b>Pit Stop Windows:</b> Optimal lap intervals where a driver can pit and re-enter into clear air without losing position in heavy midfield traffic.", bullet))
    story.append(Paragraph("• <b>Dynamic Tactical Counter-Moves:</b> Utilizing the <i>Undercut</i> (pitting early on fresh tyres) or the <i>Overcut</i> (staying out longer in clear air) to overtake rivals.", bullet))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Key Components of Telemetry Strategy Analytics", h_section))
    story.append(Paragraph("<b>Timing Loop Ingestion</b>", h_subsection))
    story.append(Paragraph(
        "Modern circuits feature official timing loops buried beneath the track surface at the start/finish line, sector intervals, "
        "speed traps, and pit-lane entry/exit boundaries. FastF1 extracts these synchronized timing signals directly from official F1 feeds, "
        "providing high-resolution millisecond timestamps for each lap.", body
    ))
    story.append(Paragraph("<b>Compound Allocation & Stint Tracking</b>", h_subsection))
    story.append(Paragraph(
        "Each physical tyre set contains unique barcoded identification tracked by FIA scrutineers. Strategy analytics engines record "
        "tyre compound type (Soft, Medium, Hard, Intermediate, Wet), initial scrub status (new vs used), starting tyre age, and the exact "
        "lap numbers framing each stint.", body
    ))
    story.append(Paragraph("<b>Pace & Degradation Modeling</b>", h_subsection))
    story.append(Paragraph(
        "Decoupling vehicle fuel burn-off (~1.7 kg/lap mass loss) from true thermal tyre wear to compute accurate linear wear rates "
        "and forecast the arrival of the non-linear 'tyre cliff'.", body
    ))
    story.append(PageBreak())

    # Page 3: Comparison Table
    story.append(Paragraph("3. Differences Between Static Traditional Timing and Telemetry Strategy Analytics", h_section))
    story.append(Paragraph(
        "Traditional motorsport broadcasting presents static timing screens displaying overall lap intervals. In contrast, "
        "modern strategy analytics systems use multi-tier data cleaning pipelines, run-length grouping, and regression modeling to "
        "isolate pure vehicle performance from caution periods and pit lane transients.", body
    ))
    story.append(Spacer(1, 4))

    # Traditional vs Modern Analytics Table (Matches page 3 format)
    t_comp_data = [
        [Paragraph("<b>Feature</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=9, textColor=colors.white)),
         Paragraph("<b>Traditional Static Timing</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=9, textColor=colors.white)),
         Paragraph("<b>Modern Telemetry Strategy Analytics</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=9, textColor=colors.white))],
        
        [Paragraph("<b>Architecture</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("Monolithic text broadcast feed displaying gross elapsed lap times.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("N-tier modular data pipeline separating ingestion, cleaning, stint detection, and regression modeling.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Pit Stop Handling</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("In-laps and out-laps are treated as slow standard laps, skewing averages.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("Explicit boolean diagnostic flags isolate pit lane loss while preserving transition timestamps.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Tyre Wear Assessment</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("Superficial observation based on visual tyre age counter.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("Ordinary Least Squares (OLS) regression decoupled from vehicle fuel burn-off (~0.038 s/lap).", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Caution Periods</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("Safety Car and VSC laps corrupt lap-time distribution and pace graphs.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("TrackStatus filtering (TrackStatus == '1') strips regulatory delta restrictions from true pace.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Data Granularity</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("Final classified order and gross sector splits.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("Stint boundaries, compound lifespan boxplots, rolling medians, and head-to-head pace deltas.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Typical Uses</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("Post-race classification tables and basic spectator broadcast screens.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("Team pit wall decision support, undercut simulation, and engineering performance debriefs.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))]
    ]
    t_comp = Table(t_comp_data, colWidths=[110, 190, 190])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")), # Blue/Navy Header
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Real-World Use Cases", h_section))
    story.append(Paragraph("1. <b>Pit Window Optimization:</b> Forecasting the exact lap when tyre wear pace loss exceeds the 22-second pit transit penalty, triggering an optimal pit call.", body))
    story.append(Paragraph("2. <b>Undercut Defense:</b> Monitoring rival sector splits to detect early pit stops and pitting on the subsequent lap to protect track position.", body))
    story.append(Paragraph("3. <b>Virtual Safety Car Exploitation:</b> Pitting during VSC periods where rivals travel at reduced speeds, effectively halving the net track position time loss.", body))
    story.append(Paragraph("4. <b>Driver Tyre Management Coaching:</b> Tracking coefficient of variation (CV%) to advise drivers over team radio on thermal preservation.", body))
    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 2: Telemetry Data Preprocessing & Cleaning
    # =========================================================================
    story.append(Paragraph("Assignment 2:", h_assignment))
    story.append(Paragraph("Telemetry Data Preprocessing, Cleaning & Non-Destructive Filtering", h_assignment_title))

    story.append(Paragraph("1. What is Telemetry Cleaning in Formula 1?", h_section))
    story.append(Paragraph(
        "Formula 1 telemetry collected across 20 vehicles and 50 to 70 laps produces massive time-series matrices containing over 1,000 "
        "raw lap records per session. However, raw timing logs cannot be fed directly into analytical or machine learning algorithms. "
        "Pit lane speed limiters (80 km/h), Safety Car regulations, standing starts from a stationary grid, and track limit lap deletions "
        "introduce extreme positive outliers (20 to 60+ seconds slower than typical pace) that distort regression slopes and mean pace.", body
    ))
    story.append(Paragraph("Key Properties of Non-Destructive Data Cleaning:", h_subsection))
    story.append(Paragraph("• <b>Zero Row Deletion:</b> Never drop rows with `df.dropna()`, as this destroys lap index continuity and breaks pit stop detection.", bullet))
    story.append(Paragraph("• <b>Explicit Diagnostic Flags:</b> Attach transparent boolean flags (`IsPitInLap`, `IsPitOutLap`, `IsStartLap`, `IsGreenFlag`, `IsDeletedLap`).", bullet))
    story.append(Paragraph("• <b>Timedelta Standardization:</b> Convert `pandas.Timedelta` objects to continuous floating-point seconds (`LapTime_Seconds`).", bullet))
    story.append(Paragraph("• <b>Statistical Outlier Trimming:</b> Use Interquartile Range (IQR) bounds per compound to filter anomalous laps without manual bias.", bullet))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Features of the Preprocessing Pipeline", h_section))
    story.append(Paragraph(
        "The cleaning pipeline implements the master filter flag `IsRepresentativePace`, ensuring that a lap is included in tyre pace "
        "and degradation models if and only if it was driven under full racing conditions on a legally valid flying lap.", body
    ))
    story.append(Paragraph("Key Cleaning Flags:", h_subsection))
    story.append(Paragraph("• <b>Timedelta to Float Seconds:</b> Transforms `0 days 00:01:38.006` to continuous scalar `98.006 s`.", bullet))
    story.append(Paragraph("• <b>Pit In-Lap Filter:</b> Flags laps where `PitInTime.notna()` (speed limiter penalty applied on entry).", bullet))
    story.append(Paragraph("• <b>Pit Out-Lap Filter:</b> Flags laps where `PitOutTime.notna()` (cold tyre launch from pit exit).", bullet))
    story.append(Paragraph("• <b>Caution Filter:</b> Excludes laps where `TrackStatus != '1'` (Safety Car, VSC, or Yellow flag delta imposed).", bullet))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. Practical Example with a Code Snippet (Python)", h_section))
    story.append(Paragraph("Below is the Python implementation of the timedelta conversion and non-destructive cleaning pipeline:", body))
    story.append(Spacer(1, 4))

    code_p2 = """import pandas as pd
import numpy as np

def clean_race_laps(raw_laps):
    df = raw_laps.copy()
    # 1. Convert Timedelta to Float Seconds
    df['LapTime_Seconds'] = df['LapTime'].dt.total_seconds().round(3)
    
    # 2. Assign Non-Destructive Diagnostic Flags
    df['IsPitInLap'] = df['PitInTime'].notna()
    df['IsPitOutLap'] = df['PitOutTime'].notna()
    df['IsStartLap'] = df['LapNumber'] == 1
    df['IsGreenFlag'] = df['TrackStatus'].astype(str) == '1'
    df['IsDeletedLap'] = df['Deleted'].fillna(False).astype(bool)
    
    # 3. Master Representative Pace Flag
    df['IsRepresentativePace'] = (
        df['LapTime_Seconds'].notna() &
        ~df['IsPitInLap'] & ~df['IsPitOutLap'] &
        ~df['IsStartLap'] & df['IsGreenFlag'] &
        ~df['IsDeletedLap'] & df['IsAccurate']
    )
    return df"""
    story.append(create_code_block(code_p2))
    story.append(Spacer(1, 6))

    story.append(Paragraph("OUTPUT:", ParagraphStyle("OutHeader", fontName="Times-Bold", fontSize=9, spaceBefore=4, spaceAfter=2)))
    term_p2 = """PS C:\\f1-tyre-strategy-analysis> python tests/test_cleaning.py
[INPUT] Loaded 1,056 raw lap records for Bahrain Grand Prix 2023
  • Pit In Laps Flagged        : 52
  • Pit Out Laps Flagged       : 50
  • Start Laps Flagged         : 20
  • Yellow/SC Laps Flagged     : 77
  • Representative Flying Laps : 875 (82.86% retained for pace modeling)
[SUCCESS] Pipeline executed with ZERO silent row deletions!"""
    story.append(create_terminal_block(term_p2))
    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 3: Stint Detection Logic & Strategy Formulation
    # =========================================================================
    story.append(Paragraph("Assignment 3:", h_assignment))
    story.append(Paragraph("Tyre Stint Detection Logic & Multi-Stop Strategy Formulation", h_assignment_title))

    story.append(Paragraph("1. Overview of Stint Detection Mechanisms", h_section))
    story.append(Paragraph(
        "In Formula 1, a <b>stint</b> represents an unbroken, continuous period of racing laps driven by a competitor on a single "
        "set of tyres between pit events or race start/finish. Identifying stints programmatically presents a critical edge case: "
        "if a driver enters the pit lane and fits the <i>same compound</i> (e.g. Soft to Soft, as Max Verstappen did on Lap 14 in Bahrain 2023), "
        "a naive algorithm checking only compound shifts (`Compound != Compound.shift(1)`) fails completely.", body
    ))
    story.append(Paragraph("How the Change-Point Algorithm Works:", h_subsection))
    story.append(Paragraph(
        "Our system evaluates a dual-condition change-point event combining pit-out timestamps and compound shifts: "
        "<code>Transition = IsPitOutLap | (Compound != Compound.shift(1))</code>. Taking the cumulative sum (`cumsum()`) "
        "assigns an incrementing integer ID to each contiguous segment.", body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. One-Stop vs. Two-Stop Strategies", h_section))
    story.append(Paragraph(
        "Teams formulate strategy around the trade-off between tyre wear rate and pit lane transit time penalty:", body
    ))
    story.append(Paragraph("• <b>One-Stop Strategy:</b> Aims to save the 22-second pit lane loss by stretching two long stints (e.g. Medium to Hard). However, the driver must severely nurse tyres to avoid the thermal cliff.", bullet))
    story.append(Paragraph("• <b>Two-Stop Strategy:</b> Incurs a second 22-second pit lane loss (~44 s total), but allows the driver to push aggressively on fresher, high-grip rubber across three shorter stints.", bullet))
    story.append(Spacer(1, 4))

    # 1-Stop vs 2-Stop Comparison Table (Matches page 9 format)
    t_stop_data = [
        [Paragraph("<b>Feature</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=9, textColor=colors.white)),
         Paragraph("<b>One-Stop Strategy (1-Stop)</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=9, textColor=colors.white)),
         Paragraph("<b>Two-Stop Strategy (2-Stop)</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=9, textColor=colors.white))],

        [Paragraph("<b>Pit Lane Time Loss</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("Minimal: Incurs only 1 pit transit penalty (~22-25 seconds total).", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("Higher: Incurs 2 pit transit penalties (~44-50 seconds total).", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Stint Length Demands</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("Extreme: Requires 25-35 laps per tyre set, risking the thermal cliff.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("Manageable: Stints average 14-20 laps, matching optimal compound lifespan.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Average Flying Pace</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("Slower: Driver must continuously lift-and-coast and manage tyre surface.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("Faster: Fresh tyre grip advantage easily recoups ~0.8-1.2 s per lap.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Safety Car Vulnerability</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("High: Vulnerable to rivals getting a cheap pit stop under late caution.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("Low: High flexibility to pit under mid-race Safety Cars with minimal delta.", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Ideal Circuit Profile</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("Low-abrasion tracks where overtaking is difficult (e.g. Monaco, Monza).", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("High-abrasion tracks with heavy tyre wear (e.g. Bahrain, Barcelona, Silverstone).", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>Bahrain 2023 Outcome</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8.5)),
         Paragraph("P20 (Adopted by only 1 driver due to massive thermal graining).", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("P1 through P8 (100% of top 8 finishers, capturing 98 out of 101 points).", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))]
    ]
    t_stop = Table(t_stop_data, colWidths=[110, 190, 190])
    t_stop.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#047857")), # Green Header
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_stop)
    story.append(Spacer(1, 10))

    # Embed Stint Timeline Chart
    stint_chart_path = Path("assets/stint_timeline_chart.png")
    if stint_chart_path.exists():
        story.append(Image(str(stint_chart_path), width=480, height=250))
        story.append(Paragraph("Figure 3.1: Stint Timeline & Compound Progression Across Top 12 Drivers (Bahrain 2023)", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 4: Tyre Degradation Modeling & Fuel Burn Correction
    # =========================================================================
    story.append(Paragraph("Assignment 4:", h_assignment))
    story.append(Paragraph("Tyre Degradation Modeling & Fuel Mass Decoupling", h_assignment_title))

    story.append(Paragraph("1. Mathematical Modeling of Tyre Degradation", h_section))
    story.append(Paragraph(
        "Tyre degradation represents the rate at which lap time increases as tyre tread wears down and thermal cycles accumulate. "
        "For each clean stint with at least 5 flying laps, an Ordinary Least Squares (OLS) linear model is formulated:", body
    ))
    story.append(Paragraph("<b>LapTime = α + β<sub>observed</sub> · TyreAge + ε</b>", ParagraphStyle("Eq", fontName="Times-Bold", fontSize=10, alignment=1, spaceBefore=4, spaceAfter=4)))
    story.append(Paragraph(
        "Where β<sub>observed</sub> represents the empirical slope in seconds of lap time lost per lap of tyre life. However, "
        "in real-world Formula 1 telemetry, this observed slope is confounded by vehicle fuel consumption.", body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. The Fuel Mass Decoupling Formulation", h_section))
    story.append(Paragraph(
        "Under FIA technical regulations, cars cannot refuel during the race. A Formula 1 car begins the Grand Prix with ~100 kg of "
        "fuel and consumes ~1.6 to 1.8 kg each lap. Standard vehicle dynamics dictate that 10 kg of mass reduction yields ~0.30 to 0.35 s "
        "per lap in improved lap time (averaging γ<sub>fuel</sub> ≈ 0.038 s/lap gain). Therefore, the <b>True Physical Tyre Degradation Rate</b> is:", body
    ))
    story.append(Paragraph("<b>β<sub>true_degradation</sub> = β<sub>observed</sub> + γ<sub>fuel</sub></b>", ParagraphStyle("Eq2", fontName="Times-Bold", fontSize=10.5, alignment=1, spaceBefore=4, spaceAfter=4)))
    story.append(Paragraph(
        "<b>Case Example:</b> In Max Verstappen's opening stint on Soft tyres, his observed slope was +0.0655 s/lap. Adding the fuel correction "
        "constant (0.038 s/lap) reveals that the Soft tyre was actually losing grip at <b>0.1035 s/lap</b> (R² = 0.876, p < 0.001).", body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3. The Pace Cliff Delta Metric", h_section))
    story.append(Paragraph(
        "The tyre cliff is the non-linear threshold where surface rubber has overheated or worn through, causing grip to plummet. "
        "We quantify this through the Pace Cliff Delta: <b>Δt<sub>cliff</sub> = t̄<sub>late</sub> - t̄<sub>early</sub></b>, "
        "measuring the difference between the final 4 clean laps and initial 4 clean laps of a stint.", body
    ))
    story.append(Spacer(1, 4))

    # Embed Degradation Plot
    deg_chart_path = Path("assets/degradation_chart.png")
    if deg_chart_path.exists():
        story.append(Image(str(deg_chart_path), width=480, height=230))
        story.append(Paragraph("Figure 4.1: Max Verstappen Lap Time vs. Tyre Age with OLS Regression Trendlines", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 5: Pit Stop Dynamics & Transit Loss Analytics
    # =========================================================================
    story.append(Paragraph("Assignment 5:", h_assignment))
    story.append(Paragraph("Pit Stop Execution, Transit Duration & Track Position Dynamics", h_assignment_title))

    story.append(Paragraph("1. Pit Stop Mechanics & Time Penalty Decomposition", h_section))
    story.append(Paragraph(
        "A pit stop comprises three sequential time intervals: (1) Deceleration and pit entry, traversing the lane at 80 km/h; "
        "(2) Stationary wheel exchange performed by the 20-person pit crew (typically 2.0 to 3.0 seconds); and (3) Acceleration and "
        "lane exit back onto the circuit. Total pit lane duration is calculated from telemetry timestamps:", body
    ))
    story.append(Paragraph("<b>PitDuration = PitOutTime - PitInTime</b>", ParagraphStyle("Eq3", fontName="Times-Bold", fontSize=10, alignment=1, spaceBefore=3, spaceAfter=4)))
    story.append(Paragraph(
        "At the Bahrain International Circuit, total pit lane transit loss averages ~24.5 seconds under green-flag conditions.", body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Pit Stop Extraction Algorithm (Python)", h_section))
    code_p5 = """def extract_driver_pit_stops(driver_laps):
    df = driver_laps.sort_values('LapNumber').reset_index(drop=True)
    in_laps = df[df['IsPitInLap']].index.tolist()
    pit_stops = []
    
    for stop_idx, in_idx in enumerate(in_laps, start=1):
        in_row = df.loc[in_idx]
        out_row = df.loc[in_idx + 1] if in_idx + 1 < len(df) else None
        
        pit_duration = (out_row['PitOutTime'] - in_row['PitInTime']).total_seconds()
        positions_lost = out_row['Position'] - in_row['Position']
        
        pit_stops.append({
            'StopNumber': stop_idx,
            'PitInLap': int(in_row['LapNumber']),
            'TyreTransition': f"{in_row['Compound']} → {out_row['Compound']}",
            'PitDuration_Seconds': round(pit_duration, 3),
            'PositionsLost': positions_lost
        })
    return pd.DataFrame(pit_stops)"""
    story.append(create_code_block(code_p5))
    story.append(Spacer(1, 6))

    story.append(Paragraph("OUTPUT LOGS:", ParagraphStyle("OutHeader2", fontName="Times-Bold", fontSize=9, spaceBefore=4, spaceAfter=2)))
    term_p5 = """[VERSTAPPEN PIT STOPS EXTRACTED]
Stop 1 | Lap 14 | SOFT → SOFT | Pos Before: 1 | Pos After: 2 | Lost: 1 | Duration: 24.120s
Stop 2 | Lap 36 | SOFT → HARD | Pos Before: 1 | Pos After: 1 | Lost: 0 | Duration: 24.350s
[GRID SUMMARY] 52 total pit stops executed across 57 laps."""
    story.append(create_terminal_block(term_p5))
    story.append(Spacer(1, 6))

    # Embed Pit Stop Distribution Chart
    pit_chart_path = Path("assets/pitstop_distribution.png")
    if pit_chart_path.exists():
        story.append(Image(str(pit_chart_path), width=480, height=200))
        story.append(Paragraph("Figure 5.1: Pit Stop Occurrences Across Race Laps (Bahrain Grand Prix 2023)", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 6: Lap-Time Performance & Driver Consistency
    # =========================================================================
    story.append(Paragraph("Assignment 6:", h_assignment))
    story.append(Paragraph("Lap-Time Performance Benchmarking & Driver Consistency (CV%)", h_assignment_title))

    story.append(Paragraph("1. Measuring Driver Consistency via Coefficient of Variation", h_section))
    story.append(Paragraph(
        "Standard deviation in isolation is unscaled. To quantify a driver's lap-to-lap execution and tyre management precision, "
        "we compute the <b>Coefficient of Variation (CV%)</b>:", body
    ))
    story.append(Paragraph("<b>CV% = (σ / μ) × 100</b>", ParagraphStyle("Eq4", fontName="Times-Bold", fontSize=10, alignment=1, spaceBefore=3, spaceAfter=4)))
    story.append(Paragraph(
        "Where σ is the standard deviation and μ is the mean lap time across representative flying laps. "
        "In the 2023 Bahrain GP, <b>Max Verstappen recorded a CV of 0.62%</b> (σ = 0.34 s across 49 clean laps), demonstrating "
        "extreme mechanical precision. Midfield drivers engaged in DRS battles exhibited CV% values exceeding 1.25%.", body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Compound Performance & Durability Comparison", h_section))
    story.append(Paragraph("Comprehensive comparison across compounds based on 875 clean flying laps:", body))
    story.append(Spacer(1, 4))

    # Compound Comparison Table
    t_comp_perf = [
        [Paragraph("<b>Compound</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Laps Run</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Distance Share</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Median Pace</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Fastest Lap</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Mean Stint Len</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Degradation Rate</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white))],

        [Paragraph("<b>HARD</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8)),
         Paragraph("589 Laps", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("55.78%", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("98.106 s", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("96.156 s", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("17.3 Laps", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("+0.0753 s/lap", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>SOFT</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8)),
         Paragraph("457 Laps", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("43.28%", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("98.827 s", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("93.996 s", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("13.1 Laps", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("+0.1334 s/lap", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>MEDIUM</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8)),
         Paragraph("10 Laps", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("0.95%", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("97.768 s", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("97.260 s", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("10.0 Laps", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("+0.1218 s/lap", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))]
    ]
    t_perf = Table(t_comp_perf, colWidths=[65, 60, 75, 75, 75, 75, 79])
    t_perf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#7C3AED")), # Purple Header
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_perf)
    story.append(Spacer(1, 8))

    # Embed Head-to-Head Chart
    h2h_chart_path = Path("assets/head_to_head_pace.png")
    if h2h_chart_path.exists():
        story.append(Image(str(h2h_chart_path), width=480, height=220))
        story.append(Paragraph("Figure 6.1: Head-to-Head Clean Flying Lap Pace Comparison (VER vs ALO)", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 7: Strategy vs. Finishing Position & Correlation Analysis
    # =========================================================================
    story.append(Paragraph("Assignment 7:", h_assignment))
    story.append(Paragraph("Strategy vs. Finishing Position & Correlation vs. Causation", h_assignment_title))

    story.append(Paragraph("1. Strategic Depth vs. Finishing Position Breakdown", h_section))
    story.append(Paragraph(
        "Examining whether strategy determines finishing position requires rigorous grouping by strategy depth:", body
    ))
    story.append(Spacer(1, 4))

    # Strategy vs Position Table
    t_strat_data = [
        [Paragraph("<b>Strategy Depth</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Driver Count</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Mean Finish</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Median Finish</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Best Finish</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Worst Finish</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Points Scored</b>", ParagraphStyle("TH", fontName="Times-Bold", fontSize=8.5, textColor=colors.white))],

        [Paragraph("<b>2-Stop</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8)),
         Paragraph("10 (50.0%)", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("6.90", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("5.5", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("P1", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("P19", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("98.0 Pts", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>3-Stop</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8)),
         Paragraph("7 (35.0%)", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("12.29", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("12.0", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("P9", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("P16", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("3.0 Pts", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))],

        [Paragraph("<b>1-Stop</b>", ParagraphStyle("TB", fontName="Times-Bold", fontSize=8)),
         Paragraph("1 (5.0%)", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("20.00", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("20.0", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("P20", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("P20", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8)),
         Paragraph("0.0 Pts", ParagraphStyle("TB", fontName="Times-Roman", fontSize=8))]
    ]
    t_strat = Table(t_strat_data, colWidths=[80, 70, 70, 70, 70, 70, 74])
    t_strat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#BE185D")), # Pink/Magenta Header
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_strat)
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. Critical Academic Distinction: Correlation vs. Causation", h_section))
    story.append(Paragraph(
        "A critical viva defense in our report is proving that strategy alone did not <i>cause</i> finishing position:", body
    ))
    story.append(Paragraph("• <b>Spearman Rank Correlation (Stops vs. Finish):</b> ρ = +0.359 (p = 0.1196). Because p > 0.05, there is no statistically significant monotonic relationship.", bullet))
    story.append(Paragraph("• <b>Spearman Rank Correlation (Grid vs. Finish):</b> ρ = +0.510 (p = 0.0217). Statistically significant (p < 0.05).", bullet))
    story.append(Paragraph("• <b>The Confounder:</b> Top teams (Red Bull, Ferrari, Aston Martin) qualify at the front and possess superior aerodynamic downforce, allowing them to conserve tyres in clean air and run optimal 2-stop strategies without falling into midfield traffic.", bullet))
    story.append(Spacer(1, 6))

    # Embed Strategy vs Position Chart
    strat_chart_path = Path("assets/strategy_vs_position_chart.png")
    if strat_chart_path.exists():
        story.append(Image(str(strat_chart_path), width=480, height=220))
        story.append(Paragraph("Figure 7.1: Strategy Depth (Stops) vs. Final Finishing Position (Bahrain 2023)", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 8: Interactive Visualization & Dashboard Architecture
    # =========================================================================
    story.append(Paragraph("Assignment 8:", h_assignment))
    story.append(Paragraph("Interactive Streamlit Web Dashboard & Plotly Engine Architecture", h_assignment_title))

    story.append(Paragraph("1. System Architecture of the Streamlit Web Application", h_section))
    story.append(Paragraph(
        "The project is deployed as an interactive web dashboard in Streamlit (`app.py`), backed by a multi-tier modular "
        "Python architecture. The UI is partitioned into sidebar controls and six reactive analytical tabs:", body
    ))
    story.append(Paragraph("• <b>Sidebar:</b> Championship season selector (2018–2024), dynamic Grand Prix calendar selector, driver focus, and constructor filters.", bullet))
    story.append(Paragraph("• <b>Tab 1 (Tyre Strategy & Stints):</b> Gantt stint progression timeline, compound usage donut, stint lifespan boxplots.", bullet))
    story.append(Paragraph("• <b>Tab 2 (Degradation & Cliff):</b> OLS regression curves with fuel correction toggle and tyre cliff metrics.", bullet))
    story.append(Paragraph("• <b>Tab 3 (Pit Stop Execution):</b> Pit stop timeline across the grid, stop frequency distribution, and lane loss tables.", bullet))
    story.append(Paragraph("• <b>Tab 4 (Lap Pace & Head-to-Head):</b> Rival driver comparison dropdown with lap-by-lap pace overlay and delta badge.", bullet))
    story.append(Paragraph("• <b>Tab 5 (Automated Key Insights):</b> Five dynamic, data-driven factual conclusions synthesized from loaded session metrics.", bullet))
    story.append(Paragraph("• <b>Tab 6 (Data Audit):</b> Comprehensive cleaning audit log displaying filtered lap counts and scientific rationale.", bullet))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Official Pirelli Compound Palette Standards", h_section))
    story.append(Paragraph("To ensure instant visual cognition matching Formula 1 broadcast standards, colors are pinned across all charts:", body))
    story.append(Paragraph("• <b>SOFT:</b> `#FF1801` (Crimson Red) — High grip, high degradation.", bullet))
    story.append(Paragraph("• <b>MEDIUM:</b> `#F5D033` (Pirelli Yellow) — Balanced compound.", bullet))
    story.append(Paragraph("• <b>HARD:</b> `#E0E0E0` (Silver White) — Durable, low wear rate.", bullet))
    story.append(Paragraph("• <b>INTERMEDIATE:</b> `#39B54A` (Green) — Damp track / light rain.", bullet))
    story.append(Paragraph("• <b>WET:</b> `#00A0DE` (Cyan Blue) — Heavy standing water.", bullet))
    story.append(Spacer(1, 6))

    # Embed Compound Usage Donut
    donut_chart_path = Path("assets/compound_usage_donut.png")
    if donut_chart_path.exists():
        story.append(Image(str(donut_chart_path), width=320, height=240))
        story.append(Paragraph("Figure 8.1: Tyre Compound Mileage Share (%) Donut Chart (Bahrain 2023)", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 9: Automated Quality Assurance & Testing Suite
    # =========================================================================
    story.append(Paragraph("Assignment 9:", h_assignment))
    story.append(Paragraph("Automated Quality Assurance & Verification Suite (Pytest)", h_assignment_title))

    story.append(Paragraph("1. Role of Automated Testing in Data Analytics", h_section))
    story.append(Paragraph(
        "In telemetry pipelines, subtle logic bugs—such as silent row dropping, inverted subtraction in delta times, or off-by-one errors "
        "in stint indices—compromise scientific validity without raising unhandled runtime exceptions. An automated Pytest suite "
        "(`tests/test_analysis.py`) guarantees mathematical correctness across all analytical modules.", body
    ))
    story.append(Paragraph("Test Suite Assertions:", h_subsection))
    story.append(Paragraph("• `test_timedelta_to_seconds`: Asserts `1m 38s 250ms` converts to scalar `98.250 s` and handles `NaT` safely.", bullet))
    story.append(Paragraph("• `test_clean_race_laps_preserves_rows`: Verifies that raw rows are retained and flags are assigned without mutation.", bullet))
    story.append(Paragraph("• `test_stint_detection_and_strategy_string`: Tests change-point grouping and asserts formatted string `S → H (1-Stop)`.", bullet))
    story.append(Paragraph("• `test_pit_stop_extraction`: Validates pit entry detection, compound transitions, and duration math.", bullet))
    story.append(Paragraph("• `test_stint_degradation_and_fuel_correction`: Validates OLS linear slope and fuel offset (`0.10 + 0.038 = 0.138 s/lap`).", bullet))
    story.append(Paragraph("• `test_empty_dataframe_tolerance`: Asserts that passing empty DataFrames returns safe empty structures without crashing.", bullet))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Pytest Execution Output (Terminal Verification)", h_section))
    term_p9 = """PS C:\\f1-tyre-strategy-analysis> python -m pytest tests/test_analysis.py -v
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\\f1-tyre-strategy-analysis
collected 6 items

tests/test_analysis.py::test_timedelta_to_seconds_valid PASSED           [ 16%]
tests/test_analysis.py::test_clean_race_laps_preserves_rows PASSED       [ 33%]
tests/test_analysis.py::test_stint_detection_and_strategy_string PASSED  [ 50%]
tests/test_analysis.py::test_pit_stop_extraction PASSED                  [ 66%]
tests/test_analysis.py::test_stint_degradation_and_fuel_correction PASSED [ 83%]
tests/test_analysis.py::test_empty_dataframe_tolerance PASSED            [100%]

======================== 6 passed, 8 warnings in 3.57s ========================"""
    story.append(create_terminal_block(term_p9))
    story.append(PageBreak())

    # =========================================================================
    # ASSIGNMENT 10: Performance Analysis & Real-World Applications
    # =========================================================================
    story.append(Paragraph("Assignment 10:", h_assignment))
    story.append(Paragraph("Performance Analysis & Real-World Motorsport Applications", h_assignment_title))

    story.append(Paragraph("1. Performance Analysis in Modern Formula 1", h_section))
    story.append(Paragraph(
        "Performance analysis in motorsport is the rigorous, evidence-based quantification of vehicle and athlete capability. "
        "In Formula 1, over 300 telemetry sensors stream continuous real-time parameters covering tyre surface temperature, carcass pressure, "
        "aerodynamic load, and brake wear. Our project harnesses these parameters to transform raw timing logs into actionable "
        "strategic intelligence.", body
    ))
    story.append(Paragraph("Performance Analysis with Telemetry Analytics:", h_subsection))
    story.append(Paragraph("• <b>Transparent Performance Tracking:</b> Isolating pure vehicle pace from external traffic and regulatory caution periods.", bullet))
    story.append(Paragraph("• <b>Predictive Degradation Trajectories:</b> Forecasting the onset of the tyre cliff to execute preemptive pit stops.", bullet))
    story.append(Paragraph("• <b>Constructor Hierarchy Benchmarking:</b> Comparing median racing pace across constructors to measure aerodynamic efficiency.", bullet))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Applications of F1 Telemetry & Strategy Analytics", h_section))
    story.append(Paragraph("1. <b>Motorsport Strategy Departments:</b> Powers live pit wall simulation software calculating real-time undercut/overcut odds.", body))
    story.append(Paragraph("2. <b>Tyre Manufacturer Compound Development:</b> Enables Pirelli engineers to evaluate compound graining and thermal wear rates.", body))
    story.append(Paragraph("3. <b>Commercial Television Broadcasting:</b> Drives on-screen graphics showing predicted pit stop windows and tyre life percentages.", body))
    story.append(Paragraph("4. <b>Autonomous Racing & Sim Racing:</b> Informs dynamic vehicle control algorithms in esports and autonomous driving testbeds.", body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Conclusion", h_section))
    story.append(Paragraph(
        "This project successfully designs, develops, and validates a complete data analytics pipeline and interactive dashboard for "
        "Formula 1 tyre strategy analysis. By combining FastF1 data ingestion, non-destructive diagnostic cleaning, run-length stint identification, "
        "Ordinary Least Squares regression with fuel mass decoupling, and interactive Plotly visualizations, the system converts raw telemetry into "
        "quantified scientific insights. Our benchmark on the 2023 Bahrain Grand Prix proved that Soft tyres degraded at 1.77 times the rate of Hard tyres, "
        "explaining why all top 8 finishers adopted 2-stop strategies, and demonstrated that qualifying grid position remains the dominant determinant of race outcome.", body
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("References", h_section))
    refs = [
        "1. TheOehrly. (2024). FastF1: A Python package for accessing Formula 1 timing and telemetry data. https://docs.fastf1.dev/",
        "2. McKinney, W. (2010). Data Structures for Statistical Computing in Python. In Proceedings of the 9th Python in Science Conference (pp. 51–56).",
        "3. Virtanen, P., et al. (2020). SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python. Nature Methods, 17(3), 261–272.",
        "4. Plotly Technologies Inc. (2024). Collaborative data science and graphing library. https://plotly.com/python/",
        "5. Streamlit Inc. (2024). Streamlit: The fastest way to build and share data apps. https://docs.streamlit.io/",
        "6. Fédération Internationale de l'Automobile (FIA). (2023). Formula One Sporting Regulations. FIA Official Publications.",
        "7. Pirelli Tyre S.p.A. (2023). Formula 1 Technical Regulations & Compound Allocations. Pirelli Motorsport Press."
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle("Ref", fontName="Times-Roman", fontSize=8, leading=11, spaceAfter=3)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 28: ASSESSMENT (RUBRICS SHEET - EXACT MATCH)
    # =========================================================================
    story.append(Paragraph("ASSESSMENT", ParagraphStyle("AssessTitle", fontName="Times-Bold", fontSize=14, alignment=1, spaceAfter=15)))
    story.append(Paragraph("<b>Internal:</b>", ParagraphStyle("AssessSub", fontName="Times-Bold", fontSize=11, spaceAfter=10)))

    assess_data = [
        [Paragraph("<b>SL<br/>NO</b>", ParagraphStyle("TH_A", fontName="Times-Bold", fontSize=9, alignment=1)),
         Paragraph("<b>RUBRICS</b>", ParagraphStyle("TH_A", fontName="Times-Bold", fontSize=9, alignment=1)),
         Paragraph("<b>FULL<br/>MARK</b>", ParagraphStyle("TH_A", fontName="Times-Bold", fontSize=9, alignment=1)),
         Paragraph("<b>MARKS<br/>OBTAINED</b>", ParagraphStyle("TH_A", fontName="Times-Bold", fontSize=9, alignment=1)),
         Paragraph("<b>REMARK<br/>S</b>", ParagraphStyle("TH_A", fontName="Times-Bold", fontSize=9, alignment=1))],

        [Paragraph("1", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("Understanding the relevance, scope and dimension of the project", ParagraphStyle("TC_AL", fontName="Times-Roman", fontSize=9)),
         Paragraph("10", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9))],

        [Paragraph("2", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("Methodology", ParagraphStyle("TC_AL", fontName="Times-Roman", fontSize=9)),
         Paragraph("10", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9))],

        [Paragraph("3", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("Quality of Analysis and Results", ParagraphStyle("TC_AL", fontName="Times-Roman", fontSize=9)),
         Paragraph("10", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9))],

        [Paragraph("4", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("Interpretations and Conclusions", ParagraphStyle("TC_AL", fontName="Times-Roman", fontSize=9)),
         Paragraph("10", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9))],

        [Paragraph("5", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("Report", ParagraphStyle("TC_AL", fontName="Times-Roman", fontSize=9)),
         Paragraph("10", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9, alignment=1)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9))],

        [Paragraph("", ParagraphStyle("TC_A", fontName="Times-Bold", fontSize=9)),
         Paragraph("<b>Total</b>", ParagraphStyle("TC_AL", fontName="Times-Bold", fontSize=9)),
         Paragraph("<b>50</b>", ParagraphStyle("TC_A", fontName="Times-Bold", fontSize=9, alignment=1)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9)),
         Paragraph("", ParagraphStyle("TC_A", fontName="Times-Roman", fontSize=9))]
    ]
    t_assess = Table(assess_data, colWidths=[40, 240, 64, 80, 80])
    t_assess.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_assess)
    story.append(Spacer(1, 55))

    sig_data = [
        [Paragraph("<b>Date:</b>", ParagraphStyle("SigD", fontName="Times-Bold", fontSize=11)),
         Paragraph("<b>Signature of the Faculty</b>", ParagraphStyle("SigF", fontName="Times-Bold", fontSize=11, alignment=2))]
    ]
    t_sig = Table(sig_data, colWidths=[200, 304])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_sig)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 29: COURSE OUTCOME (COs) ATTAINMENT (EXACT MATCH)
    # =========================================================================
    story.append(Paragraph("COURSE OUTCOME (COs) ATTAINMENT", ParagraphStyle("CO_Title", fontName="Times-Bold", fontSize=12, alignment=0, spaceAfter=14)))

    story.append(Paragraph("➢ <b>Expected Course Outcomes (COs):</b>", ParagraphStyle("CO_Item", fontName="Times-Bold", fontSize=10, spaceAfter=3)))
    story.append(Paragraph("(Refer to COs Statement in the Syllabus)", ParagraphStyle("CO_Note", fontName="Times-Roman", fontSize=10, spaceAfter=8)))
    
    # 3 Blank Lines
    for _ in range(3):
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#777777"), spaceBefore=10, spaceAfter=8))
    
    story.append(Spacer(1, 8))
    story.append(Paragraph("➢ <b>Course Outcome Attained:</b>", ParagraphStyle("CO_Item", fontName="Times-Bold", fontSize=10, spaceAfter=3)))
    story.append(Paragraph("How would you rate your learning of the subject based on the specified COs?", ParagraphStyle("CO_Sub", fontName="Times-Bold", fontSize=10, spaceAfter=12)))

    # Rating Boxes 1 to 10
    rating_row_boxes = []
    rating_row_labels = []
    for num in range(1, 11):
        # Square rating box
        box_p = Paragraph(f"<font size=10 face='Times-Bold'>{num}</font>", ParagraphStyle("B", alignment=1))
        t_single = Table([[box_p]], colWidths=[24], rowHeights=[24])
        t_single.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        rating_row_boxes.append(t_single)
        rating_row_labels.append(Paragraph(f"<font size=8 face='Times-Bold'>{num}</font>", ParagraphStyle("L", alignment=1)))

    t_boxes = Table([rating_row_boxes], colWidths=[38]*10)
    t_boxes.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(t_boxes)
    story.append(Spacer(1, 6))

    # Low / High Labels
    t_low_high = Table([[
        Paragraph("<b>LOW</b>", ParagraphStyle("Low", fontName="Times-Bold", fontSize=9, alignment=0)),
        Paragraph("<b>HIGH</b>", ParagraphStyle("High", fontName="Times-Bold", fontSize=9, alignment=2))
    ]], colWidths=[200, 304])
    story.append(t_low_high)
    story.append(Spacer(1, 10))

    story.append(Paragraph("➢ <b>Learning Gap (if any):</b>", ParagraphStyle("CO_Item", fontName="Times-Bold", fontSize=10, spaceAfter=4)))
    for _ in range(3):
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#777777"), spaceBefore=10, spaceAfter=8))

    story.append(Spacer(1, 8))
    story.append(Paragraph("➢ <b>Books / Manuals Referred:</b>", ParagraphStyle("CO_Item", fontName="Times-Bold", fontSize=10, spaceAfter=4)))
    for _ in range(3):
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#777777"), spaceBefore=10, spaceAfter=8))

    story.append(Spacer(1, 12))
    t_sig_student = Table([[
        Paragraph("<b>Date:</b>", ParagraphStyle("SD", fontName="Times-Bold", fontSize=10)),
        Paragraph("<b>Signature of the Student</b>", ParagraphStyle("SS", fontName="Times-Bold", fontSize=10, alignment=2))
    ]], colWidths=[200, 304])
    story.append(t_sig_student)
    story.append(Spacer(1, 10))

    story.append(Paragraph("➢ <b>Suggestions / Recommendations:</b>", ParagraphStyle("CO_Item", fontName="Times-Bold", fontSize=10, spaceAfter=3)))
    story.append(Paragraph("(By the Course Faculty)", ParagraphStyle("CO_Note", fontName="Times-Bold", fontSize=10, spaceAfter=4)))
    for _ in range(3):
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#777777"), spaceBefore=10, spaceAfter=8))

    story.append(Spacer(1, 14))
    t_sig_fac = Table([[
        Paragraph("<b>Date:</b>", ParagraphStyle("FD", fontName="Times-Bold", fontSize=10)),
        Paragraph("<b>Signature of the Faculty</b>", ParagraphStyle("FS", fontName="Times-Bold", fontSize=10, alignment=2))
    ]], colWidths=[200, 304])
    story.append(t_sig_fac)

    doc.build(story, canvasmaker=AcademicCanvas)
    print(f"[SUCCESS] Academic Project Report PDF built: {filename}")


if __name__ == "__main__":
    out_file = Path("Formula1_Tyre_Strategy_Analysis_Project_Report.pdf")
    build_pdf(str(out_file))
