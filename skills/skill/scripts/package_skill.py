#!/usr/bin/env python3
"""Package a skill directory into a .skill archive."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a skill directory as a .skill file")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--output", help="Output archive path")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    if not skill_dir.is_dir():
        raise SystemExit(f"Skill directory not found: {skill_dir}")

    output = Path(args.output).resolve() if args.output else skill_dir.with_suffix(".skill")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in skill_dir.rglob("*"):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(skill_dir))

    print(f"Packaged {skill_dir} -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
