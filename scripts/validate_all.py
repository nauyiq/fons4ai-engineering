"""Run current suite checks and behavior tests; legacy protocols are excluded."""
import argparse
from pathlib import Path
import subprocess
import sys

from sync_global_skills import collect_skills, verify_lock
from validate_repository import validate_docs, validate_suite


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        errors = validate_suite(root / "skills") + validate_docs(root)
        errors += verify_lock(root, collect_skills(root / "skills"))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    result = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=root)
    if errors or result.returncode:
        return 1
    print("OK: current suite, source hashes, navigation and behavior tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
