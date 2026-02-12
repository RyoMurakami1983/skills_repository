<!-- 
このテンプレートはSKILL.md単一ファイルで完結する設計です。
追加のサポートファイル（references/やassets/など）は、GitHub Copilotの
公式ガイドに従う場合のみ作成可能です。基本的には単一ファイルで完結させてください。

注意: このテンプレートは構造の例示です。実際のskillでは7-10個のパターンセクションを含めてください。
-->

---
name: your-skill-name-here
description: このスキルが解決する問題の1行説明（最大100文字）
invocable: false
tags: [tag1, tag2, tag3]  # 3-5個の技術スタック中心のタグを追加
author: RyoMurakami1983  # 本システム作成skillの識別用（オプション）
---

# スキルタイトル

## Related Skills

関連するskillをリストアップします：
- **`related-skill-1`** - 関連の簡単な説明
- **`related-skill-2`** - 関連の簡単な説明

## When to Use This Skill

このスキルを使用する場面（5-8個の具体的なシナリオ）：
- シナリオ1 - アクション志向の説明（50-100文字）
- シナリオ2 - 問題ドメインの説明
- シナリオ3 - チーム/ワークフローのシナリオ
- シナリオ4 - 技術的な決定ポイント
- シナリオ5 - 実装のユースケース

---

## Core Principles

このスキルの基盤となる原則（3-5個）：

1. **原則1** - 重要な概念の1行サマリー
2. **原則2** - 重要な概念の1行サマリー
3. **原則3** - 重要な概念の1行サマリー
4. **原則4** - 重要な概念の1行サマリー（オプション）
5. **原則5** - 重要な概念の1行サマリー（オプション）

---

## Pattern 1: [パターン名]

### Overview

このパターンが何を解決するか、なぜ重要かの簡単な説明（2-3文）。

### Basic Example

```csharp
// ✅ CORRECT - Simple, most common case
public class Example
{
    // 実装とインラインコメントで「なぜ」を説明
    public void DoSomething()
    {
        // 重要な決定の説明
    }
}
```

### When to Use

このパターンを使用する場面：
- 特定の条件A
- 特定の条件B
- 特定の条件C

| シナリオ | 推奨 | 理由 |
|----------|------|------|
| シナリオA | パターンXを使用 | 簡単な説明 |
| シナリオB | パターンYを使用 | 簡単な説明 |
| シナリオC | パターン2を参照 | 簡単な説明 |

### With Configuration

```csharp
// ✅ CORRECT - With options/configuration
public class ConfiguredExample
{
    private readonly IOptions<Settings> _options;
    
    public ConfiguredExample(IOptions<Settings> options)
    {
        _options = options;
    }
    
    public void DoSomething()
    {
        var setting = _options.Value.SomeSetting;
        // 設定を使用する際の説明
    }
}

// In Program.cs or Startup
builder.Services.Configure<Settings>(
    builder.Configuration.GetSection("Settings"));
```

### Advanced Pattern (Production-Grade)

```csharp
// ✅ CORRECT - Production-grade with error handling
public class AdvancedExample
{
    public async Task DoSomethingAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            // 以下を含む複雑な実装：
            // - Error handling
            // - Cancellation support
            // - Resource management
        }
        catch (SpecificException ex)
        {
            // 特定のエラーハンドリング
            throw;
        }
    }
}
```

---

## Pattern 2: [別のパターン名]

### Overview

このパターンの簡単な説明と、パターン1とどう異なるか。

### Basic Example

```csharp
// ✅ CORRECT - Basic usage
```

### Common Variation

```csharp
// ✅ CORRECT - Alternative approach for different scenario
```

### Comparison with Pattern 1

| 側面 | パターン1 | パターン2 |
|------|-----------|-----------|
| ユースケース | 説明 | 説明 |
| パフォーマンス | メトリック/説明 | メトリック/説明 |
| 複雑さ | 低/中/高 | 低/中/高 |
| 使用する場面 | シナリオ | シナリオ |

---

## Pattern 3: [3番目のパターン名]

[パターン1と2と同様の構造...]

---

<!-- 
注意: このテンプレートにはパターン1-3のみ記載されていますが、
実際のskillでは7-10個のパターンセクションを含めてください。
パターン4-10も同様の構造（Overview, Basic Example, When to Use, 
With Configuration, Advanced Pattern）で作成します。
-->

