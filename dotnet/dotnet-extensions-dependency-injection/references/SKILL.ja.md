---
name: dotnet-extensions-dependency-injection
description: >
  IServiceCollection 拡張メソッドを使って DI 登録を整理する。
  関連サービスをコンポーザブルな Add* メソッドにグループ化し、
  Program.cs のクリーンさ、テストでの構成再利用、適切なライフタイム管理を実現する。
  Use when ASP.NET Core や .NET アプリケーションで依存性注入を構造化する場合。
metadata:
  author: RyoMurakami1983
  tags: [dependency-injection, di, dotnet, aspnetcore, iservicecollection, testing]
  invocable: false
---

<!-- このドキュメントは dotnet-extensions-dependency-injection の日本語版です。英語版: ../SKILL.md -->

# Dependency Injection Patterns

Microsoft.Extensions.DependencyInjection（DI）の登録をコンポーザブルな `IServiceCollection` 拡張メソッドに整理する。巨大な `Program.cs` を排除し、テストでのサービス再利用を可能にし、正しいライフタイム管理を徹底する。

**略語**: DI（Dependency Injection、依存性注入）、DML（Data Manipulation Language）。

## When to Use This Skill

- ASP.NET Core アプリケーションでサービス登録を整理し、肥大化した Program.cs を避ける
- 関連サービスをまとめるコンポーザブルな `Add*` 拡張メソッドを設計する
- プロダクション環境と統合テストプロジェクト間でサービス構成を再利用可能にする
- 状態とスレッドセーフ性に基づいて正しいサービスライフタイム（Singleton, Scoped, Transient）を選択する
- Scoped サービスが Singleton やバックグラウンドサービスに注入されるスコープ関連バグを修正する
- 複雑な初期化ロジックに `IServiceProvider` を使ったファクトリベース登録を実装する
- 環境（開発 vs 本番）によって異なる条件付きサービス登録を作成する

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-project-structure` | .NET ソリューションレイアウト、プロジェクト参照、レイヤー分離 |
| `dotnet-modern-csharp-coding-standards` | Record 型、パターンマッチング、Result エラーハンドリング |
| `dotnet-efcore-patterns` | EF Core DbContext ライフタイム、NoTracking、マイグレーション管理 |

## Core Principles

1. **Compose via Extension Methods** — 関連する登録を `Add{Feature}Services()` メソッドにグループ化する。理由：Program.cs をクリーンに保ち、再利用を可能にする。
2. **Return for Chaining** — すべての拡張メソッドは `IServiceCollection` を返してフルーエントな合成をサポートする。理由：パイプラインとして読める一貫した API。
3. **Correct Lifetime by Default** — Singleton は状態なし/スレッドセーフ、Scoped はリクエスト単位の状態、Transient は軽量/安価。理由：間違ったライフタイムは古いデータやメモリリークの原因。
4. **Explicit Configuration** — 接続文字列やシークレットをハードコードせず、パラメータとして受け取る。理由：隠れた設定はデプロイ障害の原因。
5. **Scope Per Unit of Work** — バックグラウンドサービスやアクターでは、作業単位ごとにスコープを作成する。理由：Scoped サービスは HTTP リクエストパイプライン外では明示的なスコープが必要。

> **Values**: 基礎と型の追求（`Add*` メソッドという「型」を徹底することで、どのプロジェクトでも再利用可能な DI 構造の基盤を作る）, 成長の複利（テストでの再利用を設計に組み込み、実装と品質が同時に成長する構造を作る）

## Workflow: Organize DI Registrations

### Step 1: Create Feature Extension Methods

関連サービスを単一の `Add{Feature}Services()` 拡張メソッドにグループ化し、登録するサービスの近くに配置する。理由：共存配置が登録を発見しやすくする。

```csharp
namespace MyApp.Users;

