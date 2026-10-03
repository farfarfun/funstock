# 变更日志

## 未发布

### 新增

- 为 `DatabaseStock` 的公开方法补齐类型标注和中文 docstring，并新增覆盖正常路径、空响应和环境变量校验的测试。

### 修复

- 修复 `DatabaseStock.stock_min_create`/`stock_min_updated_one` 误建表名/误写入 `stock_daily` 表的问题，分钟线数据改为正确写入 `stock_min` 表。
- 移除 `example/huobi_ex.py` 中未定义变量 `a = c` 的死代码，access_key/secret_key 改为从环境变量读取。

### 变更

- README 补充 `example/huobi_Python` 的来源、原始协议（Apache License 2.0）和运行前置条件说明，新增 `example/huobi_Python/NOTICE.md`。

### 废弃

- 无。

## 0.2.10 - 2026-09-21

### 新增

- 增加根级 API 测试和公开图表计算函数导出。

### 修复

- 修复包结构、图表模块命名和 README 导入路径。
- 下载失败改为有限重试并保留带股票代码和日期的错误上下文。

### 变更

- 使用 `src/funstock/` 布局、uv 锁文件和 `funtable` SQLite 基类。
- 统一使用 `farlog`，并补齐运行时依赖版本下限。

### 废弃

- 无。

## 0.2.9

### 新增

- 延续此前行情下载与 K 线图功能。

### 修复

- 无。

### 变更

- 无。

### 废弃

- 无。
