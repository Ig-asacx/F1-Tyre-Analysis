"""
tests/test_analysis.py
======================
Automated Unit and Integration Test Suite for Formula 1 Tyre Strategy Pipeline.
Executes testing across data cleaning, stint detection, degradation modeling,
pit stop transitions, and empty data tolerance.
"""

from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_cleaning import timedelta_to_seconds, clean_race_laps, get_representative_laps
from src.stint_analysis import detect_driver_stints, generate_driver_strategy_summary
from src.tyre_analysis import calculate_compound_usage_summary, calculate_compound_pace_metrics
from src.degradation_analysis import calculate_stint_degradation, DEFAULT_FUEL_EFFECT_SEC_PER_LAP
from src.pitstop_analysis import extract_driver_pit_stops, calculate_strategy_frequency
from src.strategy_analysis import calculate_strategy_correlations
from src.visualization import plot_stint_timeline, plot_compound_usage, _create_empty_figure


# ==========================================
# 1. TIMEDELTA TO SECONDS CONVERSION TESTS
# ==========================================
def test_timedelta_to_seconds_valid():
    """Validates accurate conversion from pd.Timedelta to float seconds."""
    td_series = pd.Series([
        pd.Timedelta(minutes=1, seconds=38, milliseconds=250),
        pd.Timedelta(seconds=95),
        pd.NaT
    ])
    result = timedelta_to_seconds(td_series)
    assert result.iloc[0] == 98.250
    assert result.iloc[1] == 95.000
    assert pd.isna(result.iloc[2])


# ==========================================
# 2. DATA CLEANING & TRANSPARENCY TESTS
# ==========================================
def test_clean_race_laps_preserves_rows():
    """Ensures data cleaning does NOT silently delete rows and attaches diagnostic flags."""
    raw_laps = pd.DataFrame({
        "Driver": ["VER", "VER", "VER", "VER"],
        "Team": ["Red Bull Racing"] * 4,
        "LapNumber": [1, 2, 3, 4],
        "LapTime": [
            pd.Timedelta(seconds=102),  # Lap 1 start
            pd.Timedelta(seconds=98),   # Clean flying
            pd.Timedelta(seconds=105),  # In-lap
            pd.Timedelta(seconds=97)    # Out-lap
        ],
        "PitInTime": [pd.NaT, pd.NaT, pd.Timestamp("2023-03-05 15:10:00"), pd.NaT],
        "PitOutTime": [pd.NaT, pd.NaT, pd.NaT, pd.Timestamp("2023-03-05 15:10:25")],
        "TrackStatus": ["1", "1", "1", "1"],
        "Compound": ["SOFT", "SOFT", "SOFT", "HARD"],
        "IsAccurate": [True, True, True, True]
    })

    cleaned_df, audit = clean_race_laps(raw_laps)
    # Check no rows dropped
    assert len(cleaned_df) == 4
    # Check flags
    assert cleaned_df.loc[0, "IsStartLap"] == True
    assert cleaned_df.loc[0, "IsRepresentativePace"] == False
    assert cleaned_df.loc[1, "IsRepresentativePace"] == True
    assert cleaned_df.loc[2, "IsPitInLap"] == True
    assert cleaned_df.loc[2, "IsRepresentativePace"] == False
    assert cleaned_df.loc[3, "IsPitOutLap"] == True
    assert cleaned_df.loc[3, "IsRepresentativePace"] == False


