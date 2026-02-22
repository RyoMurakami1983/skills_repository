---
name: dotnet-crap-analysis
description: >
  コードカバレッジと CRAP（Change Risk Anti-Patterns）スコアを分析して
  高リスクな .NET コードを特定する。テストカバレッジの評価、OpenCover と
  ReportGenerator のセットアップ、CI/CD でのカバレッジ閾値適用時に使用。
  Use when evaluating coverage, setting up OpenCover, or enforcing thresholds.
metadata:
  author: RyoMurakami1983
  tags: [crap, coverage, opencover, reportgenerator, dotnet, testing, ci-cd]
  invocable: false
---

<!-- このドキュメントは dotnet-crap-analysis の日本語版です。英語版: ../SKILL.md -->

# CRAP Score Analysis

.NET プロジェクトにおけるコードカバレッジ収集と CRAP（Change Risk Anti-Patterns）スコア計算のための簡潔なガードレール。OpenCover 形式の収集、ReportGenerator による Risk Hotspots 付き HTML レポート、カバレッジ閾値、CI/CD 統合をカバーします。.NET 8+ で coverlet を使用した `dotnet test` を対象とします。

## When to Use This Skill

- 既存コードを変更する前にコード品質とテストカバレッジのメトリクスを評価する
- リファクタリングや追加テストが必要な高リスクメソッドを特定する
- 新しい .NET プロジェクトソリューションに OpenCover 形式のカバレッジ収集を設定する
- Risk Hotspot 分析付き HTML レポートを生成するために ReportGenerator を設定する
- CI/CD パイプライン適用のためにラインカバレッジとブランチカバレッジの閾値を設定する
- CRAP スコアランキングに基づいてテストすべき未テストコードパスの優先順位を決める
- テストとリファクタリングのどちらを行うかを判断するために Risk Hotspot レポートを解釈する

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-project-structure` | .NET ソリューションレイアウト、プロジェクト参照、レイヤー分離 |
| `dotnet-testcontainers` | コンテナベースデータベースによる統合テストインフラ |

## Core Principles

1. **Complexity × Coverage = Risk** — CRAP の公式 `Complexity × (1 - Coverage)²` は循環的複雑度とテストカバレッジを組み合わせてリスクを定量化する。複雑度だけでは不十分。カバレッジ 100% の複雑なメソッドは、テストされていない単純なメソッドより安全。
2. **OpenCover Format Required** — 循環的複雑度メトリクスを含む OpenCover 形式で常にカバレッジを収集する。Cobertura 形式には複雑度データがなく、CRAP スコアを算出できないため。
3. **Exclude Non-Production Code** — テストアセンブリ、生成コード、マイグレーション、自動プロパティを `coverage.runsettings` で除外する。非本番コードのカバレッジ計測はメトリクスを膨らませ、実際のギャップを隠すため。
4. **Threshold Enforcement in CI** — 最低ラインカバレッジ（80%）、ブランチカバレッジ（60%）、最大 CRAP スコア（30）を自動ゲートとして定義する。手動レビューだけではカバレッジの退行を大規模に防げないため。
5. **Risk Hotspots Drive Action** — ReportGenerator の Risk Hotspots を使用して CRAP スコアが最も高いメソッドにテスト工数を集中する。高リスクコードを最初にテストすることで、工数あたりの安全性を最大化するため。

> **Values**: 基礎と型の追求（CRAP スコアという「型」でリスクを定量化し、テスト戦略の基盤を築く）, 温故知新（カバレッジ計測の基本原則を守りつつ、最新ツールチェーンを活用する）

## Workflow: Analyze CRAP Scores

### Step 1: Create coverage.runsettings

リポジトリルートに `coverage.runsettings` ファイルを作成する。CRAP スコア計算のための循環的複雑度を含めるために OpenCover 形式を使用する。

```xml
<?xml version="1.0" encoding="utf-8" ?>
<RunSettings>
  <DataCollectionRunSettings>
    <DataCollectors>
      <DataCollector friendlyName="XPlat code coverage">
        <Configuration>
          <!-- OpenCover 形式は循環的複雑度を含む -->
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
| `Format` | `opencover` を含める必須設定 | CRAP 用の複雑度メトリクス |
| `Exclude` | テスト・ベンチマークアセンブリを除外 | 本番コードではない |
| `ExcludeByAttribute` | 生成コードと除外コードをスキップ | カバレッジメトリクスを膨張させる |
| `SkipAutoProps` | 自動プロパティのブランチを無視 | 計測する価値のない些細なもの |

> **Values**: 基礎と型の追求（runsettings という設定の「型」を最初に整えることで、正確な計測基盤を確立する）

