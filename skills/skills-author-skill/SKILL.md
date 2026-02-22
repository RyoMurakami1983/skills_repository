---
name: skills-author-skill
description: >
  Write a new SKILL.md from scratch following Agent Skills best practices.
  Use when creating a new skill and deciding the right pattern (workflow,
  cycle, situational/router, cascade, parallel, or multi-MCP), defining
  trigger-focused frontmatter, and structuring bilingual documentation.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, authoring, documentation]
  invocable: false
---

# Author a New Agent Skill

End-to-end workflow for writing a high-quality SKILL.md that follows the "1 skill = 1 pattern" principle, passes quality validation, and integrates with the development constitution (PHILOSOPHY.md).

## When to Use This Skill

Use this skill when:
- Creating a brand-new SKILL.md for a GitHub Copilot / Claude / Codex agent
- Learning the required structure and sections for a single-workflow skill
- Writing clear "When to Use" scenarios and Core Principles
- Ensuring compliance with the 500-line limit and references/ overflow strategy
- Integrating development Values (基礎と型, 成長の複利, etc.) into a skill
- Setting up bilingual support (English SKILL.md + Japanese references/SKILL.ja.md)

---

## Related Skills

- **`skills-validate-skill`** — Validate the finished skill against quality criteria
- **`skills-refactor-skill-to-single-workflow`** — Convert legacy multi-pattern skills
- **`skills-revise-skill`** — Revise and optimize discoverability after publishing

---

## Core Principles

1. **One Skill = One Pattern** — A skill should teach one executable pattern (workflow/cycle/router/etc.), not a topic dump (基礎と型)
2. **Concise is Key** — The context window is a public good; keep essential guidance in SKILL.md and move deep details to `references/` (余白の設計)
3. **Reader-First Design** — Enable readers to determine relevance within 5 seconds (ニュートラル)
4. **Set Degrees of Freedom** — Choose strictness based on fragility: low for error-prone operations, high for context-dependent tasks (基礎と型)
5. **Values Integration** — Every skill connects to PHILOSOPHY.md Values; cite at least 2 including `余白の設計` where relevant (成長の複利)

---

## Workflow: Author a New Skill

### Step 1 — Define Metadata (YAML Frontmatter)

Choose a name following the `<context>-<workflow>` convention (kebab-case, verb-led workflow, ≤ 64 chars).

```yaml
---
name: <context>-<verb>-<object>
description: <what it does>. Use when <activation scenario>. # ≤ 1024 chars
metadata:
  author: RyoMurakami1983
  tags: [tag1, tag2, tag3]   # 3-5 technology-focused tags
  invocable: false
---
```

**Naming examples**:

| Context | Workflow | Full Name |
|---------|----------|-----------|
| `git` | `protect-main` | `git-protect-main` |
| `github` | `review-pr` | `github-review-pr` |
| `skills` | `author-skill` | `skills-author-skill` |
| `dotnet` | `apply-mvvm` | `dotnet-apply-mvvm` |

**Rules**:
- `name` must equal directory name
- `description` includes concrete "Use when..." triggers (this is used for skill activation)
- Use only standard top-level keys: `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`
- Place custom fields (`author`, `tags`, `invocable`) under `metadata`

> **Values**: 基礎と型（フロントマターが発動のトリガー）

### Step 2 — Generate Initial Skeleton (Integrated)

Choose one scaffold method and create a minimal structure before writing:

```
<skill-name>/
├── SKILL.md
└── references/
    └── SKILL.ja.md
```

Scaffold options:
- Manual copy from this skill's section order template
- Script generation (if available in your environment)
- AI-assisted skeleton generation, then immediate placeholder replacement

> **Values**: 余白の設計（骨格を先に作り、中身を後から充填）

### Step 3 — Write "When to Use This Skill"

This must be the **first H2 section** after the title. Write 5–8 specific, action-oriented scenarios.

```markdown
## When to Use This Skill

Use this skill when:
- <Verb>-led scenario 1 (specific and concrete)
- <Verb>-led scenario 2
- ...
```

