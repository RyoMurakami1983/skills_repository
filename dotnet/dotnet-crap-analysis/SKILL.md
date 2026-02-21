---
name: dotnet-crap-analysis
description: >
  Analyze code coverage and CRAP (Change Risk Anti-Patterns) scores to identify
  high-risk .NET code. Use when evaluating test coverage, setting up OpenCover
  with ReportGenerator, or enforcing coverage thresholds in CI/CD pipelines.
metadata:
  author: RyoMurakami1983
  tags: [crap, coverage, opencover, reportgenerator, dotnet, testing, ci-cd]
  invocable: false
---

# CRAP Score Analysis

A concise guardrail for collecting code coverage and calculating CRAP (Change Risk Anti-Patterns) scores in .NET projects. Covers OpenCover format collection, ReportGenerator HTML reports with Risk Hotspots, coverage thresholds, and CI/CD integration. Targets .NET 8+ with coverlet via `dotnet test`.

**Acronyms**: CRAP (Change Risk Anti-Patterns), CI/CD (Continuous Integration / Continuous Delivery), DI (Dependency Injection).

## When to Use This Skill

- Evaluating code quality and test coverage metrics before modifying existing code
- Identifying high-risk methods that need immediate refactoring or additional testing
- Setting up OpenCover format coverage collection for a new .NET project solution
- Configuring ReportGenerator to produce HTML reports with Risk Hotspot analysis
- Establishing line and branch coverage thresholds for CI/CD pipeline enforcement
- Prioritizing which untested code paths to cover based on CRAP score rankings
- Interpreting Risk Hotspot reports to decide between testing and refactoring actions

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-project-structure` | .NET solution layout, project references, layer separation |
| `dotnet-testcontainers` | Integration test infrastructure with container-based databases |

## Core Principles

1. **Complexity × Coverage = Risk** — The CRAP formula `Complexity × (1 - Coverage)²` quantifies risk by combining cyclomatic complexity with test coverage. Why: complexity alone is insufficient; a complex method with 100% coverage is safer than a simple untested one.
2. **OpenCover Format Required** — Always collect coverage in OpenCover format because it includes cyclomatic complexity metrics. Why: Cobertura format lacks complexity data and cannot produce CRAP scores.
3. **Exclude Non-Production Code** — Configure `coverage.runsettings` to exclude test assemblies, generated code, migrations, and auto-properties. Why: measuring coverage of non-production code inflates metrics and hides real gaps.
4. **Threshold Enforcement in CI** — Define minimum line coverage (80%), branch coverage (60%), and maximum CRAP score (30) as automated gates. Why: manual review alone cannot prevent coverage regression at scale.
5. **Risk Hotspots Drive Action** — Use ReportGenerator Risk Hotspots to prioritize testing effort on methods with highest CRAP scores. Why: testing high-risk code first maximizes safety per unit of effort.

> **Values**: 基礎と型の追求（CRAP スコアという「型」でリスクを定量化し、テスト戦略の基盤を築く）, 温故知新（カバレッジ計測の基本原則を守りつつ、最新ツールチェーンを活用する）

## Workflow: Analyze CRAP Scores

### Step 1: Create coverage.runsettings

Create a `coverage.runsettings` file in your repository root. Use OpenCover format to include cyclomatic complexity for CRAP score calculation.

```xml
<?xml version="1.0" encoding="utf-8" ?>
<RunSettings>
  <DataCollectionRunSettings>
    <DataCollectors>
      <DataCollector friendlyName="XPlat code coverage">
        <Configuration>
          <!-- OpenCover format includes cyclomatic complexity -->
          <Format>cobertura,opencover</Format>
          <Exclude>[*.Tests]*,[*.Benchmark]*,[*.Migrations]*</Exclude>
          <ExcludeByAttribute>Obsolete,GeneratedCodeAttribute,CompilerGeneratedAttribute,ExcludeFromCodeCoverageAttribute</ExcludeByAttribute>
          <ExcludeByFile>**/obj/**/*,**/*.g.cs,**/*.designer.cs,**/*.razor.g.cs,**/Migrations/**/*</ExcludeByFile>
          <IncludeTestAssembly>false</IncludeTestAssembly>
          <SingleHit>false</SingleHit>
          <UseSourceLink>true</UseSourceLink>
          <SkipAutoProps>true</SkipAutoProps>
        </Configuration>
      </DataCollector>
    </DataCollectors>
  </DataCollectionRunSettings>
