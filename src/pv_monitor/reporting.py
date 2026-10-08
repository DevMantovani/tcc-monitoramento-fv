"""Generate reproducible tables and figures from saved experiment artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_validation_table(
    laghouat_validation: dict[str, Any], zenodo_validation: dict[str, Any]
) -> pd.DataFrame:
    """Create a tidy comparison table using validation metrics only."""
    rows: list[dict[str, Any]] = []
    for model, metrics in laghouat_validation["validation_metrics"].items():
        loss = metrics["estimated_soiling_loss"]
        rows.extend(
            [
                {
                    "experiment": "Laghouat — perda por sujidade",
                    "partition": "validação",
                    "model": model,
                    "metric": "MAE da perda estimada",
                    "value": loss["mae_fraction"] * 100,
                    "unit": "pontos percentuais",
                },
                {
                    "experiment": "Laghouat — perda por sujidade",
                    "partition": "validação",
                    "model": model,
                    "metric": "RMSE da perda estimada",
                    "value": loss["rmse_fraction"] * 100,
                    "unit": "pontos percentuais",
                },
                {
                    "experiment": "Laghouat — perda por sujidade",
                    "partition": "validação",
                    "model": model,
                    "metric": "R² da perda estimada",
                    "value": loss["r2"],
                    "unit": "adimensional",
                },
            ]
        )
    for model, metrics in zenodo_validation["validation_metrics"].items():
        rows.extend(
            [
                {
                    "experiment": "Zenodo 2023–2024 — potência externa",
                    "partition": "validação",
                    "model": model,
                    "metric": "MAE de potência",
                    "value": metrics["mae_kw"],
                    "unit": "kW",
                },
                {
                    "experiment": "Zenodo 2023–2024 — potência externa",
                    "partition": "validação",
                    "model": model,
                    "metric": "RMSE de potência",
                    "value": metrics["rmse_kw"],
                    "unit": "kW",
                },
                {
                    "experiment": "Zenodo 2023–2024 — potência externa",
                    "partition": "validação",
                    "model": model,
                    "metric": "R² de potência",
                    "value": metrics["r2"],
                    "unit": "adimensional",
                },
            ]
        )
    return pd.DataFrame(rows)


def build_final_table(laghouat_final: dict[str, Any], zenodo_final: dict[str, Any]) -> pd.DataFrame:
    """Create a tidy final-test table without mixing validation values."""
    test = laghouat_final["test_metrics"]
    alert = test["persistent_alert"]
    rows = [
        ("Laghouat — perda por sujidade", "MAE da perda estimada", test["estimated_soiling_loss"]["mae_fraction"] * 100, "pontos percentuais"),
        ("Laghouat — perda por sujidade", "RMSE da perda estimada", test["estimated_soiling_loss"]["rmse_fraction"] * 100, "pontos percentuais"),
        ("Laghouat — perda por sujidade", "R² da perda estimada", test["estimated_soiling_loss"]["r2"], "adimensional"),
        ("Laghouat — alertas persistentes", "Precisão", alert["precision"], "proporção"),
        ("Laghouat — alertas persistentes", "Sensibilidade", alert["recall"], "proporção"),
        ("Laghouat — alertas persistentes", "F1", alert["f1"], "proporção"),
        ("Zenodo 2023–2024 — potência externa", "MAE de potência", zenodo_final["test_metrics"]["mae_kw"], "kW"),
        ("Zenodo 2023–2024 — potência externa", "RMSE de potência", zenodo_final["test_metrics"]["rmse_kw"], "kW"),
        ("Zenodo 2023–2024 — potência externa", "R² de potência", zenodo_final["test_metrics"]["r2"], "adimensional"),
    ]
    return pd.DataFrame(rows, columns=["experiment", "metric", "value", "unit"])


def _save_figure(figure: plt.Figure, destination: Path) -> None:
    figure.tight_layout()
    figure.savefig(destination.with_suffix(".png"), dpi=300, bbox_inches="tight")
    figure.savefig(destination.with_suffix(".svg"), bbox_inches="tight")
    plt.close(figure)


def _plot_validation_comparison(
    laghouat_validation: dict[str, Any], zenodo_validation: dict[str, Any], destination: Path
) -> None:
    models = list(laghouat_validation["validation_metrics"])
    laghouat_mae = [
        laghouat_validation["validation_metrics"][name]["estimated_soiling_loss"]["mae_fraction"] * 100
        for name in models
    ]
    zenodo_mae = [zenodo_validation["validation_metrics"][name]["mae_kw"] for name in models]
    labels = [name.replace("_", " ").title() for name in models]
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.4))
    colors = ["#0f766e", "#f59e0b"]
    axes[0].bar(labels, laghouat_mae, color=colors)
    axes[0].set_title("Validação: erro da perda estimada")
    axes[0].set_ylabel("MAE (pontos percentuais)")
    axes[1].bar(labels, zenodo_mae, color=colors)
    axes[1].set_title("Validação externa: erro de potência")
    axes[1].set_ylabel("MAE (kW)")
    for axis, values in zip(axes, (laghouat_mae, zenodo_mae), strict=True):
        for index, value in enumerate(values):
            axis.text(index, value, f"{value:.2f}", ha="center", va="bottom")
        axis.spines[["top", "right"]].set_visible(False)
    _save_figure(figure, destination)


def _plot_daily_loss(daily: pd.DataFrame, threshold: float, destination: Path) -> None:
    figure, axis = plt.subplots(figsize=(10, 4.8))
    dates = pd.to_datetime(daily["date"])
    axis.plot(dates, daily["observed_loss_fraction"] * 100, label="Observada", color="#475569", linewidth=2)
    axis.plot(dates, daily["estimated_loss_fraction"] * 100, label="Estimada", color="#0f766e", linewidth=2)
    alerts = daily["estimated_persistent_alert"].astype(bool)
    axis.scatter(dates[alerts], (daily.loc[alerts, "estimated_loss_fraction"] * 100), color="#dc2626", label="Alerta persistente", zorder=3)
    axis.axhline(threshold * 100, color="#f59e0b", linestyle="--", label="Limiar bloqueado")
    axis.set_title("Teste final: perda diária observada e estimada")
    axis.set_ylabel("Perda (%)")
    axis.set_xlabel("Data")
    axis.legend(frameon=False, ncol=2)
    axis.spines[["top", "right"]].set_visible(False)
    _save_figure(figure, destination)


def _plot_alert_metrics(laghouat_final: dict[str, Any], destination: Path) -> None:
    alert = laghouat_final["test_metrics"]["persistent_alert"]
    names = ["Precisão", "Sensibilidade", "F1"]
    values = [alert["precision"], alert["recall"], alert["f1"]]
    figure, axis = plt.subplots(figsize=(6.5, 4.5))
    bars = axis.bar(names, values, color=["#0f766e", "#2563eb", "#7c3aed"])
    axis.set_ylim(0, 1.05)
    axis.set_ylabel("Proporção")
    axis.set_title("Teste final: desempenho dos alertas persistentes")
    for bar, value in zip(bars, values, strict=True):
        axis.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.3f}", ha="center", va="bottom")
    axis.spines[["top", "right"]].set_visible(False)
    _save_figure(figure, destination)


def generate_result_materials(input_dir: str, output_dir: str) -> dict[str, Any]:
    """Create CSV tables, figures and a short Markdown inventory from artifacts."""
    source = Path(input_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    laghouat_validation = _read_json(source / "laghouat_monitor" / "metrics_validation.json")
    laghouat_final = _read_json(source / "laghouat_final" / "metrics_test.json")
    zenodo_validation = _read_json(source / "zenodo_inverter1" / "metrics_validation.json")
    zenodo_final = _read_json(source / "zenodo_inverter1_final" / "metrics_test.json")
    daily = pd.read_csv(source / "laghouat_final" / "test_daily_losses.csv")
    validation_table = build_validation_table(laghouat_validation, zenodo_validation)
    final_table = build_final_table(laghouat_final, zenodo_final)
    validation_table.to_csv(destination / "table_validation_comparison.csv", index=False)
    final_table.to_csv(destination / "table_final_metrics.csv", index=False)
    threshold = laghouat_final["locked_alert_policy"]["threshold"]
    _plot_validation_comparison(laghouat_validation, zenodo_validation, destination / "figure_validation_comparison")
    _plot_daily_loss(daily, threshold, destination / "figure_laghouat_test_daily_loss")
    _plot_alert_metrics(laghouat_final, destination / "figure_laghouat_alert_metrics")
    summary = {
        "output_dir": str(destination),
        "validation_table_rows": len(validation_table),
        "final_table_rows": len(final_table),
        "figures": [
            "figure_validation_comparison.png/.svg",
            "figure_laghouat_test_daily_loss.png/.svg",
            "figure_laghouat_alert_metrics.png/.svg",
        ],
        "note": "As figuras usam resultados já calculados; não retreinam modelos nem alteram métricas.",
    }
    with (destination / "materials_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    markdown = "\n".join(
        [
            "# Materiais de resultado gerados",
            "",
            "- `table_validation_comparison.csv`: comparação de candidatos na validação.",
            "- `table_final_metrics.csv`: métricas dos testes finais preservados.",
            "- `figure_validation_comparison.*`: MAE de validação nas duas tarefas.",
            "- `figure_laghouat_test_daily_loss.*`: perda diária observada e estimada no teste final.",
            "- `figure_laghouat_alert_metrics.*`: precisão, sensibilidade e F1 dos alertas finais.",
            "",
            "As figuras não demonstram generalização para uma residência brasileira; elas resumem os experimentos públicos documentados.",
        ]
    )
    (destination / "README.md").write_text(markdown + "\n", encoding="utf-8")
    return summary
