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
    """Obtain the daily clean-reference and measured power in the final period."""
    frame = load_data(str(REAL_DATA)).dropna(subset=["clean_reference_power_kw", "power_kw"])
    selected = frame[frame["date"].between(daily["date"].min(), daily["date"].max())]
    return selected.groupby("date", as_index=False).agg(
        expected_clean_power_kw=("clean_reference_power_kw", "mean"),
        measured_power_kw=("power_kw", "mean"),
    )


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
    """Present the central monitoring idea without technical implementation details."""
    st.markdown('<div class="eyebrow">PROTÓTIPO DE TCC · DADOS PÚBLICOS AUDITADOS</div>', unsafe_allow_html=True)
    st.title("Monitoramento de perdas por sujidade")
    st.markdown(
        '<div class="lead">O sistema observa quando a geração do painel fica abaixo do que seria esperado em uma condição limpa. '
        'Se essa diferença persiste, ele recomenda uma inspeção.</div>',
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
    loss_percent = max(100 - generated_percent, 0)
    alert_days = int(daily["estimated_persistent_alert"].sum())

    first, second, third, fourth = st.columns(4)
    first.metric("Geração esperada", "100 unidades")
    second.metric("Geração medida", f"{generated_percent:.1f} unidades")
    third.metric("Perda identificada", f"{loss_percent:.1f}%")
    fourth.metric("Dias que pedem inspeção", f"{alert_days} de {len(daily)}")
    st.markdown(
        f'<div class="summary"><strong>Leitura principal:</strong> no período analisado, para cada 100 unidades de energia '
        f'esperadas, cerca de {generated_percent:.0f} foram medidas. A diferença representa uma perda aproximada de '
        f'{loss_percent:.0f}%. Quando a perda estimada fica acima de {policy["threshold"] * 100:.0f}% por '
        f'{policy["persistence_days"]} dias, o sistema indica que vale a pena investigar.</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Geração medida em relação ao esperado")
    relative_generation = power.assign(
        generation_of_expected_percent=(power["measured_power_kw"] / power["expected_clean_power_kw"] * 100)
    ).set_index("date")[["generation_of_expected_percent"]].rename(
        columns={"generation_of_expected_percent": "Geração medida (% do esperado)"}
    )
    st.line_chart(relative_generation, height=310)
    st.caption(
        "Quanto mais a linha se afasta de 100%, maior é a diferença entre a geração medida e a geração esperada. "
        "A curva usa o recorte final do experimento público."
    )

    st.subheader("Como o monitor ajuda")
    first, second, third = st.columns(3)
    first.markdown('<div class="step"><strong>1. Observa</strong><br><br>Compara a geração medida com a geração esperada para o mesmo momento.</div>', unsafe_allow_html=True)
    second.markdown('<div class="step"><strong>2. Identifica</strong><br><br>Procura diferenças que continuam por vários dias, e não uma variação isolada.</div>', unsafe_allow_html=True)
    third.markdown('<div class="step"><strong>3. Orienta</strong><br><br>Sugere inspeção para verificar sujeira, sombra, falha ou problema de medição.</div>', unsafe_allow_html=True)

    st.markdown(
        '<p class="footnote">Esta demonstração usa um experimento de painel limpo versus painel exposto à poeira, em Laghouat, Argélia. '
        'O protótipo é uma ferramenta de apoio à inspeção: uma instalação real precisa de calibração e validação com seus próprios dados.</p>',
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Monitoramento de perdas FV", page_icon="☀️", layout="wide")
    apply_theme()
    render_dashboard()


if __name__ == "__main__":
    main()
