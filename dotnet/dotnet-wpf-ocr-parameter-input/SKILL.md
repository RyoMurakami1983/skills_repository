---
name: dotnet-wpf-ocr-parameter-input
description: Build an OCR execution parameter input UI tab in WPF with progress display. Use when adding OCR processing tabs with configurable input fields.
author: RyoMurakami1983
tags: [dotnet, wpf, csharp, mvvm, ocr, progress, tab]
invocable: false
version: 1.0.0
---

# Build OCR Execution Parameter Input Tab with Progress Display

End-to-end workflow for adding an OCR execution parameter input UI tab to .NET WPF applications: configurable input fields (ComboBox, TextBox, CheckBox), async OCR execution with `IProgress<T>`, real-time progress bar and log display, and event-based result handoff to parent ViewModel.

## When to Use This Skill

Use this skill when:
- Adding an OCR processing tab with user-configurable input parameters
- Building a progress display (bar + log) for long-running OCR operations
- Creating a tab UI that collects selection fields, text fields, and toggles before execution
- Implementing async OCR execution with real-time progress reporting
- Wiring OCR completion events to parent ViewModels for result handling

---

## Related Skills

- **`dotnet-wpf-pdf-preview`** — PDF upload and WebView2 preview (provides the PDF path input)
- **`dotnet-wpf-dify-api-integration`** — Dify API integration for OCR extraction backend
- **`dotnet-oracle-wpf-integration`** — Store OCR results in Oracle database
- **`dotnet-wpf-comparison-view`** — Display OCR results alongside original PDF for comparison
- **`git-commit-practices`** — Commit each step as an atomic change

---

## Dependencies

- .NET + WPF (Windows Presentation Foundation)
- `CommunityToolkit.Mvvm` (ObservableObject, `[ObservableProperty]`, `[RelayCommand]`)
- An OCR execution use case interface (e.g., `IOcrUseCase`) and an OCR backend (Dify, etc.)

---

## Core Principles

1. **Ask First, Build Second** — Input fields vary per use case; always ask the user what fields they need before generating code (ニュートラル)
2. **MVVM Discipline** — ViewModel owns all input state and OCR execution logic; View is purely declarative XAML (基礎と型)
3. **Async Progress Reporting** — Use `IProgress<T>` for thread-safe progress updates from async OCR operations (継続は力)
4. **Event-Based Handoff** — OCR results flow to parent ViewModel via events, not direct coupling (ニュートラル)
5. **Reusable Skeleton** — The tab pattern (input → progress → result) applies to any long-running process, not just OCR (成長の複利)

---

## Workflow: Add OCR Parameter Input Tab to WPF

### Step 1 — Define Input Field Requirements

Use when determining what input fields the OCR tab needs before writing any code.

⚠️ **Ask the user** what input fields they need. The specific fields vary per use case — do not assume. Gather requirements first, then generate code.

**Common field types**:
- **Selection fields** (ComboBox) — e.g., classification categories, document types
- **Text fields** (TextBox) — e.g., additional instructions, remarks, reference numbers
- **Toggle fields** (CheckBox) — e.g., domestic/export selection, priority flags

**Field definition template**:

```csharp
public class OcrInputField
{
    public string Label { get; set; }
    public string FieldType { get; set; } // "ComboBox", "TextBox", "CheckBox"
    public List<string>? Options { get; set; } // For ComboBox
}
```

**Example requirements gathering**:

| Field Name | Type | Options | Required |
|-----------|------|---------|----------|
| Category | ComboBox | Ask user | ✅ |
| Document Type | ComboBox | Ask user | ✅ |
| Remarks | TextBox | Free-form | ❌ |
| Export Flag | CheckBox | On/Off | ❌ |

```
YourApp/
├── Views/
│   └── OcrProcessTabView.xaml          # 🆕 Tab UI with input fields + progress
│   └── OcrProcessTabView.xaml.cs       # 🆕 Minimal code-behind
├── ViewModels/
│   └── OcrProcessTabViewModel.cs       # 🆕 Input state + OCR execution + progress
└── Models/
    └── ProgressLogItem.cs              # 🆕 Progress log entry model
```

> **Values**: ニュートラル / 基礎と型

### Step 2 — Create Tab ViewModel

Use when implementing the ViewModel that manages input fields, OCR execution, and progress tracking.

