---
name: dotnet-extensions-configuration
description: >
  Implement strongly-typed configuration with validation using Microsoft.Extensions.Options.
  Bind appsettings.json to POCO classes, validate at startup with Data Annotations or
  IValidateOptions<T>, and choose correct IOptions lifetime for each scenario.
  Use when designing configuration classes that are testable, validated, and maintainable.
metadata:
  author: RyoMurakami1983
  tags: [configuration, options-pattern, dotnet, aspnetcore, validation, ioptions, strongly-typed]
  invocable: false
---

# Configuration Patterns

Implement strongly-typed configuration with validation using Microsoft.Extensions.Options. Bind `appsettings.json` to POCO classes, validate at startup with Data Annotations or `IValidateOptions<T>`, and choose the correct options lifetime (`IOptions<T>`, `IOptionsSnapshot<T>`, `IOptionsMonitor<T>`) for each scenario.

**Acronyms**: DI (Dependency Injection), POCO (Plain Old CLR Object).

## When to Use This Skill

- Binding configuration sections from appsettings.json to strongly-typed C# classes
- Validating configuration at application startup to fail fast on misconfiguration
- Implementing complex cross-property validation logic with IValidateOptions<T>
- Choosing between IOptions<T>, IOptionsSnapshot<T>, and IOptionsMonitor<T> lifetimes
- Designing configuration classes that are independently testable without ASP.NET hosting
- Replacing manual IConfiguration string-key access with type-safe Options pattern
- Adding environment-specific validation rules using injected IHostEnvironment

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-extensions-dependency-injection` | DI registration, service lifetimes, composable `Add*` methods |
| `dotnet-modern-csharp-coding-standards` | Record types, pattern matching, Result error handling |
| `dotnet-project-structure` | .NET solution layout, project references, layer separation |

## Core Principles

1. **Fail Fast at Startup** — Validate all configuration before the application serves requests. Why: runtime configuration failures are hard to debug and cause production incidents.
2. **Strongly-Typed over String Keys** — Bind configuration sections to POCO classes instead of accessing `IConfiguration["key"]`. Why: compile-time safety and IntelliSense catch typos before runtime.
3. **Validate Constraints, Not Just Presence** — Use cross-property and conditional validation to enforce business rules. Why: a non-null connection string can still be invalid.
4. **Choose Lifetime Intentionally** — Select `IOptions<T>` for static config, `IOptionsSnapshot<T>` for per-request reload, `IOptionsMonitor<T>` for background services. Why: wrong lifetime causes stale config or unnecessary overhead.
5. **Separate Validation from Settings** — Place validation logic in dedicated `IValidateOptions<T>` classes, not in constructors. Why: validators run at startup and are independently testable.

> **Values**: 基礎と型の追求（Options パターンという「型」を徹底し、どのプロジェクトでも再利用可能な設定基盤を作る）, 温故知新（.NET の設定バインディング原則を正しく理解し、IValidateOptions の進化した検証機能と組み合わせる）

## Workflow: Implement Validated Configuration

### Step 1: Define a Settings Class

Create a POCO class with a `SectionName` constant matching the `appsettings.json` key. Use default values for optional properties. Why: co-locating the section name with the class makes binding discoverable.

```csharp
public class SmtpSettings
{
    public const string SectionName = "Smtp";

    public string Host { get; set; } = string.Empty;
    public int Port { get; set; } = 587;
    public string? Username { get; set; }
    public string? Password { get; set; }
    public bool UseSsl { get; set; } = true;
}
```

> **Values**: 基礎と型の追求（命名規則と定数パターンの「型」が、設定バインディングの発見可能性を支える）

### Step 2: Bind and Register with Data Annotations

Use `BindConfiguration` to connect the POCO to a JSON section. Add `ValidateDataAnnotations()` for simple rules and always call `ValidateOnStart()`. Why: without `ValidateOnStart()`, validation only runs when options are first accessed — possibly hours into production.

```csharp
using System.ComponentModel.DataAnnotations;

public class SmtpSettings
{
    public const string SectionName = "Smtp";

    [Required(ErrorMessage = "SMTP host is required")]
    public string Host { get; set; } = string.Empty;

    [Range(1, 65535, ErrorMessage = "Port must be between 1 and 65535")]
    public int Port { get; set; } = 587;
}

// In Program.cs
builder.Services.AddOptions<SmtpSettings>()
    .BindConfiguration(SmtpSettings.SectionName)
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

> **Values**: 継続は力（`.ValidateOnStart()` という地道な一行をコツコツ守ることで、本番障害を未然に防ぐ）

### Step 3: Add Complex Validation with IValidateOptions

