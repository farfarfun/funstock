# coding=utf-8
import os
import time

import baostock as bs
import pandas as pd
import tushare as ts
from funstock.dataset.dataset import (QuotationDay, QuotationMin1,
                                       QuotationMin5, QuotationMin15,
                                       QuotationMin30, QuotationMin60,
                                       StockBasic)
from farlog import getLogger
from tqdm import tqdm

logger = getLogger("funstock")
MAX_RETRIES = 3


class StockDownloadError(RuntimeError):
    """行情下载在有限重试后仍失败。"""


class StockDownload:
    """下载并保存股票行情数据。"""

    def __init__(self, db_path: str | None = None) -> None:
        """初始化数据库、Tushare 和 Baostock 客户端。"""
        if db_path is None:
            db_path = os.path.abspath(
                os.path.dirname(__file__)) + '/data/stock.db'

        token = os.environ.get('TUSHARE_TOKEN')
        if not token:
            raise RuntimeError(
                '缺少 tushare token，请设置环境变量 TUSHARE_TOKEN')
        ts.set_token(token)
        self.pro = ts.pro_api()
        self.quotation_day = QuotationDay(db_path=db_path)
        self.quotation_min1 = QuotationMin1(db_path=db_path)
        self.quotation_min5 = QuotationMin5(db_path=db_path)
        self.quotation_min15 = QuotationMin15(db_path=db_path)
        self.quotation_min30 = QuotationMin30(db_path=db_path)
        self.quotation_min60 = QuotationMin60(db_path=db_path)
        self.basic = StockBasic(db_path=db_path)

        self.quotation_day.create()
        self.basic.create()

        lg = bs.login()
        logger.info("baostock 登录：{} {}", lg.error_code, lg.error_msg)

    def insert_basic(self) -> None:
        """更新股票基本信息。"""
        stock_info = self.pro.stock_basic(exchange='', list_status='L')
        response = self.basic.insert_list(
            list(stock_info.to_dict(orient='index').values()))
        logger.info("update stock info {} rows {}".format(
            len(stock_info), response))

    def _insert_day_tushare(self, ts_code: str, start_date: str = '20000901', end_date: str = '20211011') -> None:
        """下载单只股票日线数据，失败时有限重试。"""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                df = ts.pro_bar(api=self.pro, ts_code=ts_code, asset='E', freq='d', start_date=start_date,
                                end_date=end_date)
                if df is None:
                    raise StockDownloadError(f"Tushare 未返回数据：{ts_code}")
                df['trade_time'] = df['trade_date']
                df = df.rename(columns={
                    'trade_date': 'date',
                    'trade_time': 'time',
                    'vol': 'volume',
                })
                self.quotation_day.insert_list(
                    list(df.to_dict(orient='index').values()))
                break
            except Exception as e:
                if attempt == MAX_RETRIES:
                    raise StockDownloadError(f"日线下载失败：{ts_code}，日期 {start_date}-{end_date}") from e
                logger.warning("日线下载重试 {}/{}：{}", attempt, MAX_RETRIES, ts_code)
                time.sleep(attempt)
        self.quotation_day.vacuum()

    def insert_day_all_tushare(self, start_date='20000901', end_date='20211011'):
        info = pd.read_sql(
            'select * from {}'.format(self.basic.table_name), self.basic.conn)

        for ts_code in tqdm(info['ts_code'].values):
            self._insert_day_tushare(
                ts_code, start_date=start_date, end_date=end_date)
        self.quotation_day.vacuum()

    def insert_day_one_tushare(self, ts_code, start_date='20000901', end_date='20211011'):
        self._insert_day_tushare(
            ts_code, start_date=start_date, end_date=end_date)
        self.quotation_day.vacuum()

    def _insert_min_bao_stock(self, ts_code: str, start_date: str = '20000901', end_date: str = '20211011', frequency: str = "5") -> None:
        fields = "date,time,code,open,high,low,close,volume,amount"
        if frequency == '1':
            quotation = self.quotation_min1
        elif frequency == '5':
            quotation = self.quotation_min5
        elif frequency == '15':
            quotation = self.quotation_min15
        elif frequency == '30':
            quotation = self.quotation_min30
        elif frequency == '60':
            quotation = self.quotation_min60
        else:
            raise ValueError(f"不支持的分钟频率：{frequency}")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                code = ts_code.lower().split('.')
                code = '{}.{}'.format(code[1], code[0])
                rs = bs.query_history_k_data_plus(code,
                                                  fields=fields,
                                                  start_date=start_date,
                                                  end_date=end_date,
                                                  frequency=frequency,
                                                  adjustflag="3")
                df = pd.DataFrame(rs.get_data(), columns=rs.fields)

                if rs.error_code != '0':
                    raise StockDownloadError(f"Baostock 查询失败：{ts_code}，{rs.error_msg}")

                if df is None:
                    raise StockDownloadError(f"Baostock 未返回数据：{ts_code}")

                df['ts_code'] = ts_code
                quotation.insert_list(
                    list(df.to_dict(orient='index').values()))
                break
            except Exception as e:
                if attempt == MAX_RETRIES:
                    raise StockDownloadError(f"分钟线下载失败：{ts_code}，频率 {frequency}") from e
                logger.warning("分钟线下载重试 {}/{}：{}", attempt, MAX_RETRIES, ts_code)
                time.sleep(attempt)
        quotation.vacuum()
        

    def insert_min_all_bao_stock(self, start_date='20000901', end_date='20211011'):
        info = pd.read_sql(
            'select * from {}'.format(self.basic.table_name), self.basic.conn)
        start_date = '{}-{}-{}'.format(start_date[:4],
                                       start_date[4:6], start_date[6:])
        end_date = '{}-{}-{}'.format(end_date[:4], end_date[4:6], end_date[6:])
        for ts_code in tqdm(info['ts_code'].values):
            for freq in ('5', '15', '30', '60'):
                self._insert_min_bao_stock(
                    ts_code, start_date, end_date, frequency=freq)
        self.quotation_min5.vacuum()

    def insert_min_one_bao_stock(self, ts_code, start_date='20000901', end_date='20211011'):
        start_date = '{}-{}-{}'.format(start_date[:4],
                                       start_date[4:6], start_date[6:])
        end_date = '{}-{}-{}'.format(end_date[:4], end_date[4:6], end_date[6:])

        for freq in ('5', '15', '30', '60'):
            self._insert_min_bao_stock(
                ts_code, start_date, end_date, frequency=freq)
        self.quotation_min5.vacuum()

    def save_year(self, year=2020):
        self.insert_basic()
        start_date = '{}0101'.format(year)
        end_date = '{}1231'.format(year)
        self.insert_min_all_bao_stock(start_date=start_date, end_date=end_date)
        self.insert_day_all_tushare(start_date, end_date)
        self.quotation_day.vacuum()

    def save_month(self, month=202001):
        self.insert_basic()
        start_date = '{}01'.format(month)
        end_date = '{}31'.format(month)
        self.insert_min_all_bao_stock(start_date=start_date, end_date=end_date)
        self.insert_day_all_tushare(start_date, end_date)
        self.quotation_day.vacuum()

    def save_one(self, ts_code, start_date='20000901', end_date='20211011'):
        self.insert_basic()
        self.insert_day_one_tushare(ts_code, start_date, end_date)
        self.insert_min_one_bao_stock(
            ts_code, start_date=start_date, end_date=end_date)
        self.quotation_day.vacuum()

    def save_ones(self, path, start_date='20000101', end_date='20301231'):
        self.insert_basic()
        info = pd.read_sql(
            'select * from {}'.format(self.basic.table_name), self.basic.conn)

        for ts_code in tqdm(info['ts_code'].values):
            db_path = os.path.join(path, ts_code + '.db')
            stock = StockDownload(db_path=db_path)
            stock.save_one(ts_code, start_date=start_date, end_date=end_date)

    def release(self):
        # 登出系统 #
        bs.logout()
