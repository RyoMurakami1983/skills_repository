---
name: dotnet-wpf-dify-api-integration
description: Add Dify API to WPF apps with DPAPI config and SSE streaming. Use when building Dify integration.
author: RyoMurakami1983
tags: [dotnet, wpf, dify, csharp, mvvm]
invocable: false
version: 1.0.0
---

# Add Dify API Integration to WPF Applications

End-to-end workflow for adding Dify API integration to .NET WPF applications: secure configuration with DPAPI, MVVM settings UI, file upload, and SSE-based workflow streaming.

## When to Use This Skill

Use this skill when:
- Adding Dify API integration to an existing WPF application
- Creating a new WPF project that calls Dify workflows via SSE streaming
- Generating DPAPI-encrypted API key storage for Dify configuration
- Building an MVVM settings dialog for Dify API connection management
- Implementing file upload and streaming workflow execution with real-time progress

---

## Related Skills

- **`dotnet-wpf-secure-config`** — Required: DPAPI encryption foundation (apply first)
- **`dotnet-oracle-wpf-integration`** — Shares SecureConfigService when used in the same app
- **`tdd-standard-practice`** — Test generated code with Red-Green-Refactor
- **`git-commit-practices`** — Commit each step as an atomic change
- **`skills-validate-skill`** — Validate this skill's quality

---

## Core Principles

1. **Layered Architecture** — Separate Presentation, Infrastructure, and Domain concerns (基礎と型)
2. **Security by Default** — DPAPI encryption for API keys; never store plaintext (ニュートラル)
3. **Progressive Integration** — Config → Client → UI, one layer at a time (継続は力)
4. **MVVM Discipline** — ViewModel drives all UI logic; minimal code-behind (基礎と型)
5. **Reusable Components** — Each class works independently across WPF projects (成長の複利)

---

## Workflow: Integrate Dify API into WPF

### Step 1 — Set Up Project Structure

### Step 1 — Verify Prerequisites and Add Dify Files

Use when adding Dify-specific files to a project that already has `dotnet-wpf-secure-config` applied.

**Prerequisites** (must be completed first):
- `dotnet-wpf-secure-config` skill applied
- `Infrastructure/Configuration/` folder exists with:
  - `DpapiEncryptor.cs`
  - `SecureConfigService.cs`
  - `ISecureConfigService.cs`
  - `AppConfigModel.cs`

**Files to add** (Dify-specific):

```
YourApp/
├── Infrastructure/
│   ├── Configuration/
│   │   └── DifyConfigModel.cs          # 🆕 Add this
│   └── Difys/                           # 🆕 Create this folder
│       └── DifyApiService.cs            # 🆕 Add this
└── Presentation/
    ├── ViewModels/
    │   └── DifyConfigViewModel.cs       # 🆕 Add this
    └── Views/
        ├── DifyConfigDialog.xaml        # 🆕 Add this
        └── DifyConfigDialog.xaml.cs     # 🆕 Add this
```

**NuGet packages** (if not already installed):

```powershell
Install-Package CommunityToolkit.Mvvm
Install-Package Microsoft.Extensions.DependencyInjection
```

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Add Dify Config Model

Use when defining the Dify API configuration with DPAPI-encrypted API key.

**Prerequisite**: Apply `dotnet-wpf-secure-config` first to set up `DpapiEncryptor`, `SecureConfigService`, and `AppConfigModel`.

**DifyConfigModel.cs** — Dify-specific setting data (add to `Infrastructure/Configuration/`):

```csharp
public class DifyConfigModel
{
    public string BaseUrl { get; set; } = string.Empty;
    public string ApiKeyEncrypted { get; set; } = string.Empty;
    // ✅ Use employee ID for Dify logs (not Windows username — avoids PII leak)
    public string EmployeeId { get; set; } = string.Empty;

    public string GetDecryptedApiKey()
        => DpapiEncryptor.Decrypt(ApiKeyEncrypted);

    public void SetApiKey(string plainApiKey)
        => ApiKeyEncrypted = DpapiEncryptor.Encrypt(plainApiKey);

    public bool IsValid()
        => !string.IsNullOrWhiteSpace(BaseUrl)
        && !string.IsNullOrWhiteSpace(ApiKeyEncrypted);
}
```

**Update AppConfigModel** (add Dify property):

```csharp
public class AppConfigModel
{
    public DifyConfigModel DifyApi { get; set; } = new();  // 🆕 Add this
    // public OracleConfigModel OracleDb { get; set; } = new();  // Added by Oracle skill
    public string Version { get; set; } = "1.0";
}
```

