#!/usr/bin/env python3
"""Validate a Fons4AI Harness upstream feedback report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "## 来源",
    "## 问题分类",
    "## 现象",
    "## 期望行为",
    "## 初步归因",
    "## 是否建议回流上游",
    "## 建议修改位置",
    "## 证据清单",
    "## 脱敏说明",
    "## 后续行动",
)

CLASSIFICATION_TERMS = (
    "PROJECT_LOCAL",
    "SKILL_CONTRACT",
    "TEMPLATE_GAP",
    "VALIDATOR_GAP",
    "RULE_TOO_HEAVY",
    "CONTEXT_LOADING",
    "EVIDENCE_GAP",
    "ENV_LOCAL",
    "CROSS_PROJECT_REPEAT",
)

REQUIRED_TERMS = (
    "关联技能",
    "建议回流",
    "证据等级",
    "敏感信息",
    "已脱敏",
    "待观察",
)

FORBIDDEN_TERMS = (
    "自动修改上游",
    "无需脱敏",
    "直接写入 .specify",
    ".specify" + "/reports/harness-feedback",
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

    if not any(term in text for term in CLASSIFICATION_TERMS):
        errors.append("missing at least one harness feedback classification")

    for term in REQUIRED_TERMS:
        if term not in text:
            errors.append(f"missing required term: {term}")

    for term in FORBIDDEN_TERMS:
        if term in text:
            errors.append(f"forbidden wording found: {term}")

    if "spec/reports/harness-feedback" not in text:
        errors.append("report should use spec/reports/harness-feedback as the feedback location")

    if len(text.strip()) < 800:
        errors.append("report is too short for useful upstream feedback")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Fons4AI Harness upstream feedback report")
    parser.add_argument("--report", required=True, help="Path to the upstream feedback markdown file")
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
