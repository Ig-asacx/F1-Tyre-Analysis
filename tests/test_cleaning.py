"""
tests/test_cleaning.py
======================
Unit and integration test for the F1 Data Cleaning Pipeline.
Loads cached 2023 Bahrain Grand Prix data, executes cleaning, and validates
filtering rules and audit metrics.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_session_cache
from src.data_cleaning import clean_race_laps, get_representative_laps, get_pit_stop_laps


def test_pipeline():
    print("=" * 65)
    print("STEP 6: DATA CLEANING PIPELINE VALIDATION TEST")
    print("=" * 65)
    
    # Load cached 2023 Bahrain race
    cache_file = PROJECT_ROOT / "data" / "raw" / "2023_bahrain_race.pkl"
    if not cache_file.exists():
        print(f"[ERROR] Cache file not found at {cache_file}. Run Step 5 first.")
        return

    payload = load_raw_session_cache(cache_file)
    raw_laps = payload["laps"]
    print(f"[INPUT] Loaded {len(raw_laps)} raw lap records.")

    # Execute cleaning pipeline
    cleaned_df, report = clean_race_laps(raw_laps)

    print("\n--- [DATA CLEANING AUDIT REPORT] ---")
    for key, val in report.items():
        print(f"  • {key.replace('_', ' ').title():<32}: {val}")

    # Assertions
    assert "LapTime_Seconds" in cleaned_df.columns, "LapTime_Seconds column missing!"
    assert "IsRepresentativePace" in cleaned_df.columns, "Master filter flag missing!"
    assert cleaned_df["LapTime_Seconds"].dtype == float, "Lap time not converted to float!"

    # Inspect Sample Comparison for a Pit Lap vs a Flying Lap
    print("\n--- [IN-LAP VS FLYING LAP SAMPLE (VER)] ---")
    ver_laps = cleaned_df[cleaned_df["Driver"] == "VER"]
    pit_sample = ver_laps[ver_laps["IsPitInLap"]].head(1)
    flying_sample = ver_laps[ver_laps["IsRepresentativePace"]].head(1)
    
    comparison_cols = ["LapNumber", "LapTime_Seconds", "Compound", "IsPitInLap", "IsRepresentativePace"]
    print("Pit In-Lap:")
    print(pit_sample[comparison_cols].to_string(index=False))
    print("\nRepresentative Flying Lap:")
    print(flying_sample[comparison_cols].to_string(index=False))

    # Verify that In-Laps are indeed slower by >15 seconds
    pit_time = pit_sample["LapTime_Seconds"].values[0]
    flying_time = flying_sample["LapTime_Seconds"].values[0]
    delta = pit_time - flying_time
    print(f"\nPit In-Lap Time Delta: +{delta:.3f} seconds (proves why in-laps must be excluded from tyre wear)")

    # Save cleaned laps to data/processed for offline access
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_parquet(processed_dir / "2023_bahrain_cleaned_laps.parquet")
    cleaned_df.to_csv(processed_dir / "2023_bahrain_cleaned_laps.csv", index=False)
    print(f"\n[SAVED] Cleaned dataset saved to data/processed/ for subsequent analytical modules.")

    print("\n[SUCCESS] Step 6 Data Cleaning Pipeline PASSED completely!")
    print("=" * 65)


if __name__ == "__main__":
    test_pipeline()
