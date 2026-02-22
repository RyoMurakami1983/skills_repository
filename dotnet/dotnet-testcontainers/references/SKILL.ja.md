---
name: dotnet-testcontainers
description: >
  Testcontainers for .NET と xUnit を使用して、Docker 上の実インフラに対する統合テストを記述する。
  SQL Server、PostgreSQL、Redis、RabbitMQ、マルチコンテナネットワーク、コンテナ再利用、
  Respawn によるデータベースリセットをカバー。
  Use when 実データベース・キャッシュ・メッセージキューを使った統合テストを書く場合に使用。
metadata:
  author: RyoMurakami1983
  tags: [testcontainers, integration-testing, docker, xunit, dotnet, database, redis, rabbitmq]
  invocable: false
---

<!-- このドキュメントは dotnet-testcontainers の日本語版です。英語版: ../SKILL.md -->

# Integration Testing with Testcontainers

モックの代わりに Docker コンテナ上の実インフラに対して統合テストを記述する。Testcontainers がコンテナのライフサイクル管理、ポートランダム化、クリーンアップを自動的に処理する。.NET 8+ と xUnit を対象とする。

**略語**: DI（Dependency Injection）、CI（Continuous Integration）、AMQP（Advanced Message Queuing Protocol）、DML（Data Manipulation Language）。

## When to Use This Skill

- Docker 上の実データベース・キャッシュ・メッセージキューが必要な統合テストを記述する
- 実際の SQL Server や PostgreSQL インスタンスに対してデータアクセス層をテストする
- 実際の RabbitMQ ブローカーでメッセージキューのパブリッシュ・コンシュームフローを検証する
- キーの有効期限やデータ構造を含む Redis キャッシュの動作をテストする
- 脆弱なインフラモックを本番環境に近いコンテナ環境に置き換える
- デプロイ前に実データベースエンジンに対してマイグレーションスクリプトを検証する
- Docker ネットワーク上でサービスが通信するマルチコンテナテスト環境を構築する

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-efcore-patterns` | EF Core DbContext、NoTracking、マイグレーション、クエリ最適化 |
| `dotnet-database-performance` | クエリチューニング、インデックス設計、コネクションプーリング |
| `dotnet-project-structure` | .NET ソリューションレイアウト、プロジェクト参照、レイヤー分離 |

## Core Principles

1. **Real Infrastructure Over Mocks** — モックではなく、コンテナ内の実データベース・サービスを使用する。モックは SQL エラー、制約違反、パフォーマンス問題を隠蔽し、本番でしか表面化しないため。
2. **Automatic Lifecycle Management** — Testcontainers がコンテナの起動・ポート割り当て・後片付けを処理する。手動の Docker コマンドや孤立コンテナを排除するため。
3. **Test Isolation via Port Randomization** — テスト実行ごとにランダムなホストポートが割り当てられる。並列テスト実行を可能にし、「ポート使用中」エラーを防ぐため。
4. **IAsyncLifetime for Setup and Teardown** — xUnit の `IAsyncLifetime` インターフェースで非同期コンテナ管理を行う。テスト前にコンテナが起動し、完了後に破棄されることを保証するため。
5. **Container Reuse for Speed** — テスト間でコンテナをコレクションフィクスチャ経由で共有する。Respawn によるデータ分離を維持しながら、テストごとの 10〜30 秒の起動を回避するため。

> **Values**: 基礎と型の追求（Testcontainers の「型」—IAsyncLifetime・ランダムポート・自動クリーンアップ—を守ることで、再現可能なテスト基盤を築く）, ニュートラルな視点（モックの偽りの安心感に偏らず、実インフラで検証する中立的な品質基準を保つ）

## Workflow: Integration Testing with Testcontainers

### Step 1: Add Required NuGet Packages

Testcontainers とインフラ固有のクライアントパッケージをインストールする。コンテナタイプごとに専用のクライアントライブラリが必要なため。

```xml
<ItemGroup>
  <PackageReference Include="Testcontainers" Version="*" />
  <PackageReference Include="xunit" Version="*" />
  <PackageReference Include="xunit.runner.visualstudio" Version="*" />

  <!-- 必要なパッケージを選択 -->
  <PackageReference Include="Microsoft.Data.SqlClient" Version="*" />
  <PackageReference Include="Npgsql" Version="*" />
  <PackageReference Include="StackExchange.Redis" Version="*" />
  <PackageReference Include="RabbitMQ.Client" Version="*" />
  <PackageReference Include="Respawn" Version="*" />
