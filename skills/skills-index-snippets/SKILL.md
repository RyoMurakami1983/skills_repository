---
name: skills-index-snippets
description: >
  Create and maintain AGENTS.md / CLAUDE.md snippet indexes that route
  coding assistant tasks to the correct skills and agents. Use when
  adding, removing, or updating skills in a repository index.
metadata:
  author: RyoMurakami1983
  tags: [skills, routing, agents, index]
  invocable: false
---

# Maintaining Skill Index Snippets

Create compact router snippets for AGENTS.md / CLAUDE.md that direct coding assistants to invoke the correct skill by ID (Identifier) instead of guessing.

## When to Use This Skill

Use this skill when:
- Adding a new skill or agent to the registry and updating routing entries
- Removing or renaming skills and synchronizing all downstream index snippets
- Creating a compact AGENTS.md router block for a downstream repository
- Implementing compressed Vercel-style index format for minimal context use
- Validating that snippet routing IDs match frontmatter name fields exactly
- Regenerating index snippets after batch changes to plugin.json registry

---

## Related Skills

| Skill | Relationship | Invoke When |
|-------|-------------|-------------|
| **`skills-author-skill`** | Author new skills that need index entries | Creating a new skill |
| **`skills-validate-skill`** | Validate skills referenced in snippets | Checking quality gates |
| **`skills-revise-skill`** | Revise skills and update routing metadata | Updating published skills |

---

## Core Principles

1. **Router, Not Documentation** — Snippets direct assistants to the right skill; they do not teach content (余白の設計)
2. **Single Source of Truth** — The registry file is canonical; snippets are derived, not primary artifacts (基礎と型)
3. **ID-Based Referencing** — Always use frontmatter `name` fields as identifiers, never filesystem paths (基礎と型)
4. **Minimal Context Footprint** — Keep snippets small to preserve the assistant's context window budget (余白の設計)
5. **Automated Maintenance** — Prefer scripted regeneration over manual editing to reduce drift (継続は力)

---

## Workflow: Create and Maintain Index Snippets

### Step 1 — Identify the Source of Truth

Locate the canonical registry that lists all skills and agents.

```jsonc
// plugin.json — canonical skill registry
// Use this as the single authority for routing
{
  "skills": [
    { "directory": "modern-csharp-coding-standards" },
    { "directory": "efcore-patterns" }
  ],
  "agents": [
    { "file": "agents/dotnet-concurrency-specialist.md" }
  ]
}
```

- Use plugin.json or equivalent as the canonical registry
- Define the registry location before writing any snippet

**Why**: Every routing index must trace back to one registry. Without a single source of truth, snippets diverge from actual skill availability and assistants invoke nonexistent skills.

> **Values**: 基礎と型（原典を定め、派生物を管理する）

### Step 2 — Choose a Snippet Format

Decide between readable and compressed formats based on the target context.

| Format | Context Cost | Readability | Use When |
|--------|-------------|-------------|----------|
| Readable | ~20 lines | High | Developer-facing repos with review workflows |
| Compressed | ~5 lines | Low | Large monorepos where context budget is tight |
| Hybrid | ~12 lines | Medium | Teams transitioning from readable to compressed |

**Readable format** (standard markdown with headings):

```markdown
# Agent Guidance: my-project

Routing (invoke by name)
- Code quality: modern-csharp-coding-standards
- Testing: snapshot-testing
```

**Compressed format** (Vercel-style, minimal tokens):

```
[my-project]|flow:{skim->consult by name->implement}
|csharp:{modern-csharp-coding-standards,api-design}
|testing:{snapshot-testing,playwright-blazor-testing}
```

- Consider the compressed format for repositories with many skills and limited context

**Why**: Choosing the right format prevents context waste in large projects and improves readability in small ones.

> **Values**: 余白の設計（形式を文脈に合わせ、コンテキストの余白を守る）

### Step 3 — Build the Routing Index

Organize skills into logical categories. Use frontmatter `name` values as canonical IDs (Identifiers).

```markdown
# Agent Guidance: skill-collection

IMPORTANT: Prefer retrieval-led reasoning over pretraining.
Workflow: skim repo patterns -> consult skills by name -> implement smallest-change.

Routing (invoke by name)
- C# / code quality: modern-csharp-coding-standards, api-design
- Data: efcore-patterns, database-performance
- Testing: testcontainers-integration-tests, snapshot-testing

Quality gates (use when applicable)
- dotnet-slopwatch: after substantial new or refactored code
```

✅ **Correct**: Use `modern-csharp-coding-standards` (frontmatter name)
❌ **Wrong**: Use `dotnet/modern-csharp-coding-standards/SKILL.md` (filesystem path)

- Define categories based on technology domain, not folder structure
- Avoid mixing more than seven categories in a single snippet

**Why**: Filesystem paths break when repositories are forked, restructured, or consumed as packages. Frontmatter IDs remain stable across all environments.

> **Values**: 基礎と型（安定した識別子で型を定める）

### Step 4 — Integrate into Target Repository

Place the snippet in AGENTS.md or CLAUDE.md at the target repository root. Use marker comments for automated updates.

