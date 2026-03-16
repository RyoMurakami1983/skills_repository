---
name: dotnet-pdf
description: Use when you need to route a .NET PDF-related task to the right skill, such as scan PDF lightweighting, WPF PDF preview, OCR input optimization, or future PDF split/crop workflows.
---

# Route .NET PDF Workflows to the Right Skill

Router skill for .NET PDF work. Keep this skill thin: it classifies the request, points to the correct sibling or sub-skill, and avoids duplicating detailed implementation guidance.

## When to Use This Skill

Use this skill when:
- Routing a PDF-related .NET request to the correct implementation skill
- Choosing whether a request is about lightweighting, preview, split, crop, or OCR input preparation
- Starting a new PDF capability without wanting to overload an existing WPF-only skill
- Expanding PDF know-how as a family of reusable .NET skills over time

## Decision Table

| Request shape | Route | Why |
| --- | --- | --- |
| OCR upload is unstable because scan PDFs are heavy | `sub_skills/scan-pdf-lightweight` | This is input optimization, not UI work |
| Need inline PDF display in WPF | `dotnet-wpf-pdf-preview` | Existing project skill already covers preview well |
| Need full OCR-to-matching workflow wiring | `dotnet-ocr-matching-workflow` | End-to-end orchestration already exists |
| Need future PDF split/crop/normalize guidance | Add a new `sub_skills/` entry under `dotnet-pdf` | Keep PDF concerns grouped without bloating one skill |

## Related Skills

- **`dotnet-ocr-matching-workflow`** — End-to-end OCR pipeline orchestration
- **`dotnet-wpf-pdf-preview`** — WPF upload and inline PDF preview
- **`dotnet-wpf-ocr-parameter-input`** — OCR execution parameter UI in WPF
- **`skill`** — Meta-router for creating and improving skills

## Core Principles

1. **Route, Don't Re-Explain** — The router points to the right skill instead of repeating long implementation detail (ニュートラル)
2. **Keep PDF Concerns Cohesive** — Shared PDF know-how belongs in one family, but each concrete behavior gets its own sub-skill (基礎と型)
3. **Prefer Existing Skills First** — Reuse `dotnet-wpf-pdf-preview` and workflow skills before creating overlapping content (温故知新)
4. **Promote Proven Patterns** — Start sub-skills from project-proven implementations rather than generic speculation (継続は力)

## Workflow: Route a .NET PDF Request

### Step 1 — Classify the request

Decide whether the user is asking for UI preview, OCR input optimization, PDF transformation, or full workflow wiring. The router should stay short because the detailed guidance belongs elsewhere.

### Step 2 — Check for an existing skill

If an existing project skill already solves the request, route there. This avoids forking the same guidance into multiple places and keeps maintenance cost low.

### Step 3 — Use or add a focused sub-skill

If the request is truly a PDF-domain concern not covered elsewhere, use a `sub_skills/` entry under `dotnet-pdf`. Each sub-skill should own one coherent behavior, such as scan PDF lightweighting.

### Step 4 — Preserve layer and runtime assumptions

When routing to implementation skills, keep DDD boundaries and platform assumptions visible. For this repository, PDF transformation guidance should fit .NET + DDD + WPF usage without leaking UI logic into Domain or Application layers.

## Active Sub-Skills

- **`scan-pdf-lightweight`** — Reduce scanned PDF size for OCR upload stability while preserving a safe fallback path

## Pitfalls

- **Making the router too smart**: If the router contains full implementation detail, it stops being a router and becomes hard to evolve.
- **Duplicating WPF preview guidance**: Route preview work to `dotnet-wpf-pdf-preview` instead of maintaining two PDF preview explanations.
- **Creating broad “PDF everything” skills**: PDF tasks differ a lot; keep each sub-skill tightly scoped so triggers stay sharp.
