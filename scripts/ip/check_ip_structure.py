#!/usr/bin/env python3

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
IP_ROOT = REPO_ROOT / "hw" / "ip"

REQUIRED_DIRS = ("rtl", "dv", "doc")
REQUIRED_FILES = ("doc/README.md",)


def main() -> int:
    if not IP_ROOT.exists():
        print(f"missing IP root: {IP_ROOT}", file=sys.stderr)
        return 1

    failures = []

    for ip_dir in sorted(path for path in IP_ROOT.iterdir() if path.is_dir()):
        rel = ip_dir.relative_to(REPO_ROOT)

        for dirname in REQUIRED_DIRS:
            path = ip_dir / dirname
            if not path.is_dir():
                failures.append(f"{rel}: missing directory {dirname}/")

        for filename in REQUIRED_FILES:
            path = ip_dir / filename
            if not path.is_file():
                failures.append(f"{rel}: missing file {filename}")

    if failures:
        print("IP structure check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("IP structure check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