**Checklist**:
- ✅ Each item starts with a verb (Building, Implementing, Designing)
- ✅ Each item is 50–100 characters
- ❌ No abstract phrases ("When you want quality code")
- ❌ No more than 8 items

**Important**: `description` is the trigger surface for activation; this section is loaded after activation and serves as execution-time guidance.

> **Values**: ニュートラル（5秒で判断可能な形式知化）

### Step 4 — Define Core Principles (3–5)

Connect each principle to at least one PHILOSOPHY Value.

```markdown
## Core Principles

1. **Principle Name** — Short explanation (Value名)
2. **Principle Name** — Short explanation (Value名)
3. **Principle Name** — Short explanation (Value名)
```

Available Values: 基礎と型 / 成長の複利 / 温故知新 / 継続は力 / ニュートラル / 余白の設計

> **Values**: 成長の複利（Valuesとの接続が複利的成長を生む）

### Step 5 — Choose and Write One Pattern

Select one pattern that matches the task, then write the skill around that single pattern.

| Pattern | Use when | Typical structure |
|---|---|---|
| Sequential Workflow | Ordered steps with low branching | `## Workflow:` + `### Step N` |
| Cycle/Loop | Iterative improve-validate-fix flow | loop stages + exit criteria |
| Situational/Router | Decision-based branching by context | decision table + routes |
| Cascade | Progressive refinement through stages | stage-by-stage filters |
| Parallel | Independent subtasks can run concurrently | split/merge workflow |
| Multi-MCP | Multiple external systems/agents coordinate | orchestration + contracts |

```markdown
## Workflow: <Workflow Name>

### Step 1 — <Action>
Explanation + example

### Step 2 — <Action>
Explanation + example

### Step 3 — <Action>
Explanation + example
```

**Code example conventions**:
- ✅ Use `// ✅ CORRECT - Reason` and `// ❌ WRONG - Reason` markers
- ✅ Include import/using statements
- ✅ Inline examples ≤ 15 lines; longer examples go to `references/`
- ✅ Comments explain WHY, not WHAT

> **Values**: 基礎と型（1パターンの型を徹底）

### Step 6 — Add Good Practices & Pitfalls

```markdown
## Good Practices

### 1. Practice Title
**What**: Brief description.
**Why**: Rationale tied to a Value.
**Values**: Value名

## Common Pitfalls

### 1. Pitfall Title
**Problem**: What goes wrong.
**Solution**: How to fix it.
```

> **Values**: 温故知新（過去の失敗知を形式知化）

### Step 7 — Add Quick Reference & Resources

```markdown
## Quick Reference
[Checklist, decision tree, or summary table]

## Resources
- [Link 1](url) - Description
- [Link 2](url) - Description
```

> **Values**: ニュートラル（即座に参照可能な普遍的リファレンス）

### Step 8 — Manage File Size

If SKILL.md exceeds ~450 lines, proactively move content to `references/`:

```
my-skill/
├── SKILL.md                    # ≤ 500 lines (English, primary)
└── references/
    ├── SKILL.ja.md             # Japanese version
    ├── advanced-examples.md    # Detailed examples
    └── anti-patterns.md        # Extended anti-patterns
```

> **Values**: 余白の設計（コンテキストウィンドウの余白を守る）

### Step 9 — Create Japanese Version

Create `references/SKILL.ja.md` with identical structure. The Japanese version may include deeper "Why" explanations.

> **Values**: 継続は力（バイリンガル対応でアクセシビリティを維持）

### Step 10 — Validate

Run `skills-validate-skill` to check against quality criteria. Target ≥ 80% overall, ≥ 80% per category.

> **Values**: 基礎と型（品質基準で型を検証）

---

## Good Practices

### 1. Start with "When to Use" for Quick Discovery

**What**: Place "When to Use This Skill" as first H2 with 5–8 specific scenarios.

**Why**: Enables 5-second relevance check; improves AI agent discoverability.

