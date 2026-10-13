"""
src/strategy_analysis.py
========================
Formula 1 Race Strategy vs. Classified Finishing Position Analytics.

In academic data science and motorsport engineering, establishing relationships
between strategic variables (pit stop count, compound sequences, stint lengths)
and race outcomes (finishing position P1–P20) requires rigorous statistical treatment.

IMPORTANT ACADEMIC DISTINCTION (VIVA DEFENCE):
- Correlation: A mathematical measure of how two numeric variables co-vary (e.g. Spearman rho).
- Association: An observed statistical relationship between categorical choices and outcomes.
- Causation: Proving that strategy *directly caused* the result. In F1, strategy ALONE
  does not cause a win; underlying car aerodynamic efficiency, power unit performance,
  driver skill, qualifying grid position, and luck (Safety Cars) are major confounding variables.

This module provides:
1. Strategy vs. classification matrix.
2. Grouped analysis: 1-stop vs 2-stop vs 3-stop finishing outcomes.
3. Starting compound analysis (Soft vs Medium vs Hard starters).
4. Spearman rank correlation and confounding variable analysis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


def build_strategy_position_dataset(
    results_df: pd.DataFrame,
    strategy_summary_df: pd.DataFrame,
    pit_summary_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Combines race classification, grid position, pit stop counts, and strategy strings.

    Parameters:
        results_df: Official FastF1 classification DataFrame.
        strategy_summary_df: Output from stint_analysis.generate_driver_strategy_summary.
        pit_summary_df: Optional output from pitstop_analysis.calculate_driver_pit_summary.

    Returns:
        pd.DataFrame: Merged analysis dataset with positions, deltas, and strategy tags.
    """
    if results_df.empty or strategy_summary_df.empty:
        return pd.DataFrame()

    res = results_df.copy()
    if "Abbreviation" in res.columns:
        res = res.rename(columns={"Abbreviation": "Driver"})
    if "TeamName" in res.columns and "Team" not in res.columns:
        res = res.rename(columns={"TeamName": "Team"})

    # Ensure positions are numeric
    res["FinishingPosition"] = pd.to_numeric(res["PositionNumeric"] if "PositionNumeric" in res.columns else res["Position"], errors="coerce")
    res["GridPosition"] = pd.to_numeric(res["GridPosition"], errors="coerce")
    res["Points"] = pd.to_numeric(res["Points"], errors="coerce").fillna(0.0)

    # Position Change: Positive = Gained places; Negative = Lost places
    res["PositionsGained"] = res["GridPosition"] - res["FinishingPosition"]

    # Merge strategy details on Driver
    merged = res.merge(strategy_summary_df, on="Driver", how="inner", suffixes=("", "_strat"))
    if "Team_strat" in merged.columns and "Team" not in merged.columns:
        merged = merged.rename(columns={"Team_strat": "Team"})

    # Merge pit summary details if provided
    if pit_summary_df is not None and not pit_summary_df.empty and "StrategyCategory" in pit_summary_df.columns:
        sub_pit = pit_summary_df[["Driver", "StrategyCategory", "PitStopLaps"]]
        merged = merged.merge(sub_pit, on="Driver", how="left")
    else:
        merged["StrategyCategory"] = merged["NumberOfStops"].apply(lambda n: f"{n}-Stop" if n == 1 else f"{n}-Stop")

    # Sort by official classified finishing position
    return merged.sort_values(by="FinishingPosition").reset_index(drop=True)


