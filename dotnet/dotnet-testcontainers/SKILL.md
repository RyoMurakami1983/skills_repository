---
name: dotnet-testcontainers
description: >
  Write integration tests using Testcontainers for .NET with xUnit and real Docker
  infrastructure. Covers SQL Server, PostgreSQL, Redis, RabbitMQ, multi-container
  networks, container reuse, and Respawn database reset.
  Use when writing integration tests that need real databases, caches, or message queues
  instead of mocks.
metadata:
  author: RyoMurakami1983
  tags: [testcontainers, integration-testing, docker, xunit, dotnet, database, redis, rabbitmq]
  invocable: false
---

# Integration Testing with Testcontainers

Write integration tests against real infrastructure in Docker containers instead of mocks. Testcontainers manages container lifecycle, port randomization, and cleanup automatically. Targets .NET 8+ with xUnit.

**Acronyms**: DI (Dependency Injection), CI (Continuous Integration), AMQP (Advanced Message Queuing Protocol), DML (Data Manipulation Language).

## When to Use This Skill

- Writing integration tests that need real databases, caches, or message queues in Docker
- Testing data access layers against actual SQL Server or PostgreSQL instances
- Verifying message queue publish-and-consume flows with real RabbitMQ brokers
- Testing Redis caching behavior including key expiration and data structures
- Replacing fragile infrastructure mocks with production-like container environments
- Validating database migration scripts against real database engines before deployment
- Orchestrating multi-container test setups where services communicate over Docker networks

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-efcore-patterns` | EF Core DbContext, NoTracking, migrations, query optimization |
| `dotnet-database-performance` | Query tuning, indexing, connection pooling |
| `dotnet-project-structure` | .NET solution layout, project references, layer separation |

## Core Principles

1. **Real Infrastructure Over Mocks** — Use actual databases and services in containers, not mocks. Why: mocks hide SQL errors, constraint violations, and performance issues that only surface in production.
2. **Automatic Lifecycle Management** — Testcontainers handles container startup, port assignment, and teardown. Why: eliminates manual Docker commands and orphaned containers.
3. **Test Isolation via Port Randomization** — Each test run gets random host ports to avoid conflicts. Why: enables parallel test execution and prevents "port already in use" failures.
4. **IAsyncLifetime for Setup and Teardown** — Use xUnit's `IAsyncLifetime` interface for async container management. Why: ensures containers start before tests and dispose after completion.
5. **Container Reuse for Speed** — Share containers across tests in a collection fixture when isolation allows. Why: avoids 10-30 second startup per test while maintaining data isolation via Respawn.

> **Values**: 基礎と型の追求（Testcontainers の「型」—IAsyncLifetime・ランダムポート・自動クリーンアップ—を守ることで、再現可能なテスト基盤を築く）, ニュートラルな視点（モックの偽りの安心感に偏らず、実インフラで検証する中立的な品質基準を保つ）

## Workflow: Integration Testing with Testcontainers

### Step 1: Add Required NuGet Packages

Install Testcontainers and infrastructure-specific client packages. Why: each container type needs its own client library for connection.

```xml
<ItemGroup>
  <PackageReference Include="Testcontainers" Version="*" />
  <PackageReference Include="xunit" Version="*" />
  <PackageReference Include="xunit.runner.visualstudio" Version="*" />

  <!-- Pick the packages you need -->
  <PackageReference Include="Microsoft.Data.SqlClient" Version="*" />
  <PackageReference Include="Npgsql" Version="*" />
  <PackageReference Include="StackExchange.Redis" Version="*" />
  <PackageReference Include="RabbitMQ.Client" Version="*" />
  <PackageReference Include="Respawn" Version="*" />