## Common Pitfalls

よくある落とし穴と解決策：

### 1. 落とし穴の名前 - 簡単な説明

**Problem**: ユーザーが通常間違えることと、なぜ失敗するか。

```csharp
// ❌ WRONG - What not to do
public class BadExample
{
    public void DoSomethingWrong()
    {
        // アンチパターンとなぜ悪いかの説明
    }
}
```

**Solution**: 修正方法と、なぜこのアプローチが機能するか。

```csharp
// ✅ CORRECT - The right approach
public class GoodExample
{
    public void DoSomethingRight()
    {
        // 正しいパターンと説明
    }
}
```

### 2. 別のよくある落とし穴

```csharp
// ❌ WRONG - Silent failure example
var result = SomeOperation(); // エラーハンドリングがない

// ✅ CORRECT - Explicit error handling
try
{
    var result = SomeOperation();
    // 成功パス
}
catch (SpecificException ex)
{
    // 特定のエラーを処理
}
```

### 3. 3番目のよくある落とし穴

[同様のフォーマット...]

---

## Anti-Patterns

アーキテクチャレベルのアンチパターン：

### Architectural Anti-Pattern Name

**What**: アーキテクチャレベルでのアンチパターンの説明。

```csharp
// ❌ WRONG - Architectural mistake
public class AntiPatternExample
{
    // スケール時に問題を引き起こす設計上の欠陥
    // または基本原則に違反
}
```

**Why It's Wrong**:
- 理由1: 原則Xに違反
- 理由2: 問題Yを引き起こす
- 理由3: スケールしない

**Better Approach**:

```csharp
// ✅ CORRECT - Architectural solution
public class BetterDesign
{
    // 基本原則に従った適切な設計
}
```

### Breaking Changes Pattern

```csharp
// ❌ WRONG - "Bug fix" that breaks users
public async Task<Result> GetResultAsync(int id)  // 以前は同期だった！
{
    // 非同期に「修正」 - しかし既存の呼び出し元をすべて壊す
}

// ✅ CORRECT - Add new method, deprecate old
[Obsolete("GetResultAsyncを使用してください")]
public Result GetResult(int id) => GetResultAsync(id).GetAwaiter().GetResult();

public async Task<Result> GetResultAsync(int id)
{
    // 新しい非同期実装
}
```

---

## Quick Reference

素早く意思決定するためのリファレンス：

### Decision Tree

```
開始: 何が必要？
├─► Aが必要？ → パターン1を使用
├─► Bが必要？ → パターン2を使用
├─► Cが必要？ → パターン3を使用
└─► 複雑なシナリオ？ → パターンを組み合わせる（高度なセクションを参照）
```

### Common Scenarios Cheat Sheet

| シナリオ | パターン | コードスニペット |
|----------|---------|-----------------|
| シンプルなケース | パターン1 | `new Example()` |
| 設定あり | パターン1 + 設定 | `services.Configure<Settings>()` |
| 非同期操作 | パターン2 | `await DoAsync()` |
| エラーハンドリング | パターン3 | 特定の例外での`try/catch` |

---

## Best Practices Summary

ベストプラクティスのまとめ：

1. **プラクティス1** - 推奨事項の簡単な説明
2. **プラクティス2** - 推奨事項の簡単な説明
3. **プラクティス3** - 推奨事項の簡単な説明
4. **プラクティス4** - 推奨事項の簡単な説明
5. **プラクティス5** - 推奨事項の簡単な説明

---

## Resources

参考資料とリンク：

- [公式ドキュメント名](https://example.com/docs)
- [関連記事/ブログ投稿](https://example.com/article)
- [リファレンス実装](https://github.com/example/repo)
- [コミュニティディスカッション](https://example.com/discussion)

---

## Changelog

変更履歴（実質的な変更のみ記録。詳細はCHANGELOG.mdを参照）：

### Version 1.0.0 (YYYY-MM-DD)
- 初版
- パターン1-3をドキュメント化
- よくある落とし穴を特定

### Version 1.1.0 (YYYY-MM-DD) (オプション)
- パターン4を追加
- .NET Xの例を更新
- アンチパターンYを明確化

<!-- 
変更履歴が増えた場合は、CHANGELOG.mdに移動してください。
SKILL.md内には最新3-5バージョンのみ記載し、「詳細はCHANGELOG.mdを参照」と記載します。
-->
