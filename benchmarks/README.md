# 基准矩阵（released 前必须记录）

| 模型 | 日期 | 环境 | 语料 | Recall@10 | 首次加载 | 单条延迟 | 批量 32 延迟 | 备注 |
|---|---|---|---|---|---|---|---|---|
| bge-small-zh-v1.5 | 待补 | Windows 2c4g / Docker | 中文跑团世界书样本 | 待补 | 待补 | 待补 | 待补 | 主仓 MVP 已实测可用，数字待正式记录 |
| granite-embedding-97m-r2-int8 | — | — | 中文+混语样本 | 待补 | 待补 | 待补 | 待补 | **候选**：dimension 确认 + 本矩阵完成后转 released |

环境要求（2026-11-12 计划 §11）：纯 CPU、无 NVIDIA；2c4g 最低可用性、4c8g 推荐；
Linux AMD64 Docker 必测，Windows 普通安装必测。