</ItemGroup>
```

> **Values**: 基礎と型の追求（必要なパッケージを最初に揃える「型」が、後工程の混乱を防ぐ）

### Step 2: Configure Container with Wait Strategy

Build a container with the correct image, environment variables, port binding, and wait strategy. Why: without a wait strategy, tests may execute before the container is ready.

```csharp
// ✅ GOOD — wait strategy ensures container is ready before tests
var container = new TestcontainersBuilder<TestcontainersContainer>()
    .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
    .WithEnvironment("ACCEPT_EULA", "Y")
    .WithEnvironment("SA_PASSWORD", "Your_password123")
    .WithPortBinding(1433, true)  // true = random host port
    .WithWaitStrategy(Wait.ForUnixContainer()
        .UntilPortIsAvailable(1433)
        .WithTimeout(TimeSpan.FromMinutes(2)))
    .Build();
```

```csharp
// ❌ BAD — no wait strategy, tests may fail on slow startup
var container = new TestcontainersBuilder<TestcontainersContainer>()
    .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
    .WithEnvironment("ACCEPT_EULA", "Y")
    .WithEnvironment("SA_PASSWORD", "Your_password123")
    .WithPortBinding(1433, 1433)  // fixed port — causes conflicts
    .Build();
```

Why: random port binding prevents "port already in use" failures. Wait strategies prevent race conditions.

> **Values**: 余白の設計（ランダムポートとWait Strategyで、テスト実行環境の差異に対する余白を確保する）

### Step 3: Implement Test Lifecycle with IAsyncLifetime

Use `IAsyncLifetime` for async container startup and disposal. Why: constructor-based setup cannot await async operations like container startup.

```csharp
public class SqlServerIntegrationTests : IAsyncLifetime
{
    private readonly TestcontainersContainer _container;
    private IDbConnection _db = null!;

    public SqlServerIntegrationTests()
    {
        _container = new TestcontainersBuilder<TestcontainersContainer>()
            .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
            .WithEnvironment("ACCEPT_EULA", "Y")
            .WithEnvironment("SA_PASSWORD", "Your_password123")
            .WithPortBinding(1433, true)
            .WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(1433))
            .Build();
    }

    public async Task InitializeAsync()
    {
        await _container.StartAsync();

        var port = _container.GetMappedPublicPort(1433);
        var cs = $"Server=localhost,{port};Database=master;User Id=sa;"
               + "Password=Your_password123;TrustServerCertificate=true";

        _db = new SqlConnection(cs);
        await _db.OpenAsync();

        // Create schema for tests
        await _db.ExecuteAsync(@"
            CREATE TABLE Orders (
                Id INT PRIMARY KEY,
                CustomerId NVARCHAR(50) NOT NULL,
                Total DECIMAL(18,2) NOT NULL,
                CreatedAt DATETIME2 DEFAULT GETUTCDATE()
            )");
    }

    public async Task DisposeAsync()
    {
        await _db.DisposeAsync();
        await _container.DisposeAsync();
    }

    [Fact]
    public async Task CanInsertAndRetrieveOrder()
    {
        await _db.ExecuteAsync(
            "INSERT INTO Orders (Id, CustomerId, Total) VALUES (1, 'CUST001', 99.99)");

        var order = await _db.QuerySingleAsync<Order>(
            "SELECT * FROM Orders WHERE Id = @Id", new { Id = 1 });

        Assert.Equal("CUST001", order.CustomerId);
        Assert.Equal(99.99m, order.Total);
    }
}
```

> **Values**: 基礎と型の追求（IAsyncLifetime という xUnit の「型」に従うことで、確実なセットアップと後片付けを保証する）

### Step 4: Test Against Multiple Infrastructure Types

Apply the same container pattern to PostgreSQL, Redis, and RabbitMQ. Why: the Testcontainers API is consistent across all container types — learn once, apply everywhere.

**PostgreSQL — transaction rollback test:**

```csharp
public class PostgreSqlTests : IAsyncLifetime
{
    private readonly TestcontainersContainer _container;
    private NpgsqlConnection _connection = null!;

