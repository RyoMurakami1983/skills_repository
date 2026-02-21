---
name: dotnet-extensions-configuration
description: >
  Microsoft.Extensions.Options を使った厳密な型付き設定とバリデーションの実装。
  appsettings.json を POCO クラスにバインドし、Data Annotations または IValidateOptions<T> で
  起動時に検証し、シナリオに応じた IOptions ライフタイムを選択する。
  Use when テスト可能で検証済みの保守しやすい設定クラスを設計する場合。
metadata:
  author: RyoMurakami1983
  tags: [configuration, options-pattern, dotnet, aspnetcore, validation, ioptions, strongly-typed]
  invocable: false
---

<!-- このドキュメントは dotnet-extensions-configuration の日本語版です。英語版: ../SKILL.md -->

# Configuration Patterns

Microsoft.Extensions.Options を使って厳密な型付き設定を検証付きで実装する。`appsettings.json` を POCO クラスにバインドし、Data Annotations または `IValidateOptions<T>` で起動時に検証し、シナリオごとに適切なオプションライフタイム（`IOptions<T>`、`IOptionsSnapshot<T>`、`IOptionsMonitor<T>`）を選択する。

**略語**: DI（Dependency Injection、依存性注入）、POCO（Plain Old CLR Object）。

## When to Use This Skill

- appsettings.json の設定セクションを厳密な型付き C# クラスにバインドする
- アプリケーション起動時に設定を検証し、設定ミスで即座に失敗させる（フェイルファスト）
- IValidateOptions<T> を使った複雑なクロスプロパティ検証ロジックを実装する
- IOptions<T>、IOptionsSnapshot<T>、IOptionsMonitor<T> のライフタイムを選択する
- ASP.NET ホスティングなしで独立してテスト可能な設定クラスを設計する
- 手動の IConfiguration 文字列キーアクセスを型安全な Options パターンに置き換える
- 注入された IHostEnvironment を使った環境固有の検証ルールを追加する

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-extensions-dependency-injection` | DI 登録、サービスライフタイム、コンポーザブルな `Add*` メソッド |
| `dotnet-modern-csharp-coding-standards` | Record 型、パターンマッチング、Result エラーハンドリング |
| `dotnet-project-structure` | .NET ソリューションレイアウト、プロジェクト参照、レイヤー分離 |

## Core Principles

1. **Fail Fast at Startup** — アプリケーションがリクエストを処理する前にすべての設定を検証する。理由：実行時の設定障害はデバッグが難しく、本番インシデントを引き起こす。
2. **Strongly-Typed over String Keys** — `IConfiguration["key"]` でアクセスする代わりに、設定セクションを POCO クラスにバインドする。理由：コンパイル時の安全性と IntelliSense がタイポを実行前にキャッチする。
3. **Validate Constraints, Not Just Presence** — クロスプロパティおよび条件付き検証でビジネスルールを強制する。理由：null でない接続文字列でも無効な場合がある。
4. **Choose Lifetime Intentionally** — 静的設定には `IOptions<T>`、リクエストごとのリロードには `IOptionsSnapshot<T>`、バックグラウンドサービスには `IOptionsMonitor<T>` を選択する。理由：間違ったライフタイムは古い設定や不要なオーバーヘッドを引き起こす。
5. **Separate Validation from Settings** — 検証ロジックをコンストラクタではなく専用の `IValidateOptions<T>` クラスに配置する。理由：バリデーターは起動時に実行され、独立してテスト可能。

> **Values**: 基礎と型の追求（Options パターンという「型」を徹底し、どのプロジェクトでも再利用可能な設定基盤を作る）, 温故知新（.NET の設定バインディング原則を正しく理解し、IValidateOptions の進化した検証機能と組み合わせる）

## Workflow: Implement Validated Configuration

### Step 1: Define a Settings Class

`appsettings.json` のキーに一致する `SectionName` 定数を持つ POCO クラスを作成する。オプションプロパティにはデフォルト値を使う。理由：セクション名をクラスと共存させることでバインディングが発見しやすくなる。

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

`BindConfiguration` を使って POCO を JSON セクションに接続する。単純なルールには `ValidateDataAnnotations()` を追加し、常に `ValidateOnStart()` を呼ぶ。理由：`ValidateOnStart()` がないと、検証はオプションが最初にアクセスされた時にのみ実行される — 本番環境で数時間後かもしれない。

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

// Program.cs にて
builder.Services.AddOptions<SmtpSettings>()
    .BindConfiguration(SmtpSettings.SectionName)
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

> **Values**: 継続は力（`.ValidateOnStart()` という地道な一行をコツコツ守ることで、本番障害を未然に防ぐ）

### Step 3: Add Complex Validation with IValidateOptions

クロスプロパティ、条件付き、またはDI依存の検証には `IValidateOptions<T>` を実装する。例外をスローする代わりに `ValidateOptionsResult.Fail(failures)` を返す。理由：失敗を返すことで検証チェーンが保持され、すべてのエラーが一度に収集される。

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

        // クロスプロパティ検証
        if (!string.IsNullOrEmpty(options.Username) && string.IsNullOrEmpty(options.Password))
        {
            failures.Add("Password is required when Username is specified");
        }

        // 条件付き検証
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

オプションバインディングの後にバリデーターを登録する：

```csharp
builder.Services.AddOptions<SmtpSettings>()
    .BindConfiguration(SmtpSettings.SectionName)
    .ValidateDataAnnotations()
    .ValidateOnStart();

