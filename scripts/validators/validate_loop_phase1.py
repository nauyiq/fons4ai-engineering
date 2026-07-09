#!/usr/bin/env python3
"""Validate Loop Phase 1 documentation and record template."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_FILES = (
    "docs/loop-phase-1.md",
    "templates/loop-improvement-record-template.md",
)

DOC_TERMS = (
    "Loop Phase 1",
    "上游反馈单",
    "Loop 改进记录",
    "全局 skills",
    "Phase 1 完成定义",
    "非目标",
)

TEMPLATE_HEADINGS = (
    "## 1. 来源反馈",
    "## 2. 用户决策",
    "## 3. 问题归因",
    "## 4. 修改清单",
    "## 5. 验证记录",
    "## 6. 全局同步",
    "## 7. 关闭结论",
)

TEMPLATE_TERMS = (
    "Status：Draft | In Progress | Verified | Synced | Deferred | Rejected",
    "来源反馈单",
    "用户确认的边界",
    "证据成熟度",
    "python scripts/validate_all.py --root .",
    "哈希比对",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing Loop Phase 1 asset: {rel}")

    doc = root / "docs/loop-phase-1.md"
    if doc.exists():
        text = read(doc)
        missing = [term for term in DOC_TERMS if term not in text]
        if missing:
            errors.append(f"{doc} missing required terms: {', '.join(missing)}")

    template = root / "templates/loop-improvement-record-template.md"
    if template.exists():
        text = read(template)
        missing_headings = [heading for heading in TEMPLATE_HEADINGS if heading not in text]
        if missing_headings:
            errors.append(f"{template} missing headings: {', '.join(missing_headings)}")
        missing_terms = [term for term in TEMPLATE_TERMS if term not in text]
        if missing_terms:
            errors.append(f"{template} missing required terms: {', '.join(missing_terms)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Fons4AI Loop Phase 1 assets")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("OK: Loop Phase 1 assets are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
