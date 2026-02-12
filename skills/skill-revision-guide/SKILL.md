---
name: skill-revision-guide
description: Guide for revising GitHub Copilot agent skills and managing changelogs.
author: RyoMurakami1983
tags: [copilot, agent-skills, revision, maintenance, changelog]
invocable: false
---

# Skill Revision Guide

Comprehensive guide for revising, maintaining, and version-controlling GitHub Copilot agent skills with changelog management and bilingual synchronization.

## When to Use This Skill

Use this skill when:
- Updating existing SKILL.md files with new content or fixes
- Recording changes in CHANGELOG.md with concise entries
- Synchronizing English SKILL.md with Japanese versions
- Managing skill versions and backward compatibility
- Identifying system-created skills via author metadata
- Determining whether a change is substantial or trivial

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

## Pattern 1: Identifying System-Created Skills

### Overview

Detect skills created by this system via `author: RyoMurakami1983` in YAML frontmatter to provide targeted revision support.

**Why**: System-created skills require enhanced maintenance including bilingual synchronization and changelog management, while community-contributed skills may follow different conventions.

### Basic Example

```python
# ✅ CORRECT - Detect system-created skills
import yaml

def is_system_skill(skill_path: Path) -> bool:
    """Check if skill was created by this system"""
    content = skill_path.read_text(encoding='utf-8')
    
    # Extract YAML frontmatter
    if not content.startswith('---'):
        return False
    
    end_index = content.find('---', 3)
    if end_index == -1:
        return False
    
    frontmatter_text = content[3:end_index]
    frontmatter = yaml.safe_load(frontmatter_text)
    
    return frontmatter.get('author') == 'RyoMurakami1983'

# Usage
if is_system_skill(Path("~/.copilot/skills/my-skill/SKILL.md")):
    print("✅ System skill detected - applying enhanced revision support")
    print("  - Will check for references/SKILL.ja.md synchronization")
    print("  - Will verify CHANGELOG.md exists")
else:
    print("ℹ️ Non-system skill - applying standard revision support")
```

### When to Use

| Skill Type | Detection | Revision Support |
|------------|-----------|------------------|
| System-created | `author: RyoMurakami1983` | Enhanced: EN/JA sync + CHANGELOG |
| Third-party | No author or different | Standard: EN only |
| Unknown | No frontmatter | Minimal: suggest adding frontmatter |

### With Configuration

```python
# ✅ CORRECT - Enhanced revision for system skills
class SkillRevisionAssistant:
    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.is_system_skill = self._detect_system_skill()
    
    def _detect_system_skill(self) -> bool:
        """Detect if this is a system-created skill"""
        # ... (detection logic from above)
        pass
    
    def revise(self, changes: dict):
        """Apply revisions with appropriate support level"""
        if self.is_system_skill:
            self._revise_with_enhanced_support(changes)
        else:
            self._revise_standard(changes)
    
    def _revise_with_enhanced_support(self, changes: dict):
        """Enhanced revision for system skills"""
        # 1. Apply changes to English version
        self._apply_changes_to_english(changes)
        
        # 2. Check for Japanese version
        ja_path = self.skill_path.parent / "references" / "SKILL.ja.md"
        if ja_path.exists():
            print("⚠️ Japanese version detected")
            print(f"   Update references/SKILL.ja.md to match English changes")
            self._suggest_japanese_updates(changes)
        else:
            print("ℹ️ No Japanese version found - English only revision")
        
        # 3. Update CHANGELOG.md
        if self._is_substantial_change(changes):
            self._update_changelog(changes)
        
        # 4. Run quality validation
        print("✅ Running quality validation...")
        # Call skill-quality-validation
```

---

## Pattern 2: Recording Substantial Changes

### Overview

Determine if a change is substantial (should be logged) vs. trivial (skip logging).

**Why**: Maintaining a focused changelog prevents noise and helps users quickly identify meaningful updates. Logging every typo fix would make the changelog unreadable.

### Basic Example

**Substantial Changes** (log these):
- Added new pattern section
- Fixed critical bug in code example
- Changed API signature
- Updated to new framework version
- Clarified ambiguous section

