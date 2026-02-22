# Detailed Patterns — dotnet-generic-matching

Extended examples and configuration details for the generic field matching skill.

## Step 6 — Field Definition Customization (Full Example)

Define field definitions with extractors, comparison functions, and weights for your domain entities:

| Field | Comparison Type | Weight | Reason |
|-------|----------------|--------|--------|
| Product Name | `StringSimilarity` | 3.0 | Primary identifier; OCR errors common |
| Unit Price | `NumericSimilarityDecimal` | 2.0 | Must be exact for money |
| Quantity | `NumericSimilarityDouble` | 1.5 | Numeric with tolerance |
| Customer Code | `StringSimilarity` | 2.0 | Key linking field |
| Dimensions | `NumericSimilarityDouble` | 1.0 | Supplementary field |

**Example configuration**:

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
