---
name: skills-revise-skill
description: Revise existing skills, synchronize EN/JA structure, and optimize discoverability metadata. Use when updating published skills.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, revision, maintenance, changelog]
  invocable: false
---

# Skill Revision Guide

Guide for revising and maintaining GitHub Copilot agent skills with bilingual synchronization and discoverability optimization.

## When to Use This Skill

Use this skill when:
- Updating existing SKILL.md files with new content or fixes
- Improving name/description/metadata tags so skills trigger reliably
- Synchronizing English SKILL.md with Japanese versions
- Managing skill versions and backward compatibility
- Identifying system-created skills via author metadata

---

## Related Skills

- **`skills-author-skill`** - Skill writing workflow
- **`skills-validate-skill`** - Validate revisions before publishing
- **`skills-refactor-skill-to-single-workflow`** - Refactor legacy skills before revision

---

## Core Principles

1. **Changelog Discipline** - Record substantial changes in one-line format (基礎と型)
2. **Bilingual Sync** - Always update English and Japanese versions (温故知新)
3. **Author Tracking** - Use author field to detect system skills (ニュートラル)
4. **Knowledge Base** - Build revision history for compound growth (成長の複利)

---

## Workflow: Revise and Version Skills

### Step 1: Detect System-Created Skills

Check `metadata.author: RyoMurakami1983` in YAML frontmatter to determine the skill's origin. System-created skills require enhanced maintenance (bilingual sync + metadata quality), while third-party skills follow standard revision.

```python
import yaml

def is_system_skill(skill_path: Path) -> bool:
    content = skill_path.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return False
    end = content.find('---', 3)
    frontmatter = yaml.safe_load(content[3:end])
    metadata = frontmatter.get('metadata', {}) if isinstance(frontmatter, dict) else {}
    return metadata.get('author') == 'RyoMurakami1983'
```

**When**: Always run first — determines whether EN/JA sync and CHANGELOG checks apply.

| Skill Type | Detection | Revision Support |
|------------|-----------|------------------|
| System-created | `metadata.author: RyoMurakami1983` | Enhanced: EN/JA sync + metadata quality |
| Third-party | No author or different | Standard: EN only |
| Unknown | No frontmatter | Minimal: suggest adding frontmatter |

---

### Step 2: Classify Change Significance

Determine if a change is substantial (log it) or trivial (skip logging). A focused changelog prevents noise and helps users spot meaningful updates.

**Substantial** (log): New sections, bug fixes, API changes, framework updates, clarifications.
**Trivial** (skip): Typos, whitespace, grammar, punctuation.

```python
SUBSTANTIAL_KEYWORDS = ['added', 'removed', 'changed', 'fixed', 'deprecated', 'breaking']
TRIVIAL_MARKERS = ['typo', 'spelling', 'grammar', 'whitespace']

def is_substantial(description: str) -> bool:
    desc = description.lower()
    if any(k in desc for k in TRIVIAL_MARKERS):
        return False
    return any(k in desc for k in SUBSTANTIAL_KEYWORDS)
```

**When**: Before writing any CHANGELOG entry — gate all logging through this check.

| Change Type | Log? | Example |
|-------------|------|---------|
| Content added/removed | ✅ Yes | "Added: Circuit Breaker step" |
| Functionality changed | ✅ Yes | "Changed: Sync → Async pattern" |
| Bug fix | ✅ Yes | "Fixed: Memory leak in example" |
| Typo/grammar | ❌ No | "performace" → "performance" |
| Formatting | ❌ No | Indentation, line breaks |

---

### Step 3: Record Revision in Git/PR Context

Record substantial changes in commit message / PR description instead of SKILL.md changelog sections.

```text
Changed: <what changed>
Why: <why it was needed>
Impact: <trigger/discoverability/behavior impact>
```

**Format rules**: Category prefix + one-line summary + explicit Why/Impact.

**When**: After any substantial change.

---

### Step 4: Synchronize English and Japanese

For system skills, keep SKILL.md and references/SKILL.ja.md in sync. Update both versions when content changes affect meaning, sections are added/removed, or code examples change.

| Change Type | Sync Required? | Why |
|-------------|---------------|-----|
| Added section | ✅ Yes | Structure must match |
| Code example changed | ✅ Yes | Technical content changed |
| Wording improved | ⚠️ Maybe | Only if meaning changed |
| Typo fixed | ❌ No | Unless in both versions |

**Sync checklist after editing English SKILL.md**:
- [ ] Section count matches (EN = JA)
- [ ] Step titles identical
- [ ] Code block count similar (±2 acceptable)
- [ ] Tables have matching columns

**When**: Every time a system skill (`author: RyoMurakami1983`) has substantial English changes.

---

### Step 5: Bump Version Number

