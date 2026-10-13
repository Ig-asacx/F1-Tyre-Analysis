# Academic Project Report: Formula 1 Tyre Strategy Analysis Using Python

**Course Code:** CUTM1018 - Data Analytics  
**Department:** Computer Science & Engineering, School of Engineering and Technology (SOET)  
**Institution:** Centurion University of Technology and Management, Bhubaneswar  

**Project Title:** Formula 1 Tyre Strategy Analysis Using Python  
**Submitted By:**  
1. **Pratik Raj** — Reg. No: `250301120219`  
2. **Swayam Suraj Nayak** — Reg. No: `250301120227`  
3. **Debashish Pradhan** — Reg. No: `250301120238`  

**Project Supervisor:** Sabyasachi Mohanty  

---

## Abstract

This project analyzes historical Formula 1 race telemetry using Python to study how tyre strategy affects race performance. Tyre compound choice, stint length, and pit-stop timing are among the most decisive factors in a race outcome. By extracting official FIA session timing feeds through the FastF1 library, this research designs an end-to-end data processing pipeline that converts raw lap records into structured analytical models. 

The pipeline filters non-representative laps (pit in-laps, pit out-laps, safety cars, track-limit deletions) using explicit non-destructive diagnostic flags. It programmatically identifies continuous tyre stints via change-point detection algorithms and synthesizes strategy shorthand sequences (e.g. `S → S → H`). Mathematical degradation is modeled using Ordinary Least Squares (OLS) linear regression coupled with vehicle fuel burn corrections ($\approx 0.038\text{ s/lap}$). 

Tested against the 2023 Bahrain Grand Prix, the system quantifies the speed vs. durability trade-off between Soft, Medium, and Hard compounds, confirming that the Soft compound degraded at $1.77\times$ the rate of the Hard compound. Furthermore, statistical correlation analysis reveals that while a 2-stop strategy was strongly associated with top-8 finishing positions, qualifying grid position remains the primary predictor of final race classification ($\rho = 0.510, p = 0.0217$). An interactive Streamlit web dashboard is deployed to provide real-time visual exploration of stint timelines, degradation curves, and head-to-head driver telemetry.

---

## 1. Introduction

Formula 1 represents the pinnacle of international motorsport and high-velocity telemetry engineering. While public attention often centers on driver reflexes and engine horsepower, strategic tyre management is frequently the ultimate determinant of victory. Modern Formula 1 regulations mandate that every driver must use at least two distinct dry-weather slick tyre compounds during a dry Grand Prix, requiring at least one mandatory pit stop.

Teams face complex multi-variable optimization challenges:
- Softer tyre compounds offer superior chemical grip and faster cornering speeds but suffer rapid thermal wear and surface degradation.
- Harder tyre compounds offer mechanical durability and extended stint lifespans but produce slower lap times on initial laps.
- Entering the pit lane incurs a static time penalty of 20 to 25 seconds due to the mandatory pit lane speed limiter ($80\text{ km/h}$).

This project applies computerized data analytics, statistical modeling, and interactive visualization to unpack these complex dynamics from real-world telemetry data.

---

## 2. Problem Statement

Raw timing data provided by motorsport organizers cannot be analyzed directly without sophisticated data engineering:
1. **Pit Lane Distortions:** Entering and exiting the pit lane inflates lap times by 15 to 25 seconds. Treating these laps as standard racing laps distorts pace averages and creates false degradation spikes.
2. **Safety Car & Delta Interventions:** Caution periods force cars to reduce speed by ~40%.
3. **Vehicle Mass Dynamics (The Fuel Effect):** Formula 1 cars start with $\approx 100\text{ kg}$ of fuel and burn $\approx 1.7\text{ kg}$ per lap. The resulting reduction in vehicle weight improves lap times by $\approx 0.035 - 0.050\text{ s/lap}$, masking the true physical degradation of the tyres.
4. **Data Loss via Naive Deletion:** Standard cleaning techniques (`df.dropna()`) destroy chronological continuity, breaking stint tracking and pit duration calculations.

---

## 3. Project Objectives

1. Ingest official F1 session timing data directly from FastF1 with local disk caching.
2. Develop a non-destructive data cleaning pipeline using boolean diagnostic flags.
3. Formulate an automated stint identification algorithm using change-point detection.
4. Model mathematical tyre degradation rates ($\text{seconds of lap time lost per lap of tyre life}$) with fuel burn correction.
5. Extract pit stop events, transit loss durations, and track position transitions.
6. Evaluate statistical correlations between strategic variables and classified finishing positions ($P1–P20$).
7. Deploy an interactive web dashboard in Streamlit featuring responsive Plotly visualizations.

---

## 4. Dataset Description

The dataset is obtained from the official Formula 1 live timing and telemetry feeds via the **FastF1** Python API. For the primary benchmark case study, the **2023 Bahrain Grand Prix (Round 1)** was selected:
- **Total Laps:** 57 Laps ($308.238\text{ km}$).
- **Competitors:** 20 Drivers across 10 Constructors.
- **Raw Lap Records:** 1,056 individual lap records.
- **Key Attributes:** `Driver`, `LapNumber`, `LapTime`, `Sector1Time`, `Sector2Time`, `Sector3Time`, `Compound`, `TyreLife`, `Stint`, `PitInTime`, `PitOutTime`, `TrackStatus`, `Position`, `Deleted`.

---

## 5. Data Preprocessing & Cleaning Pipeline

To ensure absolute statistical integrity without losing chronological continuity, the pipeline avoids row deletion, instead tagging each lap with explicit diagnostic flags:

