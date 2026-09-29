"""Leitura, validação e separação temporal das observações."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

REQUIRED_COLUMNS = ("timestamp", "irradiance_wm2", "module_temperature_c", "power_kw")


@dataclass(frozen=True)
class TemporalSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def load_observations(path: str, minimum_irradiance_wm2: float = 50.0) -> pd.DataFrame:
    """Load a CSV, rejecting unusable records instead of imputing them silently."""
    frame = pd.read_csv(path)
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
        frame["irradiance_wm2"] * frame["module_temperature_c"]
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
