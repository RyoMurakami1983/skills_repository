---
name: dotnet-generic-matching
description: Use when you need generic weighted field matching with scoring in a .NET Domain layer.
license: MIT
version: 1.0.0
metadata:
  author: RyoMurakami1983
  tags: [dotnet, csharp, ddd, matching, domain-layer, generics, specification-pattern]
  invocable: false
---

# Implement Generic Weighted Field Matching with Scoring

End-to-end workflow for building a generic, reusable field matching system in the Domain layer (Domain-Driven Design (DDD)): value objects for comparison results and scores, similarity utilities (Levenshtein, numeric), a generic `FieldMatchingService<TSource, TCandidate>`, and the Specification pattern for quality thresholds.

## When to Use This Skill

Use this skill when:
- Matching OCR-extracted records to candidates by comparing multiple weighted fields
- Building a scoring model that yields an explainable % score and field-by-field breakdown
- Implementing fuzzy string matching (Levenshtein distance) with normalization for OCR noise
- Creating a reusable `FieldMatchingService<TSource, TCandidate>` across multiple use-cases
- Applying the Specification pattern to enforce a configurable quality threshold on results

**Prerequisites**:
- Domain layer with DDD structure (use-case based organization)
- Understanding of C# generics and value objects

---

## Related Skills

- **`dotnet-ocr-matching-workflow`** — Uses this matching foundation for OCR-to-database record matching
- **`dotnet-oracle-wpf-integration`** — Provides candidate data from Oracle for matching
- **`dotnet-wpf-comparison-view`** — Displays matching results in a WPF comparison UI
- **`tdd-standard-practice`** — Test generated code with Red-Green-Refactor
- **`git-commit-practices`** — Commit each step as an atomic change

---

## Core Principles

1. **Domain Purity** — All matching logic lives in the Domain layer with zero infrastructure dependencies (基礎と型)
2. **Generic Reusability** — `FieldMatchingService<TSource, TCandidate>` works with any entity pair (成長の複利)
3. **Weighted Scoring** — Each field contributes proportionally to the overall match score (ニュートラル)
4. **Decimal for Money** — Use `decimal` type for all monetary values; never `float` or `double` (基礎と型)
5. **Specification Pattern** — Quality thresholds are first-class domain objects, not magic numbers (継続は力)

---

## Workflow: Build Generic Field Matching

### Step 1 — Create Value Objects (Domain Layer)

Use when defining the immutable result types for field comparison, scoring, and match results.

Create value objects in the Domain layer under the matching use-case directory (e.g., `Mercury.Domain/Matching/`).

**FieldComparison.cs** — Single field comparison result:

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

**MatchingScore.cs** — Weighted score aggregation:

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

**MatchingResult.cs** — Generic result binding source to best candidate:

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

Use when building string and numeric comparison functions for field matching.

Create static utility in the Domain layer. Supports Levenshtein distance (normalized 0.0–1.0), exact decimal comparison for monetary values, and tolerance-based double comparison for dimensions.

**SimilarityCalculator.cs** (pseudocode excerpt):

```csharp
// Keep this utility in the Domain layer.
// Full example implementation: references/SimilarityCalculator.full.md
public static class SimilarityCalculator
{
    public static double StringSimilarity(string? s1, string? s2)
        => /* Normalize + LevenshteinDistance + normalize to 0.0–1.0 */ 0.0;

    // Critical: Use decimal for money (unit price, total price).
    public static double NumericSimilarityDecimal(decimal a, decimal b)
        => a == b ? 1.0 : 0.0;
}
```

⚠️ **Critical**: Use `decimal` for monetary values (unit price, total price). Never use `float` or `double` for money — floating-point rounding errors cause false mismatches.

> **Values**: 基礎と型 / ニュートラル

### Step 3 — Create Matching Service

Use when building the generic matching service that compares a source against candidates.

Create `FieldMatchingService<TSource, TCandidate>` with configurable field definitions. Each field definition specifies how to extract values and which comparison function to use.

**FieldDefinition.cs** — Describes one matchable field:

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

**FieldMatchingService.cs** — Generic matching engine:

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

**Ask the user**: What fields to match, what weights to assign, and what comparison type (string/numeric/exact) for each field.

> **Values**: 成長の複利 / 基礎と型

### Step 4 — Implement Specification Pattern (Quality Threshold)

Use when enforcing quality constraints on matching results as a first-class domain concept.

Create a Specification that validates whether a set of matching results meets minimum quality thresholds. This keeps threshold logic in the Domain layer rather than scattering magic numbers across the Application layer.

**ISpecification.cs**:

```csharp
namespace Mercury.Domain.Matching
{
    public interface ISpecification<T>
    {
        bool IsSatisfiedBy(T entity);
    }
}
```

**HighQualityMatchingSpecification.cs**:

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

**Usage**:

```csharp
var spec = new HighQualityMatchingSpecification<OrderSheet, SofRecord>(minimumScorePercent: 80.0);
bool allHighQuality = spec.IsSatisfiedBy(matchingResults);
```

> **Values**: 基礎と型 / 継続は力

### Step 5 — Integrate with Application Layer

Use when creating a use case that orchestrates the matching service.

The Application layer use case coordinates loading candidates, running the matching service, and returning results. It does **not** contain matching logic — that stays in the Domain layer.

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

Use when configuring the matching service for a specific domain (e.g., order-to-SOF matching).

Define `FieldDefinition` entries with extractors, comparison functions, and weights for your domain entities. See [references/detailed-patterns.md](references/detailed-patterns.md) for the full weight table and configuration example.

> **Values**: 継続は力 / 成長の複利

---

## Good Practices

### 1. Use decimal for Money Comparisons

