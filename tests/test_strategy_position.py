"""
tests/test_strategy_position.py
===============================
Unit and integration test for Strategy vs Finishing Position Engine.
Evaluates strategy outcome metrics and correlation vs causation distinctions.
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
from src.strategy_analysis import (
    build_strategy_position_dataset,
    analyze_stops_vs_position,
    analyze_starting_compound_vs_position,
    calculate_strategy_correlations
)


def test_strategy_position():
    print("=" * 65)
    print("STEP 12: STRATEGY VS FINISHING POSITION & CORRELATION TEST")
    print("=" * 65)

    raw_file = PROJECT_ROOT / "data" / "raw" / "2023_bahrain_race.pkl"
    strat_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_strategies.csv"
    pit_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_pit_summary.csv"

    if not raw_file.exists() or not strat_file.exists():
        print("[ERROR] Required data files missing. Run previous steps first.")
        return

    payload = load_raw_session_cache(raw_file)
    results_df = payload["results"]
    strat_df = pd.read_csv(strat_file)
    pit_df = pd.read_csv(pit_file) if pit_file.exists() else None

    # 1. Build Merged Dataset
    strat_pos_df = build_strategy_position_dataset(results_df, strat_df, pit_df)
    print("\n--- [TOP 8 FINISHERS STRATEGY SUMMARY] ---")
    p_cols = ["FinishingPosition", "Driver", "Team", "GridPosition", "PositionsGained", "StrategyCategory", "FullStrategyDescription"]
    print(strat_pos_df[p_cols].head(8).to_string(index=False))

    # 2. Stops vs Finishing Position
    stops_analysis = analyze_stops_vs_position(strat_pos_df)
    print("\n--- [STRATEGY DEPTH (STOPS) VS FINISHING POSITION] ---")
    print(stops_analysis.to_string(index=False))

    # 3. Starting Compound vs Finishing Position
    start_analysis = analyze_starting_compound_vs_position(strat_pos_df)
    print("\n--- [STARTING TYRE COMPOUND OUTCOMES] ---")
    print(start_analysis.to_string(index=False))

    # 4. Correlation Analysis
    corr_results = calculate_strategy_correlations(strat_pos_df)
    print("\n--- [STATISTICAL CORRELATION & CAUSATION AUDIT] ---")
    print(f"Spearman Rho (Stops vs Finish): {corr_results['spearman_stops_vs_finish']['rho']} (p={corr_results['spearman_stops_vs_finish']['p_value']})")
    print(f"  -> Interpretation: {corr_results['spearman_stops_vs_finish']['interpretation']}")
    print(f"Spearman Rho (Grid vs Finish):  {corr_results['spearman_grid_vs_finish']['rho']} (p={corr_results['spearman_grid_vs_finish']['p_value']})")
    print(f"  -> Interpretation: {corr_results['spearman_grid_vs_finish']['interpretation']}")
    print(f"\nAcademic Defence Note:\n  {corr_results['academic_note']}")

    # Save to data/processed
    out_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_strategy_position.csv"
    strat_pos_df.to_csv(out_file, index=False)
    print(f"\n[PERSISTENCE] Strategy vs position dataset saved to:\n  -> {out_file}")

    # Assertions
    assert len(strat_pos_df) > 0, "No records in strategy position dataset!"
    assert "2-Stop" in stops_analysis["StrategyCategory"].values, "2-Stop missing from stops analysis!"

    print("\n[SUCCESS] Step 12 Strategy vs Finishing Position PASSED completely!")
    print("=" * 65)


if __name__ == "__main__":
    test_strategy_position()
