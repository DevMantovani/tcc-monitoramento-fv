"""Local dashboard for the PV-soiling monitoring prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from pv_monitor.data import operational_input_quality_report

ROOT = Path(__file__).resolve().parents[2]
REAL_DATA = ROOT / "data" / "processed" / "laghouat_2022.csv"
MONITOR_METRICS = ROOT / "artifacts" / "laghouat_monitor" / "metrics_validation.json"
FINAL_METRICS = ROOT / "artifacts" / "laghouat_final" / "metrics_test.json"
FINAL_DAILY_LOSSES = ROOT / "artifacts" / "laghouat_final" / "test_daily_losses.csv"
CONDITION_PERFORMANCE = ROOT / "artifacts" / "laghouat_monitoring_evidence" / "condition_performance.csv"
MONTHLY_STABILITY = ROOT / "artifacts" / "laghouat_monitoring_evidence" / "monthly_alert_stability.csv"


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """Read the prepared version of the published experiment."""
    frame = pd.read_csv(path, parse_dates=["timestamp"])
    frame["date"] = frame["timestamp"].dt.date
    return frame


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    """Read a generated local report."""
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_json(path: str) -> dict[str, Any]:
    """Read a local metrics report."""
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def metrics() -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    validation = load_json(str(MONITOR_METRICS)) if MONITOR_METRICS.exists() else None
    final = load_json(str(FINAL_METRICS)) if FINAL_METRICS.exists() else None
    return validation, final


def daily_losses() -> pd.DataFrame | None:
    if not FINAL_DAILY_LOSSES.exists():
        return None
    daily = load_csv(str(FINAL_DAILY_LOSSES)).copy()
    daily["date"] = pd.to_datetime(daily["date"])
    return daily.sort_values("date")


def apply_theme() -> None:
    """Set a restrained visual hierarchy for the local dashboard."""
    st.markdown(
        """
        <style>
          .stApp { background: #fbfcfc; }
          .block-container { max-width: 1180px; padding-top: 2.1rem; padding-bottom: 3rem; }
          h1, h2, h3 { color: #17324d; letter-spacing: -0.02em; }
          [data-testid="stMetric"] { background: #fff; border: 1px solid #dbe4e7; border-radius: 10px; padding: 1rem; min-height: 116px; }
          [data-testid="stMetricLabel"] { color: #5f6f7d; }
          [data-testid="stMetricValue"] { color: #17324d; }
          .eyebrow { color: #16765d; font-size: .76rem; font-weight: 700; letter-spacing: .09em; }
          .lead { color: #5f6f7d; font-size: 1.06rem; max-width: 810px; }
          .action-box { background: #edf7f3; border-left: 4px solid #16765d; border-radius: 4px; color: #17324d; margin: 1rem 0 1.3rem; padding: 1rem 1.1rem; }
          .note-box { background: #f4f7f7; border: 1px solid #dbe4e7; border-radius: 8px; color: #5f6f7d; margin: 1rem 0; padding: .9rem 1rem; }
          [data-testid="stTabs"] button { font-size: .95rem; padding: .65rem 1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def missing_results() -> None:
    st.warning("Os resultados locais ainda não estão disponíveis. Execute `pv-launch` ou siga o README para preparar as fontes públicas.")


def render_panel() -> None:
    """Show decision-oriented information before scientific detail."""
    daily = daily_losses()
    _, final = metrics()
    st.markdown('<div class="eyebrow">DEMONSTRAÇÃO OPERACIONAL</div>', unsafe_allow_html=True)
    st.header("Painel de monitoramento")
    st.markdown(
        '<div class="lead">O monitor compara a potência medida com a potência esperada em condição limpa. '
        'Se a perda estimada persiste, a ação indicada é investigar — não limpar automaticamente.</div>',
        unsafe_allow_html=True,
    )
    if daily is None or final is None:
        missing_results()
        return

    policy = final["locked_alert_policy"]
    latest = daily.iloc[-1]
    has_alert = bool(latest["estimated_persistent_alert"])
    displayed_loss = max(float(latest["estimated_loss_fraction"]), 0.0)
    status = "Inspeção recomendada" if has_alert else "Sem alerta persistente"
    action = (
        "A perda estimada atingiu a persistência definida para o experimento. Verifique o sistema antes de decidir limpar."
        if has_alert
        else "Não há alerta persistente no último dia do recorte. Continue acompanhando a tendência de perda."
    )
    first, second, third, fourth = st.columns(4)
    first.metric("Situação atual", status)
    second.metric("Perda estimada", f"{displayed_loss * 100:.1f}%")
    third.metric("Regra de alerta", f"{policy['threshold'] * 100:.0f}% por {policy['persistence_days']} dias")
    fourth.metric("Período demonstrado", pd.Timestamp(latest["date"]).strftime("%d/%m/%Y"))
    st.markdown(f'<div class="action-box"><strong>Orientação:</strong> {action}</div>', unsafe_allow_html=True)
    st.caption("O painel mostra o último dia do teste final de Laghouat; não é leitura ao vivo nem representa automaticamente uma residência brasileira. Valores negativos pontuais são tratados como ausência de perda na leitura operacional, pois podem resultar de ruído de medição.")

    st.subheader("Tendência recente de perda estimada")
    st.line_chart(
        daily.tail(14).set_index("date")[["estimated_loss_fraction"]].mul(100).rename(
            columns={"estimated_loss_fraction": "Perda estimada (%)"}
        ),
        height=280,
    )
    st.subheader("Como interpretar")
    first, second, third = st.columns(3)
    first.markdown("**1. Acompanhar**\n\nObserve se a perda estimada cresce ou se mantém elevada.")
    second.markdown("**2. Investigar**\n\nUm alerta persistente orienta verificar sujeira, sombra, falhas ou sensores.")
    third.markdown("**3. Decidir**\n\nA limpeza depende de inspeção, custo e condições específicas da instalação.")


def render_history() -> None:
    """Present the held-out experiment history with an optional data table."""
    daily = daily_losses()
    st.markdown('<div class="eyebrow">SÉRIE DO EXPERIMENTO</div>', unsafe_allow_html=True)
    st.header("Histórico de perdas")
    st.write("A comparação mostra a referência medida no experimento e a estimativa entregue pelo monitor no período final preservado.")
    if daily is None:
        missing_results()
        return
    chart = daily.set_index("date")[["observed_loss_fraction", "estimated_loss_fraction"]].mul(100).rename(
        columns={"observed_loss_fraction": "Perda observada no experimento (%)", "estimated_loss_fraction": "Perda estimada pelo monitor (%)"}
    )
    st.line_chart(chart, height=330)
    st.caption("A perda observada usa o painel limpo como referência supervisionada. Em campo, o monitor usa potência medida e potência limpa esperada.")
    first, second, third = st.columns(3)
    first.metric("Dias analisados", len(daily))
    second.metric("Dias com alerta", int(daily["estimated_persistent_alert"].sum()))
    third.metric("Maior perda estimada", f"{daily['estimated_loss_fraction'].max() * 100:.1f}%")
    with st.expander("Consultar os valores diários"):
        display = daily.assign(
            **{
                "Perda observada (%)": (daily["observed_loss_fraction"] * 100).round(2),
                "Perda estimada (%)": (daily["estimated_loss_fraction"] * 100).round(2),
                "Alerta persistente": daily["estimated_persistent_alert"].map({True: "Sim", False: "Não"}),
            }
        )
        st.dataframe(display[["date", "samples", "Perda observada (%)", "Perda estimada (%)", "Alerta persistente"]], width="stretch", hide_index=True)
        st.download_button("Baixar resultados do teste final (CSV)", daily.to_csv(index=False).encode("utf-8"), "laghouat_teste_final_alertas.csv", "text/csv")


def render_evidence() -> None:
    """Show monitoring evidence as behavior, not as a model ranking."""
    st.markdown('<div class="eyebrow">EVIDÊNCIAS DO MONITOR</div>', unsafe_allow_html=True)
    st.header("Desempenho no experimento público")
    st.write("As evidências descrevem o monitor já selecionado. Elas mostram onde a estimativa é mais ou menos precisa dentro do experimento, sem comparar algoritmos.")
    _, final = metrics()
    if final:
        alerts = final["test_metrics"]["persistent_alert"]
        power = final["test_metrics"]["expected_clean_power"]
        first, second, third = st.columns(3)
        first.metric("Erro médio da perda", f"{final['test_metrics']['estimated_soiling_loss']['mae_fraction'] * 100:.2f} p.p.")
        second.metric("Alertas corretos", f"{alerts['precision'] * 100:.1f}%")
        third.metric("Erro da potência esperada", f"{power['mae_kw'] * 1000:.2f} W")
        st.caption("Valores obtidos uma única vez no período final separado do desenvolvimento do monitor.")
    if CONDITION_PERFORMANCE.exists():
        conditions = load_csv(str(CONDITION_PERFORMANCE))
        st.subheader("Precisão por faixa de irradiância")
        st.bar_chart(conditions.set_index("condition")[["mae_loss_percentage_points"]].rename(columns={"mae_loss_percentage_points": "Erro médio da perda (p.p.)"}), height=280)
        st.markdown('<div class="note-box"><strong>Leitura:</strong> próximo ao limite mínimo de irradiância, a estimativa de perda é menos precisa. Esse comportamento deve ser considerado antes de uso em campo.</div>', unsafe_allow_html=True)
    if MONTHLY_STABILITY.exists():
        monthly = load_csv(str(MONTHLY_STABILITY))
        st.subheader("Estabilidade da regra de alerta")
        st.bar_chart(monthly.set_index("month")[["precision", "recall"]].mul(100).rename(columns={"precision": "Alertas corretos (%)", "recall": "Eventos identificados (%)"}), height=260)
        st.caption("Os dois meses pertencem ao mesmo experimento; não são validações independentes.")
    st.info("A verificação em uma segunda fonte pública, de Dhaka, não confirmou transferência automática do monitor. Antes de uso residencial, são necessários dados confiáveis, controle de qualidade e validação local.")


def render_method_and_scenario() -> None:
    """Keep provenance, limits and optional economics secondary to operations."""
    st.markdown('<div class="eyebrow">MÉTODO E LIMITES</div>', unsafe_allow_html=True)
    st.header("Base científica e cenário econômico")
    st.write("A demonstração usa exclusivamente a base pública auditada de Laghouat, Argélia, com um painel limpo diariamente e outro exposto à poeira. Ela é evidência de protótipo, não promessa de desempenho local.")
    st.markdown("**Fonte:** [Hourly PV Power and Dust Accumulation Dataset — Laghouat, Algeria, February–August 2022](https://doi.org/10.17632/4jdt83yy43.3), licença CC BY 4.0.")
    if not REAL_DATA.exists():
        missing_results()
        return
    quality = operational_input_quality_report(str(REAL_DATA))
    first, second, third = st.columns(3)
    first.metric("Registros publicados", f"{quality['raw_rows']:,}".replace(",", "."))
    second.metric("Registros diurnos utilizáveis", f"{quality['usable_rows']:,}".replace(",", "."))
    third.metric("Timestamps duplicados", quality["duplicate_timestamp_rows_after_validation"])
    st.subheader("Cenário econômico exploratório")
    frame = load_data(str(REAL_DATA)).dropna(subset=["soiling_loss_fraction"])
    energy = frame.groupby("date", as_index=False).agg(clean_energy_wh=("power_clean_w", "sum"), dusty_energy_wh=("power_dusty_w", "sum"))
    lost_energy_kwh = max(float((energy["clean_energy_wh"] - energy["dusty_energy_wh"]).sum() / 1000), 0.0)
    left, middle, right = st.columns(3)
    tariff = left.number_input("Valor da energia (R$/kWh)", min_value=0.0, value=0.80, step=0.01)
    cleaning_cost = middle.number_input("Custo da limpeza (R$)", min_value=0.0, value=200.0, step=10.0)
    recovery = right.slider("Recuperação assumida após limpeza (%)", 0, 100, 100, 5)
    potential = lost_energy_kwh * tariff * (recovery / 100)
    first, second, third = st.columns(3)
    first.metric("Energia não gerada no experimento", f"{lost_energy_kwh:.2f} kWh")
    second.metric("Valor potencial recuperável", f"R$ {potential:.2f}")
    third.metric("Saldo do cenário", f"R$ {potential - cleaning_cost:.2f}")
    st.caption("O cálculo é uma simulação didática com premissas editáveis; não é orçamento nem indicação automática de limpeza.")
    with st.expander("Consultar detalhes técnicos e limitações"):
        validation, final = metrics()
        if validation and final:
            policy = final["locked_alert_policy"]
            st.markdown(
                f"- O estimador **{final['model_name'].replace('_', ' ').title()}** foi escolhido internamente na validação cronológica; o TCC não o apresenta como vencedor universal.\n"
                f"- A regra avaliada foi perda estimada de {policy['threshold'] * 100:.0f}% por {policy['persistence_days']} dias consecutivos.\n"
                "- A perda pode envolver sujeira, sombra, falha, degradação, indisponibilidade ou erro de sensor.\n"
                "- A verificação em Dhaka não demonstrou generalização automática entre instalações.\n"
                "- Não há, nesta etapa, dados de uma residência brasileira."
            )


def main() -> None:
    st.set_page_config(page_title="Monitoramento de perdas FV", page_icon="☀️", layout="wide")
    apply_theme()
    st.title("Monitoramento de perdas por sujidade")
    st.caption("Sistemas fotovoltaicos · protótipo acadêmico com resultados reproduzíveis")
    panel, history, evidence, method = st.tabs(["Painel", "Histórico", "Evidências", "Método e cenário"])
    with panel:
        render_panel()
    with history:
        render_history()
    with evidence:
        render_evidence()
    with method:
        render_method_and_scenario()


if __name__ == "__main__":
    main()
