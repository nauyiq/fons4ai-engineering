"""Read-only inventory of ZIP-based packages; never extract or execute content."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile


def inspect_artifact(path, match="", limit=40):
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    path = Path(path).resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"not a file: {path}")
    digest = hashlib.sha256()
    # Hash and inspect the same open file; no archive member is read or extracted.
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
        stream.seek(0)
        try:
            with zipfile.ZipFile(stream) as archive:
                entries = archive.infolist()
                matches = [item.filename for item in entries
                           if not item.is_dir() and match.casefold() in item.filename.casefold()]
        except zipfile.BadZipFile as exc:
            raise ValueError(f"not a readable ZIP-based package: {path}") from exc
    return {
        "path": str(path), "sha256": digest.hexdigest(),
        "entry_count": len(entries), "match_count": len(matches),
        "entries": matches[:limit], "truncated": len(matches) > limit,
        "evidence_scope": "Package names only; no API or runtime semantics verified.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--match", default="", help="Case-insensitive literal filename substring")
    parser.add_argument("--limit", type=int, default=40, help="Maximum entries (1-500)")
    args = parser.parse_args()
    try:
        result = inspect_artifact(args.artifact, args.match, args.limit)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
