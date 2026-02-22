---
name: dotnet-wpf-secure-config
description: >
  Add DPAPI-encrypted config management to WPF apps with secure credential storage.
  Use when setting up encrypted configuration for WPF applications.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, wpf, csharp, security, dpapi, configuration]
  invocable: false
---

# Add Secure Configuration to WPF Applications

End-to-end workflow for adding Windows DPAPI-encrypted configuration management to .NET WPF applications: encrypted credential storage, JSON persistence to `%LOCALAPPDATA%`, extensible `AppConfigModel`, and DI registration.

## When to Use This Skill

Use this skill when:
- Adding secure credential storage (passwords, API keys, tokens) to a WPF application
- Setting up DPAPI-encrypted configuration before integrating Oracle, Dify, or other services
- Creating a reusable `SecureConfigService` that multiple integration skills can share
- Porting an existing `Infrastructure/Configuration/` layer to a new WPF project
- Replacing plaintext `appsettings.json` credentials with DPAPI encryption

**Prerequisite for**:
- `dotnet-oracle-wpf-integration` — Oracle DB connection with encrypted credentials
- `dotnet-wpf-dify-api-integration` — Dify API integration with encrypted API keys

---

## Related Skills

- **`dotnet-oracle-wpf-integration`** — Add Oracle DB connection using this security foundation
- **`dotnet-wpf-dify-api-integration`** — Add Dify API using this security foundation
- **`tdd-standard-practice`** — Test generated code with Red-Green-Refactor
- **`git-commit-practices`** — Commit each step as an atomic change

---

## Core Principles

1. **Security by Default** — DPAPI encryption for all secrets; never store plaintext credentials (ニュートラル)
2. **Reusable Foundation** — DpapiEncryptor and SecureConfigService work across any WPF project (成長の複利)
3. **Extensible Config** — AppConfigModel grows with new integrations without breaking existing ones (基礎と型)
4. **Layered Architecture** — Configuration lives in Infrastructure layer, consumed via interface (基礎と型)
5. **Single Source of Truth** — One `config.json` file manages all service credentials (継続は力)

---

## Workflow: Add Secure Configuration to WPF

### Step 1 — Set Up Configuration Structure

Use when initializing the folder structure and NuGet dependencies for secure configuration.

Create the `Infrastructure/Configuration/` folder and install required packages.

```
YourApp/
└── Infrastructure/
    └── Configuration/
        ├── DpapiEncryptor.cs         # DPAPI encrypt/decrypt utility
        ├── ISecureConfigService.cs   # Service interface
        ├── SecureConfigService.cs    # JSON persistence + encryption
        └── AppConfigModel.cs         # Extensible config root
```

```powershell
# Required for DPAPI (System.Security.Cryptography.ProtectedData)
Install-Package System.Security.Cryptography.ProtectedData
# Required for DI registration
Install-Package Microsoft.Extensions.DependencyInjection
```

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Implement DpapiEncryptor

Use when adding the Windows DPAPI encryption utility that all config models will share.

Create the static encryption helper with `Encrypt`, `Decrypt`, and `MaskSensitive` methods.

```text
// Infrastructure/Configuration/DpapiEncryptor.cs — Signature Overview
public static class DpapiEncryptor
{
    private static readonly byte[] Entropy = Encoding.UTF8.GetBytes("YourApp_Config_Salt_2026");

    public static string Encrypt(string plainText)      // DPAPI Protect → Base64
    public static string Decrypt(string encryptedText)   // Base64 → DPAPI Unprotect
    public static string MaskSensitive(string value)     // "abcd****" for logging
}
```

