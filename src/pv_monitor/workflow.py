"""Treinamento e geração do indicador de perda adicional."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from pv_monitor.data import load_observations, split_temporally
from pv_monitor.models import (
    CLEAN_REFERENCE_TARGET_COLUMN,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_candidates,
    loss_metrics,
    regression_metrics,
)


def _partition_metadata(partition: pd.DataFrame) -> dict[str, Any]:
    return {
        "rows": len(partition),
        "start": partition["timestamp"].min().isoformat(),
        "end": partition["timestamp"].max().isoformat(),
    }


def train_models(input_path: str, output_dir: str, minimum_irradiance_wm2: float = 50.0) -> dict[str, Any]:
    """Fit each candidate using only past data and persist validation metrics."""
    frame = load_observations(input_path, minimum_irradiance_wm2)
    split = split_temporally(frame)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "input": str(input_path),
        "minimum_irradiance_wm2": minimum_irradiance_wm2,
        "partitions": {
            "train": _partition_metadata(split.train),
            "validation": _partition_metadata(split.validation),
            "test_held_out": _partition_metadata(split.test),
        },
        "validation_metrics": {},
        "note": "O conjunto de teste foi preservado e não foi usado para escolher o modelo.",
    }

    for name, model in build_candidates().items():
        model.fit(split.train[FEATURE_COLUMNS], split.train[TARGET_COLUMN])
        predicted = model.predict(split.validation[FEATURE_COLUMNS])
        report["validation_metrics"][name] = regression_metrics(split.validation[TARGET_COLUMN], predicted)
        joblib.dump(model, destination / f"{name}.joblib")

    with (destination / "metrics_validation.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    return report


def train_soiling_monitor(
    input_path: str, output_dir: str, minimum_irradiance_wm2: float = 50.0
) -> dict[str, Any]:
    """Train an expected-clean-power model and validate monitored loss.

    The clean reference is used only as the supervised target during development.
    The operational signal is the dirty-system power in ``power_kw``.
    """
    frame = load_observations(input_path, minimum_irradiance_wm2)
    required = {CLEAN_REFERENCE_TARGET_COLUMN, "observed_soiling_loss_fraction"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"CSV sem referência supervisionada de sujidade: {', '.join(missing)}")
    frame = frame.dropna(subset=[CLEAN_REFERENCE_TARGET_COLUMN, "observed_soiling_loss_fraction"]).copy()
    split = split_temporally(frame)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "input": str(input_path),
        "task": "monitoramento de perda por sujidade via potência limpa esperada",
        "operational_inputs": FEATURE_COLUMNS + ["power_kw"],
        "supervised_reference_not_required_in_deployment": CLEAN_REFERENCE_TARGET_COLUMN,
        "partitions": {
            "train": _partition_metadata(split.train),
            "validation": _partition_metadata(split.validation),
            "test_held_out": _partition_metadata(split.test),
        },
        "validation_metrics": {},
        "note": "O teste final foi preservado; a referência limpa é usada somente para treinamento e validação.",
    }

    for name, model in build_candidates().items():
        model.fit(split.train[FEATURE_COLUMNS], split.train[CLEAN_REFERENCE_TARGET_COLUMN])
        predicted_clean = model.predict(split.validation[FEATURE_COLUMNS])
        validation = split.validation.copy()
        validation["predicted_clean_power_kw"] = predicted_clean
        validation = validation[validation["predicted_clean_power_kw"] > 0]
        estimated_loss = (
            (validation["predicted_clean_power_kw"] - validation[TARGET_COLUMN])
            / validation["predicted_clean_power_kw"]
        )
        report["validation_metrics"][name] = {
            "expected_clean_power": regression_metrics(
                validation[CLEAN_REFERENCE_TARGET_COLUMN], validation["predicted_clean_power_kw"]
            ),
            "estimated_soiling_loss": loss_metrics(
                validation["observed_soiling_loss_fraction"], estimated_loss
            ),
        }
        joblib.dump(model, destination / f"{name}.joblib")

    with (destination / "metrics_validation.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    return report


def detect_additional_loss(
    input_path: str,
    model_path: str,
    output_path: str,
    minimum_expected_kw: float = 0.10,
    daily_loss_threshold: float = 0.12,
    minimum_samples_per_day: int = 12,
    persistence_days: int = 3,
) -> pd.DataFrame:
    """Produce an auditable operational alert, without assigning a failure cause."""
    if not 0 < daily_loss_threshold < 1:
        raise ValueError("O limiar diário deve estar entre 0 e 1.")
    if persistence_days < 1 or minimum_samples_per_day < 1:
        raise ValueError("Persistência e quantidade mínima devem ser positivas.")

    frame = load_observations(input_path)
    model = joblib.load(model_path)
    frame["predicted_power_kw"] = model.predict(frame[FEATURE_COLUMNS])
    frame = frame[frame["predicted_power_kw"] >= minimum_expected_kw].copy()
    frame["loss_fraction"] = (frame["predicted_power_kw"] - frame["power_kw"]) / frame["predicted_power_kw"]
    frame["date"] = frame["timestamp"].dt.date.astype(str)

    daily = (
        frame.groupby("date", as_index=False)
        .agg(
            samples=("loss_fraction", "size"),
            mean_loss_fraction=("loss_fraction", "mean"),
            mean_observed_power_kw=("power_kw", "mean"),
            mean_predicted_power_kw=("predicted_power_kw", "mean"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )
    daily["above_threshold"] = (
        (daily["samples"] >= minimum_samples_per_day)
        & (daily["mean_loss_fraction"] >= daily_loss_threshold)
    )

    run_length = 0
    alerts: list[bool] = []
    for is_above in daily["above_threshold"]:
        run_length = run_length + 1 if is_above else 0
        alerts.append(run_length >= persistence_days)
    daily["consecutive_days_above_threshold"] = _consecutive_counts(daily["above_threshold"])
    daily["additional_loss_alert"] = alerts
    daily["alert_interpretation"] = "Investigar perda adicional; não atribui a causa à sujidade."

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(destination, index=False)
    return daily


def _consecutive_counts(values: pd.Series) -> list[int]:
    count = 0
    counts: list[int] = []
    for value in values:
        count = count + 1 if value else 0
        counts.append(count)
    return counts
