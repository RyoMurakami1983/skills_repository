---
name: dotnet-efcore-patterns
description: >
  Apply Entity Framework Core best practices including NoTracking by default,
  query splitting, migration management, and dedicated migration services.
  Use when setting up EF Core, optimizing queries, or managing database migrations.
metadata:
  author: RyoMurakami1983
  tags: [efcore, entity-framework, dotnet, database, migrations, aspire]
  invocable: false
---

# Entity Framework Core Patterns

A concise guardrail for EF Core (Entity Framework Core) development covering NoTracking defaults, migration management, query splitting, and transient failure handling. Targets .NET 8+ with PostgreSQL via Npgsql. Integrates with .NET Aspire for migration orchestration.

**Acronyms**: EF Core (Entity Framework Core), DI (Dependency Injection), DML (Data Manipulation Language).

## When to Use This Skill

- Setting up a new EF Core DbContext with performance-oriented defaults in a .NET project
- Optimizing read-heavy query performance by configuring NoTracking behavior globally
- Managing database migrations safely using EF Core CLI commands without manual edits
- Integrating EF Core migration execution with .NET Aspire orchestration pipelines
- Debugging silent write failures caused by change tracking misconfiguration issues
- Implementing bulk update and delete operations with ExecuteUpdate and ExecuteDelete
- Preventing cartesian explosion when loading multiple navigation collections eagerly

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-project-structure` | .NET solution layout, project references, layer separation |
| `dotnet-modern-csharp-coding-standards` | Record types, pattern matching, Result error handling |

## Core Principles

1. **NoTracking by Default** — Most queries are read-only; disable change tracking globally and opt-in with `.AsTracking()` only when writes are needed. Why: eliminates unnecessary overhead.
2. **Never Edit Migrations Manually** — Always use `dotnet ef` CLI commands to create, remove, and apply migrations. Why: manual edits corrupt the migration snapshot.
3. **Dedicated Migration Service** — Separate migration execution from application startup using a hosted service. Why: migrations complete before the app starts accepting requests.
4. **ExecutionStrategy for Retries** — Wrap transient-failure-prone operations in `CreateExecutionStrategy()`. Why: transient database failures are inevitable in production.
5. **Explicit Updates with NoTracking** — When NoTracking is active, explicitly call `.Update()` or use `.AsTracking()` before saving. Why: silent save failures are the most common EF Core bug.

> **Values**: 基礎と型の追求（NoTracking やマイグレーション CLI という「型」を守ることで、安全で高速な DB 操作の基盤を築く）, 温故知新（EF Core の進化した機能を活かしつつ、変更追跡の基本原則を忠実に守る）

## Workflow: Apply EF Core Patterns

### Step 1: Configure NoTracking by Default

Apply NoTracking globally in your DbContext constructor. Why: most queries are read-only and tracking adds unnecessary overhead.

```csharp
public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
        // Disable change tracking by default for better read performance
        ChangeTracker.QueryTrackingBehavior = QueryTrackingBehavior.NoTracking;
    }

    public DbSet<Order> Orders => Set<Order>();
    public DbSet<Customer> Customers => Set<Customer>();
}
```

**When tracking is needed:**

| Scenario | Use Tracking? | Why |
|----------|---------------|-----|
| Display data in UI | No | Read-only, no updates needed |
| API GET endpoints | No | Returning data, no mutations |
| Update single entity | Yes or `.Update()` | Need to persist changes |
| Complex navigation update | Yes | Tracking handles relationships |
| Batch operations | No + `ExecuteUpdate` | Single SQL, more efficient |

Use `.AsTracking()` or explicit `.Update()` for write operations:

```csharp
// ✅ Explicit Update — works with NoTracking
var order = await db.Orders.FirstOrDefaultAsync(o => o.Id == id);
order.Status = OrderStatus.Shipped;
db.Orders.Update(order);
await db.SaveChangesAsync();

// ✅ AsTracking — opt-in for specific queries
var order = await db.Orders.AsTracking()
    .FirstOrDefaultAsync(o => o.Id == id);
order.Status = OrderStatus.Shipped;
await db.SaveChangesAsync();
```

> **Values**: 基礎と型の追求（NoTracking をデフォルトにする「型」が、読み取り性能の基盤を作る）

### Step 2: Manage Migrations with CLI

Use `dotnet ef` CLI commands exclusively. Never edit, delete, or rename migration files manually. Why: the snapshot file tracks cumulative state and manual changes corrupt it.

```bash
# Create a new migration
dotnet ef migrations add AddCustomerTable \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# Remove last unapplied migration
dotnet ef migrations remove \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# Apply all pending migrations
dotnet ef database update \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# Generate idempotent SQL script (safe to run multiple times)
dotnet ef migrations script --idempotent \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api
```

See [references/detailed-patterns.md](references/detailed-patterns.md) for rollback commands and multi-context scenarios.

> **Values**: 継続は力（CLI コマンドという決まった手順をコツコツ守ることで、マイグレーション事故を防ぐ）

### Step 3: Separate Migration Service with Aspire

Create a dedicated migration runner that executes before the main application starts. Why: clean separation ensures migrations complete before any request processing begins.

```csharp
using Microsoft.EntityFrameworkCore;

