"""Modelos candidatos e métricas de regressão."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "irradiance_wm2",
    "module_temperature_c",
    "irradiance_temperature_interaction",
]
TARGET_COLUMN = "power_kw"
CLEAN_REFERENCE_TARGET_COLUMN = "clean_reference_power_kw"


def build_candidates(random_state: int = 42) -> dict[str, Any]:
    """Return the baseline Ridge and a non-linear Random Forest candidate."""
    return {
        "ridge": Pipeline(
            [
                ("scale", StandardScaler()),
                ("model", Ridge(alpha=1.0)),
            ]
        ),
        "random_forest": RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=5,
            random_state=random_state,
            n_jobs=-1,
        ),
    }


def regression_metrics(observed: pd.Series, predicted: Any) -> dict[str, float]:
    """Calculate metrics with a consistent, serializable representation."""
    return {
        "mae_kw": float(mean_absolute_error(observed, predicted)),
        "rmse_kw": float(mean_squared_error(observed, predicted) ** 0.5),
        "r2": float(r2_score(observed, predicted)),
    }


def loss_metrics(observed: pd.Series, predicted: Any) -> dict[str, float]:
    """Calculate metrics for estimated soiling-loss fractions."""
    return {
        "mae_fraction": float(mean_absolute_error(observed, predicted)),
        "rmse_fraction": float(mean_squared_error(observed, predicted) ** 0.5),
        "r2": float(r2_score(observed, predicted)),
    }
