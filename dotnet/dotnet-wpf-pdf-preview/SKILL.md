---
name: dotnet-wpf-pdf-preview
description: Use when adding PDF upload and inline WebView2 preview to a WPF app with MVVM file selection and async initialization.
author: RyoMurakami1983
tags: [dotnet, wpf, csharp, mvvm, webview2, pdf]
invocable: false
version: 1.0.0
---

# Add PDF Upload and WebView2 Preview to WPF Applications

End-to-end workflow for adding **Portable Document Format (PDF)** file upload with inline preview to **Windows Presentation Foundation (WPF)** applications: WebView2 (Microsoft Edge WebView2) based PDF rendering, **Model-View-ViewModel (MVVM)** file selection with `CommunityToolkit.Mvvm`, event-based ViewModel→View communication, and async WebView2 initialization with error handling.

## When to Use This Skill

Use this skill when:
- Adding a PDF upload and preview panel to a WPF application
- Displaying PDF files inline using Microsoft Edge WebView2
- Building a split-panel layout with PDF preview on the left and content on the right
- Implementing file selection in ViewModel while keeping WebView2 in code-behind
- Creating an order sheet upload UI that shows the uploaded document

---

## Related Skills

- **`dotnet-wpf-secure-config`** — DPAPI encryption foundation for credential storage
- **`dotnet-wpf-dify-api-integration`** — Send uploaded PDF to Dify API for OCR extraction
- **`dotnet-oracle-wpf-integration`** — Store extracted PDF data in Oracle database
- **`git-commit-practices`** — Commit each step as an atomic change

---

## Core Principles

1. **MVVM Discipline** — ViewModel owns file selection logic; View owns WebView2 rendering (基礎と型)
2. **Minimal Code-Behind** — Only WebView2 initialization and navigation live in code-behind (基礎と型)
3. **Event-Based Communication** — ViewModel notifies View via events, not direct control access (ニュートラル)
4. **Async by Default** — WebView2 initialization is async; never block the UI thread (継続は力)
5. **Graceful Degradation** — Handle missing WebView2 Runtime without crashing (ニュートラル)

---

## Workflow: Add PDF Preview to WPF

### Step 1 — Install WebView2 and Set Up Layout

Use when adding the WebView2 NuGet package and creating the split-panel XAML layout.

Install the WebView2 package and create a 2-column Grid with PDF preview on the left and content area on the right.

```powershell
# Install WebView2 NuGet package
Install-Package Microsoft.Web.WebView2
```

```
YourApp/
├── Views/
│   └── MainWindow.xaml          # 🆕 2-column layout with WebView2
│   └── MainWindow.xaml.cs       # 🆕 WebView2 init + navigation
└── ViewModels/
    └── MainViewModel.cs         # 🆕 File selection + path management
```

**XAML layout template** — 2-column split panel:

```xml
<Window x:Class="YourApp.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:wv2="clr-namespace:Microsoft.Web.WebView2.Wpf;assembly=Microsoft.Web.WebView2.Wpf"
        Title="PDF Preview" Height="700" Width="1200">
    <Grid>
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="1*"/>   <!-- Left: PDF Preview -->
            <ColumnDefinition Width="1.5*"/> <!-- Right: Content -->
        </Grid.ColumnDefinitions>

        <Grid Grid.Column="0" Margin="5">
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>  <!-- Upload Button -->
                <RowDefinition Height="*"/>     <!-- PDF Preview -->
            </Grid.RowDefinitions>

            <Button Grid.Row="0" Content="Upload PDF"
                    Command="{Binding UploadPdfCommand}"
                    Background="#2196F3" Foreground="White" FontWeight="Bold"/>

            <Border Grid.Row="1" BorderBrush="#CCCCCC" BorderThickness="1">
                <wv2:WebView2 x:Name="PdfWebView" />
            </Border>
        </Grid>

        <!-- Right column: your content area -->
        <Grid Grid.Column="1" Margin="5">
            <!-- Add your application content here -->
        </Grid>
    </Grid>
</Window>
```

**Why WebView2 uses x:Name**: WebView2 requires imperative initialization (`EnsureCoreWebView2Async`) and navigation (`CoreWebView2.Navigate`). These APIs have no bindable equivalents, making `x:Name` the accepted MVVM exception.

> **Values**: 基礎と型 / 継続は力

### Step 2 — Implement ViewModel (File Selection + Path Management)

Use when creating the ViewModel that handles PDF file selection via `OpenFileDialog` and notifies the View.

