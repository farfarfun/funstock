import argparse
import os
from pathlib import Path

from funstock.dataset import StockDownload


def run_year(root: Path) -> None:
    """将年度行情写入指定根目录，无返回值。"""
    for year in range(2021, 2010, -1):
        path = root / "years" / f"stock-{year}.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        down = StockDownload(db_path=path)
        down.save_year(year)


def run_onebyone(root: Path) -> None:
    """将每只股票行情分别写入指定根目录，无返回值。"""
    path = root / "stocks"
    path.mkdir(parents=True, exist_ok=True)
    down = StockDownload(db_path=path / "base.db")
    down.save_ones(path)


def run_month(root: Path) -> None:
    """将月度行情写入指定根目录，无返回值。"""
    for year in range(2000, 2021):
        for month in range(1, 13):
            month = year * 100 + month
            path = root / "months" / f"stock-{month}.db"
            path.parent.mkdir(parents=True, exist_ok=True)
            down = StockDownload(db_path=path)
            down.save_month(month)


def main(argv: list[str] | None = None) -> None:
    """解析任务和数据目录参数并执行批量下载，无返回值。"""
    parser = argparse.ArgumentParser(description="批量下载股票行情")
    parser.add_argument("command", choices=("year", "month", "onebyone"))
    parser.add_argument("--root", type=Path, help="数据目录，优先于 FUNSTOCK_DATA_DIR")
    args = parser.parse_args(argv)
    root_value = args.root or os.environ.get("FUNSTOCK_DATA_DIR")
    if not root_value:
        parser.error("请通过 --root 或 FUNSTOCK_DATA_DIR 指定数据目录")
    root = Path(root_value)
    {"year": run_year, "month": run_month, "onebyone": run_onebyone}[args.command](root)


if __name__ == "__main__":
    main()