Create `OcrProcessTabViewModel` with `CommunityToolkit.Mvvm`. Input field properties should be customized per use case (Step 1 results). Progress tracking and OCR execution follow a fixed pattern.

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace YourApp.ViewModels;

public partial class OcrProcessTabViewModel : ObservableObject
{
    [ObservableProperty] private bool canStartOcr;
    [ObservableProperty] private int progressValue;

    public event EventHandler<IEnumerable<object>>? OcrCompleted;

    [RelayCommand(CanExecute = nameof(CanStartOcr))]
    private async Task StartOcrAsync()
    {
        // Collect inputs → call use case → report progress → raise OcrCompleted.
    }

    public void OnPdfUploaded(string pdfPath)
    {
        CanStartOcr = !string.IsNullOrWhiteSpace(pdfPath);
        StartOcrCommand.NotifyCanExecuteChanged();
    }
}
```

Full example: `references/OcrProcessTabViewModel.full.md`

**Why `CanExecute` on the command**: The Start button is disabled until a PDF is uploaded. `NotifyCanExecuteChanged()` refreshes the button state when `CanStartOcr` changes.

> **Values**: 基礎と型 / 継続は力

### Step 3 — Build XAML Tab View

Use when creating the tab UI with input fields, progress bar, progress log, and Start button.

Tab layout uses a 4-row Grid: input fields section, progress bar with percentage overlay, scrollable progress log (ListView with GridView columns), and a Start button that enables after PDF upload.

```xml
<UserControl x:Class="YourApp.Views.OcrProcessTabView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Grid>
        <!-- Inputs → Progress bar → Log list → Start button -->
    </Grid>
</UserControl>
```

Full example: `references/OcrProcessTabView.full.md`

**Why UserControl, not Window**: Tabs are embedded in a parent `TabControl`. `UserControl` integrates naturally; `Window` would require separate window management.

> **Values**: 基礎と型 / ニュートラル

### Step 4 — Create Progress Log Item Model

Use when defining the data model for individual progress log entries displayed in the ListView.

Create a simple immutable model for each row in the progress log. The constructor enforces all fields are set on creation.

```csharp
namespace YourApp.Models
{
    public class ProgressLogItem
    {
        public DateTime Timestamp { get; }
        public string Icon { get; }
        public string Message { get; }
        public string Status { get; }

        public ProgressLogItem(DateTime timestamp, string icon, string message, string status)
        {
            Timestamp = timestamp;
            Icon = icon;
            Message = message;
            Status = status;
        }
    }
}
```

**Icon conventions**:

| Icon | Meaning |
|------|---------|
| 🔄 | Processing / in progress |
| ✅ | Completed successfully |
| ❌ | Error occurred |
| ⚠️ | Warning |

> **Values**: 基礎と型 / 成長の複利

### Step 5 — Wire Events and Tab Integration

Use when connecting the OCR tab to the parent ViewModel and integrating into a `TabControl`.

The parent ViewModel creates the tab ViewModel, subscribes to `OcrCompleted`, and manages tab switching. PDF upload events flow from the parent to the OCR tab via `OnPdfUploaded`.

**Parent ViewModel wiring**:

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

**TabControl integration in MainWindow.xaml**:

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

**Event flow**:

```
PDF Upload → Parent.NotifyPdfUploaded() → OcrTab.OnPdfUploaded()
                                            ↓ (enables Start button)
User clicks Start → OcrTab.StartOcrAsync() → IProgress updates UI
                                            ↓ (on completion)
