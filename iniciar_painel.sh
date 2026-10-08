#!/usr/bin/env bash
# Atalho para Linux/macOS: prepara o ambiente local e abre o painel.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.11 a 3.13 não foi encontrado. Instale-o e execute este arquivo novamente."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Criando o ambiente local na primeira execução..."
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --disable-pip-version-check -e .
exec .venv/bin/python -m pv_monitor.launcher
