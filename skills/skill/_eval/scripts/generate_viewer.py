"""`benchmark_summary.json` から自己完結型の HTML viewer を生成する。

使い方:
    uv run python skills/skill/_eval/scripts/generate_viewer.py \\
        --skill-id skill \\
        [--evals-dir evals] \\
        [--out viewer/index.html]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


TEMPLATE_PATH = Path(__file__).resolve().parents[1].parent / "assets" / "eval_review.html"


def load_benchmark(evals_dir: Path, skill_id: str) -> dict:
    """指定 skill の `benchmark_summary.json` を読み込む。"""
    path = evals_dir / skill_id / "benchmark_summary.json"
    if not path.exists():
        raise FileNotFoundError(f"benchmark_summary.json not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_history(evals_dir: Path, skill_id: str) -> list[dict]:
    """append-only の履歴 ledger を読み込む。"""
    path = evals_dir / skill_id / "benchmark_history.jsonl"
    if not path.exists():
        return []

    records: list[dict] = []
    skipped = 0
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            skipped += 1
            summary = raw_line.strip()
            if len(summary) > 200:
                summary = summary[:200] + "..."
            print(
                f"WARNING: Malformed JSON in {path} at line {lineno}: {exc} | {summary}",
                file=sys.stderr,
            )
            continue
    if skipped:
        print(
            f"WARNING: Skipped {skipped} malformed JSON line(s) while reading {path}",
            file=sys.stderr,
        )
    return records


def render(template: str, data: dict) -> str:
    """HTML template の data placeholder へ benchmark JSON を埋め込む。

    trailing の `null` まで含めて sentinel token を置換し、生成後の
    JavaScript が壊れないようにする。さらに JSON payload 内の
    `</script>` を escape し、script block injection を防ぐ。
    """
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    # `</script>` は大文字小文字を問わず script 終端になるため、先に escape する。
    json_str = re.sub(r'</script', r'<\\/script', json_str, flags=re.IGNORECASE)
    # U+2028/U+2029 は JS の文字列リテラルを壊すので escape しておく。
    json_str = json_str.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    # template には `const DATA = /* __BENCHMARK_DATA__ */null;` が入っている。
    # sentinel と trailing の `null` を一体で置換する。
    placeholder = "/* __BENCHMARK_DATA__ */null"
    if placeholder not in template:
        raise ValueError(f"Template is missing the placeholder: {placeholder!r}")
    return template.replace(placeholder, json_str)


def parse_args() -> argparse.Namespace:
    """CLI 引数を定義して返す。"""
    parser = argparse.ArgumentParser(
        description="自己完結型の HTML eval viewer を生成する"
    )
    parser.add_argument("--skill-id", required=True, help="skill ディレクトリ名")
    parser.add_argument("--evals-dir", default="evals", help="evals 基底ディレクトリ")
    parser.add_argument(
        "--out",
        default=None,
        help="出力 HTML パス（既定: evals/<skill_id>/viewer.html）",
    )
    return parser.parse_args()


def main() -> int:
    """viewer を生成して HTML ファイルへ書き出す。"""
    args = parse_args()
    evals_dir = Path(args.evals_dir)

    try:
        data = load_benchmark(evals_dir, args.skill_id)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    data["history"] = load_history(evals_dir, args.skill_id)

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
