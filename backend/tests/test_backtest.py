import numpy as np
import pandas as pd
from app.ml.backtest import make_features, chronological_folds, score


def test_lags_do_not_include_same_day_sales():
    df = pd.DataFrame({"product_id": [1] * 15, "date": pd.date_range("2026-01-01", periods=15),
                       "units_sold": list(range(15))})
    prepared = make_features(df)
    assert prepared.iloc[0]["lag_1"] == 6
    assert prepared.iloc[0]["lag_7"] == 0
    assert prepared.iloc[0]["rolling_7"] == 3


def test_folds_do_not_overlap():
    df = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=300), "units_sold": np.ones(300)})
    folds = list(chronological_folds(df, folds=3, horizon_days=20))
    assert len(folds) == 3
    assert all(train.date.max() < test.date.min() for train, test in folds)
    assert folds[0][1].date.max() < folds[1][1].date.min()


def test_score_zero_demand():
    result = score([0, 0], [0, -3])
    assert result["MAE"] == 0
