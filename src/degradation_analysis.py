"""
src/degradation_analysis.py
===========================
Formula 1 Tyre Degradation & Thermal Wear Modeling Engine.

Tyre degradation is the progressive loss of grip and pace as tyre tread wears down
and rubber undergoes thermal-mechanical stress cycles.

In real-world telemetry, observed lap-time trends are confounded by:
1. Fuel Burn Effect: Car loses ~1.7 kg/lap, gaining ~0.035 to 0.050 s/lap in lap time.
2. Track Evolution: Grip improves as rubber is laid down on the racing line.
3. Traffic / Blue Flags / Overtakes.

This module models:
- Stint-level linear degradation slope (beta_deg in seconds/lap) via Ordinary Least Squares.
- Fuel-corrected true tyre degradation rate.
- Early-stint vs. Late-stint pace drop-off ('Tyre Cliff' delta).
- Goodness-of-fit metrics (R^2, p-value, standard error).
- Compound-wise degradation benchmarking.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

# Standard F1 fuel correction constant (seconds gained per lap due to fuel mass loss)
# Formula 1 cars start with ~100-110 kg and consume ~1.6-1.8 kg/lap (~0.035-0.045 s/lap gain)
DEFAULT_FUEL_EFFECT_SEC_PER_LAP = 0.038


def calculate_stint_degradation(
    stint_laps: pd.DataFrame,
    fuel_correction_per_lap: float = DEFAULT_FUEL_EFFECT_SEC_PER_LAP,
    min_laps_for_regression: int = 5
) -> Dict[str, Any]:
    """
    Computes statistical degradation trends for a single tyre stint.

    Parameters:
        stint_laps: Cleaned laps belonging to one continuous stint for a driver.
        fuel_correction_per_lap: Lap time gain (seconds) per lap due to vehicle fuel burn.
        min_laps_for_regression: Minimum clean laps required for linear regression.

    Returns:
        Dict containing degradation slope, fuel-corrected slope, R-squared, cliff delta, and pace metrics.
    """
    if stint_laps.empty:
        return {}

    driver = str(stint_laps["Driver"].iloc[0])
    team = str(stint_laps["Team"].iloc[0])
    stint_num = int(stint_laps["Stint"].iloc[0]) if "Stint" in stint_laps.columns and pd.notna(stint_laps["Stint"].iloc[0]) else 1
    compound = str(stint_laps["Compound"].iloc[0])

    # Filter for clean representative laps
    clean_mask = stint_laps["IsRepresentativePace"] if "IsRepresentativePace" in stint_laps.columns else stint_laps["IsValidTime"]
    clean_df = stint_laps[clean_mask].sort_values("LapNumber").copy()

    clean_count = len(clean_df)
    total_stint_length = len(stint_laps)

    if clean_count < min_laps_for_regression:
        return {
            "Driver": driver,
            "Team": team,
            "StintNumber": stint_num,
            "Compound": compound,
            "TotalStintLaps": total_stint_length,
            "CleanLapCount": clean_count,
            "ObservedSlope_SecPerLap": np.nan,
            "FuelCorrectedSlope_SecPerLap": np.nan,
            "RSquared": np.nan,
            "PValue": np.nan,
            "IsStatisticallySignificant": False,
            "EarlyStintPace_Seconds": np.nan,
            "LateStintPace_Seconds": np.nan,
            "PaceCliffDelta_Seconds": np.nan,
            "Note": "Insufficient clean laps for regression"
        }

    # Tyre Age vs Lap Time
    # If TyreLife is present, use it; otherwise use stint-relative lap index
    if "TyreLife" in clean_df.columns and clean_df["TyreLife"].notna().all():
        x = clean_df["TyreLife"].values.astype(float)
    else:
        x = np.arange(1, clean_count + 1, dtype=float)

    y = clean_df["LapTime_Seconds"].values.astype(float)

    # Ordinary Least Squares (OLS) Linear Regression
    regression = stats.linregress(x, y)
    observed_slope = round(float(regression.slope), 4)
    r_squared = round(float(regression.rvalue ** 2), 3)
    p_value = round(float(regression.pvalue), 4)
    std_err = round(float(regression.stderr), 4) if regression.stderr is not None else 0.0

    # Fuel-Corrected Degradation:
    # True Degradation = Observed Slope + Fuel Effect
    # If the car gets 0.038 s faster each lap from burning fuel, any flattening or positive slope
    # in lap time represents underlying tyre grip degradation.
    corrected_slope = round(observed_slope + fuel_correction_per_lap, 4)

    # Statistical significance: p < 0.05
    is_significant = bool(p_value < 0.05 and r_squared >= 0.20)

    # Early vs. Late Stint Pace (The "Tyre Cliff")
    # Take first 3-5 clean laps vs last 3-5 clean laps
    window_size = min(4, clean_count // 2)
    early_pace = round(float(np.mean(y[:window_size])), 3)
    late_pace = round(float(np.mean(y[-window_size:])), 3)
    cliff_delta = round(late_pace - early_pace, 3)

    return {
        "Driver": driver,
        "Team": team,
        "StintNumber": stint_num,
        "Compound": compound,
        "TotalStintLaps": total_stint_length,
        "CleanLapCount": clean_count,
        "ObservedSlope_SecPerLap": observed_slope,
        "FuelCorrectedSlope_SecPerLap": corrected_slope,
        "RSquared": r_squared,
        "PValue": p_value,
        "StdError": std_err,
        "IsStatisticallySignificant": is_significant,
        "EarlyStintPace_Seconds": early_pace,
        "LateStintPace_Seconds": late_pace,
        "PaceCliffDelta_Seconds": cliff_delta,
        "Note": "Statistically reliable" if is_significant else "Moderate pace variance"
    }


def analyze_race_degradation(
    cleaned_laps_df: pd.DataFrame,
    fuel_correction: float = DEFAULT_FUEL_EFFECT_SEC_PER_LAP
) -> pd.DataFrame:
    """
    Computes degradation parameters across all stints and all drivers in the race.

    Parameters:
        cleaned_laps_df: Cleaned race laps DataFrame.
        fuel_correction: Seconds gained per lap due to fuel burn (default 0.038 s).

    Returns:
        pd.DataFrame: Table of degradation slopes, cliff drops, and regression metrics per stint.
    """
    if cleaned_laps_df.empty:
        return pd.DataFrame()

    results = []
    # Group by Driver and Stint
    stint_col = "Stint" if "Stint" in cleaned_laps_df.columns else "LapNumber"
    for (driver, stint_id), group in cleaned_laps_df.groupby(["Driver", stint_col]):
        deg_data = calculate_stint_degradation(group, fuel_correction_per_lap=fuel_correction)
        if deg_data:
            results.append(deg_data)

    df = pd.DataFrame(results)
    if not df.empty:
        # Sort by Driver and StintNumber
        df = df.sort_values(by=["Driver", "StintNumber"]).reset_index(drop=True)
    return df


def compare_compound_degradation(degradation_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates degradation rates by compound to benchmark thermal durability.

    Returns:
        pd.DataFrame: Summary table comparing average wear rate (s/lap) across compounds.
    """
    if degradation_df.empty:
        return pd.DataFrame()

    valid_deg = degradation_df.dropna(subset=["FuelCorrectedSlope_SecPerLap"]).copy()

    records = []
    for compound, group in valid_deg.groupby("Compound"):
        if compound == "UNKNOWN":
            continue

        stint_count = len(group)
        mean_obs_slope = round(float(group["ObservedSlope_SecPerLap"].mean()), 4)
        mean_corr_slope = round(float(group["FuelCorrectedSlope_SecPerLap"].mean()), 4)
        med_corr_slope = round(float(group["FuelCorrectedSlope_SecPerLap"].median()), 4)
        mean_cliff = round(float(group["PaceCliffDelta_Seconds"].mean()), 3)

        records.append({
            "Compound": compound,
            "AnalyzedStints": stint_count,
            "MeanObservedSlope_SecPerLap": mean_obs_slope,
            "MeanFuelCorrectedDegradation_SecPerLap": mean_corr_slope,
            "MedianCorrectedDegradation_SecPerLap": med_corr_slope,
            "AvgPaceCliffDelta_Seconds": mean_cliff
        })

    summary_df = pd.DataFrame(records)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(by="MeanFuelCorrectedDegradation_SecPerLap", ascending=False).reset_index(drop=True)
    return summary_df
