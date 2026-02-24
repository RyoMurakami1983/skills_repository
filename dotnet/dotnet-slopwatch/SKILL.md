---
name: dotnet-slopwatch
description: >
  Two-layer slop prevention for .NET: code-level detection via Slopwatch CLI (SW-xxx)
  and architectural anti-pattern catalog (SLOP-xxx).
  Use when validating LLM-generated C# code, checking for layer boundary violations,
  or integrating anti-slop quality gates into CI/CD.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, quality, llm, anti-cheat, slopwatch]
  invocable: true
---

# Slopwatch: LLM Anti-Cheat for .NET

Two-layer slop prevention system for .NET projects:

- **Code-Level (SW-xxx)** — Automated detection via Slopwatch CLI tool (disabled tests, empty catches, warning suppression)
- **Architecture-Level (SLOP-xxx)** — Anti-pattern catalog requiring human/LLM judgment (layer violations, responsibility leaks)

## When to Use This Skill

Use this skill when:
- Validating LLM-generated C# code changes for reward hacking patterns
- Checking whether Presentation layer code contains domain logic that belongs in Application/Domain layers
- Setting up Slopwatch as a Claude Code post-edit hook
- Integrating anti-slop quality gates into GitHub Actions or Azure Pipelines
- Establishing a baseline for existing .NET projects with technical debt
- Reviewing architecture decisions in layered .NET applications (DDD, Clean Architecture)

---

## Related Skills

- **`crap-analysis`** — Identify high-risk code combining complexity with low coverage
- **`modern-csharp-coding-standards`** — The coding standards Slopwatch helps enforce
- **`dotnet-local-tools`** — Manage Slopwatch as a versioned local tool

---

## Core Principles

1. **Zero Tolerance for New Slop** — Existing issues are baselined; new shortcuts are blocked unconditionally (基礎と型)
2. **Fix, Don't Suppress** — Every flagged pattern requires a proper fix, not a workaround (温故知新)
3. **LLMs Are Not Special** — Same quality rules apply to human and AI-generated code (ニュートラル)
4. **Baseline Isolates Legacy** — Pre-existing debt is acknowledged but separated from new changes (余白の設計)

---

## Workflow: Install & Use Slopwatch

### Step 1 — Install Slopwatch

Add to `.config/dotnet-tools.json` as a local tool:

```json
{
  "version": 1,
  "isRoot": true,
  "tools": {
    "slopwatch.cmd": {
      "version": "0.2.0",
      "commands": ["slopwatch"],
      "rollForward": false
    }
  }
}
```

```bash
dotnet tool restore
```

> **Values**: 継続は力（ツールをバージョン管理し再現可能に）

### Step 2 — Establish Baseline

Create a baseline of existing issues before using Slopwatch on a project:

```bash
slopwatch init
git add .slopwatch/baseline.json
git commit -m "chore: add slopwatch baseline"
```

Legacy code may have pre-existing patterns. The baseline ensures only **new** slop is caught.

> **Values**: 余白の設計（レガシーを認め、新規の品質を守る）

### Step 3 — Run After Every Code Change

```bash
# Standard analysis
slopwatch analyze

# Strict mode — fail on warnings too (recommended for LLM sessions)
slopwatch analyze --fail-on warning
```

When Slopwatch flags an issue, **do not ignore it**:

1. Understand why the LLM took the shortcut
2. Request a proper fix — be specific about what's wrong
3. Verify the fix doesn't introduce different slop

```
❌ SW001 [Error]: Disabled test detected
   File: tests/MyApp.Tests/OrderTests.cs:45
   Pattern: [Fact(Skip="Test is flaky")]

→ "Fix the flaky test's timing issue, don't disable it."
```

> **Values**: 基礎と型（根本原因の修正が型）

### Step 4 — Configure Claude Code Hook

Add Slopwatch as a post-edit hook in `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "slopwatch analyze -d . --hook",
            "timeout": 60000
          }
        ]
      }
    ]
  }
}
```

The `--hook` flag analyzes only git-dirty files, outputs errors to stderr, and blocks the edit on failures.

> **Values**: 成長の複利（自動ガードレールで品質を仕組み化）

### Step 5 — Add to CI/CD Pipeline

Use as a quality gate in GitHub Actions:

```yaml
jobs:
  slopwatch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'
      - run: dotnet tool install --global Slopwatch.Cmd
      - run: slopwatch analyze -d . --fail-on warning
```

> **Values**: 基礎と型（品質ゲートを基盤に組み込む）

---

## Code-Level Detection Rules (SW-xxx)

Automated rules enforced by the Slopwatch CLI tool.

| Rule | Severity | Pattern | Example |
|------|----------|---------|---------|
| SW001 | Error | Disabled tests | `[Fact(Skip="flaky")]`, `#if false` |
| SW002 | Warning | Warning suppression | `#pragma warning disable CS8618` |
| SW003 | Error | Empty catch blocks | `catch (Exception) { }` |
| SW004 | Warning | Arbitrary delays | `await Task.Delay(1000);` in tests |
| SW005 | Warning | Project file slop | `<NoWarn>CS1591</NoWarn>` |
| SW006 | Warning | CPM bypass | Inline `Version="1.0.0"` |

