# Detailed Patterns — dotnet-wpf-ocr-parameter-input

Extended code examples referenced from the main [SKILL.md](../SKILL.md).

---

## Parent ViewModel Wiring (Step 5)

```csharp
public partial class MainViewModel : ObservableObject
{
    public OcrProcessTabViewModel OcrTab { get; }

    [ObservableProperty] private int selectedTabIndex;

    public MainViewModel(IOcrUseCase useCase)
    {
        OcrTab = new OcrProcessTabViewModel(useCase);
        OcrTab.OcrCompleted += OnOcrCompleted;
    }

    private void OnOcrCompleted(object? sender, IEnumerable<object> results)
    {
        // Handle OCR results (e.g., populate comparison view)
        SelectedTabIndex = 2; // Switch to results tab
    }

    // Called when PDF is uploaded (e.g., from PDF preview tab)
    private void NotifyPdfUploaded(string pdfPath)
    {
        OcrTab.OnPdfUploaded(pdfPath);
    }
}
```

---

## TabControl Integration (Step 5)

```xml
<TabControl SelectedIndex="{Binding SelectedTabIndex}">
    <TabItem Header="PDF Preview">
        <!-- PDF preview content -->
    </TabItem>
    <TabItem Header="OCR Process">
        <local:OcrProcessTabView DataContext="{Binding OcrTab}"/>
    </TabItem>
    <TabItem Header="Results">
        <!-- Results content -->
    </TabItem>
</TabControl>
```

---

## State Reset on New PDF Upload (Step 5)

```csharp
private void NotifyPdfUploaded(string pdfPath)
{
    OcrTab.Reset();              // Clear previous progress
    OcrTab.OnPdfUploaded(pdfPath); // Enable Start button
}
```
