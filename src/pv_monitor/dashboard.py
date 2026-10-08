"""Local dashboard for the PV-soiling monitoring prototype."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from pv_monitor.data import operational_input_quality_report

ROOT = Path(__file__).resolve().parents[2]
REAL_DATA = ROOT / "data" / "processed" / "laghouat_2022.csv"
MONITOR_METRICS = ROOT / "artifacts" / "laghouat_monitor" / "metrics_validation.json"
FINAL_METRICS = ROOT / "artifacts" / "laghouat_final" / "metrics_test.json"
FINAL_DAILY_LOSSES = ROOT / "artifacts" / "laghouat_final" / "test_daily_losses.csv"


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """Read the local prepared version of the published experiment."""
    frame = pd.read_csv(path, parse_dates=["timestamp"])
    frame["date"] = frame["timestamp"].dt.date
    return frame


@st.cache_data(show_spinner=False)
def load_json(path: str) -> dict:
    """Read a locally generated metrics file."""
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _metrics() -> tuple[dict | None, dict | None]:
    validation = load_json(str(MONITOR_METRICS)) if MONITOR_METRICS.exists() else None
    final = load_json(str(FINAL_METRICS)) if FINAL_METRICS.exists() else None
    return validation, final


def render_overview() -> None:
    """Present the project purpose before its scientific details."""
    validation, final = _metrics()
    st.header("Visão geral")
    st.write(
        "Este protótipo monitora perdas de geração em sistemas fotovoltaicos ao comparar "
        "a potência esperada em condição limpa com a potência medida."
    )
    first, second, third = st.columns(3)
    first.metric("Base analisada", "Dataset público auditado")
    second.metric("Fonte de validação", "Painel limpo × exposto")
    third.metric("Ação do alerta", "Inspecionar")

    if final:
        alert_metrics = final["test_metrics"]["persistent_alert"]
        policy = final["locked_alert_policy"]
        st.subheader("Resultado do teste científico")
        left, middle, right = st.columns(3)
        left.metric("F1 dos alertas", f"{alert_metrics['f1']:.3f}")
        middle.metric("Precisão", f"{alert_metrics['precision'] * 100:.1f}%")
        right.metric("Política avaliada", f"{policy['threshold'] * 100:.0f}% por {policy['persistence_days']} dias")
        st.caption(
            "F1 equilibra precisão e sensibilidade. Este resultado vale para a base experimental e não é "
            "uma garantia para qualquer residência."
        )

    st.subheader("Como navegar")
    st.markdown(
        "1. Em **Análise de dados**, explore o recorte final do dataset público selecionado.\n"
        "2. Em **Validação científica**, veja como o modelo foi avaliado sem misturar treino e teste.\n"
        "3. Em **Economia e metodologia**, consulte o cenário financeiro e as limitações."
    )
    if not validation or not final:
        st.info("As métricas do experimento ainda não foram geradas localmente.")


def render_public_data_analysis() -> None:
    """Analyze only the approved public source and its preserved final test."""
    st.header("Análise de dados")
    st.write(
        "Esta tela utiliza exclusivamente o dataset público de Laghouat já auditado e baixado para o projeto. "
        "Ela não aceita arquivos arbitrários nem fontes sem proveniência documentada."
    )
    st.markdown(
        "**Fonte:** [Hourly PV Power and Dust Accumulation Dataset — Laghouat, Algeria, February–August 2022]"
        "(https://doi.org/10.17632/4jdt83yy43.3), licença CC BY 4.0. "
        "O experimento compara um módulo lavado diariamente a outro exposto à poeira."
    )
    if not REAL_DATA.exists() or not FINAL_DAILY_LOSSES.exists():
        st.warning("Os dados preparados ou os resultados do teste final ainda não estão disponíveis localmente.")
        return

    quality = operational_input_quality_report(str(REAL_DATA))
    daily = pd.read_csv(FINAL_DAILY_LOSSES)
    final = load_json(str(FINAL_METRICS)) if FINAL_METRICS.exists() else None
    quality_left, quality_middle, quality_right, quality_fourth = st.columns(4)
    quality_left.metric("Registros publicados", f"{quality['raw_rows']:,}".replace(",", "."))
    quality_middle.metric("Registros diurnos aproveitáveis", f"{quality['usable_rows']:,}".replace(",", "."))
    quality_right.metric("Duplicidades", quality["duplicate_timestamp_rows_after_validation"])
    quality_fourth.metric("Dias em alerta no teste", int(daily["estimated_persistent_alert"].sum()))
    st.caption(
        "A análise usa somente o teste final preservado. Registros noturnos e abaixo de 50 W/m² não entram "
        "no cálculo de perda."
    )

    st.subheader("Perda diária: referência observada e estimativa do modelo")
    chart = daily.set_index("date")[["observed_loss_fraction", "estimated_loss_fraction"]].mul(100).rename(
        columns={
            "observed_loss_fraction": "Observada no experimento (%)",
            "estimated_loss_fraction": "Estimada pelo monitor (%)",
        }
    )
    st.line_chart(chart, height=300)
    if final:
        policy = final["locked_alert_policy"]
        st.caption(
            f"Alerta avaliado: perda estimada de pelo menos {policy['threshold'] * 100:.0f}% "
            f"por {policy['persistence_days']} dias consecutivos. Um alerta prioriza investigação; "
            "ele não confirma sozinho a causa da perda."
        )
    display = daily.assign(
        **{
            "Perda observada (%)": (daily["observed_loss_fraction"] * 100).round(2),
            "Perda estimada (%)": (daily["estimated_loss_fraction"] * 100).round(2),
            "Alerta estimado": daily["estimated_persistent_alert"].map({True: "Sim", False: "Não"}),
        }
    )
    st.dataframe(
        display[["date", "samples", "Perda observada (%)", "Perda estimada (%)", "Alerta estimado"]],
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Baixar resultados do teste final (CSV)",
        data=daily.to_csv(index=False).encode("utf-8"),
        file_name="laghouat_teste_final_alertas.csv",
        mime="text/csv",
    )


def render_validation() -> None:
    """Show the development experiment separately from the final data analysis."""
    st.header("Validação científica")
    st.write(
        "Esta aba explica como o monitor foi desenvolvido e avaliado. Ela não representa medições de "
        "uma residência brasileira."
    )
    if not REAL_DATA.exists():
        st.warning("O dataset real ainda não foi preparado para visualização.")
        return
    validation, final = _metrics()
    if validation:
        metrics = validation["validation_metrics"]
        best_name, best_metrics = min(
            metrics.items(), key=lambda item: item[1]["estimated_soiling_loss"]["mae_fraction"]
        )
        model_col, loss_col, power_col = st.columns(3)
        model_col.metric("Modelo selecionado", best_name.replace("_", " ").title())
        loss_col.metric("Erro médio da perda", f"{best_metrics['estimated_soiling_loss']['mae_fraction'] * 100:.2f} p.p.")
        power_col.metric("Erro da potência limpa", f"{best_metrics['expected_clean_power']['mae_kw'] * 1000:.2f} W")
    if final:
        test = final["test_metrics"]["persistent_alert"]
        first, second, third = st.columns(3)
        first.metric("F1 dos alertas", f"{test['f1']:.3f}")
        second.metric("Precisão", f"{test['precision'] * 100:.1f}%")
        third.metric("Sensibilidade", f"{test['recall'] * 100:.1f}%")

    frame = load_data(str(REAL_DATA))
    min_date, max_date = frame["date"].min(), frame["date"].max()
    dates = st.date_input("Período exibido", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    start, end = dates if isinstance(dates, tuple) and len(dates) == 2 else (dates, dates)
    daylight = frame[(frame["date"] >= start) & (frame["date"] <= end)].dropna(subset=["soiling_loss_fraction"])
    daily = daylight.groupby("date", as_index=False).agg(
        median_loss_fraction=("soiling_loss_fraction", "median"),
        mean_clean_power_w=("power_clean_w", "mean"),
        mean_dusty_power_w=("power_dusty_w", "mean"),
    )
    st.subheader("Perda observada entre módulo limpo e exposto")
    st.line_chart(
        daily.set_index("date")[["median_loss_fraction"]].mul(100).rename(
            columns={"median_loss_fraction": "Perda observada (%)"}
        ),
        height=280,
    )
    st.subheader("Potência média diária no experimento")
    st.line_chart(
        daily.set_index("date")[["mean_clean_power_w", "mean_dusty_power_w"]].rename(
            columns={"mean_clean_power_w": "Limpo (W)", "mean_dusty_power_w": "Exposto à poeira (W)"}
        ),
        height=280,
    )


def render_economics_and_method() -> None:
    """Keep optional economics separate from alerts and scientific validation."""
    st.header("Economia e metodologia")
    st.write("A simulação ajuda a discutir ordem de grandeza; não é orçamento nem regra automática de limpeza.")
    if not REAL_DATA.exists():
        st.warning("O dataset real ainda não foi preparado para a simulação.")
        return
    frame = load_data(str(REAL_DATA)).dropna(subset=["soiling_loss_fraction"])
    daily = frame.groupby("date", as_index=False).agg(
        clean_energy_wh=("power_clean_w", "sum"), dusty_energy_wh=("power_dusty_w", "sum")
    )
    lost_energy_kwh = max(float((daily["clean_energy_wh"] - daily["dusty_energy_wh"]).sum() / 1000), 0.0)
    left, middle, right = st.columns(3)
    tariff = left.number_input("Valor da energia (R$/kWh)", min_value=0.0, value=0.80, step=0.01)
    cleaning_cost = middle.number_input("Custo da limpeza (R$)", min_value=0.0, value=200.0, step=10.0)
    recovery = right.slider("Recuperação assumida após limpeza (%)", 0, 100, 100, 5)
    potential = lost_energy_kwh * tariff * (recovery / 100)
    balance = potential - cleaning_cost
    first, second, third = st.columns(3)
    first.metric("Energia não gerada no experimento", f"{lost_energy_kwh:.2f} kWh")
    second.metric("Valor potencial recuperável", f"R$ {potential:.2f}")
    third.metric("Saldo do cenário", f"R$ {balance:.2f}")
    st.caption("Uma residência real exige dados, tarifa e custo próprios.")
    with st.expander("Limites metodológicos importantes"):
        st.markdown(
            "- O experimento cobre um local e cerca de seis meses.\n"
            "- Chuva é contexto; não é assumida como limpeza garantida.\n"
            "- Um alerta não diferencia sozinho sujidade, falha, sombra ou problema de sensor.\n"
            "- O modelo e os limiares precisam de calibração antes do uso em uma instalação local."
        )


def main() -> None:
    st.set_page_config(page_title="Monitoramento de perdas FV", page_icon="☀️", layout="wide")
    st.title("Monitoramento de perdas por sujidade em sistemas fotovoltaicos")
    st.caption("Protótipo local de TCC com aprendizado de máquina e resultados auditáveis.")
    overview, analysis, validation, economics = st.tabs(
        ["Visão geral", "Análise de dados", "Validação científica", "Economia e metodologia"]
    )
    with overview:
        render_overview()
    with analysis:
        render_public_data_analysis()
    with validation:
        render_validation()
    with economics:
        render_economics_and_method()


if __name__ == "__main__":
    main()