OcrTab.OcrCompleted event → Parent.OnOcrCompleted() → Switch to results tab
```

**State reset on new PDF upload**:

```csharp
private void NotifyPdfUploaded(string pdfPath)
{
    OcrTab.Reset();              // Clear previous progress
    OcrTab.OnPdfUploaded(pdfPath); // Enable Start button
}
```

> **Values**: ニュートラル / 継続は力

### Step 6 — Customize Input Fields

Use when adapting the generated skeleton to the specific use case requirements gathered in Step 1.

⚠️ **Replace placeholder fields** with the actual fields identified in Step 1. This table guides the customization:

| Customization | File | What to Change |
|--------------|------|----------------|
| Input field properties | `OcrProcessTabViewModel.cs` | Add/remove `[ObservableProperty]` fields |
| ComboBox options | `OcrProcessTabViewModel.cs` | Populate `ObservableCollection` items |
| XAML input section | `OcrProcessTabView.xaml` | Add/remove ComboBox, TextBox, CheckBox controls |
| Use case parameters | `StartOcrAsync()` | Pass correct input values to `_useCase.ExecuteAsync()` |
| Validation rules | `OcrProcessTabViewModel.cs` | Add field validation before OCR execution |

**Adding a CheckBox toggle field**:

```csharp
// ViewModel
[ObservableProperty] private bool isExport;
```

```xml
<!-- XAML -->
<CheckBox Content="Export" IsChecked="{Binding IsExport}" Margin="0,10,0,0"/>
```

**Adding a required field validation**:

```csharp
[RelayCommand(CanExecute = nameof(CanStartOcr))]
private async Task StartOcrAsync()
{
    // ✅ Validate required fields before execution
    if (string.IsNullOrWhiteSpace(SelectedCategory))
    {
        ProgressItems.Add(new ProgressLogItem(DateTime.Now, "⚠️", "Category is required", "Validation"));
        return;
    }
    // ... proceed with OCR
}
```

> **Values**: ニュートラル / 基礎と型

---

## Good Practices

### 1. Use IProgress\<T\> for Async Progress Reporting

**What**: Pass `IProgress<(int percent, string message)>` to the use case for thread-safe progress callbacks.

**Why**: `IProgress<T>` captures the `SynchronizationContext` at creation time and dispatches callbacks to the UI thread automatically. No manual `Dispatcher.Invoke` needed.

**Values**: 継続は力（非同期の型を正しく使う）

### 2. Dispatch Progress Updates to UI Thread

**What**: Create the `Progress<T>` instance on the UI thread so callbacks marshal back automatically.

**Why**: If `Progress<T>` is created on a background thread, callbacks execute on that thread and throw when updating `ObservableCollection`.

```csharp
// ✅ CORRECT — Created on UI thread, callbacks auto-dispatch
var progress = new Progress<(int percent, string message)>(p =>
{
    ProgressValue = p.percent;
    ProgressItems.Add(new ProgressLogItem(DateTime.Now, "🔄", p.message, "Running"));
});

// ❌ WRONG — Created inside Task.Run, callbacks on background thread
await Task.Run(() =>
{
    var progress = new Progress<(int, string)>(...); // Wrong thread
});
```

**Values**: 基礎と型（スレッド安全の型）

### 3. Disable Start Button During Processing

**What**: Set `IsProcessing = true` at the start and use `CanExecute` to prevent duplicate execution.

**Why**: Double-clicking Start during OCR execution can launch parallel processes, corrupt results, and confuse progress display.

**Values**: ニュートラル（安全なUI操作）

### 4. Reset State for Re-execution

**What**: Clear `ProgressItems`, reset `ProgressValue`, and update `CanStartOcr` when a new PDF is uploaded.

**Why**: Stale progress from a previous run misleads users. Clean state ensures each execution starts fresh.

**Values**: 継続は力（再実行の信頼性）

---

## Common Pitfalls

### 1. Not Dispatching to UI Thread from Async Callback

**Problem**: Updating `ObservableCollection` or `ObservableProperty` from a background thread throws `InvalidOperationException`.

**Solution**: Create `Progress<T>` on the UI thread (before `await`). The `IProgress<T>.Report()` call from the background thread will automatically dispatch to the captured `SynchronizationContext`.

```csharp
// ❌ WRONG — Direct collection update from background thread
await Task.Run(() =>
{
    ProgressItems.Add(new ProgressLogItem(...)); // Throws!
});

// ✅ CORRECT — IProgress<T> handles marshaling
var progress = new Progress<(int percent, string message)>(p =>
{
    ProgressItems.Add(new ProgressLogItem(DateTime.Now, "🔄", p.message, "Running"));
});
await _useCase.ExecuteAsync(progress); // Reports from background thread safely
```

### 2. Forgetting to Re-enable Start Button After Completion

**Problem**: `IsProcessing` set to `true` but never reset on exception, permanently disabling the Start button.

**Solution**: Always reset `IsProcessing` in a `finally` block.

```csharp
// ❌ WRONG — IsProcessing stuck on exception
IsProcessing = true;
var results = await _useCase.ExecuteAsync(progress);
IsProcessing = false; // Never reached on exception