**Trivial Changes** (don't log):
- Fixed typo ("performace" → "performance")
- Adjusted whitespace/formatting
- Corrected grammar
- Added missing comma
- Updated punctuation

### When to Use

Use this pattern to decide if CHANGELOG.md entry is needed.

| Change Type | Log? | Example |
|-------------|------|---------|
| Content added/removed | ✅ Yes | "Added Pattern 8: Circuit Breaker" |
| Functionality changed | ✅ Yes | "Changed: Sync method → Async/await pattern" |
| Bug fix | ✅ Yes | "Fixed: Memory leak in ViewModelBase" |
| Typo/grammar | ❌ No | "performace" → "performance" |
| Formatting | ❌ No | Indentation, line breaks |

### With Configuration

```python
# ✅ CORRECT - Substantial change detector
import difflib

class ChangeAnalyzer:
    TRIVIAL_PATTERNS = [
        r'^\s+',  # Whitespace only
        r'^[.,;:!?]',  # Punctuation only
        r'typo|spelling|grammar',  # Explicit markers
    ]
    
    SUBSTANTIAL_KEYWORDS = [
        'added', 'removed', 'changed', 'fixed', 'updated',
        'improved', 'refactored', 'deprecated', 'breaking'
    ]
    
    def is_substantial(self, before: str, after: str, description: str = "") -> bool:
        """Determine if change is substantial"""
        # Check explicit description
        desc_lower = description.lower()
        if any(keyword in desc_lower for keyword in self.SUBSTANTIAL_KEYWORDS):
            return True
        
        if any(re.search(pattern, desc_lower) for pattern in self.TRIVIAL_PATTERNS):
            return False
        
        # Compare content
        diff = difflib.unified_diff(
            before.split('\n'),
            after.split('\n'),
            lineterm=''
        )
        changes = list(diff)
        
        # If > 10 lines changed, likely substantial
        if len([l for l in changes if l.startswith('+') or l.startswith('-')]) > 10:
            return True
        
        # Check for structural changes (headings, code blocks)
        before_structure = self._extract_structure(before)
        after_structure = self._extract_structure(after)
        
        return before_structure != after_structure
    
    def _extract_structure(self, content: str) -> list:
        """Extract headings and code block markers"""
        return [
            line.strip() for line in content.split('\n')
            if line.startswith('#') or line.startswith('```')
        ]

# Usage
analyzer = ChangeAnalyzer()

# Substantial change
if analyzer.is_substantial(
    before="public void DoSync()",
    after="public async Task DoAsync()",
    description="Changed to async method"
):
    print("✅ Log this change to CHANGELOG.md")

# Trivial change
if not analyzer.is_substantial(
    before="performace improvements",
    after="performance improvements",
    description="typo fix"
):
    print("ℹ️ Skip CHANGELOG.md for trivial fix")
```

---

## Pattern 3: CHANGELOG.md Format

### Overview

Maintain concise, scannable changelogs with 1-line entries for each substantial change.

### Basic Example

**CHANGELOG.md**:
```markdown
# Changelog

## Version 1.2.0 (2026-02-15)

- Changed: Sync method → Async/await pattern for API calls
- Added: Pattern 8 - Circuit Breaker implementation
- Fixed: Memory leak in ViewModelBase.Dispose()
- Updated: Examples to .NET 8

## Version 1.1.0 (2026-01-20)

- Added: Pattern 7 - Retry policies with Polly
- Changed: DI configuration → Minimal API style
- Deprecated: Old ConfigureServices method

## Version 1.0.0 (2026-01-01)

- Initial release
```

**Format Rules**:
- **Category prefix**: "Added", "Changed", "Fixed", "Removed", "Deprecated", "Updated"
- **1-line description**: Brief before → after or what was done
- **Max 100 chars per line**
- **Group by version** with date in YYYY-MM-DD format

### When to Use

Use CHANGELOG.md when:
- Skill has more than 5 versions
- Changelog in SKILL.md exceeds 50 lines
- Multiple contributors need change tracking

### With Configuration

```python
# ✅ CORRECT - Changelog manager
from datetime import date
from enum import Enum

class ChangeType(Enum):
    ADDED = "Added"
    CHANGED = "Changed"
    FIXED = "Fixed"
    REMOVED = "Removed"
    DEPRECATED = "Deprecated"
    UPDATED = "Updated"

