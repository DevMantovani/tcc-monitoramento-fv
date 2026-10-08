"""Local dashboard for the published clean-versus-dusty PV experiment."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
REAL_DATA = ROOT / "data" / "processed" / "laghouat_2022.csv"
MONITOR_METRICS = ROOT / "artifacts" / "laghouat_monitor" / "metrics_validation.json"


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """Read the locally prepared version of the published dataset."""
    frame = pd.read_csv(path, parse_dates=["timestamp"])
    frame["date"] = frame["timestamp"].dt.date
    return frame


@st.cache_data(show_spinner=False)
def load_monitor_metrics(path: str) -> dict:
    """Read local validation results produced by the monitoring workflow."""
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    st.set_page_config(page_title="Monitoramento de perdas FV", page_icon="☀️", layout="wide")
    st.title("Monitoramento de perdas por sujidade em sistemas fotovoltaicos")
    st.caption(
        "Protótipo com aprendizado de máquina: estima a potência esperada em condição limpa e a compara com a potência medida do sistema."
    )

    if not REAL_DATA.exists():
        st.warning("O dataset real ainda não foi preparado para visualização.")
        st.code(
            "pv-monitor prepare-laghouat "
            "--input data/raw/laghouat_2022/Laghouat_2022_final.csv "
            "--output data/processed/laghouat_2022.csv"
        )
        return

    frame = load_data(str(REAL_DATA))
    if MONITOR_METRICS.exists():
        monitor_metrics = load_monitor_metrics(str(MONITOR_METRICS))["validation_metrics"]
        best_name, best_metrics = min(
            monitor_metrics.items(),
            key=lambda item: item[1]["estimated_soiling_loss"]["mae_fraction"],
        )
        loss_mae_pp = best_metrics["estimated_soiling_loss"]["mae_fraction"] * 100
        clean_mae_w = best_metrics["expected_clean_power"]["mae_kw"] * 1000
        st.subheader("Validação do monitor por aprendizado de máquina")
        model_col, loss_col, power_col = st.columns(3)
        model_col.metric("Modelo com menor erro de validação", best_name.replace("_", " ").title())
        loss_col.metric("Erro médio na perda estimada", f"{loss_mae_pp:.2f} p.p.")
        power_col.metric("Erro médio na potência limpa estimada", f"{clean_mae_w:.2f} W")
        st.caption(
            "Validação cronológica nesta base. O painel limpo é usado apenas como referência de desenvolvimento; "
            "o sinal operacional do monitor é a potência medida do sistema combinada às variáveis ambientais."
        )
    else:
        st.info(
            "O conjunto foi preparado, mas o modelo ainda não foi treinado. Execute `pv-monitor train-soiling-monitor` "
            "para produzir as métricas de validação locais."
        )
    min_date, max_date = frame["date"].min(), frame["date"].max()
    selected_dates = st.sidebar.date_input("Período exibido", value=(min_date, max_date), min_value=min_date, max_value=max_date)
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
            clean_energy_wh=("power_clean_w", "sum"),
            dusty_energy_wh=("power_dusty_w", "sum"),
            median_dust_density_gm2=("dust_density_reconstructed_gm2", "median"),
            valid_records=("soiling_loss_fraction", "size"),
        )
    )
    rainfall = shown.groupby("date", as_index=False).agg(precipitation_mm=("precipitation_mm", "sum"))
    daily = daily.merge(rainfall, on="date", how="left")
    daily["lost_energy_kwh"] = (daily["clean_energy_wh"] - daily["dusty_energy_wh"]) / 1000

    st.sidebar.markdown("### Explorar um limite")
    threshold_pct = st.sidebar.slider("Perda diária de referência (%)", 0.0, 30.0, 10.0, 0.5)
    st.sidebar.caption("É um filtro visual configurável; não representa uma ordem de limpeza.")

    st.sidebar.markdown("### Cenário econômico residencial")
    tariff_brl_kwh = st.sidebar.number_input(
        "Valor da energia (R$/kWh)", min_value=0.0, value=0.80, step=0.01,
        help="Referência inicial: R$ 0,80/kWh, sem tributos. Substitua pelo valor aplicável à instalação.",
    )
    cleaning_cost_brl = st.sidebar.number_input(
        "Custo da limpeza (R$)", min_value=0.0, value=200.0, step=10.0,
        help="Referência inicial: R$ 200, ponto médio de uma faixa residencial publicada de R$ 150–250 por visita.",
    )
    recovery_pct = st.sidebar.slider(
        "Recuperação assumida após limpeza (%)", min_value=0, max_value=100, value=100, step=5,
        help="É uma hipótese de cenário. A recuperação real depende do tipo de sujeira e do procedimento de limpeza.",
    )
    st.sidebar.caption("Simulação editável, não orçamento nem recomendação automática de limpeza.")

    loss_pct = daylight["soiling_loss_fraction"] * 100
    first, second, third, fourth, fifth = st.columns(5)
    first.metric("Registros diurnos válidos", f"{len(daylight):,}".replace(",", "."))
    second.metric("Perda mediana", f"{loss_pct.median():.1f}%")
    third.metric("Perda máxima", f"{loss_pct.max():.1f}%")
    fourth.metric("Dias acima do limite", f"{int((daily['median_loss_fraction'] * 100 >= threshold_pct).sum())}")
    fifth.metric("Chuva acumulada", f"{daily['precipitation_mm'].sum():.1f} mm")

    st.subheader("Referência observada da base de validação")
    loss_chart = daily.set_index("date")[["median_loss_fraction"]].mul(100).rename(
        columns={"median_loss_fraction": "Perda mediana (%)"}
    )
    st.line_chart(loss_chart, height=300)
    st.caption(
        "Perda = (potência do painel limpo − potência do painel exposto) / potência do painel limpo. "
        "Valores negativos pontuais podem ocorrer por ruído ou condições experimentais."
    )

    st.subheader("Potência média diária no experimento de validação")
    power_chart = daily.set_index("date")[["mean_clean_power_w", "mean_dusty_power_w"]].rename(
        columns={"mean_clean_power_w": "Limpo (W)", "mean_dusty_power_w": "Exposto à poeira (W)"}
    )
    st.line_chart(power_chart, height=300)

    st.subheader("Cenário de economia potencial")
    observed_lost_energy_kwh = max(float(daily["lost_energy_kwh"].sum()), 0.0)
    potential_recovery_brl = observed_lost_energy_kwh * tariff_brl_kwh * (recovery_pct / 100)
    balance_brl = potential_recovery_brl - cleaning_cost_brl
    economy_left, economy_middle, economy_right, economy_fourth = st.columns(4)
    economy_left.metric("Energia não gerada observada", f"{observed_lost_energy_kwh:.2f} kWh")
    economy_middle.metric("Valor potencial recuperável", f"R$ {potential_recovery_brl:.2f}")
    economy_right.metric("Custo de limpeza assumido", f"R$ {cleaning_cost_brl:.2f}")
    economy_fourth.metric("Saldo do cenário", f"R$ {balance_brl:.2f}")
    st.caption(
        "Cálculo no período selecionado: energia não gerada observada × valor da energia × recuperação assumida, menos o custo de limpeza. "
        "É uma simulação de referência baseada no experimento, não uma economia efetivamente alcançada em residência real."
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Poeira acumulada")
        dust_chart = daily.set_index("date")[["median_dust_density_gm2"]].rename(
            columns={"median_dust_density_gm2": "Densidade de poeira (g/m²)"}
        )
        st.line_chart(dust_chart, height=250)
    with right:
        st.subheader("Dias acima do limite visual")
        above = daily[daily["median_loss_fraction"] * 100 >= threshold_pct].copy()
        if above.empty:
            st.success("Nenhum dia no período supera o limite selecionado.")
        else:
            st.dataframe(
                above.assign(
                    **{
                        "Perda mediana (%)": (above["median_loss_fraction"] * 100).round(2),
                        "Poeira (g/m²)": above["median_dust_density_gm2"].round(2),
                    }
                )[["date", "Perda mediana (%)", "Poeira (g/m²)", "valid_records"]],
                use_container_width=True,
                hide_index=True,
            )

    with st.expander("Como interpretar e quais são os limites"):
        st.markdown(
            "- O painel limpo foi lavado diariamente no experimento de origem; ele é a referência de treinamento e validação, não um requisito da implantação.\n"
            "- Na implantação, o monitor usa potência medida e variáveis ambientais para estimar a perda em relação à potência limpa esperada.\n"
            "- A densidade de poeira medida diretamente possui 48 observações; a série horária reconstruída foi fornecida pelos autores com interpolação PCHIP.\n"
            "- O limite exibido é exploratório e serve para priorizar investigação, não para recomendar ou otimizar a limpeza.\n"
            "- O cenário econômico usa valores residenciais editáveis e uma recuperação assumida; ele não substitui orçamento, tarifa real ou validação em campo.\n"
            "- A chuva é apresentada como contexto. Não se presume que uma quantidade fixa de chuva restaure completamente a produção.\n"
            "- Esta base representa um local e seis meses de experimento; ela não prova desempenho idêntico em outra instalação."
        )


if __name__ == "__main__":
    main()
