from __future__ import annotations

import pandas as pd
import pytest
from joblib import dump
from sklearn.dummy import DummyRegressor

from pv_monitor.data import (
    load_observations,
    operational_input_quality_report,
    prepare_laghouat_dataset,
    prepare_zenodo_inverter_dataset,
    split_temporally,
)
from pv_monitor.models import FEATURE_COLUMNS
from pv_monitor.launcher import (
    RAW_SOURCES,
    REQUIRED_RESULTS,
    dashboard_is_running,
    missing_raw_sources,
    results_are_ready,
)
from pv_monitor.reproduction import select_model_by_validation_metric
from pv_monitor.reporting import build_final_table, build_validation_table
from pv_monitor.workflow import _alert_metrics, _persistent_alerts, detect_additional_loss


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


def test_operational_input_quality_report_exposes_exclusions(tmp_path):
    path = tmp_path / "input.csv"
    pd.DataFrame(
        {
            "timestamp": ["2026-01-01 10:00", "2026-01-01 10:00", "invalid", "2026-01-01 11:00"],
            "irradiance_wm2": [300.0, 300.0, 400.0, 10.0],
            "module_temperature_c": [25.0, 25.0, 25.0, 25.0],
            "power_kw": [2.0, 2.0, 2.0, -1.0],
            "precipitation_mm": [0.0, 0.0, 0.0, 2.0],
        }
    ).to_csv(path, index=False)

    report = operational_input_quality_report(str(path), minimum_irradiance_wm2=50.0)

    assert report["temperature_input_column"] == "module_temperature_c"
    assert report["raw_rows"] == 4
    assert report["invalid_timestamp_rows"] == 1
    assert report["duplicate_timestamp_rows_after_validation"] == 1
    assert report["usable_rows"] == 1
    assert "precipitation_mm" in report["optional_context_columns_present"]


def test_detect_additional_loss_creates_auditable_persistent_alert(tmp_path):
    timestamps = pd.DatetimeIndex(
        [
            pd.Timestamp("2026-01-01", tz="UTC") + pd.Timedelta(day * 24 + hour, unit="h")
            for day in range(10)
            for hour in (8, 12, 16)
        ]
    )
    raw = pd.DataFrame(
        {
            "timestamp": timestamps.astype(str),
            "irradiance_wm2": [500.0] * len(timestamps),
            "temperature_c": [25.0] * len(timestamps),
            "power_kw": [1.5] * len(timestamps),
        }
    )
    input_path = tmp_path / "operational.csv"
    model_path = tmp_path / "model.joblib"
    output_path = tmp_path / "alerts.csv"
    raw.to_csv(input_path, index=False)
    features = pd.DataFrame(
        {
            "irradiance_wm2": [500.0],
            "temperature_c": [25.0],
            "irradiance_temperature_interaction": [12500.0],
        }
    )
    model = DummyRegressor(strategy="constant", constant=2.0).fit(features[FEATURE_COLUMNS], [2.0])
    dump(model, model_path)

    daily = detect_additional_loss(
        str(input_path),
        str(model_path),
        str(output_path),
        daily_loss_threshold=0.12,
        minimum_samples_per_day=2,
        persistence_days=2,
    )

    assert daily["additional_loss_alert"].tolist() == [False] + [True] * 9
    assert output_path.with_suffix(".summary.json").exists()
    assert "Inspecionar" in daily.loc[1, "recommended_action"]


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


def test_select_model_by_validation_metric_uses_smallest_error():
    metrics = {"ridge": {"mae_kw": 0.4}, "random_forest": {"mae_kw": 0.2}}

    assert select_model_by_validation_metric(metrics, "mae_kw") == "random_forest"

    with pytest.raises(ValueError, match="Métrica de validação ausente"):
        select_model_by_validation_metric(metrics, "r2")


def test_result_tables_keep_validation_and_final_metrics_separate():
    laghouat_validation = {
        "validation_metrics": {
            "ridge": {"estimated_soiling_loss": {"mae_fraction": 0.01, "rmse_fraction": 0.02, "r2": 0.9}}
        }
    }
    zenodo_validation = {"validation_metrics": {"ridge": {"mae_kw": 1.0, "rmse_kw": 2.0, "r2": 0.8}}}
    laghouat_final = {
        "test_metrics": {
            "estimated_soiling_loss": {"mae_fraction": 0.03, "rmse_fraction": 0.04, "r2": 0.7},
            "persistent_alert": {"precision": 0.8, "recall": 0.9, "f1": 0.85},
        }
    }
    zenodo_final = {"test_metrics": {"mae_kw": 3.0, "rmse_kw": 4.0, "r2": 0.6}}

    validation = build_validation_table(laghouat_validation, zenodo_validation)
    final = build_final_table(laghouat_final, zenodo_final)

    assert set(validation["partition"]) == {"validação"}
    assert "F1" in set(final["metric"])
    assert validation.loc[0, "value"] == pytest.approx(1.0)


def test_launcher_only_considers_the_project_ready_with_all_required_results(tmp_path):
    assert missing_raw_sources(tmp_path) == list(RAW_SOURCES)
    assert not results_are_ready(tmp_path)

    for relative in RAW_SOURCES + REQUIRED_RESULTS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    assert missing_raw_sources(tmp_path) == []
    assert results_are_ready(tmp_path)


def test_launcher_detects_the_local_dashboard_health_endpoint(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    monkeypatch.setattr("pv_monitor.launcher.urlopen", lambda *_args, **_kwargs: Response())

    assert dashboard_is_running()
