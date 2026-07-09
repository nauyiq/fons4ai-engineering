#!/usr/bin/env python3
"""Validate S0 quick-change records."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "# 快速变更记录",
    "## 变更说明",
    "## 受影响文件",
    "## S0 准入自查",
    "## 验证方式",
    "## 实现确认门禁",
    "## 变更结果",
)

ADMISSION_TERMS = (
    "影响文件不超过 5 个",
    "不改变业务逻辑或状态流转",
    "不改变数据模型或表结构",
    "不改变公共 API 或契约",
    "不改变权限或安全逻辑",
    "不涉及跨核心模块影响",
    "不涉及资金/支付/库存/监管数据",
    "可独立验证且验证方式明确",
)

PLACEHOLDER_RE = re.compile(r"<[^>]+>")
S0_LEVEL_RE = re.compile(r"SDD\s*等级\s*[:：]\s*`?S0`?", re.IGNORECASE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"quick-change report not found: {path}"]

    text = read(path)

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")

    if not S0_LEVEL_RE.search(text):
        errors.append("SDD level must be S0")

    for term in ADMISSION_TERMS:
        if term not in text:
            errors.append(f"admission check missing: {term}")

    if PLACEHOLDER_RE.search(text):
        admission_section = text[text.find("## S0 准入自查"):]
        if PLACEHOLDER_RE.search(admission_section):
            errors.append("S0 admission self-check still has placeholders; fill in yes/no for every condition")

    completion_re = re.compile(r"完成状态\s*[:：]\s*(已完成|需升级)", re.IGNORECASE)
    if completion_re.search(text):
        result_section = text[text.find("## 变更结果"):]
        if "验证结果" not in result_section:
            errors.append("completed report must record verification results")
        if not re.search(r"未验证项\s*[:：]", result_section):
            errors.append("completed report must state unverified items explicitly")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate S0 quick-change records")
    parser.add_argument("--report", required=True, help="Path to the quick-change report")
    args = parser.parse_args()

    path = Path(args.report).resolve()
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {path.name} is a valid S0 quick-change record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
