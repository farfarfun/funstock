import pytest

from funstock.echarts import calculate_ma, split_data


def test_split_data_and_moving_average():
    data = [["20240101", 1, 2, 0, 1.5, 10], ["20240102", 2, 1, 0, 2.5, 11]]
    split = split_data(data)
    assert split["categoryData"] == ["20240101", "20240102"]
    assert calculate_ma(2, split) == ["-", 1.5]


def test_moving_average_rejects_empty_window():
    with pytest.raises(ValueError, match="day_count"):
        calculate_ma(0, {"values": []})
