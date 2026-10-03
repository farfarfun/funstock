from unittest.mock import MagicMock

import pytest

from funstock.dataset.databasestock import DatabaseStock, connect_from_environment


def _make_connection():
    """构造一个可用 `with ... as cursor` 的假 MySQL 连接。"""
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = False
    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


def test_stock_min_create_uses_stock_min_table():
    """stock_min_create 曾错误地建 stock_daily 表，回归测试确保建的是 stock_min。"""
    connection, cursor = _make_connection()
    db = DatabaseStock(connection=connection, pro=MagicMock())

    db.stock_min_create()

    executed_sql = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS stock_min" in executed_sql
    assert "stock_daily" not in executed_sql
    connection.commit.assert_called_once()


def test_stock_min_updated_one_writes_to_stock_min_table():
    """stock_min_updated_one 曾错误地写入 stock_daily 表，回归测试确保写入 stock_min。"""
    connection, cursor = _make_connection()
    pro = MagicMock()
    db = DatabaseStock(connection=connection, pro=pro)

    import pandas as pd

    frame = pd.DataFrame([{
        "ts_code": "000001.SZ", "trade_time": "20240101093000", "open": 10,
        "high": 11, "low": 9, "close": 10.5, "vol": 100, "amount": 1000,
        "trade_date": "20240101", "pre_close": 10,
    }])

    import funstock.dataset.databasestock as mod
    original_pro_bar = mod.ts.pro_bar
    mod.ts.pro_bar = MagicMock(return_value=frame)
    try:
        total = db.stock_min_updated_one("000001.SZ", "20240101", "20240101", freq="5min")
    finally:
        mod.ts.pro_bar = original_pro_bar

    assert total == 1
    executed_sql = cursor.execute.call_args[0][0]
    assert executed_sql.startswith("REPLACE INTO stock_min")


def test_stock_daily_updated_one_returns_zero_on_empty_response():
    """Tushare 返回空数据时应返回 0，而不是抛异常。"""
    connection, _cursor = _make_connection()
    db = DatabaseStock(connection=connection, pro=MagicMock())

    import funstock.dataset.databasestock as mod
    original_pro_bar = mod.ts.pro_bar
    mod.ts.pro_bar = MagicMock(return_value=None)
    try:
        total = db.stock_daily_updated_one("000001.SZ", "20240101", "20240101")
    finally:
        mod.ts.pro_bar = original_pro_bar

    assert total == 0


def test_connect_from_environment_requires_token(monkeypatch):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="TUSHARE_TOKEN"):
        connect_from_environment()


def test_connect_from_environment_requires_mysql_password(monkeypatch):
    monkeypatch.setenv("TUSHARE_TOKEN", "test-token")
    monkeypatch.delenv("STOCK_MYSQL_PASSWORD", raising=False)
    monkeypatch.setattr("funstock.dataset.databasestock.ts.set_token", MagicMock())
    with pytest.raises(RuntimeError, match="STOCK_MYSQL_PASSWORD"):
        connect_from_environment()