</RunSettings>
```

| Option | Purpose | Why |
|--------|---------|-----|
| `Format` | Must include `opencover` | Complexity metrics for CRAP |
| `Exclude` | Skip test/benchmark assemblies | Not production code |
| `ExcludeByAttribute` | Skip generated and excluded code | Inflates coverage metrics |
| `SkipAutoProps` | Ignore auto-property branches | Trivial, not worth measuring |

> **Values**: 基礎と型の追求（runsettings という設定の「型」を最初に整えることで、正確な計測基盤を確立する）

### Step 2: Install ReportGenerator

Install ReportGenerator as a local tool for generating HTML reports with Risk Hotspots.

```json
{
  "version": 1,
  "isRoot": true,
  "tools": {
    "dotnet-reportgenerator-globaltool": {
      "version": "5.4.5",
      "commands": ["reportgenerator"],
      "rollForward": false
    }
  }
}
```

```bash
# Restore local tools from .config/dotnet-tools.json
dotnet tool restore
```

> **Values**: 継続は力（ツールをローカル管理して、チーム全員が同じバージョンで再現可能な計測を行う）

### Step 3: Collect Coverage Data

Run tests with OpenCover coverage collection enabled.

```bash
# ✅ Clean previous results and collect fresh coverage
rm -rf coverage/ TestResults/

dotnet test tests/MyApp.Tests.Unit \
  --settings coverage.runsettings \
  --collect:"XPlat Code Coverage" \
  --results-directory ./TestResults
```

Use `--results-directory` to consolidate output from multiple test projects into a single location. Why: ReportGenerator merges all XML files found in the glob pattern.

> **Values**: ニュートラルな視点（すべてのテストプロジェクトを偏りなく計測し、全体像を把握する）

### Step 4: Generate HTML Report with Risk Hotspots

Generate reports that include Risk Hotspots showing CRAP scores per method.

```bash
# ✅ Generate HTML report with Risk Hotspots
dotnet reportgenerator \
  -reports:"TestResults/**/coverage.opencover.xml" \
  -targetdir:"coverage" \
  -reporttypes:"Html;TextSummary;MarkdownSummaryGithub"
```

| Report Type | Output File | Purpose |
|-------------|-------------|---------|
| `Html` | `coverage/index.html` | Interactive report with Risk Hotspots |
| `TextSummary` | `coverage/Summary.txt` | Quick terminal review |
| `MarkdownSummaryGithub` | `coverage/SummaryGithub.md` | PR comment integration |

> **Values**: 成長の複利（レポートを可視化することで、チーム全体がリスクを共有し品質意識を高める）

### Step 5: Interpret Risk Hotspots and Take Action

Read the Risk Hotspots section to identify methods sorted by CRAP score.

**CRAP Score Formula**: `Complexity × (1 - Coverage)²`

| Method | Complexity | Coverage | CRAP | Action |
|--------|------------|----------|------|--------|
| `GetUserId()` | 1 | 0% | **1** | Low risk — simple code |
| `ParseToken()` | 54 | 52% | **12.4** | Acceptable — add more tests |
| `ValidateForm()` | 20 | 0% | **20** | Test immediately |
| `ProcessOrder()` | 45 | 20% | **28.8** | High risk — test or refactor |
| `ImportData()` | 80 | 10% | **64.8** | ❌ Critical — refactor and test |

**Decision guide:**

| CRAP Score | Risk Level | Action Required |
|------------|------------|-----------------|
| < 5 | Low | Well-tested, safe to modify |
| 5–30 | Medium | Acceptable but increase coverage |
| > 30 | High | ❌ Needs tests or refactoring before changes |

> **Values**: 余白の設計（CRAP スコアを読み解く力を養い、テスト戦略に余白と優先順位を設ける）

### Step 6: Integrate with CI/CD Pipeline

Automate coverage collection and threshold enforcement in GitHub Actions.

```yaml
name: Coverage

on:
  pull_request:
    branches: [main, dev]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'

      - name: Restore tools
        run: dotnet tool restore

      - name: Run tests with coverage
        run: |
          dotnet test \
            --settings coverage.runsettings \
            --collect:"XPlat Code Coverage" \
            --results-directory ./TestResults

      - name: Generate report
        run: |
          dotnet reportgenerator \
            -reports:"TestResults/**/coverage.opencover.xml" \
            -targetdir:"coverage" \
            -reporttypes:"Html;MarkdownSummaryGithub;Cobertura"

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/

      - name: Add coverage to PR
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          path: coverage/SummaryGithub.md
```

> **Values**: 継続は力（CI パイプラインで自動計測をコツコツ積み上げ、品質の複利成長を実現する）

## Good Practices

- ✅ Use OpenCover format for all coverage collection to enable CRAP score calculation
- ✅ Implement `coverage.runsettings` with explicit exclusion patterns for non-production code
- ✅ Use ReportGenerator local tool with pinned version for reproducible report generation
- ✅ Implement coverage threshold gates in CI/CD to prevent regression automatically
- ✅ Use Risk Hotspots to prioritize testing effort on highest-CRAP methods first
- ✅ Implement `MarkdownSummaryGithub` report type for automatic PR comment integration
- ✅ Use `--results-directory` to consolidate coverage from multiple test projects
- ✅ Avoid lowering thresholds for new features — meet standards from the start

## Common Pitfalls

1. **Using Cobertura Without OpenCover** — Collecting only Cobertura format loses cyclomatic complexity metrics. CRAP scores cannot be calculated. Fix: always include `opencover` in the `Format` configuration element.
2. **Measuring Test Assembly Coverage** — Including test project code in coverage inflates metrics and hides real production code gaps. Fix: set `IncludeTestAssembly` to `false` and use `Exclude` patterns for test assemblies.
3. **Ignoring Auto-Property Branches** — Auto-properties generate trivial branches that add noise to branch coverage. Fix: set `SkipAutoProps` to `true` in the runsettings configuration.
4. **Manual Threshold Enforcement** — Relying on developers to manually check coverage leads to regression. Fix: implement automated threshold gates in CI/CD pipelines with clear failure messages.
5. **Lowering Thresholds for Convenience** — Reducing coverage targets because code is "too hard to test" masks design problems. Fix: refactor the code to improve testability instead of lowering the bar.

## Anti-Patterns

### ❌ Cobertura-Only Collection → ✅ OpenCover Format

```xml
<!-- ❌ BAD — no complexity metrics, no CRAP scores -->
<Format>cobertura</Format>