Create `MainViewModel` with `CommunityToolkit.Mvvm`, using `[ObservableProperty]` for state and `[RelayCommand]` for the upload action. The `PdfPathChanged` event bridges ViewModel→View communication.

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;

namespace YourApp.ViewModels
{
    public partial class MainViewModel : ObservableObject
    {
        /// <summary>
        /// Event to notify View when a new PDF is selected.
        /// Code-behind subscribes to this for WebView2 navigation.
        /// </summary>
        public event EventHandler<string>? PdfPathChanged;

        [ObservableProperty]
        private string pdfFilePath = string.Empty;

        [ObservableProperty]
        private bool isPdfLoaded;

        [RelayCommand]
        private void UploadPdf()
        {
            var dialog = new Microsoft.Win32.OpenFileDialog
            {
                Filter = "PDF files (*.pdf)|*.pdf",
                Title = "Select PDF file"
            };
            if (dialog.ShowDialog() == true)
            {
                PdfFilePath = dialog.FileName;
                IsPdfLoaded = true;
                PdfPathChanged?.Invoke(this, PdfFilePath);
            }
        }
    }
}
```

**Why event pattern instead of binding**: WebView2's `Source` property does not support reliable two-way binding for local file URLs. The event pattern gives explicit control over navigation timing and error handling.

> **Values**: 基礎と型 / ニュートラル

### Step 3 — Initialize WebView2 (Code-Behind)

Use when wiring up WebView2 initialization and PDF navigation in the Window code-behind.

Create minimal code-behind that initializes WebView2 asynchronously and subscribes to the ViewModel's `PdfPathChanged` event for navigation.

```csharp
using System;
using System.Windows;

namespace YourApp.Views
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            var viewModel = new MainViewModel();
            DataContext = viewModel;
            InitializeWebView();
            viewModel.PdfPathChanged += OnPdfPathChanged;
        }

        private async void InitializeWebView()
        {
            try
            {
                await PdfWebView.EnsureCoreWebView2Async(null);
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"WebView2 Runtime not found.\n\n" +
                    $"Please install the WebView2 Runtime from:\n" +
                    $"https://developer.microsoft.com/microsoft-edge/webview2/\n\n" +
                    $"Error: {ex.Message}",
                    "WebView2 Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Warning);
            }
        }

        private void OnPdfPathChanged(object? sender, string pdfPath)
        {
            if (PdfWebView.CoreWebView2 != null)
            {
                PdfWebView.CoreWebView2.Navigate($"file:///{pdfPath}");
            }
        }
    }
}
```

**Why async void is acceptable here**: `InitializeWebView` is a fire-and-forget UI initialization. The `try/catch` handles all failure cases. This is one of the few places where `async void` is appropriate — event-like UI startup.

> **Values**: ニュートラル / 基礎と型

### Step 4 — Add XAML Namespace and Wire Up

Use when verifying all XAML namespaces and bindings are correctly connected.

Ensure the WebView2 XAML namespace is declared and the button command is bound to the ViewModel.

**Required XAML namespace** (in Window tag):

```xml
xmlns:wv2="clr-namespace:Microsoft.Web.WebView2.Wpf;assembly=Microsoft.Web.WebView2.Wpf"
```

**Binding checklist**:

```xml
<!-- ✅ CORRECT — Button bound to ViewModel command -->
<Button Command="{Binding UploadPdfCommand}" Content="Upload PDF" />

<!-- ❌ WRONG — Click handler in code-behind -->
<Button Click="OnUploadClick" Content="Upload PDF" />
```

```xml
<!-- ✅ CORRECT — WebView2 uses x:Name (MVVM exception) -->
<wv2:WebView2 x:Name="PdfWebView" />