### Step 2: Install ReportGenerator

Risk Hotspots 付き HTML レポートを生成するために ReportGenerator をローカルツールとしてインストールする。

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
# .config/dotnet-tools.json からローカルツールを復元
dotnet tool restore
```

> **Values**: 継続は力（ツールをローカル管理して、チーム全員が同じバージョンで再現可能な計測を行う）

### Step 3: Collect Coverage Data

OpenCover カバレッジ収集を有効にしてテストを実行する。

```bash
# ✅ 前回の結果をクリーンアップして新しいカバレッジを収集
rm -rf coverage/ TestResults/

dotnet test tests/MyApp.Tests.Unit \
  --settings coverage.runsettings \
  --collect:"XPlat Code Coverage" \
  --results-directory ./TestResults
```

`--results-directory` を使用して複数のテストプロジェクトの出力を単一の場所に統合する。ReportGenerator が glob パターンで見つかるすべての XML ファイルをマージするため。

> **Values**: ニュートラルな視点（すべてのテストプロジェクトを偏りなく計測し、全体像を把握する）

### Step 4: Generate HTML Report with Risk Hotspots

メソッドごとの CRAP スコアを示す Risk Hotspots を含むレポートを生成する。

```bash
# ✅ Risk Hotspots 付き HTML レポートを生成
dotnet reportgenerator \
  -reports:"TestResults/**/coverage.opencover.xml" \
  -targetdir:"coverage" \
  -reporttypes:"Html;TextSummary;MarkdownSummaryGithub"
```

| Report Type | Output File | Purpose |
|-------------|-------------|---------|
| `Html` | `coverage/index.html` | Risk Hotspots 付きインタラクティブレポート |
| `TextSummary` | `coverage/Summary.txt` | ターミナルでの素早い確認 |
| `MarkdownSummaryGithub` | `coverage/SummaryGithub.md` | PR コメント統合 |

> **Values**: 成長の複利（レポートを可視化することで、チーム全体がリスクを共有し品質意識を高める）

### Step 5: Interpret Risk Hotspots and Take Action

Risk Hotspots セクションを読み、CRAP スコア順にソートされたメソッドを特定する。

**CRAP スコア公式**: `Complexity × (1 - Coverage)²`

| Method | Complexity | Coverage | CRAP | Action |
|--------|------------|----------|------|--------|
| `GetUserId()` | 1 | 0% | **1** | 低リスク — シンプルなコード |
| `ParseToken()` | 54 | 52% | **12.4** | 許容範囲 — テスト追加 |
| `ValidateForm()` | 20 | 0% | **20** | 即座にテスト |
| `ProcessOrder()` | 45 | 20% | **28.8** | 高リスク — テストまたはリファクタ |
| `ImportData()` | 80 | 10% | **64.8** | ❌ 危険 — リファクタしてテスト |

**判断ガイド:**

| CRAP Score | Risk Level | 開発者のアクション |
|------------|------------|-------------------|
| < 5 | Low | 安全に変更可能 — 十分にテスト済み |
| 5–30 | Medium | 大きな変更前にテスト追加 |
| > 30 | High | ❌ 複雑度を下げるかテストを追加してから変更 |

> **Values**: 余白の設計（CRAP スコアを読み解く力を養い、テスト戦略に余白と優先順位を設ける）

### Step 6: Integrate with CI/CD Pipeline

GitHub Actions でカバレッジ収集と閾値適用を自動化する。

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

- ✅ CRAP スコア計算を有効にするため、すべてのカバレッジ収集に OpenCover 形式を使用する
- ✅ 非本番コード用の明示的な除外パターンを含む `coverage.runsettings` を実装する
- ✅ 再現可能なレポート生成のため、バージョン固定の ReportGenerator ローカルツールを使用する
- ✅ 退行を自動的に防止するため、CI/CD にカバレッジ閾値ゲートを実装する
- ✅ 最高 CRAP メソッドを優先してテスト工数を集中するため、Risk Hotspots を使用する
- ✅ PR コメント自動統合のため `MarkdownSummaryGithub` レポートタイプを実装する
- ✅ 複数テストプロジェクトのカバレッジを統合するため `--results-directory` を使用する
- ✅ 新機能の閾値は下げない — 最初から基準を満たす

## Common Pitfalls

1. **Using Cobertura Without OpenCover** — Cobertura 形式のみ収集すると循環的複雑度メトリクスが失われる。CRAP スコアは計算不可。Fix: `Format` 設定要素に常に `opencover` を含める。
2. **Measuring Test Assembly Coverage** — テストプロジェクトのコードをカバレッジに含めるとメトリクスが膨張し、本番コードの実際のギャップを隠す。Fix: `IncludeTestAssembly` を `false` に設定しテストアセンブリの `Exclude` パターンを使用する。
3. **Ignoring Auto-Property Branches** — 自動プロパティは些細なブランチを生成しブランチカバレッジにノイズを加える。Fix: runsettings 設定で `SkipAutoProps` を `true` に設定する。
4. **Manual Threshold Enforcement** — 開発者に手動でカバレッジを確認させることは退行につながる。Fix: 明確な失敗メッセージ付きの自動閾値ゲートを CI/CD パイプラインに実装する。
5. **Lowering Thresholds for Convenience** — 「テストが難しすぎる」という理由でカバレッジ目標を下げることは設計上の問題を隠す。Fix: 基準を下げる代わりに、テスト容易性を改善するためコードをリファクタリングする。

## Anti-Patterns

### ❌ Cobertura-Only Collection → ✅ OpenCover Format

```xml
<!-- ❌ BAD — 複雑度メトリクスなし、CRAP スコアなし -->
<Format>cobertura</Format>