// ✅ CORRECT — finally guarantees reset
try { var results = await _useCase.ExecuteAsync(progress); }
finally { IsProcessing = false; }
```

### 3. Not Clearing Progress Log on Re-execution

**Problem**: Previous run's log entries mix with the new run, confusing the user.

**Solution**: Call `ProgressItems.Clear()` and `ProgressValue = 0` at the start of every execution.

```csharp
[RelayCommand(CanExecute = nameof(CanStartOcr))]
private async Task StartOcrAsync()
{
    // ✅ Always clear before starting
    ProgressItems.Clear();
    ProgressValue = 0;
    // ... execute OCR
}
```

---

## Anti-Patterns

### Blocking UI Thread with Synchronous Processing

**What**: Calling `.Wait()` or `.Result` on async OCR operations from the UI thread.

**Why It's Wrong**: Blocks the UI thread, freezes the window, prevents progress bar updates, and can cause deadlocks with `SynchronizationContext`.

**Better Approach**: Use `async Task` with `await` throughout. The `[RelayCommand]` attribute generates an `IAsyncRelayCommand` that handles async execution correctly.

```csharp
// ❌ WRONG — Blocks UI, no progress updates
[RelayCommand]
private void StartOcr()
{
    var results = _useCase.ExecuteAsync(progress).Result; // Deadlock risk
}

// ✅ CORRECT — Non-blocking, progress updates flow
[RelayCommand(CanExecute = nameof(CanStartOcr))]
private async Task StartOcrAsync()
{
    var results = await _useCase.ExecuteAsync(progress);
}
```

### Hardcoding Input Fields Instead of Making Them Configurable

**What**: Embedding specific field names and options directly in the ViewModel without asking the user.

**Why It's Wrong**: Every use case has different input requirements. Hardcoded fields force users to refactor the entire tab when requirements change.

**Better Approach**: Follow Step 1 — ask the user what fields they need. Generate the ViewModel and XAML from their requirements. Provide the skeleton pattern, not a rigid implementation.

---

## Quick Reference

### Implementation Checklist

- [ ] Ask user what input fields they need (Step 1)
- [ ] Create `ProgressLogItem` model class (Step 4)
- [ ] Create `OcrProcessTabViewModel` with input fields + progress (Step 2)
- [ ] Create `OcrProcessTabView.xaml` with 4-row Grid layout (Step 3)
- [ ] Wire `OcrCompleted` event in parent ViewModel (Step 5)
- [ ] Integrate tab into `TabControl` (Step 5)
- [ ] Wire `OnPdfUploaded` from parent PDF upload flow (Step 5)
- [ ] Customize input fields per use case (Step 6)
- [ ] Test: Start button disabled until PDF uploaded
- [ ] Test: progress bar updates during OCR execution
- [ ] Test: progress log shows timestamped entries
- [ ] Test: Start button disabled during processing
- [ ] Test: re-upload clears previous progress

### File Structure

| File | Purpose | Layer |
|------|---------|-------|
| `OcrProcessTabView.xaml` | Tab UI with input fields + progress display | View |
| `OcrProcessTabView.xaml.cs` | Minimal code-behind | View (code-behind) |
| `OcrProcessTabViewModel.cs` | Input state + OCR execution + progress | ViewModel |
| `ProgressLogItem.cs` | Progress log entry model | Model |

### Progress Icon Reference

| Icon | Usage | When |
|------|-------|------|
| 🔄 | In progress | Each progress callback |
| ✅ | Success | OCR completed |
| ❌ | Error | Exception caught |
| ⚠️ | Warning | Validation failure |

---

## Resources

- **`dotnet-wpf-pdf-preview`** — PDF upload that feeds into this tab
- **`dotnet-wpf-dify-api-integration`** — Dify API backend for OCR execution
- [CommunityToolkit.Mvvm Documentation](https://learn.microsoft.com/dotnet/communitytoolkit/mvvm/)
- [IProgress\<T\> Pattern](https://learn.microsoft.com/dotnet/api/system.progress-1)
- [WPF TabControl](https://learn.microsoft.com/dotnet/desktop/wpf/controls/tabcontrol)

---

## Changelog

### Version 1.0.0 (2026-02-18)
- Initial release: OCR execution parameter input tab with progress display
- 6-step workflow: Requirements → ViewModel → XAML → Model → Events → Customize
- Configurable input fields pattern (ask user first)
- IProgress\<T\> async progress reporting with UI thread safety
- Progress bar + timestamped log ListView
- Event-based OCR result handoff to parent ViewModel
- CommunityToolkit.Mvvm integration with `[RelayCommand]` and `[ObservableProperty]`

<!--
Japanese version available at references/SKILL.ja.md
-->