    public PostgreSqlTests()
    {
        _container = new TestcontainersBuilder<TestcontainersContainer>()
            .WithImage("postgres:latest")
            .WithEnvironment("POSTGRES_PASSWORD", "postgres")
            .WithEnvironment("POSTGRES_DB", "testdb")
            .WithPortBinding(5432, true)
            .WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(5432))
            .Build();
    }

    public async Task InitializeAsync()
    {
        await _container.StartAsync();
        var port = _container.GetMappedPublicPort(5432);
        _connection = new NpgsqlConnection(
            $"Host=localhost;Port={port};Database=testdb;Username=postgres;Password=postgres");
        await _connection.OpenAsync();
    }

    public async Task DisposeAsync()
    {
        await _connection.DisposeAsync();
        await _container.DisposeAsync();
    }

    [Fact]
    public async Task Transaction_Rollback_PreventsInsert()
    {
        await _connection.ExecuteAsync(
            "CREATE TABLE orders (id SERIAL PRIMARY KEY, total NUMERIC(10,2))");

        using var tx = await _connection.BeginTransactionAsync();
        await _connection.ExecuteAsync(
            "INSERT INTO orders (total) VALUES (100.00)", transaction: tx);
        await tx.RollbackAsync();

        var count = await _connection.QuerySingleAsync<int>("SELECT COUNT(*) FROM orders");
        Assert.Equal(0, count);
    }
}
```

See [references/detailed-patterns.md](references/detailed-patterns.md) for Redis, RabbitMQ, and migration testing examples.

> **Values**: 温故知新（データベースごとに異なるSQL方言やトランザクション挙動という「過去の知恵」を、コンテナという新技術で検証する）

### Step 5: Orchestrate Multi-Container Networks

Create a shared Docker network when containers need to communicate. Why: containers on the same network can reach each other via aliases, enabling realistic service topology tests.

```csharp
public class MultiContainerTests : IAsyncLifetime
{
    private readonly INetwork _network;
    private readonly TestcontainersContainer _dbContainer;
    private readonly TestcontainersContainer _redisContainer;

    public MultiContainerTests()
    {
        _network = new TestcontainersNetworkBuilder().Build();

        _dbContainer = new TestcontainersBuilder<TestcontainersContainer>()
            .WithImage("postgres:latest")
            .WithNetwork(_network)
            .WithNetworkAliases("db")
            .WithEnvironment("POSTGRES_PASSWORD", "postgres")
            .Build();

        _redisContainer = new TestcontainersBuilder<TestcontainersContainer>()
            .WithImage("redis:alpine")
            .WithNetwork(_network)
            .WithNetworkAliases("redis")
            .Build();
    }

    public async Task InitializeAsync()
    {
        await _network.CreateAsync();
        await Task.WhenAll(
            _dbContainer.StartAsync(),
            _redisContainer.StartAsync());
    }

    public async Task DisposeAsync()
    {
        await Task.WhenAll(
            _dbContainer.DisposeAsync().AsTask(),
            _redisContainer.DisposeAsync().AsTask());
        await _network.DisposeAsync();
    }
}
```

> **Values**: 余白の設計（ネットワークエイリアスで疎結合な接続を設計し、コンテナ追加・変更の余白を確保する）

### Step 6: Optimize with Container Reuse and Respawn

Share containers across tests via xUnit collection fixtures and reset data with Respawn. Why: avoids 10-30 second container startup per test while maintaining data isolation.

```csharp
// Shared fixture — one container for all tests in the collection
public class DatabaseFixture : IAsyncLifetime
{
    private readonly TestcontainersContainer _container;
    private Respawner _respawner = null!;
    public NpgsqlConnection Connection { get; private set; } = null!;
    public string ConnectionString { get; private set; } = null!;

    public DatabaseFixture()
    {
        _container = new TestcontainersBuilder<TestcontainersContainer>()
            .WithImage("postgres:latest")
            .WithEnvironment("POSTGRES_PASSWORD", "postgres")
            .WithEnvironment("POSTGRES_DB", "testdb")
            .WithPortBinding(5432, true)
            .Build();
    }

