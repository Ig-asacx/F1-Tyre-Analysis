"""
src/stint_analysis.py
=====================
Formula 1 Tyre Stint Identification & Strategy Sequence Module.

In Formula 1 race engineering, a 'Stint' represents an unbroken, continuous
sequence of racing laps completed by a driver on a single set of tyres between
pit stops (or between race start/finish).

This module provides:
1. Change-point stint detection algorithm.
2. Extraction of comprehensive stint-level metrics (lifespan, representative pace, tyre age).
3. Strategy sequence synthesis (e.g., S → S → H) with pit-stop count categorization.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Standard F1 tyre compound shorthand mappings
COMPOUND_SHORT_MAP = {
    "SOFT": "S",
    "MEDIUM": "M",
    "HARD": "H",
    "INTERMEDIATE": "I",
    "WET": "W",
    "UNKNOWN": "?"
}


def get_compound_short(compound: str) -> str:
    """Converts compound name (e.g. 'SOFT') to standard single-letter code ('S')."""
    return COMPOUND_SHORT_MAP.get(str(compound).upper().strip(), str(compound)[0] if compound else "?")


def detect_driver_stints(driver_laps: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies discrete stints for a single driver using change-point detection.

    Parameters:
        driver_laps: DataFrame containing cleaned laps for a single driver, sorted by LapNumber.

    Returns:
        pd.DataFrame: One row per stint containing boundaries, compound, and pace statistics.
    """
    if driver_laps.empty:
        return pd.DataFrame()

    df = driver_laps.sort_values(by="LapNumber").copy()
    driver = df["Driver"].iloc[0] if "Driver" in df.columns else "UNKNOWN"
    team = df["Team"].iloc[0] if "Team" in df.columns else "UNKNOWN"

    # Identify stint boundaries
    # FastF1 provides a 'Stint' column, but we guard against missing or non-incrementing values
    # by also checking for pit-out events or compound transitions.
    if "Stint" in df.columns and df["Stint"].notna().all():
        stint_ids = df["Stint"].astype(int)
    else:
        # Change-point detection: increment whenever pit occurs or compound shifts
        pit_shift = df["IsPitOutLap"].fillna(False) if "IsPitOutLap" in df.columns else False
        compound_shift = (df["Compound"] != df["Compound"].shift(1)).fillna(False)
        stint_ids = (pit_shift | compound_shift).cumsum() + 1

    df["AssignedStint"] = stint_ids

    stints_records = []
    for stint_id, group in df.groupby("AssignedStint", sort=True):
        compound = group["Compound"].iloc[0] if "Compound" in group.columns else "UNKNOWN"
        start_lap = int(group["LapNumber"].min())
        end_lap = int(group["LapNumber"].max())
        stint_length = len(group)

        # Tyre age at start and end of stint
        start_tyre_age = float(group["TyreLife"].min()) if "TyreLife" in group.columns and group["TyreLife"].notna().any() else np.nan
        end_tyre_age = float(group["TyreLife"].max()) if "TyreLife" in group.columns and group["TyreLife"].notna().any() else np.nan

        # Representative flying laps within this stint (excluding pit in/out and safety car laps)
        clean_mask = group["IsRepresentativePace"] if "IsRepresentativePace" in group.columns else group["IsValidTime"]
        clean_laps = group.loc[clean_mask, "LapTime_Seconds"].dropna()

        if len(clean_laps) > 0:
            avg_pace = round(clean_laps.mean(), 3)
            med_pace = round(clean_laps.median(), 3)
            fastest_lap = round(clean_laps.min(), 3)
            slowest_lap = round(clean_laps.max(), 3)
            std_pace = round(clean_laps.std(), 3) if len(clean_laps) > 1 else 0.0
            valid_lap_count = len(clean_laps)
        else:
            # Fallback to all valid times if no clean flying laps exist (e.g., short 1-lap caution stint)
            raw_valid = group.loc[group["IsValidTime"], "LapTime_Seconds"].dropna() if "IsValidTime" in group.columns else pd.Series(dtype=float)
            avg_pace = round(raw_valid.mean(), 3) if len(raw_valid) > 0 else np.nan
            med_pace = round(raw_valid.median(), 3) if len(raw_valid) > 0 else np.nan
            fastest_lap = round(raw_valid.min(), 3) if len(raw_valid) > 0 else np.nan
            slowest_lap = round(raw_valid.max(), 3) if len(raw_valid) > 0 else np.nan
            std_pace = 0.0
            valid_lap_count = len(raw_valid)

        stints_records.append({
            "Driver": driver,
            "Team": team,
            "StintNumber": int(stint_id),
            "Compound": compound,
            "CompoundShort": get_compound_short(compound),
            "StartLap": start_lap,
            "EndLap": end_lap,
            "StintLength": stint_length,
            "StartTyreLife": start_tyre_age,
            "EndTyreLife": end_tyre_age,
            "RepresentativeLaps": valid_lap_count,
            "AvgLapTime_Seconds": avg_pace,
            "MedianLapTime_Seconds": med_pace,
            "FastestLap_Seconds": fastest_lap,
            "SlowestLap_Seconds": slowest_lap,
            "StdLapTime_Seconds": std_pace
        })

    return pd.DataFrame(stints_records)


