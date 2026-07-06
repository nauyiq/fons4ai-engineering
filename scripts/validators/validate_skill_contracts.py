#!/usr/bin/env python3
"""Validate core Fons4AI skill contract and evidence sections."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


CORE_SKILLS = (
    "fons4ai-sdd-feature-workflow",
    "fons4ai-sdd-requirements",
    "fons4ai-sdd-design",
    "fons4ai-sdd-tasks",
    "fons4ai-sdd-implement",
    "fons4ai-sdd-change",
    "fons4ai-bugfix-workflow",
    "fons4ai-knowledge-summary",
)

EVIDENCE_REQUIRED_SKILLS = (
    "fons4ai-sdd-design",
    "fons4ai-sdd-change",
    "fons4ai-sdd-implement",
    "fons4ai-bugfix-workflow",
    "fons4ai-knowledge-summary",
)

REQUIRED_HEADINGS = (
    "## Contract",
    "### Inputs",
    "### Preconditions",
    "### Outputs",
    "### Exit Criteria",
    "### Handoff",
)

EVIDENCE_HEADINGS = (
    "## Evidence Required",
    "### Evidence Levels",
    "### Hard Evidence Gates",
    "### Evidence Output",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def validate_skill(path: Path, require_evidence: bool = False) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing skill file: {path}"]
    text = read(path)
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"{path} missing contract heading: {heading}")
    if require_evidence:
        for heading in EVIDENCE_HEADINGS:
            if heading not in text:
                errors.append(f"{path} missing evidence heading: {heading}")
        for phrase in ("不得从实体类", "任务完成状态必须有 L3", "长期知识沉淀必须有 L3"):
            if path.parent.name in EVIDENCE_REQUIRED_SKILLS and phrase in ("不得从实体类",) and path.parent.name not in {"fons4ai-sdd-design", "fons4ai-sdd-change", "fons4ai-knowledge-summary"}:
                continue
            if path.parent.name in EVIDENCE_REQUIRED_SKILLS and phrase in ("任务完成状态必须有 L3",) and path.parent.name != "fons4ai-sdd-implement":
                continue
            if path.parent.name in EVIDENCE_REQUIRED_SKILLS and phrase in ("长期知识沉淀必须有 L3",) and path.parent.name != "fons4ai-knowledge-summary":
                continue
            if phrase not in text:
                errors.append(f"{path} evidence section missing minimum gate phrase: {phrase}")
    if "Success:" not in text and "成功" not in text:
        errors.append(f"{path} contract should define success exit criteria")
    if "Blocked:" not in text and "阻塞" not in text:
        errors.append(f"{path} contract should define blocked exit criteria")
    if "../shared/" in text or "skills/shared" in text:
        errors.append(f"{path} must not depend on sibling shared skill files")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Fons4AI core skill contracts")
    parser.add_argument("--skills-root", default="skills")
    parser.add_argument("--skill", action="append", help="Specific skill directory name to validate")
    args = parser.parse_args()

    root = Path(args.skills_root)
    names = tuple(args.skill) if args.skill else CORE_SKILLS
    errors: list[str] = []
    for name in names:
        errors.extend(validate_skill(root / name / "SKILL.md", require_evidence=name in EVIDENCE_REQUIRED_SKILLS))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: core skill contracts are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