// MigrationWorker.cs — runs migrations then stops
public class MigrationWorker(
    IServiceProvider serviceProvider,
    IHostApplicationLifetime lifetime,
    ILogger<MigrationWorker> logger) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        using var scope = serviceProvider.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        var strategy = db.Database.CreateExecutionStrategy();

        await strategy.ExecuteAsync(async () =>
        {
            await db.Database.MigrateAsync(ct);
            logger.LogInformation("Migrations applied successfully.");
        });

        lifetime.StopApplication();
    }
}
```

Configure Aspire AppHost to orchestrate the dependency order:

```csharp
// AppHost — migrations complete before API starts
var db = builder.AddPostgres("postgres").AddDatabase("appdb");

var migrations = builder.AddProject<Projects.MyApp_MigrationService>("migrations")
    .WaitFor(db).WithReference(db);

builder.AddProject<Projects.MyApp_Api>("api")
    .WaitForCompletion(migrations)  // Waits for migrations to finish
    .WithReference(db);
```

See [references/detailed-patterns.md](references/detailed-patterns.md) for full `Program.cs` setup and project structure layout.

> **Values**: 余白の設計（マイグレーションを分離することで、アプリ起動の順序に余白と安全性を確保する）

### Step 4: Handle Transient Failures

Wrap database operations in `CreateExecutionStrategy()` for automatic retry on transient failures. Why: network blips and brief database unavailability are normal in production.

```csharp
// ✅ Retry-safe update
var strategy = db.Database.CreateExecutionStrategy();

await strategy.ExecuteAsync(async () =>
{
    var order = await db.Orders.AsTracking()
        .FirstOrDefaultAsync(o => o.Id == id);
    if (order is null) return;

    order.Status = OrderStatus.Shipped;
    await db.SaveChangesAsync();
});

// ✅ Transaction inside strategy callback
await strategy.ExecuteAsync(async () =>
{
    await using var tx = await db.Database.BeginTransactionAsync();
    try
    {
        // ... operations ...
        await db.SaveChangesAsync();
        await tx.CommitAsync();
    }
    catch
    {
        await tx.RollbackAsync();
        throw;
    }
});
```

> **Values**: ニュートラルな視点（一時的障害を「異常」ではなく「日常」と捉え、偏りなく対処する設計）

### Step 5: Optimize with Bulk Operations and Query Splitting

Apply `ExecuteUpdateAsync` / `ExecuteDeleteAsync` for bulk operations instead of loading entities. Apply `SplitQuery` globally to prevent cartesian explosion with multiple `Include()` calls.

```csharp
// ❌ SLOW — loads all entities into memory
var expired = await db.Orders
    .Where(o => o.ExpiresAt < DateTimeOffset.UtcNow).ToListAsync();
foreach (var o in expired) o.Status = OrderStatus.Expired;
await db.SaveChangesAsync();

// ✅ FAST — single SQL UPDATE, no entity loading
await db.Orders
    .Where(o => o.ExpiresAt < DateTimeOffset.UtcNow)
    .ExecuteUpdateAsync(s => s
        .SetProperty(o => o.Status, OrderStatus.Expired)
        .SetProperty(o => o.UpdatedAt, DateTimeOffset.UtcNow));

// ✅ FAST — single SQL DELETE
await db.Orders
    .Where(o => o.Status == OrderStatus.Cancelled)
    .ExecuteDeleteAsync();
```

**Query splitting configuration:**

```csharp
// Global SplitQuery — prevents cartesian explosion
services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString, npgsql =>
        npgsql.UseQuerySplittingBehavior(QuerySplittingBehavior.SplitQuery)));

// Override per-query when single query is known to be better
var orders = await db.Orders
    .Include(o => o.Items)
    .Include(o => o.Payments)
    .AsSingleQuery()
    .ToListAsync();
