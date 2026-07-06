#!/usr/bin/env python3
"""Validate minimal Fons4AI Harness assets in a business project."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_FILES = (
    "AGENTS.md",
    ".specify/rules/agent运行规则.md",
    ".specify/rules/sdd团队协作规范.md",
    ".specify/memory/index.md",
)

OPTIONAL_FILES = (
    ".specify/fons4ai.yaml",
    ".specify/agent-readiness",
    ".specify/examples/sdd",
    "spec/features",
    "spec/reports/harness-feedback",
)

TEXT_REQUIREMENTS = (
    (
        "AGENTS.md",
        (
            "<!-- fons4ai-skill-routing: enabled -->",
            "Fons4AI 技能路由",
            "fons4ai-knowledge-bootstrap",
            "fons4ai-sdd-feature-workflow",
            "fons4ai-sdd-implement",
        ),
    ),
    (
        ".specify/rules/agent运行规则.md",
        ("# Agent运行规则", "实现者与裁判分离", "验证门禁", "Evidence Bundle", "Spec Reviewer", "Code Reviewer", "人工 Gate"),
    ),
    (
        ".specify/rules/sdd团队协作规范.md",
        ("# SDD团队协作规范", "SDD使用准入规则", "角色与评审门禁", "Spec Reviewer", "Code Reviewer", "人工 Gate"),
    ),
    (".specify/memory/index.md", ("# 项目知识库索引", "知识状态")),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def validate(target: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in REQUIRED_FILES:
        path = target / rel
        if not path.is_file():
            errors.append(f"missing required Harness asset: {rel}")

    for rel in OPTIONAL_FILES:
        path = target / rel
        if not path.exists():
            warnings.append(f"optional Harness asset not found: {rel}")

    for rel, terms in TEXT_REQUIREMENTS:
        path = target / rel
        if not path.exists():
            continue
        text = read_text(path)
        missing = [term for term in terms if term not in text]
        if missing:
            errors.append(f"{rel} missing required terms: {', '.join(missing)}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Fons4AI business-project Harness assets")
    parser.add_argument("--target", required=True, help="Business project root directory")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"ERROR: target is not a directory: {target}", file=sys.stderr)
        return 1

    errors, warnings = validate(target)
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {target} has minimal Fons4AI Harness assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
