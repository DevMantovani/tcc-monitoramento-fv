"""Treinamento e geração do indicador de perda adicional."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from pv_monitor.data import load_observations, operational_input_quality_report, split_temporally
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


def evaluate_final_power_model(
    input_path: str,
    output_dir: str,
    model_name: str,
    minimum_irradiance_wm2: float = 50.0,
) -> dict[str, Any]:
    """Evaluate one validation-selected expected-power model on the final test.

    This task evaluates power prediction only. It must not be used to claim
    detection of soiling when the source has no independent soiling reference.
    """
    candidates = build_candidates()
    if model_name not in candidates:
        raise ValueError(f"Modelo desconhecido: {model_name}")
    frame = load_observations(input_path, minimum_irradiance_wm2)
    split = split_temporally(frame)
    development = pd.concat([split.train, split.validation], ignore_index=True)
    model = candidates[model_name]
    model.fit(development[FEATURE_COLUMNS], development[TARGET_COLUMN])
    predicted = model.predict(split.test[FEATURE_COLUMNS])
    report = {
        "task": "teste final de potência esperada em fonte externa",
        "model_name": model_name,
        "training_rows_after_refit": len(development),
        "test_partition": _partition_metadata(split.test),
        "test_metrics": regression_metrics(split.test[TARGET_COLUMN], predicted),
        "note": (
            "O modelo foi refitado com treino mais validação após a escolha na validação. "
            "Esta fonte não tem rótulo independente de sujidade; o resultado avalia somente potência esperada."
        ),
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "metrics_test.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    joblib.dump(model, destination / f"{model_name}_refit_development.joblib")
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


def _load_soiling_monitor_frame(input_path: str, minimum_irradiance_wm2: float) -> pd.DataFrame:
    """Load rows that contain the supervised reference used only in evaluation."""
    frame = load_observations(input_path, minimum_irradiance_wm2)
    required = {CLEAN_REFERENCE_TARGET_COLUMN, "observed_soiling_loss_fraction"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"CSV sem referência supervisionada de sujidade: {', '.join(missing)}")
    return frame.dropna(subset=required).copy()


def _daily_losses(frame: pd.DataFrame, predicted_clean: Any) -> pd.DataFrame:
    """Aggregate observed and estimated loss consistently for alert analysis."""
    evaluated = frame.copy()
    evaluated["predicted_clean_power_kw"] = predicted_clean
    evaluated = evaluated[evaluated["predicted_clean_power_kw"] > 0].copy()
    evaluated["estimated_soiling_loss_fraction"] = (
        (evaluated["predicted_clean_power_kw"] - evaluated[TARGET_COLUMN])
        / evaluated["predicted_clean_power_kw"]
    )
    evaluated["date"] = evaluated["timestamp"].dt.date.astype(str)
    return (
        evaluated.groupby("date", as_index=False)
        .agg(
            samples=("estimated_soiling_loss_fraction", "size"),
            observed_loss_fraction=("observed_soiling_loss_fraction", "median"),
            estimated_loss_fraction=("estimated_soiling_loss_fraction", "median"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )


def _persistent_alerts(values: pd.Series, threshold: float, persistence_days: int) -> list[bool]:
    """Return alerts only after a loss stays over a threshold for consecutive days."""
    if not 0 < threshold < 1:
        raise ValueError("O limiar de perda deve estar entre 0 e 1.")
    if persistence_days < 1:
        raise ValueError("A persistência deve ser positiva.")
    return _persistent_flags(values >= threshold, persistence_days)


def _persistent_flags(above: pd.Series, persistence_days: int) -> list[bool]:
    """Return days that complete a consecutive run of already-qualified values."""
    run_length = 0
    alerts: list[bool] = []
    for is_above in above:
        run_length = run_length + 1 if is_above else 0
        alerts.append(run_length >= persistence_days)
    return alerts


def _alert_metrics(observed: pd.Series, estimated: pd.Series, threshold: float, persistence_days: int) -> dict[str, float | int]:
    """Score persistent estimated-loss alerts against the independent loss reference."""
    expected_alert = _persistent_alerts(observed, threshold, persistence_days)
    estimated_alert = _persistent_alerts(estimated, threshold, persistence_days)
    pairs = pd.DataFrame({"expected": expected_alert, "estimated": estimated_alert})
    true_positive = int((pairs["expected"] & pairs["estimated"]).sum())
    false_positive = int((~pairs["expected"] & pairs["estimated"]).sum())
    false_negative = int((pairs["expected"] & ~pairs["estimated"]).sum())
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positive_days": true_positive,
        "false_positive_days": false_positive,
        "false_negative_days": false_negative,
    }


def calibrate_alert_policy(
    input_path: str,
    output_dir: str,
    model_name: str = "ridge",
    thresholds: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20),
    persistence_days: tuple[int, ...] = (1, 2, 3),
    minimum_irradiance_wm2: float = 50.0,
) -> dict[str, Any]:
    """Choose alert settings on validation data only, preserving the final test."""
    candidates = build_candidates()
    if model_name not in candidates:
        raise ValueError(f"Modelo desconhecido: {model_name}")
    frame = _load_soiling_monitor_frame(input_path, minimum_irradiance_wm2)
    split = split_temporally(frame)
    model = candidates[model_name]
    model.fit(split.train[FEATURE_COLUMNS], split.train[CLEAN_REFERENCE_TARGET_COLUMN])
    validation_predicted_clean = model.predict(split.validation[FEATURE_COLUMNS])
    daily = _daily_losses(split.validation, validation_predicted_clean)

    rows: list[dict[str, float | int]] = []
    for threshold in thresholds:
        for persistence in persistence_days:
            score = _alert_metrics(
                daily["observed_loss_fraction"], daily["estimated_loss_fraction"], threshold, persistence
            )
            rows.append({"threshold": threshold, "persistence_days": persistence, **score})
    candidates_frame = pd.DataFrame(rows)
    selected = candidates_frame.sort_values(
        ["f1", "precision", "recall", "persistence_days", "threshold"],
        ascending=[False, False, False, False, False],
    ).iloc[0]
    policy = {
        "model_name": model_name,
        "selection_partition": "validation",
        "selected_policy": {
            "threshold": float(selected["threshold"]),
            "persistence_days": int(selected["persistence_days"]),
            "validation_metrics": {
                key: float(selected[key]) if key in {"precision", "recall", "f1"} else int(selected[key])
                for key in [
                    "precision",
                    "recall",
                    "f1",
                    "true_positive_days",
                    "false_positive_days",
                    "false_negative_days",
                ]
            },
        },
        "candidate_grid": candidates_frame.to_dict(orient="records"),
        "note": "Limiar e persistência foram escolhidos somente na validação; o teste final permanece preservado.",
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    daily.to_csv(destination / "validation_daily_losses.csv", index=False)
    with (destination / "alert_policy_validation.json").open("w", encoding="utf-8") as handle:
        json.dump(policy, handle, ensure_ascii=False, indent=2)
    return policy


def evaluate_final_soiling_monitor(
    input_path: str,
    output_dir: str,
    policy_path: str,
    minimum_irradiance_wm2: float = 50.0,
) -> dict[str, Any]:
    """Evaluate one locked model and alert policy on the untouched final test set."""
    with Path(policy_path).open(encoding="utf-8") as handle:
        policy = json.load(handle)
    model_name = policy["model_name"]
    selected_policy = policy["selected_policy"]
    candidates = build_candidates()
    if model_name not in candidates:
        raise ValueError(f"Modelo desconhecido no arquivo de política: {model_name}")

    frame = _load_soiling_monitor_frame(input_path, minimum_irradiance_wm2)
    split = split_temporally(frame)
    development = pd.concat([split.train, split.validation], ignore_index=True)
    model = candidates[model_name]
    model.fit(development[FEATURE_COLUMNS], development[CLEAN_REFERENCE_TARGET_COLUMN])
    test_predicted_clean = model.predict(split.test[FEATURE_COLUMNS])
    daily = _daily_losses(split.test, test_predicted_clean)
    threshold = float(selected_policy["threshold"])
    persistence = int(selected_policy["persistence_days"])
    alert_score = _alert_metrics(
        daily["observed_loss_fraction"], daily["estimated_loss_fraction"], threshold, persistence
    )
    daily["observed_persistent_alert"] = _persistent_alerts(
        daily["observed_loss_fraction"], threshold, persistence
    )
    daily["estimated_persistent_alert"] = _persistent_alerts(
        daily["estimated_loss_fraction"], threshold, persistence
    )
    evaluated_test = split.test.copy()
    evaluated_test["predicted_clean_power_kw"] = test_predicted_clean
    evaluated_test = evaluated_test[evaluated_test["predicted_clean_power_kw"] > 0]
    estimated_loss = (
        (evaluated_test["predicted_clean_power_kw"] - evaluated_test[TARGET_COLUMN])
        / evaluated_test["predicted_clean_power_kw"]
    )
    report = {
        "task": "teste final do monitor de perdas por sujidade",
        "model_name": model_name,
        "training_rows_after_refit": len(development),
        "test_partition": _partition_metadata(split.test),
        "locked_alert_policy": {"threshold": threshold, "persistence_days": persistence},
        "test_metrics": {
            "expected_clean_power": regression_metrics(
                evaluated_test[CLEAN_REFERENCE_TARGET_COLUMN], evaluated_test["predicted_clean_power_kw"]
            ),
            "estimated_soiling_loss": loss_metrics(
                evaluated_test["observed_soiling_loss_fraction"], estimated_loss
            ),
            "persistent_alert": alert_score,
        },
        "note": "O modelo foi refitado com treino mais validação após a seleção. O teste final não participou da escolha do modelo ou da política de alerta.",
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    daily.to_csv(destination / "test_daily_losses.csv", index=False)
    with (destination / "metrics_test.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    joblib.dump(model, destination / f"{model_name}_refit_development.joblib")
    return report


def detect_additional_loss(
    input_path: str,
    model_path: str,
    output_path: str,
    minimum_expected_kw: float = 0.10,
    daily_loss_threshold: float = 0.12,
    minimum_samples_per_day: int = 12,
    persistence_days: int = 3,
    minimum_irradiance_wm2: float = 50.0,
) -> pd.DataFrame:
    """Produce an auditable operational alert, without assigning a failure cause."""
    if not 0 < daily_loss_threshold < 1:
        raise ValueError("O limiar diário deve estar entre 0 e 1.")
    if persistence_days < 1 or minimum_samples_per_day < 1:
        raise ValueError("Persistência e quantidade mínima devem ser positivas.")

    input_quality = operational_input_quality_report(input_path, minimum_irradiance_wm2)
    frame = load_observations(input_path, minimum_irradiance_wm2)
    model = joblib.load(model_path)
    frame["predicted_power_kw"] = model.predict(frame[FEATURE_COLUMNS])
    frame = frame[frame["predicted_power_kw"] >= minimum_expected_kw].copy()
    if frame.empty:
        raise ValueError("Nenhuma observação atingiu a potência esperada mínima configurada.")
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

    daily["consecutive_days_above_threshold"] = _consecutive_counts(daily["above_threshold"])
    daily["additional_loss_alert"] = _persistent_flags(daily["above_threshold"], persistence_days)
    daily["recommended_action"] = daily["additional_loss_alert"].map(
        {
            True: "Inspecionar o sistema e confirmar a causa antes de limpar.",
            False: "Continuar o monitoramento; não há alerta persistente.",
        }
    )
    daily["alert_interpretation"] = "O alerta prioriza investigação; não confirma sujidade nem falha específica."

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(destination, index=False)
    summary = {
        "task": "monitoramento operacional de perda adicional",
        "input_quality": input_quality,
        "alert_policy": {
            "minimum_expected_kw": minimum_expected_kw,
            "daily_loss_threshold": daily_loss_threshold,
            "minimum_samples_per_day": minimum_samples_per_day,
            "persistence_days": persistence_days,
        },
        "daily_rows": len(daily),
        "persistent_alert_days": int(daily["additional_loss_alert"].sum()),
        "note": (
            "A saída é um sinal para inspeção. Não atribui a perda exclusivamente à sujidade "
            "e não deve acionar limpeza automática."
        ),
    }
    summary_path = destination.with_suffix(".summary.json")
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    return daily


def _consecutive_counts(values: pd.Series) -> list[int]:
    count = 0
    counts: list[int] = []
    for value in values:
        count = count + 1 if value else 0
        counts.append(count)
    return counts