```

| Behavior | Pros | Cons |
|----------|------|------|
| SplitQuery | No cartesian explosion, better for large collections | Multiple round-trips |
| SingleQuery | Single round-trip, transactional consistency | Cartesian explosion risk |

> **Values**: 成長の複利（バルク操作と SplitQuery の習得が、すべてのクエリ設計の品質を底上げする）

## Good Practices

- ✅ Use NoTracking by default; opt-in to tracking only for writes
- ✅ Use `dotnet ef` CLI commands exclusively for migration management
- ✅ Implement a dedicated migration service for production deployments
- ✅ Use `CreateExecutionStrategy()` for all database operations in production
- ✅ Use `ExecuteUpdateAsync` / `ExecuteDeleteAsync` for bulk data manipulation
- ✅ Use `SplitQuery` globally; override with `AsSingleQuery()` when appropriate
- ✅ Implement `IDbContextFactory<T>` for long-lived services and actors
- ✅ Use scoped DbContext lifetime in ASP.NET Core (one per HTTP request)
- ✅ Accept `CancellationToken` in all async database methods
- ✅ Use `await using` for manually created DbContext instances

## Common Pitfalls

1. **Forgetting Update with NoTracking** — Modifying an entity and calling `SaveChangesAsync()` without `.Update()` or `.AsTracking()`. The change is silently lost. Fix: always explicitly mark entities for update.
2. **N+1 Query Problem** — Accessing navigation properties in a loop without `.Include()`. Fix: use eager loading with `.Include()` or explicit `.Select()` projection.
3. **Blocking on Async** — Calling `.Result` or `.Wait()` in async context causes deadlocks. Fix: use `await` consistently through the entire call chain.
4. **Querying Inside Loops** — Executing `FindAsync` per iteration instead of a single `Where` with `Contains`. Fix: batch the query with `Where(o => ids.Contains(o.Id))`.
5. **Manual Migration Edits** — Editing or deleting migration files directly corrupts the model snapshot. Fix: use `dotnet ef migrations remove` to undo the last migration.

## Anti-Patterns

### ❌ Silent Save with NoTracking → ✅ Explicit Update

```csharp
// ❌ BAD — entity not tracked, SaveChanges does nothing
var customer = await db.Customers.FindAsync(id);
customer.Name = "New Name";
await db.SaveChangesAsync(); // Silent failure!

// ✅ GOOD — explicitly mark as modified
var customer = await db.Customers.FindAsync(id);
customer.Name = "New Name";
db.Customers.Update(customer);
await db.SaveChangesAsync();
```

### ❌ Loading Entities for Bulk Ops → ✅ ExecuteUpdate

```csharp
// ❌ BAD — loads all entities into memory, N+1 writes
var orders = await db.Orders.Where(o => o.IsExpired).ToListAsync();
foreach (var o in orders) { o.Status = OrderStatus.Expired; }
await db.SaveChangesAsync();

// ✅ GOOD — single SQL UPDATE statement
await db.Orders.Where(o => o.IsExpired)
    .ExecuteUpdateAsync(s => s.SetProperty(o => o.Status, OrderStatus.Expired));
```

### ❌ Manual Migration File Deletion → ✅ CLI Remove

```bash
# ❌ BAD — corrupts model snapshot
rm Migrations/20240101_AddCustomerTable.cs

# ✅ GOOD — safely removes migration and updates snapshot
dotnet ef migrations remove
```

### ❌ N+1 Lazy Loading → ✅ Eager Loading

```csharp
// ❌ BAD — one query per customer's orders
var customers = await db.Customers.ToListAsync();
foreach (var c in customers) { var orders = c.Orders; } // N+1!

// ✅ GOOD — single query with Include
var customers = await db.Customers
    .Include(c => c.Orders)
    .ToListAsync();
```

## Quick Reference

### DbContext Lifetime by Scenario

| Scenario | Lifetime | Registration |
|----------|----------|--------------|
| ASP.NET Core controllers | Scoped (per request) | `AddDbContext<T>()` |
| Background services | Create scope per unit | `IServiceProvider.CreateScope()` |
| Actors / long-lived objects | Factory per operation | `AddDbContextFactory<T>()` |

### NoTracking Decision Guide

| Operation | Approach | Why |
|-----------|----------|-----|
| Read-only query | NoTracking (default) | No overhead |
| Single entity update | `.AsTracking()` or `.Update()` | Need change detection |
| Bulk update / delete | `ExecuteUpdate` / `ExecuteDelete` | Single SQL statement |
| Complex navigation writes | `.AsTracking()` | Relationship handling |

### Migration Command Cheat Sheet

| Task | Command |
|------|---------|
| Create migration | `dotnet ef migrations add <Name>` |
| Remove last migration | `dotnet ef migrations remove` |
| Apply all pending | `dotnet ef database update` |
| Generate SQL script | `dotnet ef migrations script --idempotent` |
| Rollback to migration | `dotnet ef database update <PreviousName>` |

## Resources

- [EF Core Documentation](https://learn.microsoft.com/en-us/ef/core/)
- [Change Tracking in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/)
- [ExecuteUpdate and ExecuteDelete](https://learn.microsoft.com/en-us/ef/core/saving/execute-insert-update-delete)
- [Query Splitting](https://learn.microsoft.com/en-us/ef/core/querying/single-split-queries)
- [.NET Aspire Overview](https://learn.microsoft.com/en-us/dotnet/aspire/get-started/aspire-overview)
- [references/detailed-patterns.md](references/detailed-patterns.md) — Full migration service code, DbContext lifetime examples, testing patterns