> See [references/detailed-patterns.md](references/detailed-patterns.md#dpapiencryptor--full-implementation) for full implementation with error handling.

**Why full error handling**: `CryptographicException` occurs when data was encrypted by user A but decrypted by user B (e.g., after profile migration). Without catching this, the app crashes on startup instead of prompting re-entry.

> **Values**: ニュートラル / 基礎と型

### Step 3 — Define Config Models

Use when defining the extensible configuration data structure.

Create `AppConfigModel` as the root, with domain-specific models as properties. Each integration skill adds its own model.

**AppConfigModel.cs** — Extensible root:

```csharp
namespace YourApp.Infrastructure.Configuration
{
    /// <summary>
    /// Application configuration root.
    /// Add new config models as properties when integrating new services.
    /// </summary>
    public class AppConfigModel
    {
        // ✅ Add properties here as you integrate new services
        // public OracleConfigModel OracleDb { get; set; } = new();  // Added by dotnet-oracle-wpf-integration
        // public DifyConfigModel DifyApi { get; set; } = new();     // Added by dotnet-wpf-dify-api-integration

        public string Version { get; set; } = "1.0";
    }
}
```

**Config model pattern** — Each service follows this template:

```csharp
/// <summary>
/// Template for domain-specific config models.
/// Replace "Service" with your integration name.
/// </summary>
public class ServiceConfigModel
{
    public string Endpoint { get; set; } = string.Empty;
    public string CredentialEncrypted { get; set; } = string.Empty;

    public string GetDecryptedCredential()
        => DpapiEncryptor.Decrypt(CredentialEncrypted);

    public void SetCredential(string plainCredential)
        => CredentialEncrypted = DpapiEncryptor.Encrypt(plainCredential);

    public bool IsValid()
        => !string.IsNullOrWhiteSpace(Endpoint)
        && !string.IsNullOrWhiteSpace(CredentialEncrypted);
}
```

**Why extensible root**: When Oracle and Dify are used together, `AppConfigModel` holds both:

```json
{
  "OracleDb": {
    "UserId": "SCOTT",
    "PasswordEncrypted": "AQAAANCMnd8B..."
  },
  "DifyApi": {
    "BaseUrl": "https://api.dify.ai",
    "ApiKeyEncrypted": "AQAAANCMnd8B..."
  },
  "Version": "1.0"
}
```

> **Values**: 成長の複利 / 基礎と型

### Step 4 — Build SecureConfigService

Use when implementing the JSON persistence service with DPAPI-encrypted credential support.

Create `ISecureConfigService` interface and `SecureConfigService` implementation. The service manages `AppConfigModel` as a whole and exposes typed load/save methods for each integration.

**ISecureConfigService.cs**:

```csharp
using System.Threading.Tasks;

namespace YourApp.Infrastructure.Configuration
{
    public interface ISecureConfigService
    {
        bool ConfigExists();
        Task ResetConfigAsync();

        // ✅ Add typed load/save methods per integration
        // Task<OracleConfigModel> LoadOracleConfigAsync();
        // Task SaveOracleConfigAsync(OracleConfigModel config);
        // Task<DifyConfigModel> LoadDifyConfigAsync();
        // Task SaveDifyConfigAsync(DifyConfigModel config);
    }
}
```

**SecureConfigService.cs**:

```text
// Infrastructure/Configuration/SecureConfigService.cs — Signature Overview
public class SecureConfigService : ISecureConfigService
{
    // ✅ Change "YourAppName" — see Step 6
    // Stores config at %LOCALAPPDATA%/YourAppName/config/config.json

    public bool ConfigExists()
    public Task ResetConfigAsync()

    // ✅ Add typed load/save methods per integration
    protected Task<AppConfigModel> LoadAppConfigAsync()
    protected Task SaveAppConfigAsync(AppConfigModel appConfig)
}
```

> See [references/detailed-patterns.md](references/detailed-patterns.md#secureconfigservice--full-implementation) for full implementation.

**Why `protected` for Load/SaveAppConfigAsync**: Integration skills (Oracle, Dify) add typed methods that call these internal helpers. Using `protected` allows subclassing if needed, while keeping the public API clean.

> **Values**: 基礎と型 / 継続は力

### Step 5 — Register DI Container

Use when wiring `SecureConfigService` into the WPF application's dependency injection.

Register `ISecureConfigService` as singleton in `App.xaml.cs`:

```csharp
// App.xaml.cs
using Microsoft.Extensions.DependencyInjection;

public partial class App : Application
{
    private ServiceProvider? _serviceProvider;

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        var services = new ServiceCollection();

        // ✅ Singleton — one config file, one service instance
        services.AddSingleton<ISecureConfigService, SecureConfigService>();

        // Integration skills add their services here:
        // services.AddSingleton<DifyApiService>();           // Dify integration
        // services.AddTransient<ISofRepository, SofDatabaseOracle>(); // Oracle integration

        _serviceProvider = services.BuildServiceProvider();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _serviceProvider?.Dispose();
        base.OnExit(e);
    }
}
```

**Why singleton**: All integrations share the same `config.json` file. Multiple instances risk concurrent write conflicts.

> **Values**: 成長の複利 / 基礎と型

### Step 6 — Customize for Your App

Use when preparing the generated code for production deployment.

Replace these placeholders before shipping:

| Item | File | What to Change | Impact if Skipped |
|------|------|----------------|-------------------|
| App name | `SecureConfigService.cs` | `"YourAppName"` → actual app name | Config saved to wrong folder |
| Salt | `DpapiEncryptor.cs` | `Entropy` byte array value | Shared salt weakens isolation |
| Namespace | All `.cs` files | `YourApp` → actual namespace | Build errors |

**Customization checklist**:

```powershell
# Verify all placeholders are replaced
Select-String -Path "Infrastructure/Configuration/*.cs" -Pattern "YourApp" -SimpleMatch
# Expected: 0 matches after customization
```

⚠️ **Critical**: Changing the `Entropy` value after data has been encrypted makes all existing encrypted data unrecoverable. Set it once before first use.

> **Values**: ニュートラル / 基礎と型

---

## Common Pitfalls

### 1. Changing Entropy After Encryption

**Problem**: Updating the salt value in `DpapiEncryptor` after credentials are already saved.

**Solution**: Set the entropy value once before first deployment. If you must change it, implement a migration that decrypts with the old salt and re-encrypts with the new one.

### 2. Using LocalMachine Scope Instead of CurrentUser

**Problem**: `DataProtectionScope.LocalMachine` allows any user on the same PC to decrypt.

**Solution**: Always use `DataProtectionScope.CurrentUser` for per-user credential isolation.

```csharp
// ❌ WRONG — Any user on this PC can decrypt
ProtectedData.Protect(data, entropy, DataProtectionScope.LocalMachine);

// ✅ CORRECT — Only the encrypting user can decrypt
ProtectedData.Protect(data, entropy, DataProtectionScope.CurrentUser);
```

### 3. Logging Decrypted Secrets

**Problem**: Writing plaintext passwords or API keys to log files.

**Solution**: Always use `DpapiEncryptor.MaskSensitive()` for log output.

```csharp
// ❌ WRONG — Secret leaked to log
logger.LogInformation($"Password: {password}");

// ✅ CORRECT — Masked output
logger.LogInformation($"Password: {DpapiEncryptor.MaskSensitive(password)}");
// Output: "Password: abcd****"
```

### 4. Swallowing CryptographicException

**Problem**: Catching decryption errors silently and returning empty strings.

**Solution**: Surface the error to the user so they can re-enter credentials.

---

## Anti-Patterns

### Storing Credentials in appsettings.json

**What**: Putting passwords or API keys in plaintext configuration files.

**Why It's Wrong**: Source-controlled files are readable by anyone with repo access; deployment artifacts are often not encrypted.

**Better Approach**: Use `DpapiEncryptor` + `SecureConfigService` to store encrypted values in `%LOCALAPPDATA%`.

### Multiple Config Files per Service

**What**: Creating separate `oracle-config.json`, `dify-config.json` files for each integration.

**Why It's Wrong**: Duplicates file I/O logic, creates race conditions, makes backup/reset harder.

**Better Approach**: Single `AppConfigModel` with typed properties per service, persisted to one `config.json`.

### Hardcoding Credentials in Source Code

**What**: Embedding connection strings or API keys directly in C# code.

**Why It's Wrong**: Credentials end up in version control history even after removal.

**Better Approach**: Always read from `ISecureConfigService` at runtime.

---

## Quick Reference

### Migration Checklist (Porting to New App)

- [ ] Copy `Infrastructure/Configuration/` folder (4 files)
- [ ] Change namespace from source app to target app
- [ ] Change app name in `SecureConfigService` constructor (`"YourAppName"`)
- [ ] Change entropy value in `DpapiEncryptor` (set unique salt per app)
- [ ] Add config model properties to `AppConfigModel` for your integrations
- [ ] Add typed load/save methods to `ISecureConfigService` and `SecureConfigService`
- [ ] Register `ISecureConfigService` in DI container
- [ ] Test: encrypt → save → reload → decrypt cycle

### Security Checklist

- [ ] All passwords and API keys use `DpapiEncryptor.Encrypt()` before storage
- [ ] Log output uses `MaskSensitive()` for any credential values
- [ ] Error messages do not contain decrypted secrets
- [ ] `DataProtectionScope.CurrentUser` is used (not `LocalMachine`)
- [ ] Entropy value is unique per application
- [ ] Config file stored in `%LOCALAPPDATA%` (user-isolated by Windows)

### What to Encrypt — Decision Table

| Data Type | Encrypt? | Reason |
|-----------|----------|--------|
| Passwords | ✅ Always | Authentication credential |
| API keys | ✅ Always | Service access token |
| Tokens / secrets | ✅ Always | Bearer credentials |
| URLs / endpoints | ❌ No | Public information |
| User IDs / names | ⚠️ Policy-dependent | May be PII |
| Timeout values | ❌ No | Non-sensitive setting |

### DPAPI Security Properties

| Property | Value |
|----------|-------|
| Encryption scope | Per-user (CurrentUser) |
| Key management | Automatic (Windows manages keys) |
| Portable? | ❌ Cannot decrypt on different PC or user |
| Cloud sync? | ❌ Not suitable (different machine keys) |
| Backup strategy | Re-enter credentials after restore |

---

## Resources

- Shared Security Components — Full implementation reference (internal documentation maintained outside this repository)
- [Microsoft: Data Protection API (DPAPI)](https://docs.microsoft.com/windows/win32/seccng/data-protection-api)
