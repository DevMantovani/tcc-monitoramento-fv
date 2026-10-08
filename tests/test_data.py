from __future__ import annotations

import pandas as pd
import pytest

from pv_monitor.data import (
    load_observations,
    prepare_laghouat_dataset,
    prepare_zenodo_inverter_dataset,
    split_temporally,
)
from pv_monitor.workflow import _alert_metrics, _persistent_alerts


def test_load_observations_filters_invalid_rows(tmp_path):
    timestamps = pd.date_range("2026-01-01", periods=40, freq="h", tz="UTC")
    frame = pd.DataFrame(
        {
            "timestamp": list(timestamps.astype(str)) + ["invalid"],
            "irradiance_wm2": [300.0] * 40 + [400.0],
            "temperature_c": [25.0] * 41,
            "power_kw": [2.0] * 40 + [2.0],
        }
    )
    path = tmp_path / "input.csv"
    frame.to_csv(path, index=False)

    cleaned = load_observations(str(path))

    assert len(cleaned) == 40
    assert cleaned["timestamp"].is_monotonic_increasing
    assert "irradiance_temperature_interaction" in cleaned


def test_split_temporally_preserves_time_order():
    frame = pd.DataFrame({"timestamp": pd.date_range("2026-01-01", periods=100, freq="h", tz="UTC")})
    split = split_temporally(frame)

    assert len(split.train) == 60
    assert len(split.validation) == 20
    assert len(split.test) == 20
    assert split.train["timestamp"].max() < split.validation["timestamp"].min()
    assert split.validation["timestamp"].max() < split.test["timestamp"].min()


def test_load_observations_requires_columns(tmp_path):
    path = tmp_path / "invalid.csv"
    pd.DataFrame({"timestamp": ["2026-01-01"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="colunas obrigatórias"):
        load_observations(str(path))


def test_prepare_laghouat_calculates_loss_only_with_clean_reference(tmp_path):
    raw = pd.DataFrame(
        {
            "datetime": ["17/02/2022 10:00", "17/02/2022 11:00"],
            "dust_density_measured_gm2": [1.0, None],
            "dust_density_reconstructed_PCHIP_gm2": [1.0, 1.1],
            "temp_amb_C": [20.0, 21.0],
            "T_cell_C": [30.0, 31.0],
            "G_POA_Wm2": [500.0, 0.0],
            "RH_pct": [40.0, 41.0],
            "wind_speed_ms": [2.0, 2.1],
            "cloud_cover_pct": [10.0, 11.0],
            "precipitation_mm": [0.0, 0.0],
            "P_clean_W": [80.0, 0.0],
            "P_dusty_W": [72.0, 0.0],
        }
    )
    input_path = tmp_path / "raw.csv"
    output_path = tmp_path / "prepared.csv"
    raw.to_csv(input_path, index=False)

    prepared = prepare_laghouat_dataset(str(input_path), str(output_path))

    assert prepared.loc[0, "soiling_loss_fraction"] == pytest.approx(0.10)
    assert pd.isna(prepared.loc[1, "soiling_loss_fraction"])
    assert prepared.loc[0, "power_kw"] == pytest.approx(0.072)
    assert prepared.loc[0, "clean_reference_power_kw"] == pytest.approx(0.080)
    assert prepared.loc[0, "temperature_c"] == pytest.approx(30.0)


def test_prepare_zenodo_inverter_keeps_measured_power_not_source_prediction(tmp_path):
    raw = pd.DataFrame(
        {
            "datetime": ["2024-01-01 10:00", "2024-01-01 11:00", "2024-01-01 10:00"],
            "id": ["inverter1", "inverter1", "inverter2"],
            "inverter": [1200.0, 1400.0, 9999.0],
            "temperature_2m (°C)": [20.0, 21.0, 22.0],
            "global_tilted_irradiance (W/m²)": [500.0, 600.0, 700.0],
            "panel_size": [107.1, 107.1, 95.2],
            "energy": [100.0, 100.0, 100.0],
        }
    )
    input_path = tmp_path / "raw.csv"
    output_path = tmp_path / "prepared.csv"
    raw.to_csv(input_path, index=False)

    prepared = prepare_zenodo_inverter_dataset(str(input_path), str(output_path), "inverter1")

    assert len(prepared) == 2
    assert prepared["power_kw"].tolist() == pytest.approx([1.2, 1.4])
    assert prepared["temperature_c"].tolist() == pytest.approx([20.0, 21.0])
    assert "energy" not in prepared.columns


def test_persistent_alerts_and_metrics_require_consecutive_days():
    observed = pd.Series([0.12, 0.12, 0.02, 0.12, 0.12])
    estimated = pd.Series([0.11, 0.11, 0.02, 0.04, 0.11])

    assert _persistent_alerts(observed, threshold=0.10, persistence_days=2) == [False, True, False, False, True]
    score = _alert_metrics(observed, estimated, threshold=0.10, persistence_days=2)

    assert score["true_positive_days"] == 1
    assert score["false_positive_days"] == 0
    assert score["false_negative_days"] == 1
