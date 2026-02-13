---
name: skill-revision-guide
description: Guide for revising GitHub Copilot agent skills and managing changelogs.
author: RyoMurakami1983
tags: [copilot, agent-skills, revision, maintenance, changelog]
invocable: false
---

# Skill Revision Guide

Guide for revising, versioning, and maintaining GitHub Copilot agent skills with changelog management and bilingual synchronization.

## When to Use This Skill

Use this skill when:
- Updating existing SKILL.md files with new content or fixes
- Recording changes in CHANGELOG.md with concise entries
- Synchronizing English SKILL.md with Japanese versions
- Managing skill versions and backward compatibility
- Identifying system-created skills via author metadata

---

## Related Skills

- **`skill-writing-guide`** - Reference skill writing standards
- **`skill-quality-validation`** - Validate revisions before publishing
- **`skill-template-generator`** - Generate new skills

---

## Core Principles

1. **Changelog Discipline** - Record substantial changes in one-line format (基礎と型)
2. **Bilingual Sync** - Always update English and Japanese versions (温故知新)
3. **Author Tracking** - Use author field to detect system skills (ニュートラル)
4. **Knowledge Base** - Build revision history for compound growth (成長の複利)

---

## Workflow: Revise and Version Skills

### Step 1: Detect System-Created Skills

Check `author: RyoMurakami1983` in YAML frontmatter to determine the skill's origin. System-created skills require enhanced maintenance (bilingual sync + changelog), while third-party skills follow standard revision.

```python
import yaml

def is_system_skill(skill_path: Path) -> bool:
    content = skill_path.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return False
    end = content.find('---', 3)
    frontmatter = yaml.safe_load(content[3:end])
    return frontmatter.get('author') == 'RyoMurakami1983'
```

**When**: Always run first — determines whether EN/JA sync and CHANGELOG checks apply.

| Skill Type | Detection | Revision Support |
|------------|-----------|------------------|
| System-created | `author: RyoMurakami1983` | Enhanced: EN/JA sync + CHANGELOG |
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

### Step 3: Update CHANGELOG.md

Maintain concise, scannable changelogs with 1-line entries per substantial change. Use category prefixes and group by version with ISO dates.

```markdown
# Changelog

## Version 1.2.0 (2026-02-15)

- Changed: Sync method → Async/await pattern for API calls
- Added: Step 8 - Circuit Breaker implementation
- Fixed: Memory leak in ViewModelBase.Dispose()

## Version 1.1.0 (2026-01-20)

- Added: Step 7 - Retry policies with Polly
- Deprecated: Old ConfigureServices method

## Version 1.0.0 (2026-01-01)

- Initial release
```

**Format rules**: Category prefix (Added/Changed/Fixed/Removed/Deprecated/Updated) + 1-line description (max 100 chars) + grouped by version (YYYY-MM-DD).

**When**: After any substantial change. Use a separate CHANGELOG.md when skill has >5 versions or changelog exceeds 50 lines.

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

**When**: After all changes are applied and changelog is updated. Each version bump = one atomic commit.

---

### Step 6: Detect Outdated Skills

Proactively identify skills needing updates based on age. Parse the latest version date from the changelog and flag stale skills for review.

```python
import re
from datetime import datetime

def check_freshness(skill_path: Path) -> str:
    content = skill_path.read_text(encoding='utf-8')
    match = re.search(r'## Version.*?\((\d{4}-\d{2}-\d{2})\)', content)
    if not match:
        return "unknown - add changelog"
    age = (datetime.now() - datetime.strptime(match.group(1), '%Y-%m-%d')).days
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

Revise multiple skills in a single session for consistency. Apply the same standards across all skills: detect system skills, apply changes, sync JA versions, update changelogs, and validate.

```python
def batch_revise(skill_paths: list[Path], description: str):
    for path in skill_paths:
        is_system = is_system_skill(path)
        apply_revision(path)
        if is_system:
            ja = path.parent / "references" / "SKILL.ja.md"
            if ja.exists():
                apply_revision(ja, language='ja')
        update_changelog(path, description)
        score = run_validation(path)
        status = "PASS" if score >= 80 else "FAIL"
        print(f"{path.name}: {score:.0f}% ({status})")
```

**When**: Framework/library updates across skills, standardizing style, fixing recurring issues, or quarterly maintenance.

---

## Best Practices

1. **Detect System Skills** - Use `author: RyoMurakami1983` field programmatically
2. **Log Substantial Only** - Skip typos, formatting; log content/functionality changes
3. **1-Line Changelog** - "Category: Brief description (max 100 chars)"
4. **Sync EN/JA** - Always update both versions for system skills
5. **CHANGELOG.md** - Move from SKILL.md when > 50 lines
6. **Semantic Versioning** - MAJOR.MINOR.PATCH based on change type
7. **Validate After Revision** - Run quality check before publishing
8. **Commit Atomically** - Each version bump = one commit
9. **Backward Compatibility** - Deprecate before removing features

---

## Common Pitfalls

- **Forgetting Japanese version**: After editing English SKILL.md, always check if `references/SKILL.ja.md` exists and update it. Fix: add JA check to your revision workflow.
- **Logging trivial changes**: Don't clutter CHANGELOG with typo/formatting fixes. Fix: gate all entries through `is_substantial()` check.
- **Hard-coding system skill lists**: Don't maintain manual lists of system skills. Fix: detect via `author` frontmatter field programmatically.

---

## Anti-Patterns

### 1. Logging Every Change

**Problem**: Trivial entries (typos, indentation) bury meaningful updates.

```python
# ❌ changelog.append("Fixed: typo in line 42")
# ✅ Only log substantial: changelog.append(f"Changed: {before} → {after}")
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
1. Open SKILL.md → Check author field
   ├─ author: RyoMurakami1983 → System skill (enhanced)
   └─ Other/none → Standard revision

2. Make changes to English SKILL.md

3. Substantial change?
   ├─ Yes → Update CHANGELOG.md + continue
   └─ No (typo/format) → Skip to step 6

4. If system skill → Update references/SKILL.ja.md

5. Bump version (Breaking→MAJOR, Feature→MINOR, Fix→PATCH)

6. Run skill-quality-validation → Commit
```

**System Skill** (`author: RyoMurakami1983`): EN/JA sync + CHANGELOG + enhanced validation.
**Non-System Skill**: English only + standard changelog + basic validation.

---

## Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [skill-quality-validation](../skill-quality-validation/SKILL.md) - Validate revisions
- [CHANGELOG_TEMPLATE.md](assets/CHANGELOG_TEMPLATE.md) - Changelog template

---

## Changelog

### Version 2.0.0 (2026-02-15)
- Changed: Multi-pattern format → single-workflow with 7 steps
- Removed: Verbose code blocks (compressed to essential logic)
- Changed: Best Practices Summary merged into Best Practices
- Changed: Common Pitfalls compressed to bullet format

### Version 1.0.0 (2026-02-12)
- Initial release
- Author-based system skill detection
- CHANGELOG.md format specification
- EN/JA synchronization patterns
- Version bump strategies

<!-- 
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