**Update ISecureConfigService and SecureConfigService** (add Dify methods):

```csharp
// ISecureConfigService — add:
Task<DifyConfigModel> LoadDifyConfigAsync();
Task SaveDifyConfigAsync(DifyConfigModel config);

// SecureConfigService — implement:
public async Task<DifyConfigModel> LoadDifyConfigAsync()
{
    var appConfig = await LoadAppConfigAsync();
    return appConfig.DifyApi;
}

public async Task SaveDifyConfigAsync(DifyConfigModel config)
{
    var appConfig = await LoadAppConfigAsync();
    appConfig.DifyApi = config;
    await SaveAppConfigAsync(appConfig);
}
```

For `DpapiEncryptor`, `SecureConfigService` framework, and `AppConfigModel` base — see `dotnet-wpf-secure-config`.

> **Values**: 基礎と型 / ニュートラル

### Step 3 — Implement API Client (Upload + SSE)

Use when connecting to Dify API for file upload and workflow execution.

Create `DifyApiService` with file upload and streaming workflow execution. Examples use `using var client = new HttpClient()` for simplicity — in production, prefer `IHttpClientFactory` (registered in DI) to avoid socket exhaustion.

**File upload** (`/v1/files/upload`):

```csharp
public class DifyApiService
{
    private readonly ISecureConfigService _configService;

    public DifyApiService(ISecureConfigService configService)
        => _configService = configService;

    public async Task<string> UploadFileAsync(string filePath)
    {
        var config = await _configService.LoadDifyConfigAsync();
        string apiKey = config.GetDecryptedApiKey();
        string baseUrl = config.BaseUrl.TrimEnd('/');

        using var client = new HttpClient();
        client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

        using var form = new MultipartFormDataContent();
        // ✅ Use employee ID — avoids leaking Windows username to external service
        form.Add(new StringContent(config.EmployeeId), "user");
        var fileContent = new ByteArrayContent(await File.ReadAllBytesAsync(filePath));
        fileContent.Headers.ContentType = new MediaTypeHeaderValue("application/pdf");
        form.Add(fileContent, "file", Path.GetFileName(filePath));

        var res = await client.PostAsync($"{baseUrl}/v1/files/upload", form);
        res.EnsureSuccessStatusCode();
        var json = JsonDocument.Parse(await res.Content.ReadAsStringAsync());
        return json.RootElement.GetProperty("id").GetString()!;
    }
}
```

**Workflow execution with SSE** (`/v1/workflows/run`):

```csharp
public async Task<string> RunWorkflowStreamingAsync(
    string uploadFileId, Dictionary<string, object> inputs,
    IProgress<string>? progress = null)
{
    var config = await _configService.LoadDifyConfigAsync();
    string apiKey = config.GetDecryptedApiKey();
    string baseUrl = config.BaseUrl.TrimEnd('/');

    // 5-minute timeout for long-running workflows
    using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(300) };
    client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

    inputs["pdf_file"] = new {
        transfer_method = "local_file", upload_file_id = uploadFileId, type = "document"
    };
    // ✅ Use employee ID for Dify logs (identifiable but not exploitable)
    var body = new { inputs, response_mode = "streaming",
        user = config.EmployeeId };

    var content = new StringContent(
        JsonSerializer.Serialize(body), Encoding.UTF8, "application/json");
    using var req = new HttpRequestMessage(HttpMethod.Post,
        $"{baseUrl}/v1/workflows/run") { Content = content };

    // ResponseHeadersRead avoids buffering the entire SSE stream
    var res = await client.SendAsync(req, HttpCompletionOption.ResponseHeadersRead);
    res.EnsureSuccessStatusCode();
    return await ReadSseStreamAsync(res, progress);
}
```

**SSE stream reader** — Routes events to progress reporter:

```csharp
private async Task<string> ReadSseStreamAsync(
    HttpResponseMessage response, IProgress<string>? progress)
{
    using var reader = new StreamReader(await response.Content.ReadAsStreamAsync());
    string? result = null;

    while (!reader.EndOfStream)
    {
        var line = await reader.ReadLineAsync();
        if (string.IsNullOrWhiteSpace(line) || !line.StartsWith("data:")) continue;

        try
        {
            using var doc = JsonDocument.Parse(line[5..].Trim());
            var evt = doc.RootElement.GetProperty("event").GetString();
            switch (evt)
            {
                case "workflow_started":
                    progress?.Report("▶️ Workflow started"); break;
                case "node_started":
                    var title = doc.RootElement.GetProperty("data")
                        .GetProperty("title").GetString();
                    progress?.Report($"🔄 {title} running..."); break;
                case "node_finished":
                    var d = doc.RootElement.GetProperty("data");
                    var s = d.GetProperty("status").GetString();
                    var t = d.GetProperty("title").GetString();
                    progress?.Report(s == "succeeded" ? $"✅ {t} done" : $"❌ {t} failed");
                    break;
                case "workflow_finished":
                    result = doc.RootElement.GetProperty("data")
                        .GetProperty("outputs").GetRawText();
                    progress?.Report("✅ Workflow complete"); break;
            }
        }
        catch (JsonException) { continue; } // Skip malformed SSE lines
    }
    return result ?? throw new InvalidOperationException("No workflow output received.");
}
```