// カスタムバリデーター登録 — Data Annotations の後に実行される
builder.Services.AddSingleton<IValidateOptions<SmtpSettings>, SmtpSettingsValidator>();
```

> **Values**: 成長の複利（バリデーターを独立クラスに分離することで、テストと検証ロジックが同時に成長する構造を作る）

### Step 4: Choose the Correct Options Lifetime

サービスが設定を消費する方法に一致するインターフェースを選択する。理由：間違ったライフタイムは長時間実行サービスで古いデータを引き起こすか、シングルトンで不要なオーバーヘッドを生む。

| インターフェース | ライフタイム | 変更時リロード | 用途 |
|----------------|------------|---------------|------|
| `IOptions<T>` | Singleton | なし | 静的設定、起動時に1回読み取り |
| `IOptionsSnapshot<T>` | Scoped | あり（リクエスト毎） | リクエスト毎に最新設定が必要な Web アプリ |
| `IOptionsMonitor<T>` | Singleton | あり（コールバック） | バックグラウンドサービス、リアルタイム更新 |

```csharp
// ✅ シングルトンサービス — IOptions<T> を使用
public class EmailService
{
    private readonly SmtpSettings _settings;
    public EmailService(IOptions<SmtpSettings> options)
    {
        _settings = options.Value;
    }
}

// ✅ バックグラウンドサービス — IOptionsMonitor<T> を使用
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

ASP.NET ホスティングなしでユニットテストでバリデーターを直接インスタンス化する。既知の値で設定オブジェクトを作成し、`ValidateOptionsResult` をアサートする。理由：バリデーターは単純なクラス — DI コンテナも HTTP パイプラインも不要。

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

- ✅ すべてのオプション登録に `ValidateOnStart()` を使い、起動時にフェイルファストする
- ✅ 設定クラス内に `SectionName` を `const string` として定義し共存配置する
- ✅ 単純なルールには Data Annotations（Required, Range, EmailAddress）を使う
- ✅ クロスプロパティおよび条件付き検証ロジックには `IValidateOptions<T>` を使う
- ✅ 最初のエラーで返すのではなく、すべての失敗を `List<string>` に収集する
- ✅ バックグラウンドサービスではライブ設定リロードのために `IOptionsMonitor<T>` を使う
- ✅ バリデーターを設定クラスの近くに配置し発見可能性を高める
- ✅ 再利用可能な拡張メソッドのために設定セクション名をパラメータとして受け取る

## Common Pitfalls

1. **ValidateOnStart の忘れ** — `.ValidateOnStart()` がないと、検証はオプションが最初にアクセスされた時にのみ実行される（実行時に数時間後の可能性）。修正：検証登録後に常に `.ValidateOnStart()` をチェーンする。
2. **IValidateOptions での例外スロー** — `Validate()` 内で例外をスローすると検証チェーンが壊れ、他のエラーが失われる。修正：代わりに `ValidateOptionsResult.Fail(message)` を返す。
3. **間違った Options ライフタイム** — バックグラウンドサービスで `IOptions<T>` を使うと設定変更を見逃す。シングルトンで `IOptionsSnapshot<T>` を使うとスコープエラーになる。修正：インターフェースをサービスライフタイムに合わせる。
4. **キャプティブ設定** — `IConfiguration` を直接注入し `config["Smtp:Host"]` でアクセスすると、すべての検証と型安全性をバイパスする。修正：代わりに `IOptions<SmtpSettings>` を使う。
5. **クロスプロパティ検証なし** — Data Annotations はプロパティ間の関係（例：Username に Password が必要）を検証できない。修正：複数フィールドルールには `IValidateOptions<T>` を実装する。

