"""Command-line interface for the reproducible pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pv_monitor.data import prepare_laghouat_dataset, prepare_zenodo_inverter_dataset
from pv_monitor.demo import create_demo_dataset
from pv_monitor.workflow import (
    calibrate_alert_policy,
    detect_additional_loss,
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
            daily_loss_threshold=args.daily_loss_threshold,
            persistence_days=args.persistence_days,
        )
        print(f"Indicadores diários criados: {len(daily)} dias em {args.output}")
