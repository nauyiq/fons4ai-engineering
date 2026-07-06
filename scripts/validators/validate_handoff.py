#!/usr/bin/env python3
"""Validate a Fons4AI stage handoff document."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "## 基本信息",
    "## 输入产物",
    "## 输出产物",
    "## 下一步建议",
    "## 下游必须读取",
    "## 下游不得假设",
    "## 已确认事实",
    "## 待确认问题",
    "## 风险与阻塞",
    "## Validator 结果",
    "## 需要用户确认的事项",
)

REQUIRED_TERMS = (
    "当前阶段",
    "当前 Agent / Skill",
    "当前状态",
    "建议下游 Skill",
    "是否需要用户确认",
    "校验命令",
    "校验结果",
    "是否阻塞",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"handoff file not found: {path}"]

    text = read_text(path)
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"{path} missing required heading: {heading}")
    for term in REQUIRED_TERMS:
        if term not in text:
            errors.append(f"{path} missing required term: {term}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Fons4AI handoff document")
    parser.add_argument("--file", required=True, help="Handoff markdown file")
    args = parser.parse_args()

    path = Path(args.file).resolve()
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {path} is a valid Fons4AI handoff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