Implement `IValidateOptions<T>` for cross-property, conditional, or DI-dependent validation. Return `ValidateOptionsResult.Fail(failures)` instead of throwing exceptions. Why: returning failures preserves the validation chain and collects all errors at once.

```csharp
using Microsoft.Extensions.Options;

public class SmtpSettingsValidator : IValidateOptions<SmtpSettings>
{
    public ValidateOptionsResult Validate(string? name, SmtpSettings options)
    {
        var failures = new List<string>();

        if (string.IsNullOrWhiteSpace(options.Host))
        {
            failures.Add("Host is required");
        }

        if (options.Port is < 1 or > 65535)
        {
            failures.Add($"Port {options.Port} is invalid. Must be between 1 and 65535");
        }

        // Cross-property validation
        if (!string.IsNullOrEmpty(options.Username) && string.IsNullOrEmpty(options.Password))
        {
            failures.Add("Password is required when Username is specified");
        }

        // Conditional validation
        if (options.UseSsl && options.Port == 25)
        {
            failures.Add("Port 25 is typically not used with SSL. Consider port 465 or 587");
        }

        return failures.Count > 0
            ? ValidateOptionsResult.Fail(failures)
            : ValidateOptionsResult.Success;
    }
}
```

Register the validator after options binding:

```csharp
builder.Services.AddOptions<SmtpSettings>()
    .BindConfiguration(SmtpSettings.SectionName)
    .ValidateDataAnnotations()
    .ValidateOnStart();

// Register custom validator — runs after Data Annotations
builder.Services.AddSingleton<IValidateOptions<SmtpSettings>, SmtpSettingsValidator>();
```

> **Values**: 成長の複利（バリデーターを独立クラスに分離することで、テストと検証ロジックが同時に成長する構造を作る）

### Step 4: Choose the Correct Options Lifetime

Select the interface that matches how your service consumes configuration. Why: wrong lifetime causes stale data in long-running services or unnecessary overhead in singletons.

| Interface | Lifetime | Reloads on Change | Use Case |
|-----------|----------|-------------------|----------|
| `IOptions<T>` | Singleton | No | Static config, read once at startup |
| `IOptionsSnapshot<T>` | Scoped | Yes (per request) | Web apps needing fresh config per request |
| `IOptionsMonitor<T>` | Singleton | Yes (with callback) | Background services, real-time updates |

```csharp
// ✅ Singleton service — use IOptions<T>
public class EmailService
{
    private readonly SmtpSettings _settings;
    public EmailService(IOptions<SmtpSettings> options)
    {
        _settings = options.Value;
    }
}

// ✅ Background service — use IOptionsMonitor<T>
public class HealthChecker : BackgroundService
{
    private readonly IOptionsMonitor<HealthCheckSettings> _monitor;
    public HealthChecker(IOptionsMonitor<HealthCheckSettings> monitor)
    {
        _monitor = monitor;
        _monitor.OnChange(s => _logger.LogInformation("Settings reloaded"));
    }
}
```

> **Values**: ニュートラルな視点（ライフタイムの選択基準を明確にし、環境に依存しない判断基準を提供する）

### Step 5: Test Validators Independently

Instantiate validators directly in unit tests without ASP.NET hosting. Create settings objects with known values and assert on `ValidateOptionsResult`. Why: validators are plain classes — no DI container or HTTP pipeline needed.

```csharp
public class SmtpSettingsValidatorTests
{
    private readonly SmtpSettingsValidator _validator = new();

    [Fact]
    public void Validate_WithValidSettings_ReturnsSuccess()
    {
        var settings = new SmtpSettings
        {
            Host = "smtp.example.com", Port = 587,
            Username = "user@example.com", Password = "secret"
        };

        var result = _validator.Validate(null, settings);
        result.Succeeded.Should().BeTrue();
    }

    [Fact]
    public void Validate_WithUsernameButNoPassword_ReturnsFail()
    {
        var settings = new SmtpSettings
        {
            Host = "smtp.example.com",
            Username = "user@example.com", Password = null
        };

        var result = _validator.Validate(null, settings);
        result.Succeeded.Should().BeFalse();
        result.FailureMessage.Should().Contain("Password is required");
    }
}
```

> **Values**: 成長の複利（テスト可能な設計が、実装と品質を同時に成長させる）

## Good Practices

- ✅ Use `ValidateOnStart()` on every options registration to fail fast at startup
- ✅ Define `SectionName` as a `const string` inside the settings class for co-location
- ✅ Use Data Annotations for simple rules (Required, Range, EmailAddress)
- ✅ Use `IValidateOptions<T>` for cross-property and conditional validation logic
- ✅ Collect all failures in a `List<string>` instead of returning on first error
- ✅ Use `IOptionsMonitor<T>` in background services for live configuration reload
- ✅ Place validators near the settings class for discoverability
- ✅ Accept configuration section names as parameters for reusable extension methods

