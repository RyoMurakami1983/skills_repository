# ComparisonItemViewModel.cs (Full Reference)

This is the full example referenced from `SKILL.md`.

```csharp
using CommunityToolkit.Mvvm.ComponentModel;

namespace YourApp.ViewModels
{
    public partial class ComparisonItemViewModel : ObservableObject
    {
        // === Score ===
        [ObservableProperty] private int index;
        [ObservableProperty] private double scorePercent;
        [ObservableProperty] private bool isSuccessful;
        [ObservableProperty] private string scoreColor = "Black";

        // === Source A fields (read-only, e.g., database record) ===
        [ObservableProperty] private string sourceAField1 = "";
        [ObservableProperty] private string sourceAField2 = "";
        [ObservableProperty] private string sourceAField3 = "";

        // === Source B fields (e.g., OCR-extracted data) ===
        [ObservableProperty] private string sourceBField1 = "";
        [ObservableProperty] private string sourceBField2 = "";
        [ObservableProperty] private string sourceBField3 = "";

        // === Background colors for mismatch highlighting ===
        [ObservableProperty] private string sourceBField1Background = "Transparent";
        [ObservableProperty] private string sourceBField2Background = "Transparent";
        [ObservableProperty] private string sourceBField3Background = "Transparent";

        // === Checkbox verification per field ===
        [ObservableProperty] private bool isField1Checked;
        [ObservableProperty] private bool isField2Checked;
        [ObservableProperty] private bool isField3Checked;

        // === Editable fields (trigger recalculation) ===
        [ObservableProperty] private decimal editableUnitPrice;
        [ObservableProperty] private string editableDeliveryDate = "";
        [ObservableProperty] private bool isModified = false;

        // === Editable field backgrounds ===
        [ObservableProperty] private string editableUnitPriceBackground = "White";

        partial void OnEditableUnitPriceChanged(decimal value)
        {
            IsModified = true;
            UpdateMismatchBackgrounds();
            RecalculateMatchingScore();
        }

        partial void OnIsField1CheckedChanged(bool value)
        {
            UpdateMismatchBackgrounds();
        }

        /// <summary>
        /// Update backgrounds: pink (#F8D7DA) for mismatch, green (#BBF7D0) when checked, Transparent otherwise.
        /// </summary>
        public void UpdateMismatchBackgrounds()
        {
            SourceBField1Background = IsField1Checked ? "#BBF7D0"
                : IsMismatch(SourceAField1, SourceBField1) ? "#F8D7DA"
                : "Transparent";

            SourceBField2Background = IsField2Checked ? "#BBF7D0"
                : IsMismatch(SourceAField2, SourceBField2) ? "#F8D7DA"
                : "Transparent";

            SourceBField3Background = IsField3Checked ? "#BBF7D0"
                : IsMismatch(SourceAField3, SourceBField3) ? "#F8D7DA"
                : "Transparent";
        }

        private static bool IsMismatch(string? a, string? b)
            => (a ?? string.Empty) != (b ?? string.Empty);

        /// <summary>
        /// Count visible fields that have not been checked by the user.
        /// </summary>
        public int GetUncheckedVisibleCount()
        {
            int count = 0;
            if (HasDisplayValue(SourceAField1) && !IsField1Checked) count++;
            if (HasDisplayValue(SourceAField2) && !IsField2Checked) count++;
            if (HasDisplayValue(SourceAField3) && !IsField3Checked) count++;
            return count;
        }

        /// <summary>
        /// Recalculate matching score after editable field changes.
        /// Delegate to domain matching service with updated values.
        /// </summary>
        private void RecalculateMatchingScore()
        {
            // Re-run matching with updated values via domain service
            // ScorePercent = newResult.Score.ScorePercent;
            // IsSuccessful = ScorePercent >= 80.0;
            // ScoreColor = IsSuccessful ? "Green" : "Red";
        }

        public void UpdateScoreColor()
        {
            ScoreColor = IsSuccessful ? "Green" : (ScorePercent >= 60 ? "Orange" : "Red");
        }

        // === Visibility (HasDisplayValue pattern) ===
        public bool IsField1Visible => HasDisplayValue(SourceAField1);
        public bool IsField2Visible => HasDisplayValue(SourceAField2);
        public bool IsField3Visible => HasDisplayValue(SourceAField3);

        private static bool HasDisplayValue(string? value)
        {
            if (string.IsNullOrWhiteSpace(value)) return false;
            return value.Trim() != "-";
        }

        partial void OnSourceAField1Changed(string value)
        {
            OnPropertyChanged(nameof(IsField1Visible));
        }
    }
}
```
