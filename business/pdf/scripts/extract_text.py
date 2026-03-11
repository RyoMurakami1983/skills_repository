from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Extract text layer from PDF into a text file.')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('--output', '-o', help='Output text file path (default: <input>.txt)')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_pdf = Path(args.input_pdf)
    if not input_pdf.exists():
        raise FileNotFoundError(f'Input PDF not found: {input_pdf}')

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError('pypdf is required. Example: uv run --with pypdf==6.1.1 python scripts\\extract_text.py <file.pdf>') from exc

    output_path = Path(args.output) if args.output else input_pdf.with_suffix('.txt')

    reader = PdfReader(str(input_pdf))
    lines: list[str] = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ''
        lines.append(f'=== PAGE {idx} ===')
        lines.append(text)
        lines.append('')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote text extraction: {output_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
