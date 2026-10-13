"""
src/data_cleaning.py
====================
Formula 1 Data Cleaning & Preprocessing Pipeline.

Formula 1 telemetry cannot be analyzed using raw, unfiltered timing logs.
Pit in-laps, pit out-laps, safety cars, track limit violations, and standing starts
introduce massive positive outliers (20 to 60+ seconds slower than typical pace)
that distort tyre degradation slopes, mean pace calculations, and strategy comparisons.

This module provides:
1. Timedelta to floating-point seconds transformation.
2. Transparent flag-based data cleansing (NO silent row deletion).
3. Outlier identification using statistical Interquartile Range (IQR).
4. Data audit report detailing exactly why laps were classified as non-representative.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def timedelta_to_seconds(series: pd.Series) -> pd.Series:
    """
    Converts a pandas Timedelta Series into continuous float seconds.

    Parameters:
        series: pd.Series containing pd.Timedelta or NaT values.

    Returns:
        pd.Series: Floating-point seconds rounded to 3 decimal places (milliseconds).
    """
    return series.dt.total_seconds().round(3)


def clean_race_laps(
    raw_laps: pd.DataFrame,
    iqr_multiplier: float = 1.5,
    filter_unrealistic_times: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes the complete F1 lap cleaning pipeline.

    Instead of silently discarding rows, this function enriches the DataFrame with
    explicit boolean diagnostic flags. This guarantees full data transparency and
    preserves in-laps and out-laps for pit stop analysis while isolating clean
    flying laps for tyre pace and degradation modeling.

    Diagnostic Flags Added:
    - LapTime_Seconds: Numerical lap time in seconds.
    - S1_Seconds, S2_Seconds, S3_Seconds: Sector times in seconds.
    - IsPitInLap: True if the driver entered the pit lane at the end of this lap.
    - IsPitOutLap: True if the driver exited the pit lane at the start of this lap.
    - IsStartLap: True for Lap 1 (standing start from grid).
    - IsGreenFlag: True if TrackStatus is '1' (no Yellow Flag, SC, or VSC).
    - IsDeletedLap: True if deleted by Race Control for track limits.
    - IsValidTime: True if LapTime is non-null and greater than zero.
    - IsAccurateLap: True if FastF1 verifies timing loop continuity (IsAccurate == True).
    - IsOutlierPace: True if lap time is outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR] for its compound.
    - IsRepresentativePace: Master flag combining all criteria for pure tyre pace analysis.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: (Enriched DataFrame, Cleaning Audit Report)
    """
    if raw_laps is None or raw_laps.empty:
        raise ValueError("Cannot clean an empty or None laps DataFrame.")

    df = raw_laps.copy()
    initial_lap_count = len(df)

    # 1. Type Standardizations & Timedelta Conversions
    if "LapTime" in df.columns:
        df["LapTime_Seconds"] = timedelta_to_seconds(df["LapTime"])
    else:
        df["LapTime_Seconds"] = np.nan

    for sec in ["Sector1Time", "Sector2Time", "Sector3Time"]:
        if sec in df.columns:
            sec_name = sec.replace("Time", "_Seconds").replace("Sector", "S")
            df[sec_name] = timedelta_to_seconds(df[sec])

    # Standardize string fields
    if "Compound" in df.columns:
        df["Compound"] = df["Compound"].astype(str).str.upper().str.strip()
        # Replace 'NAN' string from conversion
        df["Compound"] = df["Compound"].replace({"NAN": "UNKNOWN", "NONE": "UNKNOWN"})
    else:
        df["Compound"] = "UNKNOWN"

    if "Driver" in df.columns:
        df["Driver"] = df["Driver"].astype(str).str.upper().str.strip()

    if "Team" in df.columns:
        df["Team"] = df["Team"].astype(str).str.strip()

    # 2. Derive Explicit Diagnostic Flags
    # Flag: Pit In-lap (Car slows down, enters pit lane)
    df["IsPitInLap"] = df["PitInTime"].notna() if "PitInTime" in df.columns else False

    # Flag: Pit Out-lap (Car exits pit lane on cold tyres)
    df["IsPitOutLap"] = df["PitOutTime"].notna() if "PitOutTime" in df.columns else False

    # Flag: Start Lap (Standing start from stationary grid, accordion effect)
    df["IsStartLap"] = df["LapNumber"] == 1 if "LapNumber" in df.columns else False

    # Flag: Track Status (1 = All Clear / Green; 2 = Yellow; 4 = SC; 5 = Red; 6 = VSC)
    if "TrackStatus" in df.columns:
        df["IsGreenFlag"] = df["TrackStatus"].astype(str) == "1"
    else:
        df["IsGreenFlag"] = True

    # Flag: Deleted Lap (Track limits violation)
    if "Deleted" in df.columns:
        df["IsDeletedLap"] = df["Deleted"].notna() & (df["Deleted"] == True)
    else:
        df["IsDeletedLap"] = False

    # Flag: Valid Time Non-Null
    df["IsValidTime"] = df["LapTime_Seconds"].notna() & (df["LapTime_Seconds"] > 0)

    # Flag: FastF1 Timing Accuracy Check
    if "IsAccurate" in df.columns:
        df["IsAccurateLap"] = df["IsAccurate"].fillna(False).astype(bool)
    else:
        df["IsAccurateLap"] = True

    # 3. Statistical Outlier Detection (per compound)
    # Applied to green-flag valid laps to catch anomalous slow laps (e.g. spins, yellow flags not logged)
    df["IsOutlierPace"] = False
    valid_mask = (
        df["IsValidTime"] &
        ~df["IsPitInLap"] &
        ~df["IsPitOutLap"] &
        ~df["IsStartLap"] &
        df["IsGreenFlag"] &
        ~df["IsDeletedLap"]
    )

    for compound in df["Compound"].unique():
        if compound == "UNKNOWN":
            continue
        compound_mask = valid_mask & (df["Compound"] == compound)
        times = df.loc[compound_mask, "LapTime_Seconds"]
        
        if len(times) >= 5:
            q1 = times.quantile(0.25)
            q3 = times.quantile(0.75)
            iqr = q3 - q1
            upper_bound = q3 + (iqr_multiplier * iqr)
            lower_bound = max(0.0, q1 - (iqr_multiplier * iqr))
            
            outlier_indices = df.loc[compound_mask & ((df["LapTime_Seconds"] > upper_bound) | (df["LapTime_Seconds"] < lower_bound))].index
            df.loc[outlier_indices, "IsOutlierPace"] = True

    # 4. Master Representative Pace Flag
    # A lap is representative of pure vehicle & tyre performance if and only if ALL conditions pass
    df["IsRepresentativePace"] = (
        df["IsValidTime"] &
        ~df["IsPitInLap"] &
        ~df["IsPitOutLap"] &
        ~df["IsStartLap"] &
        df["IsGreenFlag"] &
        ~df["IsDeletedLap"] &
        df["IsAccurateLap"] &
        ~df["IsOutlierPace"]
    )

    # 5. Build Audit Report
    audit_report = {
        "total_laps_loaded": initial_lap_count,
        "pit_in_laps": int(df["IsPitInLap"].sum()),
        "pit_out_laps": int(df["IsPitOutLap"].sum()),
        "start_laps_excluded": int(df["IsStartLap"].sum()),
        "yellow_or_sc_laps": int((~df["IsGreenFlag"]).sum()),
        "deleted_laps_track_limits": int(df["IsDeletedLap"].sum()),
        "invalid_or_missing_times": int((~df["IsValidTime"]).sum()),
        "statistical_outliers": int(df["IsOutlierPace"].sum()),
        "representative_flying_laps": int(df["IsRepresentativePace"].sum()),
        "representative_percentage": round((df["IsRepresentativePace"].sum() / initial_lap_count) * 100, 2)
    }

    logger.info(
        f"Data Cleaning Completed: {audit_report['representative_flying_laps']} / {initial_lap_count} "
        f"laps ({audit_report['representative_percentage']}%) classified as representative pace."
    )

    return df, audit_report


def get_representative_laps(df: pd.DataFrame) -> pd.DataFrame:
    """Returns only clean flying laps suitable for pace and tyre degradation modeling."""
    return df[df["IsRepresentativePace"]].copy()


def get_pit_stop_laps(df: pd.DataFrame) -> pd.DataFrame:
    """Returns in-laps and out-laps for pit stop and strategy transition analysis."""
    return df[df["IsPitInLap"] | df["IsPitOutLap"]].copy()
