# Skill Quality Levels

Use this file as the single source of truth for validation.

## Critical Checks

All Critical checks must pass before a skill is treated as shippable.

| ID | Check | Why it matters |
| --- | --- | --- |
| C1 | Frontmatter includes `name` and `description` | Activation depends on metadata being present and parseable. |
| C2 | `name` matches the directory name | Stable lookup depends on `name` and directory staying aligned. |
| C3 | `description` includes `Use when` triggers | Discovery fails when the trigger surface is vague. |
| C4 | `## When to Use This Skill` exists | Readers need fast relevance judgment after activation. |
| C5 | A workflow or router section exists with explicit steps or routes | The skill must tell the agent what to do next. |

## Recommended Checks

Recommended checks improve clarity, reuse, and long-term maintainability.

| ID | Check | Why it matters |
| --- | --- | --- |
| R1 | "When to Use" contains 3-8 bullets | Too few misses intent space; too many diffuses focus. |
| R2 | Each scenario starts with an action verb | Verb-led bullets are easier to match to user intent. |
| R3 | The skill explains why, not only what | WHY-oriented guidance generalizes better than rigid rules. |
| R4 | `## Pitfalls` exists | Failure modes should be explicit, not tribal knowledge. |
| R5 | Main `SKILL.md` stays compact | Keep hot-path context small and push overflow to `references/`. |
| R6 | Overflow detail moves to `references/` when needed | Large bodies should be loaded on demand. |
| R7 | Related resources or sibling skills are linked | Cross-navigation reduces duplicated explanation. |
| R8 | Quick reference or decision table exists when operations are multi-step | Operators need a fast execution view. |
| R9 | Code or command examples are syntactically valid | Broken examples erode trust immediately. |
| R10 | `references/SKILL.ja.md` exists when the skill is intended for bilingual use | Japanese guidance helps team adoption without forcing every skill to duplicate effort. |

## Validation Levels

| Level | Scope | Expected use |
| --- | --- | --- |
| L1 | Critical checks only | Draft gate after initial authoring |
| L2 | Critical + Recommended | Review gate before broad use |
| L3 | Governance and enterprise review | Team or organization rollout |
| L4 | Behavioral eval pipeline | Important skills where trigger quality must be measured |