## Common Pitfalls

1. **Forgetting ValidateOnStart** — Without `.ValidateOnStart()`, validation only runs when options are first accessed, possibly hours into runtime. Fix: always chain `.ValidateOnStart()` after validation registration.
2. **Throwing in IValidateOptions** — Throwing exceptions inside `Validate()` breaks the validation chain and loses other errors. Fix: return `ValidateOptionsResult.Fail(message)` instead.
3. **Wrong Options Lifetime** — Using `IOptions<T>` in a background service misses configuration changes. Using `IOptionsSnapshot<T>` in a singleton causes scope errors. Fix: match the interface to service lifetime.
4. **Captive Configuration** — Injecting `IConfiguration` directly and accessing `config["Smtp:Host"]` bypasses all validation and type safety. Fix: use `IOptions<SmtpSettings>` instead.
5. **No Cross-Property Validation** — Data Annotations cannot validate relationships between properties (e.g., Username requires Password). Fix: implement `IValidateOptions<T>` for multi-field rules.

## Anti-Patterns

### ❌ Manual Configuration Access → ✅ Strongly-Typed Options

```csharp
// ❌ BAD: Bypasses validation, hard to test, no IntelliSense
public class MyService
{
    public MyService(IConfiguration configuration)
    {
        var host = configuration["Smtp:Host"]; // No validation, no type safety
    }
}

// ✅ GOOD: Strongly-typed, validated at startup
public class MyService
{
    public MyService(IOptions<SmtpSettings> options)
    {
        var host = options.Value.Host; // Validated, typed, discoverable
    }
}
```

### ❌ Constructor Validation → ✅ Startup Validation

```csharp
// ❌ BAD: Validation happens at runtime, not at startup
public class MyService
{
    public MyService(IOptions<Settings> options)
    {
        if (string.IsNullOrEmpty(options.Value.Required))
            throw new ArgumentException("Required is missing"); // Too late!
    }
}

// ✅ GOOD: Fails immediately at startup with clear error message
builder.Services.AddOptions<Settings>()
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

### ❌ Throwing in Validator → ✅ Returning Failure Result

```csharp
// ❌ BAD: Throws exception, breaks validation chain
public ValidateOptionsResult Validate(string? name, Settings options)
{
    if (options.Value < 0)
        throw new ArgumentException("Value cannot be negative");
    return ValidateOptionsResult.Success;
}

// ✅ GOOD: Returns failure, all validators run and errors are collected
public ValidateOptionsResult Validate(string? name, Settings options)
{
    if (options.Value < 0)
        return ValidateOptionsResult.Fail("Value cannot be negative");
    return ValidateOptionsResult.Success;
}
```

## Quick Reference

### Validation Strategy Decision Table

| Scenario | Strategy | Why |
|----------|----------|-----|
| Required field, range, format | Data Annotations (`[Required]`, `[Range]`) | Simple, declarative, built-in |
| Cross-property rules | `IValidateOptions<T>` | Access to full options object |
| Conditional logic (if X then Y) | `IValidateOptions<T>` | Programmatic control flow |
| Environment-specific rules | `IValidateOptions<T>` with DI | Inject `IHostEnvironment` |
| Multiple named instances | `IValidateOptions<T>` with `name` param | Name-specific validation |

### Options Lifetime Decision Table

| Service Type | Interface | Why |
|-------------|-----------|-----|
| Singleton service | `IOptions<T>` | Static config, read once |
| Scoped/request service | `IOptionsSnapshot<T>` | Fresh config per HTTP request |
| Background service | `IOptionsMonitor<T>` | Live reload with `OnChange` callback |
| Transient validator | `IOptions<T>` | Cheap, no reload needed |

### Registration Checklist

```csharp
builder.Services.AddOptions<MySettings>()
    .BindConfiguration(MySettings.SectionName)   // 1. Bind to JSON section
    .ValidateDataAnnotations()                    // 2. Attribute validation
    .ValidateOnStart();                           // 3. Fail fast at startup

// 4. Register complex validator (optional)
builder.Services.AddSingleton<IValidateOptions<MySettings>, MySettingsValidator>();
```

## Resources

- [Options Pattern in .NET](https://learn.microsoft.com/en-us/dotnet/core/extensions/options)
- [Configuration in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration)
- [IValidateOptions<T>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.options.ivalidateoptions-1)
- [references/detailed-patterns.md](references/detailed-patterns.md) — Named Options, Options Lifetime, Post-Configuration, Akka.NET production example, testing validators