---

## Architectural Slop Patterns (SLOP-xxx)

Design-level anti-patterns requiring human or LLM judgment. These cannot be detected by static analysis alone — they require understanding of architectural intent.

### SLOP-001: Layer Boundary Violation

**Severity**: Error

**Symptom**: Upper layer (Presentation/ViewModel) uses `string.Split`, `Substring`, or `Regex` to reconstruct domain values from a concatenated string received from a lower layer.

**Why It's Dangerous**:
- Relies on implicit assumptions about string format (delimiters, order, escaping)
- Domain knowledge leaks into Presentation layer ("steel type names can contain hyphens")
- Fragile under change: format changes break Presentation code silently

**Real-World Example** (MillScanSplitter PR#20):

```csharp
// ❌ SLOP-001: Presentation layer parsing domain values
// OcrValue = "25_10_29-394R072-9#SUH3-AIS-X578D"
var parts = ocrValue.Split('-');
var steelType = parts[2]; // Returns "9#SUH3" — WRONG (actual: "9#SUH3-AIS")
```

Steel type `9#SUH3-AIS` contains a hyphen, so naive splitting destroys the value.

```csharp
// ✅ Fix: Extend Application layer response with structured fields
record ProcessDocumentComparisonRow(
    // ... existing fields ...
    string ManufacturingNumber,  // Set from ExtractedItem (Domain)
    string SteelType,
    string HeatNo
);
```

**Prescription**: If the upper layer needs data that isn't in the response, **extend the lower layer's response** — never reconstruct domain values by parsing strings.

**Checklist**:
- [ ] Does the new feature need data not in the current Application layer response?
- [ ] If yes, have structured fields been added to the response record?
- [ ] Is the Presentation layer free of `Split`/`Substring`/`Regex` on domain strings?

**Decision Rule**: "Does this `Split` require knowledge of domain structure to write?" → Yes = SLOP-001 violation. No = legitimate UI formatting.

> **Values**: 基礎と型（DDD layer boundaries are foundational — violating them creates hidden fragility）

---

## Good Practices

### 1. Strict Mode for LLM Sessions

**What**: Elevate all rules to error severity during AI-assisted coding.

**Why**: LLMs are more likely to introduce slop than humans — higher guard rails are justified.

**Values**: 基礎と型（厳格な型でスロップを排除）

### 2. Baseline on First Use

**What**: Always run `slopwatch init` before first `analyze` on existing projects.

**Why**: Without a baseline, every legacy issue triggers false positives, eroding trust in the tool.

**Values**: 余白の設計（既存の技術的負債を認識して分離）

---

## Common Pitfalls

### 1. Updating Baseline to Silence Warnings

**Problem**: Running `--update-baseline` whenever Slopwatch flags an issue.

**Solution**: Only update baseline for genuinely justified exceptions (third-party constraints, generated code). Document the reason in a code comment.

### 2. Disabling Rules Instead of Fixing Code

**Problem**: Setting `"enabled": false` for noisy rules.

**Solution**: Fix the underlying code. If a rule produces false positives, report it upstream; don't disable the guard rail.

---

## Anti-Patterns

### "We'll Fix It Later"

**What**: Accepting slop with a plan to revisit.

**Why It's Wrong**: "Later" never comes. The shortcut becomes permanent technical debt.

**Better Approach**: Fix the actual problem now. If time-constrained, create a tracked issue and keep the guard rail active.

### Slop-Fixing with More Slop

**What**: Fixing a disabled test by adding `Task.Delay(2000)` instead of fixing the race condition.

**Why It's Wrong**: Replaces one slop pattern (SW001) with another (SW004).

**Better Approach**: Identify and fix the root cause (race condition, timing dependency, shared state).

---

## Quick Reference

```bash
# First time setup
slopwatch init
git add .slopwatch/baseline.json

# After every LLM code change
slopwatch analyze

# Strict mode (recommended)
slopwatch analyze --fail-on warning

# Hook mode (git dirty files only)
slopwatch analyze -d . --hook

# Update baseline (rare, document why)
slopwatch analyze --update-baseline

# JSON output for tooling
slopwatch analyze --output json
```

### Override Decision Table

| Scenario | Action | Requirement |
|----------|--------|-------------|
| Third-party forces pattern | Update baseline | Code comment explaining why |
| Generated code (not editable) | Add to exclude list | Document in config |
| Intentional rate limiting | Update baseline | Code comment, not in test |
| "Test is flaky" | ❌ Never override | Fix the flakiness |
| "Warning is annoying" | ❌ Never override | Fix the code |

---

## Resources

- [Slopwatch NuGet Package](https://www.nuget.org/packages/Slopwatch.Cmd)
- [dotnet-local-tools](../dotnet-local-tools/SKILL.md) — Managing local .NET tools
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution

---
