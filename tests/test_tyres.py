"""
tests/test_tyres.py
===================
Unit and integration test for Tyre Compound Analytics Engine.
Evaluates tyre usage, lifespan, and pace metrics on Bahrain 2023 data.
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

from src.tyre_analysis import (
    calculate_compound_usage_summary,
    calculate_compound_stint_metrics,
    calculate_compound_pace_metrics,
    get_comprehensive_tyre_report
)


def test_tyres():
    print("=" * 65)
    print("STEP 8: TYRE COMPOUND USAGE & PERFORMANCE TEST")
    print("=" * 65)

    cleaned_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_cleaned_laps.csv"
    stints_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_stints.csv"

    if not cleaned_file.exists() or not stints_file.exists():
        print("[ERROR] Required processed files missing. Run previous steps first.")
        return

    cleaned_laps = pd.read_csv(cleaned_file)
    stints = pd.read_csv(stints_file)

    # 1. Compound Usage Summary
    usage_df = calculate_compound_usage_summary(cleaned_laps)
    print("\n--- [TYRE COMPOUND USAGE DISTRIBUTION] ---")
    print(usage_df[["Compound", "TotalLapsRun", "PercentageOfRaceLaps", "UniqueDriversUsing"]].to_string(index=False))

    # 2. Stint Lifespan Metrics
    lifespan_df = calculate_compound_stint_metrics(stints)
    print("\n--- [TYRE STINT LIFESPAN STATISTICS (LAPS)] ---")
    print(lifespan_df.to_string(index=False))

    # 3. Clean Pace Metrics
    pace_df = calculate_compound_pace_metrics(cleaned_laps)
    print("\n--- [REPRESENTATIVE LAP PACE BY COMPOUND] ---")
    pace_cols = ["Compound", "RepresentativeLapCount", "MedianPace_Seconds", "FastestLap_Seconds", "DeltaToFastest_Seconds"]
    print(pace_df[pace_cols].to_string(index=False))

    # 4. Master Comprehensive Report
    report = get_comprehensive_tyre_report(cleaned_laps, stints)
    out_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_tyre_summary.csv"
    report.to_csv(out_file, index=False)
    print(f"\n[PERSISTENCE] Master tyre report saved to:\n  -> {out_file}")

    # Assertions
    assert "HARD" in usage_df["Compound"].values, "Hard compound missing from usage!"
    assert "SOFT" in usage_df["Compound"].values, "Soft compound missing from usage!"
    assert len(pace_df) > 0, "No pace metrics calculated!"

    print("\n[SUCCESS] Step 8 Tyre Compound Analytics PASSED completely!")
    print("=" * 65)


if __name__ == "__main__":
    test_tyres()
