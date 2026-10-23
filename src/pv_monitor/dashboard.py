"""Simple presentation dashboard for the PV-soiling monitoring prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
REAL_DATA = ROOT / "data" / "processed" / "laghouat_2022.csv"
FINAL_METRICS = ROOT / "artifacts" / "laghouat_final" / "metrics_test.json"
FINAL_DAILY_LOSSES = ROOT / "artifacts" / "laghouat_final" / "test_daily_losses.csv"


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """Read the prepared public experiment."""
    frame = pd.read_csv(path, parse_dates=["timestamp"])
    frame["date"] = frame["timestamp"].dt.normalize()
    return frame


@st.cache_data(show_spinner=False)
def load_daily_losses(path: str) -> pd.DataFrame:
    """Read the saved final-test daily results."""
    daily = pd.read_csv(path, parse_dates=["date"])
    return daily.sort_values("date")


@st.cache_data(show_spinner=False)
def load_json(path: str) -> dict[str, Any]:
    """Read the frozen final-test configuration."""
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def test_power_series(daily: pd.DataFrame) -> pd.DataFrame:
    """Use only saved model predictions from the evaluated test observations."""
    required = {"date", "expected_clean_power_kw", "measured_power_kw"}
    if not required.issubset(daily.columns):
        raise ValueError("Resultados antigos: reproduza o experimento para obter a referência do modelo.")
    return daily[["date", "expected_clean_power_kw", "measured_power_kw"]].copy()


def apply_theme() -> None:
    """Use a high-contrast dark presentation theme."""
    st.markdown(
        """
        <style>
          .stApp, [data-testid="stAppViewContainer"] { background: #0b1220; color: #e7edf5; }
          [data-testid="stHeader"] { background: rgba(11, 18, 32, .96); }
          .block-container { max-width: 1120px; padding-top: 2.5rem; padding-bottom: 3rem; }
          h1, h2, h3 { color: #f4f8fc; letter-spacing: -.025em; }
          p, li, [data-testid="stMarkdownContainer"] { color: #d8e2ec; }
          [data-testid="stMetric"] { background: #131f2c; border: 1px solid #2b3d4f; border-radius: 10px; min-height: 120px; padding: 1rem; }
          [data-testid="stMetricLabel"] { color: #a8b8c8; }
          [data-testid="stMetricValue"] { color: #f4f8fc; }
          .eyebrow { color: #6ee7b7; font-size: .76rem; font-weight: 700; letter-spacing: .1em; }
          .lead { color: #bdcad7; font-size: 1.1rem; line-height: 1.55; max-width: 780px; }
          .summary { background: #102a22; border-left: 4px solid #46c796; border-radius: 4px; color: #e1f6ec; margin: 1.25rem 0 1.5rem; padding: 1rem 1.15rem; }
          .step { background: #131f2c; border: 1px solid #2b3d4f; border-radius: 10px; min-height: 132px; padding: 1rem 1.1rem; }
          .step strong { color: #6ee7b7; }
          .footnote { color: #9eb0c0; font-size: .9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    """Present a product-like monitoring view using clearly labelled demo data."""
    st.markdown('<div class="eyebrow">PAINEL OPERACIONAL · MODO DEMONSTRAÇÃO</div>', unsafe_allow_html=True)
    st.title("Monitoramento fotovoltaico")
    st.markdown(
        '<div class="lead">Acompanhe se a geração medida está abaixo do esperado e receba uma orientação de inspeção '
        'quando essa diferença persistir.</div>',
        unsafe_allow_html=True,
    )
    if not (REAL_DATA.exists() and FINAL_DAILY_LOSSES.exists() and FINAL_METRICS.exists()):
        st.warning("Os resultados locais ainda não estão disponíveis. Execute `pv-launch` para preparar a demonstração.")
        return

    daily = load_daily_losses(str(FINAL_DAILY_LOSSES))
    power = test_power_series(daily)
    final = load_json(str(FINAL_METRICS))
    policy = final["locked_alert_policy"]
    expected = float(power["expected_clean_power_kw"].mean())
    measured = float(power["measured_power_kw"].mean())
    generated_percent = max(measured / expected * 100, 0) if expected else 0
    loss_percent = float(daily["estimated_loss_fraction"].median()) * 100
    alert_days = int(daily["estimated_persistent_alert"].sum())

    first, second, third, fourth = st.columns(4)
    first.metric("Situação do período", "Atenção" if alert_days else "Normal")
    second.metric("Geração medida", f"{generated_percent:.1f}% do esperado")
    third.metric("Perda diária típica", f"{loss_percent:.1f}%")
    fourth.metric("Calibração", "Referência experimental")
    st.markdown(
        f'<div class="summary"><strong>Ação recomendada:</strong> investigar a instalação quando a geração fica abaixo de '
        f'{100 - policy["threshold"] * 100:.0f}% do esperado por {policy["persistence_days"]} dias consecutivos. '
        f'No recorte demonstrativo, isso ocorreu em {alert_days} de {len(daily)} dias.</div>',
        unsafe_allow_html=True,
    )
    st.caption("Demonstração: a potência esperada vem do modelo treinado em Laghouat. Perda diária típica é a mediana das perdas diárias estimadas; não é perda de energia acumulada. A referência limpa medida é usada apenas na avaliação científica.")

    st.subheader("Desempenho da geração")
    relative_generation = power.assign(
        generation_of_expected_percent=(power["measured_power_kw"] / power["expected_clean_power_kw"] * 100)
    ).set_index("date")[["generation_of_expected_percent"]].rename(
        columns={"generation_of_expected_percent": "Geração medida (% do esperado)"}
    )
    st.line_chart(relative_generation, height=310)
    st.caption(
        "Razão entre potências médias diárias nas mesmas observações do teste. A curva usa a previsão do modelo. O alerta usa a mediana diária das perdas e reinicia após dias ausentes; os dois indicadores têm agregações diferentes."
    )

    st.subheader("Entenda os indicadores")
    first, second, third = st.columns(3)
    first.markdown('<div class="step"><strong>Geração medida</strong><br><br>Mostra o quanto o sistema entregou em relação ao esperado.</div>', unsafe_allow_html=True)
    second.markdown('<div class="step"><strong>Perda diária típica</strong><br><br>Resume a perda calculada a partir do modelo. Uma perda pode ter mais de uma causa.</div>', unsafe_allow_html=True)
    third.markdown('<div class="step"><strong>Ação recomendada</strong><br><br>O alerta pede inspeção. Ele não confirma sujeira nem aciona limpeza automática.</div>', unsafe_allow_html=True)

    st.markdown(
        '<p class="footnote">Dados demonstrativos: experimento público de painel limpo versus painel exposto à poeira, em Laghouat, Argélia. '
        'O protótipo apoia inspeção; uma instalação real precisa de calibração e validação com seus próprios dados.</p>',
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Monitoramento de perdas FV", page_icon="☀️", layout="wide")
    apply_theme()
    render_dashboard()


if __name__ == "__main__":
    main()