<!-- ✅ GOOD — CRAP 用の循環的複雑度を含む -->
<Format>cobertura,opencover</Format>
```

CRAP 分析アーキテクチャ全体が OpenCover のみが提供する循環的複雑度データに依存するため。

### ❌ Measuring Everything → ✅ Targeted Exclusions

```xml
<!-- ❌ BAD — テストコードと生成コードによる膨張カバレッジ -->
<IncludeTestAssembly>true</IncludeTestAssembly>

<!-- ✅ GOOD — 本番コードのみ計測 -->
<IncludeTestAssembly>false</IncludeTestAssembly>
<Exclude>[*.Tests]*,[*.Benchmark]*,[*.Migrations]*</Exclude>
<ExcludeByAttribute>GeneratedCodeAttribute,CompilerGeneratedAttribute,ExcludeFromCodeCoverageAttribute</ExcludeByAttribute>
```

非本番コードをカバレッジメトリクスに含めると誤った安心感を生み、実際のリスクを隠すため。

### ❌ Ignoring Risk Hotspots → ✅ Prioritized Testing

```text
# ❌ BAD — 高 CRAP メソッドを無視してシンプルな getter をテスト
Test: GetUserId()        (CRAP: 1)   ← 既に安全
Test: GetCustomerName()  (CRAP: 1)   ← 既に安全

# ✅ GOOD — 高 CRAP メソッドを最初にテスト
Test: ImportData()       (CRAP: 64.8) ← 危険リスク解消
Test: ValidateToken()    (CRAP: 32.0) ← 高リスク解消
```

低リスクコードへのテスト工数は収穫逓減。高 CRAP メソッドに集中して工数あたりの安全性を最大化するため。

## Quick Reference

### Coverage Threshold Standards

| Metric | New Code | Legacy Code | Action |
|--------|----------|-------------|--------|
| Line Coverage | 80%+ | 60%+（段階的に改善） | CI で適用 |
| Branch Coverage | 60%+ | 40%+（段階的に改善） | CI で適用 |
| Maximum CRAP | 30 | 例外を文書化 | リファクタまたはテスト |

### CRAP Score Decision Table

| CRAP Score | Risk | 開発者のアクション |
|------------|------|-------------------|
| < 5 | Low | 安全に変更可能 — 十分にテスト済み |
| 5–30 | Medium | 大きな変更前にテスト追加 |
| > 30 | High | 複雑度を下げるかテストを追加 |

### One-Liner Analysis Workflow

```bash
# 完全分析: クリーン → テスト → レポート → 確認
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
| `[*.Tests]*` | テストアセンブリは本番コードではない |
| `[*.Benchmark]*` | ベンチマークプロジェクトはメトリクスを歪める |
| `GeneratedCodeAttribute` | ソースジェネレータ出力 |
| `ExcludeFromCodeCoverageAttribute` | 開発者による明示的オプトアウト |
| `*.g.cs`, `*.designer.cs` | 生成ファイルとデザイナーファイル |
| `**/Migrations/**/*` | EF Core 自動生成マイグレーション |

## Resources

- [Coverlet Documentation](https://github.com/coverlet-coverage/coverlet) — .NET クロスプラットフォームカバレッジライブラリ
- [ReportGenerator](https://github.com/danielpalme/ReportGenerator) — Risk Hotspots 付き HTML レポート生成
- [CRAP Score Original Paper](http://www.artima.com/weblogs/viewpost.jsp?thread=215899) — Alberto Savoia による CRAP メトリクスの原論文
- [dotnet test Coverage Collection](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-code-coverage) — カバレッジ収集に関する Microsoft ドキュメント
