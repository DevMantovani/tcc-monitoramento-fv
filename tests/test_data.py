from __future__ import annotations

import pandas as pd
import pytest

from pv_monitor.data import load_observations, split_temporally


def test_load_observations_filters_invalid_rows(tmp_path):
    timestamps = pd.date_range("2026-01-01", periods=40, freq="h", tz="UTC")
    frame = pd.DataFrame(
        {
            "timestamp": list(timestamps.astype(str)) + ["invalid"],
            "irradiance_wm2": [300.0] * 40 + [400.0],
            "module_temperature_c": [25.0] * 41,
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
