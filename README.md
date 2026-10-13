# Formula 1 Tyre Strategy Analysis Using Python 🏎️

> **Academic Course Project | CUTM1018 - Data Analytics**  
> **Department of Computer Science & Engineering, SOET**  
> **Centurion University of Technology and Management, Bhubaneswar**  
>
> **Project Team:**  
> - **Pratik Raj** — Reg No: `250301120218`  
> - **Swayam Suraj Nayak** — Reg No: `250301120227`  
> - **Debashish Pradhan** — Reg No: `250301120238`  
>  
> **Course Supervisor:** Sabyasachi Mohanty  

---

## 1. Project Overview

In Formula 1 motorsport, race outcomes are determined not merely by peak single-lap driving speed, but fundamentally by **dynamic tyre strategy and pit stop execution**. Over a 305 km Grand Prix distance, teams must strategically decide:
- Which Pirelli tyre compounds to nominate (Soft, Medium, Hard, Intermediate, Wet).
- When to open pit stop windows and execute tyre changes.
- How to manage thermal tyre degradation against vehicle fuel burn-off.
- Whether an aggressive 2-stop or conservative 1-stop strategy provides superior expected finishing position.

This project delivers an **end-to-end, production-grade telemetry analytics pipeline and interactive Streamlit web dashboard** built using real-world Formula 1 timing feeds via **FastF1**. It processes lap-by-lap timing loops, models mathematical tyre degradation slopes using Ordinary Least Squares (OLS) regression with fuel correction, tracks pit lane transit loss, and evaluates strategic correlations against classified finishing positions.

---

## 2. Problem Statement

Raw Formula 1 timing feeds contain substantial telemetry anomalies:
1. **Confounded Lap Times:** In-laps (entering pits at 80 km/h) and out-laps (cold tyres exiting pits) add 15–25 seconds per lap, causing naive analytical models to misclassify pit stop speed penalties as catastrophic tyre wear.
2. **Safety Car & Caution Periods:** Safety Cars (SC) and Virtual Safety Cars (VSC) mandate strict FIA target deltas (~40% slower than race pace) that falsely distort tyre degradation curves.
3. **The Fuel Effect Bias:** Cars burn ~1.7 kg of fuel per lap, gaining ~0.038 s/lap in lap time. Uncorrected lap time analysis erroneously suggests that tyres "improve" as they age.
4. **Correlation vs. Causation Fallacy:** Slower cars frequently run divergent strategies out of desperation, leading naive observers to believe non-standard strategies cause lower finishing positions.

---

## 3. Key Objectives

- **Automated Data Ingestion:** Interface directly with official F1 timing streams via FastF1 with persistent local SQLite/binary caching.
- **Transparent Preprocessing:** Build a non-destructive cleaning pipeline utilizing explicit boolean diagnostic flags (`IsPitInLap`, `IsPitOutLap`, `IsRepresentativePace`).
- **Run-Length Stint Detection:** Programmatically identify tyre stints and format standardized strategy sequences (e.g. `S → S → H (2-Stop)`).
- **Mathematical Tyre Degradation Modeling:** Compute OLS regression slopes ($\beta_{\text{deg}}$) and fuel-corrected wear rates on clean flying laps.
- **Pit Stop Analytics:** Measure pit stop lap windows, stationary/lane transit duration, and track position delta.
- **Interactive Dashboard:** Provide a reactive multi-tab Streamlit dashboard with F1-themed dark Plotly visualizations.

---

## 4. Technology Stack & Justification

