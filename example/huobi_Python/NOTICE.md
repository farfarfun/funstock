# 第三方代码声明

本目录下的代码来自火币（Huobi）官方 Python SDK 示例，vendored 进 funstock 仓库仅用于学习参考，与股票行情主功能无关。

- 上游仓库：<https://github.com/HuobiRDCenter/huobi_Python>
- 原始协议：Apache License 2.0（<https://www.apache.org/licenses/LICENSE-2.0>）
- 版权归原作者及贡献者所有

示例脚本中出现的 `g_api_key`/`g_secret_key`/`sub_uid`/`access_key`/`otp_token` 等均为上游仓库自带的占位数据，不是任何真实账户的凭据；使用前需替换为调用方自己的配置（建议通过环境变量或 `funsecret` 注入，不要写死在代码里）。

funstock 本身基于 MIT 协议开源（见仓库根目录 `LICENSE`），Apache License 2.0 与 MIT 兼容，可在保留本声明和原始版权信息的前提下收录。
