"""Local dashboard for the published clean-versus-dusty PV experiment."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
REAL_DATA = ROOT / "data" / "processed" / "laghouat_2022.csv"


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """Read the locally prepared version of the published dataset."""
    frame = pd.read_csv(path, parse_dates=["timestamp"])
    frame["date"] = frame["timestamp"].dt.date
    return frame


def main() -> None:
    st.set_page_config(page_title="Sujidade fotovoltaica", page_icon="☀️", layout="wide")
    st.title("Análise de sujidade fotovoltaica")
    st.caption(
        "Dados reais de experimento com um painel limpo diariamente e outro exposto ao acúmulo natural de poeira."
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
            median_dust_density_gm2=("dust_density_reconstructed_gm2", "median"),
            valid_records=("soiling_loss_fraction", "size"),
        )
    )

    st.sidebar.markdown("### Explorar um limite")
    threshold_pct = st.sidebar.slider("Perda diária de referência (%)", 0.0, 30.0, 10.0, 0.5)
    st.sidebar.caption("É um filtro visual configurável; não é ainda uma recomendação econômica de limpeza.")

    loss_pct = daylight["soiling_loss_fraction"] * 100
    first, second, third, fourth = st.columns(4)
    first.metric("Registros diurnos válidos", f"{len(daylight):,}".replace(",", "."))
    second.metric("Perda mediana", f"{loss_pct.median():.1f}%")
    third.metric("Perda máxima", f"{loss_pct.max():.1f}%")
    fourth.metric("Dias acima do limite", f"{int((daily['median_loss_fraction'] * 100 >= threshold_pct).sum())}")

    st.subheader("Perda diária observada")
    loss_chart = daily.set_index("date")[["median_loss_fraction"]].mul(100).rename(
        columns={"median_loss_fraction": "Perda mediana (%)"}
    )
    st.line_chart(loss_chart, height=300)
    st.caption(
        "Perda = (potência do painel limpo − potência do painel exposto) / potência do painel limpo. "
        "Valores negativos pontuais podem ocorrer por ruído ou condições experimentais."
    )

    st.subheader("Potência média diária: painel limpo × painel exposto")
    power_chart = daily.set_index("date")[["mean_clean_power_w", "mean_dusty_power_w"]].rename(
        columns={"mean_clean_power_w": "Limpo (W)", "mean_dusty_power_w": "Exposto à poeira (W)"}
    )
    st.line_chart(power_chart, height=300)

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
            "- O painel limpo foi lavado diariamente no experimento de origem; ele funciona como referência.\n"
            "- A densidade de poeira medida diretamente possui 48 observações; a série horária reconstruída foi fornecida pelos autores com interpolação PCHIP.\n"
            "- O limite exibido é exploratório. A recomendação real de limpeza deve considerar custo de limpeza, tarifa/valor da energia, previsão de chuva e persistência da perda.\n"
            "- Esta base representa um local e seis meses de experimento; ela não prova desempenho idêntico em outra instalação."
        )


if __name__ == "__main__":
    main()
