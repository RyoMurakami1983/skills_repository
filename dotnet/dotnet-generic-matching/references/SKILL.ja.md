<!-- このドキュメントは dotnet-generic-matching の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-generic-matching
description: .NETドメイン層で汎用的な重み付きフィールドマッチングとスコアリングを実装。
license: MIT
version: 1.0.0
metadata:
  author: RyoMurakami1983
  tags: [dotnet, csharp, ddd, matching, domain-layer, generics, specification-pattern]
  invocable: false
---

# Implement Generic Weighted Field Matching with Scoring

ドメイン層で汎用的かつ再利用可能なフィールドマッチングシステムを構築するためのエンドツーエンドワークフロー：比較結果とスコアの値オブジェクト、類似度ユーティリティ（レーベンシュタイン距離、数値比較）、汎用 `FieldMatchingService<TSource, TCandidate>`、および品質閾値のためのSpecificationパターン。

## When to Use This Skill

以下の場合にこのスキルを使用してください：
- 複数のフィールドを比較して2つの異なるデータソースからレコードをマッチングするとき
- フィールドごとに異なる重要度を持つ重み付きスコアリングシステムを構築するとき
- レーベンシュタイン距離を使ったファジー文字列マッチングを実装するとき
- ジェネリクスを使用して任意のエンティティ型で動作する再利用可能なマッチングサービスを作成するとき
- マッチング結果に品質閾値を適用するためにSpecificationパターンを適用するとき

**前提条件**：
- DDD構造のドメイン層（ユースケースベースの構成）
- C#ジェネリクスと値オブジェクトの理解

---

## Related Skills

- **`dotnet-ocr-matching-workflow`** — このマッチング基盤をOCR-データベースレコードマッチングに使用
- **`dotnet-oracle-wpf-integration`** — マッチング用の候補データをOracleから提供
- **`dotnet-wpf-comparison-view`** — マッチング結果をWPF比較UIで表示
- **`tdd-standard-practice`** — Red-Green-Refactorで生成コードをテスト
- **`git-commit-practices`** — 各ステップをアトミックな変更としてコミット

---

## Core Principles

1. **ドメインの純粋性** — すべてのマッチングロジックはインフラ依存ゼロでドメイン層に配置（基礎と型）
2. **汎用的な再利用性** — `FieldMatchingService<TSource, TCandidate>` は任意のエンティティペアで動作（成長の複利）
3. **重み付きスコアリング** — 各フィールドが全体のマッチスコアに比例して貢献（ニュートラル）
4. **金額にはdecimal** — すべての金額値に `decimal` 型を使用。`float` や `double` は禁止（基礎と型）
5. **Specificationパターン** — 品質閾値はマジックナンバーではなくファーストクラスのドメインオブジェクト（継続は力）

---

## Workflow: Build Generic Field Matching

### Step 1 — Create Value Objects (Domain Layer)

フィールド比較、スコアリング、マッチング結果の不変な結果型を定義するときに使用します。

マッチングユースケースディレクトリ配下のドメイン層に値オブジェクトを作成します（例：`Mercury.Domain/Matching/`）。

**FieldComparison.cs** — 単一フィールドの比較結果：

```csharp
namespace Mercury.Domain.Matching
{
    public class FieldComparison
    {
        public FieldComparison(string fieldName, string sourceAValue, string sourceBValue, double similarity)
        {
            FieldName = fieldName;
            SourceAValue = sourceAValue;
            SourceBValue = sourceBValue;
            Similarity = similarity;
            IsMatch = similarity >= 0.8;
        }

        public string FieldName { get; }
        public string SourceAValue { get; }
        public string SourceBValue { get; }
        public double Similarity { get; }
        public bool IsMatch { get; }
    }
}
```

**MatchingScore.cs** — 重み付きスコア集計：

```csharp
namespace Mercury.Domain.Matching
{
    public class MatchingScore
    {
        public MatchingScore(IEnumerable<FieldComparison> comparisons, Dictionary<string, double> weights)
        {
            Comparisons = comparisons.ToList();
            double totalScore = 0, totalWeight = 0;
            foreach (var comp in Comparisons)
            {
                if (weights.TryGetValue(comp.FieldName, out var weight))
                {
                    totalScore += comp.Similarity * weight;
                    totalWeight += weight;
                }
            }
            ScorePercent = totalWeight > 0 ? (totalScore / totalWeight) * 100 : 0;
        }

        public IReadOnlyList<FieldComparison> Comparisons { get; }
        public double ScorePercent { get; }
    }
}
```

**MatchingResult.cs** — ソースと最良候補を紐付ける汎用結果：