<!-- ❌ WRONG — Trying to bind Source directly -->
<wv2:WebView2 Source="{Binding PdfFileUri}" />
```

> **Values**: 基礎と型 / ニュートラル

### Step 5 — Handle Edge Cases

Use when adding robustness for deployment and real-world usage scenarios.

Handle the three main failure scenarios: missing runtime, large files, and re-upload state.

**WebView2 Runtime missing**:

```csharp
// ✅ Graceful fallback when WebView2 Runtime is not installed
private async void InitializeWebView()
{
    try
    {
        await PdfWebView.EnsureCoreWebView2Async(null);
    }
    catch (Exception)
    {
        // Show fallback UI or download link
        PdfWebView.Visibility = Visibility.Collapsed;
        // Show a TextBlock with download instructions instead
    }
}
```

**Re-upload (state reset)**:

```csharp
[RelayCommand]
private void UploadPdf()
{
    var dialog = new Microsoft.Win32.OpenFileDialog
    {
        Filter = "PDF files (*.pdf)|*.pdf",
        Title = "Select PDF file"
    };
    if (dialog.ShowDialog() == true)
    {
        // ✅ Reset state before loading new PDF
        PdfFilePath = dialog.FileName;
        IsPdfLoaded = true;
        PdfPathChanged?.Invoke(this, PdfFilePath);
    }
}
```

**Large PDF files** — WebView2 handles large PDFs natively via Chromium's built-in PDF viewer. No special handling is required, but consider showing a loading indicator:

```csharp
private void OnPdfPathChanged(object? sender, string pdfPath)
{
    if (PdfWebView.CoreWebView2 != null)
    {
        // Chromium PDF viewer handles large files with streaming
        PdfWebView.CoreWebView2.Navigate($"file:///{pdfPath}");
    }
}
```

> **Values**: ニュートラル / 継続は力

### Step 6 — Customize for Your Application

Use when preparing the generated code for production deployment.

Replace these placeholders before shipping:

| Item | File | What to Change | Impact if Skipped |
|------|------|----------------|-------------------|
| Namespace | All `.cs` files | `YourApp` → actual namespace | Build errors |
| Window title | `MainWindow.xaml` | `"PDF Preview"` → actual title | Generic window title |
| Column ratio | `MainWindow.xaml` | `1*` / `1.5*` → desired ratio | Layout mismatch |
| Button style | `MainWindow.xaml` | Colors and font to match your theme | Inconsistent UI |
| Upload filter | `MainViewModel.cs` | File dialog filter if accepting other types | Wrong file types |

**Customization checklist**:

```powershell
# Verify all placeholders are replaced
Select-String -Path "Views/*.xaml","Views/*.cs","ViewModels/*.cs" -Pattern "YourApp" -SimpleMatch
# Expected: 0 matches after customization
```

> **Values**: 基礎と型 / 成長の複利

---

## Good Practices

### 1. Keep WebView2 Code in Code-Behind

**What**: WebView2 initialization and navigation stay in `MainWindow.xaml.cs`, not in ViewModel.

**Why**: WebView2 requires `x:Name` and imperative API calls (`EnsureCoreWebView2Async`, `CoreWebView2.Navigate`). This is the accepted MVVM exception — the code-behind acts as a thin adapter between ViewModel events and WebView2 APIs.

**Values**: 基礎と型（MVVM例外の型）

### 2. Use Event Pattern for ViewModel→View Communication

**What**: ViewModel raises `PdfPathChanged` event; code-behind subscribes and navigates WebView2.

**Why**: Keeps ViewModel testable (no UI dependency) while giving the View explicit control over navigation timing. Alternative approaches (Messenger, behavior) add complexity without benefit for this use case.

**Values**: ニュートラル / 基礎と型

### 3. Initialize WebView2 Async on Window Load

**What**: Call `EnsureCoreWebView2Async` in the constructor or `Loaded` event, not on first PDF upload.

**Why**: WebView2 initialization takes 100–500ms. Doing it upfront avoids a visible delay when the user first clicks Upload.

**Values**: 継続は力（先回りの準備）

### 4. Quick Language Checklist

- Use **Portable Document Format (PDF)** on first mention, then use "PDF".
- Use **Windows Presentation Foundation (WPF)** and **Model-View-ViewModel (MVVM)** on first mention.
- Implement WebView2 initialization with `EnsureCoreWebView2Async` before first navigation.
- Avoid binding `WebView2.Source` directly for local PDF files; navigate imperatively.
- Consider handling missing WebView2 Runtime with a user-facing message and link.

---

## Common Pitfalls

### 1. Forgetting to Install WebView2 Runtime on Deployment Machines

**Problem**: WebView2 Runtime is pre-installed on Windows 11 but may be missing on Windows 10 or locked-down corporate machines.

**Solution**: Include the WebView2 Evergreen Bootstrapper in your installer, or detect and prompt the user with a download link. Always wrap `EnsureCoreWebView2Async` in try/catch.

```csharp
// ❌ WRONG — No error handling, crashes on machines without Runtime
await PdfWebView.EnsureCoreWebView2Async(null);

