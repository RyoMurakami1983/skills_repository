---
name: knowledge-capture
description: >
  Structured knowledge capture with anonymization gate for documents that may
  become public skills or references.
  Use when creating furikaeri, ADR, incident reports, or any document that
  could flow into a public repository.
metadata:
  author: RyoMurakami1983
  tags: [documentation, anonymization, knowledge-management, cross-cutting]
  invocable: false
---

# Knowledge Capture

A cross-cutting utility for capturing knowledge from sessions, incidents, and decisions into structured documents — with an anonymization gate that prevents proprietary data from leaking into public skills and references.

## When to Use This Skill

Use this skill when:
- Creating documents that may later become skill examples (furikaeri, incident reports)
- Converting real project experiences into reusable skill patterns
- Writing ADRs (Architecture Decision Records), learning notes, or post-mortems that reference proprietary systems
- Reviewing existing skill examples for proprietary data leakage
- Any document workflow needs an anonymization quality gate

## Related Skills

- **`furikaeri-practice`** — Retrospective workflow (references this skill's anonymization gate)
- **`skills-author-skill`** — Skill creation (references this skill's anonymization checklist)
- **`skills-revise-skill`** — Skill revision (references this skill's anonymization checklist)
- **`github-issue-intake`** — Capture improvement items as tracked issues

---

## Dependencies

- None required (conversation-only workflow)
- Optional: GitHub CLI (`gh`) for creating improvement issues

## Core Principles

1. **Knowledge Flows Outward** — Write every document as if it will be read outside the project. Internal-only assumptions create leakage risk (ニュートラルな視点)
2. **Anonymize at the Source** — Replace proprietary data during document creation, not after. Retrofitting anonymization is error-prone and costly (基礎と型)
3. **Structured Over Narrative** — Structured documents (tables, checklists, code blocks) are easier to anonymize and reuse than free-form prose (成長の複利)
4. **Preserve Teaching Value** — Anonymization must not destroy the educational point. Choose dummy data that demonstrates the same concept (温故知新)

---

## Workflow: Capture & Gate

### Step 1 — Identify Knowledge Type

Determine the document type and its downstream destination. Use this table to decide whether anonymization is required:

| Type | Primary Skill | Destination | Anonymization Required |
|------|--------------|-------------|----------------------|
| Retrospective | `furikaeri-practice` | `docs/furikaeri/` | Yes (if skill-bound) |
| Architecture Decision | (ADR workflow) | `docs/adr/` | Yes (if public repo) |
| Incident Report | (incident workflow) | `docs/incidents/` | Yes |
| Learning Note | (standalone) | project docs | Context-dependent |

**Decision Rule**: "Could this document's content end up in a public repository?" → Yes = anonymization required.

> **Values**: ニュートラルな視点（前提を明確にし、判断基準を形式知化）

### Step 2 — Write with Structure

Use structured formats that separate facts from proprietary details. Apply tables and code blocks instead of free-form prose:

```markdown
## Good: Structured (easy to anonymize)

| Input | Expected | Actual |
|-------|----------|--------|
| `20240101-MFG001-AL-6XN-H12345` | ProductType=`AL-6XN` | ProductType=`AL` |

## Bad: Narrative (hard to anonymize)

When we processed the OrderProcessor output for order ORD-394072,
the product type X-200-B was incorrectly parsed because...
```

Structured formats make proprietary data visible and replaceable. Narrative buries it in context.

> **Values**: 基礎と型（構造が品質を生む）

### Step 3 — Apply Anonymization Gate

Before outputting the document, apply the **Anonymization Checklist** (AC: Anonymization Check items, see below). This is the critical quality gate.

If the document will be used as a skill example:
1. Apply every item in the Anonymization Checklist
2. Verify the anonymized version still teaches the intended lesson
3. Have a second reader (human or AI) check for residual proprietary data

> **Values**: 基礎と型（ゲートを通さなければ出力しない）

### Step 4 — Route Output

Deliver the document to its destination and link to next actions. Check the routing table and confirm the output path:

| Destination | Action |
|------------|--------|
| `docs/furikaeri/` | Commit, PR, link to improvement issues |
| Skill example | Feed into `skills-author-skill` or `skills-revise-skill` |
| ADR | Commit to `docs/adr/`, update ADR index |
| GitHub Issue | Create via `github-issue-intake` |

> **Values**: 継続は力（知識を正しい場所に届け、次のアクションに繋げる）

---

## Anonymization Checklist

This section is designed to be referenced directly by other skills. Apply each check to any content that may appear in a public repository.

### AC-1: Project and Company Names

**Check**: Does the document contain real project names, company names, or product names?

**Action**: Remove or replace with generic names.

```
❌ "MillScanSplitter PR#20"
✅ (remove project reference entirely, or use "Example:")

❌ "Contoso Steel Division"
✅ "manufacturing division"
```

### AC-2: Data Formats and Identifiers

**Check**: Does the document contain real data values, ID formats, or record structures?

**Action**: Replace with dummy values that preserve the same structural characteristics.

```
❌ "25_10_29-394R072-9#SUH3-AIS-X578D"
✅ "20240101-MFG001-AL-6XN-H12345"
    (preserves: date prefix, hyphen-delimited, embedded hyphens in values)
```

**Key principle**: Dummy data must demonstrate the same edge case. If the real data broke because a value contained a hyphen, the dummy data must also contain a hyphen.

### AC-3: Domain-Specific Terminology

**Check**: Does the document use terminology that reveals the specific industry, client, or internal system?

**Action**: Generalize to industry-neutral terms.

```
❌ "鋼種名" (steel type name), "溶解番号" (heat number)
✅ "製品型番" (product type code), "ロット番号" (lot number)

❌ "SteelType", "HeatNo"
✅ "ProductType", "LotNumber"
```

### AC-4: Numeric Values and Thresholds

**Check**: Does the document contain real measurements, thresholds, or business-specific numbers?

**Action**: Replace with representative dummy values.

```
❌ "Tolerance: ±0.003mm for SUH3 grade"
✅ "Tolerance: ±0.01mm for this product grade"
```

### Decision Rule

> "Could someone reconstruct the original project, client, or proprietary system from this content?"
>
> → **Yes** = Apply AC-1 through AC-4
> → **No** = Content is safe for public use

---

## Good Practices

### 1. Anonymize During Writing, Not After

**What**: Apply anonymization as you write, not as a separate review pass.

**Why**: Retrofitting is error-prone. Writers forget which details are proprietary after the document is complete.

**Values**: 基礎と型（入口で品質を確保する）

### 2. Keep a Dummy Data Palette

**What**: Maintain a small set of reusable dummy values for common patterns (dates, IDs, product codes).

**Why**: Consistent dummy data across skills improves readability and reduces cognitive load.

**Values**: 継続は力（再利用可能な素材を積み上げる）

---

## Common Pitfalls

### 1. Anonymizing Away the Teaching Point

**Problem**: Replacing data so aggressively that the example no longer demonstrates the intended concept.

**Fix**: Choose dummy data that preserves the structural characteristic being taught. If the lesson is "hyphens in values break naive splitting," the dummy value must contain hyphens.

### 2. Partial Anonymization

**Problem**: Replacing the project name but leaving identifiable data formats, class names, or domain terms.

**Fix**: Run through all four AC checks systematically. Proprietary data leaks through combinations, not individual fields.

### 3. Skipping Internal Documents

**Problem**: Assuming internal documents do not need anonymization because "they won't be published."

**Fix**: Apply the decision rule: "Could this content end up in a public repository?" Documents frequently flow from internal records to public skills.

---

## Anti-Patterns

### "Nobody Will See This"

**What**: Skipping anonymization for documents in internal repositories.

**Why It's Wrong**: Knowledge flows outward. Internal furikaeri become skill examples. Internal ADRs become public references. The assumption of privacy is temporary.

**Better Approach**: Anonymize at the source. The cost is minimal; the risk of leakage is permanent.

### Copy-Paste from Production

**What**: Copying real error messages, log outputs, or data samples directly into documentation.

**Why It's Wrong**: Production data contains customer information, internal system names, and proprietary formats.

**Better Approach**: Create synthetic examples that reproduce the same error pattern with dummy data.

---

## Quick Reference

### Anonymization Checklist (Summary)

| # | Check | Action |
|---|-------|--------|
| AC-1 | Project/company names | Remove or use generic names |
| AC-2 | Data formats/IDs | Replace with structurally equivalent dummies |
| AC-3 | Domain terminology | Generalize to industry-neutral terms |
| AC-4 | Numeric values | Use representative dummy values |

### Decision Flow

```
Document created
    │
    ├─ Could content reach a public repo?
    │     │
    │     ├─ Yes → Apply AC-1 through AC-4
    │     │         │
    │     │         └─ Does anonymized version still teach the lesson?
    │     │               │
    │     │               ├─ Yes → ✅ Output
    │     │               └─ No  → Revise dummy data
    │     │
    │     └─ No  → ✅ Output (but consider future flow)
    │
    └─ Feeding into a skill?
          │
          ├─ Yes → MANDATORY: Apply full checklist
          └─ No  → Apply decision rule above
```

---

## Resources

- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- [furikaeri-practice](../furikaeri-practice/SKILL.md) — Retrospective workflow
- [skills-author-skill](../skills-author-skill/SKILL.md) — Skill creation workflow

---