> **Values**: 継続は力 / 温故知新

### Step 4 — Build MVVM Settings UI

Use when creating or updating the Dify API settings dialog.

Create ViewModel and XAML dialog for Dify API configuration.

**DifyConfigViewModel.cs**:

```csharp
public partial class DifyConfigViewModel : ObservableObject
{
    private readonly ISecureConfigService _configService;

    [ObservableProperty] private string baseUrl = string.Empty;
    [ObservableProperty] private string apiKey = string.Empty;
    [ObservableProperty] private string employeeId = string.Empty;
    [ObservableProperty] private string statusMessage = string.Empty;
    [ObservableProperty] private bool isSaving;

    public DifyConfigViewModel(ISecureConfigService configService)
        => _configService = configService;

    public async Task LoadConfigAsync()
    {
        var cfg = await _configService.LoadDifyConfigAsync();
        BaseUrl = cfg.BaseUrl;
        EmployeeId = cfg.EmployeeId;
        try
        {
            ApiKey = cfg.GetDecryptedApiKey();
        }
        catch (CryptographicException)
        {
            // DPAPI decryption fails if user profile or machine changed
            ApiKey = string.Empty;
            StatusMessage = "Failed to decrypt stored API key. Please re-enter.";
        }
    }

    [RelayCommand]
    private async Task SaveAsync()
    {
        if (string.IsNullOrWhiteSpace(BaseUrl) || string.IsNullOrWhiteSpace(ApiKey))
        { StatusMessage = "Base URL and API Key are required."; return; }

        IsSaving = true;
        try
        {
            var config = new DifyConfigModel
                { BaseUrl = BaseUrl, EmployeeId = EmployeeId };
            config.SetApiKey(ApiKey);
            await _configService.SaveDifyConfigAsync(config);
            StatusMessage = "Saved.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Save failed: {ex.Message}";
        }
        finally
        {
            IsSaving = false;
        }
    }
}
```

**DifyConfigDialog.xaml.cs** — Minimal code-behind (PasswordBox bridging only):

```csharp
public partial class DifyConfigDialog : Window
{
    public DifyConfigDialog(DifyConfigViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
        // PasswordBox does not support two-way binding natively
        Loaded += async (_, _) => await viewModel.LoadConfigAsync();
        viewModel.PropertyChanged += (_, e) =>
        { if (e.PropertyName == nameof(viewModel.ApiKey)) ApiKeyBox.Password = viewModel.ApiKey; };
        ApiKeyBox.PasswordChanged += (_, _) => viewModel.ApiKey = ApiKeyBox.Password;
    }
    private void Close_Click(object sender, RoutedEventArgs e) => Close();
}
```

> **Values**: 基礎と型 / 成長の複利

### Step 5 — Wire DI and Launch

Use when registering services and launching the settings dialog for the first time.

Register services in `App.xaml.cs` and connect the settings dialog.

```csharp
// App.xaml.cs
protected override void OnStartup(StartupEventArgs e)
{
    base.OnStartup(e);
    var services = new ServiceCollection();
    services.AddSingleton<ISecureConfigService, SecureConfigService>();
    services.AddSingleton<DifyApiService>();
    services.AddTransient<DifyConfigViewModel>();
    _serviceProvider = services.BuildServiceProvider();
}
```

```csharp
// Launch from any window
var vm = _serviceProvider.GetRequiredService<DifyConfigViewModel>();
new DifyConfigDialog(vm).ShowDialog();
```

> **Values**: 成長の複利 / 継続は力

### Step 6 — Customize for Your Application

Use when preparing the generated code for production deployment.

Replace these placeholders before shipping:

| Item | File | What to Change |
|------|------|----------------|
| App name | `SecureConfigService.cs` | `"YourAppName"` in config path |
| Salt | `DpapiEncryptor.cs` | `Entropy` byte array value |
| Namespace | All `.cs` files | `YourApp` → actual namespace |
| Workflow inputs | `DifyApiService.cs` | `inputs` dictionary keys |
| Employee ID | `DifyConfigDialog.xaml` | Add TextBox for employee ID |

