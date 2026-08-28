# funstock

股票行情数据下载/存储与 K 线图表工具：通过 [tushare](https://tushare.pro/) 和 [baostock](http://baostock.com/) 拉取 A 股基本信息、日线/分钟线行情，写入本地 SQLite；并基于 [pyecharts](https://pyecharts.org/) 绘制 K 线图。

## 安装

尚未发布到 PyPI，需要从源码安装：

```bash
git clone https://github.com/farfarfun/funstock.git
cd funstock
pip install -e .
```

使用行情下载功能前需要设置 tushare token：

```bash
export TUSHARE_TOKEN=your_token
```

## 用法示例

下载并写入某只股票的日线行情：

```python
from funstock.dataset import StockDownload

down = StockDownload(db_path="./stock.db")
down.insert_basic()          # 写入股票基本信息
down.save_one("000001.SZ")   # 写入指定股票的日线/分钟线行情
```

绘制 K 线图：

```python
from funstock.echarts.DayChart import DayChart

chart = DayChart(token="your_token")
chart.start_date, chart.end_date = "20230101", "20231231"
grid_chart = chart.get_chart(ts_code="000001.SZ")
grid_chart.render("kline.html")
```

## 现状说明

`funstock/analyse/manage.py` 依赖 `keras_bert`，与股票数据下载/图表功能无关，是未完成的遗留代码。`example/huobi_Python/` 是 vendored 的火币交易所 SDK 示例，与本项目主功能（股票行情）无关。`pyproject.toml` 中仅声明了 `tushare` 一个依赖，实际还用到 `baostock`、`pandas`、`tqdm`、`fundata`、`funtool`、`pyecharts`、`requests`、`pymysql` 等未声明的第三方库，需要自行安装。
