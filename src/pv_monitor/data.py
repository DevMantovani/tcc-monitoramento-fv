"""Leitura, validação e separação temporal das observações."""

from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class TemporalSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


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


def load_observations(path: str, minimum_irradiance_wm2: float = 50.0) -> pd.DataFrame:
    """Load a CSV, rejecting unusable records instead of imputing them silently."""
    frame = pd.read_csv(path)
    if "temperature_c" not in frame.columns and LEGACY_TEMPERATURE_COLUMN in frame.columns:
        frame["temperature_c"] = frame[LEGACY_TEMPERATURE_COLUMN]
    missing = sorted(set(REQUIRED_COLUMNS).difference(frame.columns))
    if missing:
        raise ValueError(f"CSV sem colunas obrigatórias: {', '.join(missing)}")

    frame = frame.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
    for column in REQUIRED_COLUMNS[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

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