```csharp
namespace Mercury.Domain.Matching
{
    public class MatchingResult<TSource, TCandidate>
    {
        public MatchingResult(TSource source, TCandidate? bestMatch, MatchingScore score, double successThreshold)
        {
            Source = source;
            BestMatch = bestMatch;
            Score = score;
            SuccessThreshold = successThreshold;
        }

        public TSource Source { get; }
        public TCandidate? BestMatch { get; }
        public MatchingScore Score { get; }
        public bool IsSuccessful => Score.ScorePercent >= SuccessThreshold;
        public double SuccessThreshold { get; }
    }
}
```

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Implement Similarity Utilities

文字列および数値の比較関数をフィールドマッチング用に構築するときに使用します。

ドメイン層に静的ユーティリティを作成します。レーベンシュタイン距離（0.0〜1.0に正規化）、金額値の厳密なdecimal比較、寸法のための許容範囲ベースのdouble比較をサポートします。

**SimilarityCalculator.cs**：

```csharp
namespace Mercury.Domain.Matching
{
    public static class SimilarityCalculator
    {
        /// <summary>
        /// Normalized Levenshtein similarity (0.0 = completely different, 1.0 = identical).
        /// Strings are normalized before comparison (lowercase, whitespace removed).
        /// </summary>
        public static double StringSimilarity(string? s1, string? s2)
        {
            var a = Normalize(s1);
            var b = Normalize(s2);
            if (a.Length == 0 && b.Length == 0) return 1.0;
            if (a.Length == 0 || b.Length == 0) return 0.0;
            int maxLen = Math.Max(a.Length, b.Length);
            int distance = LevenshteinDistance(a, b);
            return 1.0 - (double)distance / maxLen;
        }

        /// <summary>
        /// Exact match for monetary values. Use decimal to avoid floating-point errors.
        /// Returns 1.0 if equal, 0.0 otherwise.
        /// </summary>
        public static double NumericSimilarityDecimal(decimal a, decimal b)
            => a == b ? 1.0 : 0.0;

        /// <summary>
        /// Tolerance-based comparison for dimensions (width, height, weight).
        /// Parses strings to double; returns similarity based on relative difference.
        /// </summary>
        public static double NumericSimilarityDouble(string? s1, string? s2)
        {
            if (!double.TryParse(Normalize(s1), out var a)
                || !double.TryParse(Normalize(s2), out var b))
                return 0.0;

            if (a == 0 && b == 0) return 1.0;
            double maxVal = Math.Max(Math.Abs(a), Math.Abs(b));
            if (maxVal == 0) return 1.0;
            double diff = Math.Abs(a - b) / maxVal;
            return Math.Max(0.0, 1.0 - diff);
        }

        private static string Normalize(string? value)
            => (value ?? string.Empty).Trim().Replace(" ", "").Replace("　", "").ToLowerInvariant();

        private static int LevenshteinDistance(string s1, string s2)
        {
            int m = s1.Length, n = s2.Length;
            var dp = new int[m + 1, n + 1];
            for (int i = 0; i <= m; i++) dp[i, 0] = i;
            for (int j = 0; j <= n; j++) dp[0, j] = j;
            for (int i = 1; i <= m; i++)
                for (int j = 1; j <= n; j++)
                {
                    int cost = s1[i - 1] == s2[j - 1] ? 0 : 1;
                    dp[i, j] = Math.Min(
                        Math.Min(dp[i - 1, j] + 1, dp[i, j - 1] + 1),
                        dp[i - 1, j - 1] + cost);
                }
            return dp[m, n];
        }
    }
}
```

⚠️ **重要**: 金額値（単価、合計金額）には `decimal` を使用してください。金額に `float` や `double` を使用しないでください — 浮動小数点の丸め誤差が誤った不一致を引き起こします。

> **Values**: 基礎と型 / ニュートラル

### Step 3 — Create Matching Service

ソースを候補と比較する汎用マッチングサービスを構築するときに使用します。

設定可能なフィールド定義を持つ `FieldMatchingService<TSource, TCandidate>` を作成します。各フィールド定義は、値の抽出方法と使用する比較関数を指定します。

**FieldDefinition.cs** — マッチング可能な1つのフィールドを記述：

```csharp
namespace Mercury.Domain.Matching
{
    public class FieldDefinition<TSource, TCandidate>
    {
        public string FieldName { get; init; } = string.Empty;
        public Func<TSource, string> SourceExtractor { get; init; } = _ => string.Empty;
        public Func<TCandidate, string> CandidateExtractor { get; init; } = _ => string.Empty;
        public Func<string, string, double> CompareFunction { get; init; }
            = SimilarityCalculator.StringSimilarity;
        public double Weight { get; init; } = 1.0;
    }
}
```