def extract_all_stints(cleaned_laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts stint metadata across all drivers present in the race session.

    Parameters:
        cleaned_laps_df: Cleaned race laps DataFrame containing all drivers.

    Returns:
        pd.DataFrame: Stint summary for all drivers.
    """
    if cleaned_laps_df is None or cleaned_laps_df.empty:
        return pd.DataFrame()

    all_stints = []
    drivers = cleaned_laps_df["Driver"].unique()

    for drv in drivers:
        drv_laps = cleaned_laps_df[cleaned_laps_df["Driver"] == drv]
        drv_stints = detect_driver_stints(drv_laps)
        if not drv_stints.empty:
            all_stints.append(drv_stints)

    if not all_stints:
        return pd.DataFrame()

    combined_df = pd.concat(all_stints, ignore_index=True)
    return combined_df


def generate_driver_strategy_summary(stints_df: pd.DataFrame, arrow_symbol: str = "→") -> pd.DataFrame:
    """
    Aggregates stint sequences into human-readable tyre strategy representations.

    Example Output String:
        'S → S → H (2-Stop)'
        'S → H → H (2-Stop)'
        'M → H (1-Stop)'

    Parameters:
        stints_df: Stints DataFrame from extract_all_stints().
        arrow_symbol: Separator for compound transitions (default '→', or '->' for ASCII terminals).

    Returns:
        pd.DataFrame indexed by Driver containing:
            - StrategyString: e.g. 'S → S → H'
            - FullStrategyDescription: e.g. 'S → S → H (2-Stop)'
            - NumberOfStops: Total pit stops completed (stints - 1)
            - TotalRaceLaps: Sum of all completed stint lengths
            - StartingCompound: Compound used in Stint 1
            - FinalCompound: Compound used in last stint
    """
    if stints_df.empty:
        return pd.DataFrame()

    summary_list = []
    for (driver, team), group in stints_df.groupby(["Driver", "Team"], sort=False):
        sorted_stints = group.sort_values(by="StintNumber")
        num_stints = len(sorted_stints)
        num_stops = max(0, num_stints - 1)

        # Sequence of shorthand symbols (e.g. ['S', 'S', 'H'])
        compounds_seq = sorted_stints["CompoundShort"].tolist()
        strategy_str = f" {arrow_symbol} ".join(compounds_seq)
        
        # Stop descriptor
        stop_desc = f"{num_stops}-Stop" if num_stops != 1 else "1-Stop"
        full_desc = f"{strategy_str} ({stop_desc})"

        total_laps = sorted_stints["StintLength"].sum()
        start_comp = sorted_stints.iloc[0]["Compound"]
        end_comp = sorted_stints.iloc[-1]["Compound"]

        summary_list.append({
            "Driver": driver,
            "Team": team,
            "NumberOfStops": num_stops,
            "NumberOfStints": num_stints,
            "StrategyString": strategy_str,
            "FullStrategyDescription": full_desc,
            "StartingCompound": start_comp,
            "FinalCompound": end_comp,
            "TotalLaps": total_laps
        })

    return pd.DataFrame(summary_list)
