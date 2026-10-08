"""Local dashboard for the PV-soiling monitoring prototype."""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from pv_monitor.data import operational_input_quality_report
from pv_monitor.workflow import detect_additional_loss

ROOT = Path(__file__).resolve().parents[2]
REAL_DATA = ROOT / "data" / "processed" / "laghouat_2022.csv"
MONITOR_METRICS = ROOT / "artifacts" / "laghouat_monitor" / "metrics_validation.json"
FINAL_METRICS = ROOT / "artifacts" / "laghouat_final" / "metrics_test.json"
OPERATIONAL_MODEL = ROOT / "artifacts" / "laghouat_final" / "ridge_refit_development.joblib"


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """Read the local prepared version of the published experiment."""
    frame = pd.read_csv(path, parse_dates=["timestamp"])
    frame["date"] = frame["timestamp"].dt.date
    return frame


@st.cache_data(show_spinner=False)
def load_json(path: str) -> dict:
    """Read a locally generated metrics or summary file."""
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _metrics() -> tuple[dict | None, dict | None]:
    validation = load_json(str(MONITOR_METRICS)) if MONITOR_METRICS.exists() else None
    final = load_json(str(FINAL_METRICS)) if FINAL_METRICS.exists() else None
    return validation, final


def render_overview() -> None:
    """Present the product purpose before implementation details."""
    validation, final = _metrics()
    st.header("Visão geral")
    st.write(
        "Este protótipo estima a potência esperada de um sistema fotovoltaico e compara "
        "a estimativa com a potência medida. Perdas persistentes viram um sinal para inspeção."
    )
    first, second, third = st.columns(3)
    first.metric("Fonte de validação", "Painel limpo × exposto")
    second.metric("Fluxo operacional", "CSV → qualidade → alerta")
    third.metric("Ação do alerta", "Inspecionar")

    if final:
        alert_metrics = final["test_metrics"]["persistent_alert"]
        final_policy = final["locked_alert_policy"]
        st.subheader("Resultado do teste científico")
        left, middle, right = st.columns(3)
        left.metric("F1 dos alertas", f"{alert_metrics['f1']:.3f}")
        middle.metric("Precisão", f"{alert_metrics['precision'] * 100:.1f}%")
        right.metric(
            "Política avaliada",
            f"{final_policy['threshold'] * 100:.0f}% por {final_policy['persistence_days']} dias",
        )
        st.caption(
            "F1 equilibra precisão e sensibilidade dos alertas. Este resultado vale para a base experimental, "
            "não é garantia de desempenho em uma residência brasileira."
        )

    st.subheader("Como usar o painel")
    st.markdown(
        "1. Na aba **Análise de dados**, carregue um CSV com data/hora, irradiância, "
        "temperatura e potência.\n"
        "2. Confira as exclusões e os registros aproveitáveis.\n"
        "3. Gere o indicador diário e investigue alertas persistentes.\n"
        "4. Consulte **Validação científica** para entender de onde vêm as métricas e limites do modelo."
    )
    if not validation or not final:
        st.info("As métricas do experimento ainda não foram geradas localmente.")