```text
Raw Laps (1,056)
   │
   ├── 1. Timedelta Conversion ───> LapTime_Seconds (float, millisecond precision)
   ├── 2. Pit In-Lap Check     ───> IsPitInLap = PitInTime.notna() (52 laps flagged)
   ├── 3. Pit Out-Lap Check    ───> IsPitOutLap = PitOutTime.notna() (50 laps flagged)
   ├── 4. Grid Launch Check    ───> IsStartLap = LapNumber == 1 (20 laps flagged)
   ├── 5. Caution Periods      ───> IsGreenFlag = TrackStatus == '1' (77 laps flagged)
   ├── 6. Track Limits Check   ───> IsDeletedLap = Deleted == True
   └── 7. IQR Outlier Filter   ───> IsOutlierPace (14 laps flagged)
   │
   ▼
Representative Flying Laps: 875 laps (82.86% of session)
```

---

## 6. Algorithms & Mathematical Logic

### A. Run-Length Stint Detection Algorithm
Stint transitions are detected by evaluating the boolean condition:
$$\text{Transition}_t = (\text{IsPitOutLap}_t == \text{True}) \lor (\text{Compound}_t \neq \text{Compound}_{t-1})$$
Taking the cumulative sum assigns a unique Stint ID to each contiguous segment, correctly capturing pit stops even when the driver fits the same tyre compound (e.g. Soft $\rightarrow$ Soft).

### B. Tyre Degradation Modeling with Fuel Correction
For each stint with $\ge 5$ clean laps, an Ordinary Least Squares (OLS) regression line is fitted:
$$\text{LapTime} = \alpha + \beta_{\text{observed}} \cdot \text{TyreAge} + \epsilon$$
Because the car gains $\gamma_{\text{fuel}} \approx 0.038\text{ s/lap}$ from fuel burn-off, the **true physical tyre degradation rate** is:
$$\beta_{\text{true\_degradation}} = \beta_{\text{observed}} + \gamma_{\text{fuel}}$$

### C. The Tyre Cliff Delta
$$\Delta t_{\text{cliff}} = \bar{t}_{\text{late}} - \bar{t}_{\text{early}}$$
Where $\bar{t}_{\text{early}}$ is the mean of the first 4 clean laps and $\bar{t}_{\text{late}}$ is the mean of the final 4 clean laps of a stint.

---

## 7. Experimental Results (Bahrain 2023 Case Study)

### Compound Utilization & Durability
| Compound | Laps Run | Distance Share (%) | Unique Drivers | Mean Stint Length | Max Stint Length | Fuel-Corrected Degradation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **HARD** | 589 | 55.78% | 19 | 17.3 Laps | 29 Laps | $+0.0753\text{ s/lap}$ |
| **SOFT** | 457 | 43.28% | 20 | 13.1 Laps | 22 Laps | $+0.1334\text{ s/lap}$ |
| **MEDIUM**| 10 | 0.95% | 1 | 10.0 Laps | 10 Laps | $+0.1218\text{ s/lap}$ |

### Strategy vs. Finishing Position
- **2-Stop Strategy:** Adopted by 10 drivers (50% of the grid). Mean finish position: **$6.90$** (Median: **$5.5$**). Scored **98 out of 101 points**.
- **3-Stop Strategy:** Adopted by 7 drivers (35% of the grid). Mean finish position: **$12.29$** (Median: **$12.0$**). Scored **3 points**.
- **1-Stop Strategy:** Adopted by 1 driver ($P20$, DNF).

---

## 8. Discussion: Correlation vs. Association vs. Causation

A critical academic insight from this project is the distinction between statistical correlation and motorsport causation:
1. **Pit Stop Correlation:** Spearman rank correlation between stop count and finish position was $\rho = 0.359$ ($p = 0.1196$), which is not statistically significant.
2. **Grid Position Correlation:** Spearman rank correlation between qualifying grid position and finish position was $\rho = 0.510$ ($p = 0.0217$), which is statistically significant.
3. **The Engineering Explanation:** Slower cars engaged in 3-stop strategies because their aerodynamic sliding overheated their tyres in dirty air, not because 3-stop strategies inherently cause slow lap times. Front-running cars possessed superior aerodynamic efficiency, allowing them to conserve tyres in clean air and execute the 2-stop strategy effectively.

---

## 9. Limitations & Future Work

### Limitations
1. Fuel mass consumption is modeled using a constant vehicle physics coefficient ($0.038\text{ s/lap}$) rather than proprietary live mass sensor data.
2. Track evolution (rubber grip laid down over the weekend) is not separated from atmospheric temperature deltas.

### Future Scope
1. Implement machine learning models (Gradient Boosted Trees / Neural Networks) to predict real-time pit entry laps under virtual safety cars.
2. Develop a Monte Carlo race simulation engine to evaluate counter-factual strategy decisions.

---

## 10. Conclusion

This project successfully implements an end-to-end data analytics and telemetry visualization pipeline for Formula 1 tyre strategy analysis. By combining FastF1 data ingestion, non-destructive data cleaning, run-length stint identification, OLS regression with fuel correction, and interactive Streamlit dashboards, the system transforms raw lap telemetry into rigorous scientific insights into the pace vs. durability trade-offs of modern motorsport strategy.

---

## References

1. FastF1 Documentation — TheOehrly, Python Package for F1 Telemetry (`https://docs.fastf1.dev/`)
2. Pandas Documentation — Python Data Analysis Library (`https://pandas.pydata.org/`)
3. SciPy Statistical Documentation — Linear Regression & Rank Correlation (`https://docs.scipy.org/`)
4. Plotly Open Source Graphing Library for Python (`https://plotly.com/python/`)
5. Streamlit Framework Documentation (`https://docs.streamlit.io/`)
6. Official Formula 1 Technical Regulations — Fédération Internationale de l'Automobile (FIA)
