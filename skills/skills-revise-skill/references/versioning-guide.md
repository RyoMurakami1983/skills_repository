# Skill Versioning Guide

Comprehensive guide for managing skill versions using semantic versioning principles.

## Semantic Versioning Basics

**Format**: MAJOR.MINOR.PATCH (e.g., 2.3.1)

- **MAJOR** (X.0.0): Breaking changes, incompatible API
- **MINOR** (0.X.0): New features, backward-compatible additions
- **PATCH** (0.0.X): Bug fixes, typos, minor improvements

## Version Bump Decision Tree

```
Is the change breaking existing usage?
├─ YES → MAJOR bump (1.x.x → 2.0.0)
│   Examples:
│   - Changed method signature
│   - Removed public API
│   - Renamed core concepts
│   - Changed file structure
│
└─ NO → Is new functionality added?
    ├─ YES → MINOR bump (x.1.x → x.2.0)
    │   Examples:
    │   - Added new pattern
    │   - New configuration option
    │   - Additional examples
    │   - New section
    │
    └─ NO → Is it a bug fix or improvement?
        ├─ YES → PATCH bump (x.x.1 → x.x.2)
        │   Examples:
        │   - Fixed incorrect example
        │   - Corrected logic error
        │   - Updated deprecated API
        │   - Performance improvement
        │
        └─ NO → No version bump needed
            Examples:
            - Typo fixes
            - Formatting changes
            - Grammar corrections
```

## Detailed Version Bump Rules

### MAJOR Bumps (Breaking Changes)

#### When to Bump MAJOR

1. **API Signature Changes**
   ```python
   # v1.x.x
   def process_data(data: str) -> dict:
       pass
   
   # v2.0.0 - Breaking: parameter type changed
   def process_data(data: list) -> dict:
       pass
   ```

2. **Removed Functionality**
   ```markdown
   <!-- v1.x.x had "Pattern 5: Legacy Approach" -->
   <!-- v2.0.0 removed it completely -->
   ```

3. **Restructured Content**
   ```
   v1.x.x structure:
   - Pattern 1: Basic
   - Pattern 2: Advanced
   
   v2.0.0 structure:
   - Section A: Getting Started
     - Pattern 1: Basic
   - Section B: Advanced Topics
     - Pattern 2: Advanced
   ```

4. **Changed Core Concepts**
   ```
   v1.x.x: "Use synchronous methods"
   v2.0.0: "Always use async/await" (fundamentally different approach)
   ```

#### Migration Guide for MAJOR Bumps

When bumping MAJOR version, create `MIGRATION.md`:

```markdown
# Migration Guide: v1.x to v2.0

## Breaking Changes

### 1. Method Signature Changed

**Old (v1.x)**:
```python
process_data(data: str)
```

**New (v2.0)**:
```python
process_data(data: list)
```

**Migration Steps**:
1. Convert string data to list: `data.split(',')`
2. Update all calls to `process_data()`

### 2. Pattern 5 Removed

**Old (v1.x)**: Used Pattern 5 for legacy systems

**New (v2.0)**: Pattern 5 removed; use Pattern 3 instead

**Migration Steps**:
1. Identify uses of Pattern 5
2. Replace with Pattern 3 equivalent
3. Update tests
```

### MINOR Bumps (New Features)

#### When to Bump MINOR

1. **Added New Pattern**
   ```markdown
   v1.2.0 → v1.3.0
   - Added: Pattern 8 - Circuit Breaker implementation
   ```

2. **New Configuration Option**
   ```python
   # v1.2.0 - Only had 'timeout' option
   config = {"timeout": 30}
   
   # v1.3.0 - Added 'retry_count' (backward compatible)
   config = {"timeout": 30, "retry_count": 3}
   ```

3. **Additional Examples**
   ```markdown
   v1.2.0: Pattern 3 had 2 examples
   v1.3.0: Pattern 3 now has 5 examples (3 new)
   ```

4. **New Section**
   ```markdown
   v1.2.0: Had "Core Principles" and "Patterns"
   v1.3.0: Added "Best Practices" section
   ```

#### Backward Compatibility Check

Before MINOR bump, verify:

- [ ] Existing code examples still work
- [ ] Old configuration still valid
- [ ] Previous patterns unchanged
- [ ] Links/references still resolve

### PATCH Bumps (Bug Fixes)

#### When to Bump PATCH

1. **Incorrect Code Example**
   ```python
   # v1.2.0 - Bug: missing await
   result = async_function()
   
   # v1.2.1 - Fixed
   result = await async_function()
   ```

2. **Typo in Technical Content**
   ```python
   # v1.2.0 - Typo affects meaning
   # "Use synchronous I/O"  # Wrong advice
   
   # v1.2.1 - Fixed
   # "Use asynchronous I/O"  # Correct advice
   ```

3. **Updated Deprecated API**
   ```python
   # v1.2.0 - Using deprecated API
   import warnings
   warnings.warn("old way")
   
   # v1.2.1 - Updated to new API
   import logging
   logging.warning("new way")
   ```