class ChangelogManager:
    def __init__(self, skill_path: Path):
        self.changelog_path = skill_path.parent / "CHANGELOG.md"
        self.current_version = self._get_current_version()
    
    def add_entry(self, change_type: ChangeType, description: str):
        """Add new changelog entry"""
        if not self.changelog_path.exists():
            self._create_changelog()
        
        entry = f"- {change_type.value}: {description}"
        
        # Insert into current version section
        content = self.changelog_path.read_text(encoding='utf-8')
        version_header = f"## Version {self.current_version}"
        
        if version_header in content:
            # Append to existing version
            lines = content.split('\n')
            insert_index = None
            for i, line in enumerate(lines):
                if line.strip() == version_header:
                    # Find next empty line after version header
                    insert_index = i + 2  # Skip version line and date line
                    break
            
            if insert_index:
                lines.insert(insert_index, entry)
                content = '\n'.join(lines)
        else:
            # Create new version section
            new_section = f"\n## Version {self.current_version} ({date.today()})\n\n{entry}\n"
            content = content.replace("# Changelog\n", f"# Changelog\n{new_section}")
        
        self.changelog_path.write_text(content, encoding='utf-8')
        print(f"✅ Added to CHANGELOG.md: {entry}")
    
    def _create_changelog(self):
        """Create new CHANGELOG.md"""
        template = f"""# Changelog

All notable changes to this skill will be documented in this file.

## Version {self.current_version} ({date.today()})

- Initial version

"""
        self.changelog_path.write_text(template, encoding='utf-8')

# Usage
manager = ChangelogManager(Path("~/.copilot/skills/my-skill/SKILL.md"))
manager.add_entry(
    ChangeType.CHANGED,
    "Sync method → Async/await pattern for API calls"
)
manager.add_entry(
    ChangeType.FIXED,
    "Memory leak in ViewModelBase.Dispose()"
)
```

---

## Pattern 4: English-Japanese Synchronization

### Overview

Keep English SKILL.md and Japanese references/SKILL.ja.md in sync when revising system-created skills.

### Basic Example

**Sync Workflow**:
1. Edit English SKILL.md
2. Identify changed sections
3. Update corresponding sections in references/SKILL.ja.md
4. Verify both versions have same structure (section count, order)

### When to Use

Synchronize when:
- System skill (`author: RyoMurakami1983`) is being revised
- Content changes affect meaning (not just wording)
- New sections added or removed
- Examples updated with different code

| Change Type | Sync Required? | Why |
|-------------|---------------|-----|
| Added section | ✅ Yes | Structure must match |
| Code example changed | ✅ Yes | Technical content changed |
| Wording improved | ⚠️ Maybe | If meaning changed, yes |
| Typo fixed | ❌ No | Unless in both versions |

### Manual Sync Checklist

**After editing English SKILL.md, verify**:

- [ ] Section count matches (EN: 8 sections = JA: 8 sections)
- [ ] Pattern titles identical (e.g., "## Pattern 4:")
- [ ] Code block count similar (±2 blocks acceptable)
- [ ] Examples structurally aligned
- [ ] Tables have matching columns

> 📚 **Automated sync checker**: See [references/sync-checker.md](references/sync-checker.md) for detailed synchronization guide and Python implementation.

---

## Pattern 5: Version Bump Strategy

### Overview

Determine when to increment version numbers based on change significance.

### Basic Example

**Semantic Versioning**: MAJOR.MINOR.PATCH (e.g., 1.2.3)

- **MAJOR** (1.x.x): Breaking changes, incompatible API changes
- **MINOR** (x.1.x): New features, backward-compatible additions
- **PATCH** (x.x.1): Bug fixes, typos, minor improvements

### When to Use

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking change | MAJOR | Changed async signature |
| New pattern added | MINOR | Added Pattern 8 |
| Bug fix | PATCH | Fixed memory leak |
| Typo fix | (none) | Don't bump for trivial |

### Decision Helper

**Quick Guide**:

```python
# Breaking change? → MAJOR
"Changed: sync method → async/await (incompatible)"  # → 2.0.0

# New feature? → MINOR
"Added: Pattern 8 - Circuit Breaker"  # → 1.3.0

# Bug fix? → PATCH
"Fixed: Memory leak in example"  # → 1.2.1

# Typo? → No bump
"Fixed typo: 'performace' → 'performance'"  # → 1.2.0 (unchanged)
```

> 📚 **Detailed versioning rules**: See [references/versioning-guide.md](references/versioning-guide.md) for comprehensive semantic versioning guide, deprecation strategies, and CHANGELOG best practices.

---

## Anti-Patterns

### 1. Logging Every Change

**Problem**: Recording trivial changes like typo fixes clutters the changelog and obscures meaningful updates.

**Impact**: Users waste time reading irrelevant changelog entries; actual breaking changes get buried.

**Solution**: Apply the substantial change filter - only log content/functionality changes, not formatting or typos.

```python
# ❌ ANTI-PATTERN - Logging everything
changelog.append("Fixed: typo in line 42")
changelog.append("Fixed: indentation")
changelog.append("Fixed: comma placement")

