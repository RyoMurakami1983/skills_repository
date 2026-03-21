---
name: pdf
description: Use when: extracting PDF text, running Optical Character Recognition (OCR), splitting/merging files, and processing forms with reproducible uv-based commands.
---

## When to Use This Skill

Use this skill when your task requires repeatable Portable Document Format (PDF) operations in business workflows.

- Extracting text from born-digital PDF invoices for downstream reconciliation logs.
- Running OCR on scanned maintenance reports before classification or compliance review.
- Splitting large audit binders into deterministic page ranges for department delivery.
- Merging signed appendices into a single release artifact with controlled file naming.
- Filling or flattening form fields while preserving an auditable processing trail.
- Building rerunnable command records that teammates can execute without hidden context.

## Core Principles

1. **Foundation before optimization**: Start with deterministic commands, then tune speed and cost.
2. **Pattern over improvisation**: Reuse named flows so outputs stay consistent across operators.
3. **Traceability over guessing**: Mark source method and uncertainty instead of silent correction.
4. **Lifecycle-aware artifacts**: Separate intermediate files from final deliverables by design.

## Workflow:

### Step 1 - Confirm paths and policy

Use explicit paths for input, output, and retention metadata.

```powershell
Test-Path input.pdf
```

> **Values**: Foundation and Form

### Step 2 - Detect text layer

Use extraction first, because it is faster and preserves native text when available.

```powershell
uv run --with pypdf==6.1.1 python scripts\extract_text.py input.pdf --output input.txt
```

> **Values**: Foundation and Compound Growth

### Step 3 - Choose extraction or OCR path

Use OCR only when extraction is empty or unusable, because OCR costs more compute time.

```powershell
uv run --with pypdfium2==5.6.0 --with rapidocr-onnxruntime==1.4.4 --with numpy==2.4.3 python scripts\ocr_script.py input.pdf --output input.ocr.txt
```

> **Values**: Neutral Perspective and White Space Design

### Step 4 - Publish and record provenance

Use deterministic naming and keep a rerunnable log, because operational audits require reproducibility.

```powershell
uv cache prune
```

> **Values**: Teachability and Compound Growth

### Decision Table

| Situation | Primary Path | Fallback | Output Suffix |
| --- | --- | --- | --- |
| Text layer exists and quality is acceptable | `extract_text.py` | OCR only for failed pages | `.txt` |
| Text layer missing or empty | `ocr_script.py` | Increase `--scale` and rerun | `.ocr.txt` |
| Mixed quality across pages | Hybrid by page | Manual review for unreadable spans | `.hybrid.txt` |

## Patterns

### Basic Pattern

#### Overview

Use this pattern to extract text from born-digital PDFs with minimal setup.

#### When to Use

Use when extraction quality is already high and OCR would add unnecessary cost.

#### Steps

1. Confirm that the source file exists.
2. Run extraction with pinned dependency versions.
3. Save output beside business artifacts, not in temp-only locations.

```powershell
uv run --with pypdf==6.1.1 python scripts\extract_text.py input.pdf --output input.txt
```

### Intermediate Pattern

#### Overview

Use this pattern to switch between extraction and OCR based on measured evidence.

#### When to Use

Use when source quality varies by document or by page.

#### Steps

1. Run text extraction first.
2. If extracted text is empty or unusable, run OCR.
3. Record source type (`text-layer` or `ocr`) in the output header.

```powershell
uv run --with pypdf==6.1.1 python scripts\extract_text.py scan.pdf --output scan.txt
uv run --with pypdfium2==5.6.0 --with rapidocr-onnxruntime==1.4.4 --with numpy==2.4.3 python scripts\ocr_script.py scan.pdf --output scan.ocr.txt
```

### Advanced Pattern

#### Overview

Use this pattern to operate batch pipelines with explicit error handling and recovery.

#### When to Use

Use when processing many files, enforcing naming rules, and preserving auditability.

#### Steps

1. Iterate files with deterministic naming conventions.
2. Track success and failure per file.
3. Preserve intermediate outputs for troubleshooting.

```python
from pathlib import Path
import subprocess

for pdf in sorted(Path("incoming").glob("*.pdf")):
    out = Path("outputs") / f"{pdf.stem}.txt"
    cmd = ["uv", "run", "--with", "pypdf==6.1.1", "python", "scripts\\extract_text.py", str(pdf), "--output", str(out)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {pdf.name}: {result.stderr.strip()}")
        continue
    print(f"[OK] {pdf.name} -> {out}")
```

## Best Practices

- Pin every `--with` dependency to reduce drift.
- Keep OCR raw output and normalized output as separate files.
- Mark unreadable segments explicitly, such as `[UNREADABLE: page 3 line 12]`.
- Record the exact command line used for each deliverable.
- Use explicit source labels in every output header.
- Avoid silent normalization when confidence is low.
- Apply deterministic naming for every run.
- Define retention rules before batch execution.
- Consider audit-readiness as a default output requirement.

### Why these practices work

- **Why** deterministic commands: they reduce cross-operator variance.
- **Why** source labels: they prevent mixing OCR and text-layer outputs.
- **Why** separate raw/normalized files: they enable defensible reviews.
- **Why** explicit retention policy: it avoids accidental loss of evidence.
- **Why** rerunnable logs: they make troubleshooting and audits faster.

### Good vs Bad Examples

❌ Bad: Rewrite uncertain OCR text without documenting confidence or source method.

✅ Good: Keep original OCR output, create a reviewed version, and log each correction reason.

❌ Bad: Save final files only to temporary locations that are cleaned automatically.

✅ Good: Save final files to a durable business path and archive processing metadata.

❌ Bad: Detect extraction failure but continue without a fallback decision record.

✅ Good: Record the fallback decision and run OCR **instead** with a clear reason.

## Common Pitfalls

- Forgetting to pass explicit input and output paths in automation jobs.
- Mixing OCR and text-layer results without source labels.
- Reusing stale outputs after source PDFs changed.

### Fixes

- Use deterministic file naming with run identifiers as the first **solution**.
- Add a header line that states extraction method and timestamp as a second **solution**.
- Recompute output whenever source hash changes to **correct** stale deliverables.
- If a page remains unreadable, **fix** downstream mapping by keeping explicit placeholders.

## Anti-Patterns

- Mixing `pip install` and `uv run --with` without an environment policy.
- Deleting uv cache on every run, which wastes time and energy.
- Publishing business outputs with no reproducibility log.

## FAQ

Q. Why does AppData cache appear during `uv run --with`?
A. uv reuses cached dependency artifacts by design for faster reruns.

Q. Should we always create `.venv`?
A. Use `.venv` for long-lived projects; use `--with` for task-scoped operations.

Q. When should cache be deleted?
A. Delete cache only for disk pressure or suspected corruption.

## Quick Reference

| Decision | Command | Why |
| --- | --- | --- |
| Text layer available | `python scripts\extract_text.py` | Faster and preserves native text. |
| Text layer unavailable | `python scripts\ocr_script.py` | Restores searchable text for downstream use. |

```powershell
# Text-layer extraction
uv run --with pypdf==6.1.1 python scripts\extract_text.py input.pdf --output input.txt

# OCR for scanned PDFs
uv run --with pypdfium2==5.6.0 --with rapidocr-onnxruntime==1.4.4 --with numpy==2.4.3 python scripts\ocr_script.py input.pdf --output input.ocr.txt

# Cache operations
uv cache dir
uv cache prune
```

## License Note

This skill was authored from scratch for repository operations. Follow repository governance for reuse and redistribution.