    public async Task InitializeAsync()
    {
        await _container.StartAsync();
        var port = _container.GetMappedPublicPort(5432);
        ConnectionString = $"Host=localhost;Port={port};Database=testdb;"
                         + "Username=postgres;Password=postgres";
        Connection = new NpgsqlConnection(ConnectionString);
        await Connection.OpenAsync();

        // Run schema setup, then create Respawner
        _respawner = await Respawner.CreateAsync(ConnectionString, new RespawnerOptions
        {
            TablesToIgnore = new Table[] { "__EFMigrationsHistory" },
            DbAdapter = DbAdapter.Postgres
        });
    }

    public async Task ResetDatabaseAsync() => await _respawner.ResetAsync(ConnectionString);

    public async Task DisposeAsync()
    {
        await Connection.DisposeAsync();
        await _container.DisposeAsync();
    }
}

[CollectionDefinition("Database collection")]
public class DatabaseCollection : ICollectionFixture<DatabaseFixture> { }

// Tests share the container, reset data between tests
[Collection("Database collection")]
public class OrderTests : IAsyncLifetime
{
    private readonly DatabaseFixture _fixture;
    public OrderTests(DatabaseFixture fixture) => _fixture = fixture;

    public async Task InitializeAsync() => await _fixture.ResetDatabaseAsync();
    public Task DisposeAsync() => Task.CompletedTask;

    [Fact]
    public async Task CreateOrder_ShouldPersist()
    {
        await _fixture.Connection.ExecuteAsync(
            "INSERT INTO orders (customer_id, total) VALUES ('CUST1', 100.00)");

        var count = await _fixture.Connection.QuerySingleAsync<int>(
            "SELECT COUNT(*) FROM orders");
        Assert.Equal(1, count);
    }
}
```

See [references/detailed-patterns.md](references/detailed-patterns.md) for Respawn options and performance comparison table.

> **Values**: 成長の複利（コンテナ再利用 + Respawn の組み合わせを習得することで、テストスイート全体の実行速度と信頼性が複利的に向上する）

## Good Practices

- ✅ Always use `IAsyncLifetime` for async container setup and teardown
- ✅ Use `WithWaitStrategy` to ensure containers are ready before tests execute
- ✅ Use random port binding (`true` parameter) to avoid port conflicts
- ✅ Dispose containers in `DisposeAsync` to prevent orphaned Docker containers
- ✅ Reuse containers via collection fixtures when tests share infrastructure
- ✅ Use Respawn to reset database state between tests without recreating containers
- ✅ Test real SQL queries, constraints, transactions, and migrations — not mocks
- ✅ Use lightweight images (Alpine variants) for faster container startup
- ✅ Accept `CancellationToken` in async test setup methods
- ✅ Run tests against production-like data volumes for realistic behavior

## Common Pitfalls

1. **No Wait Strategy** — Tests execute before the database accepts connections. Fix: add `.WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(port))`.
2. **Fixed Port Binding** — Using `.WithPortBinding(5432, 5432)` causes "port already in use" in parallel runs. Fix: use `.WithPortBinding(5432, true)` for random host ports.
3. **Missing Disposal** — Forgetting `DisposeAsync` leaves containers running and consumes resources. Fix: implement `IAsyncLifetime.DisposeAsync` with null-safe disposal: `await _container?.DisposeAsync()`.
4. **Container Per Test** — Creating a new container for each `[Fact]` causes 10-30 second overhead per test. Fix: share containers with collection fixtures and reset with Respawn.
5. **Testing Mocks Instead of Infrastructure** — Mocking `IDbConnection` gives false confidence and misses real SQL errors. Fix: use Testcontainers with real database instances.

## Anti-Patterns

### ❌ Mocking Infrastructure → ✅ Real Containers

```csharp
// ❌ BAD — mock hides real SQL behavior, constraints, and errors
var mockDb = new Mock<IDbConnection>();
mockDb.Setup(db => db.QueryAsync<Order>(It.IsAny<string>()))
    .ReturnsAsync(new[] { new Order { Id = 1 } });

