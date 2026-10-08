"""Simple local launcher for people who only need to open the TCC dashboard."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from pv_monitor.reporting import generate_result_materials
from pv_monitor.reproduction import reproduce_public_experiments

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_URL = "http://127.0.0.1:8501"
RAW_SOURCES = (
    Path("data/raw/laghouat_2022/Laghouat_2022_final.csv"),
    Path(
        "data/raw/zenodo_inverter_2023_2024/"
        "math_model_all_inverters_03.11.2023-25.06.2024.csv"
    ),
)
REQUIRED_RESULTS = (
    Path("data/processed/laghouat_2022.csv"),
    Path("artifacts/laghouat_monitor/metrics_validation.json"),
    Path("artifacts/laghouat_final/metrics_test.json"),
    Path("artifacts/laghouat_final/test_daily_losses.csv"),
    Path("artifacts/zenodo_inverter1/metrics_validation.json"),
    Path("artifacts/zenodo_inverter1_final/metrics_test.json"),
)


def missing_raw_sources(root: Path = ROOT) -> list[Path]:
    """Return the public files required for the reproducible experiment."""
    return [relative for relative in RAW_SOURCES if not (root / relative).exists()]


def results_are_ready(root: Path = ROOT) -> bool:
    """Check whether the dashboard inputs have already been generated locally."""
    return all((root / relative).exists() for relative in REQUIRED_RESULTS)


def dashboard_is_running() -> bool:
    """Avoid starting a second local Streamlit process on the same port."""
    try:
        with urlopen(f"{DASHBOARD_URL}/_stcore/health", timeout=0.5) as response:
            return response.status == 200
    except URLError:
        return False


def prepare_dashboard_data(root: Path = ROOT) -> bool:
    """Generate missing local artifacts once, preserving existing results afterwards."""
    if results_are_ready(root):
        materials_summary = root / "artifacts/result_materials/materials_summary.json"
        if not materials_summary.exists():
            generate_result_materials(str(root / "artifacts"), str(materials_summary.parent))
            return True
        return False
    missing = missing_raw_sources(root)
    if missing:
        missing_text = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(
            "Faltam os dados públicos necessários para a primeira execução:\n"
            f"{missing_text}\n\n"
            "Baixe as fontes documentadas em docs/dados.md, mantenha os nomes dos arquivos "
            "e execute novamente. Os dados não acompanham o Git por licença e tamanho."
        )
    print("Preparando os resultados públicos pela primeira vez. Isto pode levar alguns segundos...")
    reproduce_public_experiments(
        str(root / RAW_SOURCES[0]),
        str(root / RAW_SOURCES[1]),
        str(root / "data/processed"),
        str(root / "artifacts"),
        str(root / "artifacts/reproduction_summary.json"),
    )
    generate_result_materials(str(root / "artifacts"), str(root / "artifacts/result_materials"))
    return True


def main() -> int:
    """Prepare local artifacts when needed and start the Streamlit dashboard."""
    parser = argparse.ArgumentParser(description="Abre o painel local do TCC com preparação automática.")
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="gera os resultados necessários sem abrir o navegador",
    )
    args = parser.parse_args()
    try:
        prepared = prepare_dashboard_data()
    except FileNotFoundError as error:
        print(f"\n{error}\n", file=sys.stderr)
        return 2
    if args.prepare_only:
        print("Resultados já estavam prontos." if not prepared else "Resultados preparados com sucesso.")
        return 0
    if dashboard_is_running():
        print(f"O painel já está aberto em {DASHBOARD_URL}.")
        webbrowser.open(DASHBOARD_URL)
        return 0
    print(f"Abrindo o painel em {DASHBOARD_URL} ...")
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "src/pv_monitor/dashboard.py"),
        "--server.address",
        "127.0.0.1",
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    process = subprocess.Popen(command, cwd=ROOT)
    try:
        time.sleep(1)
        webbrowser.open(DASHBOARD_URL)
        return process.wait()
    except KeyboardInterrupt:
        process.terminate()
        return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