**FieldMatchingService.cs** — 汎用マッチングエンジン：

```csharp
namespace Mercury.Domain.Matching
{
    public class FieldMatchingService<TSource, TCandidate>
    {
        private readonly List<FieldDefinition<TSource, TCandidate>> _fields;
        private readonly double _successThreshold;

        public FieldMatchingService(
            IEnumerable<FieldDefinition<TSource, TCandidate>> fields,
            double successThreshold = 70.0)
        {
            _fields = fields.ToList();
            _successThreshold = successThreshold;
        }

        public MatchingResult<TSource, TCandidate> FindBestMatch(
            TSource source, IEnumerable<TCandidate> candidates)
        {
            var candidateList = candidates.ToList();
            if (candidateList.Count == 0)
                return new MatchingResult<TSource, TCandidate>(
                    source, default, new MatchingScore([], BuildWeights()), _successThreshold);

            MatchingScore? bestScore = null;
            TCandidate? bestCandidate = default;

            foreach (var candidate in candidateList)
            {
                var comparisons = _fields.Select(f => new FieldComparison(
                    f.FieldName,
                    f.SourceExtractor(source),
                    f.CandidateExtractor(candidate),
                    f.CompareFunction(f.SourceExtractor(source), f.CandidateExtractor(candidate))
                )).ToList();

                var score = new MatchingScore(comparisons, BuildWeights());
                if (bestScore == null || score.ScorePercent > bestScore.ScorePercent)
                {
                    bestScore = score;
                    bestCandidate = candidate;
                }
            }

            return new MatchingResult<TSource, TCandidate>(
                source, bestCandidate, bestScore!, _successThreshold);
        }

        private Dictionary<string, double> BuildWeights()
            => _fields.ToDictionary(f => f.FieldName, f => f.Weight);
    }
}
```

**ユーザーに確認**: マッチングするフィールド、割り当てる重み、各フィールドの比較タイプ（文字列/数値/厳密一致）を確認してください。

> **Values**: 成長の複利 / 基礎と型

### Step 4 — Implement Specification Pattern (Quality Threshold)

マッチング結果に対する品質制約をファーストクラスのドメイン概念として適用するときに使用します。

マッチング結果のセットが最低品質閾値を満たしているかどうかを検証するSpecificationを作成します。これにより閾値ロジックがアプリケーション層にマジックナンバーとして散在するのではなく、ドメイン層に保持されます。

**ISpecification.cs**：

```csharp
namespace Mercury.Domain.Matching
{
    public interface ISpecification<T>
    {
        bool IsSatisfiedBy(T entity);
    }
}
```

**HighQualityMatchingSpecification.cs**：

```csharp
namespace Mercury.Domain.Matching
{
    public class HighQualityMatchingSpecification<TSource, TCandidate>
        : ISpecification<IEnumerable<MatchingResult<TSource, TCandidate>>>
    {
        private readonly double _minimumScorePercent;

        public HighQualityMatchingSpecification(double minimumScorePercent = 70.0)
        {
            _minimumScorePercent = minimumScorePercent;
        }

        public bool IsSatisfiedBy(IEnumerable<MatchingResult<TSource, TCandidate>> results)
        {
            var list = results.ToList();
            return list.Any()
                && list.All(r => r.Score.ScorePercent >= _minimumScorePercent);
        }
    }
}
```

**使用例**：

```csharp
var spec = new HighQualityMatchingSpecification<OrderSheet, SofRecord>(minimumScorePercent: 80.0);
bool allHighQuality = spec.IsSatisfiedBy(matchingResults);
```

> **Values**: 基礎と型 / 継続は力

### Step 5 — Integrate with Application Layer

マッチングサービスをオーケストレーションするユースケースを作成するときに使用します。

アプリケーション層のユースケースが候補の読み込み、マッチングサービスの実行、結果の返却を調整します。マッチングロジックは含まず — それはドメイン層に留まります。

```csharp
namespace Mercury.Application.UseCases.Matching
{
    public class MatchOrderWithSofUseCase
    {
        private readonly ISofRepository _sofRepository;
        private readonly FieldMatchingService<OrderSheet, SofRecord> _matchingService;

        public MatchOrderWithSofUseCase(
            ISofRepository sofRepository,
            FieldMatchingService<OrderSheet, SofRecord> matchingService)
        {
            _sofRepository = sofRepository;
            _matchingService = matchingService;
        }

        public async Task<List<MatchingResult<OrderSheet, SofRecord>>> ExecuteAsync(
            IEnumerable<OrderSheet> orders)
        {
            var candidates = await _sofRepository.GetAllAsync();
            return orders
                .Select(order => _matchingService.FindBestMatch(order, candidates))
                .ToList();
        }
    }
}
```