public static class UserServiceCollectionExtensions
{
    public static IServiceCollection AddUserServices(this IServiceCollection services)
    {
        // リポジトリ
        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IUserReadStore, UserReadStore>();

        // サービス
        services.AddScoped<IUserService, UserService>();
        services.AddScoped<IUserValidationService, UserValidationService>();

        // チェーン用に返す
        return services;
    }
}
```

**ファイル配置規則**: `{Feature}ServiceCollectionExtensions.cs` を機能のサービスの隣に配置。

```
src/
  MyApp.Api/
    Program.cs                                  # すべての Add* メソッドを合成
  MyApp.Users/
    Services/
      UserService.cs
    UserServiceCollectionExtensions.cs          # AddUserServices()
  MyApp.Email/
    EmailServiceCollectionExtensions.cs         # AddEmailServices()
```

> **Values**: 基礎と型の追求（命名規則とファイル配置の「型」が、チーム全体の発見可能性を支える）

### Step 2: Add Configuration Binding

`IOptions<T>` と `BindConfiguration` を使って機能固有の設定を行う。設定セクション名をパラメータとして受け取り、柔軟性を確保する。理由：明示的な設定がデプロイ障害を防ぐ。

```csharp
namespace MyApp.Email;

public static class EmailServiceCollectionExtensions
{
    public static IServiceCollection AddEmailServices(
        this IServiceCollection services,
        string configSectionName = "EmailSettings")
    {
        // 設定のバインドと検証
        services.AddOptions<EmailOptions>()
            .BindConfiguration(configSectionName)
            .ValidateDataAnnotations()
            .ValidateOnStart();

        // サービス登録
        services.AddSingleton<IMjmlTemplateRenderer, MjmlTemplateRenderer>();
        services.AddScoped<IUserEmailComposer, UserEmailComposer>();
        services.AddScoped<IEmailSender, SmtpEmailSender>();

        return services;
    }
}
```

> **Values**: ニュートラルな視点（設定を外部パラメータ化し、環境に依存しない普遍的な設計を保つ）

### Step 3: Choose Correct Lifetimes

状態とスレッドセーフ性に基づいてライフタイムを選択する。理由：間違ったライフタイムは最も一般的な DI バグの原因 — 古い DbContext、キャプティブ依存関係、メモリリーク。

| ライフタイム | 使用条件 | 例 |
|-------------|----------|-----|
| **Singleton** | 状態なし、スレッドセーフ、生成コスト高 | 設定、HttpClient ファクトリ、キャッシュ |
| **Scoped** | リクエスト単位の状態、DB コンテキスト | DbContext、リポジトリ、ユーザーコンテキスト |
| **Transient** | 軽量、状態あり、生成コスト低 | バリデーター、短命ヘルパー |

```csharp
// SINGLETON: 状態なしサービス、安全に共有
services.AddSingleton<IMjmlTemplateRenderer, MjmlTemplateRenderer>();
services.AddSingleton<IEmailLinkGenerator, EmailLinkGenerator>();

// SCOPED: データベースアクセス、リクエスト単位の状態
services.AddScoped<IUserRepository, UserRepository>();
services.AddScoped<IOrderService, OrderService>();

// TRANSIENT: 安価、短命
services.AddTransient<CreateUserRequestValidator>();
```

> **Values**: 温故知新（DI コンテナの基本原則を正しく理解し、.NET の進化した機能と組み合わせる）

### Step 4: Compose in Program.cs

すべての `Add*` 呼び出しを `Program.cs` でチェーンし、クリーンでスキャンしやすいエントリーポイントにする。理由：トップレベルの合成がアプリの依存構造を一目で明らかにする。

```csharp
// ✅ GOOD: クリーンでコンポーザブルな Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddUserServices()
    .AddOrderServices()
    .AddEmailServices()
    .AddPaymentServices()
    .AddValidators();

