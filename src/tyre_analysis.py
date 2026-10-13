"""
src/tyre_analysis.py
====================
Formula 1 Tyre Compound Performance & Lifespan Analytics Engine.

This module analyzes the physical characteristics, usage distribution,
and lap-time performance across official Pirelli dry and wet compounds:
- SOFT (C3 / C4 / C5 depending on race nomination)
- MEDIUM (C2 / C3 / C4)
- HARD (C1 / C2 / C3)
- INTERMEDIATE (Green band, damp/drying track)
- WET (Blue band, standing water)

Calculates:
1. Aggregate compound usage distribution (% of total race mileage).
2. Compound stint lifespan statistics (mean, median, min, max, standard deviation).
3. Representative lap-time pace offsets (pace delta between compounds).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Standard Pirelli compound color palette for consistent presentation
PIRELLI_COMPOUND_COLORS = {
    "SOFT": "#FF1801",          # Red
    "MEDIUM": "#F5D033",        # Yellow
    "HARD": "#CCCCCC",          # White / Silver
    "INTERMEDIATE": "#39B54A",  # Green
    "WET": "#00A0DE",           # Blue
    "UNKNOWN": "#808080"        # Gray
}


def calculate_compound_usage_summary(cleaned_laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes lap count distribution and percentage of total race laps run on each compound.

    Parameters:
        cleaned_laps_df: DataFrame of cleaned race laps.

    Returns:
        pd.DataFrame: Table of compound, lap count, percentage, and unique drivers.
    """
    if cleaned_laps_df.empty:
        return pd.DataFrame()

    total_valid_laps = len(cleaned_laps_df[cleaned_laps_df["Compound"] != "UNKNOWN"])
    if total_valid_laps == 0:
        total_valid_laps = len(cleaned_laps_df)

    usage_records = []
    for compound, group in cleaned_laps_df.groupby("Compound"):
        if compound == "UNKNOWN":
            continue
        laps_run = len(group)
        pct = round((laps_run / total_valid_laps) * 100, 2)
        drivers_using = group["Driver"].nunique()

        usage_records.append({
            "Compound": compound,
            "TotalLapsRun": laps_run,
            "PercentageOfRaceLaps": pct,
            "UniqueDriversUsing": drivers_using,
            "ColorHex": PIRELLI_COMPOUND_COLORS.get(compound, "#808080")
        })

    summary_df = pd.DataFrame(usage_records)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(by="TotalLapsRun", ascending=False).reset_index(drop=True)
    return summary_df


def calculate_compound_stint_metrics(stints_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes lifespan and durability metrics per compound from stint records.

    Parameters:
        stints_df: DataFrame of stints produced by stint_analysis.detect_driver_stints.

    Returns:
        pd.DataFrame: Lifespan summary (mean, median, min, max, std of stint length).
    """
    if stints_df.empty:
        return pd.DataFrame()

    metrics_list = []
    for compound, group in stints_df.groupby("Compound"):
        if compound == "UNKNOWN":
            continue
        stint_lengths = group["StintLength"]
        total_stints = len(group)

        mean_len = round(float(stint_lengths.mean()), 1)
        med_len = round(float(stint_lengths.median()), 1)
        min_len = int(stint_lengths.min())
        max_len = int(stint_lengths.max())
        std_len = round(float(stint_lengths.std()), 1) if total_stints > 1 else 0.0

        metrics_list.append({
            "Compound": compound,
            "StintCount": total_stints,
            "AvgStintLength": mean_len,
            "MedianStintLength": med_len,
            "MinStintLength": min_len,
            "MaxStintLength": max_len,
            "StdStintLength": std_len
        })

    metrics_df = pd.DataFrame(metrics_list)
    if not metrics_df.empty:
        metrics_df = metrics_df.sort_values(by="AvgStintLength", ascending=False).reset_index(drop=True)
    return metrics_df


def calculate_compound_pace_metrics(cleaned_laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates pure representative pace metrics per compound.
    Only clean flying laps (IsRepresentativePace == True) are evaluated.

    Parameters:
        cleaned_laps_df: DataFrame of cleaned race laps.

    Returns:
        pd.DataFrame: Pace statistics (mean, median, std, fastest, slowest, pace delta).
    """
    if cleaned_laps_df.empty:
        return pd.DataFrame()

    # Filter for clean flying laps
    if "IsRepresentativePace" in cleaned_laps_df.columns:
        pace_df = cleaned_laps_df[cleaned_laps_df["IsRepresentativePace"]].copy()
    else:
        pace_df = cleaned_laps_df[cleaned_laps_df["IsValidTime"]].copy()

    pace_records = []
    for compound, group in pace_df.groupby("Compound"):
        if compound == "UNKNOWN":
            continue
        times = group["LapTime_Seconds"].dropna()
        if len(times) == 0:
            continue

        mean_pace = round(float(times.mean()), 3)
        med_pace = round(float(times.median()), 3)
        std_pace = round(float(times.std()), 3) if len(times) > 1 else 0.0
        fastest_lap = round(float(times.min()), 3)
        slowest_lap = round(float(times.max()), 3)

        pace_records.append({
            "Compound": compound,
            "RepresentativeLapCount": len(times),
            "MeanPace_Seconds": mean_pace,
            "MedianPace_Seconds": med_pace,
            "StdPace_Seconds": std_pace,
            "FastestLap_Seconds": fastest_lap,
            "SlowestLap_Seconds": slowest_lap
        })

    result_df = pd.DataFrame(pace_records)
    if not result_df.empty:
        # Calculate pace delta relative to fastest compound
        best_median = result_df["MedianPace_Seconds"].min()
        result_df["DeltaToFastest_Seconds"] = (result_df["MedianPace_Seconds"] - best_median).round(3)
        result_df = result_df.sort_values(by="MedianPace_Seconds", ascending=True).reset_index(drop=True)

    return result_df


def get_comprehensive_tyre_report(
    cleaned_laps_df: pd.DataFrame,
    stints_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merges usage distribution, durability/stint length, and lap pace into
    a single master benchmarking report.

    Returns:
        pd.DataFrame: Unified compound analysis table.
    """
    usage = calculate_compound_usage_summary(cleaned_laps_df)
    stints = calculate_compound_stint_metrics(stints_df)
    pace = calculate_compound_pace_metrics(cleaned_laps_df)

    if usage.empty or stints.empty or pace.empty:
        return pd.DataFrame()

    merged = usage.merge(stints, on="Compound", how="left")
    merged = merged.merge(pace, on="Compound", how="left")
    return merged
