from unittest.mock import Mock

import pandas as pd
import pytest

from funstock.echarts import DayChart, calculate_ma, split_data


def test_split_data_and_moving_average():
    data = [["20240101", 1, 2, 0, 1.5, 10], ["20240102", 2, 1, 0, 2.5, 11]]
    split = split_data(data)
    assert split["categoryData"] == ["20240101", "20240102"]
    assert calculate_ma(2, split) == ["-", 1.5]


def test_moving_average_rejects_empty_window():
    with pytest.raises(ValueError, match="day_count"):
        calculate_ma(0, {"values": []})


def test_day_chart_loads_default_data_and_draws(monkeypatch):
    pro_api = Mock(return_value=Mock())
    monkeypatch.setattr("funstock.echarts.day_chart.ts.pro_api", pro_api)
    response = Mock(json=Mock(return_value=[
        ["20240101", 1, 2, 0, 1.5, 10],
        ["20240102", 2, 3, 1, 2.5, 11],
    ]))
    request = Mock(return_value=response)
    monkeypatch.setattr("funstock.echarts.day_chart.requests.get", request)

    chart = DayChart()
    result = chart.get_chart()

    assert chart.chart_data["categoryData"] == ["20240101", "20240102"]
    assert request.call_count == 1
    assert result.options["series"]


def test_day_chart_loads_requested_stock_data(monkeypatch):
    pro = Mock()
    monkeypatch.setattr("funstock.echarts.day_chart.ts.pro_api", Mock(return_value=pro))
    frame = pd.DataFrame([
        {"trade_date": "20240102", "open": 2, "high": 3, "low": 1, "close": 2.5, "vol": 11},
        {"trade_date": "20240101", "open": 1, "high": 2, "low": 0, "close": 1.5, "vol": 10},
    ])
    pro_bar = Mock(return_value=frame)
    monkeypatch.setattr("funstock.echarts.day_chart.ts.pro_bar", pro_bar)

    chart = DayChart(token="test-token")
    result = chart.get_chart("000001.SZ")

    pro_bar.assert_called_once()
    assert chart.chart_data["categoryData"] == ["20240101", "20240102"]
    assert result.options["series"]
