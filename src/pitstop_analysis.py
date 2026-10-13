"""
src/pitstop_analysis.py
=======================
Formula 1 Pit Stop Detection, Transit Duration & Tyre Transition Analytics.

A pit stop is the operational inflection point of race strategy where:
- The car enters the pit lane (restricted by the 80 km/h pit speed limiter).
- The pit crew executes tyre replacement (typically 2.0 to 3.5 seconds stationary).
- The driver returns to the track on fresh rubber, sacrificing track position in
  exchange for a tyre grip advantage (the 'undercut' or 'overcut' dynamic).

This module extracts:
1. Exact pit-stop lap numbers and sequence ordering.
2. Compound transitions (e.g. SOFT -> HARD).
3. Pit lane transit duration (PitInTime to PitOutTime in seconds).
4. Track position loss and post-stop track re-entry.
5. Overall stop count categorizations (1-Stop, 2-Stop, 3-Stop).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def extract_driver_pit_stops(driver_laps: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts all pit stop events for an individual driver.

    Parameters:
        driver_laps: Cleaned laps DataFrame for a single driver, sorted by LapNumber.

    Returns:
        pd.DataFrame: One row per pit stop event with timing, compounds, and positions.
    """
    if driver_laps.empty:
        return pd.DataFrame()

    df = driver_laps.sort_values("LapNumber").copy().reset_index(drop=True)
    driver = str(df["Driver"].iloc[0])
    team = str(df["Team"].iloc[0])

    # In-laps indicate pit entry
    in_lap_indices = df[df["IsPitInLap"]].index.tolist()
    if not in_lap_indices and "PitInTime" in df.columns:
        in_lap_indices = df[df["PitInTime"].notna()].index.tolist()

    pit_records = []
    for stop_idx, in_idx in enumerate(in_lap_indices, start=1):
        in_row = df.loc[in_idx]
        pit_in_lap = int(in_row["LapNumber"])
        compound_before = str(in_row["Compound"])
        pos_before = int(in_row["Position"]) if "Position" in in_row and pd.notna(in_row["Position"]) else np.nan

        # Out-lap is normally the next row
        out_row = df.loc[in_idx + 1] if in_idx + 1 < len(df) else None
        
        if out_row is not None:
            pit_out_lap = int(out_row["LapNumber"])
            compound_after = str(out_row["Compound"])
            pos_after = int(out_row["Position"]) if "Position" in out_row and pd.notna(out_row["Position"]) else np.nan

            # Pit transit duration (PitOutTime - PitInTime)
            pit_duration = np.nan
            in_time = in_row.get("PitInTime", np.nan)
            out_time = out_row.get("PitOutTime", np.nan)

            if pd.notna(in_time) and pd.notna(out_time):
                if isinstance(in_time, str):
                    in_time = pd.to_timedelta(in_time, errors="coerce")
                if isinstance(out_time, str):
                    out_time = pd.to_timedelta(out_time, errors="coerce")

                if pd.notna(in_time) and pd.notna(out_time):
                    td = out_time - in_time
                    if hasattr(td, "total_seconds"):
                        pit_duration = round(td.total_seconds(), 3)
        else:
            pit_out_lap = pit_in_lap + 1
            compound_after = "UNKNOWN"
            pos_after = np.nan
            pit_duration = np.nan

        positions_delta = (pos_after - pos_before) if (pd.notna(pos_after) and pd.notna(pos_before)) else np.nan

        pit_records.append({
            "Driver": driver,
            "Team": team,
            "StopNumber": stop_idx,
            "PitInLap": pit_in_lap,
            "PitOutLap": pit_out_lap,
            "CompoundBefore": compound_before,
            "CompoundAfter": compound_after,
            "TyreTransition": f"{compound_before} → {compound_after}",
            "PitDuration_Seconds": pit_duration,
            "PositionBeforePit": pos_before,
            "PositionAfterPit": pos_after,
            "TrackPositionsLost": positions_delta
        })

    return pd.DataFrame(pit_records)


