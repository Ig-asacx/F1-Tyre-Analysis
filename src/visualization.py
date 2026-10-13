"""
src/visualization.py
====================
Formula 1 High-Fidelity Data Visualization Engine.

This module provides interactive Plotly charting functions customized with
official Pirelli tyre compound colors and dark-mode styling:
- Soft: #FF1801 (Red)
- Medium: #F5D033 (Yellow)
- Hard: #E0E0E0 (White / Silver)
- Intermediate: #39B54A (Green)
- Wet: #00A0DE (Blue)

Charts Generated:
1. Horizontal Stint Timeline (Gantt-style race strategy map sorted by finish).
2. Compound Usage & Distance Share Donut/Bar Chart.
3. Stint Lifespan Box Plots per compound.
4. Clean Flying Lap-Time Box/Violin Plots.
5. Tyre Age vs. Lap-Time Degradation Scatter with OLS Trendline.
6. Pit Stop Sequence & Window Timeline.
7. Strategy Category vs. Finishing Position Scatter/Bar.
8. Driver Head-to-Head Lap Time Comparison.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# Pirelli Compound Color Mapping
PIRELLI_COLORS = {
    "SOFT": "#FF1801",
    "MEDIUM": "#F5D033",
    "HARD": "#E0E0E0",
    "INTERMEDIATE": "#39B54A",
    "WET": "#00A0DE",
    "UNKNOWN": "#888888"
}

# Standardized Dark Theme Layout
DARK_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#111116",
    plot_bgcolor="#181820",
    font=dict(family="Arial, Helvetica, sans-serif", color="#FFFFFF", size=12),
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(
        bgcolor="rgba(24, 24, 32, 0.8)",
        bordercolor="#333340",
        borderwidth=1,
        font=dict(size=11)
    )
)


def _create_empty_figure(message: str = "Data unavailable for this selection.") -> go.Figure:
    """Creates a blank Plotly figure with a clear, user-facing notice."""
    fig = go.Figure()
    fig.add_annotation(
        text=f"⚠️ {message}",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="#A0A0B0", family="Arial")
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        **DARK_LAYOUT
    )
    return fig


def plot_stint_timeline(
    stints_df: pd.DataFrame,
    results_df: Optional[pd.DataFrame] = None
) -> go.Figure:
    """
    Renders a Gantt-style horizontal stint timeline for all drivers across the race.
    Drivers are sorted chronologically by classified finishing position (P1 at the top).
    """
    if stints_df is None or stints_df.empty:
        return _create_empty_figure("Stint timeline data unavailable for this session.")

    df = stints_df.copy()

    # Determine driver ordering (by finishing position if results_df supplied)
    if results_df is not None and not results_df.empty and "Abbreviation" in results_df.columns:
        res = results_df.copy()
        res["Pos"] = pd.to_numeric(res["PositionNumeric"] if "PositionNumeric" in res.columns else res["Position"], errors="coerce")
        sorted_drivers = res.sort_values(by="Pos", ascending=False)["Abbreviation"].dropna().tolist()
    else:
        sorted_drivers = sorted(df["Driver"].unique().tolist(), reverse=True)

    fig = go.Figure()

    # Add each stint segment as a horizontal bar
    for compound, group in df.groupby("Compound"):
        color = PIRELLI_COLORS.get(compound, "#888888")
        
        # Hover information
        hover_texts = [
            f"<b>Driver:</b> {row['Driver']} ({row['Team']})<br>"
            f"<b>Stint:</b> {row['StintNumber']} | <b>Compound:</b> {row['Compound']}<br>"
            f"<b>Laps:</b> {row['StartLap']} → {row['EndLap']} ({row['StintLength']} laps)<br>"
            f"<b>Avg Pace:</b> {row['AvgLapTime_Seconds']:.3f}s<br>"
            f"<b>Tyre Life at In-lap:</b> {row['EndTyreLife']}"
            for _, row in group.iterrows()
        ]

        fig.add_trace(go.Bar(
            name=compound,
            y=group["Driver"],
            x=group["StintLength"],
            base=group["StartLap"] - 1,
            orientation="h",
            marker=dict(
                color=color,
                line=dict(color="#111116", width=1.5)
            ),
            hoverinfo="text",
            hovertext=hover_texts,
            showlegend=True
        ))

    fig.update_layout(
        title="<b>Tyre Stint Timeline & Strategy Progression</b>",
        xaxis=dict(
            title="Race Lap Number",
            showgrid=True,
            gridcolor="#282835",
            dtick=5
        ),
        yaxis=dict(
            title="Driver (Ordered by Classification)",
            categoryorder="array",
            categoryarray=sorted_drivers
        ),
        barmode="stack",
        height=max(500, len(sorted_drivers) * 26),
        **DARK_LAYOUT
    )

    return fig


def plot_compound_usage(usage_df: pd.DataFrame) -> go.Figure:
    """
    Renders a donut chart illustrating the percentage distribution of race mileage per compound.
    """
    if usage_df is None or usage_df.empty:
        return _create_empty_figure("Tyre compound usage data unavailable for this session.")

    colors = [row["ColorHex"] for _, row in usage_df.iterrows()]

    fig = go.Figure(data=[go.Pie(
        labels=usage_df["Compound"],
        values=usage_df["TotalLapsRun"],
        hole=0.45,
        marker=dict(colors=colors, line=dict(color="#111116", width=2)),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Laps Run: %{value}<br>Share: %{percent}<extra></extra>"
    )])

    fig.update_layout(
        title="<b>Tyre Compound Usage Share (% of Total Race Laps)</b>",
        **DARK_LAYOUT
    )
    return fig


def plot_stint_length_box(stints_df: pd.DataFrame) -> go.Figure:
    """
    Renders a box plot showing the lifespan distribution (stint length in laps) per compound.
    """
    if stints_df is None or stints_df.empty:
        return _create_empty_figure("Stint lifespan data unavailable for this session.")

    fig = go.Figure()
    for compound, group in stints_df.groupby("Compound"):
        color = PIRELLI_COLORS.get(compound, "#888888")
        fig.add_trace(go.Box(
            y=group["StintLength"],
            name=compound,
            marker_color=color,
            boxpoints="all",
            jitter=0.3,
            pointpos=-1.8,
            boxmean=True
        ))

    fig.update_layout(
        title="<b>Tyre Stint Lifespan Distribution by Compound</b>",
        xaxis=dict(title="Compound"),
        yaxis=dict(title="Stint Length (Laps)", showgrid=True, gridcolor="#282835"),
        showlegend=False,
        **DARK_LAYOUT
    )
    return fig


def plot_lap_times_by_compound_box(cleaned_laps_df: pd.DataFrame) -> go.Figure:
    """
    Renders a box plot comparing clean representative lap times across tyre compounds.
    """
    if cleaned_laps_df is None or cleaned_laps_df.empty:
        return _create_empty_figure("Lap time data unavailable for this session.")

    clean_mask = cleaned_laps_df["IsRepresentativePace"] if "IsRepresentativePace" in cleaned_laps_df.columns else cleaned_laps_df["IsValidTime"]
    df = cleaned_laps_df[clean_mask].copy()

    if df.empty:
        return _create_empty_figure("No clean flying laps found for compound comparison.")

    fig = go.Figure()
    for compound, group in df.groupby("Compound"):
        if compound == "UNKNOWN":
            continue
        color = PIRELLI_COLORS.get(compound, "#888888")
        fig.add_trace(go.Box(
            y=group["LapTime_Seconds"],
            name=compound,
            marker_color=color,
            boxpoints="outliers",
            boxmean=True
        ))

    fig.update_layout(
        title="<b>Clean Lap Time Distribution by Tyre Compound</b>",
        xaxis=dict(title="Tyre Compound"),
        yaxis=dict(title="Lap Time (Seconds)", showgrid=True, gridcolor="#282835"),
        showlegend=False,
        **DARK_LAYOUT
    )
    return fig


def plot_driver_degradation(
    cleaned_laps_df: pd.DataFrame,
    driver: str,
    show_regression: bool = True
) -> go.Figure:
    """
    Plots lap time against tyre age for a driver, colored by compound with OLS trend lines.
    """
    if cleaned_laps_df is None or cleaned_laps_df.empty:
        return _create_empty_figure("Telemetry unavailable for this session.")

    drv_laps = cleaned_laps_df[cleaned_laps_df["Driver"] == driver.upper().strip()].copy()
    if drv_laps.empty:
        return _create_empty_figure(f"No telemetry found for driver {driver.upper()}.")

    clean_mask = drv_laps["IsRepresentativePace"] if "IsRepresentativePace" in drv_laps.columns else drv_laps["IsValidTime"]
    clean_df = drv_laps[clean_mask].sort_values("LapNumber").copy()

    if clean_df.empty:
        return _create_empty_figure(f"Insufficient representative flying laps for {driver.upper()} (DNF or non-racing laps).")

    fig = go.Figure()

    for stint_id, stint_group in clean_df.groupby("Stint"):
        compound = str(stint_group["Compound"].iloc[0])
        color = PIRELLI_COLORS.get(compound, "#888888")

        x = stint_group["TyreLife"] if "TyreLife" in stint_group.columns and stint_group["TyreLife"].notna().all() else np.arange(1, len(stint_group) + 1)
        y = stint_group["LapTime_Seconds"]

        # Scatter points
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="markers",
            name=f"Stint {int(stint_id)} ({compound})",
            marker=dict(color=color, size=8, line=dict(color="#111116", width=1)),
            hovertemplate="<b>Lap %{text}</b><br>Tyre Life: %{x}<br>Lap Time: %{y:.3f}s<extra></extra>",
            text=stint_group["LapNumber"]
        ))

        # Regression line
        if show_regression and len(x) >= 4:
            reg = stats.linregress(x, y)
            x_line = np.linspace(x.min(), x.max(), 50)
            y_line = reg.intercept + reg.slope * x_line
            fig.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                name=f"Stint {int(stint_id)} Trend (+{reg.slope:.3f}s/lap)",
                line=dict(color=color, dash="dash", width=1.8),
                hoverinfo="skip"
            ))

    fig.update_layout(
        title=f"<b>Tyre Degradation Analysis: {driver.upper()} (Lap Time vs. Tyre Age)</b>",
        xaxis=dict(title="Tyre Age (Laps Completed on Current Set)", showgrid=True, gridcolor="#282835"),
        yaxis=dict(title="Lap Time (Seconds)", showgrid=True, gridcolor="#282835"),
        **DARK_LAYOUT
    )
    return fig


def plot_pit_stops_timeline(
    pit_stops_df: pd.DataFrame,
    results_df: Optional[pd.DataFrame] = None
) -> go.Figure:
    """
    Renders pit stop events on a scatter timeline (Pit In Lap vs Driver).
    """
    if pit_stops_df is None or pit_stops_df.empty:
        return _create_empty_figure("No pit stop records found for this session.")

    df = pit_stops_df.copy()

    fig = go.Figure()
    for stop_num, group in df.groupby("StopNumber"):
        fig.add_trace(go.Scatter(
            x=group["PitInLap"],
            y=group["Driver"],
            mode="markers",
            name=f"Stop {stop_num}",
            marker=dict(
                size=12,
                symbol="circle",
                line=dict(color="#FFFFFF", width=1.5)
            ),
            hovertemplate=(
                "<b>%{y}</b> (Stop " + str(stop_num) + ")<br>"
                "Pit In Lap: %{x}<br>"
                "Transition: %{text}<extra></extra>"
            ),
            text=group["TyreTransition"]
        ))

    fig.update_layout(
        title="<b>Pit Stop Lap Occurrence Across Grid</b>",
        xaxis=dict(title="Race Lap Number", showgrid=True, gridcolor="#282835", dtick=5),
        yaxis=dict(title="Driver"),
        **DARK_LAYOUT
    )
    return fig


def plot_strategy_vs_finishing_position(strategy_pos_df: pd.DataFrame) -> go.Figure:
    """
    Renders a scatter plot showing Strategy Depth (NumberOfStops) against Classified Finishing Position.
    """
    if strategy_pos_df is None or strategy_pos_df.empty:
        return _create_empty_figure("Strategy classification data unavailable.")

    df = strategy_pos_df.dropna(subset=["FinishingPosition"]).copy()
    if df.empty:
        return _create_empty_figure("No classified finishers found for strategy correlation.")

    fig = px.scatter(
        df,
        x="NumberOfStops",
        y="FinishingPosition",
        color="StartingCompound",
        color_discrete_map=PIRELLI_COLORS,
        hover_name="Driver",
        hover_data=["Team", "FullStrategyDescription", "PositionsGained"],
        labels={
            "NumberOfStops": "Number of Pit Stops",
            "FinishingPosition": "Classified Finishing Position (P1–P20)"
        },
        title="<b>Strategy Depth vs. Final Race Finishing Position</b>"
    )

    fig.update_yaxes(autorange="reversed", dtick=1)
    fig.update_xaxes(dtick=1)
    fig.update_layout(**DARK_LAYOUT)
    return fig


def plot_driver_head_to_head(
    cleaned_laps_df: pd.DataFrame,
    driver_a: str,
    driver_b: str
) -> go.Figure:
    """
    Plots lap-by-lap pace comparison between two selected drivers.
    """
    if cleaned_laps_df is None or cleaned_laps_df.empty:
        return _create_empty_figure("Lap data unavailable for driver comparison.")

    da = driver_a.upper().strip()
    db = driver_b.upper().strip()

    laps_a = cleaned_laps_df[(cleaned_laps_df["Driver"] == da) & (cleaned_laps_df["IsRepresentativePace"])].sort_values("LapNumber")
    laps_b = cleaned_laps_df[(cleaned_laps_df["Driver"] == db) & (cleaned_laps_df["IsRepresentativePace"])].sort_values("LapNumber")

    if laps_a.empty or laps_b.empty:
        return _create_empty_figure(f"Insufficient clean flying laps for head-to-head comparison between {da} and {db}.")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=laps_a["LapNumber"],
        y=laps_a["LapTime_Seconds"],
        mode="lines+markers",
        name=da,
        line=dict(color="#00D2BE", width=2),
        marker=dict(size=5),
        hovertemplate=f"<b>{da}</b><br>Lap %{{x}}: %{{y:.3f}}s<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=laps_b["LapNumber"],
        y=laps_b["LapTime_Seconds"],
        mode="lines+markers",
        name=db,
        line=dict(color="#FF8700", width=2),
        marker=dict(size=5),
        hovertemplate=f"<b>{db}</b><br>Lap %{{x}}: %{{y:.3f}}s<extra></extra>"
    ))

    fig.update_layout(
        title=f"<b>Head-to-Head Flying Lap Pace: {da} vs. {db}</b>",
        xaxis=dict(title="Race Lap Number", showgrid=True, gridcolor="#282835"),
        yaxis=dict(title="Lap Time (Seconds)", showgrid=True, gridcolor="#282835"),
        **DARK_LAYOUT
    )
    return fig
