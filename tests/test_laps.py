"""
tests/test_laps.py
==================
Unit and integration test for Lap-Time Performance & Driver/Team Comparison Engine.
Tests against Bahrain 2023 cleaned data.
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

from src.lap_analysis import (
    calculate_driver_pace_summary,
    calculate_team_pace_summary,
    calculate_driver_compound_breakdown,
    calculate_rolling_pace,
    compare_drivers_head_to_head
)


def test_laps():
    print("=" * 65)
    print("STEP 9: LAP-TIME PERFORMANCE & DRIVER/TEAM PACE TEST")
    print("=" * 65)

    cleaned_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_cleaned_laps.csv"
    if not cleaned_file.exists():
        print("[ERROR] Required cleaned laps file missing. Run previous steps first.")
        return

    cleaned_laps = pd.read_csv(cleaned_file)

    # 1. Driver Pace Summary
    driver_summary = calculate_driver_pace_summary(cleaned_laps)
    print("\n--- [TOP 6 DRIVER PACE RANKING (BY MEDIAN FLYING PACE)] ---")
    d_cols = ["Driver", "Team", "RepresentativeLaps", "MedianPace_Seconds", "FastestLap_Seconds", "PaceDeltaToLeader_Seconds", "Consistency_CV_Pct"]
    print(driver_summary[d_cols].head(6).to_string(index=False))

    # 2. Team Pace Summary
    team_summary = calculate_team_pace_summary(cleaned_laps)
    print("\n--- [TOP 5 CONSTRUCTOR PACE BENCHMARK] ---")
    t_cols = ["Team", "TotalCleanLaps", "MedianTeamPace_Seconds", "BestTeamLap_Seconds", "PaceDeltaToFastestTeam"]
    print(team_summary[t_cols].head(5).to_string(index=False))

    # 3. Single Driver Compound Breakdown (VER)
    ver_breakdown = calculate_driver_compound_breakdown(cleaned_laps, "VER")
    print("\n--- [VERSTAPPEN COMPOUND PACE BREAKDOWN] ---")
    print(ver_breakdown.to_string(index=False))

    # 4. Head-to-Head Comparison: VER (P1) vs ALO (P3)
    h2h = compare_drivers_head_to_head(cleaned_laps, "VER", "ALO")
    print("\n--- [HEAD-TO-HEAD COMPARISON: VER vs ALO] ---")
    print(f"Faster Driver (Median Pace): {h2h['faster_driver_median']}")
    print(f"Median Pace Delta (VER - ALO): {h2h['median_pace_delta_a_minus_b']} seconds")
    print(f"Fastest Lap Delta (VER - ALO): {h2h['fastest_lap_delta_a_minus_b']} seconds")

    # 5. Rolling Pace Calculation
    rolling_df = calculate_rolling_pace(cleaned_laps, "ALO", window=3)
    print("\n--- [FERNANDO ALONSO (ALO) ROLLING 3-LAP PACE (LAPS 20-25)] ---")
    sample_rolling = rolling_df[(rolling_df["LapNumber"] >= 20) & (rolling_df["LapNumber"] <= 25)]
    print(sample_rolling[["LapNumber", "LapTime_Seconds", "RollingMedianPace", "Compound"]].to_string(index=False))

    # Save driver pace summary
    out_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_driver_pace.csv"
    driver_summary.to_csv(out_file, index=False)
    print(f"\n[PERSISTENCE] Driver pace summary saved to:\n  -> {out_file}")

    # Assertions
    assert driver_summary.iloc[0]["Driver"] in ["VER", "PER"], "Expected Red Bull driver to top median pace!"
    assert team_summary.iloc[0]["Team"] == "Red Bull Racing", "Expected Red Bull Racing as top constructor!"

    print("\n[SUCCESS] Step 9 Lap-Time Analysis PASSED completely!")
    print("=" * 65)


if __name__ == "__main__":
    test_laps()
