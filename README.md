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

## 批量下载

批量下载脚本要求通过命令行参数或环境变量指定数据目录：

```bash
python -m funstock.dataset.run --root ./stocks year
# 或 export FUNSTOCK_DATA_DIR=./stocks
```

未完成且依赖未声明 `keras_bert` 的旧分析模块已移除。

## 第三方示例代码

`example/huobi_Python/` 与 `example/huobi_ex.py` 是火币（Huobi）交易所 Python SDK 的用法示例，与本项目主功能（股票行情）无关，不是 funstock 的运行时依赖：

- 来源：<https://github.com/HuobiRDCenter/huobi_Python>（原始协议 Apache License 2.0，版权归原作者所有，详见 `example/huobi_Python/NOTICE.md`）
- 运行这些示例前需单独安装 `huobi_client`（`uv pip install huobi_client`），并通过环境变量 `HUOBI_ACCESS_KEY`/`HUOBI_SECRET_KEY` 提供账户密钥；`example/huobi_Python/example/` 下的脚本沿用上游仓库的 `g_api_key`/`g_secret_key` 占位写法，需要使用者自行补充后才能运行，示例中出现的 ID、密钥均为上游仓库自带的占位数据，不是真实凭据。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
