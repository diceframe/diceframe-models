# diceframe-models

DiceFrame 可选本地模型的**受审核资产清单仓库**：只存模型目录（manifest）、
固定上游 revision、SHA-256、许可证与基准矩阵，**不存放模型权重**——权重由
上游 Hugging Face / hf-mirror.com 分发，本仓库只登记其固定 URL 与校验值。

设计依据：`diceframe_optional_local_models_plan_2026-11-12.md` §3（提议本仓库）、
主仓 `src/memory/model_catalog.py` 的 `load_catalog` 校验契约。

## 目录结构

```text
catalog/index.json            # 目录入口：模型 id → 明细文件 + 状态（released/candidate）
models/<id>/<version>.json    # loader 兼容的 catalog 分片（与主仓 load_catalog 同一契约）
licenses/LICENSES.md          # 许可证登记（允许再分发与归属声明）
benchmarks/README.md          # 基准矩阵模板与已记录结果
scripts/validate_catalog.py   # CI 校验：loader 规则 + index 一致性 + 状态规则
```

## 与主仓的关系

- 主仓内置 `src/memory/default_model_catalog.json` 是**离线兜底**（首次启动、
  仓库不可达时仍可安装 bge-small-zh-v1.5）；
- 本仓库 `catalog/index.json` 是**权威目录**：新增/升级模型在这里登记，
  主仓的远端目录接入（读取本仓库 raw URL + 固定工件校验）为后续工作；
- 下载域白名单：`huggingface.co`、`hf-mirror.com` 及其子域（与主仓
  `_trusted_download_host` 一致），禁止其它来源。

## 收录标准（进入 released 必须）

1. 每个文件有固定 URL + 真实 SHA-256（从上游 LFS oid 或逐字节计算获得，禁止手填）；
2. 许可证允许再分发且已登记归属与模型卡链接；
3. dimension / max_input_tokens 经真实推理确认（候选条目 dimension 可为 0）；
4. CPU（2c4g 起步）基准矩阵记录于 `benchmarks/`；
5. `scripts/validate_catalog.py` 通过。