var app = builder.Build();
```

> **Values**: 余白の設計（Program.cs を最小限に保つことで、構造の見通しという余白を確保する）

### Step 5: Handle Scopes in Background Services

バックグラウンドサービスでは、作業単位ごとにスコープを作成する。理由：Scoped サービス（DbContext、リポジトリ）は ASP.NET Core のリクエスト単位パイプライン外では明示的なスコープが必要。

```csharp
// ✅ GOOD: 作業単位ごとにスコープを作成
public class OrderProcessingService : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;

    public OrderProcessingService(IServiceScopeFactory scopeFactory)
    {
        _scopeFactory = scopeFactory;
    }

    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            using var scope = _scopeFactory.CreateScope();
            var orderService = scope.ServiceProvider
                .GetRequiredService<IOrderService>();

            await orderService.ProcessPendingOrdersAsync(ct);
            await Task.Delay(TimeSpan.FromMinutes(1), ct);
        }
    }
}
```

> **Values**: 継続は力（スコープ管理という地道な「型」をコツコツ守ることで、本番環境の安定性を積み上げる）

### Step 6: Reuse Extensions in Tests

テストセットアップで `Add*` メソッドを使ってプロダクション構成を再利用する。外部依存のみをテストダブルで上書きする。理由：テストの信頼性は実際の登録を実行することから生まれる。

```csharp
public class ApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public ApiTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // プロダクションサービスは Add* メソッドで既に登録済み
                // テスト用に外部依存のみを上書き
                services.RemoveAll<IEmailSender>();
                services.AddSingleton<IEmailSender, TestEmailSender>();

                services.RemoveAll<IPaymentProcessor>();
                services.AddSingleton<IPaymentProcessor, FakePaymentProcessor>();
            });
        });
    }

    [Fact]
    public async Task CreateOrder_SendsConfirmationEmail()
    {
        var client = _factory.CreateClient();
        var emailSender = _factory.Services
            .GetRequiredService<IEmailSender>() as TestEmailSender;

        await client.PostAsJsonAsync("/api/orders", new CreateOrderRequest(...));

        Assert.Single(emailSender!.SentEmails);
    }
}
```

> **Values**: 成長の複利（テストでプロダクションコードを再利用する設計が、実装と品質を同時に成長させる）

## Good Practices

- ✅ 関連サービスを `Add{Feature}Services()` メソッドにグループ化して明確な境界を作る
- ✅ 拡張メソッドを登録するサービスの近くに配置して発見可能性を高める
- ✅ すべての拡張メソッドから `IServiceCollection` を返してフルーエントチェーンを可能にする
- ✅ 値をハードコードせず、設定パラメータを明示的に受け取る
- ✅ 一貫した命名を使う：機能は `Add{Feature}Services()`、オプションは `Configure{Feature}()`
- ✅ バックグラウンドサービスでは `IServiceScopeFactory` を使って作業単位ごとにスコープを作成する
- ✅ テストセットアップでプロダクションの `Add*` メソッドを再利用して現実的な構成にする
- ✅ `IOptions<T>` で `ValidateOnStart()` を使い、起動時に設定エラーを検出する
- ✅ `IHostEnvironment` を使って環境固有のサービスを条件付き登録する
- ✅ すべての非同期サービスメソッドで `CancellationToken` を受け取る

## Common Pitfalls

1. **Captive Dependency（キャプティブ依存関係）** — Scoped サービスを Singleton に注入すると、古いインスタンスが永久にキャプチャされる。修正：`IServiceProvider` または `IServiceScopeFactory` を注入し、手動でスコープを作成する。
2. **No Scope in Background Work（バックグラウンドワークでスコープなし）** — `BackgroundService` に Scoped サービスを直接注入するとスローまたは古いデータを返す。修正：イテレーションごとに `IServiceScopeFactory.CreateScope()` を使用する。
3. **Hidden Configuration（隠れた設定）** — 拡張メソッド内に接続文字列やシークレットをハードコードする。修正：メソッドパラメータまたは `IOptions<T>` で設定値を受け取る。
4. **Overly Generic Extensions（汎用的すぎる拡張）** — 50個の無関係なものを登録する `AddServices()` を作成する。修正：機能固有の `Add{Feature}Services()` メソッドに分割する。
5. **Missing Return Statement（return 文の欠落）** — 拡張メソッドから `IServiceCollection` を返し忘れる。修正：チェーン用に常に `return services;` で終わる。

## Anti-Patterns

### ❌ Massive Program.cs → ✅ Composable Extensions

```csharp
// ❌ BAD: 200行以上の整理されていない登録
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IOrderRepository, OrderRepository>();
// ... 150行以上の混在した登録 ...