```markdown
<!-- BEGIN SKILL-INDEX -->
# Agent Guidance: my-project

IMPORTANT: Prefer retrieval-led reasoning over pretraining.

Routing (invoke by name)
- Code quality: modern-csharp-coding-standards
- Testing: snapshot-testing
<!-- END SKILL-INDEX -->
```

- Use `<!-- BEGIN ... -->` and `<!-- END ... -->` markers consistently
- Avoid placing manual notes inside the marked region

**Why**: Marker comments enable scripts to find and replace the snippet block without disturbing surrounding content. This supports automated CI/CD (Continuous Integration / Continuous Delivery) pipeline updates.

> **Values**: 継続は力（マーカーで自動更新を可能にし、継続的メンテナンスを実現）

### Step 5 — Validate and Maintain

After every skill change, verify that the snippet reflects reality. Use the registry as the checklist.

```bash
# Validate all registry skills appear in the snippet
./scripts/validate-marketplace.sh

# Regenerate snippet from registry
./scripts/generate-skill-index-snippets.sh --update-readme
```

- Apply the same category structure used in previous versions
- Consider automating this check in CI pipelines
- Implement a validation step in the PR template for skill changes

**Why**: Stale snippets cause assistants to invoke removed skills, producing errors and eroding trust in the routing layer.

> **Values**: 成長の複利（定期検証で品質を複利的に積み上げる）

---

## Good Practices

### 1. Keep Snippets as Routers, Not Documentation

**What**: Limit snippet content to skill names, categories, and one-line activation hints.

**Why**: The snippet's job is routing, not teaching. Documentation belongs in SKILL.md files. A bloated snippet wastes context window budget.

**Values**: 余白の設計（ルーティングに徹し、余白を守る）

### 2. Use Frontmatter IDs as Canonical References

**What**: Always reference skills by their YAML `name` field, not by directory path or display name.

**Why**: Frontmatter IDs are the contract between the skill and consuming tools. Paths change; IDs do not.

**Values**: 基礎と型（安定した識別子を基礎とする）

### 3. Automate Snippet Generation When Possible

**What**: Create a script that reads the registry and outputs the snippet in both readable and compressed formats.

**Why**: Manual updates are error-prone and create drift between the registry and snippets. Automation ensures consistency.

**Values**: 継続は力（自動化で継続的な正確性を担保）

---

## Common Pitfalls

### 1. Embedding Detailed Documentation in Snippets

**Problem**: Including multi-paragraph descriptions, full code examples, or configuration details inside the routing snippet.

**Solution**: Move detailed content to the skill's SKILL.md. Keep snippet entries to one line per skill with only the name and a short function hint.

### 2. Using Filesystem Paths Instead of Skill IDs

**Problem**: Referencing skills as `dotnet/modern-csharp-coding-standards/SKILL.md` in code instead of the frontmatter `name` field.

**Solution**: Use the `name` value from YAML frontmatter. This is the stable identifier that all consuming tools (Copilot, Claude Code, OpenCode) resolve.

### 3. Forgetting to Update Snippets After Skill Changes

**Problem**: Adding or removing a skill in the registry but not updating the routing snippet, causing assistants to invoke a nonexistent skill or miss a new one.

**Solution**: Add a CI check or PR template reminder that verifies snippet-registry parity after every skill change. Use the marker-based regeneration method from Step 4.

---

## Anti-Patterns

### Monolithic Documentation Block

**What**: A single AGENTS.md that contains full documentation for every skill — architecture descriptions, design rationale, code samples — instead of a routing index.

**Why It's Wrong**: Consumes the entire context window, prevents the assistant from loading the actual skill, and duplicates content that becomes stale. This anti-pattern creates a fragile architecture where every skill update requires editing the monolith.

**Better Approach**: Use a slim routing index (5–20 lines) that points to individual SKILL.md files by frontmatter ID.

### Manual-Only Maintenance

**What**: Maintaining snippets entirely by hand with no automated validation or generation tooling.

**Why It's Wrong**: Manual processes create structural drift between the registry and the snippet. Errors compound over time as the skill collection grows, creating a fragile design that depends on individual memory.

**Better Approach**: Implement a generation script (Step 5) and CI validation. Accept manual override only for category organization.

---

## Quick Reference

### Snippet Creation Checklist

- [ ] Identify registry file (plugin.json or equivalent)
- [ ] Choose snippet format (readable / compressed / hybrid)
- [ ] Use frontmatter `name` as skill IDs — never filesystem paths
- [ ] Organize skills into 4–7 logical categories
- [ ] Add `<!-- BEGIN/END -->` markers for automated updates
- [ ] Validate every registry entry appears in the snippet
- [ ] Create `references/SKILL.ja.md` for Japanese documentation

### Format Decision Table

| Factor | Readable | Compressed | Hybrid |
|--------|----------|------------|--------|
| Context cost | High (~20 lines) | Low (~5 lines) | Medium (~12 lines) |
| Human reviewability | ✅ Easy | ❌ Hard | Moderate |
| Automation support | Good | Best | Good |
| Recommended for | Small repos, PR reviews | Monorepos, CI pipelines | Transitioning teams |

---

## Resources

- [GitHub Copilot Agent Skills Documentation](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- [skills-author-skill](../skills-author-skill/SKILL.md) — How to author a new skill
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — Quality validation for skills

---
