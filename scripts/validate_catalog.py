"""目录校验：与主仓 src/memory/model_catalog.load_catalog 同一契约。

独立实现（模型仓库不 import 主程序）；两处规则若漂移，以主仓为准并同步本文件。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

TRUSTED_HOSTS = {"huggingface.co", "hf-mirror.com"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def trusted_download_host(hostname: str) -> bool:
    return hostname in TRUSTED_HOSTS or any(hostname.endswith(f".{h}") for h in TRUSTED_HOSTS)


def validate_model_entry(model: dict, source: str) -> None:
    model_id = str(model.get("id") or "").strip()
    if not model_id or Path(model_id).name != model_id or ".." in Path(model_id).parts:
        fail(f"{source}: invalid model id")
    if model.get("kind") != "embedding" or model.get("backend") != "onnxruntime":
        fail(f"{source}: unsupported kind/backend")
    status = str(model.get("status") or "released")
    if status not in {"released", "candidate", "deprecated"}:
        fail(f"{source}: unknown status {status!r}")
    files = model.get("files")
    if not isinstance(files, list) or not files:
        fail(f"{source}: no files")
    for item in files:
        sha = str(item.get("sha256") or "").lower()
        if not HEX64.match(sha):
            fail(f"{source}/{item.get('path')}: sha256 must be 64 hex chars")
        url = str(item.get("url") or "")
        if not url.startswith("https://") or not urlsplit(url).hostname:
            fail(f"{source}: unsafe file url")
        size = item.get("size")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            fail(f"{source}: invalid file size")
        for mirror in item.get("mirrors") or []:
            host = str(urlsplit(str(mirror)).hostname or "").lower()
            if not str(mirror).startswith("https://") or not trusted_download_host(host):
                fail(f"{source}: untrusted mirror {mirror}")
    if status == "released":
        if not int(model.get("dimension") or 0) > 0:
            fail(f"{source}: released entry must have a benchmark-confirmed dimension")
        if model.get("max_input_chars", 0) <= 0:
            fail(f"{source}: released entry must declare max_input_chars")
    if not str(model.get("license") or "").strip():
        fail(f"{source}: license is required")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    index_path = root / "catalog" / "index.json"
    if not index_path.exists():
        fail("catalog/index.json is missing")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if int(index.get("catalog_version", 0)) != 1:
        fail("unsupported catalog_version")
    seen: set[str] = set()
    for row in index.get("models") or []:
        model_file = root / str(row.get("file") or "")
        if not model_file.exists():
            fail(f"index points to missing file: {row.get('file')}")
        shard = json.loads(model_file.read_text(encoding="utf-8"))
        if int(shard.get("catalog_version", 0)) != 1:
            fail(f"{model_file}: unsupported catalog_version")
        for model in shard.get("models") or []:
            model_id = str(model.get("id") or "")
            if model_id in seen:
                fail(f"duplicate model id: {model_id}")
            seen.add(model_id)
            validate_model_entry(model, str(model_file.relative_to(root)))
            if model_id != row.get("id"):
                fail(f"index/model id mismatch: {row.get('id')} vs {model_id}")
            if str(model.get("status") or "released") != str(row.get("status") or "released"):
                fail(f"{model_id}: index status disagrees with model entry")
    # 仓库根不再持有旧版顶层 catalog.json（避免双源）。
    if (root / "catalog.json").exists():
        fail("legacy top-level catalog.json must not exist")
    print(f"OK: {len(seen)} model(s) validated")


if __name__ == "__main__":
    main()