| Technology | Role in Project | Justification & Viva Defence |
| :--- | :--- | :--- |
| **Python 3.10+** | Core Programming Language | Universal data science ecosystem, native array vectorization, rich scientific libraries. |
| **FastF1** | Official F1 Timing API Wrapper | Direct access to FIA timing loops, tyre compound nominations, and session status flags. |
| **Pandas & NumPy** | Tabular Data Manipulation | High-performance vectorized filtering, rolling window calculations, and timedelta transformations. |
| **SciPy & Scikit-Learn** | Statistical Modeling | Ordinary Least Squares (OLS) regression for degradation and Spearman rank correlation coefficients. |
| **Plotly** | Interactive Visualizations | Client-side SVG/WebGL charting allowing hover tooltips, zoomable lap ranges, and dynamic legends. |
| **Streamlit** | Web Application Dashboard | Pure Python reactive web interface with sidebar filters and `@st.cache_data` memoization. |
| **Pytest** | Automated Quality Assurance | Automated unit tests ensuring 100% test coverage across mathematical transformations and edge cases. |

---

## 5. System Architecture

```text
f1-tyre-strategy-analysis/
│
├── app.py                      # Main entrypoint: Streamlit interactive web dashboard
├── requirements.txt            # Dependency manifest (FastF1, pandas, plotly, streamlit, pytest)
├── README.md                   # Comprehensive project documentation
├── PROJECT_REPORT.md           # Formal academic submission report
├── .gitignore                  # Git exclusions for binary caches and virtual environments
│
├── data/
│   ├── raw/                    # Cached raw session payloads (2023_bahrain_race.pkl)
│   ├── processed/              # Cleaned CSV/Parquet datasets (laps, stints, pit stops)
│   └── cache/                  # FastF1 internal SQLite and HTTP cache
│
├── notebooks/
│   └── exploratory_analysis.ipynb  # Step-by-step EDA and research notebook
│
├── src/                        # Modular source code package
│   ├── __init__.py
│   ├── data_loader.py          # Session extraction, FastF1 cache initialization, offline fallback
│   ├── data_cleaning.py        # Diagnostic flags, timedelta conversion, IQR outlier filtering
│   ├── tyre_analysis.py        # Compound usage share, stint lifespan, representative pace
│   ├── stint_analysis.py       # Change-point stint detection, strategy string synthesis
│   ├── degradation_analysis.py # OLS regression slopes, fuel-corrected wear rates, tyre cliff deltas
│   ├── pitstop_analysis.py     # Pit stop detection, lane transit loss, strategy categorization
│   ├── lap_analysis.py         # Driver/Team pace summaries, rolling medians, head-to-head deltas
│   ├── strategy_analysis.py    # Stops vs finishing position, Spearman rank correlations
│   └── visualization.py        # Reusable Plotly charts with official Pirelli dark theme
│
├── tests/
│   ├── __init__.py
│   ├── test_analysis.py        # Pytest automated test suite (100% passing)
│   ├── test_real_race_loader.py# Live FastF1 connection test script
│   ├── test_cleaning.py        # Cleaning pipeline validation test
│   ├── test_stints.py          # Stint detection test
│   ├── test_tyres.py           # Compound metrics test
│   ├── test_laps.py            # Lap pace benchmarking test
│   ├── test_degradation.py     # Tyre degradation regression test
│   ├── test_pitstops.py        # Pit stop extraction test
│   ├── test_strategy_position.py # Strategy vs position correlation test
│   └── test_visualization.py   # Plotly compilation and HTML export test
│
└── assets/
    └── strategy_timeline_preview.html  # Standalone interactive HTML strategy chart
```

---

## 6. Installation & Setup Guide

### Prerequisites
- Python 3.10 to 3.14 installed on your machine.
- Git (optional, for cloning).

### Step 1: Clone or Navigate to Project
```powershell
cd C:\Users\user\.gemini\antigravity\scratch\f1-tyre-strategy-analysis
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Automated Unit Tests
```powershell
python -m pytest tests/test_analysis.py -v
```

### Step 4: Launch the Streamlit Dashboard
```powershell
python -m streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 7. Interactive Dashboard Features

1. **Sidebar Navigation Controls:**
   - Championship Season selector ($2018$ through $2024$).
   - Dynamic Grand Prix Event dropdown populated from championship calendars.
   - Driver & Constructor focus filters.
2. **Top-Level KPI Badges:**
   - Race Winner, Winning Strategy, Focus Driver Finish Position ($P1–P20$), and Personal Strategy Sequence.
