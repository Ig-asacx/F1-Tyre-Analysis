"""
src/data_loader.py
===================
Formula 1 Session Data Ingestion & Caching Engine.

This module interfaces directly with the official FastF1 API to retrieve:
- Championship event calendars
- Full race session telemetry & timing matrices
- Driver classifications and race outcomes
- Lap-by-lap tyre compound allocation and stint metadata

All network queries are persisted to a local disk cache to minimize API load,
comply with rate limits, and provide instant sub-second retrieval for repeat queries.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import fastf1
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Default Cache Directory
DEFAULT_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"


class F1DataError(Exception):
    """Custom exception raised when F1 session data retrieval or parsing fails."""
    pass


def setup_fastf1_cache(cache_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Enables and verifies the FastF1 local file cache.

    Parameters:
        cache_dir: Custom filesystem path for caching. Defaults to 'data/cache/'.

    Returns:
        Path: The absolute path of the active cache directory.
    """
    target_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        fastf1.Cache.enable_cache(str(target_dir))
        logger.info(f"FastF1 cache initialized successfully at: {target_dir}")
    except Exception as exc:
        logger.warning(f"Could not enable FastF1 cache at {target_dir}: {exc}. Proceeding without cache.")
        
    return target_dir


def get_available_seasons(min_year: int = 2018, max_year: int = 2024) -> List[int]:
    """
    Returns supported championship seasons with high-fidelity tyre compound data.
    
    F1 standardised tyre compounds (Soft, Medium, Hard) across all races in 2019,
    with full digital telemetry logs available reliably from 2018 onwards.
    """
    return list(range(min_year, max_year + 1))


def get_season_events(year: int) -> pd.DataFrame:
    """
    Fetches the Grand Prix calendar and event metadata for a specified season.

    Parameters:
        year: Championship season (e.g. 2023, 2024)

    Returns:
        pd.DataFrame containing RoundNumber, EventName, Country, Location, EventDate
    """
    setup_fastf1_cache()
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        if schedule is None or schedule.empty:
            raise F1DataError(f"No race calendar found for season {year}.")
            
        # Filter for valid championship rounds
        valid_events = schedule[schedule["RoundNumber"] > 0].copy()
        columns_to_keep = ["RoundNumber", "Country", "Location", "OfficialEventName", "EventName", "EventDate"]
        available_cols = [c for c in columns_to_keep if c in valid_events.columns]
        return valid_events[available_cols].reset_index(drop=True)
    except Exception as exc:
        logger.error(f"Failed to fetch event schedule for {year}: {exc}")
        raise F1DataError(f"Error loading season {year} calendar: {str(exc)}") from exc


def load_race_session(
    year: int,
    gp_identifier: Union[int, str],
    session_type: str = "R",
    load_telemetry: bool = False,
    load_weather: bool = True
) -> fastf1.core.Session:
    """
    Loads an official Formula 1 session object with laps, results, and timing.

    Parameters:
        year: Championship season year (e.g. 2023)
        gp_identifier: Round number (e.g. 1) or Grand Prix name (e.g. 'Bahrain', 'Monza')
        session_type: 'R' (Race), 'Q' (Qualifying), 'SQ' (Sprint Shootout), 'S' (Sprint)
        load_telemetry: Whether to load high-frequency car telemetry (speed, throttle, brake)
        load_weather: Whether to load track and ambient weather conditions

    Returns:
        fastf1.core.Session: The fully loaded session object.
    """
    setup_fastf1_cache()
    
    # Suppress verbose FastF1 internal timing logs for cleaner output
    fastf1.set_log_level("WARNING")

    logger.info(f"Loading session: Year={year}, Event='{gp_identifier}', Session='{session_type}'...")
    
    try:
        session = fastf1.get_session(year, gp_identifier, session_type)
        session.load(
            laps=True,
            telemetry=load_telemetry,
            weather=load_weather,
            messages=False
        )
    except Exception as exc:
        error_msg = f"Failed to load session ({year}, {gp_identifier}, {session_type}): {exc}"
        logger.error(error_msg)
        raise F1DataError(error_msg) from exc

    if session.laps is None or session.laps.empty:
        raise F1DataError(f"Session ({year}, {gp_identifier}) returned no lap timing records.")

    return session


