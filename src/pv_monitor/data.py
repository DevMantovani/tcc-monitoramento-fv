"""Leitura, validação e separação temporal das observações."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = ("timestamp", "irradiance_wm2", "temperature_c", "power_kw")
LEGACY_TEMPERATURE_COLUMN = "module_temperature_c"
LAGHOUAT_COLUMNS = (
    "datetime",
    "dust_density_measured_gm2",
    "dust_density_reconstructed_PCHIP_gm2",
    "temp_amb_C",
    "T_cell_C",
    "G_POA_Wm2",
    "RH_pct",
    "wind_speed_ms",
    "cloud_cover_pct",
    "precipitation_mm",
    "P_clean_W",
    "P_dusty_W",
)
BANGLADESH_REQUIRED_COLUMNS = (
    "Date",
    "Time",
    "Clean Temperature",
    "Dusty Temperature",
    "Wind Speed",
    "Humidity",
    "Air Pressure",
    "Ideal_Irradiance",
    "Clean_pmp",
    "Dusty_pmp",
)


@dataclass(frozen=True)
class TemporalSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def _normalize_observation_columns(frame: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Validate and coerce the common operational fields once.

    The original frame is retained so specialized datasets can carry their
    supervised reference columns through the same validation path.
    """
    normalized = frame.copy()
    temperature_source = "temperature_c"
    if "temperature_c" not in normalized.columns and LEGACY_TEMPERATURE_COLUMN in normalized.columns:
        normalized["temperature_c"] = normalized[LEGACY_TEMPERATURE_COLUMN]
        temperature_source = LEGACY_TEMPERATURE_COLUMN
    missing = sorted(set(REQUIRED_COLUMNS).difference(normalized.columns))
    if missing:
        raise ValueError(f"CSV sem colunas obrigatórias: {', '.join(missing)}")
    normalized["timestamp"] = pd.to_datetime(normalized["timestamp"], errors="coerce", utc=True)
    for column in REQUIRED_COLUMNS[1:]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    return normalized, temperature_source


def prepare_laghouat_dataset(input_path: str, output_path: str) -> pd.DataFrame:
    """Prepare the published clean-versus-dusty panel dataset without imputation.

    The output keeps the measured variables in their published units. Loss is only
    defined when irradiance is at least 50 W/m² and the clean-panel power is positive.
    """
    frame = pd.read_csv(input_path)
    missing = sorted(set(LAGHOUAT_COLUMNS).difference(frame.columns))
    if missing:
        raise ValueError(f"CSV Laghouat sem colunas esperadas: {', '.join(missing)}")

    frame = frame.loc[:, LAGHOUAT_COLUMNS].copy()
    frame = frame.rename(
        columns={
            "datetime": "timestamp",
            "dust_density_measured_gm2": "dust_density_measured_gm2",
            "dust_density_reconstructed_PCHIP_gm2": "dust_density_reconstructed_gm2",
            "temp_amb_C": "ambient_temperature_c",
            "T_cell_C": "cell_temperature_c",
            "G_POA_Wm2": "poa_irradiance_wm2",
            "RH_pct": "relative_humidity_pct",
            "P_clean_W": "power_clean_w",
            "P_dusty_W": "power_dusty_w",
        }
    )
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], dayfirst=True, errors="coerce")
    numeric_columns = [column for column in frame.columns if column != "timestamp"]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["timestamp"]).drop_duplicates(subset="timestamp", keep="last")
    frame = frame.sort_values("timestamp").reset_index(drop=True)

    valid_reference = (frame["poa_irradiance_wm2"] >= 50) & (frame["power_clean_w"] > 0)
    frame["soiling_loss_fraction"] = pd.NA
    frame.loc[valid_reference, "soiling_loss_fraction"] = (
        (frame.loc[valid_reference, "power_clean_w"] - frame.loc[valid_reference, "power_dusty_w"])
        / frame.loc[valid_reference, "power_clean_w"]
    )
    # The following standardized fields emulate the information available to a
    # deployed monitor. The clean panel remains only as a supervised reference
    # for training and evaluating the expected-power model.
    frame["irradiance_wm2"] = frame["poa_irradiance_wm2"]
    frame["temperature_c"] = frame["cell_temperature_c"]
    frame["power_kw"] = frame["power_dusty_w"] / 1000
    frame["clean_reference_power_kw"] = frame["power_clean_w"] / 1000
    frame["observed_soiling_loss_fraction"] = frame["soiling_loss_fraction"]
    frame.to_csv(output_path, index=False)
    return frame


