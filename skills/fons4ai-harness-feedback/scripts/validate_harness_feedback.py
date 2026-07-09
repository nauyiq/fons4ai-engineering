#!/usr/bin/env python3
"""Validate a Fons4AI Harness upstream feedback report."""

from __future__ import annotations

import argparse
import re
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
    "待观察",
)

FORBIDDEN_TERMS = (
    "自动修改上游",
    "无需脱敏",
    "直接写入 .specify",
    ".specify" + "/reports/harness-feedback",
)

PLACEHOLDER_PATTERN = re.compile(r"<[^>\n]+>")
STATUS_PATTERN = re.compile(r"^>\s*Status\s*:\s*(?P<status>\S+)", re.MULTILINE)
EVIDENCE_ROW_PATTERN = re.compile(
    r"^\|\s*(?P<claim>[^|]+?)\s*\|\s*(?P<source>[^|]+?)\s*\|\s*(?P<level>L[123])\s*\|\s*(?P<state>[^|]+?)\s*\|",
    re.MULTILINE,
)

UNCERTAIN_REPEAT_TERMS = (
    "当前仅基于一个试点项目",
    "尚未形成多项目重复证据",
    "跨项目重复性待观察",
)

OVERSTATED_REPEAT_TERMS = (
    "具有跨项目通用性",
    "已在多个项目重复",
    "多个项目重复出现",
    "多项目重复出现",
    "跨项目通用问题",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def extract_status(text: str) -> str | None:
    match = STATUS_PATTERN.search(text)
    return match.group("status") if match else None


def validate_status_and_placeholders(text: str) -> list[str]:
    errors: list[str] = []
    status = extract_status(text)
    placeholders = sorted(set(PLACEHOLDER_PATTERN.findall(text)))

    if status == "Ready" and placeholders:
        errors.append(
            "Ready report contains unresolved placeholder(s): "
            + ", ".join(placeholders)
        )

    if status == "Ready" and "待脱敏" in text:
        errors.append("Ready report must not contain pending desensitization state: 待脱敏")

    return errors


def validate_evidence_rows(text: str) -> list[str]:
    errors: list[str] = []
    for match in EVIDENCE_ROW_PATTERN.finditer(text):
        claim = match.group("claim").strip()
        source = match.group("source").strip()
        level = match.group("level").strip()
        state = match.group("state").strip()
        has_placeholder = bool(PLACEHOLDER_PATTERN.search(source))

        if "已验证" in state and has_placeholder:
            errors.append(
                f"verified evidence row uses unresolved placeholder source: {claim}"
            )

        if level in {"L2", "L3"} and "已验证" in state and source in {"用户描述", "实施报告", "任务规划", "风险清单"}:
            errors.append(
                f"verified {level} evidence row must cite a specific report, script output, or confirmation: {claim}"
            )

    return errors


def validate_repeatability_claims(text: str) -> list[str]:
    has_uncertain_repeat = any(term in text for term in UNCERTAIN_REPEAT_TERMS)
    has_overstated_repeat = any(term in text for term in OVERSTATED_REPEAT_TERMS)
    if has_uncertain_repeat and has_overstated_repeat:
        return [
            "report overstates cross-project repeatability while also marking repeatability as unconfirmed"
        ]
    return []


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

    if "已脱敏" not in text and "敏感信息状态：不涉及" not in text and "敏感信息状态: 不涉及" not in text:
        errors.append("missing desensitization state: 已脱敏 or 敏感信息状态：不涉及")

    for term in FORBIDDEN_TERMS:
        if term in text:
            errors.append(f"forbidden wording found: {term}")

    if "spec/reports/harness-feedback" not in text:
        errors.append("report should use spec/reports/harness-feedback as the feedback location")

    if len(text.strip()) < 800:
        errors.append("report is too short for useful upstream feedback")

    errors.extend(validate_status_and_placeholders(text))
    errors.extend(validate_evidence_rows(text))
    errors.extend(validate_repeatability_claims(text))

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
