---
name: evidence-response
description: >
  Build a reusable evidence-response system for recurring business inquiries — audits,
  questionnaires, compliance surveys — using historical evidence archives and structured
  workflows. Use when your organization repeatedly receives the same structured inquiries,
  you need to leverage past responses instead of starting from scratch, or you are setting
  up a new operational domain response capability.
---

# Evidence Response

A template skill for building **evidence-based response systems** in operational domains. When your organization repeatedly receives structured inquiries — audits, questionnaires, compliance surveys — this skill provides the **reusable workflow pattern** and **scaffolding files** to respond accurately using historical evidence.

## When to Use This Skill

- **Responding** to recurring structured inquiries systematically
- **Leveraging** past responses as references instead of starting from scratch
- **Setting up** an evidence-based response system for a new domain
- **Building** a reusable template for domain knowledge and history

**Do NOT use when:**

- ❌ Handling a one-time unique request with no recurring pattern
- ❌ Responding without needing evidence or historical references
- ❌ A domain-specific skill already exists — use it instead

---

## Decision Table

| Current situation | Action | Start at |
|---|---|---|
| **First time** setting up evidence-response | Copy templates, define taxonomy | Setup Checklist |
| **New inquiry** received for existing domain | Run the 7-step workflow | Step 1 |
| **Similar question** answered before | Search response index first | Step 4 |
| **Annual review** date reached | Run freshness protocol | Freshness Management |
| **New domain** to add | Create new instance from templates | Scaffolding Files |
| **One-off inquiry** with no recurring pattern | ❌ Do NOT use this skill | — |

---

## Related Skills

- **`knowledge-capture`** — Structured capture and anonymization of domain knowledge before building evidence archives
- **`git-commit-practices`** — Version-controlled evidence archive management with meaningful commit history
- **`furikaeri-practice`** — Post-response retrospective to improve the response process

---

## Core Principles

1. **Evidence over Memory** — Document responses; recall is unreliable
2. **Structured Classification** — Categorize inquiries for consistent handling
3. **Intentional Blank Space** — Structure provided; domain knowledge is yours to fill
4. **Cumulative Knowledge** — Each response compounds the archive's value
5. **Annual Freshness** — Scheduled review prevents knowledge decay

| Principle | Value Alignment | Why It Matters |
|---|---|---|
| Evidence over Memory | 温故知新 (Onko Chishin) | Past documented responses beat recalled answers |
| Structured Classification | 基礎と型 (Kiso to Kata) | Categorizing enables repeatable responses |
| Intentional Blank Space | 余白の設計 (Yohaku no Sekkei) | Template provides structure; you fill the gaps |
| Cumulative Knowledge | 成長の複利 (Seicho no Fukuri) | Each response makes the next one faster |
| Annual Freshness | 継続は力 (Keizoku wa Chikara) | Scheduled review prevents knowledge decay |

---

## Dependencies

| Dependency | Purpose |
|---|---|
| **Git** | Version control for knowledge base and response index |
| **GitHub Copilot** (Claude recommended) | Long-context knowledge retrieval and structured reasoning |
| **`knowledge-base-template.md`** | Domain knowledge structure (included in `references/`) |
| **`response-index-template.md`** | Response history archive (included in `references/`) |

---

## Scaffolding Files

| File | Purpose |
|---|---|
| [`knowledge-base-template.md`](references/knowledge-base-template.md) | Domain knowledge — copy and fill with your requirements |
| [`response-index-template.md`](references/response-index-template.md) | Response archive — copy and record every response |

### Setup Checklist

1. ✅ Copy template files to `.github/skills/<your-domain>/references/`
2. ✅ Define inquiry **classification taxonomy** (Step 1)
3. ✅ Map **domain requirements** to evidence documents
4. ✅ Record **first response** in the response index
5. ✅ Set **annual freshness** review date

---

## Workflow: Evidence-Based Response Generation

### Step 1: Receive and Classify

> Use when a new inquiry arrives. Why: Classification enables consistent downstream handling.

Classify the inquiry using your domain's taxonomy. Define taxonomy by identifying **recurring types**:

| Field | Description | Example |
|---|---|---|
| Type ID | Short uppercase identifier | `AUDIT`, `SURVEY`, `CERT-CHECK` |
| Name | Descriptive name | External System Audit |
| Source | Typical sender | Certification body |
| Complexity | Low / Medium / High | Based on response effort |

```
# Why: Every inquiry must map to exactly one type for consistent handling
New inquiry received
  ├─ Formal audit?           → AUDIT
  ├─ Questionnaire/survey?   → SURVEY
  ├─ Certificate request?    → CERT-CHECK
  ├─ Compliance inquiry?     → COMPLIANCE
  └─ No match?               → Flag for taxonomy expansion
```

- ❌ **Bad**: Classify later after drafting — leads to inconsistent structure
- ✅ **Good**: Classify first, then draft — taxonomy drives the response format

> **Values**: Kiso to Kata — Classification is the foundation. Without it, responses are ad-hoc.