Apply semantic versioning (MAJOR.MINOR.PATCH) based on change significance. Update the version in frontmatter and CHANGELOG.

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking change | MAJOR (2.0.0) | Changed async signature |
| New feature/step | MINOR (1.3.0) | Added Step 8 |
| Bug fix | PATCH (1.2.1) | Fixed memory leak |
| Typo fix | (none) | Don't bump for trivial |

**When**: After all changes are applied and revision notes are recorded in commit/PR context.

---

### Step 6: Detect Outdated Skills

Proactively identify skills needing updates based on age. Use Git history (last significant update date) and flag stale skills for review.

```python
import re
from datetime import datetime

def check_freshness(skill_path: Path) -> str:
    content = skill_path.read_text(encoding='utf-8')
    last_updated = get_last_git_update_date(skill_path)  # implement via `git log -1 --format=%cs`
    if not last_updated:
        return "unknown - check git history"
    age = (datetime.now() - datetime.strptime(last_updated, '%Y-%m-%d')).days
    if age > 180: return f"stale ({age}d) - review needed"
    if age > 90:  return f"aging ({age}d) - consider review"
    return f"fresh ({age}d)"
```

**When**: During quarterly maintenance or before batch revisions.

| Age | Status | Action |
|-----|--------|--------|
| < 90 days | Fresh | No action needed |
| 90-180 days | Aging | Consider review |
| > 180 days | Stale | Review for updates |

---

### Step 7: Batch Revise Skills

Revise multiple skills in a single session for consistency. Apply the same standards across all skills: detect system skills, apply changes, sync JA versions, optimize metadata discoverability, and validate.

```python
def batch_revise(skill_paths: list[Path], description: str):
    for path in skill_paths:
        is_system = is_system_skill(path)
        apply_revision(path)
        if is_system:
            ja = path.parent / "references" / "SKILL.ja.md"
            if ja.exists():
                apply_revision(ja, language='ja')
        optimize_discoverability_metadata(path)
        score = run_validation(path)
        status = "PASS" if score >= 80 else "FAIL"
        print(f"{path.name}: {score:.0f}% ({status})")
```

**When**: Framework/library updates across skills, standardizing style, fixing recurring issues, or quarterly maintenance.

---

## Best Practices

1. **Detect System Skills** - Use `metadata.author: RyoMurakami1983` field programmatically
2. **Log Substantial Only** - Skip typos, formatting; record meaningful changes in commit/PR context
3. **Optimize Discoverability** - Review `name`, `description`, and `metadata.tags` on each revision
4. **Sync EN/JA** - Always update both versions for system skills
5. **No In-File Changelog** - Keep history in Git commits/PRs, not SKILL.md sections
6. **Semantic Versioning** - MAJOR.MINOR.PATCH based on change type
7. **Validate After Revision** - Run quality check before publishing
8. **Commit Atomically** - Each version bump = one commit
9. **Backward Compatibility** - Deprecate before removing features

---

## Common Pitfalls

- **Forgetting Japanese version**: After editing English SKILL.md, always check if `references/SKILL.ja.md` exists and update it. Fix: add JA check to your revision workflow.
- **Logging trivial changes**: Don't clutter commit/PR summaries with typo-only details. Fix: gate notes through `is_substantial()` check.
- **Hard-coding system skill lists**: Don't maintain manual lists of system skills. Fix: detect via `metadata.author` field programmatically.

---

## Anti-Patterns

### 1. Logging Every Trivial Change

**Problem**: Trivial entries (typos, indentation) bury meaningful updates.

```python
# ❌ notes.append("Fixed: typo in line 42")
# ✅ Only log substantial: notes.append(f"Changed: {before} → {after}")
```

### 2. Neglecting Bilingual Sync

**Problem**: Updating English only creates documentation drift for Japanese users.

```python
# ❌ update_file("SKILL.md", content)  # Forgot JA!
# ✅ update_file("SKILL.md", en); update_file("references/SKILL.ja.md", ja)
```

---

## Quick Reference

```
1. Open SKILL.md → Check metadata.author field
   ├─ metadata.author: RyoMurakami1983 → System skill (enhanced)
   └─ Other/none → Standard revision

2. Make changes to English SKILL.md

3. Substantial change?
   ├─ Yes → Record commit/PR revision notes + continue
   └─ No (typo/format) → Skip to step 6

4. If system skill → Update references/SKILL.ja.md

5. Optimize discoverability metadata (name/description/tags)

6. Run skills-validate-skill → Commit
```

**System Skill** (`metadata.author: RyoMurakami1983`): EN/JA sync + metadata optimization + enhanced validation.
**Non-System Skill**: English only + basic validation.

---

## Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [skills-validate-skill](../skills-validate-skill/SKILL.md) - Validate revisions
- [skills-author-skill](../skills-author-skill/SKILL.md) - Authoring conventions and metadata rules

---
