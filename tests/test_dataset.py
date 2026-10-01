import sqlite3

from funstock.dataset import QuotationDay, StockBasic


def test_stock_basic_creates_and_writes_rows(tmp_path):
    db_path = tmp_path / "stock.db"
    table = StockBasic(db_path=db_path)
    table.create()
    table.insert_list([{"ts_code": "000001.SZ", "symbol": "000001", "name": "平安银行"}])

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT ts_code, symbol, name FROM stock_basic"
        ).fetchone()
    assert row == ("000001.SZ", "000001", "平安银行")


def test_insert_list_accepts_empty_rows(tmp_path):
    table = QuotationDay(db_path=tmp_path / "stock.db")
    table.create()
    assert table.insert_list([]) is None
