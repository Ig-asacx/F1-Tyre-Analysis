"""
tests/test_visualization.py
===========================
Unit and integration test for the F1 Data Visualization Engine.
Validates Plotly figure generation and exports interactive HTML charts to assets/.
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
from src.tyre_analysis import calculate_compound_usage_summary
from src.visualization import (
    plot_stint_timeline,
    plot_compound_usage,
    plot_stint_length_box,
    plot_lap_times_by_compound_box,
    plot_driver_degradation,
    plot_pit_stops_timeline,
    plot_strategy_vs_finishing_position,
    plot_driver_head_to_head
)


def test_visuals():
    print("=" * 65)
    print("STEP 13: VISUALIZATION ENGINE GENERATION & INTEGRATION TEST")
    print("=" * 65)

    raw_file = PROJECT_ROOT / "data" / "raw" / "2023_bahrain_race.pkl"
    cleaned_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_cleaned_laps.csv"
    stints_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_stints.csv"
    pitstops_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_pitstops.csv"
    strat_pos_file = PROJECT_ROOT / "data" / "processed" / "2023_bahrain_strategy_position.csv"

    if not cleaned_file.exists() or not stints_file.exists() or not raw_file.exists():
        print("[ERROR] Required data files missing. Run previous steps first.")
        return

    payload = load_raw_session_cache(raw_file)
    results_df = payload["results"]
    cleaned_laps = pd.read_csv(cleaned_file)
    stints = pd.read_csv(stints_file)
    pitstops = pd.read_csv(pitstops_file) if pitstops_file.exists() else pd.DataFrame()
    strat_pos = pd.read_csv(strat_pos_file) if strat_pos_file.exists() else pd.DataFrame()

    # 1. Stint Timeline Chart
    fig1 = plot_stint_timeline(stints, results_df)
    assert len(fig1.data) > 0, "Stint timeline figure has no traces!"
    print(f"  [✓] Chart 1: Stint Timeline generated ({len(fig1.data)} compound traces)")

    # 2. Compound Usage Donut Chart
    usage_df = calculate_compound_usage_summary(cleaned_laps)
    fig2 = plot_compound_usage(usage_df)
    assert len(fig2.data) > 0, "Compound usage figure has no traces!"
    print(f"  [✓] Chart 2: Compound Usage Donut generated")

    # 3. Stint Length Box Plot
    fig3 = plot_stint_length_box(stints)
    assert len(fig3.data) > 0, "Stint box plot has no traces!"
    print(f"  [✓] Chart 3: Stint Lifespan Box Plot generated")

    # 4. Lap Times Box Plot
    fig4 = plot_lap_times_by_compound_box(cleaned_laps)
    assert len(fig4.data) > 0, "Lap time box plot has no traces!"
    print(f"  [✓] Chart 4: Compound Lap Times Box Plot generated")

    # 5. Driver Degradation Regression (VER)
    fig5 = plot_driver_degradation(cleaned_laps, "VER")
    assert len(fig5.data) > 0, "Degradation chart has no traces!"
    print(f"  [✓] Chart 5: Verstappen Degradation Scatter with OLS Trends generated")

    # 6. Pit Stops Timeline
    fig6 = plot_pit_stops_timeline(pitstops)
    assert len(fig6.data) > 0, "Pit stop timeline has no traces!"
    print(f"  [✓] Chart 6: Pit Stop Timeline generated")

    # 7. Strategy vs. Finishing Position
    fig7 = plot_strategy_vs_finishing_position(strat_pos)
    assert len(fig7.data) > 0, "Strategy vs position chart has no traces!"
    print(f"  [✓] Chart 7: Strategy vs Finishing Position Scatter generated")

    # 8. Head-to-Head Comparison (VER vs ALO)
    fig8 = plot_driver_head_to_head(cleaned_laps, "VER", "ALO")
    assert len(fig8.data) == 2, "Head to head chart missing driver traces!"
    print(f"  [✓] Chart 8: Driver Head-to-Head Pace (VER vs ALO) generated")

    # Save an interactive standalone HTML dashboard artifact
    assets_dir = PROJECT_ROOT / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    demo_html = assets_dir / "strategy_timeline_preview.html"
    fig1.write_html(str(demo_html), include_plotlyjs="cdn")
    print(f"\n[ARTIFACT] Interactive timeline exported to:\n  -> {demo_html}")

    print("\n[SUCCESS] Step 13 Visualization Engine PASSED completely!")
    print("=" * 65)


if __name__ == "__main__":
    test_visuals()