# ✅ CORRECT - Log only substantial changes
if is_substantial_change(diff):
    changelog.append(f"Changed: {before} → {after}")
```

### 2. Neglecting Bilingual Synchronization

**Problem**: Updating English SKILL.md but forgetting the Japanese version creates documentation drift.

**Impact**: Japanese users receive outdated or incorrect information; translation inconsistencies accumulate.

**Solution**: Always update both versions atomically, or use automation to detect desync.

```python
# ❌ ANTI-PATTERN - English only update
update_file("SKILL.md", new_content)
# Forgot references/SKILL.ja.md!

# ✅ CORRECT - Synchronized update
update_file("SKILL.md", new_content_en)
update_file("references/SKILL.ja.md", new_content_ja)
verify_sync("SKILL.md", "references/SKILL.ja.md")
```

---

## Pattern 6: Detecting Outdated Skills

### Overview

Identify skills that need updates based on age, dependency changes, or framework evolution.

**Why**: Proactive maintenance prevents skills from becoming obsolete. Regular reviews ensure examples remain current and compatible with latest tooling.

### Basic Example

```python
# ✅ CORRECT - Detect outdated skills
from datetime import datetime, timedelta
import re

def check_skill_freshness(skill_path: Path) -> dict:
    """Check if skill needs review"""
    content = skill_path.read_text(encoding='utf-8')
    
    # Extract last update from changelog
    changelog_match = re.search(r'## Version.*?\((\d{4}-\d{2}-\d{2})\)', content)
    if not changelog_match:
        return {"status": "no_changelog", "action": "Add changelog"}
    
    last_update = datetime.strptime(changelog_match.group(1), '%Y-%m-%d')
    age_days = (datetime.now() - last_update).days
    
    if age_days > 180:
        return {"status": "stale", "age_days": age_days, "action": "Review for updates"}
    elif age_days > 90:
        return {"status": "aging", "age_days": age_days, "action": "Consider review"}
    else:
        return {"status": "fresh", "age_days": age_days, "action": "No action needed"}

# Usage
result = check_skill_freshness(Path("skills/skill-writing-guide/SKILL.md"))
print(f"Status: {result['status']} ({result['age_days']} days)")
print(f"Action: {result['action']}")
```

### When to Use

| Age | Status | Action |
|-----|--------|--------|
| < 90 days | Fresh | No action needed |
| 90-180 days | Aging | Consider review |
| > 180 days | Stale | Review for updates |
| No changelog | Unknown | Add changelog |

---

## Pattern 7: Batch Revision Workflow

### Overview

Efficiently revise multiple skills in a single session with consistent quality standards.

**Why**: Batch processing reduces context-switching overhead. Applying the same standards across all skills ensures consistency and completeness.

### Basic Example

```python
# ✅ CORRECT - Batch revision with validation
from pathlib import Path
from typing import List

def batch_revise_skills(skill_paths: List[Path], changes: dict):
    """Revise multiple skills consistently"""
    results = []
    
    for skill_path in skill_paths:
        print(f"\nRevising: {skill_path.name}")
        
        # 1. Check if system skill
        is_system = check_author_field(skill_path)
        
        # 2. Apply changes
        apply_revision(skill_path, changes)
        
        # 3. Update Japanese version if system skill
        if is_system:
            ja_path = skill_path.parent / "references" / "SKILL.ja.md"
            if ja_path.exists():
                apply_revision(ja_path, changes, language='ja')
        
        # 4. Update changelog
        update_changelog(skill_path, changes['description'])
        
        # 5. Run validation
        score = run_validation(skill_path)
        
        results.append({
            "skill": skill_path.name,
            "system_skill": is_system,
            "score": score,
            "passed": score >= 80.0
        })
    
    # Summary report
    print("\n=== Batch Revision Summary ===")
    for r in results:
        status = "PASS" if r['passed'] else "FAIL"
        print(f"{r['skill']}: {r['score']:.1f}% ({status})")
    
    return results

# Usage
skills_to_update = [
    Path("skills/skill-writing-guide/SKILL.md"),
    Path("skills/skill-quality-validation/SKILL.md"),
    Path("skills/skill-template-generator/SKILL.md")
]

