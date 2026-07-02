#!/usr/bin/env python3
"""Validate an Agent environment readiness report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "## 评估范围",
    "## 当前准备度等级",
    "## 外部依赖与验证场景矩阵",
    "## 已具备能力",
    "## 缺失能力与影响",
    "## MCP 与替代方案建议",
    "## 安全与权限边界",
    "## Agent 交付证据要求",
    "## 未验证项声明",
    "## 后续行动",
)

REQUIRED_TERMS = (
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "MySQL",
    "Redis",
    "RocketMQ",
    "Nacos",
    "MCP",
    "替代方案",
    "权限",
    "未验证",
)

FORBIDDEN_TERMS = (
    "必须安装 MCP",
    "必须配置 MCP",
    "作为开发准入门槛",
    "属于 SDD 必经步骤",
    "是 SDD 必经步骤",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def validate_report(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"report does not exist: {path}"]

    text = read_text(path)
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")

    for term in REQUIRED_TERMS:
        if term not in text:
            errors.append(f"missing required term: {term}")

    for term in FORBIDDEN_TERMS:
        if term in text:
            errors.append(f"forbidden hard-gate wording found: {term}")

    if len(text.strip()) < 800:
        errors.append("report is too short for a useful readiness assessment")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Agent environment readiness report")
    parser.add_argument("--report", required=True, help="Path to the readiness report markdown file")
    args = parser.parse_args()

    errors = validate_report(Path(args.report).resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {args.report} is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