// ✅ CORRECT — Graceful fallback
try { await PdfWebView.EnsureCoreWebView2Async(null); }
catch (Exception ex) { ShowWebView2MissingMessage(ex); }
```

### 2. Trying to Bind WebView2 Source Property Directly

**Problem**: Attempting `<wv2:WebView2 Source="{Binding PdfUri}" />` for local file URLs does not work reliably.

**Solution**: Use the event pattern (Step 2–3) with `CoreWebView2.Navigate()` for reliable local file navigation.

```csharp
// ❌ WRONG — Binding Source for local files
<wv2:WebView2 Source="{Binding PdfFileUri}" />

// ✅ CORRECT — Imperative navigation via event
PdfWebView.CoreWebView2.Navigate($"file:///{pdfPath}");
```

### 3. Not Handling WebView2 Initialization Failure

**Problem**: `EnsureCoreWebView2Async` throws if WebView2 Runtime is missing or corrupted, causing an unhandled exception crash.

**Solution**: Always wrap in try/catch and show a user-friendly message with the Runtime download URL.

---

## Anti-Patterns

### Putting File Dialog Logic in Code-Behind

**What**: Opening `OpenFileDialog` directly in `MainWindow.xaml.cs` button click handlers.

**Why It's Wrong**: Violates MVVM separation. File selection is application logic, not UI rendering. Code-behind file dialog logic cannot be unit tested.

**Better Approach**: Use `[RelayCommand]` in ViewModel to handle file selection. The dialog result updates ViewModel properties, which the View observes.

### Using x:Name for Controls Other Than WebView2

**What**: Adding `x:Name` to TextBoxes, Buttons, or DataGrids and manipulating them in code-behind.

**Why It's Wrong**: Bypasses data binding and makes the UI tightly coupled to code-behind. Every `x:Name` reference is a missed binding opportunity.

**Better Approach**: Use `{Binding}` for all standard WPF controls. Reserve `x:Name` exclusively for controls that require imperative APIs (WebView2).

```csharp
// ❌ WRONG — Manipulating controls by name
StatusLabel.Text = "PDF loaded";
UploadButton.IsEnabled = false;

// ✅ CORRECT — Bind to ViewModel properties
[ObservableProperty] private string statusText = "Ready";
[ObservableProperty] private bool canUpload = true;
```

---

## Quick Reference

### Implementation Checklist

- [ ] Install `Microsoft.Web.WebView2` NuGet package
- [ ] Add `wv2` XAML namespace for WebView2
- [ ] Create 2-column Grid layout (preview + content)
- [ ] Add `WebView2` control with `x:Name="PdfWebView"`
- [ ] Create ViewModel with `[RelayCommand]` for upload
- [ ] Add `PdfPathChanged` event in ViewModel
- [ ] Subscribe to event in code-behind
- [ ] Initialize WebView2 async with try/catch
- [ ] Navigate to PDF via `CoreWebView2.Navigate()`
- [ ] Test with WebView2 Runtime missing scenario

### File Structure

| File | Purpose | Layer |
|------|---------|-------|
| `MainWindow.xaml` | 2-column layout + WebView2 | View |
| `MainWindow.xaml.cs` | WebView2 init + navigation | View (code-behind) |
| `MainViewModel.cs` | File selection + state | ViewModel |

### WebView2 Navigation Patterns

| Scenario | Code | Notes |
|----------|------|-------|
| Local PDF file | `CoreWebView2.Navigate($"file:///{path}")` | Convert to an absolute path and URL-escape if needed. |
| Blank page | `CoreWebView2.Navigate("about:blank")` | Use to reset the preview on errors. |
| Check readiness | `if (PdfWebView.CoreWebView2 != null)` | Guard before calling `Navigate`. |

---

## Resources

- [Microsoft WebView2 SDK Documentation](https://docs.microsoft.com/microsoft-edge/webview2/)
- [WebView2 NuGet Package](https://www.nuget.org/packages/Microsoft.Web.WebView2)
- [WebView2 Runtime Download](https://developer.microsoft.com/microsoft-edge/webview2/)
- [CommunityToolkit.Mvvm Documentation](https://learn.microsoft.com/dotnet/communitytoolkit/mvvm/)

---

## Changelog

### Version 1.0.0 (2026-02-15)
- Initial release: single-workflow PDF upload + WebView2 preview guide
- 6-step workflow: Layout → ViewModel → Code-Behind → Namespace → Edge Cases → Customize
- Event-based ViewModel→View communication pattern
- WebView2 async initialization with error handling
- CommunityToolkit.Mvvm integration with `[RelayCommand]` and `[ObservableProperty]`

<!--
Japanese version available at references/SKILL.ja.md
-->