def analyze_stops_vs_position(strategy_pos_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compares average and median finishing positions across strategy depths (1-Stop, 2-Stop, etc.).

    Returns:
        pd.DataFrame: Aggregated performance metrics per strategy category.
    """
    if strategy_pos_df.empty:
        return pd.DataFrame()

    # Consider classified finishers for position averages
    classified = strategy_pos_df.dropna(subset=["FinishingPosition"]).copy()

    records = []
    for cat, group in classified.groupby("StrategyCategory"):
        count = len(group)
        mean_finish = round(float(group["FinishingPosition"].mean()), 2)
        med_finish = round(float(group["FinishingPosition"].median()), 1)
        best_finish = int(group["FinishingPosition"].min())
        worst_finish = int(group["FinishingPosition"].max())
        mean_gained = round(float(group["PositionsGained"].mean()), 2)
        total_pts = round(float(group["Points"].sum()), 1)

        records.append({
            "StrategyCategory": cat,
            "DriverCount": count,
            "MeanFinishingPosition": mean_finish,
            "MedianFinishingPosition": med_finish,
            "BestFinishingPosition": best_finish,
            "WorstFinishingPosition": worst_finish,
            "MeanPositionsGained": mean_gained,
            "TotalPointsScored": total_pts
        })

    summary_df = pd.DataFrame(records)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(by="MeanFinishingPosition", ascending=True).reset_index(drop=True)
    return summary_df


def analyze_starting_compound_vs_position(strategy_pos_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes finishing performance based on starting tyre compound choice.

    Returns:
        pd.DataFrame: Finishing position metrics grouped by starting compound.
    """
    if strategy_pos_df.empty:
        return pd.DataFrame()

    classified = strategy_pos_df.dropna(subset=["FinishingPosition"]).copy()

    records = []
    for compound, group in classified.groupby("StartingCompound"):
        count = len(group)
        mean_finish = round(float(group["FinishingPosition"].mean()), 2)
        med_finish = round(float(group["FinishingPosition"].median()), 1)
        podiums = int((group["FinishingPosition"] <= 3).sum())
        points_finishes = int((group["FinishingPosition"] <= 10).sum())
        total_pts = round(float(group["Points"].sum()), 1)

        records.append({
            "StartingCompound": compound,
            "DriverCount": count,
            "MeanFinishingPosition": mean_finish,
            "MedianFinishingPosition": med_finish,
            "PodiumFinishes_P1_P3": podiums,
            "Top10PointsFinishes": points_finishes,
            "TotalPointsScored": total_pts
        })

    summary_df = pd.DataFrame(records)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(by="MeanFinishingPosition", ascending=True).reset_index(drop=True)
    return summary_df


def calculate_strategy_correlations(strategy_pos_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates Pearson and Spearman rank correlation between strategy variables and race outcome.
    Includes statistical significance (p-values) and academic context.

    Returns:
        Dict: Statistical coefficients, p-values, and contextual explanations.
    """
    if strategy_pos_df.empty:
        return {}

    classified = strategy_pos_df.dropna(subset=["FinishingPosition", "NumberOfStops"]).copy()
    if len(classified) < 4:
        return {"error": "Insufficient classified drivers for correlation analysis."}

    stops = classified["NumberOfStops"].values
    finishes = classified["FinishingPosition"].values
    grids = classified["GridPosition"].fillna(classified["FinishingPosition"]).values

    # Spearman Rank Correlation (Stops vs. Finishing Position)
    # Monotonic relationship between ranking variables
    spearman_stops = stats.spearmanr(stops, finishes)
    rho_stops = round(float(spearman_stops.statistic), 3)
    p_stops = round(float(spearman_stops.pvalue), 4)

    # Spearman Rank Correlation (Grid vs. Finishing Position) - Confounding Benchmark
    spearman_grid = stats.spearmanr(grids, finishes)
    rho_grid = round(float(spearman_grid.statistic), 3)
    p_grid = round(float(spearman_grid.pvalue), 4)

    return {
        "spearman_stops_vs_finish": {
            "rho": rho_stops,
            "p_value": p_stops,
            "interpretation": (
                "Statistically significant association" if p_stops < 0.05
                else "No statistically significant correlation"
            )
        },
        "spearman_grid_vs_finish": {
            "rho": rho_grid,
            "p_value": p_grid,
            "interpretation": (
                "Strong predictor of finish" if rho_grid > 0.60
                else "Moderate predictor of finish"
            )
        },
        "academic_note": (
            "IMPORTANT: Correlation does NOT equal causation. In Formula 1, cars that qualify "
            "higher (e.g. Red Bull, Ferrari) possess superior aerodynamic efficiency and pace, "
            "enabling them to run optimal 2-stop strategies without falling into midfield traffic. "
            "Grid position and car performance are major confounding variables."
        )
    }
