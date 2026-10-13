"""
tests/test_real_race_loader.py
==============================
Verification script to load real Formula 1 session data using FastF1,
test local disk caching, and inspect raw tyre telemetry fields.

Target Race: 2023 Bahrain Grand Prix (Round 1)
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import (
    load_race_session,
    extract_session_payload,
    save_raw_session_cache,
    setup_fastf1_cache
)


def run_test():
    print("=" * 65)
    print("STEP 5: REAL F1 SESSION DATA INGESTION TEST")
    print("=" * 65)
    
    # 1. Setup cache
    cache_path = setup_fastf1_cache()
    print(f"[CACHE] Active Cache Directory: {cache_path}")

    # 2. Load 2023 Bahrain GP Race Session
    year = 2023
    gp = "Bahrain"
    session_type = "R"
    print(f"[FETCH] Querying FastF1 API for: {year} {gp} Grand Prix ({session_type})...")
    
    session = load_race_session(year=year, gp_identifier=gp, session_type=session_type)
    print("[FETCH] Session loaded successfully!")

    # 3. Extract Payload
    payload = extract_session_payload(session)
    meta = payload["metadata"]
    results = payload["results"]
    laps = payload["laps"]
    
    print("\n--- [SESSION METADATA] ---")
    print(f"Official Name: {meta['official_name']}")
    print(f"Circuit:       {meta['circuit_name']}, {meta['country']}")
    print(f"Date:          {meta['session_date']}")
    print(f"Total Laps:    {meta['total_laps']}")
    print(f"Total Drivers: {len(payload['drivers'])}")
    print(f"Total Teams:   {len(payload['teams'])}")

    print("\n--- [TOP 5 CLASSIFICATION] ---")
    top_5 = results.head(5)[["Position", "BroadcastName", "TeamName", "Points", "Status"]]
    print(top_5.to_string(index=False))

    print("\n--- [TYRE COMPOUND TELEMETRY AUDIT] ---")
    compounds_used = laps["Compound"].dropna().unique().tolist()
    print(f"Tyre Compounds Detected in Session: {compounds_used}")
    print(f"Total Lap Records Extracted:        {len(laps):,}")

    # Inspect Winner's Lap Sample
    winner_code = results.iloc[0]["Abbreviation"]
    winner_laps = laps[laps["Driver"] == winner_code]
    print(f"\n--- [SAMPLE LAPS: {winner_code} (Race Winner)] ---")
    sample_cols = ["LapNumber", "LapTime", "Compound", "TyreLife", "Stint", "PitInTime"]
    print(winner_laps[sample_cols].head(8).to_string(index=False))

    # 4. Save Raw Snapshot for Offline Viva Demo
    offline_file = PROJECT_ROOT / "data" / "raw" / f"{year}_{gp.lower()}_race.pkl"
    save_raw_session_cache(payload, offline_file)
    print(f"\n[OFFLINE PERSISTENCE] Session payload saved to:\n  -> {offline_file}")
    
    print("\n[SUCCESS] Step 5 Data Ingestion Test PASSED completely!")
    print("=" * 65)


if __name__ == "__main__":
    run_test()
