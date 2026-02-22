---
name: dotnet-database-performance
description: >
  Optimize .NET database access with CQRS read/write separation, N+1 prevention,
  AsNoTracking, row limits, and SQL-side joins. Use when designing data access layers,
  optimizing slow queries, or choosing between EF Core and Dapper.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [cqrs, ef-core, dapper, performance, database]
  invocable: false
---

# Database Performance Patterns

Optimize .NET database access using proven patterns: CQRS (Command Query Responsibility Segregation) read/write model separation, N+1 query prevention, AsNoTracking for reads, mandatory row limits, and SQL-side joins. Works with EF Core and Dapper on .NET 8+. Requires NuGet packages `Microsoft.EntityFrameworkCore` and/or `Dapper`.

**Acronyms**: CQRS (Command Query Responsibility Segregation), EF (Entity Framework), DTO (Data Transfer Object), DI (Dependency Injection).

## When to Use This Skill

- Designing data access layers with separate read and write models for performance isolation
- Optimizing slow database queries by eliminating N+1 patterns and unnecessary tracking
- Choosing between EF Core and Dapper for specific workload types in the same project
- Implementing cursor-based or offset pagination with mandatory row limits on every query
- Reviewing existing code for Cartesian explosion risks caused by multiple Include calls
- Replacing generic repository patterns with purpose-built, query-optimized read stores

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-modern-csharp-coding-standards` | Record types, pattern matching, Result\<T\> error handling |
| `dotnet-type-design-performance` | Span\<T\>, Memory\<T\>, zero-allocation patterns |
| `dotnet-project-structure` | Solution layout, project organization, dependency management |

## Core Principles

1. **Separate Read and Write Models** — Use different types for queries and commands. Why: read models are denormalized projections; write models enforce validation and invariants.
2. **Think in Batches** — Fetch related data in bulk queries, never one-by-one. Why: N+1 queries cause linear database round-trips that destroy performance under load.
3. **Only Retrieve What You Need** — Project specific columns and apply row limits on every read. Why: transferring unused data wastes bandwidth, memory, and database I/O.
4. **Do Joins in SQL** — Never join collections in application memory. Why: the database engine optimizes joins with indexes; application-side joins are O(n×m) brute force.
5. **Disable Tracking for Reads** — Use AsNoTracking on all read-only queries in EF Core. Why: change tracking allocates snapshot copies of every entity, doubling memory usage.

> **Values**: 基礎と型の追求（最小形式で最大可能性を生む設計思想）, 温故知新（SQL の基本原則を EF Core/Dapper の最新 API で活かす）

## Workflow: Optimize Database Access

### Step 1: Separate Read and Write Stores

Apply CQRS by creating distinct interfaces for read and write operations. Use when designing a new data access layer or refactoring a single repository into optimized query paths.

```csharp
// Read models: multiple specialized projections for different use cases
public interface IUserReadStore
{
    Task<UserProfile?> GetByIdAsync(UserId id, CancellationToken ct = default);
    Task<IReadOnlyList<UserSummary>> GetAllAsync(int limit, UserId? cursor = null, CancellationToken ct = default);
    Task<bool> EmailExistsAsync(EmailAddress email, CancellationToken ct = default);
}

// Write model: accepts typed commands, returns minimal data
public interface IUserWriteStore
{
    Task<UserId> CreateAsync(CreateUserCommand command, CancellationToken ct = default);
    Task UpdateAsync(UserId id, UpdateUserCommand command, CancellationToken ct = default);
    Task DeleteAsync(UserId id, CancellationToken ct = default);
}
```

**Key structural differences:**
- **Read store** returns multiple DTO types (UserProfile, UserSummary, bool) — stateless projections
- **Write store** returns minimal data (UserId on create, void on update) — command-focused
- Different databases or tables can back read vs write for eventual consistency

See [references/cqrs-patterns.md](references/cqrs-patterns.md) for full folder structure and implementation examples.

> **Values**: 基礎と型の追求（読み取りと書き込みの責務を分離し、各モデルを最適化する型設計）

### Step 2: Apply Row Limits and Pagination

Apply mandatory `limit` parameters on every read method. Use when designing any query that returns a collection — unbounded result sets are a production incident waiting to happen.

```csharp
public interface IOrderReadStore
{
    // Limit is required, not optional
    Task<IReadOnlyList<OrderSummary>> GetByCustomerAsync(
        CustomerId customerId, int limit,
        OrderId? cursor = null, CancellationToken ct = default);
}
```

**Cursor-based pagination (Dapper):**

```csharp
const string sql = """
    SELECT id, customer_id, total, status, created_at
    FROM orders
    WHERE customer_id = @CustomerId
    AND (@Cursor IS NULL OR created_at < (SELECT created_at FROM orders WHERE id = @Cursor))
    ORDER BY created_at DESC
    LIMIT @Limit
    """;
