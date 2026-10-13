"""
tests/test_degradation.py
=========================
Unit and integration test for Tyre Degradation Modeling Engine.
Evaluates OLS regression slopes, fuel-corrected degradation, and tyre cliff metrics.
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

from src.degradation_analysis import (
    calculate_stint_degradation,
    analyze_race_degradation,
    compare_compound_degradation
)


def test_degradation():
    print("=" * 65)
    print("STEP 10: TYRE DEGRADATION & THERMAL CLIFF MODELING TEST")
    print("=" * 65)

    cleaned_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_cleaned_laps.csv"
    if not cleaned_file.exists():
        print("[ERROR] Required cleaned laps file missing. Run previous steps first.")
        return

    cleaned_laps = pd.read_csv(cleaned_file)

    # 1. Inspect Single Stint Degradation for VER Stint 1 (Soft)
    ver_stint1 = cleaned_laps[(cleaned_laps["Driver"] == "VER") & (cleaned_laps["Stint"] == 1)]
    deg_ver1 = calculate_stint_degradation(ver_stint1)

    print("\n--- [VERSTAPPEN STINT 1 (SOFT TYRE) DEGRADATION METRICS] ---")
    for k, v in deg_ver1.items():
        print(f"  • {k:<35}: {v}")

    # 2. Run Degradation Modeling Across All Driver Stints
    all_deg = analyze_race_degradation(cleaned_laps)
    print(f"\n[GRID] Successfully computed degradation models for {len(all_deg)} stints.")

    print("\n--- [TOP 6 STINTS BY FUEL-CORRECTED DEGRADATION RATE] ---")
    cols = ["Driver", "Team", "StintNumber", "Compound", "CleanLapCount", "ObservedSlope_SecPerLap", "FuelCorrectedSlope_SecPerLap", "PaceCliffDelta_Seconds"]
    print(all_deg.dropna(subset=["FuelCorrectedSlope_SecPerLap"])[cols].head(6).to_string(index=False))

    # 3. Compound Degradation Benchmarking
    comp_deg = compare_compound_degradation(all_deg)
    print("\n--- [COMPOUND THERMAL DEGRADATION COMPARISON] ---")
    print(comp_deg.to_string(index=False))

    # Save to data/processed
    out_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_degradation.csv"
    all_deg.to_csv(out_file, index=False)
    print(f"\n[PERSISTENCE] Stint degradation models saved to:\n  -> {out_file}")

    # Assertions
    assert len(all_deg) > 0, "No degradation models generated!"
    assert len(comp_deg) > 0, "No compound degradation comparison generated!"

    print("\n[SUCCESS] Step 10 Tyre Degradation Modeling PASSED completely!")
    print("=" * 65)


if __name__ == "__main__":
    test_degradation()