</ItemGroup>
```

> **Values**: 基礎と型の追求（必要なパッケージを最初に揃える「型」が、後工程の混乱を防ぐ）

### Step 2: Configure Container with Wait Strategy

正しいイメージ、環境変数、ポートバインディング、Wait Strategy でコンテナを構築する。Wait Strategy がないと、コンテナの準備が整う前にテストが実行される可能性があるため。

```csharp
// ✅ GOOD — Wait Strategy でコンテナの準備完了を保証
var container = new TestcontainersBuilder<TestcontainersContainer>()
    .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
    .WithEnvironment("ACCEPT_EULA", "Y")
    .WithEnvironment("SA_PASSWORD", "Your_password123")
    .WithPortBinding(1433, true)  // true = ランダムホストポート
    .WithWaitStrategy(Wait.ForUnixContainer()
        .UntilPortIsAvailable(1433)
        .WithTimeout(TimeSpan.FromMinutes(2)))
    .Build();
```

```csharp
// ❌ BAD — Wait Strategy なし、起動が遅い場合にテストが失敗する可能性
var container = new TestcontainersBuilder<TestcontainersContainer>()
    .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
    .WithEnvironment("ACCEPT_EULA", "Y")
    .WithEnvironment("SA_PASSWORD", "Your_password123")
    .WithPortBinding(1433, 1433)  // 固定ポート — 競合の原因
    .Build();
```

ランダムポートバインディングは「ポート使用中」エラーを防ぎ、Wait Strategy は競合状態を防ぐ。

> **Values**: 余白の設計（ランダムポートとWait Strategyで、テスト実行環境の差異に対する余白を確保する）

### Step 3: Implement Test Lifecycle with IAsyncLifetime

非同期コンテナの起動と破棄に `IAsyncLifetime` を使用する。コンストラクタベースのセットアップではコンテナ起動のような非同期操作を await できないため。

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

        // テスト用スキーマを作成
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

同じコンテナパターンを PostgreSQL、Redis、RabbitMQ に適用する。Testcontainers の API はすべてのコンテナタイプで一貫しており、一度学べばどこでも適用できるため。

**PostgreSQL — トランザクションロールバックテスト：**

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

Redis、RabbitMQ、マイグレーションテストの例は [references/detailed-patterns.md](detailed-patterns.md) を参照。

> **Values**: 温故知新（データベースごとに異なるSQL方言やトランザクション挙動という「過去の知恵」を、コンテナという新技術で検証する）

### Step 5: Orchestrate Multi-Container Networks

コンテナ間の通信が必要な場合に共有 Docker ネットワークを作成する。同一ネットワーク上のコンテナはエイリアスで到達でき、リアルなサービストポロジのテストが可能になるため。

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

xUnit コレクションフィクスチャでコンテナを共有し、Respawn でデータをリセットする。テストごとの 10〜30 秒のコンテナ起動を回避しつつ、データ分離を維持するため。

```csharp
// 共有フィクスチャ — コレクション内の全テストで1つのコンテナ
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

        // スキーマセットアップ後に Respawner を作成
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

// テストはコンテナを共有し、テスト間でデータをリセット
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

Respawn のオプションとパフォーマンス比較表は [references/detailed-patterns.md](detailed-patterns.md) を参照。

> **Values**: 成長の複利（コンテナ再利用 + Respawn の組み合わせを習得することで、テストスイート全体の実行速度と信頼性が複利的に向上する）

## Good Practices

- ✅ 非同期コンテナのセットアップと後片付けには必ず `IAsyncLifetime` を使用する
- ✅ テスト実行前にコンテナの準備完了を保証するため `WithWaitStrategy` を使用する
- ✅ ポート競合を回避するためランダムポートバインディング（`true` パラメータ）を使用する
- ✅ `DisposeAsync` でコンテナを破棄し、孤立した Docker コンテナを防ぐ
- ✅ インフラを共有するテストにはコレクションフィクスチャ経由でコンテナを再利用する
- ✅ コンテナ再作成なしでテスト間のデータベース状態をリセットするため Respawn を使用する
- ✅ モックではなく、実際の SQL クエリ、制約、トランザクション、マイグレーションをテストする
- ✅ コンテナ起動高速化のため軽量イメージ（Alpine バリアント）を使用する
- ✅ 非同期テストセットアップメソッドで `CancellationToken` を受け入れる
- ✅ 現実的な動作のため本番に近いデータ量でテストを実行する

## Common Pitfalls

1. **Wait Strategy なし** — データベースが接続を受け付ける前にテストが実行される。対策：`.WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(port))` を追加する。
2. **固定ポートバインディング** — `.WithPortBinding(5432, 5432)` は並列実行時に「ポート使用中」エラーを引き起こす。対策：ランダムホストポートに `.WithPortBinding(5432, true)` を使用する。
3. **破棄の欠如** — `DisposeAsync` を忘れるとコンテナが実行されたままリソースを消費する。対策：null 安全な破棄で `IAsyncLifetime.DisposeAsync` を実装する：`await _container?.DisposeAsync()`。
4. **テストごとのコンテナ** — 各 `[Fact]` で新しいコンテナを作成すると、テストごとに 10〜30 秒のオーバーヘッドが発生する。対策：コレクションフィクスチャでコンテナを共有し、Respawn でリセットする。
5. **インフラのモック化** — `IDbConnection` のモックは偽りの安心感を与え、実際の SQL エラーを見逃す。対策：Testcontainers で実データベースインスタンスを使用する。