// ✅ GOOD — tests run against a real database in a container
await _container.StartAsync();
var port = _container.GetMappedPublicPort(1433);
var conn = new SqlConnection($"Server=localhost,{port};...");
var order = await conn.QuerySingleAsync<Order>("SELECT * FROM Orders WHERE Id = 1");
```

Why: mocks cannot catch SQL syntax errors, constraint violations, or transaction bugs.

### ❌ Fixed Ports → ✅ Random Port Binding

```csharp
// ❌ BAD — fails when port 5432 is already in use
.WithPortBinding(5432, 5432)

// ✅ GOOD — Testcontainers assigns a random available port
.WithPortBinding(5432, true)
var port = _container.GetMappedPublicPort(5432);
```

Why: fixed ports cause flaky tests in CI and block parallel execution.

### ❌ New Container Per Test → ✅ Shared Fixture with Respawn

```csharp
// ❌ BAD — 10-30 seconds overhead per test
public class SlowTests : IAsyncLifetime
{
    public async Task InitializeAsync() => await _container.StartAsync();
    public async Task DisposeAsync() => await _container.DisposeAsync();
}

// ✅ GOOD — shared container, ~50ms data reset
[Collection("Database collection")]
public class FastTests : IAsyncLifetime
{
    public async Task InitializeAsync() => await _fixture.ResetDatabaseAsync();
    public Task DisposeAsync() => Task.CompletedTask;
}
```

Why: Respawn resets data in ~50ms vs 10-30 seconds for container recreation.

### ❌ No Disposal → ✅ Proper Cleanup

```csharp
// ❌ BAD — container keeps running after tests
public async Task DisposeAsync() { /* empty */ }

// ✅ GOOD — null-safe disposal chain
public async Task DisposeAsync()
{
    await _connection?.DisposeAsync();
    await _container?.DisposeAsync();
}
```

Why: orphaned containers consume memory, CPU, and disk until manually stopped.

## Quick Reference

### Container Setup by Infrastructure Type

| Infrastructure | Image | Default Port | Key Environment Variables |
|---------------|-------|-------------|--------------------------|
| SQL Server | `mcr.microsoft.com/mssql/server:2022-latest` | 1433 | `ACCEPT_EULA=Y`, `SA_PASSWORD` |
| PostgreSQL | `postgres:latest` | 5432 | `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| Redis | `redis:alpine` | 6379 | (none required) |
| RabbitMQ | `rabbitmq:management-alpine` | 5672, 15672 | `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS` |

### Data Reset Strategy Decision

| Strategy | Speed | Isolation | Best For |
|----------|-------|-----------|----------|
| New container per test | ~15s | Complete | Rare, heavy schema changes |
| Respawn | ~50ms | Data-level | Most integration tests |
| Transaction rollback | ~1ms | Fastest | Tests that don't verify commits |

### Test Lifecycle Cheat Sheet

| Phase | Method | Action |
|-------|--------|--------|
| Build | Constructor | Configure container builder |
| Start | `InitializeAsync` | Start container, open connection, run migrations |
| Test | `[Fact]` methods | Execute tests against real infrastructure |
| Cleanup | `DisposeAsync` | Dispose connection, then dispose container |

## Resources

- [Testcontainers for .NET](https://dotnet.testcontainers.org/)
- [xUnit IAsyncLifetime](https://xunit.net/docs/shared-context#class-fixture)
- [Respawn — Database Reset Tool](https://github.com/jbogard/Respawn)
- [Docker Hub](https://hub.docker.com/) — Official container images
- [references/detailed-patterns.md](references/detailed-patterns.md) — Redis, RabbitMQ, migration testing, Respawn options, CI/CD setup
