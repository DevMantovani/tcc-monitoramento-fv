"""Treinamento e geração do indicador de perda adicional."""

from __future__ import annotations

import json
from datetime import date
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


def calibrate_installation_baseline(
    input_path: str,
    cleaning_timestamp: str,
    calibration_days: int,
    output_dir: str,
    minimum_observations: int = 30,
    minimum_irradiance_wm2: float = 50.0,
) -> dict[str, Any]:
    """Create an installation-specific clean-generation reference after cleaning.

    The period must be confirmed by the operator as clean and operational. Its
    measured power becomes the local target for the expected-power baseline;
    no clean companion panel is required in deployment.
    """
    if calibration_days < 1:
        raise ValueError("A janela de calibração deve ter ao menos um dia.")
    if minimum_observations < 1:
        raise ValueError("A quantidade mínima de observações deve ser positiva.")
    cleaning_start = pd.to_datetime(cleaning_timestamp, errors="coerce", utc=True)
    if pd.isna(cleaning_start):
        raise ValueError("Data de limpeza inválida. Use formato ISO 8601, por exemplo 2026-01-15T00:00:00Z.")

    frame = load_observations(input_path, minimum_irradiance_wm2)
    cleaning_end = cleaning_start + pd.DateOffset(days=int(calibration_days))
    baseline = frame[frame["timestamp"].between(cleaning_start, cleaning_end, inclusive="left")].copy()
    if len(baseline) < minimum_observations:
        raise ValueError(
            f"A janela pós-limpeza possui {len(baseline)} observações válidas; são necessárias ao menos "
            f"{minimum_observations}."
        )

    model = build_candidates()["ridge"]
    model.fit(baseline[FEATURE_COLUMNS], baseline[TARGET_COLUMN])
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    model_path = destination / "clean_baseline_ridge.joblib"
    joblib.dump(model, model_path)
    report = {
        "task": "calibração local de referência pós-limpeza",
        "input": str(input_path),
        "model_name": "ridge",
        "model_path": str(model_path),
        "cleaning_event": {
            "timestamp": cleaning_start.isoformat(),
            "calibration_window_days": calibration_days,
            "window_end": cleaning_end.isoformat(),
            "operator_confirmation_required": True,
        },
        "baseline": {
            "valid_daylight_observations": len(baseline),
            "start": baseline["timestamp"].min().isoformat(),
            "end": baseline["timestamp"].max().isoformat(),
            "mean_measured_power_kw": float(baseline[TARGET_COLUMN].mean()),
        },
        "operational_inputs": FEATURE_COLUMNS + [TARGET_COLUMN],
        "note": (
            "A referência foi ajustada somente com dados posteriores a uma limpeza confirmada. "
            "Antes de uso decisório, a instalação deve manter qualidade de dados, registrar novas limpezas "
            "e validar seus próprios limiares de alerta."
        ),
    }
    with (destination / "calibration.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    return report


def evaluate_post_cleaning_calibration(
    input_path: str,
    output_dir: str,
    calibration_days: tuple[int, ...] = (14, 28, 42, 60),
    alert_threshold: float = 0.15,
    persistence_days: int = 3,
    minimum_irradiance_wm2: float = 50.0,
) -> dict[str, Any]:
    """Evaluate calibration-window duration with an experimental clean-panel proxy.

    The published clean panel supplies the post-cleaning target only during
    calibration. Future clean-panel values are retained exclusively to score
    expected power and the independent observed loss on later dirty-panel data.
    """
    if not calibration_days or any(days < 1 for days in calibration_days):
        raise ValueError("Informe ao menos uma duração positiva de calibração.")
    frame = _load_soiling_monitor_frame(input_path, minimum_irradiance_wm2)
    first_timestamp = frame["timestamp"].min()
    common_start = first_timestamp + pd.DateOffset(days=int(max(calibration_days)))
    future = frame[frame["timestamp"] >= common_start].copy()
    rows: list[dict[str, float | int]] = []
    for days in sorted(set(calibration_days)):
        calibration_end = first_timestamp + pd.DateOffset(days=int(days))
        calibration = frame[frame["timestamp"] < calibration_end].copy()
        if calibration.empty or future.empty:
            raise ValueError(f"A janela de {days} dias não deixa dados para calibração e avaliação.")
        model = build_candidates()["ridge"]
        model.fit(calibration[FEATURE_COLUMNS], calibration[CLEAN_REFERENCE_TARGET_COLUMN])
        predicted_clean = model.predict(future[FEATURE_COLUMNS])
        evaluated = future.copy()
        evaluated["predicted_clean_power_kw"] = predicted_clean
        evaluated = evaluated[evaluated["predicted_clean_power_kw"] > 0].copy()
        estimated_loss = (
            (evaluated["predicted_clean_power_kw"] - evaluated[TARGET_COLUMN])
            / evaluated["predicted_clean_power_kw"]
        )
        daily = _daily_losses(future, predicted_clean)
        power_score = regression_metrics(
            evaluated[CLEAN_REFERENCE_TARGET_COLUMN], evaluated["predicted_clean_power_kw"]
        )
        loss_score = loss_metrics(evaluated["observed_soiling_loss_fraction"], estimated_loss)
        alert = _alert_metrics(
            daily["observed_loss_fraction"], daily["estimated_loss_fraction"], alert_threshold, persistence_days, daily["date"]
        )
        rows.append(
            {
                "calibration_days": int(days),
                "calibration_observations": int(len(calibration)),
                "future_observations": int(len(evaluated)),
                "evaluation_start": future["timestamp"].min().isoformat(),
                "evaluation_end": future["timestamp"].max().isoformat(),
                "expected_power_mae_kw": power_score["mae_kw"],
                "loss_mae_percentage_points": loss_score["mae_fraction"] * 100,
                "loss_r2": loss_score["r2"],
                "alert_precision": alert["precision"],
                "alert_recall": alert["recall"],
                "alert_f1": alert["f1"],
                "false_positive_days": alert["false_positive_days"],
                "false_negative_days": alert["false_negative_days"],
            }
        )
    results = pd.DataFrame(rows)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    results.to_csv(destination / "calibration_sensitivity.csv", index=False)
    report = {
        "task": "avaliação experimental da calibração pós-limpeza",
        "source": str(input_path),
        "model_name": "ridge",
        "fixed_alert_policy": {"threshold": alert_threshold, "persistence_days": persistence_days},
        "common_evaluation_period": _partition_metadata(future),
        "comparison_note": "Todas as janelas usam o mesmo período futuro após a maior janela. Análise retrospectiva exploratória; não seleciona uma janela com teste intocado.",
        "experimental_proxy": (
            "A potência do painel limpo é usada somente no período inicial para simular uma janela pós-limpeza. "
            "No período futuro, ela é usada apenas como referência independente de avaliação."
        ),
        "results": results.to_dict(orient="records"),
        "scope_note": (
            "A análise mede a sensibilidade à duração de calibração neste experimento controlado. "
            "Ela não valida a duração ideal nem o alerta em uma residência real."
        ),
    }
    with (destination / "calibration_sensitivity.json").open("w", encoding="utf-8") as handle:
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
            expected_clean_power_kw=("predicted_clean_power_kw", "mean"),
            measured_power_kw=(TARGET_COLUMN, "mean"),
            observed_loss_fraction=("observed_soiling_loss_fraction", "median"),
            estimated_loss_fraction=("estimated_soiling_loss_fraction", "median"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )


def _consecutive_counts(values: pd.Series, dates: pd.Series) -> list[int]:
    """Count qualified calendar days; missing dates and missing values break a run.

    Dates follow the normalized timestamp convention of the input pipeline.
    Duplicate/out-of-order days are rejected instead of silently reordered.
    """
    days = pd.DatetimeIndex(pd.to_datetime(list(dates), errors="raise", utc=True)).normalize()
    if len(days) != len(values) or days.isna().any():
        raise ValueError("Datas válidas devem corresponder a cada indicador diário.")
    if days.has_duplicates or not days.is_monotonic_increasing:
        raise ValueError("Datas diárias devem ser únicas e estar em ordem crescente.")
    count = 0
    counts = []
    previous: date | None = None
    for day, value in zip(days, values):
        current = pd.Timestamp(day).date()
        if previous is not None and (current - previous).days != 1:
            count = 0
        count = count + 1 if pd.notna(value) and bool(value) else 0
        counts.append(count)
        previous = current
    return counts


def _persistent_alerts(values: pd.Series, threshold: float, persistence_days: int, dates: pd.Series) -> list[bool]:
    if not 0 < threshold < 1:
        raise ValueError("O limiar de perda deve estar entre 0 e 1.")
    return _persistent_flags(values >= threshold, persistence_days, dates)


def _persistent_flags(above: pd.Series, persistence_days: int, dates: pd.Series) -> list[bool]:
    if persistence_days < 1:
        raise ValueError("A persistência deve ser positiva.")
    return [count >= persistence_days for count in _consecutive_counts(above, dates)]


def _classification_metrics(expected: Any, estimated: Any) -> dict[str, float | int | None]:
    pairs = pd.DataFrame({"expected": list(expected), "estimated": list(estimated)}, dtype=bool)
    tp = int((pairs["expected"] & pairs["estimated"]).sum())
    fp = int((~pairs["expected"] & pairs["estimated"]).sum())
    fn = int((pairs["expected"] & ~pairs["estimated"]).sum())
    tn = int((~pairs["expected"] & ~pairs["estimated"]).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "precision": precision, "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "true_positive_days": tp, "false_positive_days": fp,
        "false_negative_days": fn, "true_negative_days": tn,
        "specificity": tn / (tn + fp) if tn + fp else None,
        "evaluated_days": len(pairs),
        "positive_prevalence": (tp + fn) / len(pairs) if len(pairs) else None,
    }


def _alert_metrics(observed: pd.Series, estimated: pd.Series, threshold: float, persistence_days: int, dates: pd.Series) -> dict[str, float | int | None]:
    return _classification_metrics(
        _persistent_alerts(observed, threshold, persistence_days, dates),
        _persistent_alerts(estimated, threshold, persistence_days, dates),
    )


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
                daily["observed_loss_fraction"], daily["estimated_loss_fraction"], threshold, persistence, daily["date"]
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
        daily["observed_loss_fraction"], daily["estimated_loss_fraction"], threshold, persistence, daily["date"]
    )
    daily["observed_persistent_alert"] = _persistent_alerts(
        daily["observed_loss_fraction"], threshold, persistence, daily["date"]
    )
    daily["estimated_persistent_alert"] = _persistent_alerts(
        daily["estimated_loss_fraction"], threshold, persistence, daily["date"]
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
        "locked_alert_policy": {"threshold": threshold, "persistence_days": persistence, "daily_aggregation": "median", "minimum_expected_kw": 0.0, "minimum_samples_per_day": 1, "minimum_irradiance_wm2": minimum_irradiance_wm2, "gap_rule": "reset"},
        "test_metrics": {
            "expected_clean_power": regression_metrics(
                evaluated_test[CLEAN_REFERENCE_TARGET_COLUMN], evaluated_test["predicted_clean_power_kw"]
            ),
            "estimated_soiling_loss": loss_metrics(
                evaluated_test["observed_soiling_loss_fraction"], estimated_loss
            ),
            "persistent_alert": alert_score,
            "alert_baselines": {
                "always_alert": _classification_metrics(daily["observed_persistent_alert"], [True] * len(daily)),
                "never_alert": _classification_metrics(daily["observed_persistent_alert"], [False] * len(daily)),
                "always_above_threshold_with_same_persistence": _classification_metrics(
                    daily["observed_persistent_alert"],
                    _persistent_flags(pd.Series([True] * len(daily)), persistence, daily["date"]),
                ),
            },
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
    minimum_expected_kw: float = 0.0,
    daily_loss_threshold: float = 0.15,
    minimum_samples_per_day: int = 1,
    persistence_days: int = 3,
    minimum_irradiance_wm2: float = 50.0,
) -> pd.DataFrame:
    """Produce an auditable operational alert, without assigning a failure cause."""
    if not 0 < daily_loss_threshold < 1:
        raise ValueError("O limiar diário deve estar entre 0 e 1.")
    if persistence_days < 1 or minimum_samples_per_day < 1:
        raise ValueError("Persistência e quantidade mínima devem ser positivas.")

    if minimum_expected_kw < 0:
        raise ValueError("A potência mínima não pode ser negativa.")
    input_quality = operational_input_quality_report(input_path, minimum_irradiance_wm2)
    frame = load_observations(input_path, minimum_irradiance_wm2)
    model = joblib.load(model_path)
    frame["predicted_power_kw"] = model.predict(frame[FEATURE_COLUMNS])
    frame = frame[(frame["predicted_power_kw"] > 0) & (frame["predicted_power_kw"] >= minimum_expected_kw)].copy()
    if frame.empty:
        raise ValueError("Nenhuma observação atingiu a potência esperada mínima configurada.")
    frame["loss_fraction"] = (frame["predicted_power_kw"] - frame["power_kw"]) / frame["predicted_power_kw"]
    frame["date"] = frame["timestamp"].dt.date.astype(str)

    daily = (
        frame.groupby("date", as_index=False)
        .agg(
            samples=("loss_fraction", "size"),
            mean_loss_fraction=("loss_fraction", "mean"),
            median_loss_fraction=("loss_fraction", "median"),
            mean_observed_power_kw=("power_kw", "mean"),
            mean_predicted_power_kw=("predicted_power_kw", "mean"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )
    daily["above_threshold"] = (
        (daily["samples"] >= minimum_samples_per_day)
        & (daily["median_loss_fraction"] >= daily_loss_threshold)
    )

    daily["consecutive_days_above_threshold"] = _consecutive_counts(daily["above_threshold"], daily["date"])
    daily["additional_loss_alert"] = _persistent_flags(daily["above_threshold"], persistence_days, daily["date"])
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
            "daily_aggregation": "median",
            "gap_rule": "reset",
            "minimum_irradiance_wm2": minimum_irradiance_wm2,
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