4. **Clarification**
   ```markdown
   v1.2.0: "Use caching" (vague)
   v1.2.1: "Use Redis for session caching" (specific)
   ```

### No Bump (Trivial Changes)

Don't bump version for:

- Spelling/grammar fixes (non-technical)
- Whitespace/formatting
- Link updates (same content, different URL)
- Improved wording (same meaning)

## Version Lifecycle

### Pre-release Versions

For testing before official release:

- **Alpha**: `2.0.0-alpha.1` - Early testing, unstable
- **Beta**: `2.0.0-beta.1` - Feature complete, testing
- **RC**: `2.0.0-rc.1` - Release candidate, final testing

### Deprecation Strategy

When removing features:

```
v1.5.0: Add deprecation warning for Pattern X
v1.6.0: Pattern X still works but marked deprecated
v1.7.0: Pattern X still works, warning shown
v2.0.0: Pattern X removed (MAJOR bump)
```

Example deprecation notice:

```markdown
## Pattern 5: Legacy Approach

> **⚠️ DEPRECATED**: This pattern is deprecated as of v1.5.0 and will be removed in v2.0.0.
> Use Pattern 3 instead. See [migration guide](MIGRATION.md#pattern-5-to-pattern-3).

<!-- Keep old content for reference -->
```

## CHANGELOG.md Best Practices

### Format

```markdown
# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Pattern 9: Rollback strategies for failed deployments

### Changed
- Improved examples in Pattern 3 with async/await

## [2.0.0] - 2026-02-15

### Added
- Pattern 8: Circuit Breaker implementation
- Migration guide for v1.x to v2.0

### Changed
- **BREAKING**: Restructured content into sections
- **BREAKING**: Renamed Pattern 5 to Pattern 5A

### Deprecated
- Pattern 7 will be removed in v3.0.0

### Removed
- Pattern 6 (moved to separate skill)

### Fixed
- Corrected async example in Pattern 3

## [1.5.0] - 2026-01-20

### Added
- Pattern 7: Retry policies with Polly

### Deprecated
- Pattern 5: Use Pattern 3 instead (removal in v2.0.0)

## [1.0.0] - 2026-01-01

### Added
- Initial release with 5 core patterns

[Unreleased]: https://github.com/user/repo/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/user/repo/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/user/repo/compare/v1.0.0...v1.5.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

### Categories

Use these standard categories:

- **Added**: New features, patterns, sections
- **Changed**: Modifications to existing content
- **Deprecated**: Soon-to-be-removed features
- **Removed**: Deleted features
- **Fixed**: Bug fixes, corrections
- **Security**: Vulnerability fixes

## Automated Version Management

### Python Script

```python
from packaging import version
from typing import List, Tuple

class VersionManager:
    def __init__(self, current_version: str):
        self.current = version.parse(current_version)
    
    def bump(self, bump_type: str) -> str:
        """Bump version by type"""
        major, minor, patch = self.current.release
        
        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
    
    def recommend_bump(self, changelog_entries: List[str]) -> Tuple[str, str]:
        """Recommend version bump based on changelog"""
        has_breaking = any(
            "BREAKING" in e or "breaking:" in e.lower()
            for e in changelog_entries
        )
        has_removed = any("Removed:" in e for e in changelog_entries)
        has_added = any("Added:" in e for e in changelog_entries)
        has_fixed = any("Fixed:" in e for e in changelog_entries)
        
        if has_breaking or has_removed:
            return "major", "Breaking changes detected"
        elif has_added:
            return "minor", "New features added"
        elif has_fixed:
            return "patch", "Bug fixes only"
        else:
            return "none", "No substantial changes"
    
    def validate_bump(self, new_version: str) -> bool:
        """Validate that new version is higher"""
        new_ver = version.parse(new_version)
        return new_ver > self.current

# Usage
manager = VersionManager("1.2.3")

# Manual bump
new_v = manager.bump("minor")  # → "1.3.0"

# Automated recommendation
entries = [
    "Added: Pattern 8 - Circuit Breaker",
    "Fixed: Memory leak in example"
]
bump_type, reason = manager.recommend_bump(entries)
print(f"Recommend {bump_type} bump: {reason}")  # → "minor bump: New features added"
```

## Version Comparison

### Valid Version Progressions

✅ **Correct**:
- 1.0.0 → 1.0.1 (patch)
- 1.0.0 → 1.1.0 (minor)
- 1.0.0 → 2.0.0 (major)
- 1.9.9 → 1.10.0 (minor, not 2.0.0)
- 1.9.9 → 2.0.0 (major)

❌ **Incorrect**:
- 1.0.0 → 1.0.0 (no change)
- 1.2.0 → 1.1.9 (downgrade)
- 1.0.0 → 1.0.2 (skipped 1.0.1)
- 1.0.0 → 3.0.0 (skipped 2.x)

## Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