> **Values**: ニュートラル / 基礎と型

---

## Good Practices

### 1. Validate BaseUrl Scheme Before Saving

**What**: Reject non-HTTPS URLs in the ViewModel's `SaveAsync` method.

**Why**: API keys travel over the wire; HTTP exposes them to interception.

**Values**: ニュートラル（セキュリティを標準化）

### 2. Set Explicit Timeouts per Operation

**What**: 300s for workflow, 30s for upload, 10s for connection test.

**Why**: Prevents indefinite hangs and improves user experience.

**Values**: 継続は力（安定した動作を継続）

### 3. Use IProgress<string> for All Long Operations

**What**: Report progress at each SSE event, not just start and finish.

**Why**: Users see node-level progress instead of a frozen screen.

**Values**: 成長の複利（UXの知見がチームに蓄積）

---

## Common Pitfalls

### 1. Storing API Keys in appsettings.json

**Problem**: Plaintext API keys in source-controlled config files.

**Solution**: Use `DpapiEncryptor` + `SecureConfigService` from Step 2.

```csharp
// ❌ WRONG - Plaintext in config
{ "DifyApi": { "ApiKey": "app-xxxxxxxxxxxx" } }

// ✅ CORRECT - DPAPI encrypted
{ "DifyApi": { "ApiKeyEncrypted": "AQAAANCMnd8B..." } }
```

### 2. Blocking UI Thread During SSE Streaming

**Problem**: Using `.Result` or `.Wait()` on async SSE calls freezes the UI.

**Solution**: Use `await` with `IProgress<string>` for non-blocking updates.

```csharp
// ❌ WRONG
var result = difyService.RunWorkflowStreamingAsync(...).Result;

// ✅ CORRECT
var result = await difyService.RunWorkflowStreamingAsync(..., progress);
```

### 3. Ignoring CryptographicException on Load

**Problem**: DPAPI data encrypted by user A cannot be decrypted by user B.

**Solution**: Catch the exception and prompt the user to re-enter credentials.

### 4. Hardcoding BaseUrl Without Configuration

**Problem**: `https://api.dify.ai` embedded in source code; cannot change per environment.

**Solution**: Always read from `SecureConfigService`; let the settings dialog handle changes.

---

## Anti-Patterns

### Business Logic in Code-Behind

**What**: Writing save/load logic directly in `.xaml.cs` event handlers.

**Why It's Wrong**: Untestable without a running WPF window; violates MVVM separation.

**Better Approach**: Delegate all logic to ViewModel via `[RelayCommand]` and data binding.

### Single HttpClient with No Timeout

**What**: Creating `new HttpClient()` without setting `Timeout` for SSE calls.

**Why It's Wrong**: Default timeout (100s) kills long workflows; no timeout means infinite hang.

**Better Approach**: Set explicit timeout per operation type; consider `IHttpClientFactory` for pooling.

---

## Quick Reference

### Implementation Checklist

- [ ] Install NuGet: `CommunityToolkit.Mvvm`, `Microsoft.Extensions.DependencyInjection`
- [ ] Create `Infrastructure/Configuration/` with 4 files (Step 2)
- [ ] Create `Infrastructure/Difys/DifyApiService.cs` (Step 3)
- [ ] Create `Presentation/ViewModels/DifyConfigViewModel.cs` (Step 4)
- [ ] Create `Presentation/Views/DifyConfigDialog.xaml` + `.xaml.cs` (Step 4)
- [ ] Register services in `App.xaml.cs` (Step 5)
- [ ] Replace all `YourApp` / `YourAppName` placeholders (Step 6)
- [ ] Test: save config → reload → verify decryption
- [ ] Test: upload file → run workflow → check SSE progress

---

## Resources

- `local_docs/DifyAPI実装ガイド.md` — Full implementation reference (internal doc, not tracked in this repo)
- `local_docs/共通セキュリティコンポーネント.md` — DPAPI details (internal doc, not tracked in this repo)
- [CommunityToolkit.Mvvm Docs](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/)
- [Dify API Documentation](https://docs.dify.ai/)

---

## Changelog

### Version 1.0.0 (2026-02-15)
- Initial release: single-workflow Dify API integration guide
- 6-step workflow: Structure → Config → Client → UI → DI → Customize
- DPAPI encryption with CurrentUser scope
- SSE streaming with real-time progress reporting
- CommunityToolkit.Mvvm integration

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
