"""One-command reproduction of the public-source experiments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pv_monitor.data import prepare_laghouat_dataset, prepare_zenodo_inverter_dataset
from pv_monitor.monitoring_evidence import generate_monitoring_evidence
from pv_monitor.workflow import (
    calibrate_alert_policy,
    evaluate_final_power_model,
    evaluate_final_soiling_monitor,
    train_models,
    train_soiling_monitor,
)


def select_model_by_validation_metric(
    metrics: dict[str, dict[str, Any]], metric_name: str
) -> str:
    """Select the smallest validation error without accessing the final test."""
    if not metrics:
        raise ValueError("Não há métricas de validação para selecionar um modelo.")
    try:
        return min(metrics, key=lambda name: float(metrics[name][metric_name]))
    except KeyError as error:
        raise ValueError(f"Métrica de validação ausente: {metric_name}") from error


def reproduce_public_experiments(
    laghouat_input: str,
    zenodo_input: str,
    processed_dir: str,
    artifacts_dir: str,
    output_path: str,
    zenodo_inverter_id: str = "inverter1",
) -> dict[str, Any]:
    """Rebuild both public-source experiments and save one auditable summary.

    Selection of models and alert policy uses validation only. Each final test is
    executed after those choices are fixed.
    """
    processed = Path(processed_dir)
    artifacts = Path(artifacts_dir)
    processed.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)
    laghouat_processed = processed / "laghouat_2022.csv"
    zenodo_processed = processed / f"zenodo_{zenodo_inverter_id}_2023_2024.csv"
    laghouat_monitor_dir = artifacts / "laghouat_monitor"
    laghouat_final_dir = artifacts / "laghouat_final"
    zenodo_train_dir = artifacts / f"zenodo_{zenodo_inverter_id}"
    zenodo_final_dir = artifacts / f"zenodo_{zenodo_inverter_id}_final"

    laghouat = prepare_laghouat_dataset(laghouat_input, str(laghouat_processed))
    soiling_validation = train_soiling_monitor(str(laghouat_processed), str(laghouat_monitor_dir))
    selected_soiling_model = min(
        soiling_validation["validation_metrics"],
        key=lambda name: soiling_validation["validation_metrics"][name]["estimated_soiling_loss"]["mae_fraction"],
    )
    alert_policy = calibrate_alert_policy(
        str(laghouat_processed), str(laghouat_monitor_dir), model_name=selected_soiling_model
    )
    soiling_final = evaluate_final_soiling_monitor(
        str(laghouat_processed),
        str(laghouat_final_dir),
        str(laghouat_monitor_dir / "alert_policy_validation.json"),
    )
    monitoring_evidence = generate_monitoring_evidence(
        str(laghouat_processed),
        str(laghouat_final_dir / "metrics_test.json"),
        str(artifacts / "laghouat_monitoring_evidence"),
    )

    zenodo = prepare_zenodo_inverter_dataset(zenodo_input, str(zenodo_processed), zenodo_inverter_id)
    power_validation = train_models(str(zenodo_processed), str(zenodo_train_dir))
    selected_power_model = select_model_by_validation_metric(
        power_validation["validation_metrics"], "mae_kw"
    )
    power_final = evaluate_final_power_model(
        str(zenodo_processed), str(zenodo_final_dir), selected_power_model
    )

    summary = {
        "task": "reprodução dos experimentos com fontes públicas auditadas",
        "selection_rule": "modelos e política de alerta foram escolhidos somente na validação cronológica",
        "laghouat_soiling_experiment": {
            "raw_input": str(laghouat_input),
            "processed_output": str(laghouat_processed),
            "prepared_rows": len(laghouat),
            "selected_model": selected_soiling_model,
            "alert_policy": alert_policy["selected_policy"],
            "final_test_metrics": soiling_final["test_metrics"],
            "monitoring_evidence": monitoring_evidence,
        },
        "zenodo_external_power_experiment": {
            "raw_input": str(zenodo_input),
            "inverter_id": zenodo_inverter_id,
            "processed_output": str(zenodo_processed),
            "prepared_rows": len(zenodo),
            "selected_model": selected_power_model,
            "final_test_metrics": power_final["test_metrics"],
            "scope_note": "Avalia somente estimação de potência; a fonte não possui rótulo independente de sujidade.",
        },
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    return summary
