#!/usr/bin/env python3
"""Validate Fons4AI implementation report evidence and gate fields."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_TERMS = (
    "Harness 校验结果",
    "校验来源",
    "上游版本",
    "校验命令",
    "校验结果",
    "未验证项",
    "Evidence Bundle",
    "Spec Review",
    "Code Review",
    "人工 Gate",
    "是否阻塞交付",
    "是否可交付",
)

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def field_value(text: str, label: str) -> str | None:
    match = re.search(rf"^\s*-\s*{re.escape(label)}\s*[：:]\s*(.+)$", text, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def declares_completion(text: str) -> bool:
    for label, positive in (
        ("是否可交付完成", "是"),
        ("是否可交付", "是"),
        ("是否发布就绪", "是"),
        ("实施结果", "完成"),
    ):
        value = field_value(text, label)
        if value and "|" not in value and value.startswith(positive):
            return True
    return False


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"implementation report not found: {path}"]

    text = read_text(path)
    missing = [term for term in REQUIRED_TERMS if term not in text]
    if missing:
        errors.append(f"{path} missing required terms: {', '.join(missing)}")

    if declares_completion(text):
        if not re.search(r"未验证项\s*[：:]\s*无", text):
            errors.append(f"{path} declares completion but has missing or non-empty 未验证项")
        if not re.search(r"验证证据等级\s*[：:]\s*L3", text):
            errors.append(f"{path} declares completion but validation evidence level is not L3")
        if not re.search(r"Spec Review\s*[：:]\s*(通过|有条件通过)", text):
            errors.append(f"{path} declares completion but Spec Review is not passed or conditionally passed")
        if not re.search(r"Code Review\s*[：:]\s*(通过|有条件通过)", text):
            errors.append(f"{path} declares completion but Code Review is not passed or conditionally passed")
        if re.search(r"人工 Gate 适用性\s*[：:]\s*适用", text) and not re.search(r"人工 Gate 状态\s*[：:]\s*(已通过|有条件通过)", text):
            errors.append(f"{path} declares completion but required 人工 Gate is not passed or conditionally passed")
        blocking_value = field_value(text, "是否阻塞交付")
        if blocking_value and "|" not in blocking_value and blocking_value.startswith("是"):
            errors.append(f"{path} declares completion but Harness 校验结果 still blocks delivery")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Fons4AI implementation report")
    parser.add_argument("--report", required=True, help="Implementation report markdown file")
    args = parser.parse_args()

    path = Path(args.report).resolve()
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {path} is a valid Fons4AI implementation report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
