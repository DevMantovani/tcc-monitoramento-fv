"""Monitoring-focused evidence reports for the audited soiling experiment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from pv_monitor.data import load_observations, split_temporally
from pv_monitor.models import CLEAN_REFERENCE_TARGET_COLUMN, FEATURE_COLUMNS, TARGET_COLUMN, build_candidates, loss_metrics
from pv_monitor.workflow import _alert_metrics, _daily_losses

IRRADIANCE_BINS = (50.0, 300.0, 600.0, 900.0, float("inf"))
IRRADIANCE_LABELS = ("50–299 W/m²", "300–599 W/m²", "600–899 W/m²", "≥ 900 W/m²")
CONTEXT_COLUMNS = (
    "dust_density_reconstructed_gm2",
    "precipitation_mm",
    "relative_humidity_pct",
    "wind_speed_ms",
    "cloud_cover_pct",
)


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def condition_performance_table(test: pd.DataFrame) -> pd.DataFrame:
    """Summarize loss-estimation error by operating irradiance range."""
    evaluated = test.copy()
    evaluated["irradiance_range"] = pd.cut(
        evaluated["irradiance_wm2"],
        bins=IRRADIANCE_BINS,
        labels=IRRADIANCE_LABELS,
        right=False,
    )
    rows: list[dict[str, float | int | str]] = []
    for condition, subset in evaluated.groupby("irradiance_range", observed=True):
        metrics = loss_metrics(subset["observed_soiling_loss_fraction"], subset["estimated_loss_fraction"])
        rows.append(
            {
                "condition": str(condition),
                "samples": int(len(subset)),
                "mae_loss_percentage_points": metrics["mae_fraction"] * 100,
                "rmse_loss_percentage_points": metrics["rmse_fraction"] * 100,
                "mean_observed_loss_percentage": subset["observed_soiling_loss_fraction"].mean() * 100,
                "mean_estimated_loss_percentage": subset["estimated_loss_fraction"].mean() * 100,
            }
        )
    return pd.DataFrame(rows)


def monthly_alert_stability_table(
    daily: pd.DataFrame, threshold: float, persistence_days: int
) -> pd.DataFrame:
    """Report the frozen alert policy separately for each final-test month."""
    evaluated = daily.copy()
    evaluated["month"] = pd.to_datetime(evaluated["date"]).dt.to_period("M").astype(str)
    rows: list[dict[str, float | int | str]] = []
    for month, subset in evaluated.groupby("month"):
        alert = _alert_metrics(
            subset["observed_loss_fraction"],
            subset["estimated_loss_fraction"],
            threshold,
            persistence_days,
        )
        loss = loss_metrics(subset["observed_loss_fraction"], subset["estimated_loss_fraction"])
        rows.append(
            {
                "month": month,
                "days": int(len(subset)),
                "mae_loss_percentage_points": loss["mae_fraction"] * 100,
                "precision": alert["precision"],
                "recall": alert["recall"],
                "f1": alert["f1"],
                "true_positive_days": alert["true_positive_days"],
                "false_positive_days": alert["false_positive_days"],
                "false_negative_days": alert["false_negative_days"],
            }
        )
    return pd.DataFrame(rows)


def context_correlation_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Describe exploratory associations without treating them as causal inputs."""
    rows: list[dict[str, float | int | str]] = []
    for column in CONTEXT_COLUMNS:
        if column not in frame:
            continue
        subset = frame[["observed_soiling_loss_fraction", column]].dropna()
        rows.append(
            {
                "context_variable": column,
                "available_samples": int(len(subset)),
                "spearman_correlation_with_observed_loss": subset.corr(method="spearman").iloc[0, 1],
                "interpretation": "exploratória; não demonstra causalidade nem entra no modelo operacional atual",
            }
        )
    return pd.DataFrame(rows)


def generate_monitoring_evidence(
    input_path: str, final_metrics_path: str, output_dir: str, minimum_irradiance_wm2: float = 50.0
) -> dict[str, Any]:
    """Generate monitoring evidence using the model and policy fixed before final test.

    The report does not compare candidate algorithms or select new settings. It
    refits only the model already locked in ``metrics_test.json`` to reproduce
    the same final period at operating-condition level.
    """
    final_metrics = _read_json(Path(final_metrics_path))
    model_name = final_metrics["model_name"]
    policy = final_metrics["locked_alert_policy"]
    if model_name not in build_candidates():
        raise ValueError(f"Modelo desconhecido no teste final: {model_name}")

    raw = pd.read_csv(input_path)
    frame = load_observations(input_path, minimum_irradiance_wm2)
    required = {CLEAN_REFERENCE_TARGET_COLUMN, "observed_soiling_loss_fraction"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"CSV sem referência supervisionada de sujidade: {', '.join(missing)}")
    frame = frame.dropna(subset=required).copy()
    split = split_temporally(frame)
    development = pd.concat([split.train, split.validation], ignore_index=True)
    model = build_candidates()[model_name]
    model.fit(development[FEATURE_COLUMNS], development[CLEAN_REFERENCE_TARGET_COLUMN])
    test = split.test.copy()
    test["predicted_clean_power_kw"] = model.predict(test[FEATURE_COLUMNS])
    test = test[test["predicted_clean_power_kw"] > 0].copy()
    test["estimated_loss_fraction"] = (
        (test["predicted_clean_power_kw"] - test[TARGET_COLUMN]) / test["predicted_clean_power_kw"]
    )
    daily = _daily_losses(test, test["predicted_clean_power_kw"])
    condition_table = condition_performance_table(test)
    monthly_table = monthly_alert_stability_table(
        daily, float(policy["threshold"]), int(policy["persistence_days"])
    )
    context_table = context_correlation_table(frame)

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    condition_table.to_csv(destination / "condition_performance.csv", index=False)
    monthly_table.to_csv(destination / "monthly_alert_stability.csv", index=False)
    context_table.to_csv(destination / "context_correlations.csv", index=False)
    report = {
        "task": "evidência operacional do monitor de perdas por sujidade",
        "source": str(input_path),
        "model_locked_before_final_test": model_name,
        "locked_alert_policy": policy,
        "coverage": {
            "raw_rows": int(len(raw)),
            "eligible_daylight_rows": int(len(frame)),
            "days": int(frame["timestamp"].dt.date.nunique()),
            "direct_dust_measurements": int(raw.get("dust_density_measured_gm2", pd.Series()).notna().sum()),
        },
        "scope_note": (
            "As estratificações descrevem o comportamento do monitor no teste final de Laghouat. "
            "Elas não comprovam desempenho em outra instalação nem estabelecem causalidade ambiental."
        ),
    }
    with (destination / "monitoring_evidence.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    return report
