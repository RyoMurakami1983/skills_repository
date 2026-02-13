# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version 1.0.0 (YYYY-MM-DD)

- Initial release

---

## How to Use This Template

**Category Prefixes** (choose one):
- **Added**: New features, patterns, sections
- **Changed**: Modifications to existing functionality
- **Fixed**: Bug fixes, corrections
- **Removed**: Deleted features or sections
- **Deprecated**: Features marked for future removal
- **Updated**: Version updates, dependency upgrades

**Format**:
```
- Category: Brief description (max 100 characters)
```

**Examples**:
```markdown
## Version 1.2.0 (2026-02-15)

- Added: Pattern 8 - Circuit Breaker implementation with Polly
- Changed: Sync method → Async/await pattern for all API calls
- Fixed: Memory leak in ViewModelBase.Dispose() method
- Updated: Examples to .NET 8 and C# 12 syntax
- Deprecated: Old ConfigureServices pattern (use WebApplication.CreateBuilder)

## Version 1.1.0 (2026-01-20)

- Added: Pattern 7 - Retry policies with exponential backoff
- Changed: DI configuration examples to minimal API style
- Fixed: Incorrect using statement in Pattern 3 example
```

**Rules**:
1. One line per change
2. Max 100 characters per line
3. Use present tense ("Add" not "Added feature")
4. Be specific: include method/class names when relevant
5. Group by version with date (YYYY-MM-DD format)
6. Most recent version at top

**Substantial Changes Only**:
✅ Log: Content changes, new features, bug fixes, breaking changes
❌ Skip: Typos, formatting, grammar, punctuation
