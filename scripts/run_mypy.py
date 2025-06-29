#!/usr/bin/env python3
"""Script chạy mypy với các options khác nhau."""

import subprocess
import sys
from pathlib import Path


def run_mypy(target: str = "pages/ utils/ config/ tests/", strict: bool = False):
    """Chạy mypy với target và options cụ thể."""
    cmd = ["mypy"]

    if strict:
        cmd.append("--strict")

    cmd.extend(target.split())

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "pages/ utils/ config/"
    strict = "--strict" in sys.argv

    success = run_mypy(target, strict)
    sys.exit(0 if success else 1)
