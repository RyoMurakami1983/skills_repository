---
name: <context>-<verb>-<object>
description: >
  <What this skill does>. Use when <scenario 1>, <scenario 2>, or
  <scenario 3>, even if the user describes the workflow without saying
  "skill".
compatibility: <optional tools, runtime, or platform constraints>
---

# <Skill Title>

<Explain why this skill exists in 1-2 sentences.>

## When to Use This Skill

Use this skill when:
- <Verb-led scenario 1>
- <Verb-led scenario 2>
- <Verb-led scenario 3>

## Workflow: <Workflow Name>

### Step 1 — <Action>
Explain what to do, why it matters, and show one short example.

### Step 2 — <Action>
Explain what to do next, why it matters, and what can go wrong.

## Pitfalls

- **<Pitfall>**: <How to avoid it and why the safer choice works better.>

## Bundled Resources

Use this directory shape when the skill needs reusable assets:

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

- `scripts/`: deterministic helper code worth reusing
- `references/`: overflow documentation loaded only when needed
- `assets/`: files embedded into outputs such as HTML or templates