```

**Offset pagination (EF Core):**

```csharp
var orders = await query
    .AsNoTracking()
    .Skip((paginator.PageNumber - 1) * paginator.PageSize)
    .Take(paginator.PageSize)  // Always limit!
    .Select(o => new OrderSummary(new OrderId(o.Id), o.Total, o.Status, o.CreatedAt))
    .ToListAsync(ct);
```

> **Values**: 継続は力（すべてのクエリに制限を適用する習慣が、本番障害を未然に防ぐ）

### Step 3: Use AsNoTracking for Read Queries

Apply `AsNoTracking()` on all read-only EF Core queries. Use when retrieving data you will not modify — change tracking doubles memory usage by storing entity snapshots.

```csharp
// ✅ Disable tracking for reads
var users = await _context.Users
    .AsNoTracking()
    .Where(u => u.IsActive)
    .ToListAsync();

// ❌ Track entities you won't modify — wasteful
var users = await _context.Users
    .Where(u => u.IsActive)
    .ToListAsync();  // Change tracking enabled
```

**Configure default behavior for read-heavy applications:**

```csharp
// In DbContext configuration
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    optionsBuilder.UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking);
}

// Then explicitly enable tracking when needed for writes
var user = await _context.Users
    .AsTracking()  // Explicit — we intend to modify
    .FirstOrDefaultAsync(u => u.Id == userId);
```

> **Values**: ニュートラルな視点（デフォルトを NoTracking にし、追跡が必要な箇所だけ明示する偏りのない設計）

### Step 4: Prevent N+1 Queries

Apply batch loading or eager loading instead of per-item queries. Use when fetching a list and its related data — the N+1 pattern causes one query per item, scaling linearly with data size.

```csharp
// ❌ N+1 queries — each iteration hits the database
var orders = await _context.Orders.ToListAsync();
foreach (var order in orders)
{
    var items = await _context.OrderItems
        .Where(i => i.OrderId == order.Id).ToListAsync();
}

// ✅ EF Core: single query with join
var orders = await _context.Orders
    .AsNoTracking()
    .Include(o => o.Items)
    .ToListAsync();
```

**Dapper batch approach (two queries, no N+1):**

```csharp
const string sql = """
    SELECT id, customer_id, total FROM orders WHERE customer_id = @CustomerId;
    SELECT oi.* FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.id WHERE o.customer_id = @CustomerId;
    """;

using var multi = await connection.QueryMultipleAsync(sql, new { CustomerId = customerId });
var orders = (await multi.ReadAsync<OrderRow>()).ToList();
var items = (await multi.ReadAsync<OrderItemRow>()).ToList();
```

> **Values**: 成長の複利（N+1 を見抜く力が、あらゆるデータアクセス層の品質を底上げする）

### Step 5: Perform Joins in SQL and Avoid Cartesian Explosions

Apply SQL-side joins and use `AsSplitQuery()` or explicit projection for multiple Include calls. Use when combining related entities — application-side joins waste memory and CPU.

```csharp
// ❌ Application-side join — two full table scans, O(n×m) in memory
var customers = await _context.Customers.ToListAsync();
var orders = await _context.Orders.ToListAsync();
var result = customers.Select(c => new {
    Customer = c,
    Orders = orders.Where(o => o.CustomerId == c.Id).ToList()
});

// ✅ SQL join — single query, database-optimized
var result = await _context.Customers
    .AsNoTracking()
    .Include(c => c.Orders)
    .ToListAsync();
```

**Avoid Cartesian explosions with AsSplitQuery:**

```csharp
// ❌ Cartesian: 100 reviews × 20 images × 5 categories = 10,000 rows
var product = await _context.Products
    .Include(p => p.Reviews).Include(p => p.Images).Include(p => p.Categories)
    .FirstOrDefaultAsync(p => p.Id == id);

// ✅ Split: 4 separate queries, ~125 rows total
var product = await _context.Products
    .AsSplitQuery()
    .Include(p => p.Reviews).Include(p => p.Images).Include(p => p.Categories)
    .FirstOrDefaultAsync(p => p.Id == id);

// ✅ Best: explicit projection — only fetch what you need
var product = await _context.Products
    .AsNoTracking()
    .Where(p => p.Id == id)
    .Select(p => new ProductDetail(
        p.Id, p.Name,
        p.Reviews.OrderByDescending(r => r.CreatedAt).Take(10).ToList(),
        p.Images.Take(5).ToList(),
        p.Categories.Select(c => c.Name).ToList()))
    .FirstOrDefaultAsync();