## Anti-Patterns

### ❌ Mocking Infrastructure → ✅ Real Containers

```csharp
// ❌ BAD — モックは実際の SQL の動作、制約、エラーを隠す
var mockDb = new Mock<IDbConnection>();
mockDb.Setup(db => db.QueryAsync<Order>(It.IsAny<string>()))
    .ReturnsAsync(new[] { new Order { Id = 1 } });

// ✅ GOOD — コンテナ内の実データベースに対してテスト
await _container.StartAsync();
var port = _container.GetMappedPublicPort(1433);
var conn = new SqlConnection($"Server=localhost,{port};...");
var order = await conn.QuerySingleAsync<Order>("SELECT * FROM Orders WHERE Id = 1");
```

モックは SQL 構文エラー、制約違反、トランザクションバグを検出できないため。

### ❌ Fixed Ports → ✅ Random Port Binding

```csharp
// ❌ BAD — ポート 5432 が使用中の場合に失敗
.WithPortBinding(5432, 5432)

// ✅ GOOD — Testcontainers が利用可能なランダムポートを割り当て
.WithPortBinding(5432, true)
var port = _container.GetMappedPublicPort(5432);
```

固定ポートは CI でフレーキーテストを引き起こし、並列実行をブロックするため。

### ❌ New Container Per Test → ✅ Shared Fixture with Respawn

```csharp
// ❌ BAD — テストごとに 10〜30 秒のオーバーヘッド
public class SlowTests : IAsyncLifetime
{
    public async Task InitializeAsync() => await _container.StartAsync();
    public async Task DisposeAsync() => await _container.DisposeAsync();
}

// ✅ GOOD — 共有コンテナ、約 50ms のデータリセット
[Collection("Database collection")]
public class FastTests : IAsyncLifetime
{
    public async Task InitializeAsync() => await _fixture.ResetDatabaseAsync();
    public Task DisposeAsync() => Task.CompletedTask;
}
```

Respawn はコンテナ再作成の 10〜30 秒に対して約 50ms でデータをリセットするため。

### ❌ No Disposal → ✅ Proper Cleanup

```csharp
// ❌ BAD — テスト後もコンテナが実行され続ける
public async Task DisposeAsync() { /* 空 */ }

// ✅ GOOD — null 安全な破棄チェーン
public async Task DisposeAsync()
{
    await _connection?.DisposeAsync();
    await _container?.DisposeAsync();
}
```

孤立コンテナは手動で停止するまでメモリ、CPU、ディスクを消費し続けるため。

## Quick Reference

### Container Setup by Infrastructure Type

| インフラ | イメージ | デフォルトポート | 主要な環境変数 |
|---------|---------|---------------|--------------|
| SQL Server | `mcr.microsoft.com/mssql/server:2022-latest` | 1433 | `ACCEPT_EULA=Y`, `SA_PASSWORD` |
| PostgreSQL | `postgres:latest` | 5432 | `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| Redis | `redis:alpine` | 6379 | （不要） |
| RabbitMQ | `rabbitmq:management-alpine` | 5672, 15672 | `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS` |

### Data Reset Strategy Decision

| 戦略 | 速度 | 分離度 | 最適な用途 |
|------|------|--------|----------|
| テストごとに新コンテナ | 約 15 秒 | 完全 | スキーマ大変更が稀なケース |
| Respawn | 約 50ms | データレベル | ほとんどの統合テスト |
| トランザクションロールバック | 約 1ms | 最速 | コミット検証不要なテスト |

### Test Lifecycle Cheat Sheet

| フェーズ | メソッド | アクション |
|---------|---------|----------|
| 構築 | コンストラクタ | コンテナビルダーを設定 |
| 開始 | `InitializeAsync` | コンテナ起動、接続確立、マイグレーション実行 |
| テスト | `[Fact]` メソッド | 実インフラに対してテスト実行 |
| 後片付け | `DisposeAsync` | 接続を破棄、次にコンテナを破棄 |

## Resources

- [Testcontainers for .NET](https://dotnet.testcontainers.org/)
- [xUnit IAsyncLifetime](https://xunit.net/docs/shared-context#class-fixture)
- [Respawn — データベースリセットツール](https://github.com/jbogard/Respawn)
- [Docker Hub](https://hub.docker.com/) — 公式コンテナイメージ
- [references/detailed-patterns.md](detailed-patterns.md) — Redis、RabbitMQ、マイグレーションテスト、Respawn オプション、CI/CD セットアップ
