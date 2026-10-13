"""
tests/test_stints.py
====================
Unit and integration test for Stint Detection and Strategy String Generation.
Tests against real 2023 Bahrain Grand Prix data.
"""

import sys
from pathlib import Path
import pandas as pd

# Ensure console supports UTF-8 on Windows
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stint_analysis import detect_driver_stints, extract_all_stints, generate_driver_strategy_summary


def test_stint_detection():
    print("=" * 65)
    print("STEP 7: TYRE STINT DETECTION & STRATEGY SEQUENCE TEST")
    print("=" * 65)

    # Load cleaned laps from data/processed
    cleaned_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_cleaned_laps.csv"
    if not cleaned_file.exists():
        print(f"[ERROR] Cleaned file not found at {cleaned_file}. Run Step 6 first.")
        return

    cleaned_laps = pd.read_csv(cleaned_file)
    print(f"[INPUT] Loaded {len(cleaned_laps)} cleaned laps.")

    # 1. Test Stint Detection for Max Verstappen (VER)
    ver_laps = cleaned_laps[cleaned_laps["Driver"] == "VER"]
    ver_stints = detect_driver_stints(ver_laps)
    
    print("\n--- [MAX VERSTAPPEN (VER) STINT BREAKDOWN] ---")
    stint_cols = ["StintNumber", "Compound", "StartLap", "EndLap", "StintLength", "StartTyreLife", "EndTyreLife", "AvgLapTime_Seconds"]
    print(ver_stints[stint_cols].to_string(index=False))

    # 2. Extract All Stints Across the Entire Grid
    all_stints = extract_all_stints(cleaned_laps)
    print(f"\n[GRID] Successfully extracted {len(all_stints)} total stints across {all_stints['Driver'].nunique()} drivers.")

    # 3. Generate Strategy Strings (e.g. S -> S -> H)
    strategy_summary = generate_driver_strategy_summary(all_stints)
    print("\n--- [TOP 8 STRATEGY SEQUENCES IDENTIFIED] ---")
    strat_cols = ["Driver", "Team", "NumberOfStops", "FullStrategyDescription", "StartingCompound", "FinalCompound"]
    print(strategy_summary[strat_cols].head(8).to_string(index=False))

    # Assertions
    ver_strat = strategy_summary[strategy_summary["Driver"] == "VER"]["FullStrategyDescription"].values[0]
    alo_strat = strategy_summary[strategy_summary["Driver"] == "ALO"]["FullStrategyDescription"].values[0]
    
    print(f"\n[VERIFIED] VER Strategy: {ver_strat}")
    print(f"[VERIFIED] ALO Strategy: {alo_strat}")
    
    assert "S → S → H (2-Stop)" in ver_strat, f"Unexpected VER strategy: {ver_strat}"
    assert "S → H → H (2-Stop)" in alo_strat, f"Unexpected ALO strategy: {alo_strat}"

    # Save to data/processed for subsequent modules
    out_stints = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_stints.csv"
    out_strat = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_strategies.csv"
    all_stints.to_csv(out_stints, index=False)
    strategy_summary.to_csv(out_strat, index=False)
    print(f"\n[PERSISTENCE] Stint and strategy summaries saved to:\n  -> {out_stints}\n  -> {out_strat}")

    print("\n[SUCCESS] Step 7 Stint Detection Test PASSED completely!")
    print("=" * 65)


if __name__ == "__main__":
    test_stint_detection()