changes = {
    "type": "update",
    "description": "Updated code examples to Python 3.12 syntax"
}

batch_revise_skills(skills_to_update, changes)
```

### When to Use

- Applying framework/library version updates across multiple skills
- Standardizing formatting or style across the repository
- Fixing the same issue found in multiple skills
- Performing quarterly skill maintenance reviews

---

## Common Pitfalls

### 1. Forgetting to Update Japanese Version

**Problem**: Revise English SKILL.md but forget to update references/SKILL.ja.md, causing sync drift.

**Solution**: Always check for Japanese version after editing English.

```python
# ✅ CORRECT - Auto-check for JA version
def revise_skill(skill_path: Path, changes: dict):
    # Apply changes to English
    apply_changes(skill_path, changes)
    
    # Check for Japanese version
    ja_path = skill_path.parent / "references" / "SKILL.ja.md"
    if ja_path.exists():
        print("⚠️ WARNING: Japanese version exists")
        print("   Remember to update references/SKILL.ja.md with equivalent changes")
        print("\nChanged sections:")
        for section in changes.get('sections', []):
            print(f"  - {section}")
```

### 2. Logging Trivial Changes

**Problem**: CHANGELOG.md gets cluttered with typo fixes and formatting changes.

**Solution**: Only log substantial changes.

```markdown
❌ WRONG CHANGELOG:
## Version 1.2.1
- Fixed: typo "performace" → "performance"
- Updated: indentation in code block
- Changed: comma placement
- Fixed: typo "recieve" → "receive"

✅ CORRECT CHANGELOG:
## Version 1.2.0
- Changed: Sync method → Async/await pattern
- Added: Pattern 8 - Circuit Breaker
- Fixed: Memory leak in ViewModelBase
```

### 3. Not Using author Field for Detection

**Problem**: Manually tracking which skills are system-created vs. third-party.

**Solution**: Use `author: RyoMurakami1983` field programmatically.

```python
# ❌ WRONG - Manual tracking
SYSTEM_SKILLS = ["skill-writing-guide", "skill-quality-validation"]  # Hard-coded

# ✅ CORRECT - Automatic detection
def is_system_skill(path: Path) -> bool:
    frontmatter = extract_frontmatter(path)
    return frontmatter.get('author') == 'RyoMurakami1983'
```

---

## Quick Reference

### Revision Workflow

```
1. Open SKILL.md to revise

2. Check author field
   ├─ author: RyoMurakami1983? → System skill (enhanced support)
   └─ Other/none → Standard revision

3. Make changes to English SKILL.md

4. Is change substantial?
   ├─ Yes (content/functionality) → Continue
   └─ No (typo/format) → Skip to step 7

5. Update CHANGELOG.md
   - Category: Added/Changed/Fixed/etc.
   - Description: 1-line summary (max 100 chars)

6. If system skill: Check for references/SKILL.ja.md
   ├─ Exists → Update Japanese version
   └─ Missing → English only

7. Run skill-quality-validation

8. Bump version in frontmatter
   - Breaking? → MAJOR
   - Feature? → MINOR
   - Bug fix? → PATCH

9. Commit changes
```

### System Skill Indicators

✅ **System Skill** (`author: RyoMurakami1983`):
- Check for references/SKILL.ja.md
- Verify CHANGELOG.md exists (if > 5 versions)
- Sync English & Japanese
- Enhanced validation

ℹ️ **Non-System Skill**:
- English only revision
- Standard changelog (in SKILL.md)
- Basic validation

---

## Best Practices Summary

1. **Detect System Skills** - Use `author: RyoMurakami1983` field programmatically
2. **Log Substantial Only** - Skip typos, formatting; log content/functionality changes
3. **1-Line Changelog** - "Category: Brief description (max 100 chars)"
4. **Sync EN/JA** - Always update both versions for system skills
5. **CHANGELOG.md** - Move from SKILL.md when > 50 lines
6. **Semantic Versioning** - MAJOR.MINOR.PATCH based on change type
7. **Validate After Revision** - Run quality check before publishing
8. **Commit Atomically** - Each version bump = one commit
9. **Reference Changes** - Link to related issues/PRs in changelog
10. **Backward Compatibility** - Deprecate before removing features

---

## Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [skill-quality-validation](../skill-quality-validation/SKILL.md) - Validate revisions
- [CHANGELOG_TEMPLATE.md](assets/CHANGELOG_TEMPLATE.md) - Changelog template

---

## Changelog

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