```

> **Values**: 余白の設計（プロジェクションで必要なデータだけ取得し、将来のスケーリングに余白を残す）

## Good Practices

- ✅ Use separate read/write store interfaces — never reuse the same entity for both
- ✅ Apply `AsNoTracking()` on every read-only query in EF Core
- ✅ Use `AsSplitQuery()` when multiple `Include` calls risk Cartesian products
- ✅ Apply mandatory `limit` parameter on every collection-returning read method
- ✅ Use cursor-based pagination for large datasets over offset pagination
- ✅ Use Dapper for complex read queries where explicit SQL is cleaner and faster
- ✅ Use EF Core for writes with validation and domain-heavy operations
- ✅ Constrain column sizes with `HasMaxLength()` in EF Core model configuration
- ✅ Avoid generic `IRepository<T>` — build purpose-specific read stores instead
- ✅ Accept `CancellationToken` in all async data access methods

## Common Pitfalls

1. **Unbounded result sets** — Returning all rows without a `LIMIT` clause causes out-of-memory in production. Fix: make `limit` a required method parameter.
2. **Tracking read-only entities** — EF Core change tracking doubles memory usage. Fix: apply `AsNoTracking()` on every read-only query.
3. **N+1 query loops** — Fetching related data inside a `foreach` loop creates one query per item. Fix: use `Include()` or batch queries.
4. **Application-side joins** — Loading two full tables and joining in LINQ is O(n×m). Fix: use SQL `JOIN` or EF Core `Include()`.
5. **Cartesian explosion from multiple Includes** — Three `Include` calls can multiply rows exponentially. Fix: use `AsSplitQuery()` or explicit projection.
6. **Generic repository hiding complexity** — `IRepository<T>.GetAll()` makes it impossible to enforce limits or optimize queries. Fix: design purpose-built stores.

## Anti-Patterns

### ❌ Generic Repository → ✅ Purpose-Built Stores

```csharp
// ❌ BAD — can't optimize, no limits, hides N+1
public interface IRepository<T>
{
    Task<T?> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();  // No limit!
    Task<IEnumerable<T>> FindAsync(Expression<Func<T, bool>> predicate);
}

// ✅ GOOD — query-specific, enforces limits, optimizable
public interface IOrderReadStore
{
    Task<OrderDetail?> GetByIdAsync(OrderId id, CancellationToken ct = default);
    Task<IReadOnlyList<OrderSummary>> GetByCustomerAsync(
        CustomerId id, int limit, CancellationToken ct = default);
}
```

**Architecture-level problems with generic repositories:**
- Cannot optimize specific query patterns or enforce row limits
- Hide N+1 problems behind abstraction layers
- Encourage fetching too much data through convenience methods

### ❌ SELECT * → ✅ Explicit Column Projection

```csharp
// ❌ BAD — fetches all columns including large text fields
var users = await _context.Users.ToListAsync();

// ✅ GOOD — project only needed columns
var users = await _context.Users
    .AsNoTracking()
    .Select(u => new UserSummary(u.Id, u.Name, u.Email))
    .ToListAsync();
```

### ❌ Unconstrained Strings → ✅ MaxLength Configuration

```csharp
// ✅ Configure column sizes to prevent oversized data
builder.Property(u => u.Email).HasMaxLength(254).IsRequired();  // RFC 5321 limit
builder.Property(u => u.Name).HasMaxLength(100).IsRequired();
builder.Property(u => u.Notes).HasColumnType("text");  // Explicit large content
```

## Quick Reference

### EF Core vs Dapper Decision Table

| Scenario | Recommendation | Why |
|----------|---------------|-----|
| Simple CRUD operations | EF Core | Change tracking and migrations simplify writes |
| Complex read queries | Dapper | Explicit SQL gives full control over performance |
| Writes with domain validation | EF Core | Entity configuration enforces constraints |
| Bulk insert/update operations | Dapper or raw SQL | Avoids per-entity tracking overhead |
| Reporting and analytics queries | Dapper | Complex aggregations are cleaner in raw SQL |
| Mixed read/write project | Both | EF Core for writes, Dapper for reads |

### Anti-Pattern Quick Fix Table

| Anti-Pattern | Fix | Instead |
|--------------|-----|---------|
| No row limit | Add `limit` parameter | Every read method requires a limit |
| SELECT * | Project columns | Use `.Select()` for specific fields |
| N+1 queries | Batch or Include | Use `.Include()` or multi-query |
| Application joins | SQL JOIN | Use `.Include()` or `INNER JOIN` |
| Cartesian explosion | AsSplitQuery | Use `.AsSplitQuery()` or projection |
| Tracking reads | AsNoTracking | Use `.AsNoTracking()` on read queries |
| Generic repository | Purpose-built stores | Design query-specific interfaces |

## Resources

- [EF Core Performance](https://learn.microsoft.com/en-us/ef/core/performance/) — Official performance guide
- [Dapper](https://github.com/DapperLib/Dapper) — Micro-ORM for high-performance reads
- [AsSplitQuery](https://learn.microsoft.com/en-us/ef/core/querying/single-split-queries) — Split vs single query guidance
- [references/cqrs-patterns.md](references/cqrs-patterns.md) — Full CQRS folder structure and Dapper implementation
