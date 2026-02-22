---
name: dotnet-extensions-dependency-injection
description: >
  Organize DI registrations using IServiceCollection extension methods.
  Group related services into composable Add* methods for clean Program.cs,
  reusable test configuration, and proper lifetime management.
  Use when structuring dependency injection in ASP.NET Core or .NET applications.
metadata:
  author: RyoMurakami1983
  tags: [dependency-injection, di, dotnet, aspnetcore, iservicecollection, testing]
  invocable: false
---

# Dependency Injection Patterns

Organize Microsoft.Extensions.DependencyInjection (DI) registrations into composable `IServiceCollection` extension methods. Eliminates massive `Program.cs` files, enables service reuse in tests, and enforces correct lifetime management.

**Acronyms**: DI (Dependency Injection), DML (Data Manipulation Language).

## When to Use This Skill

- Organizing service registrations in ASP.NET Core applications to avoid bloated Program.cs files
- Designing composable `Add*` extension methods that group related services into cohesive units
- Making service configuration reusable between production application and integration test projects
- Choosing correct service lifetimes (Singleton, Scoped, Transient) based on state and threading
- Fixing scope-related bugs where scoped services are injected into singletons or background services
- Implementing factory-based registration with `IServiceProvider` for complex initialization logic
- Creating conditional service registration that varies by environment (development vs production)

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-project-structure` | .NET solution layout, project references, layer separation |
| `dotnet-modern-csharp-coding-standards` | Record types, pattern matching, Result error handling |
| `dotnet-efcore-patterns` | EF Core DbContext lifetime, NoTracking, migration management |

## Core Principles

1. **Compose via Extension Methods** — Group related registrations into `Add{Feature}Services()` methods on `IServiceCollection`. Why: keeps Program.cs clean and enables reuse.
2. **Return for Chaining** — Every extension method returns `IServiceCollection` to support fluent composition. Why: consistent API that reads as a pipeline.
3. **Correct Lifetime by Default** — Choose Singleton for stateless/thread-safe, Scoped for per-request state, Transient for lightweight/cheap. Why: wrong lifetimes cause stale data or memory leaks.
4. **Explicit Configuration** — Accept configuration parameters instead of hardcoding connection strings or secrets. Why: hidden settings cause deployment failures.
5. **Scope Per Unit of Work** — In background services and actors, create a scope for each unit of work. Why: scoped services require an explicit scope outside HTTP request pipelines.

> **Values**: 基礎と型の追求（`Add*` メソッドという「型」を徹底することで、どのプロジェクトでも再利用可能な DI 構造の基盤を作る）, 成長の複利（テストでの再利用を設計に組み込み、実装と品質が同時に成長する構造を作る）

## Workflow: Organize DI Registrations

### Step 1: Create Feature Extension Methods

Group related services into a single `Add{Feature}Services()` extension method placed near the services it registers. Why: co-location makes registrations discoverable.

```csharp
namespace MyApp.Users;

public static class UserServiceCollectionExtensions
{
    public static IServiceCollection AddUserServices(this IServiceCollection services)
    {
        // Repositories
        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IUserReadStore, UserReadStore>();

        // Services
        services.AddScoped<IUserService, UserService>();
        services.AddScoped<IUserValidationService, UserValidationService>();

        // Return for chaining
        return services;
    }
}
```

**File placement convention**: `{Feature}ServiceCollectionExtensions.cs` next to the feature's services.

```
src/
  MyApp.Api/
    Program.cs                                  # Composes all Add* methods
  MyApp.Users/
    Services/
      UserService.cs
    UserServiceCollectionExtensions.cs          # AddUserServices()
  MyApp.Email/
    EmailServiceCollectionExtensions.cs         # AddEmailServices()
```

> **Values**: 基礎と型の追求（命名規則とファイル配置の「型」が、チーム全体の発見可能性を支える）

### Step 2: Add Configuration Binding

Use `IOptions<T>` with `BindConfiguration` for feature-specific settings. Accept the config section name as a parameter for flexibility. Why: explicit configuration prevents hidden deployment failures.

```csharp
namespace MyApp.Email;

public static class EmailServiceCollectionExtensions
{
    public static IServiceCollection AddEmailServices(
        this IServiceCollection services,
        string configSectionName = "EmailSettings")
    {
        // Bind and validate configuration
        services.AddOptions<EmailOptions>()
            .BindConfiguration(configSectionName)
            .ValidateDataAnnotations()
            .ValidateOnStart();

        // Register services
        services.AddSingleton<IMjmlTemplateRenderer, MjmlTemplateRenderer>();
        services.AddScoped<IUserEmailComposer, UserEmailComposer>();
        services.AddScoped<IEmailSender, SmtpEmailSender>();

        return services;
    }
}
```

> **Values**: ニュートラルな視点（設定を外部パラメータ化し、環境に依存しない普遍的な設計を保つ）

### Step 3: Choose Correct Lifetimes

Select lifetimes based on state and thread-safety. Why: wrong lifetimes cause the most common DI bugs — stale DbContext, captive dependencies, and memory leaks.

| Lifetime | Use When | Examples |
|----------|----------|----------|
| **Singleton** | Stateless, thread-safe, expensive to create | Configuration, HttpClient factories, caches |
| **Scoped** | Stateful per-request, database contexts | DbContext, repositories, user context |
| **Transient** | Lightweight, stateful, cheap to create | Validators, short-lived helpers |

```csharp
// SINGLETON: Stateless services, shared safely
services.AddSingleton<IMjmlTemplateRenderer, MjmlTemplateRenderer>();
services.AddSingleton<IEmailLinkGenerator, EmailLinkGenerator>();

