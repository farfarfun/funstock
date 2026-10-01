import os
import sqlite3
from os import PathLike
from typing import Any

from funtable.kv.sqlite_table import SQLiteTableBase


class SqliteTable(SQLiteTableBase):
    """为现有行情表提供 funtable SQLite 基类的列式兼容操作。"""

    def __init__(self, db_path: str, table_name: str, *args: Any, **kwargs: Any) -> None:
        del args, kwargs
        super().__init__(db_path)
        self.table_name = table_name
        self.columns: list[str] = []

    @property
    def conn(self) -> sqlite3.Connection:
        """返回当前线程的 SQLite 连接。"""
        return self.connection

    def execute(self, sql: str) -> sqlite3.Cursor:
        """执行建表或其他 SQL。"""
        return self._execute(sql)

    def insert_list(self, rows: list[dict[str, Any]]) -> None:
        """批量插入行情记录。"""
        if not rows:
            return
        columns = [column for column in self.columns if column in rows[0]]
        placeholders = ", ".join("?" for _ in columns)
        sql = f"INSERT OR REPLACE INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        self._executemany(sql, [tuple(row.get(column) for column in columns) for row in rows])

    def vacuum(self) -> None:
        """整理 SQLite 数据库。"""
        self._execute("VACUUM")


class StockBasic(SqliteTable):
    """存储股票基本信息的 SQLite 表。"""

    def __init__(self, table_name: str = 'stock_basic', db_path: str | PathLike[str] | None = None,
                 *args: Any, **kwargs: Any) -> None:
        """初始化表；参数为表名、数据库路径及基类扩展参数，无返回值。"""
        if db_path is None:
            db_path = os.path.abspath(
                os.path.dirname(__file__)) + '/data/stock.db'

        super(StockBasic, self).__init__(db_path=db_path,
                                         table_name=table_name, *args, **kwargs)
        self.columns = ['ts_code', 'symbol', 'name', 'area', 'industry', 'fullname', 'enname', 'market', 'exchange',
                        'curr_type', 'list_status', 'list_date', 'delist_date', 'is_hs'
                        ]

    def create(self) -> None:
        """创建股票基本信息表，无参数和返回值。"""
        self.execute("""
                create table if not exists {} (
                 ts_code       VARCHAR(255)
                ,symbol        VARCHAR(255)
                ,name          VARCHAR(255)
                ,area          VARCHAR(255)
                ,industry      VARCHAR(255)
                ,fullname      VARCHAR(255)
                ,enname        VARCHAR(255)
                ,market        VARCHAR(255)
                ,exchange      VARCHAR(255)
                ,curr_type     VARCHAR(255)
                ,list_status   VARCHAR(255)
                ,list_date     VARCHAR(255)
                ,delist_date   VARCHAR(255)
                ,is_hs         VARCHAR(255)
                ,PRIMARY KEY (ts_code)
                )
                """.format(self.table_name))


class QuotationDay(SqliteTable):
    """存储股票日线行情的 SQLite 表。"""

    def __init__(self, table_name: str = 'quotation_day', db_path: str | PathLike[str] | None = None,
                 *args: Any, **kwargs: Any) -> None:
        """初始化表；参数为表名、数据库路径及基类扩展参数，无返回值。"""
        if db_path is None:
            db_path = os.path.abspath(
                os.path.dirname(__file__)) + '/data/stock.db'

        super(QuotationDay, self).__init__(
            db_path=db_path, table_name=table_name, *args, **kwargs)
        self.columns = ['ts_code', 'date', 'time', 'open', 'high',
                        'low', 'close', 'volume', 'amount', 'pre_close']

    def create(self) -> None:
        """创建日线行情表，无参数和返回值。"""
        self.execute("""
            create table if not exists {} (
               ts_code       VARCHAR(255)
              ,date          VARCHAR(255)
              ,time          VARCHAR(255)
              ,open          FLOAT
              ,high          FLOAT
              ,low           FLOAT
              ,close         FLOAT
              ,volume        FLOAT
              ,amount        FLOAT
              ,pre_close     FLOAT   
              ,primary key (ts_code,time)           
              )
            """.format(self.table_name))