> **Values**: 基礎と型 / 成長の複利

### Step 6 — Customize Field Definitions

特定のドメイン（例：注文書-SOFマッチング）用にマッチングサービスを設定するときに使用します。

ドメインエンティティに対して抽出関数、比較関数、重みを持つフィールド定義を定義します：

| フィールド | 比較タイプ | 重み | 理由 |
|-----------|-----------|------|------|
| 品名 | `StringSimilarity` | 3.0 | 主要識別子。OCRエラーが発生しやすい |
| 単価 | `NumericSimilarityDecimal` | 2.0 | 金額は厳密一致が必要 |
| 数量 | `NumericSimilarityDouble` | 1.5 | 許容範囲付きの数値比較 |
| 得意先コード | `StringSimilarity` | 2.0 | 主要な紐付けフィールド |
| 寸法 | `NumericSimilarityDouble` | 1.0 | 補助フィールド |

**設定例**：

```csharp
var fields = new List<FieldDefinition<OrderSheet, SofRecord>>
{
    new()
    {
        FieldName = "ProductName",
        SourceExtractor = o => o.ProductName,
        CandidateExtractor = s => s.ProductName,
        CompareFunction = SimilarityCalculator.StringSimilarity,
        Weight = 3.0
    },
    new()
    {
        FieldName = "UnitPrice",
        SourceExtractor = o => o.UnitPrice.ToString(),
        CandidateExtractor = s => s.UnitPrice.ToString(),
        CompareFunction = (a, b) =>
            decimal.TryParse(a, out var da) && decimal.TryParse(b, out var db)
                ? SimilarityCalculator.NumericSimilarityDecimal(da, db)
                : 0.0,
        Weight = 2.0
    },
    new()
    {
        FieldName = "Quantity",
        SourceExtractor = o => o.Quantity.ToString(),
        CandidateExtractor = s => s.Quantity.ToString(),
        CompareFunction = SimilarityCalculator.NumericSimilarityDouble,
        Weight = 1.5
    }
};

var service = new FieldMatchingService<OrderSheet, SofRecord>(fields, successThreshold: 70.0);
```

> **Values**: 継続は力 / 成長の複利

---

## Good Practices

### 1. Use decimal for Money Comparisons

✅ 金額フィールドの比較（単価、合計金額）には必ず `decimal` を使用してください。浮動小数点型（`float`、`double`）は丸め誤差を引き起こし、厳密値での誤った不一致の原因になります。

```csharp
// ✅ 正しい — 金額の厳密比較
public static double NumericSimilarityDecimal(decimal a, decimal b)
    => a == b ? 1.0 : 0.0;
```

### 2. Normalize Strings Before Comparison

✅ 類似度計算前に空白（全角スペースを含む）を除去し、小文字に変換してください。書式の違いによるスコア低下を防ぎます。

```csharp
private static string Normalize(string? value)
    => (value ?? string.Empty).Trim().Replace(" ", "").Replace("　", "").ToLowerInvariant();
```

### 3. Make Weights Configurable, Not Hardcoded

✅ `FieldDefinition` の設定で重みを渡してください。異なるマッチングシナリオ（注文マッチング vs 在庫マッチング）では異なる重み配分が必要になる場合があります。

---

## Common Pitfalls

### 1. Using float/double for Monetary Field Comparison

**Problem**: `double` の演算は丸め誤差を生じ（例：`0.1 + 0.2 != 0.3`）、厳密一致の金額比較が失敗します。

**Solution**: すべての金額値に `decimal` を使用し、比較には `NumericSimilarityDecimal` を使用してください。

```csharp
// ❌ 間違い — 金額に浮動小数点比較
double price1 = 1234.56;
double price2 = 1234.56;
bool match = Math.Abs(price1 - price2) < 0.01; // 脆弱

// ✅ 正しい — decimalの厳密比較
decimal price1 = 1234.56m;
decimal price2 = 1234.56m;
bool match = price1 == price2; // 信頼性が高い
```

### 2. Hardcoding Field Names in Matching Service

**Problem**: `"ProductName"` のようなフィールド名をマッチングループに直接埋め込むと、サービスが再利用できなくなります。

**Solution**: 設定可能な抽出関数と名前を持つ `FieldDefinition<TSource, TCandidate>` を使用してください。

### 3. Not Handling Empty Candidate Lists

