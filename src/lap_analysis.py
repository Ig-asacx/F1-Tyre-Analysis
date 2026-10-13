"""
src/lap_analysis.py
===================
Formula 1 Lap-Time Performance & Driver/Team Pace Analysis Engine.

This module evaluates driver and constructor lap times across a Grand Prix:
- Isolates clean flying laps (excluding pit in/out, safety car, and track-limit laps).
- Calculates statistical pace indicators: Mean, Median, Std Dev, and Coefficient of Variation (CV%).
- Generates rolling lap-time moving medians to filter transient traffic and DRS overtakes.
- Produces head-to-head driver and constructor pace benchmarking tables.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_driver_pace_summary(cleaned_laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes lap-time summary metrics for all drivers in the session.
    Evaluates only representative flying laps to prevent pit stop and caution distortion.

    Parameters:
        cleaned_laps_df: Cleaned race laps DataFrame.

    Returns:
        pd.DataFrame: Driver pace rankings, fastest laps, median pace, and consistency (CV%).
    """
    if cleaned_laps_df.empty:
        return pd.DataFrame()

    # Filter for clean racing laps
    rep_mask = cleaned_laps_df["IsRepresentativePace"] if "IsRepresentativePace" in cleaned_laps_df.columns else cleaned_laps_df["IsValidTime"]
    clean_df = cleaned_laps_df[rep_mask].copy()

    records = []
    for (driver, team), group in clean_df.groupby(["Driver", "Team"], sort=False):
        times = group["LapTime_Seconds"].dropna()
        if len(times) == 0:
            continue

        mean_pace = round(float(times.mean()), 3)
        median_pace = round(float(times.median()), 3)
        std_pace = round(float(times.std()), 3) if len(times) > 1 else 0.0

        # Consistency: Coefficient of Variation (CV% = std / mean * 100)
        # Lower CV% indicates higher lap-to-lap consistency
        cv_pct = round((std_pace / mean_pace) * 100, 2) if mean_pace > 0 else 0.0

        # Identify driver's absolute fastest lap in the race
        fastest_idx = times.idxmin()
        fastest_row = group.loc[fastest_idx]
        fastest_time = round(float(fastest_row["LapTime_Seconds"]), 3)
        fastest_lap_num = int(fastest_row["LapNumber"])
        fastest_compound = str(fastest_row["Compound"])

        records.append({
            "Driver": driver,
            "Team": team,
            "RepresentativeLaps": len(times),
            "MedianPace_Seconds": median_pace,
            "MeanPace_Seconds": mean_pace,
            "FastestLap_Seconds": fastest_time,
            "FastestLapNumber": fastest_lap_num,
            "FastestCompound": fastest_compound,
            "StdDev_Seconds": std_pace,
            "Consistency_CV_Pct": cv_pct
        })

    summary_df = pd.DataFrame(records)
    if not summary_df.empty:
        # Rank drivers by Median Racing Pace (more robust than mean against remaining micro-traffic)
        summary_df = summary_df.sort_values(by="MedianPace_Seconds", ascending=True).reset_index(drop=True)
        best_median = summary_df.iloc[0]["MedianPace_Seconds"]
        summary_df["PaceDeltaToLeader_Seconds"] = (summary_df["MedianPace_Seconds"] - best_median).round(3)

    return summary_df


