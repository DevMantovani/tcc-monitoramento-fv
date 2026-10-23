import json

import pandas as pd
import pytest
from joblib import dump
from sklearn.dummy import DummyRegressor

from pv_monitor.models import FEATURE_COLUMNS
from pv_monitor.workflow import (
    _daily_losses, _persistent_alerts, _consecutive_counts,
    detect_additional_loss, evaluate_post_cleaning_calibration,
)
from pv_monitor.monitoring_evidence import monthly_alert_stability_table
from pv_monitor.dashboard import test_power_series as power_series


def test_gap_missing_value_and_month_boundary():
    dates = pd.Series(['2026-01-30', '2026-01-31', '2026-02-01', '2026-02-03', '2026-02-04', '2026-02-05'])
    assert _persistent_alerts(pd.Series([.2] * 6), .15, 3, dates) == [False, False, True, False, False, True]
    assert _consecutive_counts(pd.Series([True, None, True]), dates[:3]) == [1, 0, 1]
    with pytest.raises(ValueError, match='únicas'):
        _consecutive_counts(pd.Series([True, True]), pd.Series(['2026-01-01'] * 2))


def test_monthly_report_keeps_persistence_across_months():
    daily = pd.DataFrame({'date': ['2026-01-30', '2026-01-31', '2026-02-01'],
                          'observed_loss_fraction': [.2] * 3, 'estimated_loss_fraction': [.2] * 3})
    report = monthly_alert_stability_table(daily, .15, 3).set_index('month')
    assert report.loc['2026-02', 'true_positive_days'] == 1


def test_dashboard_uses_predictions_without_clean_measurement():
    daily = pd.DataFrame({'date': ['2026-01-01'], 'expected_clean_power_kw': [2.0],
                          'measured_power_kw': [1.5], 'clean_reference_power_kw': [99.0]})
    actual = power_series(daily)
    assert actual['expected_clean_power_kw'].iloc[0] == 2.0
    assert 'clean_reference_power_kw' not in actual
    with pytest.raises(ValueError, match='antigos'):
        power_series(daily.drop(columns='expected_clean_power_kw'))


def test_operational_matches_experiment_with_outlier_and_calendar_gap(tmp_path):
    # Mean loss >15%, median loss <15% on day one; missing day four resets run.
    dates = ['2026-01-01', '2026-01-02', '2026-01-03', '2026-01-05', '2026-01-06', '2026-01-07']
    timestamps = [pd.Timestamp(f'{day} {8 + h:02d}:00:00', tz='UTC') for day in dates for h in range(6)]
    loss = [.01, .01, .01, .01, .9, .9] + [.25] * 30
    frame = pd.DataFrame({'timestamp': timestamps, 'irradiance_wm2': 500., 'temperature_c': 25.,
                          'power_kw': [2*(1-x) for x in loss], 'observed_soiling_loss_fraction': loss})
    frame['irradiance_temperature_interaction'] = 12500.
    source = tmp_path/'input.csv'
    frame.to_csv(source, index=False)
    model = DummyRegressor(strategy='constant', constant=2.).fit(frame[FEATURE_COLUMNS], [2.] * len(frame))
    dump(model, tmp_path/'model.joblib')
    actual = detect_additional_loss(str(source), str(tmp_path/'model.joblib'), str(tmp_path/'daily.csv'))
    experimental = _daily_losses(frame, [2.] * len(frame))
    expected = _persistent_alerts(experimental['estimated_loss_fraction'], .15, 3, experimental['date'])
    assert actual['additional_loss_alert'].tolist() == expected == [False, False, False, False, False, True]
    assert actual['median_loss_fraction'].tolist() == pytest.approx(experimental['estimated_loss_fraction'].tolist())
    summary = json.loads((tmp_path/'daily.summary.json').read_text())
    assert summary['alert_policy']['daily_aggregation'] == 'median'


def test_calibration_windows_use_same_future_and_no_future_targets_in_fit(tmp_path):
    times = pd.date_range('2026-01-01', periods=120, freq='h', tz='UTC')
    frame = pd.DataFrame({'timestamp': times, 'irradiance_wm2': [400 + i % 12 * 10 for i in range(120)],
                          'temperature_c': 25., 'power_kw': .8, 'clean_reference_power_kw': 1.,
                          'observed_soiling_loss_fraction': .2})
    source = tmp_path/'paired.csv'
    frame.to_csv(source, index=False)
    first = evaluate_post_cleaning_calibration(str(source), str(tmp_path/'first'), calibration_days=(1, 2))
    assert {r['future_observations'] for r in first['results']} == {72}
    assert len({r['evaluation_start'] for r in first['results']}) == 1
    frame.loc[48:, 'clean_reference_power_kw'] = 100.
    frame.to_csv(source, index=False)
    second = evaluate_post_cleaning_calibration(str(source), str(tmp_path/'second'), calibration_days=(1, 2))
    # Altering future clean targets changes power score, not predictions or loss alerts.
    assert [r['loss_mae_percentage_points'] for r in first['results']] == pytest.approx([r['loss_mae_percentage_points'] for r in second['results']])
    assert first['results'][0]['expected_power_mae_kw'] != second['results'][0]['expected_power_mae_kw']
