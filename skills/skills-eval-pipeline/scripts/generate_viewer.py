"""generate_viewer.py

Generate a self-contained HTML eval viewer from benchmark_summary.json.

Usage:
    python skills/skills-eval-pipeline/scripts/generate_viewer.py \\
        --skill-id skills-author-skill \\
        [--evals-dir evals] \\
        [--out viewer/index.html]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TEMPLATE_PATH = Path(__file__).parent.parent / "viewer" / "index.html"


def load_benchmark(evals_dir: Path, skill_id: str) -> dict:
    path = evals_dir / skill_id / "benchmark_summary.json"
    if not path.exists():
        raise FileNotFoundError(f"benchmark_summary.json not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def render(template: str, data: dict) -> str:
    """Inject benchmark JSON into the HTML template's data placeholder.

    Replaces the sentinel token (including the trailing null literal) so the
    resulting JavaScript is valid.  Also escapes '</script>' inside the JSON
    payload to prevent script-block injection.
    """
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    # Escape '</script>' in data values to prevent script-block breakout
    json_str = json_str.replace("</script>", "<\\/script>")
    # The template contains: const DATA = /* __BENCHMARK_DATA__ */null;
    # Replace the sentinel + the trailing 'null' literal as one atomic token.
    placeholder = "/* __BENCHMARK_DATA__ */null"
    if placeholder not in template:
        raise ValueError(f"Template is missing the placeholder: {placeholder!r}")
    return template.replace(placeholder, json_str)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate self-contained HTML eval viewer"
    )
    parser.add_argument("--skill-id", required=True, help="Skill directory name")
    parser.add_argument("--evals-dir", default="evals", help="Base evals directory")
    parser.add_argument(
        "--out",
        default=None,
        help="Output HTML path (default: evals/<skill_id>/viewer.html)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evals_dir = Path(args.evals_dir)

    try:
        data = load_benchmark(evals_dir, args.skill_id)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not TEMPLATE_PATH.exists():
        print(f"ERROR: Viewer template not found: {TEMPLATE_PATH}", file=sys.stderr)
        return 1

    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    try:
        html = render(template, data)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    out_path = Path(args.out) if args.out else evals_dir / args.skill_id / "viewer.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print(f"Viewer generated → {out_path}")
    print(f"Open in browser:  file://{out_path.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
