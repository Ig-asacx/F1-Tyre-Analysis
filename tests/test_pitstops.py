"""
tests/test_pitstops.py
======================
Unit and integration test for Pit Stop Analytics Engine.
Evaluates pit stop detection, pit lane duration, compound transitions, and stop frequency.
"""

import sys
from pathlib import Path
import pandas as pd

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_session_cache
from src.pitstop_analysis import (
    extract_driver_pit_stops,
    extract_all_pit_stops,
    calculate_driver_pit_summary,
    calculate_strategy_frequency
)


def test_pitstops():
    print("=" * 65)
    print("STEP 11: PIT STOP DETECTION & STRATEGY CATEGORIZATION TEST")
    print("=" * 65)

    cleaned_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_cleaned_laps.csv"
    raw_file = PROJECT_ROOT / "data" / "raw" / "2023_bahrain_race.pkl"

    if not cleaned_file.exists() or not raw_file.exists():
        print("[ERROR] Required data files missing. Run previous steps first.")
        return

    cleaned_laps = pd.read_csv(cleaned_file)
    raw_payload = load_raw_session_cache(raw_file)
    results_df = raw_payload["results"]

    # 1. Driver-Level Pit Stops: Max Verstappen (VER)
    ver_laps = cleaned_laps[cleaned_laps["Driver"] == "VER"]
    ver_stops = extract_driver_pit_stops(ver_laps)
    print("\n--- [MAX VERSTAPPEN (VER) PIT STOP BREAKDOWN] ---")
    ver_cols = ["StopNumber", "PitInLap", "TyreTransition", "PositionBeforePit", "PositionAfterPit", "TrackPositionsLost"]
    print(ver_stops[ver_cols].to_string(index=False))

    # 2. Extract All Pit Stops Across Grid
    all_stops = extract_all_pit_stops(cleaned_laps)
    print(f"\n[GRID] Successfully extracted {len(all_stops)} total pit stops across the race.")

    print("\n--- [SAMPLE PIT STOPS (LAPS 11-15: FIRST PIT WINDOW)] ---")
    sample_cols = ["Driver", "Team", "StopNumber", "PitInLap", "TyreTransition", "PositionBeforePit", "PositionAfterPit"]
    print(all_stops[(all_stops["PitInLap"] >= 11) & (all_stops["PitInLap"] <= 15)][sample_cols].head(8).to_string(index=False))

    # 3. Driver Pit Stop Summary
    pit_summary = calculate_driver_pit_summary(all_stops, all_drivers=raw_payload["drivers"], results_df=results_df)
    print("\n--- [TOP 8 DRIVER PIT STOP STRATEGY & FINISHING POSITIONS] ---")
    sum_cols = ["FinishingPosition", "Driver", "Team", "TotalPitStops", "StrategyCategory", "PitStopLaps"]
    print(pit_summary[sum_cols].head(8).to_string(index=False))

    # 4. Strategy Frequency (1-Stop vs 2-Stop vs 3-Stop)
    strat_freq = calculate_strategy_frequency(pit_summary)
    print("\n--- [GRID STRATEGY CATEGORY DISTRIBUTION] ---")
    print(strat_freq.to_string(index=False))

    # Save to data/processed
    out_stops = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_pitstops.csv"
    out_sum = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_pit_summary.csv"
    all_stops.to_csv(out_stops, index=False)
    pit_summary.to_csv(out_sum, index=False)
    print(f"\n[PERSISTENCE] Pit stop records saved to:\n  -> {out_stops}\n  -> {out_sum}")

    # Assertions
    assert len(ver_stops) == 2, f"Expected VER to have 2 pit stops, found {len(ver_stops)}"
    assert ver_stops.iloc[0]["PitInLap"] == 14, f"Expected VER Stop 1 on Lap 14, found {ver_stops.iloc[0]['PitInLap']}"
    assert "2-Stop" in strat_freq["StrategyCategory"].values, "2-Stop category missing from grid distribution!"

    print("\n[SUCCESS] Step 11 Pit Stop Analytics PASSED completely!")
    print("=" * 65)


if __name__ == "__main__":
    test_pitstops()
