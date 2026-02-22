# Detailed Patterns — dotnet-wpf-comparison-view

Code examples extracted from the main SKILL.md for reference.

---

## Good Practices — Code Examples

### 1. Background Colors for Visual Matching Feedback

```csharp
// ✅ CORRECT — ViewModel drives background color via binding
SourceBField1Background = IsField1Checked ? "#BBF7D0"
    : IsMismatch(SourceAField1, SourceBField1) ? "#F8D7DA"
    : "Transparent";
```

### 2. Recalculate Score on Editable Field Change

```csharp
partial void OnEditableUnitPriceChanged(decimal value)
{
    IsModified = true;
    UpdateMismatchBackgrounds();
    RecalculateMatchingScore();
}
```

### 3. Validate All Checkboxes Before Export

```csharp
var unchecked = ComparisonItems.Sum(i => i.GetUncheckedVisibleCount());
if (unchecked > 0) { /* Block export */ }
```

---

## Anti-Patterns — Code Examples

### Direct UI Manipulation from ViewModel

```csharp
// ❌ WRONG — Direct UI manipulation
Field1TextBlock.Background = new SolidColorBrush(Colors.Pink);

// ✅ CORRECT — ViewModel property with binding
[ObservableProperty] private string sourceBField1Background = "Transparent";
```

### Putting Comparison Logic in View Layer

```csharp
// ❌ WRONG — Mismatch check in IValueConverter
public object Convert(object[] values, ...) =>
    values[0]?.ToString() != values[1]?.ToString() ? Brushes.Pink : Brushes.Transparent;

// ✅ CORRECT — Mismatch check in ViewModel
private static bool IsMismatch(string? a, string? b)
    => (a ?? string.Empty) != (b ?? string.Empty);
```