def extract_session_payload(session: fastf1.core.Session) -> Dict[str, Any]:
    """
    Extracts, normalizes, and packages all raw session tables into a dictionary.

    Returns:
        Dict containing:
            - 'session_name': Name of the Grand Prix
            - 'circuit_name': Circuit name and location
            - 'year': Championship season
            - 'total_laps': Official race lap count
            - 'results': Driver classification DataFrame
            - 'laps': Uncleaned raw lap-by-lap timing DataFrame
            - 'weather': Track & air temperature time series
            - 'drivers_list': List of 3-letter driver codes (e.g. ['VER', 'HAM', 'LEC'])
            - 'teams_list': List of constructor names (e.g. ['Red Bull Racing', 'Ferrari'])
    """
    if session is None or session.laps is None:
        raise F1DataError("Cannot extract data from an uninitialized or empty session.")

    # 1. Session Information
    event = session.event
    total_laps = int(session.laps["LapNumber"].max()) if not session.laps.empty else 0

    session_metadata = {
        "event_name": event.get("EventName", "Grand Prix"),
        "official_name": event.get("OfficialEventName", "Formula 1 Grand Prix"),
        "circuit_name": event.get("Location", "Unknown Circuit"),
        "country": event.get("Country", "Unknown"),
        "year": int(session.event.get("Year", session.date.year)),
        "round_number": int(event.get("RoundNumber", 0)),
        "session_date": str(session.date.date()) if session.date is not None else "Unknown",
        "total_laps": total_laps,
    }

    # 2. Race Results Table
    results_df = pd.DataFrame()
    if session.results is not None and not session.results.empty:
        res = session.results.copy()
        
        # Select essential classification fields
        desired_cols = [
            "DriverNumber", "BroadcastName", "Abbreviation", "TeamName",
            "TeamColor", "GridPosition", "Position", "ClassifiedPosition",
            "Status", "Points", "Time"
        ]
        available_res_cols = [c for c in desired_cols if c in res.columns]
        results_df = res[available_res_cols].copy()
        
        # Ensure Position is numeric where possible
        results_df["PositionNumeric"] = pd.to_numeric(results_df["Position"], errors="coerce")
        results_df = results_df.sort_values(by="PositionNumeric").reset_index(drop=True)

    # 3. Lap Timing & Tyre Records
    laps_df = session.laps.copy()

    # 4. Extract Drivers & Teams
    drivers = []
    if "Abbreviation" in results_df.columns:
        drivers = results_df["Abbreviation"].dropna().unique().tolist()
    elif "Driver" in laps_df.columns:
        drivers = laps_df["Driver"].dropna().unique().tolist()

    teams = []
    if "TeamName" in results_df.columns:
        teams = results_df["TeamName"].dropna().unique().tolist()
    elif "Team" in laps_df.columns:
        teams = laps_df["Team"].dropna().unique().tolist()

    # 5. Weather Telemetry (if recorded)
    weather_df = pd.DataFrame()
    if session.weather_data is not None and not session.weather_data.empty:
        weather_df = session.weather_data.copy()

    return {
        "metadata": session_metadata,
        "results": results_df,
        "laps": laps_df,
        "drivers": drivers,
        "teams": teams,
        "weather": weather_df
    }


def save_raw_session_cache(payload: Dict[str, Any], filepath: Union[str, Path]) -> None:
    """
    Saves an extracted session payload to CSV/Pickle for offline viva demonstrations.
    """
    target = Path(filepath)
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(payload, str(target))
    logger.info(f"Session data saved for offline use to {target}")


def load_raw_session_cache(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Loads a previously cached session payload from disk.
    """
    target = Path(filepath)
    if not target.exists():
        raise FileNotFoundError(f"Offline cache not found at {target}")
    return pd.read_pickle(str(target))