## Anti-Patterns

### ❌ Manual Configuration Access → ✅ Strongly-Typed Options

```csharp
// ❌ BAD: 検証をバイパス、テスト困難、IntelliSense なし
public class MyService
{
    public MyService(IConfiguration configuration)
    {
        var host = configuration["Smtp:Host"]; // 検証なし、型安全性なし
    }
}

// ✅ GOOD: 厳密な型付き、起動時に検証済み
public class MyService
{
    public MyService(IOptions<SmtpSettings> options)
    {
        var host = options.Value.Host; // 検証済み、型付き、発見可能
    }
}
```

### ❌ Constructor Validation → ✅ Startup Validation

```csharp
// ❌ BAD: 検証が起動時ではなく実行時に発生
public class MyService
{
    public MyService(IOptions<Settings> options)
    {
        if (string.IsNullOrEmpty(options.Value.Required))
            throw new ArgumentException("Required is missing"); // 遅すぎる！
    }
}

// ✅ GOOD: 起動時に明確なエラーメッセージで即座に失敗
builder.Services.AddOptions<Settings>()
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

### ❌ Throwing in Validator → ✅ Returning Failure Result

```csharp
// ❌ BAD: 例外スロー、検証チェーンが壊れる
public ValidateOptionsResult Validate(string? name, Settings options)
{
    if (options.Value < 0)
        throw new ArgumentException("Value cannot be negative");
    return ValidateOptionsResult.Success;
}

// ✅ GOOD: 失敗を返し、全バリデーターが実行されエラーが収集される
public ValidateOptionsResult Validate(string? name, Settings options)
{
    if (options.Value < 0)
        return ValidateOptionsResult.Fail("Value cannot be negative");
    return ValidateOptionsResult.Success;
}
```

## Quick Reference

### Validation Strategy Decision Table

| シナリオ | 戦略 | 理由 |
|---------|------|------|
| 必須フィールド、範囲、形式 | Data Annotations（`[Required]`、`[Range]`） | シンプル、宣言的、組み込み |
| クロスプロパティルール | `IValidateOptions<T>` | 完全なオプションオブジェクトにアクセス可能 |
| 条件付きロジック（X なら Y） | `IValidateOptions<T>` | プログラム的な制御フロー |
| 環境固有のルール | `IValidateOptions<T>` + DI | `IHostEnvironment` を注入 |
| 複数の名前付きインスタンス | `IValidateOptions<T>` + `name` パラメータ | 名前固有の検証 |

### Options Lifetime Decision Table

| サービスタイプ | インターフェース | 理由 |
|--------------|----------------|------|
| シングルトンサービス | `IOptions<T>` | 静的設定、1回読み取り |
| スコープ/リクエストサービス | `IOptionsSnapshot<T>` | HTTP リクエスト毎に最新設定 |
| バックグラウンドサービス | `IOptionsMonitor<T>` | `OnChange` コールバックでライブリロード |
| トランジェントバリデーター | `IOptions<T>` | 安価、リロード不要 |

### Registration Checklist

```csharp
builder.Services.AddOptions<MySettings>()
    .BindConfiguration(MySettings.SectionName)   // 1. JSON セクションにバインド
    .ValidateDataAnnotations()                    // 2. 属性検証
    .ValidateOnStart();                           // 3. 起動時フェイルファスト

// 4. 複雑なバリデーター登録（オプション）
builder.Services.AddSingleton<IValidateOptions<MySettings>, MySettingsValidator>();
```

## Resources

- [Options Pattern in .NET](https://learn.microsoft.com/en-us/dotnet/core/extensions/options)
- [Configuration in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration)
- [IValidateOptions<T>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.options.ivalidateoptions-1)
- [references/detailed-patterns.md](references/detailed-patterns.md) — Named Options、Options Lifetime、Post-Configuration、Akka.NET 本番例、テストバリデーター
