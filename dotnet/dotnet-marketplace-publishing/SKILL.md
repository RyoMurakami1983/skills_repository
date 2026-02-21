---
name: dotnet-marketplace-publishing
description: >
  Publish skills and agents to the dotnet-skills Claude Code marketplace.
  Use when adding new skills, registering agents, updating plugin.json,
  or releasing a new marketplace version.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, marketplace, publishing, claude-code, skills]
  invocable: false
---

# Marketplace Publishing Workflow

A step-by-step guide for publishing skills and agents to the dotnet-skills Claude Code marketplace. Covers folder structure, SKILL.md authoring, plugin.json registration, validation, and semantic versioning releases.

**Acronyms**: YAML (YAML Ain't Markup Language), JSON (JavaScript Object Notation), CLI (Command-Line Interface), CI (Continuous Integration), DI (Dependency Injection).

## When to Use This Skill

- Adding a new skill folder and SKILL.md to the dotnet-skills marketplace repository
- Registering a new agent definition in the agents directory and plugin.json registry
- Updating plugin.json to include newly created skill or agent path entries
- Validating marketplace structure before committing changes with the validation script
- Bumping the semantic version in plugin.json and tagging a release for distribution
- Troubleshooting missing skills or validation errors after a marketplace installation
- Choosing the correct category folder for a new skill based on its technology domain
- Reviewing an existing skill submission for completeness and frontmatter correctness

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-modern-csharp-coding-standards` | C# coding standards referenced in skill content |
| `dotnet-project-structure` | .NET project layout conventions for skill examples |
| `dotnet-package-management` | NuGet dependency documentation within skills |

## Core Principles

1. **Single Source of Truth** — Register every skill and agent in `plugin.json`. Why: the marketplace catalog reads this file to discover available content. Duplicates or orphan entries cause installation failures.
2. **Convention Over Configuration** — Follow the `skills/<category>/<name>/SKILL.md` path convention. Why: consistent structure enables automated validation and reduces onboarding friction for contributors.
3. **Atomic Commits** — Commit the skill folder and `plugin.json` update together. Why: separate commits leave the registry in an inconsistent state where paths reference missing files.
4. **Semantic Versioning** — Apply MAJOR.MINOR.PATCH versioning to every release tag. Why: consumers rely on version numbers to decide when to update and whether breaking changes exist.

> **Values**: 基礎と型の追求（規約に従った構造が、自動バリデーションと再利用性を最大化する）, 継続は力（小さなスキルをコツコツ追加し、マーケットプレイスの価値を複利で積み上げる）

## Workflow: Publish to Marketplace

### Step 1: Choose the Category Folder

Select the appropriate category folder under `skills/`. Create a new folder if none fits the domain.

| Category | Purpose | Example skills |
|----------|---------|----------------|
| `akka/` | Akka.NET actor patterns, clustering, testing | `best-practices`, `testing-patterns` |
| `aspire/` | .NET Aspire orchestration and configuration | `service-defaults`, `dashboard` |
| `csharp/` | C# language features and coding standards | `modern-csharp`, `pattern-matching` |
| `testing/` | Testing frameworks (xUnit, Playwright) | `testcontainers`, `snapshot-testing` |
| `meta/` | Meta skills about the marketplace itself | `marketplace-publishing` |

```bash
# Verify the category exists
ls skills/

# Create a new category if needed
mkdir -p skills/newcategory/
```

> **Values**: 余白の設計（カテゴリ構造に余白を残し、将来のドメイン拡張を容易にする）

### Step 2: Create the Skill Folder and SKILL.md

Create a kebab-case folder containing a single `SKILL.md` file. Why: the validation script expects exactly this structure.

```bash
# Create skill folder
mkdir -p skills/akka/cluster-sharding/
```

Write the SKILL.md with valid YAML frontmatter:

```yaml
---
name: cluster-sharding
description: >
  Implement Akka.NET Cluster Sharding for distributed
  entity management. Use when designing sharded actors.
---
```

**Requirements checklist:**

| Field | Rule | Example |
|-------|------|---------|
| `name` | Lowercase kebab-case, matches folder | `cluster-sharding` |
| `description` | 1–2 sentences, includes "use when" trigger | See above |
| Content | 10–40 KB, concrete code examples | C# 12+ patterns |

> **Values**: 基礎と型の追求（フロントマターの型を守ることで、自動検出と品質検証が機能する）

### Step 3: Register the Skill in plugin.json

Add the skill path to the `skills` array in `.claude-plugin/plugin.json`. Why: unregistered skills are invisible to the marketplace installer.

```json
{
  "skills": [
    "./skills/akka/best-practices",
    "./skills/akka/cluster-sharding"
  ]
}
```

- ✅ Use relative paths starting with `./skills/`
- ✅ Point to the folder, not the SKILL.md file
- ❌ Avoid trailing commas — JSON does not allow them
- ❌ Avoid duplicate entries — each path must be unique

> **Values**: ニュートラルな視点（plugin.json は機械可読な唯一の登録簿であり、曖昧さを排除する）

### Step 4: Add an Agent (Optional)

Create an agent markdown file in `/agents/` with model and description metadata. Why: agents extend the marketplace with specialized domain expertise.

```markdown
---
name: akka-net-specialist
description: >
  Expert in Akka.NET actor model patterns.
  Use for actor design and cluster configuration.
model: sonnet
color: blue
---

You are an Akka.NET specialist with deep expertise in actor systems.
```

Register the agent in plugin.json:

```json
{
  "agents": [
    "./agents/akka-net-specialist"
  ]
}
```

| Field | Required | Values |
|-------|----------|--------|
| `name` | Yes | Lowercase kebab-case |
| `description` | Yes | 1–2 sentences with "use for" trigger |
| `model` | Yes | `haiku`, `sonnet`, or `opus` |
| `color` | No | UI display hint |

> **Values**: 成長の複利（エージェントを追加するほど、チーム全体が利用できる専門知識が増幅する）

### Step 5: Validate the Marketplace

Run the validation script before committing. Why: CI will reject invalid structure, so catching errors locally saves time.

```bash
# Run marketplace validation
./scripts/validate-marketplace.sh

# Check JSON syntax separately
jq . .claude-plugin/plugin.json
```

**Validation checks:**

- SKILL.md has valid YAML frontmatter with `name` and `description`
- Skill folder is under an appropriate category
- Path in plugin.json matches the actual folder structure
- Agent files specify a valid `model` value
- No orphan entries (paths pointing to missing folders)

> **Values**: 温故知新（バリデーションスクリプトという「型」を守ることで、過去の失敗パターンを繰り返さない）

### Step 6: Commit and Release

Commit the skill and registry update atomically. Why: separate commits risk leaving the marketplace in an inconsistent state.

```bash
# Atomic commit — skill + registry together
git add skills/akka/cluster-sharding/ .claude-plugin/plugin.json
git commit -m "feat: add cluster-sharding skill for Akka.NET Cluster Sharding"

# Version bump for release
# Update version in plugin.json first, then:
git add .claude-plugin/plugin.json
git commit -m "chore: bump version to 1.1.0"

# Tag and push
git tag v1.1.0
git push origin master --tags
```

**Semantic versioning rules:**

| Change type | Version bump | Example |
|-------------|-------------|---------|
| Breaking (renamed/removed skills) | MAJOR | 1.0.0 → 2.0.0 |
| New skills or agents added | MINOR | 1.0.0 → 1.1.0 |
| Fixes to existing content | PATCH | 1.0.0 → 1.0.1 |

GitHub Actions automatically validates the structure and creates a release with notes.

> **Values**: 継続は力（小さなリリースをコツコツ積み上げることで、マーケットプレイスの信頼性が向上する）

## Good Practices

- ✅ Use `name` in frontmatter that exactly matches the folder name in kebab-case
- ✅ Include "use when" trigger phrase in the skill description for discoverability
- ✅ Commit skill folder and plugin.json changes in a single atomic commit
- ✅ Apply semantic versioning consistently — MINOR for new content, PATCH for fixes
- ✅ Run `validate-marketplace.sh` locally before pushing to avoid CI failures
- ✅ Use concrete code examples with modern C# patterns in skill content
- ✅ Provide 10–40 KB of comprehensive coverage per skill topic
- ✅ Expand acronyms on first use in skill content (e.g., DI, DTO, CI)

## Common Pitfalls

1. **Forgetting plugin.json update** — Adding a skill folder without registering it. The skill is invisible to installers. Fix: always commit both together.
2. **Trailing commas in JSON** — JSON does not allow trailing commas in arrays. Fix: use `jq .` to validate syntax before committing.
3. **Name mismatch** — Frontmatter `name` differs from the folder name. Fix: ensure exact kebab-case match between both.
4. **Missing SKILL.md** — Creating the folder but not the SKILL.md file inside it. Fix: validate with the marketplace script.
5. **Split commits** — Committing the skill folder and plugin.json separately. Fix: use `git add` for both, then a single `git commit`.
6. **Wrong model value** — Using an unsupported model name in agent metadata. Fix: use only `haiku`, `sonnet`, or `opus`.

## Anti-Patterns

### ❌ Orphan Registry Entry → ✅ Validated Path

```json
// ❌ BAD — path points to non-existent folder
{ "skills": ["./skills/akka/nonexistent-skill"] }
// ✅ GOOD — path matches actual folder structure
{ "skills": ["./skills/akka/cluster-sharding"] }
```

Why: orphan entries cause silent installation failures. The validation script catches this.

### ❌ Split Commits → ✅ Atomic Commit

```bash
# ❌ BAD — two separate commits leave registry inconsistent
git add skills/akka/cluster-sharding/
git commit -m "Add skill"
git add .claude-plugin/plugin.json
git commit -m "Register skill"

# ✅ GOOD — single atomic commit
git add skills/akka/cluster-sharding/ .claude-plugin/plugin.json
git commit -m "feat: add cluster-sharding skill"
```

Why: if the first commit is deployed without the second, the registry is broken.

### ❌ Unversioned Release → ✅ Semantic Version Tag

```bash
# ❌ BAD — tag without version bump in plugin.json
git tag latest
# ✅ GOOD — version bump + semver tag
# (after updating version in plugin.json to 1.1.0)
git tag v1.1.0
```

Why: consumers use semver to decide whether updates contain breaking changes.

## Quick Reference

### Publishing Decision Table

| Task | Key action | Commit includes |
|------|-----------|-----------------|
| Add a skill | Create `skills/<cat>/<name>/SKILL.md` | Skill folder + plugin.json |
| Add an agent | Create `agents/<name>.md` | Agent file + plugin.json |
| Fix existing skill | Edit SKILL.md content | Skill file only |
| Release version | Bump version, create tag | plugin.json + git tag |

### User Installation Commands

```bash
# Add the marketplace (one-time)
/plugin marketplace add Aaronontheweb/dotnet-skills

# Install the plugin (gets all skills and agents)
/plugin install dotnet-skills

# Update to latest version
/plugin marketplace update
```

### Troubleshooting Quick Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Skill not appearing | Missing plugin.json entry | Add path and reinstall |
| Validation error | Invalid JSON syntax | Run `jq .` to find error |
| Release not created | Tag format wrong | Use `v1.0.0` semver format |
| Agent not loading | Missing `model` field | Add `haiku`, `sonnet`, or `opus` |

## Resources

- [Claude Code Plugin System](https://docs.anthropic.com/claude-code/plugins) — Official plugin documentation
- [Semantic Versioning 2.0.0](https://semver.org/) — Versioning specification
- [Conventional Commits](https://www.conventionalcommits.org/) — Commit message format used in releases
- [JSON Specification](https://www.json.org/) — JSON syntax reference for plugin.json editing
