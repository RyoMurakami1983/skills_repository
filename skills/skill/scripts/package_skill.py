#!/usr/bin/env python3
"""Package a skill directory into a .skill archive."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


EXCLUDED_DIR_NAMES = {"__pycache__"}


def iter_skill_files(skill_dir: Path, output: Path):
    resolved_output = output.resolve()
    for file_path in skill_dir.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.resolve() == resolved_output:
            continue
        relative_path = file_path.relative_to(skill_dir)
        if any(part in EXCLUDED_DIR_NAMES for part in relative_path.parts):
            continue
        yield file_path, relative_path


def package_skill(skill_dir: Path, output: Path) -> Path:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path, relative_path in iter_skill_files(skill_dir, output):
            archive.write(file_path, relative_path)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a skill directory as a .skill file")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--output", help="Output archive path")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    if not skill_dir.is_dir():
        raise SystemExit(f"Skill directory not found: {skill_dir}")

    output = Path(args.output).resolve() if args.output else skill_dir.with_suffix(".skill")
    package_skill(skill_dir, output)

    print(f"Packaged {skill_dir} -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