### Step 2: Decompose and Map to Requirements

> Use when inquiry contains multiple questions. Why: Mapping ensures no question is missed and reveals shared evidence.

Break the inquiry into individual questions. Map each to your requirement framework — e.g., ISO (International Organization for Standardization) standards, IATF (International Automotive Task Force) clauses, or internal procedures.

```markdown
<!-- Why: Per-question status tracking prevents gaps in the final response -->
| Q# | Summary | Requirement | Evidence | Status |
|----|---------|-------------|----------|--------|
| Q1 | "Describe calibration procedure" | ISO 9001 §7.1.5 | Procedure Rev.N | ✅ Current |
| Q2 | "Provide traceability evidence" | IATF 16949 §7.1.5.3 | Record FY2025 | ⚠️ Needs update |
```

Use `knowledge-base.md` for the mapping. Flag unmapped questions for investigation.

- ❌ **Bad**: Answer questions in received order without mapping
- ✅ **Good**: Map all questions first, then identify shared evidence

> **Values**: Onko Chishin — The knowledge base is your accumulated wisdom.

### Step 3: Draft Responses from Knowledge Base

> Use when questions are mapped to requirements. Why: Evidence-cited drafts prevent opinion-based answers.

For each mapped question, draft a response using knowledge base content.

```markdown
<!-- Why: Consistent structure enables quality review across all responses -->
**Question**: [Original question text]
**Classification**: [Type ID] — [Requirement reference]
**Response**:
[Evidence-based answer referencing specific documents and versions]

**Evidence**: [Document name, version, date]
**Confidence**: High / Medium / Low
```

- **High**: Direct evidence exists, document is current
- **Medium**: Evidence exists but may need updating
- **Low**: No direct evidence — flag for review

> **Values**: Kiso to Kata — Consistent response structure enables quality review.

### Step 4: Locate Historical References

> Use when drafting responses. Why: Past answers provide tested language and prevent contradictions.

Search the response index for past answers to similar questions.

**Search strategy** — check in this order:

1. By **inquiry type** — find past responses of same classification
2. By **question keyword** — find similar questions across all types
3. By **sender** — check consistency with previous responses to same organization
4. By **date** — prefer recent responses as references

```markdown
<!-- Why: Linking to past responses enables consistency verification -->
**Historical reference**: [Year]-[Month] | [Sender] | [Type]
**Source file**: [Folder path and filename]
**Relevance**: [Why this past response applies to the current question]
```

> **Values**: Onko Chishin — Past responses are your most valuable asset.

### Step 5: Verify Evidence Currency

> Use when finalizing response drafts. Why: Outdated evidence damages credibility and may cause compliance issues.

Verify that all referenced evidence documents are still current.

```markdown
<!-- Why: Currency verification prevents sending outdated evidence -->
| Document | Expected ver. | Actual ver. | Status |
|----------|--------------|-------------|--------|
| Procedure A | Rev.5 (KB) | Rev.5 (verified) | ✅ Current |
| Traceability Record | FY2025 (KB) | FY2024 (actual) | ❌ Outdated |
| Calibration Cert | 2025-01 | 2025-01 | ✅ Current |
```

**Action on failure:**

| Check | Action |
|---|---|
| Version mismatch | Update knowledge base to latest version |
| Beyond freshness period | Flag for review; note gap in response |
| Standard superseded | Check for replacement standard |
| Procedure changed | Verify with document owner |

- ❌ **Bad**: Skip currency check for "obvious" answers — outdated evidence persists
- ✅ **Good**: Verify every referenced document, every time — no exceptions

> **Values**: Keizoku wa Chikara — Evidence currency is non-negotiable.

### Step 6: Apply Confidentiality Masking

> Use when preparing responses for external sharing. Why: Protecting confidential information prevents legal and business risk.

Apply your organization's confidentiality rules before sharing externally. Define masking rules in your knowledge base.

```markdown
<!-- Why: Consistent masking prevents accidental disclosure -->
| Category | Rule | Before | After |
|----------|------|--------|-------|
| Customer terms | Generalize | "Customer X's format" | "the customer's format" |
| Internal forms | Redact | "Form K-1234" | "internal form" |
| Personnel | Remove names | "Reviewed by Tanaka" | "Reviewed by authorized personnel" |
| Proprietary methods | Summarize | "Our XYZ process..." | "An established process..." |
```

**Do NOT mask** references to public standards — ISO, IATF, JIS (Japanese Industrial Standards), etc. — or general procedure descriptions approved for external use.

> **Values**: Yohaku no Sekkei — Confidentiality rules create intentional boundaries.

### Step 7: Review and Finalize

> Use when all responses are drafted and masked. Why: Final quality gate prevents errors from reaching the recipient.

Run the final quality check before submission.

```markdown
<!-- Why: Checklist prevents common omissions in final responses -->
## Final Review
- [ ] Every question has a response (no blanks)
- [ ] Evidence documents cited with version and date
- [ ] Historical references noted where applicable
- [ ] Confidentiality masking applied consistently
- [ ] Response tone matches inquiry formality
- [ ] No out-of-scope claims (flagged items escalated)
- [ ] Response index updated with this new entry
```