# ==========================================
# 3. STINT DETECTION & STRATEGY STRING TESTS
# ==========================================
def test_stint_detection_and_strategy_string():
    """Tests run-length grouping of compound stints and formatted strategy string."""
    synthetic_laps = pd.DataFrame({
        "Driver": ["ALO"] * 10,
        "Team": ["Aston Martin"] * 10,
        "LapNumber": list(range(1, 11)),
        "LapTime_Seconds": [98.0] * 10,
        "Compound": ["SOFT"] * 5 + ["HARD"] * 5,
        "Stint": [1] * 5 + [2] * 5,
        "TyreLife": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        "IsRepresentativePace": [True] * 10,
        "IsValidTime": [True] * 10
    })

    stints = detect_driver_stints(synthetic_laps)
    assert len(stints) == 2
    assert stints.iloc[0]["Compound"] == "SOFT"
    assert stints.iloc[0]["StintLength"] == 5
    assert stints.iloc[1]["Compound"] == "HARD"
    assert stints.iloc[1]["StintLength"] == 5

    strategy_df = generate_driver_strategy_summary(stints, arrow_symbol="→")
    assert strategy_df.iloc[0]["StrategyString"] == "S → H"
    assert strategy_df.iloc[0]["NumberOfStops"] == 1
    assert strategy_df.iloc[0]["FullStrategyDescription"] == "S → H (1-Stop)"


# ==========================================
# 4. PIT STOP EXTRACTION TESTS
# ==========================================
def test_pit_stop_extraction():
    """Validates pit stop detection, compound transitions, and duration math."""
    pit_laps = pd.DataFrame({
        "Driver": ["HAM", "HAM"],
        "Team": ["Mercedes", "Mercedes"],
        "LapNumber": [12, 13],
        "Compound": ["SOFT", "HARD"],
        "IsPitInLap": [True, False],
        "PitInTime": [pd.Timedelta(seconds=1200), pd.NaT],
        "PitOutTime": [pd.NaT, pd.Timedelta(seconds=1224)],
        "Position": [3, 5]
    })

    stops = extract_driver_pit_stops(pit_laps)
    assert len(stops) == 1
    assert stops.iloc[0]["PitInLap"] == 12
    assert stops.iloc[0]["CompoundBefore"] == "SOFT"
    assert stops.iloc[0]["CompoundAfter"] == "HARD"
    assert stops.iloc[0]["PitDuration_Seconds"] == 24.0
    assert stops.iloc[0]["TrackPositionsLost"] == 2


# ==========================================
# 5. TYRE DEGRADATION & FUEL CORRECTION TESTS
# ==========================================
def test_stint_degradation_and_fuel_correction():
    """Validates OLS linear regression and fuel-corrected degradation slope."""
    # Create 10 laps where lap time steadily climbs by 0.10s per lap
    tyre_age = np.arange(1, 11)
    lap_times = 95.0 + (0.10 * tyre_age)  # Observed slope = 0.10 s/lap

    stint_df = pd.DataFrame({
        "Driver": ["LEC"] * 10,
        "Team": ["Ferrari"] * 10,
        "Stint": [1] * 10,
        "Compound": ["SOFT"] * 10,
        "LapNumber": list(range(1, 11)),
        "TyreLife": tyre_age,
        "LapTime_Seconds": lap_times,
        "IsRepresentativePace": [True] * 10,
        "IsValidTime": [True] * 10
    })

    deg_metrics = calculate_stint_degradation(stint_df, fuel_correction_per_lap=0.038)
    assert deg_metrics["ObservedSlope_SecPerLap"] == pytest.approx(0.10, abs=0.001)
    assert deg_metrics["FuelCorrectedSlope_SecPerLap"] == pytest.approx(0.138, abs=0.001)
    assert deg_metrics["IsStatisticallySignificant"] == True
    assert deg_metrics["PaceCliffDelta_Seconds"] > 0


# ==========================================
# 6. CORRELATION & EMPTY DATA HANDLING
# ==========================================
def test_empty_dataframe_tolerance():
    """Ensures analytical and plotting functions handle empty DataFrames safely without crashing."""
    empty_df = pd.DataFrame()

    # Analytics functions
    assert calculate_compound_usage_summary(empty_df).empty
    assert calculate_compound_pace_metrics(empty_df).empty
    assert detect_driver_stints(empty_df).empty
    assert extract_driver_pit_stops(empty_df).empty
    assert calculate_strategy_correlations(empty_df) == {}

    # Visualization functions
    fig1 = plot_stint_timeline(empty_df)
    assert fig1 is not None
    fig2 = plot_compound_usage(empty_df)
    assert fig2 is not None