def prepare_zenodo_inverter_dataset(
    input_path: str, output_path: str, inverter_id: str
) -> pd.DataFrame:
    """Prepare one inverter from the audited 2023--2024 external dataset.

    The source's ``inverter`` column is measured PV power in watts. Its
    ``energy`` column is an already predicted value from the source authors'
    mathematical model and is deliberately excluded to avoid target leakage.
    Ambient temperature is kept under its real name; it is not presented as
    module temperature.
    """
    source_columns = (
        "datetime",
        "id",
        "inverter",
        "temperature_2m (°C)",
        "global_tilted_irradiance (W/m²)",
        "panel_size",
    )
    frame = pd.read_csv(input_path)
    missing = sorted(set(source_columns).difference(frame.columns))
    if missing:
        raise ValueError(f"CSV Zenodo sem colunas esperadas: {', '.join(missing)}")
    frame = frame.loc[:, source_columns].copy()
    frame = frame[frame["id"] == inverter_id].copy()
    if frame.empty:
        available = ", ".join(sorted(pd.read_csv(input_path, usecols=["id"])["id"].dropna().unique()))
        raise ValueError(f"Inversor '{inverter_id}' não encontrado. Disponíveis: {available}")

    frame = frame.rename(
        columns={
            "datetime": "timestamp",
            "inverter": "power_w",
            "temperature_2m (°C)": "ambient_temperature_c",
            "global_tilted_irradiance (W/m²)": "irradiance_wm2",
            "id": "inverter_id",
            "panel_size": "panel_area_m2",
        }
    )
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
    numeric_columns = [
        "power_w",
        "ambient_temperature_c",
        "irradiance_wm2",
        "panel_area_m2",
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["timestamp", "power_w", "ambient_temperature_c", "irradiance_wm2"])
    frame = frame.drop_duplicates(subset="timestamp", keep="last")
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    frame["power_kw"] = frame["power_w"] / 1000
    frame["temperature_c"] = frame["ambient_temperature_c"]
    frame.to_csv(output_path, index=False)
    return frame


def _normalize_bangladesh_headers(frame: pd.DataFrame) -> pd.DataFrame:
    """Fix documented spelling and spacing variations across daily source files."""
    normalized = frame.copy()
    normalized.columns = [
        column.strip().replace("Temparature", "Temperature").replace("  ", " ")
        for column in normalized.columns
    ]
    missing = sorted(set(BANGLADESH_REQUIRED_COLUMNS).difference(normalized.columns))
    if missing:
        raise ValueError(f"CSV Bangladesh sem colunas esperadas: {', '.join(missing)}")
    return normalized


def _parse_bangladesh_timestamp(frame: pd.DataFrame, source_path: Path) -> pd.Series:
    """Parse source timestamps, preferring the unambiguous date in each filename."""
    dates = frame["Date"].astype("string").str.strip()
    times = frame["Time"].astype("string").str.strip()
    filename_date = re.search(
        r"(\d+)(?:st|nd|rd|th)\s+"
        r"(January|February|March|April|May|June|July|August|September|October|November|December)",
        source_path.name,
        flags=re.IGNORECASE,
    )
    years = dates.str.extract(r"(\d{4})", expand=False).dropna()
    if filename_date and not years.empty:
        month = pd.to_datetime(filename_date.group(2), format="%B").month
        calendar_date = f"{years.iloc[0]}-{month:02d}-{int(filename_date.group(1)):02d}"
        return pd.to_datetime(calendar_date + " " + times, format="%Y-%m-%d %I:%M:%S %p", errors="coerce")
    source = dates + " " + times
    timestamps = pd.Series(pd.NaT, index=frame.index, dtype="datetime64[ns]")
    iso_dates = dates.str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)
    timestamps.loc[iso_dates] = pd.to_datetime(
        source.loc[iso_dates], format="%Y-%m-%d %I:%M:%S %p", errors="coerce"
    )
    timestamps.loc[~iso_dates] = pd.to_datetime(
        source.loc[~iso_dates], format="%m/%d/%Y %I:%M:%S %p", errors="coerce"
    )
    return timestamps


def prepare_bangladesh_dataset(input_dir: str, output_path: str) -> pd.DataFrame:
    """Prepare the audited Dhaka clean-versus-dusty dataset at hourly resolution.

    The source contains one CSV per available day at 30-second resolution. It
    is aggregated hourly from measured clean and dusty maximum-power values;
    the source's cumulative-energy fields are deliberately not used as model
    inputs or targets.
    """
    source = Path(input_dir)
    files = sorted(source.rglob("*.csv"))
    if not files:
        raise ValueError("Nenhum CSV Bangladesh foi encontrado no diretório informado.")
    frames: list[pd.DataFrame] = []
    for path in files:
        raw = _normalize_bangladesh_headers(pd.read_csv(path))
        frame = pd.DataFrame(
            {
                "timestamp": _parse_bangladesh_timestamp(raw, path),
                "irradiance_wm2": raw["Ideal_Irradiance"],
                "temperature_c": raw["Dusty Temperature"],
                "power_dusty_w": raw["Dusty_pmp"],
                "power_clean_w": raw["Clean_pmp"],
                "wind_speed_ms": raw["Wind Speed"],
                "relative_humidity_pct": raw["Humidity"],
                "air_pressure_hpa": raw["Air Pressure"],
                "source_file": path.name,
            }
        )
        for column in frame.columns:
            if column not in {"timestamp", "source_file"}:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frames.append(frame)
    records = pd.concat(frames, ignore_index=True)
    records = records.dropna(subset=["timestamp"]).sort_values("timestamp")
    hourly = (
        records.set_index("timestamp")
        .groupby(pd.Grouper(freq="h"))
        .agg(
            source_samples=("power_dusty_w", "size"),
            irradiance_wm2=("irradiance_wm2", "mean"),
            temperature_c=("temperature_c", "mean"),
            power_dusty_w=("power_dusty_w", "mean"),
            power_clean_w=("power_clean_w", "mean"),
            wind_speed_ms=("wind_speed_ms", "mean"),
            relative_humidity_pct=("relative_humidity_pct", "mean"),
            air_pressure_hpa=("air_pressure_hpa", "mean"),
        )
        .dropna(subset=["irradiance_wm2", "temperature_c", "power_dusty_w", "power_clean_w"])
        .reset_index()
    )
    hourly["power_kw"] = hourly["power_dusty_w"] / 1000
    hourly["clean_reference_power_kw"] = hourly["power_clean_w"] / 1000
    valid_reference = (hourly["irradiance_wm2"] >= 50) & (hourly["power_clean_w"] > 0)
    hourly["observed_soiling_loss_fraction"] = pd.NA
    hourly.loc[valid_reference, "observed_soiling_loss_fraction"] = (
        (hourly.loc[valid_reference, "power_clean_w"] - hourly.loc[valid_reference, "power_dusty_w"])
        / hourly.loc[valid_reference, "power_clean_w"]
    )
    hourly["source_dataset"] = "Dhaka 2019-2020 clean-versus-dusty panels"
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    hourly.to_csv(destination, index=False)
    return hourly