// SCOPED: Database access, per-request state
services.AddScoped<IUserRepository, UserRepository>();
services.AddScoped<IOrderService, OrderService>();

// TRANSIENT: Cheap, short-lived
services.AddTransient<CreateUserRequestValidator>();
```

> **Values**: 温故知新（DI コンテナの基本原則を正しく理解し、.NET の進化した機能と組み合わせる）

### Step 4: Compose in Program.cs

Chain all `Add*` calls in `Program.cs` for a clean, scannable entry point. Why: composition at the top level reveals the application's dependency structure at a glance.

```csharp
// ✅ GOOD: Clean, composable Program.cs
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

In background services, create a scope for each unit of work. Why: scoped services (DbContext, repositories) require an explicit scope outside ASP.NET Core's per-request pipeline.

```csharp
// ✅ GOOD: Create scope for each unit of work
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

Use `Add*` methods in test setup to reuse production configuration. Override only external dependencies with test doubles. Why: test confidence comes from running real registrations.

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
                // Production services already registered via Add* methods
                // Only override external dependencies for testing
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

- ✅ Group related services into `Add{Feature}Services()` methods for clear boundaries
- ✅ Place extension methods near the services they register for discoverability
- ✅ Return `IServiceCollection` from every extension method for fluent chaining
- ✅ Accept configuration parameters explicitly instead of hardcoding values
- ✅ Use consistent naming: `Add{Feature}Services()` for features, `Configure{Feature}()` for options
- ✅ Use `IServiceScopeFactory` in background services to create scopes per unit of work
- ✅ Reuse production `Add*` methods in test setup for realistic configuration
- ✅ Use `ValidateOnStart()` with `IOptions<T>` to catch configuration errors at startup
- ✅ Use conditional registration with `IHostEnvironment` for environment-specific services
- ✅ Accept `CancellationToken` in all async service methods

## Common Pitfalls

1. **Captive Dependency** — Injecting a Scoped service into a Singleton captures a stale instance forever. Fix: inject `IServiceProvider` or `IServiceScopeFactory` and create scopes manually.
2. **No Scope in Background Work** — Directly injecting scoped services into `BackgroundService` throws or returns stale data. Fix: use `IServiceScopeFactory.CreateScope()` per iteration.
3. **Hidden Configuration** — Hardcoding connection strings or secrets inside extension methods. Fix: accept configuration values as method parameters or use `IOptions<T>`.
4. **Overly Generic Extensions** — Creating `AddServices()` that registers 50 unrelated things. Fix: split into feature-specific `Add{Feature}Services()` methods.
5. **Missing Return Statement** — Forgetting to return `IServiceCollection` from the extension method. Fix: always end with `return services;` for chaining.

## Anti-Patterns

### ❌ Massive Program.cs → ✅ Composable Extensions

```csharp
// ❌ BAD: 200+ lines of unorganized registrations
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IOrderRepository, OrderRepository>();
// ... 150 more lines of mixed registrations ...

// ✅ GOOD: Clean composition with clear structure
builder.Services
    .AddUserServices()
    .AddOrderServices()
    .AddEmailServices();
```

### ❌ Scoped into Singleton → ✅ Scope Factory

```csharp
// ❌ BAD: Singleton captures scoped service — stale DbContext!
public class CacheService  // Registered as Singleton
{
    private readonly IUserRepository _repo;  // Scoped — captured at startup!
    public CacheService(IUserRepository repo) { _repo = repo; }
}

// ✅ GOOD: Create scope when needed
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
// ❌ BAD: Buried important settings inside extension
public static IServiceCollection AddDatabase(this IServiceCollection services)
{
    services.AddDbContext<AppDbContext>(options =>
        options.UseSqlServer("hardcoded-connection-string"));
}

// ✅ GOOD: Accept configuration explicitly
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

| Pattern | Use For | Example |
|---------|---------|---------|
| `Add{Feature}Services()` | General feature registration | `AddUserServices()` |
| `Add{Feature}()` | Short form when unambiguous | `AddStripePayments()` |
| `Configure{Feature}()` | Primarily setting options | `ConfigureAuthentication()` |
| `Use{Feature}()` | Middleware on IApplicationBuilder | `UseAuthentication()` |

### Lifetime Decision Table

| Service characteristic | Lifetime | Why |
|------------------------|----------|-----|
| Stateless, thread-safe, expensive init | Singleton | Share one instance safely |
| Per-request state (DbContext, repos) | Scoped | Fresh state per HTTP request |
| Lightweight, cheap to create | Transient | No shared state needed |
| Long-lived host (BackgroundService) | Inject `IServiceScopeFactory` | Create scope per unit of work |
| Actor with scoped dependencies | Inject `IServiceProvider` | Create scope per message |

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
- [references/detailed-patterns.md](references/detailed-patterns.md) — Layered composition, Akka.Hosting integration, keyed services, actor scope management
