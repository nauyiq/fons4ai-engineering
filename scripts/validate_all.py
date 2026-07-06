#!/usr/bin/env python3
"""Run repository-level Fons4AI Harness validation."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_check(label: str, command: list[str], cwd: Path) -> int:
    print(f"==> {label}", flush=True)
    result = subprocess.run(command, cwd=cwd)
    if result.returncode == 0:
        print(f"OK: {label}", flush=True)
    else:
        print(f"ERROR: {label} failed with exit code {result.returncode}", file=sys.stderr)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate all Fons4AI Harness repository assets")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    python = sys.executable
    checks = [
        (
            "skill contracts",
            [python, "scripts/validators/validate_skill_contracts.py", "--skills-root", "skills"],
        ),
        (
            "feedback harness entrypoint",
            [python, "scripts/validators/validate_feedback_harness.py", "--root", "."],
        ),
        (
            "business project validator help",
            [python, "scripts/validators/validate_business_project_harness.py", "--help"],
        ),
        (
            "handoff template",
            [python, "scripts/validators/validate_handoff.py", "--file", "templates/handoff-template.md"],
        ),
        (
            "implementation report template",
            [
                python,
                "scripts/validators/validate_implementation_report.py",
                "--report",
                "skills/fons4ai-sdd-implement/assets/templates/implementation-report-template.md",
            ],
        ),
    ]

    example = root / "examples" / "business-project-minimal"
    if example.exists():
        checks.append(
            (
                "business project minimal example",
                [python, "scripts/validators/validate_business_project_harness.py", "--target", str(example)],
            )
        )

    failures = 0
    for label, command in checks:
        failures += 1 if run_check(label, command, root) != 0 else 0

    if failures:
        print(f"ERROR: {failures} validation check(s) failed", file=sys.stderr)
        return 1

    print("OK: all Fons4AI Harness validations passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