def operational_input_quality_report(
    input_path: str, minimum_irradiance_wm2: float = 50.0
) -> dict[str, Any]:
    """Describe data exclusions before an operational alert is generated.

    This report intentionally does not impute or repair records. It makes the
    amount of usable information visible to the user before alerting.
    """
    frame = pd.read_csv(input_path)
    normalized_frame, temperature_source = _normalize_observation_columns(frame)
    normalized = normalized_frame.loc[:, REQUIRED_COLUMNS].copy()
    valid_required = normalized.notna().all(axis=1)
    valid_rows = normalized[valid_required].copy()
    duplicate_rows = int(valid_rows.duplicated(subset="timestamp", keep="last").sum())
    unique_rows = valid_rows.drop_duplicates(subset="timestamp", keep="last")
    usable = unique_rows[
        (unique_rows["power_kw"] >= 0)
        & (unique_rows["irradiance_wm2"] >= minimum_irradiance_wm2)
    ].copy()
    report: dict[str, Any] = {
        "input": str(input_path),
        "required_columns": list(REQUIRED_COLUMNS),
        "temperature_input_column": temperature_source,
        "minimum_irradiance_wm2": minimum_irradiance_wm2,
        "raw_rows": int(len(frame)),
        "invalid_timestamp_rows": int(normalized["timestamp"].isna().sum()),
        "rows_with_missing_or_invalid_required_values": int((~valid_required).sum()),
        "duplicate_timestamp_rows_after_validation": duplicate_rows,
        "negative_power_rows_after_validation": int((unique_rows["power_kw"] < 0).sum()),
        "below_minimum_irradiance_rows_after_validation": int(
            (unique_rows["irradiance_wm2"] < minimum_irradiance_wm2).sum()
        ),
        "usable_rows": int(len(usable)),
        "optional_context_columns_present": [
            column
            for column in ("precipitation_mm", "rain_mm", "ambient_temperature_c")
            if column in frame.columns
        ],
    }
    if not usable.empty:
        report["usable_period"] = {
            "start": usable["timestamp"].min().isoformat(),
            "end": usable["timestamp"].max().isoformat(),
        }
    return report


def load_observations(path: str, minimum_irradiance_wm2: float = 50.0) -> pd.DataFrame:
    """Load a CSV, rejecting unusable records instead of imputing them silently."""
    frame, _ = _normalize_observation_columns(pd.read_csv(path))

    frame = frame.dropna(subset=REQUIRED_COLUMNS)
    frame = frame.drop_duplicates(subset="timestamp", keep="last")
    frame = frame[(frame["power_kw"] >= 0) & (frame["irradiance_wm2"] >= minimum_irradiance_wm2)]
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    if len(frame) < 30:
        raise ValueError("Há menos de 30 observações válidas após a limpeza.")

    frame["irradiance_temperature_interaction"] = (
        frame["irradiance_wm2"] * frame["temperature_c"]
    )
    return frame


def split_temporally(
    frame: pd.DataFrame, train_fraction: float = 0.60, validation_fraction: float = 0.20
) -> TemporalSplit:
    """Split chronological data into train, validation and final test sets."""
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1:
        raise ValueError("As frações devem estar entre 0 e 1.")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("Treino e validação devem deixar uma parcela para teste.")

    train_end = int(len(frame) * train_fraction)
    validation_end = train_end + int(len(frame) * validation_fraction)
    split = TemporalSplit(
        train=frame.iloc[:train_end].copy(),
        validation=frame.iloc[train_end:validation_end].copy(),
        test=frame.iloc[validation_end:].copy(),
    )
    if min(len(split.train), len(split.validation), len(split.test)) < 10:
        raise ValueError("Uma partição ficou pequena demais para avaliação.")
    return split
