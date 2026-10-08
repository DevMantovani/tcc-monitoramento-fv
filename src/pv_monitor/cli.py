"""Command-line interface for the reproducible pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pv_monitor.data import (
    operational_input_quality_report,
    prepare_bangladesh_dataset,
    prepare_laghouat_dataset,
    prepare_zenodo_inverter_dataset,
)
from pv_monitor.demo import create_demo_dataset
from pv_monitor.monitoring_evidence import generate_monitoring_evidence
from pv_monitor.reproduction import reproduce_public_experiments
from pv_monitor.reporting import generate_result_materials
from pv_monitor.workflow import (
    calibrate_installation_baseline,
    calibrate_alert_policy,
    detect_additional_loss,
    evaluate_post_cleaning_calibration,
    evaluate_final_soiling_monitor,
    evaluate_final_power_model,
    train_models,
    train_soiling_monitor,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Monitoramento fotovoltaico orientado por dados")
    commands = parser.add_subparsers(dest="command", required=True)

    demo = commands.add_parser("demo", help="gera dados sintéticos para testar o software")
    demo.add_argument("--output", required=True)
    demo.add_argument("--days", type=int, default=90)

    prepare = commands.add_parser("prepare-laghouat", help="prepara o dataset real de painéis limpo e exposto")
    prepare.add_argument("--input", required=True)
    prepare.add_argument("--output", required=True)

    prepare_external = commands.add_parser(
        "prepare-zenodo-inverter",
        help="prepara um inversor da fonte externa de 2023--2024 para avaliar potência esperada",
    )
    prepare_external.add_argument("--input", required=True)
    prepare_external.add_argument("--output", required=True)
    prepare_external.add_argument("--inverter-id", required=True)

    prepare_bangladesh = commands.add_parser(
        "prepare-bangladesh",
        help="prepara a fonte pública Dhaka de painéis limpo e exposto",
    )
    prepare_bangladesh.add_argument("--input-dir", required=True)
    prepare_bangladesh.add_argument("--output", required=True)

    train = commands.add_parser("train", help="treina Ridge e Random Forest")
    train.add_argument("--input", required=True)
    train.add_argument("--output", required=True)
    train.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)

    monitor = commands.add_parser(
        "train-soiling-monitor",
        help="treina o monitor de perda por sujidade com referência limpa apenas para validação",
    )
    monitor.add_argument("--input", required=True)
    monitor.add_argument("--output", required=True)
    monitor.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)

    calibrate = commands.add_parser(
        "calibrate-alert-policy",
        help="calibra limiar e persistência somente na partição de validação",
    )
    calibrate.add_argument("--input", required=True)
    calibrate.add_argument("--output", required=True)
    calibrate.add_argument("--model-name", choices=("ridge", "random_forest"), default="ridge")
    calibrate.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)

    final_evaluation = commands.add_parser(
        "evaluate-final",
        help="avalia uma política bloqueada no teste final preservado",
    )
    final_evaluation.add_argument("--input", required=True)
    final_evaluation.add_argument("--output", required=True)
    final_evaluation.add_argument("--policy", required=True)
    final_evaluation.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)

    final_power = commands.add_parser(
        "evaluate-final-power",
        help="avalia no teste final preservado um modelo de potência escolhido na validação",
    )
    final_power.add_argument("--input", required=True)
    final_power.add_argument("--output", required=True)
    final_power.add_argument("--model-name", choices=("ridge", "random_forest"), required=True)
    final_power.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)

    detect = commands.add_parser("detect", help="calcula o alerta de perda adicional")
    detect.add_argument("--input", required=True)
    detect.add_argument("--model", required=True)
    detect.add_argument("--output", required=True)
    detect.add_argument("--daily-loss-threshold", type=float, default=0.12)
    detect.add_argument("--persistence-days", type=int, default=3)
    detect.add_argument("--minimum-samples-per-day", type=int, default=12)
    detect.add_argument("--minimum-expected-kw", type=float, default=0.10)
    detect.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)

    installation_calibration = commands.add_parser(
        "calibrate-installation",
        help="cria uma referência de geração pós-limpeza para uma instalação específica",
    )
    installation_calibration.add_argument("--input", required=True)
    installation_calibration.add_argument("--cleaning-timestamp", required=True)
    installation_calibration.add_argument("--calibration-days", type=int, default=14)
    installation_calibration.add_argument("--minimum-observations", type=int, default=30)
    installation_calibration.add_argument("--output", required=True)
    installation_calibration.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)

    calibration_evaluation = commands.add_parser(
        "evaluate-local-calibration",
        help="avalia no experimento público o efeito da duração da calibração pós-limpeza",
    )
    calibration_evaluation.add_argument("--input", required=True)
    calibration_evaluation.add_argument("--output", required=True)
    calibration_evaluation.add_argument("--calibration-days", type=int, nargs="+", default=(14, 28, 42, 60))
    calibration_evaluation.add_argument("--alert-threshold", type=float, default=0.15)
    calibration_evaluation.add_argument("--persistence-days", type=int, default=3)
    calibration_evaluation.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)

    quality = commands.add_parser(
        "check-input",
        help="verifica a qualidade de um CSV operacional antes de monitorar perdas",
    )
    quality.add_argument("--input", required=True)
    quality.add_argument("--output", required=True)
    quality.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)

    reproduce = commands.add_parser(
        "reproduce-public-experiments",
        help="reproduz os experimentos das duas fontes públicas auditadas",
    )
    reproduce.add_argument("--laghouat-input", required=True)
    reproduce.add_argument("--zenodo-input", required=True)
    reproduce.add_argument("--processed-dir", default="data/processed")
    reproduce.add_argument("--artifacts-dir", default="artifacts")
    reproduce.add_argument("--zenodo-inverter-id", default="inverter1")
    reproduce.add_argument("--output", required=True)

    materials = commands.add_parser(
        "generate-results",
        help="gera tabelas e figuras reproduzíveis a partir dos artefatos experimentais",
    )
    materials.add_argument("--input-dir", default="artifacts")
    materials.add_argument("--output", required=True)

    evidence = commands.add_parser(
        "analyze-monitoring-evidence",
        help="analisa a estabilidade do monitor já selecionado, sem comparar algoritmos",
    )
    evidence.add_argument("--input", required=True)
    evidence.add_argument("--final-metrics", required=True)
    evidence.add_argument("--output", required=True)
    evidence.add_argument("--minimum-irradiance-wm2", type=float, default=50.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    if args.command == "demo":
        frame = create_demo_dataset(args.output, days=args.days)
        print(f"Dados sintéticos criados: {len(frame)} linhas em {args.output}")
    elif args.command == "prepare-laghouat":
        frame = prepare_laghouat_dataset(args.input, args.output)
        print(f"Dataset Laghouat preparado: {len(frame)} linhas em {args.output}")
    elif args.command == "prepare-zenodo-inverter":
        frame = prepare_zenodo_inverter_dataset(args.input, args.output, args.inverter_id)
        print(f"Dataset externo preparado: {len(frame)} linhas em {args.output}")
    elif args.command == "prepare-bangladesh":
        frame = prepare_bangladesh_dataset(args.input_dir, args.output)
        print(f"Dataset Bangladesh preparado: {len(frame)} linhas em {args.output}")
    elif args.command == "train":
        report = train_models(args.input, args.output, args.minimum_irradiance_wm2)
        print(json.dumps(report["validation_metrics"], ensure_ascii=False, indent=2))
    elif args.command == "train-soiling-monitor":
        report = train_soiling_monitor(args.input, args.output, args.minimum_irradiance_wm2)
        print(json.dumps(report["validation_metrics"], ensure_ascii=False, indent=2))
    elif args.command == "calibrate-alert-policy":
        report = calibrate_alert_policy(
            args.input, args.output, args.model_name, minimum_irradiance_wm2=args.minimum_irradiance_wm2
        )
        print(json.dumps(report["selected_policy"], ensure_ascii=False, indent=2))
    elif args.command == "evaluate-final":
        report = evaluate_final_soiling_monitor(
            args.input, args.output, args.policy, args.minimum_irradiance_wm2
        )
        print(json.dumps(report["test_metrics"], ensure_ascii=False, indent=2))
    elif args.command == "evaluate-final-power":
        report = evaluate_final_power_model(
            args.input, args.output, args.model_name, args.minimum_irradiance_wm2
        )
        print(json.dumps(report["test_metrics"], ensure_ascii=False, indent=2))
    elif args.command == "detect":
        daily = detect_additional_loss(
            args.input,
            args.model,
            args.output,
            minimum_expected_kw=args.minimum_expected_kw,
            daily_loss_threshold=args.daily_loss_threshold,
            minimum_samples_per_day=args.minimum_samples_per_day,
            persistence_days=args.persistence_days,
            minimum_irradiance_wm2=args.minimum_irradiance_wm2,
        )
        print(f"Indicadores diários criados: {len(daily)} dias em {args.output}")
    elif args.command == "calibrate-installation":
        report = calibrate_installation_baseline(
            args.input,
            args.cleaning_timestamp,
            args.calibration_days,
            args.output,
            args.minimum_observations,
            args.minimum_irradiance_wm2,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.command == "evaluate-local-calibration":
        report = evaluate_post_cleaning_calibration(
            args.input,
            args.output,
            tuple(args.calibration_days),
            args.alert_threshold,
            args.persistence_days,
            args.minimum_irradiance_wm2,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.command == "check-input":
        report = operational_input_quality_report(args.input, args.minimum_irradiance_wm2)
        with Path(args.output).open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.command == "reproduce-public-experiments":
        report = reproduce_public_experiments(
            args.laghouat_input,
            args.zenodo_input,
            args.processed_dir,
            args.artifacts_dir,
            args.output,
            args.zenodo_inverter_id,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.command == "generate-results":
        report = generate_result_materials(args.input_dir, args.output)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.command == "analyze-monitoring-evidence":
        report = generate_monitoring_evidence(
            args.input,
            args.final_metrics,
            args.output,
            args.minimum_irradiance_wm2,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