def extract_all_pit_stops(cleaned_laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts all pit stop events across the entire race grid.

    Parameters:
        cleaned_laps_df: Cleaned race laps DataFrame.

    Returns:
        pd.DataFrame: Table of every pit stop executed in the Grand Prix.
    """
    if cleaned_laps_df.empty:
        return pd.DataFrame()

    all_stops = []
    for drv in cleaned_laps_df["Driver"].unique():
        drv_laps = cleaned_laps_df[cleaned_laps_df["Driver"] == drv]
        drv_stops = extract_driver_pit_stops(drv_laps)
        if not drv_stops.empty:
            all_stops.append(drv_stops)

    if not all_stops:
        return pd.DataFrame()

    combined = pd.concat(all_stops, ignore_index=True)
    return combined.sort_values(by=["PitInLap", "StopNumber"]).reset_index(drop=True)


def calculate_driver_pit_summary(
    all_pit_stops_df: pd.DataFrame,
    all_drivers: Optional[List[str]] = None,
    results_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Aggregates pit stops per driver, including drivers who completed zero stops.

    Parameters:
        all_pit_stops_df: DataFrame from extract_all_pit_stops.
        all_drivers: Optional full list of driver codes to account for 0-stop drivers.
        results_df: Optional race results table to include finishing positions.

    Returns:
        pd.DataFrame: Driver-level pit stop summary with strategy categorization.
    """
    records = []

    # Map driver list
    driver_set = set(all_pit_stops_df["Driver"].unique()) if not all_pit_stops_df.empty else set()
    if all_drivers:
        driver_set = driver_set.union(set(all_drivers))

    for drv in sorted(driver_set):
        drv_stops = all_pit_stops_df[all_pit_stops_df["Driver"] == drv] if not all_pit_stops_df.empty else pd.DataFrame()
        total_stops = len(drv_stops)

        # Categorize Strategy
        if total_stops == 0:
            category = "0-Stop"
        elif total_stops == 1:
            category = "1-Stop"
        elif total_stops == 2:
            category = "2-Stop"
        elif total_stops == 3:
            category = "3-Stop"
        else:
            category = f"{total_stops}-Stop"

        durations = drv_stops["PitDuration_Seconds"].dropna() if not drv_stops.empty else pd.Series(dtype=float)
        avg_dur = round(float(durations.mean()), 3) if len(durations) > 0 else np.nan
        fastest_dur = round(float(durations.min()), 3) if len(durations) > 0 else np.nan
        team = drv_stops["Team"].iloc[0] if not drv_stops.empty else "UNKNOWN"
        stop_laps = drv_stops["PitInLap"].tolist() if not drv_stops.empty else []

        records.append({
            "Driver": drv,
            "Team": team,
            "TotalPitStops": total_stops,
            "StrategyCategory": category,
            "PitStopLaps": str(stop_laps),
            "AvgPitLaneDuration_Seconds": avg_dur,
            "FastestPitLaneDuration_Seconds": fastest_dur
        })

    summary_df = pd.DataFrame(records)

    # Merge official finishing position if results_df provided
    if results_df is not None and not results_df.empty and "Abbreviation" in results_df.columns:
        res_sub = results_df[["Abbreviation", "PositionNumeric", "Status"]].rename(
            columns={"Abbreviation": "Driver", "PositionNumeric": "FinishingPosition"}
        )
        summary_df = summary_df.merge(res_sub, on="Driver", how="left")
        summary_df = summary_df.sort_values(by="FinishingPosition").reset_index(drop=True)
    else:
        summary_df = summary_df.sort_values(by="TotalPitStops").reset_index(drop=True)

    return summary_df


def calculate_strategy_frequency(driver_pit_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Computes distribution of strategy types (1-stop vs 2-stop vs 3-stop) across the grid.

    Returns:
        pd.DataFrame: StrategyCategory, DriverCount, PercentageOfGrid.
    """
    if driver_pit_summary.empty:
        return pd.DataFrame()

    total_drivers = len(driver_pit_summary)
    grouped = driver_pit_summary.groupby("StrategyCategory").size().reset_index(name="DriverCount")
    grouped["PercentageOfGrid"] = round((grouped["DriverCount"] / total_drivers) * 100, 2)
    return grouped.sort_values(by="DriverCount", ascending=False).reset_index(drop=True)
