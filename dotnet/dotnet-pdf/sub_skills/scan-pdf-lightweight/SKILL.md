---
name: scan-pdf-lightweight
description: Use when you need to reduce scanned PDF size in a .NET app for OCR upload stability, token reduction, or network resilience, especially by rasterizing scan pages and rebuilding an OCR-friendly PDF with a safe fallback path.
---

# Lightweight Scanned PDFs for OCR in .NET

Use this sub-skill when scanned PDFs are too heavy or unstable for OCR upload. The goal is not “compression at any cost”; it is to create an OCR-friendly input PDF while keeping behavior safe through explicit fallback and diagnostics.

## When to Use This Skill

Use this skill when:
- Reducing scanned PDF size before sending it to an OCR service
- Stabilizing OCR uploads that fail on large request bodies or weak networks
- Rebuilding scan PDFs as grayscale JPEG-based OCR input in a .NET application
- Keeping PDF preprocessing inside DDD boundaries without leaking image logic into Application
- Adding tests and diagnostics so lightweighting behavior is observable and safe

## Related Skills

- **`dotnet-pdf`** — Router for PDF-related .NET work
- **`dotnet-ocr-matching-workflow`** — End-to-end OCR workflow that can consume lightweighted PDFs
- **`dotnet-wpf-dify-api-integration`** — OCR API integration on the client side
- **`dotnet-wpf-ocr-parameter-input`** — Future UI surfacing for OCR parameters

## Core Principles

1. **Optimize Input, Not Business Rules** — Lightweighting belongs to Infrastructure; Application asks for OCR-ready chunks and stays orchestration-focused (基礎と型)
2. **Fallback Before Regression** — If the rebuilt PDF is larger than the original chunk, use the original chunk instead (ニュートラル)
3. **TDD Before Tuning** — Lock in chunk behavior, fallback, and diagnostics with tests before changing DPI or JPEG quality (継続は力)
4. **Observe the Result** — Emit diagnostic events that tell operators whether preprocessing was applied or skipped (成長の複利)

## Workflow: Add Scan PDF Lightweighting

### Step 1 — Define the preprocessing contract

Create an OCR preprocessing settings model in Domain and expose a PDF processor contract that can return OCR-ready chunks. Application should request “OCR chunks,” not describe image-processing steps itself.

Example shape:

```csharp
public sealed record OcrPreprocessSettings(
    bool Enabled,
    int TargetDpi,
    bool UseGrayscale,
    int JpegQuality);
```

Why: this keeps policy explicit and testable while preserving DDD boundaries.

### Step 2 — Implement rasterize → encode → rebuild in Infrastructure

Render each PDF page to a bitmap, convert to grayscale if needed, encode as JPEG, and rebuild a temporary OCR PDF. In the project implementation, `PDFtoImage`, `SkiaSharp`, and `PdfSharpCore` form that pipeline well.

Typical flow:

1. Split the source PDF into OCR chunks
2. Render each page at target DPI
3. Encode page images as JPEG
4. Rebuild a temporary PDF from those images
5. Compare size against the original chunk

Why: scanned PDFs often carry bulky image payloads, and controlled re-encoding can reduce upload cost substantially.

### Step 3 — Add safe fallback logic

If the rebuilt OCR PDF is larger than the original chunk, keep the original chunk instead. Also delete temporary `.preprocessed` files on both failure and fallback paths.

Why: lightweighting is an optimization, not a correctness requirement. The fallback path protects reliability.

### Step 4 — Wire OCR-only usage in Application

Use the OCR-ready chunk method only for the OCR upload path. Do not let lightweighting affect final saved pages or unrelated PDF output unless that is explicitly part of the feature.

Why: OCR input optimization and final artifact preservation are different concerns.

### Step 5 — Emit diagnostics

Publish a structured diagnostic result that reports:

- chunk index
- page range
- original vs output size
- DPI
- grayscale on/off
- whether preprocessing was applied or skipped

Why: operators need to confirm what actually happened when debugging OCR upload issues.

### Step 6 — Validate with TDD

Cover at least these tests:

- OCR chunk path uses lightweight preprocessing
- fallback occurs when rebuilt PDF grows
- grayscale output is actually grayscale
- diagnostics report preprocessing result
- final saved single-page extraction path is unchanged

Why: PDF/image changes are easy to “make work once” and hard to keep safe without regression coverage.

## Best Practices

- Prefer explicit settings objects over scattered magic numbers
- Keep image-processing libraries isolated in Infrastructure
- Record preprocessing outcome in structured diagnostics, not only in message strings
- Tune DPI and JPEG quality with a real sample PDF, not guesswork

## Pitfalls

- **Changing final output artifacts unintentionally**: Lightweighting for OCR should not silently alter the later page-save flow.
- **Treating smaller size as always better**: Smaller PDFs can still hurt OCR quality; validate against real scan samples.
- **Skipping cleanup of temporary files**: Rebuilt PDF temp files can accumulate quickly during failures.
- **Baking project-specific constants into the skill title**: Keep the trigger reusable even if the first implementation came from one project.