**Problem**: 候補ゼロで `FindBestMatch` を呼び出すと `NullReferenceException` や誤った「100%一致」結果が発生します。

**Solution**: 候補リストが空の場合はスコアゼロの `MatchingResult` を返してください。

```csharp
if (candidateList.Count == 0)
    return new MatchingResult<TSource, TCandidate>(
        source, default, new MatchingScore([], BuildWeights()), _successThreshold);
```

---

## Anti-Patterns

### Putting Matching Logic in ViewModel

**What**: WPF ViewModelで類似度スコアの計算やマッチングループを実行すること。

**Why It's Wrong**: DDDのレイヤリングに違反します。マッチングはドメインロジックであり、UI依存なしでテスト可能であるべきです。

**Better Approach**: すべてのマッチングをドメイン層（`FieldMatchingService`）に保持してください。ViewModelはアプリケーション層のユースケースを呼び出し、結果をバインドするだけです。

### Using String Comparison for Numeric Fields

**What**: 数値をパースせずに `"1234.56"` と `"1234.560"` を文字列として比較すること。

**Why It's Wrong**: 文字列比較では `"1234.56"` と `"1234.560"` は異なるものとして扱われます（レーベンシュタイン距離 = 1）が、同じ値を表しています。

**Better Approach**: 金額値には `NumericSimilarityDecimal`、寸法値には `NumericSimilarityDouble` を使用してください。

```csharp
// ❌ 間違い — 数値に文字列比較
SimilarityCalculator.StringSimilarity("1234.56", "1234.560"); // ~0.93、1.0ではない

// ✅ 正しい — 数値比較
SimilarityCalculator.NumericSimilarityDecimal(1234.56m, 1234.560m); // 1.0
```

---

## Quick Reference

### Implementation Checklist

- [ ] `FieldComparison` 値オブジェクトを作成（Step 1）
- [ ] 重み付き計算を持つ `MatchingScore` を作成（Step 1）
- [ ] `MatchingResult<TSource, TCandidate>` 汎用結果を作成（Step 1）
- [ ] レーベンシュタイン、decimal、double比較を持つ `SimilarityCalculator` を実装（Step 2）
- [ ] `FieldDefinition<TSource, TCandidate>` 設定クラスを作成（Step 3）
- [ ] `FieldMatchingService<TSource, TCandidate>` を実装（Step 3）
- [ ] `ISpecification<T>` と `HighQualityMatchingSpecification` を追加（Step 4）
- [ ] アプリケーション層のユースケースを作成（Step 5）
- [ ] 適切な重みでフィールド定義を設定（Step 6）
- [ ] 検証: 空の候補リストがスコアゼロの結果を返すこと
- [ ] 検証: 金額フィールドが `decimal` 比較を使用していること

### Comparison Type Decision Table

| データ型 | 比較関数 | 戻り値 | 用途 |
|---------|---------|--------|------|
| テキスト（名前、コード） | `StringSimilarity` | 0.0〜1.0（レーベンシュタイン） | 品名、得意先コード |
| 金額（価格、合計） | `NumericSimilarityDecimal` | 0.0 または 1.0（厳密一致） | 単価、合計金額 |
| 寸法（サイズ、重量） | `NumericSimilarityDouble` | 0.0〜1.0（許容範囲） | 幅、高さ、重量 |

### Weight Assignment Guidelines

| 優先度 | 重み範囲 | フィールド例 |
|-------|---------|------------|
| 🆕 主要識別子 | 2.5〜3.0 | 品名、注文番号 |
| ✅ 主要紐付けフィールド | 1.5〜2.5 | 得意先コード、単価 |
| 補助 | 0.5〜1.5 | 寸法、数量 |
| ❌ 低信頼度 | 0.1〜0.5 | 自由記述の備考 |

---

## Resources

- `dotnet-ocr-matching-workflow` — このスキルを使用した完全なOCR-データベースマッチングワークフロー
- `dotnet-wpf-comparison-view` — マッチング結果表示用のWPF UI
- [レーベンシュタイン距離（Wikipedia）](https://ja.wikipedia.org/wiki/%E3%83%AC%E3%83%BC%E3%83%99%E3%83%B3%E3%82%B7%E3%83%A5%E3%82%BF%E3%82%A4%E3%83%B3%E8%B7%9D%E9%9B%A2)
- [Specificationパターン（Martin Fowler）](https://martinfowler.com/apsupp/spec.pdf)

---

## Changelog

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| 1.0.0 | 2025-07-13 | 🆕 初回リリース — 重み付きスコアリング付き汎用マッチング |

<!-- 英語版は ../SKILL.md を参照してください -->