def calculate_team_pace_summary(cleaned_laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates driver performance up to the constructor/team level.

    Returns:
        pd.DataFrame: Constructor pace rankings, median team pace, and best team lap.
    """
    if cleaned_laps_df.empty:
        return pd.DataFrame()

    rep_mask = cleaned_laps_df["IsRepresentativePace"] if "IsRepresentativePace" in cleaned_laps_df.columns else cleaned_laps_df["IsValidTime"]
    clean_df = cleaned_laps_df[rep_mask].copy()

    records = []
    for team, group in clean_df.groupby("Team", sort=False):
        times = group["LapTime_Seconds"].dropna()
        if len(times) == 0:
            continue

        mean_pace = round(float(times.mean()), 3)
        median_pace = round(float(times.median()), 3)
        best_lap = round(float(times.min()), 3)
        total_clean_laps = len(times)

        records.append({
            "Team": team,
            "TotalCleanLaps": total_clean_laps,
            "MedianTeamPace_Seconds": median_pace,
            "MeanTeamPace_Seconds": mean_pace,
            "BestTeamLap_Seconds": best_lap,
        })

    summary_df = pd.DataFrame(records)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(by="MedianTeamPace_Seconds", ascending=True).reset_index(drop=True)
        best_median = summary_df.iloc[0]["MedianTeamPace_Seconds"]
        summary_df["PaceDeltaToFastestTeam"] = (summary_df["MedianTeamPace_Seconds"] - best_median).round(3)

    return summary_df


def calculate_driver_compound_breakdown(cleaned_laps_df: pd.DataFrame, driver: str) -> pd.DataFrame:
    """
    Breaks down a single driver's pace by each tyre compound used during the race.

    Parameters:
        cleaned_laps_df: Cleaned race laps DataFrame.
        driver: 3-letter driver abbreviation (e.g. 'VER', 'ALO').

    Returns:
        pd.DataFrame: One row per compound with lap count, median pace, and standard deviation.
    """
    drv_laps = cleaned_laps_df[cleaned_laps_df["Driver"] == driver.upper().strip()].copy()
    if drv_laps.empty:
        return pd.DataFrame()

    rep_mask = drv_laps["IsRepresentativePace"] if "IsRepresentativePace" in drv_laps.columns else drv_laps["IsValidTime"]
    clean_laps = drv_laps[rep_mask].copy()

    records = []
    for compound, group in clean_laps.groupby("Compound"):
        times = group["LapTime_Seconds"].dropna()
        if len(times) == 0:
            continue

        records.append({
            "Driver": driver.upper(),
            "Compound": compound,
            "RepresentativeLaps": len(times),
            "MedianPace_Seconds": round(float(times.median()), 3),
            "MeanPace_Seconds": round(float(times.mean()), 3),
            "FastestLap_Seconds": round(float(times.min()), 3),
            "StdDev_Seconds": round(float(times.std()), 3) if len(times) > 1 else 0.0
        })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values(by="MedianPace_Seconds").reset_index(drop=True)
    return df


def calculate_rolling_pace(
    cleaned_laps_df: pd.DataFrame,
    driver: str,
    window: int = 3
) -> pd.DataFrame:
    """
    Calculates a rolling median of lap times for a driver to smooth out transient lap variance.

    Parameters:
        cleaned_laps_df: Cleaned race laps DataFrame.
        driver: Driver code (e.g. 'VER').
        window: Rolling window size (default: 3 laps).

    Returns:
        pd.DataFrame: DataFrame containing LapNumber, LapTime_Seconds, RollingMedianPace, Compound.
    """
    drv_laps = cleaned_laps_df[cleaned_laps_df["Driver"] == driver.upper().strip()].sort_values("LapNumber").copy()
    if drv_laps.empty:
        return pd.DataFrame()

    # Calculate rolling median on representative laps, reindexing back to all laps
    drv_laps["RollingMedianPace"] = (
        drv_laps.loc[drv_laps["IsRepresentativePace"], "LapTime_Seconds"]
        .rolling(window=window, min_periods=1)
        .median()
        .round(3)
    )

    cols = ["LapNumber", "LapTime_Seconds", "RollingMedianPace", "Compound", "Stint", "IsRepresentativePace"]
    available_cols = [c for c in cols if c in drv_laps.columns]
    return drv_laps[available_cols].reset_index(drop=True)


def compare_drivers_head_to_head(
    cleaned_laps_df: pd.DataFrame,
    driver_a: str,
    driver_b: str
) -> Dict[str, Any]:
    """
    Performs head-to-head pace comparison between two drivers.

    Returns:
        Dict with head-to-head delta metrics, compound pace differences, and lap-by-lap comparison.
    """
    da = driver_a.upper().strip()
    db = driver_b.upper().strip()

    summary_df = calculate_driver_pace_summary(cleaned_laps_df)
    row_a = summary_df[summary_df["Driver"] == da]
    row_b = summary_df[summary_df["Driver"] == db]

    if row_a.empty or row_b.empty:
        return {"error": f"One or both drivers ({da}, {db}) not found in session data."}

    data_a = row_a.iloc[0].to_dict()
    data_b = row_b.iloc[0].to_dict()

    median_delta = round(data_a["MedianPace_Seconds"] - data_b["MedianPace_Seconds"], 3)
    fastest_delta = round(data_a["FastestLap_Seconds"] - data_b["FastestLap_Seconds"], 3)

    return {
        "driver_a": da,
        "driver_b": db,
        "driver_a_metrics": data_a,
        "driver_b_metrics": data_b,
        "median_pace_delta_a_minus_b": median_delta,
        "fastest_lap_delta_a_minus_b": fastest_delta,
        "faster_driver_median": da if median_delta < 0 else db
    }
