# funstock

股票行情数据下载/存储与 K 线图表工具：通过 [tushare](https://tushare.pro/) 和 [baostock](http://baostock.com/) 拉取 A 股基本信息、日线/分钟线行情，写入本地 SQLite；并基于 [pyecharts](https://pyecharts.org/) 绘制 K 线图。

## 安装

使用 uv 安装依赖并创建开发环境：

```bash
git clone https://github.com/farfarfun/funstock.git
cd funstock
uv sync
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
from funstock.echarts.day_chart import DayChart

chart = DayChart(token="your_token")
chart.start_date, chart.end_date = "20230101", "20231231"
grid_chart = chart.get_chart(ts_code="000001.SZ")
grid_chart.render("kline.html")
```

## 现状说明

`funstock/analyse/manage.py` 依赖 `keras_bert`，与股票数据下载/图表功能无关，是未完成的遗留代码。`example/huobi_Python/` 是 vendored 的火币交易所 SDK 示例，与本项目主功能（股票行情）无关。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
