#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/04/04 00:31
# @Author  : niuliangtao
# @Site    :
# @Software: PyCharm

import os
import time

import pymysql.cursors
import tushare as ts
from farlog import getLogger

logger = getLogger("funstock")


class DatabaseStock:
    """操作 MySQL 中的股票行情表。"""

    def __init__(self, connection: object, pro: object | None = None) -> None:
        """初始化连接和可选的 Tushare Pro 客户端。"""
        self.pro = pro or ts.pro_api()
        self.connect = connection

    def stock_basic_create(self):
        try:
            with self.connect.cursor() as cursor:
                sql = """CREATE TABLE IF NOT EXISTS stock_basic (
            ts_code       VARCHAR(255) COMMENT 'TS代码'
           ,symbol        VARCHAR(255) COMMENT '股票代码'
           ,name          VARCHAR(255) COMMENT '股票名称'
           ,area          VARCHAR(255) COMMENT '所在地域'
           ,industry      VARCHAR(255) COMMENT '所属行业'
           ,fullname      VARCHAR(255) COMMENT '股票全称'
           ,enname        VARCHAR(255) COMMENT '英文全称'
           ,market        VARCHAR(255) COMMENT '市场类型 （主板/中小板/创业板）'
           ,exchange      VARCHAR(255) COMMENT '交易所代码'
           ,curr_type     VARCHAR(255) COMMENT '交易货币'
           ,list_status   VARCHAR(255) COMMENT '上市状态： L上市 D退市 P暂停上市'
           ,list_date     VARCHAR(255) COMMENT '上市日期'
           ,delist_date   VARCHAR(255) COMMENT '退市日期'
           ,is_hs         VARCHAR(255) COMMENT '是否沪深港通标的，N否 H沪股通 S深股通'
           ,PRIMARY KEY (ts_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;
        	"""
                cursor.execute(sql)
            self.connect.commit()
        except Exception:
            logger.exception("创建 stock_basic 表失败")
            raise

    def stock_basic_updated_data(self):
        try:
            with self.connect.cursor() as cursor:
                fields = "ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs"
                param2 = ('%s, ' * len(fields.split(',')))[:-2]
                sql = 'REPLACE INTO stock_basic ({}) VALUES ({})'.format(fields, param2)

                fields = "ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs"
                data = self.pro.stock_basic(exchange='', list_status='L', fields=fields)

                for line in data.values:
                    cursor.execute(sql, tuple(line))

            self.connect.commit()
        except Exception:
            logger.exception("更新 stock_basic 数据失败")
            raise

    def stock_daily_create(self):
        try:
            with self.connect.cursor() as cursor:
                # Create a new record
                sql = """CREATE TABLE IF NOT EXISTS stock_daily (
               ts_code       VARCHAR(255) COMMENT 'TS代码'
              ,trade_date    VARCHAR(255) COMMENT '交易日期'
              ,open          FLOAT        COMMENT '开盘价'
              ,high          FLOAT        COMMENT '最高价'
              ,low           FLOAT        COMMENT '最低价'              
              ,close         FLOAT        COMMENT '收盘价'
              ,pre_close     FLOAT        COMMENT '昨收价'
              ,changes       FLOAT        COMMENT '涨跌幅'
              ,pct_chg       FLOAT        COMMENT '涨跌幅(未复权)'
              ,vol           FLOAT        COMMENT '成交量（手）'
              ,amount        FLOAT        COMMENT '成交额（千元）'
              ,PRIMARY KEY (ts_code,trade_date)
           ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;
           	"""
                # ['ts_code', 'trade_time', 'open', 'high', 'low', 'close', 'vol', 'amount', 'trade_date', 'pre_close']
                cursor.execute(sql)
            self.connect.commit()
        except Exception:
            logger.exception("创建 stock_daily 表失败")
            raise

    def stock_daily_updated_one(self, ts_code='000001.SH', start_date='20150101', end_date='20190405', freq='D'):
        total_line = 0
        try:
            end_date = end_date or time.strftime("%Y%m%d", time.localtime())
            with self.connect.cursor() as cursor:
                fields = "ts_code,trade_date,open,high,low,close,pre_close,changes,pct_chg,vol,amount"
                param2 = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'
                sql = 'REPLACE INTO stock_daily ({}) VALUES ({})'.format(fields, param2)

                data = ts.pro_bar(api=self.pro, ts_code=ts_code, asset='E', freq=freq, start_date=start_date,
                                  end_date=end_date)

                if data is None:
                    return 0

                if 'min' not in freq:
                    data = data[
                        ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg',
                         'vol', 'amount']]

                data = data.fillna(0)

                for line in data.values:
                    cursor.execute(sql, tuple(line))
                total_line = len(data.values)

                logger.info("{} from {} to {} {} Done", ts_code, start_date, end_date, total_line)
            self.connect.commit()
        except Exception:
            logger.exception("更新股票日线失败：{}", ts_code)
            raise
        return total_line

    def stock_daily_updated_all(self, start_date='20150101', end_date='20190405', freq='5min'):
        data = self.pro.stock_basic(exchange='', list_status='L', fields="ts_code")
        for line in data.values:
            ts_code = line[0]
            self.stock_daily_updated_one(ts_code=ts_code, start_date=start_date, end_date=end_date, freq=freq)

    def stock_min_create(self):
        try:
            with self.connect.cursor() as cursor:
                # Create a new record
                sql = """CREATE TABLE IF NOT EXISTS stock_daily (
               ts_code       VARCHAR(255) COMMENT 'TS代码'
              ,trade_time    VARCHAR(255) COMMENT '交易时间'
              ,open          FLOAT        COMMENT '开盘价'
              ,high          FLOAT        COMMENT '最高价'
              ,low           FLOAT        COMMENT '最低价'
              ,close         FLOAT        COMMENT '收盘价'
              ,vol           FLOAT        COMMENT '成交量（手）'
              ,amount        FLOAT        COMMENT '成交额（千元）'
              ,trade_date    VARCHAR(255) COMMENT '交易日期'
              ,pre_close     FLOAT        COMMENT '昨收价'
              ,PRIMARY KEY (ts_code,trade_time)
           ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;
           	"""
                # ['ts_code', 'trade_time', 'open', 'high', 'low', 'close', 'vol', 'amount', 'trade_date', 'pre_close']
                cursor.execute(sql)
            self.connect.commit()
        except Exception:
            logger.exception("创建分钟线表失败")
            raise

    def stock_min_updated_one(self, ts_code='000001.SH', start_date='20150101', end_date='20190405', freq='5min'):
        total_line = 0
        try:
            end_date = end_date or time.strftime("%Y%m%d", time.localtime())
            with self.connect.cursor() as cursor:
                fields = "ts_code,trade_time,open,high,low,close,vol,amount,trade_date,pre_close"
                param2 = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s'
                sql = 'REPLACE INTO stock_daily ({}) VALUES ({})'.format(fields, param2)

                data = ts.pro_bar(api=self.pro, ts_code=ts_code, asset='E', freq=freq, start_date=start_date,
                                  end_date=end_date)

                if data is None:
                    return 0

                if 'min' not in freq:
                    data = data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount', 'trade_date',
                                 'pre_close']]

                data = data.fillna(0)

                for line in data.values:
                    cursor.execute(sql, tuple(line))
                total_line = len(data.values)

                logger.info("{} from {} to {} {} Done", ts_code, start_date, end_date, total_line)
            self.connect.commit()
        except Exception:
            logger.exception("更新股票分钟线失败：{}", ts_code)
            raise
        return total_line

    def stock_min_updated_all(self, start_date='20150101', end_date='20190405', freq='5min'):
        data = self.pro.stock_basic(exchange='', list_status='L', fields="ts_code")
        for line in data.values:
            ts_code = line[0]
            self.stock_min_updated_one(ts_code=ts_code, start_date=start_date, end_date=end_date, freq=freq)


def connect_from_environment() -> DatabaseStock:
    """根据环境变量创建 MySQL 行情数据库对象。"""
    token = os.environ.get("TUSHARE_TOKEN")
    if not token:
        raise RuntimeError("缺少 tushare token，请设置环境变量 TUSHARE_TOKEN")
    password = os.environ.get("STOCK_MYSQL_PASSWORD")
    if password is None:
        raise RuntimeError("缺少 STOCK_MYSQL_PASSWORD 环境变量")
    ts.set_token(token)
    connection = pymysql.connect(
        host=os.environ.get("STOCK_MYSQL_HOST", "localhost"),
        user=os.environ.get("STOCK_MYSQL_USER", "root"),
        password=password,
        db=os.environ.get("STOCK_MYSQL_DB", "stock"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return DatabaseStock(connection=connection)


if __name__ == "__main__":
    connect_from_environment().stock_daily_updated_all(freq="D", end_date="")
