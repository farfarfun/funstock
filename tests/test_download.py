from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from funstock.dataset.download import StockDownload, StockDownloadError


@pytest.fixture
def downloader(monkeypatch, tmp_path):
    monkeypatch.setenv("TUSHARE_TOKEN", "test-token")
    monkeypatch.setattr("funstock.dataset.download.ts.set_token", Mock())
    monkeypatch.setattr("funstock.dataset.download.ts.pro_api", Mock(return_value=Mock()))
    monkeypatch.setattr(
        "funstock.dataset.download.bs.login",
        Mock(return_value=SimpleNamespace(error_code="0", error_msg="success")),
    )
    return StockDownload(db_path=tmp_path / "stock.db")


def test_download_requires_tushare_token(monkeypatch, tmp_path):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="TUSHARE_TOKEN"):
        StockDownload(db_path=tmp_path / "stock.db")


def test_tushare_download_writes_normal_response(monkeypatch, downloader):
    frame = pd.DataFrame([{
        "ts_code": "000001.SZ", "trade_date": "20240101", "open": 10,
        "high": 11, "low": 9, "close": 10.5, "vol": 100, "amount": 1000,
        "pre_close": 10,
    }])
    monkeypatch.setattr("funstock.dataset.download.ts.pro_bar", Mock(return_value=frame))
    monkeypatch.setattr("funstock.dataset.download.time.sleep", Mock())

    downloader._insert_day_tushare("000001.SZ", "20240101", "20240101")

    row = downloader.quotation_day.conn.execute(
        "SELECT date, time, volume FROM quotation_day WHERE ts_code = ?",
        ("000001.SZ",),
    ).fetchone()
    assert tuple(row) == ("20240101", "20240101", 100.0)


def test_baostock_download_writes_normal_response(monkeypatch, downloader):
    fields = ["date", "time", "code", "open", "high", "low", "close", "volume", "amount"]
    response = SimpleNamespace(
        error_code="0",
        error_msg="success",
        fields=fields,
        get_data=Mock(return_value=[["2024-01-01", "20240101100000", "sz.000001", 10, 11, 9, 10.5, 100, 1000]]),
    )
    monkeypatch.setattr(
        "funstock.dataset.download.bs.query_history_k_data_plus", Mock(return_value=response)
    )

    downloader._insert_min_bao_stock(
        "000001.SZ", "2024-01-01", "2024-01-01", frequency="5"
    )

    row = downloader.quotation_min5.conn.execute(
        "SELECT date, time, volume FROM quotation_min5 WHERE ts_code = ?",
        ("000001.SZ",),
    ).fetchone()
    assert tuple(row) == ("2024-01-01", "20240101100000", 100.0)


def test_tushare_empty_response_exhausts_retries(monkeypatch, downloader):
    request = Mock(return_value=None)
    monkeypatch.setattr("funstock.dataset.download.ts.pro_bar", request)
    monkeypatch.setattr("funstock.dataset.download.time.sleep", Mock())

    with pytest.raises(StockDownloadError, match="日线下载失败"):
        downloader._insert_day_tushare("000001.SZ")
    assert request.call_count == 3


def test_baostock_error_exhausts_retries(monkeypatch, downloader):
    response = SimpleNamespace(
        error_code="100", error_msg="failed", fields=[], get_data=Mock(return_value=[])
    )
    request = Mock(return_value=response)
    monkeypatch.setattr("funstock.dataset.download.bs.query_history_k_data_plus", request)
    monkeypatch.setattr("funstock.dataset.download.time.sleep", Mock())

    with pytest.raises(StockDownloadError, match="分钟线下载失败"):
        downloader._insert_min_bao_stock("000001.SZ")
    assert request.call_count == 3


def test_baostock_rejects_unknown_frequency(downloader):
    with pytest.raises(ValueError, match="不支持的分钟频率"):
        downloader._insert_min_bao_stock("000001.SZ", frequency="2")


def test_save_year_uses_boundary_dates(downloader):
    downloader.insert_basic = Mock()
    downloader.insert_min_all_bao_stock = Mock()
    downloader.insert_day_all_tushare = Mock()

    downloader.save_year(2024)

    downloader.insert_min_all_bao_stock.assert_called_once_with(
        start_date="20240101", end_date="20241231"
    )
    downloader.insert_day_all_tushare.assert_called_once_with("20240101", "20241231")