<!-- ✅ GOOD — includes cyclomatic complexity for CRAP -->
<Format>cobertura,opencover</Format>
```

Why: the entire CRAP analysis architecture depends on cyclomatic complexity data that only OpenCover provides.

### ❌ Measuring Everything → ✅ Targeted Exclusions

```xml
<!-- ❌ BAD — inflated coverage from test and generated code -->
<IncludeTestAssembly>true</IncludeTestAssembly>

<!-- ✅ GOOD — measure only production code -->
<IncludeTestAssembly>false</IncludeTestAssembly>
<Exclude>[*.Tests]*,[*.Benchmark]*,[*.Migrations]*</Exclude>
<ExcludeByAttribute>GeneratedCodeAttribute,CompilerGeneratedAttribute,ExcludeFromCodeCoverageAttribute</ExcludeByAttribute>
```

Why: including non-production code in coverage metrics creates a false sense of safety and hides real risk.

### ❌ Ignoring Risk Hotspots → ✅ Prioritized Testing

```text
# ❌ BAD — writing tests for simple getters while ignoring high-CRAP methods
Test: GetUserId()        (CRAP: 1)   ← already safe
Test: GetCustomerName()  (CRAP: 1)   ← already safe

# ✅ GOOD — test high-CRAP methods first
Test: ImportData()       (CRAP: 64.8) ← critical risk resolved
Test: ValidateToken()    (CRAP: 32.0) ← high risk resolved
```

Why: testing effort on low-risk code has diminishing returns; focus on high-CRAP methods to maximize safety per effort.

## Quick Reference

### Coverage Threshold Standards

| Metric | New Code | Legacy Code | Action |
|--------|----------|-------------|--------|
| Line Coverage | 80%+ | 60%+ (improve gradually) | Enforce in CI |
| Branch Coverage | 60%+ | 40%+ (improve gradually) | Enforce in CI |
| Maximum CRAP | 30 | Document exceptions | Refactor or test |

### CRAP Score Decision Table

| CRAP Score | Risk | Developer Action |
|------------|------|------------------|
| < 5 | Low | Safe to modify — well-tested code |
| 5–30 | Medium | Add tests before major changes |
| > 30 | High | Refactor to reduce complexity or add tests |

### One-Liner Analysis Workflow

```bash
# Full analysis: clean → test → report → view
rm -rf coverage/ TestResults/ && \
dotnet test --settings coverage.runsettings \
  --collect:"XPlat Code Coverage" \
  --results-directory ./TestResults && \
dotnet reportgenerator \
  -reports:"TestResults/**/coverage.opencover.xml" \
  -targetdir:"coverage" \
  -reporttypes:"Html;TextSummary" && \
cat coverage/Summary.txt
```

### Exclusion Pattern Reference

| Pattern | Reason |
|---------|--------|
| `[*.Tests]*` | Test assemblies are not production code |
| `[*.Benchmark]*` | Benchmark projects skew metrics |
| `GeneratedCodeAttribute` | Source generator output |
| `ExcludeFromCodeCoverageAttribute` | Explicit developer opt-out |
| `*.g.cs`, `*.designer.cs` | Generated and designer files |
| `**/Migrations/**/*` | EF Core auto-generated migrations |

## Resources

- [Coverlet Documentation](https://github.com/coverlet-coverage/coverlet) — .NET cross-platform coverage library
- [ReportGenerator](https://github.com/danielpalme/ReportGenerator) — HTML report generation with Risk Hotspots
- [CRAP Score Original Paper](http://www.artima.com/weblogs/viewpost.jsp?thread=215899) — Alberto Savoia's original CRAP metric paper
- [dotnet test Coverage Collection](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-code-coverage) — Microsoft documentation for coverage collection