✅ Always use `decimal` for monetary field comparison (unit price, total price). Floating-point types (`float`, `double`) introduce rounding errors that cause false mismatches on exact values.

```csharp
// ✅ CORRECT — Exact comparison for money
public static double NumericSimilarityDecimal(decimal a, decimal b)
    => a == b ? 1.0 : 0.0;
```

### 2. Normalize Strings Before Comparison

✅ Remove whitespace (including full-width spaces), convert to lowercase before computing similarity. This prevents false low scores from formatting differences.

```csharp
private static string Normalize(string? value)
    => (value ?? string.Empty).Trim().Replace(" ", "").Replace("　", "").ToLowerInvariant();
```

### 3. Make Weights Configurable, Not Hardcoded

✅ Pass weights via `FieldDefinition` configuration. Different matching scenarios (order matching vs. inventory matching) may need different weight distributions.

---

## Common Pitfalls

### 1. Using float/double for Monetary Field Comparison

**Problem**: `double` arithmetic produces rounding errors (e.g., `0.1 + 0.2 != 0.3`), causing exact-match monetary comparisons to fail.

**Solution**: Use `decimal` for all monetary values and `NumericSimilarityDecimal` for comparison.

```csharp
// ❌ WRONG — Floating-point comparison for money
double price1 = 1234.56;
double price2 = 1234.56;
bool match = Math.Abs(price1 - price2) < 0.01; // Fragile

// ✅ CORRECT — Decimal exact comparison
decimal price1 = 1234.56m;
decimal price2 = 1234.56m;
bool match = price1 == price2; // Reliable
```

### 2. Hardcoding Field Names in Matching Service

**Problem**: Embedding field names like `"ProductName"` directly in the matching loop makes the service non-reusable.

**Solution**: Use `FieldDefinition<TSource, TCandidate>` with configurable extractors and names.

### 3. Not Handling Empty Candidate Lists

**Problem**: Calling `FindBestMatch` with zero candidates causes `NullReferenceException` or incorrect "100% match" results.

**Solution**: Return a zero-score `MatchingResult` when the candidate list is empty.

```csharp
if (candidateList.Count == 0)
    return new MatchingResult<TSource, TCandidate>(
        source, default, new MatchingScore([], BuildWeights()), _successThreshold);
```

---

## Anti-Patterns

### Putting Matching Logic in ViewModel

**What**: Computing similarity scores or running the matching loop inside a WPF ViewModel.

**Why It's Wrong**: Violates DDD layering. Matching is domain logic and should be testable without UI dependencies.

**Better Approach**: Keep all matching in the Domain layer (`FieldMatchingService`). The ViewModel only calls the Application layer use case and binds results.

### Using String Comparison for Numeric Fields

**What**: Comparing `"1234.56"` and `"1234.560"` as strings instead of parsing to numbers.

**Why It's Wrong**: String comparison treats `"1234.56"` and `"1234.560"` as different (Levenshtein distance = 1), even though they represent the same value.

**Better Approach**: Use `NumericSimilarityDecimal` for monetary values and `NumericSimilarityDouble` for dimensional values.

```csharp
// ❌ WRONG — String comparison for numbers
SimilarityCalculator.StringSimilarity("1234.56", "1234.560"); // ~0.93, not 1.0

// ✅ CORRECT — Numeric comparison
SimilarityCalculator.NumericSimilarityDecimal(1234.56m, 1234.560m); // 1.0
```

---

## Quick Reference

### Implementation Checklist

- [ ] Create `FieldComparison` value object (Step 1)
- [ ] Create `MatchingScore` with weighted calculation (Step 1)
- [ ] Create `MatchingResult<TSource, TCandidate>` generic result (Step 1)
- [ ] Implement `SimilarityCalculator` with Levenshtein, decimal, and double comparisons (Step 2)
- [ ] Create `FieldDefinition<TSource, TCandidate>` configuration class (Step 3)
- [ ] Implement `FieldMatchingService<TSource, TCandidate>` (Step 3)
- [ ] Add `ISpecification<T>` and `HighQualityMatchingSpecification` (Step 4)
- [ ] Create Application layer use case (Step 5)
- [ ] Configure field definitions with appropriate weights (Step 6)
- [ ] Verify: empty candidate list returns zero-score result
- [ ] Verify: monetary fields use `decimal` comparison

### Comparison Type Decision Table

| Data Type | Comparison Function | Returns | Use For |
|-----------|-------------------|---------|---------|
| Text (names, codes) | `StringSimilarity` | 0.0–1.0 (Levenshtein) | Product names, customer codes |
| Money (prices, totals) | `NumericSimilarityDecimal` | 0.0 or 1.0 (exact) | Unit price, total amount |
| Dimensions (size, weight) | `NumericSimilarityDouble` | 0.0–1.0 (tolerance) | Width, height, weight |

### Weight Assignment Guidelines

| Priority | Weight Range | Example Fields |
|----------|-------------|----------------|
| 🆕 Primary identifier | 2.5–3.0 | Product name, order number |
| ✅ Key linking field | 1.5–2.5 | Customer code, unit price |
| Supplementary | 0.5–1.5 | Dimensions, quantity |
| ❌ Low confidence | 0.1–0.5 | Free-text remarks |

---

## Resources

- `dotnet-ocr-matching-workflow` — Complete OCR-to-database matching workflow using this skill
- `dotnet-wpf-comparison-view` — WPF UI for displaying matching results
- [Levenshtein Distance (Wikipedia)](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [Specification Pattern (Martin Fowler)](https://martinfowler.com/apsupp/spec.pdf)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-07-13 | 🆕 Initial release — generic matching with weighted scoring |

<!-- Japanese version available at references/SKILL.ja.md -->
