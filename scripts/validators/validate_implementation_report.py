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
    "Test Decision",
    "Evidence Ledger",
    "回归范围",
    "全量回归触发",
    "证据复用",
    "服务级 Evidence Matrix",
    "运行初始化 DML / Seed 状态",
    "Spec Review",
    "Code Review",
    "人工 Gate",
    "是否阻塞交付",
    "是否可交付",
)
ALIGNMENT_MARKER = "ImplementationAlignmentVersion: 1"
ALIGNMENT_HEADERS = ("任务", "AC", "DesignRefs", "读取证据", "与当前代码对齐结论", "冲突/处理")

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
    is_template = "template" in path.name.lower()
    missing = [term for term in REQUIRED_TERMS if term not in text]
    if missing:
        errors.append(f"{path} missing required terms: {', '.join(missing)}")

    if ALIGNMENT_MARKER in text:
        if "Implementation Alignment" not in text:
            errors.append(f"{path} declares {ALIGNMENT_MARKER} but has no Implementation Alignment section")
        if not all(header in text for header in ALIGNMENT_HEADERS):
            errors.append(f"{path} Implementation Alignment table is missing required columns")
        alignment_rows = re.findall(r"^\|\s*(T\d{3})\s*\|\s*(AC-\d{3}(?:\s*[,，]\s*AC-\d{3})*)\s*\|([^\n]+)$", text, re.MULTILINE)
        if not alignment_rows:
            errors.append(f"{path} has no concrete Implementation Alignment task row")
        for task_id, _acs, remainder in alignment_rows:
            if not is_template and ("<" in remainder or "§x" in remainder or re.search(r"\b(?:TD|DEC)-x", remainder, re.IGNORECASE)):
                errors.append(f"{path} {task_id} Implementation Alignment contains placeholders")
            if re.search(r"\|\s*drift-found\s*\|\s*(?:无|none)\s*\|", f"|{remainder}", re.IGNORECASE):
                errors.append(f"{path} {task_id} reports drift-found without conflict handling")

    full_scope = re.search(r"回归范围\s*[：:]\s*full\b", text, re.IGNORECASE)
    full_trigger = field_value(text, "全量回归触发")
    if full_scope and (not full_trigger or full_trigger in {"无", "不适用"} or "更稳妥" in full_trigger):
        errors.append(f"{path} uses full regression without an explicit risk trigger")
    if re.search(r"证据复用\s*[：:]\s*是", text) and not re.search(
        r"输入指纹|源码指纹|测试指纹|依赖/构建指纹", text
    ):
        errors.append(f"{path} reuses evidence without input fingerprints")

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
