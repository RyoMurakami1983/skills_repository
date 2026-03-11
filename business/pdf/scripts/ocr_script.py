from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='OCR scanned PDF pages into text.')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('--output', '-o', help='Output text file path (default: <input>.ocr.txt)')
    parser.add_argument('--scale', type=float, default=2.5, help='Render scale for OCR image quality (default: 2.5)')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_pdf = Path(args.input_pdf)
    if not input_pdf.exists():
        raise FileNotFoundError(f'Input PDF not found: {input_pdf}')

    try:
        import numpy as np
        import pypdfium2 as pdfium
        from rapidocr_onnxruntime import RapidOCR
    except ImportError as exc:
        raise RuntimeError('OCR deps are required. Example: uv run --with pypdfium2==5.6.0 --with rapidocr-onnxruntime==1.4.4 --with numpy==2.4.3 python scripts\\ocr_script.py <file.pdf>') from exc

    output_path = Path(args.output) if args.output else input_pdf.with_suffix('.ocr.txt')

    doc = pdfium.PdfDocument(str(input_pdf))
    engine = RapidOCR()
    lines: list[str] = []

    for idx in range(len(doc)):
        page = doc[idx]
        pil_img = page.render(scale=args.scale).to_pil().convert('L')
        arr = np.array(pil_img)
        result, _ = engine(arr)
        page_text = '\n'.join([item[1] for item in result]) if result else ''
        lines.append(f'=== PAGE {idx + 1} ===')
        lines.append(page_text)
        lines.append('')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote OCR text: {output_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
