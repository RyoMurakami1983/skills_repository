# Skill執筆ガイド

**作成日**: 2026-02-07  
**バージョン**: 1.0.0

このガイドは、高品質なSkillを作成するための実践的な執筆ルールとベストプラクティスを提供します。

---

## 📋 目次

1. [基本原則](#基本原則)
2. [ファイル構造](#ファイル構造)
3. [YAML Frontmatter](#yaml-frontmatter)
4. [セクション執筆ルール](#セクション執筆ルール)
5. [コード例のベストプラクティス](#コード例のベストプラクティス)
6. [比較表の作成方法](#比較表の作成方法)
7. [Anti-PatternsとPitfallsの書き分け](#anti-patternsとpitfallsの書き分け)
8. [言語とトーン](#言語とトーン)
9. [品質チェックリスト](#品質チェックリスト)

---

## 基本原則

### 1. 単一ファイル原則

✅ **DO**: SKILL.md のみで完結させる  
❌ **DON'T**: 追加のサポートファイルを作成しない

**理由**: 
- 読者が一箇所で全情報を得られる
- メンテナンス性が高い
- 検索性が向上

### 2. 読者ファーストの設計

✅ **DO**: 読者が5秒以内に「このSkillは自分に関係あるか」を判断できるようにする  
❌ **DON'T**: 抽象的な説明から始めない

**実装方法**:
- "When to Use This Skill" セクションを最優先配置
- 具体的なユースケースを箇条書き
- 各項目は50-100文字以内

### 3. 段階的な学習体験

✅ **DO**: Simple → Intermediate → Advanced の順でコード例を提示  
❌ **DON'T**: いきなり複雑なコードを見せない

**実装方法**:
- 各パターンで最低3段階の例を用意
- 各段階で「なぜこの進化が必要か」を説明

### 4. Problem-Solution構造

✅ **DO**: 「なぜこのパターンが必要か」を先に説明  
❌ **DON'T**: いきなり解決策を提示しない

**実装方法**:
- 悪い例（❌）→ 良い例（✅）のペアで提示
- Why を必ず含める

### 5. 実用性の重視

✅ **DO**: コピー&ペーストで動くコードを提供  
❌ **DON'T**: 抽象的な疑似コードや理論のみ

**実装方法**:
- 全コード例をコンパイル可能にする
- 必要なusing文やDI設定を含める

---

## ファイル構造

### ディレクトリ配置

```
.github/skills/
└── your-skill-name/
    └── SKILL.md          # ← 唯一のファイル
```

### 命名規則

- **フォルダ名**: kebab-case（例: `wpf-mvvm-ddd-enterprise`）
- **SKILL.md**: 固定（全て大文字）
- **name** (frontmatter): フォルダ名と一致

---

## YAML Frontmatter

### 必須フィールド

```yaml
---
name: your-skill-name        # kebab-case, フォルダ名と一致
description: One-line description of what problem this skill solves
invocable: false             # 通常は false
---
```

### オプションフィールド

```yaml
---
name: skill-name
description: Description here
invocable: false
tags: [csharp, dotnet, aspire]          # 関連技術タグ
version: 1.0.0                           # セマンティックバージョニング
author: GitHub Copilot Team              # 作成者
last_updated: 2026-02-07                 # 最終更新日
---
```

### 執筆ルール

| フィールド | ルール | 例 |
|-----------|--------|-----|
| `name` | kebab-case、フォルダ名と一致 | `wpf-mvvm-patterns` |
| `description` | 100文字以内、1行、問題解決にフォーカス | `Implement MVVM in WPF with DDD patterns` |
| `invocable` | 通常は `false` | `false` |
| `tags` | 3-5個、技術スタック中心 | `[wpf, mvvm, ddd, csharp]` |

---

## セクション執筆ルール

### 1. "When to Use This Skill" セクション

**目的**: 読者が5秒で関連性を判断できるようにする

**フォーマット**:
```markdown
## When to Use This Skill

Use this skill when:
- Designing public APIs for NuGet packages or libraries
- Making changes to existing public APIs
- Planning wire format changes for distributed systems
- Implementing versioning strategies
- Reviewing pull requests for breaking changes
```

**ルール**:
- ✅ 5-8個の具体的なシナリオ
- ✅ 動詞で始める（Designing, Implementing, Building, etc.）
- ✅ 各項目は50-100文字
- ❌ 抽象的な表現（"When you need quality code"）
- ❌ 10個以上のリスト（冗長）

**Good Example**:
```markdown
- Building enterprise WPF applications with complex business logic
- Implementing MVVM pattern with domain-driven design
- Integrating APIs with retry/circuit breaker policies
```

**Bad Example**:
```markdown
- When you want to write good code ← 抽象的すぎ
- Use WPF ← 技術名だけでシナリオ不明
- Desktop applications ← 広すぎる
```

### 2. "Core Principles" セクション

**目的**: このSkillの哲学・基盤となる考え方を伝える

**フォーマット**:
```markdown
## Core Principles

1. **Principle Name** - One-line summary (30-50 chars)
2. **Another Principle** - One-line summary
3. **Third Principle** - One-line summary
```

**ルール**:
- ✅ 3-5個の原則
- ✅ 太字で原則名、ハイフン後に説明
- ✅ 説明は30-50文字
- ❌ 長文の説明（別セクションで詳述）

**Example**:
```markdown
1. **Separation of Concerns** - Views, ViewModels, and Models have distinct responsibilities
2. **Dependency Inversion** - Depend on abstractions, not concrete implementations
3. **Testability First** - Design for unit testing from day one
```

### 3. パターンセクション（Pattern 1, Pattern 2, ...）

**構造**:
```markdown
## Pattern 1: [Pattern Name]

### Overview
Brief explanation (2-3 sentences)

### Basic Example
```csharp
// ✅ CORRECT - Simple case
```

### When to Use
- Condition A
- Condition B

### With Configuration
```csharp
// ✅ CORRECT - With options
```

### Advanced Pattern
```csharp
// ✅ CORRECT - Production-grade
```
```

**ルール**:
- ✅ 1つのSkillに7-10個のパターン
- ✅ 各パターンは独立して理解可能
- ✅ 進化的な例（Simple → Advanced）
- ❌ 他のパターンへの強い依存

### 4. "Common Pitfalls" セクション

**目的**: 実装時によくある失敗を予防

**フォーマット**:
```markdown
## Common Pitfalls

### 1. Pitfall Name - Brief Description

**Problem**: What users typically do wrong.

```csharp
// ❌ WRONG
```

**Solution**: How to fix it.

```csharp
// ✅ CORRECT
```
```

**ルール**:
- ✅ 3-5個の具体的な失敗例
- ✅ Problem-Solution構造
- ✅ 実際のコードで示す
- ❌ 理論的な説明のみ

### 5. "Anti-Patterns" セクション

**目的**: アーキテクチャレベルの設計ミスを防ぐ

**フォーマット**:
```markdown
## Anti-Patterns

### Anti-Pattern Name

**What**: Description of the architectural mistake.

```csharp
// ❌ WRONG - Architectural flaw
```

**Why It's Wrong**:
- Reason 1
- Reason 2

**Better Approach**:

```csharp
// ✅ CORRECT - Proper design
```
```

**ルール**:
- ✅ 2-4個のアーキテクチャレベルの問題
- ✅ Why（なぜダメか）を明確に
- ✅ Better Approach を必ず提示
- ❌ Pitfallsと混同しない（後述）

### 6. "Quick Reference" セクション

**目的**: at-a-glance で意思決定できるようにする

**フォーマット**:
```markdown
## Quick Reference

| Scenario | Pattern | Code Snippet |
|----------|---------|--------------|
| Simple case | Pattern 1 | `new Example()` |
| With config | Pattern 2 | `services.Configure<T>()` |
```

**ルール**:
- ✅ 表形式で簡潔に
- ✅ 3-5列、5-10行
- ✅ コードスニペットを含める
- ❌ 詳細な説明（本文で行う）

---

## コード例のベストプラクティス

### 1. 段階的な進化

**パターン**: Simple → With Configuration → Advanced

**例**:

**Level 1: Basic**
```csharp
// ✅ CORRECT - Simplest case
var data = await _client.GetAsync("/api/data");
```

**Level 2: With Configuration**
```csharp
// ✅ CORRECT - With retry policy
var data = await _retryPolicy.ExecuteAsync(
    () => _client.GetAsync("/api/data"));
```

**Level 3: Production-Grade**
```csharp
// ✅ CORRECT - With circuit breaker, timeout, and logging
var data = await _combinedPolicy.ExecuteAsync(
    async ct =>
    {
        _logger.LogInformation("Calling API...");
        var response = await _client.GetAsync("/api/data", ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<Data>(ct);
    },
    cancellationToken);
```

### 2. ✅/❌ マーカーの使用

**ルール**:
- ✅ `// ✅ CORRECT -` で正しい例を示す
- ✅ `// ❌ WRONG -` で間違った例を示す
- ✅ マーカー後に理由を簡潔に追加

**Good Example**:
```csharp
// ✅ CORRECT - Async all the way
await SomeAsyncMethod();

// ❌ WRONG - Deadlock risk with .Result
var result = SomeAsyncMethod().Result;
```

**Bad Example**:
```csharp
// Good ← ✅を使うべき
await SomeAsyncMethod();

// Bad ← ❌を使うべき
var result = SomeAsyncMethod().Result;
```

### 3. インラインコメントの書き方

**ルール**:
- ✅ WHYを説明（HOWはコードで明らか）
- ✅ 重要な決定ポイントのみ
- ❌ 冗長なコメント

**Good Example**:
```csharp
// ✅ CORRECT - AsNoTracking for read-only queries improves performance
var orders = await _db.Orders.AsNoTracking().ToListAsync();
```

**Bad Example**:
```csharp
// Get orders from database ← HOWを説明（不要）
var orders = await _db.Orders.ToListAsync();
```

### 4. using文とDI設定を含める

**ルール**:
- ✅ 必要なusing文を明記
- ✅ DI設定例を含める
- ❌ "省略" や "..." で済ませない

**Good Example**:
```csharp
using Microsoft.Extensions.DependencyInjection;
using Polly;

// In Program.cs
builder.Services.AddHttpClient<IApiClient, ApiClient>()
    .AddTransientHttpErrorPolicy(p => p.WaitAndRetryAsync(3, _ => TimeSpan.FromSeconds(2)));
```

### 5. 実行可能なコード

**ルール**:
- ✅ コピー&ペーストでコンパイル可能
- ✅ 依存関係を明記
- ❌ 疑似コードや抽象的な例

**Good Example**:
```csharp
public class OrderService
{
    private readonly IOrderRepository _repository;
    
    public OrderService(IOrderRepository repository)
    {
        _repository = repository;
    }
    
    public async Task<Order> GetOrderAsync(int id)
    {
        return await _repository.GetByIdAsync(id);
    }
}

// In Program.cs
builder.Services.AddScoped<IOrderRepository, OrderRepository>();
builder.Services.AddScoped<OrderService>();
```

---

## 比較表の作成方法

### 1. 意思決定支援表

**目的**: 読者が「どのパターンを選ぶべきか」を即座に判断できるようにする

**フォーマット**:
```markdown
| Scenario | Recommendation | Why |
|----------|----------------|-----|
| Read-only data | AsNoTracking() | No change tracking overhead |
| Update entity | Tracking | Automatic change detection |
| Bulk operations | ExecuteUpdate() | More efficient than tracking |
```

**ルール**:
- ✅ 3列: Scenario, Recommendation, Why
- ✅ 5-10行（多すぎない）
- ✅ 推奨パターンを太字で強調
- ❌ 詳細な説明（本文で）

### 2. 技術比較表

**目的**: 複数の技術・ツールから選択する際のガイド

**フォーマット**:
```markdown
| Tool | Type | Performance | Use When |
|------|------|-------------|----------|
| **Polly** | Resilience | High | HTTP calls, retries |
| **MediatR** | Messaging | Medium | CQRS, event-driven |
| Refit | HTTP Client | High | Type-safe REST clients |
```

**ルール**:
- ✅ 推奨ツールを太字
- ✅ 4-6列まで
- ✅ "Use When" 列を含める
- ❌ 主観的な評価のみ（定量データも）

### 3. パターン比較表

**フォーマット**:
```markdown
| Aspect | Pattern A | Pattern B | Pattern C |
|--------|-----------|-----------|-----------|
| **Complexity** | Low | Medium | High |
| **Performance** | Fast | Faster | Fastest |
| **Use Case** | Simple queries | Complex queries | Bulk operations |
```

---

## Anti-PatternsとPitfallsの書き分け

### 違いの定義

| 区分 | 対象 | 例 |
|------|------|-----|
| **Anti-Patterns** | アーキテクチャ・設計レベルの問題 | God Class, Tight Coupling |
| **Common Pitfalls** | 実装・使用時のミス | Forgetting await, Null reference |

### Anti-Patterns の書き方

**フォーカス**: 設計原則違反、スケーラビリティ問題、保守性の低下

**例**:
```markdown
### God ViewModel Anti-Pattern

**What**: ViewModelが全ての責務を持つ

```csharp
// ❌ WRONG - 1000行のViewModel
public class MainViewModel
{
    // UI logic, business logic, data access, validation...
}
```

**Why It's Wrong**:
- Violates Single Responsibility Principle
- Difficult to test
- Hard to maintain

**Better Approach**:
```csharp
// ✅ CORRECT - 責務を分離
public class MainViewModel
{
    private readonly IOrderService _orderService;
    // Only UI logic
}
```
```

### Common Pitfalls の書き方

**フォーカス**: 実装ミス、よくある間違い、Silent failures

**例**:
```markdown
### Forgetting AsNoTracking for Read-Only Queries

**Problem**: Change tracking オーバーヘッドが発生

```csharp
// ❌ WRONG - Tracking for read-only data
var orders = await _db.Orders.ToListAsync();
```

**Solution**:

```csharp
// ✅ CORRECT - AsNoTracking for reads
var orders = await _db.Orders.AsNoTracking().ToListAsync();
```
```

---

## 言語とトーン

### 1. 明確で簡潔な表現

✅ **DO**: 能動態、短文、具体的な用語  
❌ **DON'T**: 受動態、長文、曖昧な表現

**Good Example**:
> "Use `AsNoTracking()` for read-only queries to improve performance."

**Bad Example**:
> "It is recommended that `AsNoTracking()` should be used in scenarios where data is being read without the intention of modification, as this can potentially lead to performance improvements."

### 2. 一貫した用語

✅ **DO**: 同じ概念に同じ用語を使う  
❌ **DON'T**: 類義語を混在させる

**Example**:
- 一貫して "ViewModel" を使う（"View Model", "VM" を混ぜない）
- 一貫して "dependency injection" を使う（"DI", "IoC" を混ぜない）

### 3. 技術用語の定義

✅ **DO**: 初出時に簡潔に定義  
❌ **DON'T**: 読者が知っている前提

**Example**:
> "MVVM (Model-View-ViewModel) is an architectural pattern that separates UI logic from business logic."

### 4. 命令形の使用

✅ **DO**: "Use", "Implement", "Avoid"  
❌ **DON'T**: "You should", "It is better to"

**Good Example**:
> "Implement INotifyPropertyChanged for data binding."

**Bad Example**:
> "You should implement INotifyPropertyChanged if you want data binding to work."

---

## 品質チェックリスト

執筆完了後、以下をチェック：

### 構造チェック（10項目）

- [ ] ✅ SKILL.md 単一ファイルのみ
- [ ] ✅ YAML frontmatter が正しい
- [ ] ✅ "When to Use" が最初のセクション
- [ ] ✅ Core Principles を含む
- [ ] ✅ 7-10個のパターンセクション
- [ ] ✅ Problem-Solution 構造
- [ ] ✅ 比較表が含まれている
- [ ] ✅ Anti-Patterns セクションがある
- [ ] ✅ Common Pitfalls セクションがある
- [ ] ✅ Quick Reference または Decision Tree がある

### 内容チェック

- [ ] 全コード例がコンパイル可能
- [ ] ✅/❌ マーカーが一貫している
- [ ] using文やDI設定が含まれている
- [ ] 段階的な例（Simple → Advanced）
- [ ] Why が説明されている
- [ ] 具体的なシナリオが5個以上
- [ ] Related Skills のリンクが正しい

### 言語チェック

- [ ] 能動態で書かれている
- [ ] 一文が50文字以内（英語なら20単語以内）
- [ ] 専門用語が初出時に定義されている
- [ ] 一貫した用語使用

### 読みやすさチェック

- [ ] 見出しのみをスキャンして構造が理解できる
- [ ] コード例にインラインコメントがある
- [ ] 表が見やすい（3-6列）
- [ ] セクションの長さが適切（500-1000文字）

---

## まとめ

高品質なSkillは以下を満たす：

1. **明確な価値提案** - "When to Use" で即座に関連性が分かる
2. **段階的な学習** - Simple → Advanced の進化
3. **実用性** - コピペで動くコード
4. **問題解決フォーカス** - Why を説明
5. **一貫性** - フォーマット、用語、マーカー
6. **完全性** - using文、DI、エラーハンドリング
7. **意思決定支援** - 比較表、Decision Tree
8. **失敗予防** - Anti-Patterns, Pitfalls
9. **保守性** - 単一ファイル、明確な構造
10. **読みやすさ** - スキャン可能、簡潔な文章

このガイドに従えば、`.github/skills/` の既存Skillと同等の品質を達成できます。

---

**次のステップ**: [SKILL_QUALITY_CHECKLIST.md](./SKILL_QUALITY_CHECKLIST.md) で品質を検証