class QuotationMin(SqliteTable):
    """存储股票分钟行情的 SQLite 表。"""

    def __init__(self, table_name: str = 'quotation_min', db_path: str | PathLike[str] | None = None,
                 *args: Any, **kwargs: Any) -> None:
        """初始化并创建表；参数为表名、数据库路径及基类扩展参数，无返回值。"""
        if db_path is None:
            db_path = os.path.abspath(
                os.path.dirname(__file__)) + '/data/stock.db'

        super(QuotationMin, self).__init__(
            db_path=db_path, table_name=table_name, *args, **kwargs)
        self.columns = ['ts_code', 'date', 'time', 'open',
                        'high', 'low', 'close', 'volume', 'amount']
        self.create()

    def create(self) -> None:
        """创建分钟行情表，无参数和返回值。"""
        self.execute("""
            create table if not exists {} (
               ts_code       VARCHAR(255)
              ,date          VARCHAR(255)
              ,time          VARCHAR(255)
              ,open          FLOAT
              ,high          FLOAT
              ,low           FLOAT
              ,close         FLOAT
              ,volume        FLOAT
              ,amount        FLOAT                 
              ,primary key (ts_code,time)           
              )
            """.format(self.table_name))


class QuotationMin1(QuotationMin):
    """存储一分钟行情的 SQLite 表。"""

    def __init__(self, table_name: str = 'quotation_min1', *args: Any, **kwargs: Any) -> None:
        """初始化一分钟行情表；参数为表名及基类扩展参数，无返回值。"""
        super(QuotationMin1, self).__init__(
            table_name=table_name, *args, **kwargs)


class QuotationMin5(QuotationMin):
    """存储五分钟行情的 SQLite 表。"""

    def __init__(self, table_name: str = 'quotation_min5', *args: Any, **kwargs: Any) -> None:
        """初始化五分钟行情表；参数为表名及基类扩展参数，无返回值。"""
        super(QuotationMin5, self).__init__(
            table_name=table_name, *args, **kwargs)


class QuotationMin15(QuotationMin):
    """存储十五分钟行情的 SQLite 表。"""

    def __init__(self, table_name: str = 'quotation_min15', *args: Any, **kwargs: Any) -> None:
        """初始化十五分钟行情表；参数为表名及基类扩展参数，无返回值。"""
        super(QuotationMin15, self).__init__(
            table_name=table_name, *args, **kwargs)


class QuotationMin30(QuotationMin):
    """存储三十分钟行情的 SQLite 表。"""

    def __init__(self, table_name: str = 'quotation_min30', *args: Any, **kwargs: Any) -> None:
        """初始化三十分钟行情表；参数为表名及基类扩展参数，无返回值。"""
        super(QuotationMin30, self).__init__(
            table_name=table_name, *args, **kwargs)


class QuotationMin60(QuotationMin):
    """存储六十分钟行情的 SQLite 表。"""

    def __init__(self, table_name: str = 'quotation_min60', *args: Any, **kwargs: Any) -> None:
        """初始化六十分钟行情表；参数为表名及基类扩展参数，无返回值。"""
        super(QuotationMin60, self).__init__(
            table_name=table_name, *args, **kwargs)


class TradeDetail(SqliteTable):
    """存储逐笔成交明细的 SQLite 表。"""

    def __init__(self, table_name: str = 'trade_detail', db_path: str | PathLike[str] | None = None,
                 *args: Any, **kwargs: Any) -> None:
        """初始化表；参数为表名、数据库路径及基类扩展参数，无返回值。"""
        if db_path is None:
            db_path = os.path.abspath(
                os.path.dirname(__file__)) + '/data/stock.db'

        super(TradeDetail, self).__init__(db_path=db_path,
                                          table_name=table_name, *args, **kwargs)
        self.columns = ['ts_code', 'trade_date', 'trade_time',
                        'price', 'price_mod', 'vol', 'amount']

    def create(self) -> None:
        """创建逐笔成交明细表，无参数和返回值。"""
        self.execute("""
            create table if not exists {} (
               ts_code       VARCHAR(255)
              ,trade_date    VARCHAR(255)
              ,trade_time    VARCHAR(255)
              
              ,price         FLOAT
              ,price_mod     FLOAT
              ,vol           FLOAT
              ,amount        FLOAT
              ,primary key (ts_code,trade_time)           
              )
            """.format(self.table_name))
