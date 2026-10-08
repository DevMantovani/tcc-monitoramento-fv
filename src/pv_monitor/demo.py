"""Synthetic data used only for an integration test of the pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd


def create_demo_dataset(output_path: str, days: int = 90, seed: int = 42) -> pd.DataFrame:
    """Create controlled hourly records with a known artificial loss at the end."""
    if days < 30:
        raise ValueError("O conjunto demonstrativo precisa ter ao menos 30 dias.")
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2026-01-01", periods=days * 12, freq="h", tz="UTC")
    daylight = timestamps.hour.to_numpy()
    irradiance = np.maximum(0, 950 * np.sin(np.pi * (daylight - 6) / 12))
    irradiance = np.maximum(0, irradiance + rng.normal(0, 35, len(timestamps)))
    module_temperature = 18 + 0.018 * irradiance + rng.normal(0, 2, len(timestamps))
    expected_kw = 5.2 * (irradiance / 1000) * (1 - 0.0035 * (module_temperature - 25))
    power_kw = np.maximum(0, expected_kw + rng.normal(0, 0.08, len(timestamps)))

    # Controlled scenario: five final days have a 20% loss. This is not real soiling data.
    loss_start = timestamps.max() - pd.Timedelta(days=5)
    power_kw = np.where(timestamps >= loss_start, power_kw * 0.80, power_kw)
    frame = pd.DataFrame(
        {
            "timestamp": timestamps.astype(str),
            "irradiance_wm2": irradiance,
            "temperature_c": module_temperature,
            "power_kw": power_kw,
        }
    )
    frame.to_csv(output_path, index=False)
    return frame