**Out-of-scope protocol** — if a question falls outside your domain:

1. **Flag** clearly — do not attempt to answer
2. **Assess** — adjacent to your domain or completely unrelated?
3. **Escalate** — route to the responsible department
4. **Never fabricate** — "outside our scope" beats a guess every time

> **Values**: Kiso to Kata — Quality gates prevent errors from propagating.

---

## Freshness Management

**Trigger conditions** (any one triggers a review):

1. ✅ Freshness interval (default: 365 days) elapsed since last update
2. ✅ A referenced standard or regulation has been revised
3. ✅ Internal procedures significantly updated
4. ✅ A response revealed a knowledge gap

**Annual review checklist:**

- [ ] All evidence documents in knowledge base are current
- [ ] Response index includes all inquiries from the past year
- [ ] Classification taxonomy covers incoming inquiry types
- [ ] Masking rules match current confidentiality requirements
- [ ] New recurring patterns added as types
- [ ] `metadata.created` date refreshed in frontmatter

> **Values**: Keizoku wa Chikara — Annual maintenance prevents knowledge decay.

---

## Best Practices

- ✅ **Start with one domain** — get it working, then expand
- ✅ **Record every response** in the index, even quick ones. Why: Compound value requires completeness
- ✅ **Use Claude** for knowledge retrieval. Why: Long-context structured reasoning matches this workflow
- ✅ **Keep files in `.github/skills/`** — use `git-ops-folder-init` for directory-based tracking
- ✅ **Review with your team annually**. Why: Multiple perspectives strengthen the knowledge base
- ✅ **Link template to domain implementations** — the template is the form; each domain is a concrete application

---

## Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| Updating knowledge base but not the response index | Responses reference outdated entries | ✅ Update both simultaneously |
| Using knowledge base as the only search target | Miss relevant answers in response history | ✅ Search both knowledge base AND response index |
| Mixing classification types in a single response | Inconsistent format confuses reviewers | ✅ One response per type; split if needed |
| Masking too aggressively | Response becomes uninformative | ✅ Mask only what confidentiality rules require |
| Skipping currency check for "obvious" answers | Outdated evidence persists undetected | ✅ Verify every document, every time |

---

## Anti-Patterns

| ❌ Don't | ✅ Do Instead | Why |
|----------|--------------|-----|
| Copy-paste old responses without checking currency | Verify evidence versions before reuse | Outdated evidence damages credibility |
| Skip the response index for "quick" replies | Record every response, however brief | Compound value depends on completeness |
| Answer questions outside your scope | Flag, escalate, and document the gap | Fabricated answers create liability |
| Store knowledge only in someone's head | Document in `knowledge-base.md` with links | Tacit knowledge doesn't survive personnel changes |
| Create types for one-off inquiries | Only add types for recurring patterns (3+) | Over-classification adds noise |
| Ignore the annual freshness review | Schedule it and complete the checklist | Knowledge decay is invisible until a wrong answer ships |

---

## Implementation Example

An IATF 16949 internal laboratory questionnaire response skill demonstrates this template applied to calibration quality management:

- ✅ 5-type classification taxonomy (AUDIT, CAL-EVAL, CAL-CERT, IATF-GEN, STD-SAMPLE)
- ✅ Knowledge base mapped to IATF 16949 §7.1.5.3 sub-requirements
- ✅ Response index with 37+ historical entries spanning 8 years
- ✅ 3-tier confidentiality masking (internal, external, audit)
- ✅ Annual freshness management aligned with audit cycles

Use it as a reference when creating your own domain-specific implementation.

---

## FAQ

**Q: How many responses before this template becomes useful?**
A: Even 1 recorded response has reference value. Compound benefit becomes obvious after 10+.

**Q: Can I use this for non-audit inquiries?**
A: Yes. Any recurring structured inquiry — customer surveys, regulatory questionnaires, internal audits — fits.

**Q: What if my domain has no formal standards?**
A: Use internal procedures or policies as the requirement framework. External standards are not required.

**Q: How do I handle multilingual inquiries?**
A: Record the original language in the response index. Maintain the knowledge base in your primary working language.

**Q: Should I version-control these files?**
A: Yes. Use `git-ops-folder-init` for directory-based tracking with change history and rollback.

---

## Quick Reference

### Response Workflow (7 Steps)

1. **Receive & Classify** → inquiry type assigned
2. **Decompose & Map** → requirement references identified
3. **Draft from Knowledge Base** → evidence-cited responses
4. **Search Response Index** → historical precedents found
5. **Verify Evidence Currency** → document versions confirmed
6. **Apply Confidentiality Masking** → external-safe content
7. **Review & Finalize** → quality gate passed, index updated

### Scaffolding Files

- `knowledge-base-template.md` → domain knowledge + evidence registry + masking rules
- `response-index-template.md` → response archive + taxonomy + statistics
