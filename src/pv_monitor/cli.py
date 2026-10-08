"""Command-line interface for the reproducible pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pv_monitor.data import prepare_laghouat_dataset
from pv_monitor.demo import create_demo_dataset
from pv_monitor.workflow import detect_additional_loss, train_models, train_soiling_monitor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Monitoramento fotovoltaico orientado por dados")
    commands = parser.add_subparsers(dest="command", required=True)

    demo = commands.add_parser("demo", help="gera dados sintéticos para testar o software")
    demo.add_argument("--output", required=True)
    demo.add_argument("--days", type=int, default=90)

    prepare = commands.add_parser("prepare-laghouat", help="prepara o dataset real de painéis limpo e exposto")
    prepare.add_argument("--input", required=True)
    prepare.add_argument("--output", required=True)

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
    elif args.command == "train":
        report = train_models(args.input, args.output, args.minimum_irradiance_wm2)
        print(json.dumps(report["validation_metrics"], ensure_ascii=False, indent=2))
    elif args.command == "train-soiling-monitor":
        report = train_soiling_monitor(args.input, args.output, args.minimum_irradiance_wm2)
        print(json.dumps(report["validation_metrics"], ensure_ascii=False, indent=2))
    elif args.command == "detect":
        daily = detect_additional_loss(
            args.input,
            args.model,
            args.output,
            daily_loss_threshold=args.daily_loss_threshold,
            persistence_days=args.persistence_days,
        )
        print(f"Indicadores diários criados: {len(daily)} dias em {args.output}")
