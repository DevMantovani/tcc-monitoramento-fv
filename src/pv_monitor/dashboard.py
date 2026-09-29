"""Local Streamlit dashboard for inspecting pipeline outputs."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from pv_monitor.data import load_observations
from pv_monitor.models import FEATURE_COLUMNS

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data" / "processed" / "demo_sintetico.csv"
DEFAULT_ARTIFACTS = ROOT / "artifacts" / "demo"


@st.cache_data(show_spinner=False)
def load_dashboard_data(data_path: str, model_path: str) -> pd.DataFrame:
    """Load observations and calculate predicted power for visualization."""
    frame = load_observations(data_path)
    model = joblib.load(model_path)
    frame["predicted_power_kw"] = model.predict(frame[FEATURE_COLUMNS])
    frame["loss_fraction"] = (
        (frame["predicted_power_kw"] - frame["power_kw"])
        / frame["predicted_power_kw"].clip(lower=0.10)
    )
    return frame


def load_metrics(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    st.set_page_config(page_title="Monitoramento Fotovoltaico", page_icon="☀️", layout="wide")
    st.title("Monitoramento fotovoltaico por dados")
    st.caption("Painel local de análise — o alerta indica perda adicional persistente, não a causa da perda.")

    metrics_path = DEFAULT_ARTIFACTS / "metrics_validation.json"
    alert_path = DEFAULT_ARTIFACTS / "alertas.csv"
    model_options = {
        "Ridge (referência linear)": DEFAULT_ARTIFACTS / "ridge.joblib",
        "Random Forest": DEFAULT_ARTIFACTS / "random_forest.joblib",
    }

    missing = [path for path in [DEFAULT_DATA, metrics_path, alert_path, *model_options.values()] if not path.exists()]
    if missing:
        st.warning("Ainda não há resultados locais para exibir. Execute primeiro o cenário demonstrativo descrito no README.")
        st.code(
            "pv-monitor demo --output data/processed/demo_sintetico.csv\n"
            "pv-monitor train --input data/processed/demo_sintetico.csv --output artifacts/demo\n"
            "pv-monitor detect --input data/processed/demo_sintetico.csv --model artifacts/demo/random_forest.joblib --output artifacts/demo/alertas.csv"
        )
        return

    choice = st.sidebar.radio("Modelo visualizado", list(model_options))
    observations = load_dashboard_data(str(DEFAULT_DATA), str(model_options[choice]))
    metrics = load_metrics(metrics_path)["validation_metrics"]
    alerts = pd.read_csv(alert_path)

    st.subheader("Qualidade dos modelos na validação")
    metric_columns = st.columns(2)
    for column, (model_name, values) in zip(metric_columns, metrics.items()):
        with column:
            st.markdown(f"#### {model_name.replace('_', ' ').title()}")
            one, two, three = st.columns(3)
            one.metric("MAE", f"{values['mae_kw']:.3f} kW")
            two.metric("RMSE", f"{values['rmse_kw']:.3f} kW")
            three.metric("R²", f"{values['r2']:.3f}")

    st.subheader("Potência observada × potência prevista")
    plot_frame = observations.set_index("timestamp")[["power_kw", "predicted_power_kw"]].rename(
        columns={"power_kw": "Observada (kW)", "predicted_power_kw": "Prevista (kW)"}
    )
    st.line_chart(plot_frame, height=340)

    st.subheader("Perda adicional diária")
    alert_plot = alerts.set_index("date")[["mean_loss_fraction"]].rename(
        columns={"mean_loss_fraction": "Fração média de perda"}
    )
    st.line_chart(alert_plot, height=250)

    active_alerts = alerts[alerts["additional_loss_alert"]].copy()
    st.subheader("Alertas ativos")
    if active_alerts.empty:
        st.success("Nenhum alerta ativo com a configuração atual.")
    else:
        st.warning(f"{len(active_alerts)} dia(s) com alerta de perda adicional persistente.")
        st.dataframe(active_alerts, use_container_width=True, hide_index=True)

    with st.expander("Limitações da demonstração"):
        st.write(
            "Os dados deste painel são sintéticos e incluem uma perda artificial controlada. "
            "Eles validam o funcionamento do software, não a detecção de sujidade em campo."
        )


if __name__ == "__main__":
    main()