def render_operational_monitor() -> None:
    """Render local CSV analysis without persisting uploaded data."""
    st.header("Análise de dados")
    st.write(
        "Carregue um CSV local para analisar a qualidade dos dados, a perda estimada e os alertas diários. "
        "O arquivo não é enviado para a internet nem é armazenado permanentemente pelo painel."
    )
    st.info(
        "Esta é a tela de análise do conjunto selecionado. Em uma futura integração com inversor ou API, "
        "os dados chegariam aqui automaticamente; a análise permaneceria a mesma."
    )
    st.markdown(
        "**Colunas obrigatórias:** `timestamp`, `irradiance_wm2`, `temperature_c` e `power_kw`. "
        "A coluna antiga `module_temperature_c` também é aceita."
    )
    uploaded = st.file_uploader("CSV de medições", type="csv", key="operational_csv")

    control_left, control_middle, control_right = st.columns(3)
    threshold_pct = control_left.number_input(
        "Limiar diário de perda (%)", min_value=1.0, max_value=90.0, value=15.0, step=1.0
    )
    minimum_samples = control_middle.number_input(
        "Mínimo de amostras por dia", min_value=1, max_value=200, value=4, step=1
    )
    persistence_days = control_right.number_input(
        "Dias consecutivos", min_value=1, max_value=30, value=3, step=1
    )
    with st.expander("Parâmetros avançados"):
        minimum_irradiance = st.number_input(
            "Irradiância mínima (W/m²)", min_value=0.0, value=50.0, step=10.0
        )
        minimum_expected_power = st.number_input(
            "Potência esperada mínima (kW)", min_value=0.0, value=0.10, step=0.05
        )
        st.caption("Esses valores devem ser calibrados para a instalação e frequência de medição reais.")

    if uploaded is None:
        st.caption("Selecione um arquivo para iniciar a análise local.")
        return
    if not OPERATIONAL_MODEL.exists():
        st.error("O modelo operacional local ainda não foi gerado. Execute a avaliação final do monitor primeiro.")
        return

    raw_bytes = uploaded.getvalue()
    try:
        preview = pd.read_csv(io.BytesIO(raw_bytes))
    except Exception as error:
        st.error(f"Não foi possível ler o CSV: {error}")
        return
    st.caption(f"Arquivo carregado: {len(preview):,} linhas.".replace(",", "."))
    with st.expander("Prévia dos dados carregados"):
        st.dataframe(preview.head(10), use_container_width=True, hide_index=True)

    if not st.button("Analisar dados e gerar indicador", type="primary"):
        return

    with st.spinner("Validando dados e calculando o indicador..."):
        with tempfile.TemporaryDirectory(prefix="pv-monitor-") as temporary_directory:
            temporary = Path(temporary_directory)
            input_path = temporary / "entrada.csv"
            output_path = temporary / "alertas_diarios.csv"
            input_path.write_bytes(raw_bytes)
            try:
                quality = operational_input_quality_report(str(input_path), minimum_irradiance)
                daily = detect_additional_loss(
                    str(input_path),
                    str(OPERATIONAL_MODEL),
                    str(output_path),
                    minimum_expected_kw=minimum_expected_power,
                    daily_loss_threshold=threshold_pct / 100,
                    minimum_samples_per_day=int(minimum_samples),
                    persistence_days=int(persistence_days),
                    minimum_irradiance_wm2=minimum_irradiance,
                )
                summary = load_json(str(output_path.with_suffix(".summary.json")))
            except (ValueError, KeyError) as error:
                st.error(f"Não foi possível gerar o indicador: {error}")
                return

            alert_days = int(daily["additional_loss_alert"].sum())
            quality_left, quality_middle, quality_right, quality_fourth = st.columns(4)
            quality_left.metric("Linhas recebidas", f"{quality['raw_rows']:,}".replace(",", "."))
            quality_middle.metric("Linhas aproveitáveis", f"{quality['usable_rows']:,}".replace(",", "."))
            quality_right.metric("Duplicidades", quality["duplicate_timestamp_rows_after_validation"])
            quality_fourth.metric("Dias em alerta", alert_days)
            st.caption(
                "Registros noturnos/abaixo da irradiância mínima e leituras inválidas não entram no cálculo. "
                "A qualidade completa pode ser baixada no resumo."
            )
            st.subheader("Perda adicional estimada por dia")
            chart = daily.set_index("date")[["mean_loss_fraction"]].mul(100).rename(
                columns={"mean_loss_fraction": "Perda estimada (%)"}
            )
            st.line_chart(chart, height=280)
            latest = daily.iloc[-1]
            if bool(latest["additional_loss_alert"]):
                st.warning(f"Último dia analisado: {latest['recommended_action']}")
            else:
                st.success(f"Último dia analisado: {latest['recommended_action']}")
            st.caption("Um alerta não confirma sujidade: verifique sensores, disponibilidade, sombra e falhas antes de limpar.")
            display = daily.assign(
                **{
                    "Perda estimada (%)": (daily["mean_loss_fraction"] * 100).round(2),
                    "Potência medida (kW)": daily["mean_observed_power_kw"].round(3),
                    "Potência esperada (kW)": daily["mean_predicted_power_kw"].round(3),
                    "Alerta persistente": daily["additional_loss_alert"].map({True: "Sim", False: "Não"}),
                }
            )
            st.dataframe(
                display[
                    [
                        "date", "samples", "Perda estimada (%)", "Potência medida (kW)",
                        "Potência esperada (kW)", "Alerta persistente", "recommended_action",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
            download_left, download_right = st.columns(2)
            download_left.download_button(
                "Baixar indicadores diários (CSV)",
                data=daily.to_csv(index=False).encode("utf-8"),
                file_name="alertas_diarios.csv",
                mime="text/csv",
            )
            download_right.download_button(
                "Baixar resumo de auditoria (JSON)",
                data=json.dumps(summary, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name="alertas_diarios.summary.json",
                mime="application/json",
            )


def render_validation() -> None:
    """Show the scientific experiment separately from operational use."""
    st.header("Validação científica")
    st.write(
        "Esta aba apresenta o experimento usado para desenvolver e avaliar o monitor. "
        "Ela não representa medições de uma residência brasileira."
    )
    if not REAL_DATA.exists():
        st.warning("O dataset real ainda não foi preparado para visualização.")
        return
    validation, final = _metrics()
    if validation:
        monitor_metrics = validation["validation_metrics"]
        best_name, best_metrics = min(
            monitor_metrics.items(), key=lambda item: item[1]["estimated_soiling_loss"]["mae_fraction"]
        )
        model_col, loss_col, power_col = st.columns(3)
        model_col.metric("Modelo selecionado", best_name.replace("_", " ").title())
        loss_col.metric("Erro médio da perda", f"{best_metrics['estimated_soiling_loss']['mae_fraction'] * 100:.2f} p.p.")
        power_col.metric("Erro da potência limpa", f"{best_metrics['expected_clean_power']['mae_kw'] * 1000:.2f} W")
    if final:
        test = final["test_metrics"]
        test_left, test_middle, test_right = st.columns(3)
        test_left.metric("F1 dos alertas", f"{test['persistent_alert']['f1']:.3f}")
        test_middle.metric("Precisão", f"{test['persistent_alert']['precision'] * 100:.1f}%")
        test_right.metric("Sensibilidade", f"{test['persistent_alert']['recall'] * 100:.1f}%")

    frame = load_data(str(REAL_DATA))
    min_date, max_date = frame["date"].min(), frame["date"].max()
    selected_dates = st.date_input(
        "Período exibido", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start, end = selected_dates
    else:
        start = end = selected_dates
    shown = frame[(frame["date"] >= start) & (frame["date"] <= end)].copy()
    daylight = shown.dropna(subset=["soiling_loss_fraction"]).copy()
    daily = (
        daylight.groupby("date", as_index=False)
        .agg(
            median_loss_fraction=("soiling_loss_fraction", "median"),
            mean_clean_power_w=("power_clean_w", "mean"),
            mean_dusty_power_w=("power_dusty_w", "mean"),
        )
        .sort_values("date")
    )
    loss_chart = daily.set_index("date")[["median_loss_fraction"]].mul(100).rename(
        columns={"median_loss_fraction": "Perda observada (%)"}
    )
    st.subheader("Perda observada entre módulo limpo e exposto")
    st.line_chart(loss_chart, height=280)
    st.caption(
        "Perda = (potência do painel limpo − potência do painel exposto) / potência do painel limpo. "
        "O painel limpo foi usado exclusivamente como referência de desenvolvimento."
    )
    power_chart = daily.set_index("date")[["mean_clean_power_w", "mean_dusty_power_w"]].rename(
        columns={"mean_clean_power_w": "Limpo (W)", "mean_dusty_power_w": "Exposto à poeira (W)"}
    )
    st.subheader("Potência média diária no experimento")
    st.line_chart(power_chart, height=280)


def render_economics_and_method() -> None:
    """Keep optional economics separate from alert generation."""
    st.header("Economia e metodologia")
    st.write(
        "A simulação abaixo ajuda a discutir ordem de grandeza. Ela não é orçamento, economia garantida "
        "nem regra automática para limpeza."
    )
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
    metric_left, metric_middle, metric_right = st.columns(3)
    metric_left.metric("Energia não gerada no experimento", f"{lost_energy_kwh:.2f} kWh")
    metric_middle.metric("Valor potencial recuperável", f"R$ {potential:.2f}")
    metric_right.metric("Saldo do cenário", f"R$ {balance:.2f}")
    st.caption(
        "Cálculo baseado na perda observada da base experimental. Uma residência real exige dados, tarifa e custo próprios."
    )
    with st.expander("Limites metodológicos importantes"):
        st.markdown(
            "- O experimento principal cobre um local e cerca de seis meses.\n"
            "- Chuva é contexto; não é assumida como limpeza garantida.\n"
            "- Um alerta de perda adicional não diferencia sozinho sujidade, falha, sombra ou problema de sensor.\n"
            "- Para uso local, o modelo e os limiares precisam de calibração com dados da instalação."
        )


def main() -> None:
    st.set_page_config(page_title="Monitoramento de perdas FV", page_icon="☀️", layout="wide")
    st.title("Monitoramento de perdas por sujidade em sistemas fotovoltaicos")
    st.caption("Protótipo local de TCC com aprendizado de máquina e resultados auditáveis.")
    overview, operational, validation, economics = st.tabs(
        ["Visão geral", "Análise de dados", "Validação científica", "Economia e metodologia"]
    )
    with overview:
        render_overview()
    with operational:
        render_operational_monitor()
    with validation:
        render_validation()
    with economics:
        render_economics_and_method()


if __name__ == "__main__":
    main()