**Values**: ニュートラル（形式知化で誰もが理解可能）

### 2. Use ✅/❌ Markers Consistently

**What**: Prefix code with `// ✅ CORRECT - Reason` or `// ❌ WRONG - Reason`.

**Why**: Eliminates ambiguity; enables contrast learning.

**Values**: 基礎と型（明確なパターン）/ 成長の複利（対比学習）

### 3. Explain WHY in Comments

**What**: Comments describe rationale, not syntax.

**Why**: Transforms 暗黙知 into 形式知; supports compound learning growth.

**Values**: 成長の複利（学習資産化）/ ニュートラル（形式知化）

### 4. Keep SKILL.md Under 500 Lines

**What**: Move advanced content to `references/` when approaching the limit.

**Why**: Maintains AI context efficiency; reduces cognitive load.

**Values**: 基礎と型（最小形式で最大可能性）

---

## Common Pitfalls

### 1. Stuffing Multiple Workflows into One Skill

**Problem**: Including 7–10 numbered `## Pattern N:` sections that are really separate workflows.

**Solution**: Each skill = one workflow. Split independent workflows into separate skills.

```markdown
❌ WRONG: One skill with Pattern 1: Setup, Pattern 2: Validate, Pattern 3: Deploy
✅ CORRECT: Three skills — setup-X, validate-X, deploy-X
```

### 2. Vague "When to Use" Scenarios

**Problem**: Abstract scenarios like "When you want better code quality".

**Solution**: Specific, verb-led: "Validating SKILL.md structure against 64-item checklist".

### 3. Missing Values Integration

**Problem**: Core Principles have no connection to PHILOSOPHY.md.

**Solution**: Each principle cites at least one Value in parentheses.

### 4. Exceeding 500-Line Limit

**Problem**: SKILL.md grows beyond 550 lines without using `references/`.

**Solution**: Move detailed examples, anti-patterns, and Japanese content to `references/`.

---

## Anti-Patterns

### Kitchen-Sink Skill

**What**: A single skill that tries to cover an entire domain (e.g., "everything about WPF").

**Why It's Wrong**: Exceeds line limits, impossible for agents to activate precisely, hard to maintain.

**Better Approach**: Split by workflow — one skill per independently executable task.

### Copy-Paste Without Adaptation

**What**: Generating a template and publishing without filling placeholders or adapting to context.

**Why It's Wrong**: Placeholders confuse agents; generic content provides no value.

**Better Approach**: Generate/prepare a skeleton in Step 2, then fill every section with domain-specific content.

---

## Quick Reference

### Skill Authoring Checklist

- [ ] YAML frontmatter: name, description (with "Use when..."), metadata(author/tags/invocable)
- [ ] `name` matches directory name, follows `<context>-<workflow>` convention
- [ ] "When to Use This Skill" is first H2 (5–8 verb-led scenarios)
- [ ] Core Principles (3–5) with ≥ 2 Values references
- [ ] Single workflow section with sequential steps
- [ ] Code examples use ✅/❌ markers, explain WHY
- [ ] Good Practices section with Values links
- [ ] Common Pitfalls (3–5 items)
- [ ] Anti-Patterns (2–3 items)
- [ ] Quick Reference (checklist or decision tree)
- [ ] Resources section
- [ ] SKILL.md ≤ 500 lines
- [ ] `references/SKILL.ja.md` exists (Japanese version)
- [ ] Validated with `skills-validate-skill`

### Section Order

```
1. YAML Frontmatter
2. # Title
3. Introduction (1-2 sentences)
4. ## When to Use This Skill
5. ## Related Skills
6. ## Core Principles
7. ## Workflow: <Name>
8. ## Good Practices
9. ## Common Pitfalls
10. ## Anti-Patterns
11. ## Quick Reference
12. ## Resources
13. (No changelog section; use git history)
```

---

## Resources

- [GitHub Copilot Agent Skills Documentation](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Agent Skills Specification](https://agentskills.io/specification)
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — Quality validation

---