// ✅ GOOD: 明確な構造でクリーンな合成
builder.Services
    .AddUserServices()
    .AddOrderServices()
    .AddEmailServices();
```

### ❌ Scoped into Singleton → ✅ Scope Factory

```csharp
// ❌ BAD: Singleton が Scoped サービスをキャプチャ — 古い DbContext！
public class CacheService  // Singleton として登録
{
    private readonly IUserRepository _repo;  // Scoped — 起動時にキャプチャ！
    public CacheService(IUserRepository repo) { _repo = repo; }
}

// ✅ GOOD: 必要時にスコープを作成
public class CacheService
{
    private readonly IServiceScopeFactory _scopeFactory;
    public CacheService(IServiceScopeFactory scopeFactory) { _scopeFactory = scopeFactory; }

    public async Task<User> GetUserAsync(string id)
    {
        using var scope = _scopeFactory.CreateScope();
        var repo = scope.ServiceProvider.GetRequiredService<IUserRepository>();
        return await repo.GetByIdAsync(id);
    }
}
```

### ❌ Hidden Connection String → ✅ Explicit Parameter

```csharp
// ❌ BAD: 拡張内に隠された重要な設定
public static IServiceCollection AddDatabase(this IServiceCollection services)
{
    services.AddDbContext<AppDbContext>(options =>
        options.UseSqlServer("hardcoded-connection-string"));
}

// ✅ GOOD: 設定を明示的に受け取る
public static IServiceCollection AddDatabase(
    this IServiceCollection services, string connectionString)
{
    services.AddDbContext<AppDbContext>(options =>
        options.UseSqlServer(connectionString));
    return services;
}
```

## Quick Reference

### Naming Convention Guide

| パターン | 用途 | 例 |
|---------|------|-----|
| `Add{Feature}Services()` | 一般的な機能登録 | `AddUserServices()` |
| `Add{Feature}()` | 曖昧さがない場合の短縮形 | `AddStripePayments()` |
| `Configure{Feature}()` | 主にオプション設定 | `ConfigureAuthentication()` |
| `Use{Feature}()` | IApplicationBuilder 上のミドルウェア | `UseAuthentication()` |

### Lifetime Decision Table

| サービス特性 | ライフタイム | 理由 |
|-------------|------------|------|
| 状態なし、スレッドセーフ、初期化コスト高 | Singleton | 1インスタンスを安全に共有 |
| リクエスト単位の状態（DbContext、リポジトリ） | Scoped | HTTP リクエストごとにフレッシュな状態 |
| 軽量、生成コスト低 | Transient | 共有状態不要 |
| 長寿命ホスト（BackgroundService） | `IServiceScopeFactory` を注入 | 作業単位ごとにスコープ作成 |
| Scoped 依存のあるアクター | `IServiceProvider` を注入 | メッセージごとにスコープ作成 |

### Conditional Registration Pattern

```csharp
public static IServiceCollection AddEmailServices(
    this IServiceCollection services, IHostEnvironment environment)
{
    services.AddSingleton<IEmailComposer, MjmlEmailComposer>();

    if (environment.IsDevelopment())
        services.AddSingleton<IEmailSender, MailpitEmailSender>();
    else
        services.AddSingleton<IEmailSender, SmtpEmailSender>();

    return services;
}
```

## Resources

- [Microsoft.Extensions.DependencyInjection](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection)
- [Service Lifetimes](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection#service-lifetimes)
- [Options Pattern](https://learn.microsoft.com/en-us/dotnet/core/extensions/options)
- [references/detailed-patterns.md](references/detailed-patterns.md) — 階層的合成、Akka.Hosting 統合、キー付きサービス、アクタースコープ管理
