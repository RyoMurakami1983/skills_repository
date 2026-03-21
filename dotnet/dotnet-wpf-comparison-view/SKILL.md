---
name: dotnet-wpf-comparison-view
description: Use when: building a side-by-side comparison view in WPF for matching results with mismatch highlighting and checkbox verification.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, wpf, csharp, mvvm, comparison-view, matching, community-toolkit]
  invocable: false
---

# Build a Side-by-Side Comparison View in WPF

End-to-end workflow for building a comparison view that displays matching results side-by-side in **Windows Presentation Foundation (WPF)** using **Model-View-ViewModel (MVVM)**: a comparison item ViewModel with score tracking, 3-column XAML layout (field name / Source A / Source B), mismatch highlighting with background colors, editable fields with live score recalculation, and checkbox-based user verification before export.

## When to Use This Skill

Use this skill when:
- Displaying matching results from two data sources in a side-by-side comparison UI
- Building a verification workflow where users review and confirm each matched field
- Highlighting mismatched fields with color-coded backgrounds (pink for mismatch, green for verified)
- Implementing editable fields that trigger live score recalculation
- Creating an export gate that requires all items to be checked and scored above a threshold

**Prerequisites**:
- WPF application with `CommunityToolkit.Mvvm` installed
- Matching results from a matching service (e.g., `dotnet-generic-matching`)
- MVVM architecture with ObservableObject-based ViewModels

---

## Related Skills

- **`dotnet-generic-matching`** — Provides the matching results that this view displays
- **`dotnet-wpf-pdf-preview`** — PDF preview panel alongside the comparison view
- **`dotnet-oracle-wpf-integration`** — Loads Source A candidate data from Oracle
- **`dotnet-wpf-dify-api-integration`** — Extracts Source B data via AI OCR
- **`git-commit-practices`** — Commit each step as an atomic change

## Dependencies

- .NET + WPF (Windows Presentation Foundation)
- `CommunityToolkit.Mvvm` (ObservableObject, `[ObservableProperty]`, `[RelayCommand]`)
- Matching results from your Domain/Application layer (e.g., `dotnet-generic-matching`)

## Core Principles