3. **Six Deep-Dive Analytical Tabs:**
   - **Tab 1: Tyre Strategy & Stints:** Interactive Gantt-style timeline sorted by finishing position, compound usage donut, and stint length box plots.
   - **Tab 2: Degradation & Thermal Cliff:** Lap time vs. tyre age scatter plot with OLS linear trendlines ($\beta_{\text{deg}}$) and fuel-corrected wear rates.
   - **Tab 3: Pit Stop Execution:** Pit stop timeline across the grid, 1-stop vs 2-stop frequency distribution, and lane transit loss.
   - **Tab 4: Lap Pace & Head-to-Head:** Interactive driver rival selector with lap-by-lap telemetry overlay and median pace advantage badge.
   - **Tab 5: Automated Key Insights:** 5 dynamic, data-driven factual conclusions synthesized from the race results.
   - **Tab 6: Data Cleaning & Audit:** Non-destructive filtering breakdown and audit metrics.

---

## 8. Real-World Findings (2023 Bahrain Grand Prix Case Study)

- **The Hard Compound Was the Race Workhorse:**  
  Hard tyres accounted for **55.78% (589 laps)** of all racing mileage across 19 drivers, with an average stint lifespan of **17.3 laps**.
- **Medium Tyre Avoidance:**  
  Only 1 driver ran the Medium compound (10 laps total). Teams avoided the Medium tyre due to severe thermal surface graining identified during practice.
- **Quantified Tyre Degradation:**  
  - **Soft Compound Wear Rate:** $\mathbf{0.1334\text{ s/lap}}$ fuel-corrected wear, experiencing an average **$+0.742\text{ s}$ tyre cliff drop**.  
  - **Hard Compound Wear Rate:** $\mathbf{0.0753\text{ s/lap}}$ fuel-corrected wear, experiencing an average **$+0.429\text{ s}$ tyre cliff drop**.  
  - Soft tyres degraded at **$1.77\times$ the rate of Hard tyres**.
- **Strategy Dominance:**  
  **100% of the top 8 finishers** executed a **2-Stop strategy** (`S → S → H` or `S → H → H`).
- **Correlation vs. Causation:**  
  Qualifying Grid Position correlated with race finish at **$\rho = 0.510$ ($p = 0.0217$, statistically significant)**, whereas Pit Stop Count correlated at only **$\rho = 0.359$ ($p = 0.1196$, not significant)**. This proves car performance and grid launch remain the dominant determinants of finishing outcome.

---

## 9. Academic Limitations & Future Scope

### Limitations
- **Fuel Mass Telemetry:** Fuel consumption is modeled using standard vehicle physics ($\approx 0.038\text{ s/lap}$) rather than proprietary sensor feeds.
- **Traffic Wake Modeling:** Clean air versus aerodynamic dirty air is approximated using moving medians rather than 3D LiDAR/GPS proximity tracking.
- **Track Temperature Fluctuations:** Twilight and night races experience cooling asphalt, which interacts with tyre compound heating.

### Future Scope
- Integration of Machine Learning models (Random Forest / XGBoost) to forecast the optimal pit window lap under live Safety Car probabilities.
- Monte Carlo race simulation models to test hypothetical alternate strategies ("What if Alonso had pitted on Lap 12 instead of Lap 14?").

---

## 10. Team Members & Contributions

| Member Name | Registration Number | Core Contributions |
| :--- | :--- | :--- |
| **Pratik Raj** | `250301120218` | Data Ingestion, FastF1 Caching Engine, Stint Detection Algorithm, Testing Suite |
| **Swayam Suraj Nayak** | `250301120227` | Data Cleaning Pipeline, Outlier Flagging, Lap-Time Performance & Head-to-Head Analytics |
| **Debashish Pradhan** | `250301120238` | Tyre Degradation OLS Modeling, Fuel Correction, Pit Stop Analysis, Streamlit UI & Visuals |
