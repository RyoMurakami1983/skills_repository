# Skill Conventions

Use these conventions to keep `skills/skill/` coherent and predictable.

## Naming

- Use kebab-case.
- Prefer `<context>-<verb>-<object>` for top-level skills.
- Internal sub-skills may use short names when the directory is nested under a router.

## Frontmatter

- Required: `name`, `description`
- Optional: `compatibility`
- `description` should be trigger-oriented and include `Use when`
- `compatibility` should only describe real constraints such as required tools or platform assumptions

## Directory Rules

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

- `SKILL.md` is the primary execution guide.
- `references/` stores overflow docs or localized variants.
- `scripts/` holds deterministic helpers that the agent would otherwise rewrite repeatedly.
- `assets/` stores files consumed by outputs, not explanatory prose.

## Progressive Disclosure

| Level | Content | Rule |
| --- | --- | --- |
| L1 | frontmatter | Keep it short and trigger-rich. |
| L2 | `SKILL.md` body | Keep the hot path compact and readable. |
| L3 | bundled resources | Load only when needed. |

## Writing Style

- Explain why the step exists instead of shouting MUST/NEVER repeatedly.
- Use imperative prose so the next action is obvious.
- Write like you are teaching a capable teammate.
- Add a table of contents to large reference files.

## Safety

- Do not package malware, exploit instructions, or security-bypass guidance as reusable skills.
- Prefer least-surprise workflows that surface risks before destructive actions.