1. **MVVM Binding Only** — All UI updates via data binding; never manipulate controls by `x:Name` (基礎と型)
2. **Visual Feedback First** — Background colors (#F8D7DA pink, #BBF7D0 green) give instant mismatch/verified status (ニュートラル)
3. **Live Recalculation** — Score updates immediately when editable fields change (継続は力)
4. **Gated Export** — All checkboxes checked + all scores ≥ threshold before export is allowed (基礎と型)
5. **Separation of Concerns** — Comparison logic stays in ViewModel; View only renders bindings (成長の複利)

## Workflow: Build Comparison View

### Step 1 — Create Comparison Item ViewModel

Use when defining the ViewModel that represents a single comparison row with score, source fields, backgrounds, and checkboxes.

Create a `ComparisonItemViewModel` inheriting from `ObservableObject`. Each instance holds one matched pair: Source A fields (e.g., database record), Source B fields (e.g., OCR-extracted data), background colors for mismatch highlighting, and checkbox properties for user verification.

```
YourApp/
├── ViewModels/
│   ├── ComparisonItemViewModel.cs   # 🆕 Single comparison row
│   └── ComparisonTabViewModel.cs    # 🆕 Parent with ObservableCollection
└── Views/
    └── ComparisonView.xaml          # 🆕 3-column layout
```

**ComparisonItemViewModel.cs** — Core structure (excerpt):

```csharp
using CommunityToolkit.Mvvm.ComponentModel;

namespace YourApp.ViewModels;

public partial class ComparisonItemViewModel : ObservableObject
{
    [ObservableProperty] private double scorePercent;

    [ObservableProperty] private string sourceAField1 = "";
    [ObservableProperty] private string sourceBField1 = "";

    [ObservableProperty] private bool isField1Checked;
    [ObservableProperty] private string sourceBField1Background = "Transparent";

    partial void OnIsField1CheckedChanged(bool value) => UpdateMismatchBackgrounds();

    public void UpdateMismatchBackgrounds()
    {
        // Pink (#F8D7DA) for mismatch, Green (#BBF7D0) when checked.
    }
}
```

Full example: `references/ComparisonItemViewModel.full.md`

**Key patterns from Mercury's `MatchingResultItemViewModel`**:
- `partial void OnXxxChanged()` hooks for change tracking and recalculation
- `HasDisplayValue()` filters out empty/dash values from visibility
- Background color uses string binding (`"Transparent"`, `"#F8D7DA"`, `"#BBF7D0"`)
- `GetUncheckedVisibleCount()` validates all visible fields are checked before export

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Build 3-Column XAML Layout

Use when creating the ItemsControl-based comparison view with field name, Source A, and Source B columns.

Create a scrollable `ItemsControl` with a `DataTemplate` containing a 3-column Grid. Each matching result is rendered as a bordered card with a score header and field rows.

**ComparisonView.xaml** — Layout template (excerpt):

```xml
<UserControl x:Class="YourApp.Views.ComparisonView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <ScrollViewer>
        <ItemsControl ItemsSource="{Binding ComparisonItems}">
            <ItemsControl.ItemTemplate>
                <DataTemplate>
                    <!-- 3 columns: Field | Source A | Source B -->
                </DataTemplate>
            </ItemsControl.ItemTemplate>
        </ItemsControl>
    </ScrollViewer>
</UserControl>
```

Full example: `references/ComparisonView.full.md`

**Why ItemsControl over DataGrid**: DataGrid adds selection, sorting, and editing chrome that conflicts with the custom comparison layout. `ItemsControl` gives full control over the per-item `DataTemplate`.

> **Values**: 基礎と型 / ニュートラル

### Step 3 — Add Score Color Converter

Use when applying color-coded styling to score values based on thresholds.

Implement score color logic in the ViewModel (not as an `IValueConverter`) for testability. The ViewModel exposes a `ScoreColor` string property that XAML binds to `Foreground`.

```csharp
// In ComparisonItemViewModel
public void UpdateScoreColor()
{
    // ✅ Green ≥80%, Orange 60–79%, Red <60%
    ScoreColor = IsSuccessful ? "Green" : (ScorePercent >= 60 ? "Orange" : "Red");
}
```

```xml
<!-- ✅ CORRECT — Bind to ViewModel color property -->
<TextBlock Text="{Binding ScorePercent, StringFormat={}{0:F1}%}"
           Foreground="{Binding ScoreColor}" FontWeight="Bold"/>

<!-- ❌ WRONG — IValueConverter for simple threshold logic -->
<TextBlock Foreground="{Binding ScorePercent, Converter={StaticResource ScoreColorConverter}}"/>
```

**Why ViewModel property over IValueConverter**: The 3-tier threshold logic (Green/Orange/Red) is domain-meaningful. Keeping it in the ViewModel makes it testable without XAML infrastructure.

> **Values**: 基礎と型 / ニュートラル

### Step 4 — Implement Editable Fields

Use when adding TextBox bindings for fields that users can modify, with yellow background and live recalculation.

Use `TwoWay` binding with `UpdateSourceTrigger=PropertyChanged` for immediate feedback. Editable fields have a distinct background (yellow `#FFFFCC` or white) to visually distinguish them from read-only fields.

```xml
<!-- ✅ Editable field with TwoWay binding and yellow background -->
<TextBox Grid.Column="2" Grid.Row="5"
         Text="{Binding EditableUnitPrice, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged,
                StringFormat={}{0:N0}}"
         Background="{Binding EditableUnitPriceBackground}"
         FontSize="11" Padding="3,1"/>

<!-- ✅ Read-only field (TextBlock, not TextBox) -->
<TextBlock Grid.Column="2" Grid.Row="1"
           Text="{Binding SourceBField1}"
           Background="{Binding SourceBField1Background}"
           Style="{StaticResource ValueStyle}"/>
```

**ViewModel change handler** — Trigger recalculation on edit:

```csharp
partial void OnEditableUnitPriceChanged(decimal value)
{
    IsModified = true;
    UpdateMismatchBackgrounds();
    RecalculateMatchingScore();
}
```

**Key points**:
- Use `decimal` for monetary fields (never `float` or `double`)
- `UpdateSourceTrigger=PropertyChanged` fires on every keystroke for live updates
- `IsModified` flag tracks whether any editable field has been changed

> **Values**: 継続は力 / 基礎と型

### Step 5 — Add Checkbox Verification

Use when adding per-field CheckBoxes that users must tick to confirm they have reviewed a field.

Add a `CheckBox` column (or inline CheckBox) for fields that require manual verification. When checked, the background changes to green (#BBF7D0). The `GetUncheckedVisibleCount()` method validates all visible fields are checked before export.

```xml
<!-- Checkbox column (between Source A and Source B, or after Source B) -->
<CheckBox Grid.Column="3" Grid.Row="1"
          IsChecked="{Binding IsField1Checked}"
          VerticalAlignment="Center" HorizontalAlignment="Center"/>
```

**ViewModel — CheckBox triggers background update**:

```csharp
partial void OnIsField1CheckedChanged(bool value)
{
    UpdateMismatchBackgrounds();
}

public void UpdateMismatchBackgrounds()
{
    // Green when checked, pink when mismatched, transparent when matching
    SourceBField1Background = IsField1Checked ? "#BBF7D0"
        : IsMismatch(SourceAField1, SourceBField1) ? "#F8D7DA"
        : "Transparent";
}
```

**Color legend**:

| Color | Hex Code | Meaning |
|-------|----------|---------|
| 🆕 Pink | `#F8D7DA` | Mismatch detected between Source A and Source B |
| ✅ Green | `#BBF7D0` | User has verified and checked the field |
| Transparent | `Transparent` | Fields match (no action needed) |

> **Values**: ニュートラル / 基礎と型

### Step 6 — Wire Results and Export

Use when connecting the comparison view to the parent ViewModel, populating results, and implementing export gating.

Create a parent `ComparisonTabViewModel` with an `ObservableCollection<ComparisonItemViewModel>` and a `SetResults` method. Subscribe to each item's `PropertyChanged` for live preview updates. Gate export on all-checked + all-scores-above-threshold.

**ComparisonTabViewModel.cs**:

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;

namespace YourApp.ViewModels
{
    public partial class ComparisonTabViewModel : ObservableObject
    {
        public ObservableCollection<ComparisonItemViewModel> ComparisonItems { get; } = new();

        [ObservableProperty]
        private string qualityMessage = string.Empty;

        public event EventHandler<string>? ExportCompleted;

        /// <summary>
        /// Populate from matching results with PropertyChanged subscription.
        /// </summary>
        public void SetResults(IEnumerable<MatchingResultData> results)
        {
            ComparisonItems.Clear();

            int idx = 1;
            foreach (var result in results)
            {
                var item = new ComparisonItemViewModel
                {
                    Index = idx++,
                    ScorePercent = result.ScorePercent,
                    IsSuccessful = result.ScorePercent >= 80.0,
                    SourceAField1 = result.SourceAField1,
                    SourceBField1 = result.SourceBField1,
                    // ... map remaining fields
                };
                item.UpdateScoreColor();
                item.UpdateMismatchBackgrounds();

                // ✅ Subscribe for live preview updates
                item.PropertyChanged += (s, e) => UpdateExportPreview();

                ComparisonItems.Add(item);
            }

            UpdateExportPreview();
        }

        private void UpdateExportPreview()
        {
            int total = ComparisonItems.Count;
            int qualified = ComparisonItems.Count(i => i.IsSuccessful);

            QualityMessage = qualified == total
                ? $"✅ All scores ≥80% ({qualified}/{total}). Export ready."
                : $"⚠ {qualified}/{total} items ≥80%. All must pass before export.";
        }

        [RelayCommand]
        private void Export()
        {
            // Gate 1: All checkboxes must be checked
            var unchecked = ComparisonItems.Sum(i => i.GetUncheckedVisibleCount());
            if (unchecked > 0)
            {
                ExportCompleted?.Invoke(this,
                    $"❌ {unchecked} unchecked items remain. Check all before export.");
                return;
            }

            // Gate 2: All scores must be ≥ threshold
            int total = ComparisonItems.Count;
            int qualified = ComparisonItems.Count(i => i.IsSuccessful);
            if (qualified < total)
            {
                ExportCompleted?.Invoke(this,
                    $"❌ {qualified}/{total} items ≥80%. All must pass.");
                return;
            }

            // Execute export
            // var outputPath = _exportUseCase.Execute(results);
            ExportCompleted?.Invoke(this, $"✅ Exported {total} items.");
        }
    }
}
```

**Why two export gates**: Gate 1 (checkboxes) ensures the user has visually reviewed every field. Gate 2 (score threshold) ensures data quality. Both must pass — this mirrors Mercury's `ResultTabViewModel.ExportRpaData` pattern.

> **Values**: 基礎と型 / 継続は力

---

## Good Practices

### 1. Use Background Colors for Visual Matching Feedback

✅ Apply `#F8D7DA` (pink) for mismatched fields, `#BBF7D0` (green) for verified fields, and `Transparent` for matching fields. Bind background to a ViewModel string property — see Step 5 for implementation.

**Values**: ニュートラル（即座の視覚フィードバック）

### 2. Recalculate Score on Editable Field Change

✅ Use `partial void OnXxxChanged()` hooks to trigger `RecalculateMatchingScore()` immediately when the user edits a field — see Step 4 for implementation.

**Values**: 継続は力（リアルタイム再計算）

### 3. Validate All Checkboxes Before Export

✅ Use `GetUncheckedVisibleCount()` to ensure every visible field has been reviewed. Only count fields where `HasDisplayValue` returns true — see Step 6 for implementation.

**Values**: 基礎と型（品質ゲート）

> Code examples: `references/detailed-patterns.md`

---

## Common Pitfalls

### 1. Not Subscribing to PropertyChanged for Live Preview Updates

**Problem**: Export preview does not update when the user edits a field or checks a checkbox, because the parent ViewModel is not listening to child item changes.

**Solution**: Subscribe to each `ComparisonItemViewModel.PropertyChanged` in `SetResults()`.

```csharp
// ❌ WRONG — No subscription, preview is stale
ComparisonItems.Add(item);

// ✅ CORRECT — Subscribe for live updates
item.PropertyChanged += (s, e) => UpdateExportPreview();
ComparisonItems.Add(item);
```

### 2. Hardcoding Colors Instead of Using Background Binding

**Problem**: Setting background colors directly in XAML with static values. Mismatch highlighting never updates when data changes.

**Solution**: Bind `Background` to a ViewModel string property that `UpdateMismatchBackgrounds()` updates dynamically.

```xml
<!-- ❌ WRONG — Static background, never updates -->
<TextBlock Background="#F8D7DA" Text="{Binding SourceBField1}"/>

<!-- ✅ CORRECT — Dynamic background via binding -->
<TextBlock Background="{Binding SourceBField1Background}" Text="{Binding SourceBField1}"/>
```

### 3. Forgetting to Reset State on New Data Load

**Problem**: Previous matching results remain visible when the user loads a new dataset, causing confusion with stale data.

**Solution**: Call `ComparisonItems.Clear()` at the start of `SetResults()` and reset all quality messages.

```csharp
public void SetResults(IEnumerable<MatchingResultData> results)
{
    // ✅ Always clear previous state first
    ComparisonItems.Clear();
    QualityMessage = string.Empty;
    // ... populate new results
}
```

---

## Anti-Patterns

### Direct UI Manipulation from ViewModel

**What**: Using `x:Name` to directly set TextBlock colors or backgrounds from code-behind instead of data binding.

**Why It's Wrong**: Violates MVVM. The ViewModel cannot be unit tested if it depends on UI controls.

**Better Approach**: Expose color as a string `[ObservableProperty]` in the ViewModel. Bind `Background="{Binding FieldBackground}"` in XAML.

### Putting Comparison Logic in View Layer

**What**: Computing mismatch status or score in XAML triggers, code-behind, or value converters.

**Why It's Wrong**: Comparison logic is domain logic. Placing it in the View makes it untestable.

**Better Approach**: Keep `IsMismatch()`, `UpdateMismatchBackgrounds()`, and `RecalculateMatchingScore()` in the ViewModel.

> Code examples: `references/detailed-patterns.md`

---

## Quick Reference

### Implementation Checklist

- [ ] Create `ComparisonItemViewModel` with score, source A/B fields, backgrounds (Step 1)
- [ ] Add `UpdateMismatchBackgrounds()` with pink/green/transparent logic (Step 1)
- [ ] Add `GetUncheckedVisibleCount()` for export validation (Step 1)
- [ ] Add `HasDisplayValue` visibility pattern for conditional field display (Step 1)
- [ ] Build 3-column XAML layout with `ItemsControl` and `DataTemplate` (Step 2)
- [ ] Add `FieldNameStyle` and `ValueStyle` resource styles (Step 2)
- [ ] Implement `UpdateScoreColor()` with Green/Orange/Red thresholds (Step 3)
- [ ] Add editable `TextBox` fields with `TwoWay` + `UpdateSourceTrigger=PropertyChanged` (Step 4)
- [ ] Wire `partial void OnXxxChanged()` to `RecalculateMatchingScore()` (Step 4)
- [ ] Add `CheckBox` per verifiable field, bound to `IsFieldXChecked` (Step 5)
- [ ] Create parent ViewModel with `ObservableCollection` and `SetResults()` (Step 6)
- [ ] Subscribe to `PropertyChanged` on each item for live preview (Step 6)
- [ ] Implement dual export gate: all-checked + all-scores-above-threshold (Step 6)
- [ ] Verify: `ComparisonItems.Clear()` called before loading new data

### File Structure

| File | Purpose | Layer |
|------|---------|-------|
| `ComparisonItemViewModel.cs` | Single comparison row with score + backgrounds | ViewModel |
| `ComparisonTabViewModel.cs` | Parent collection + export gating | ViewModel |
| `ComparisonView.xaml` | 3-column layout with ItemsControl | View |

### Color Reference

| Color | Hex | When Applied |
|-------|-----|--------------|
| 🆕 Pink | `#F8D7DA` | Mismatch: Source A ≠ Source B |
| ✅ Green | `#BBF7D0` | User checked the verification checkbox |
| ❌ Red | `Red` | Score < 60% |
| Orange | `Orange` | Score 60–79% |
| Green | `Green` | Score ≥ 80% |
| Transparent | `Transparent` | Fields match (no highlighting) |
| Yellow | `#FFFFCC` | Editable field background |

---

## Resources

- [CommunityToolkit.Mvvm Documentation](https://learn.microsoft.com/dotnet/communitytoolkit/mvvm/)
- [WPF ItemsControl and DataTemplate](https://learn.microsoft.com/dotnet/desktop/wpf/controls/itemscontrol)
- [ObservableObject and Source Generators](https://learn.microsoft.com/dotnet/communitytoolkit/mvvm/observableobject)
- `dotnet-generic-matching` — Matching service that produces the results this view displays
- `dotnet-wpf-pdf-preview` — PDF preview panel to show alongside comparison results

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-07-13 | 🆕 Initial release — side-by-side comparison view with mismatch highlighting |

<!-- Japanese version available at references/SKILL.ja.md -->
