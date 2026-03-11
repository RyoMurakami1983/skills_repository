# Business Evidence Response — Deep Knowledge

## Evidence Archive Structure

A mature evidence archive follows this directory pattern:

```
domain-name/
├── .github/        # CI, issue templates
├── knowledge-base.md   # Domain taxonomy and facts
├── response-index.md   # Searchable log of past responses
└── responses/
    ├── YYYY/
    │   └── inquiry-name.md  # Actual response records
    └── templates/
        └── standard-response.md
```

## Taxonomy Design Principles

When defining your inquiry taxonomy (categories):
1. **Exhaustive but minimal** — Every inquiry fits exactly one category
2. **Stable over time** — Category names don't change yearly
3. **Action-oriented** — Names suggest who handles it (quality, safety, env)

## Freshness Management

Annual review cadence (余白の設計):
- Q1: Review response-index for gaps
- Q2: Update knowledge-base with organizational changes
- Q4: Validate taxonomy still covers all inquiry types

## Evidence Quality Scoring

Rate each evidence item on 3 axes:
- **Recency** (1-5): How recently was this evidence verified?
- **Specificity** (1-5): Exact data or general claim?
- **Traceability** (1-5): Can you find the original source?

High-quality evidence: total ≥ 10 points
