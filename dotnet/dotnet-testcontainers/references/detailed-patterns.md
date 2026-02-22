# Detailed Patterns — Testcontainers for .NET

Extended examples and configurations referenced from the main [SKILL.md](../SKILL.md).

## Redis Integration Tests

```csharp
public class RedisTests : IAsyncLifetime
{
    private readonly TestcontainersContainer _redisContainer;
    private IConnectionMultiplexer _redis = null!;

    public RedisTests()
    {
        _redisContainer = new TestcontainersBuilder<TestcontainersContainer>()
            .WithImage("redis:alpine")
            .WithPortBinding(6379, true)
            .WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(6379))
            .Build();
    }

    public async Task InitializeAsync()
    {
        await _redisContainer.StartAsync();
        var port = _redisContainer.GetMappedPublicPort(6379);
        _redis = await ConnectionMultiplexer.ConnectAsync($"localhost:{port}");
    }

    public async Task DisposeAsync()
    {
        await _redis.DisposeAsync();
        await _redisContainer.DisposeAsync();
    }

    [Fact]
    public async Task Redis_ShouldCacheValues()
    {
        var db = _redis.GetDatabase();
        await db.StringSetAsync("key1", "value1");

        var value = await db.StringGetAsync("key1");
        Assert.Equal("value1", value.ToString());
    }

    [Fact]
    public async Task Redis_ShouldExpireKeys()
    {
        var db = _redis.GetDatabase();
        await db.StringSetAsync("temp-key", "temp-value",
            expiry: TimeSpan.FromSeconds(1));

        Assert.True(await db.KeyExistsAsync("temp-key"));

        await Task.Delay(1100);

        Assert.False(await db.KeyExistsAsync("temp-key"));
    }
}
```

## RabbitMQ Integration Tests

```csharp
public class RabbitMqTests : IAsyncLifetime
{
    private readonly TestcontainersContainer _rabbitContainer;
    private IConnection _connection = null!;

    public RabbitMqTests()
    {
        _rabbitContainer = new TestcontainersBuilder<TestcontainersContainer>()
            .WithImage("rabbitmq:management-alpine")
            .WithPortBinding(5672, true)
            .WithPortBinding(15672, true)
            .WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(5672))
            .Build();
    }

    public async Task InitializeAsync()
    {
        await _rabbitContainer.StartAsync();
        var port = _rabbitContainer.GetMappedPublicPort(5672);
        var factory = new ConnectionFactory
        {
            HostName = "localhost",
            Port = port,
            UserName = "guest",
            Password = "guest"
        };
        _connection = await factory.CreateConnectionAsync();
    }

    public async Task DisposeAsync()
    {
        await _connection.CloseAsync();
        await _rabbitContainer.DisposeAsync();
    }

    [Fact]
    public async Task RabbitMq_ShouldPublishAndConsumeMessage()
    {
        using var channel = await _connection.CreateChannelAsync();

        var queueName = "test-queue";
        await channel.QueueDeclareAsync(queueName, durable: false,
            exclusive: false, autoDelete: true);

        // Publish
        var message = "Hello, RabbitMQ!";
        var body = Encoding.UTF8.GetBytes(message);
        await channel.BasicPublishAsync(exchange: "",
            routingKey: queueName, body: body);

        // Consume
        var consumer = new EventingBasicConsumer(channel);
        var tcs = new TaskCompletionSource<string>();

        consumer.Received += (model, ea) =>
        {
            var received = Encoding.UTF8.GetString(ea.Body.ToArray());
            tcs.SetResult(received);
        };

        await channel.BasicConsumeAsync(queueName, autoAck: true,
            consumer: consumer);

        var result = await tcs.Task.WaitAsync(TimeSpan.FromSeconds(5));
        Assert.Equal(message, result);
    }
}
```

## Testing Migrations with Real Databases

```csharp
public class MigrationTests : IAsyncLifetime
{
    private readonly TestcontainersContainer _container;
    private string _connectionString = null!;

    public async Task InitializeAsync()
    {
        _container = new TestcontainersBuilder<TestcontainersContainer>()
            .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
            .WithEnvironment("ACCEPT_EULA", "Y")
            .WithEnvironment("SA_PASSWORD", "Your_password123")
            .WithPortBinding(1433, true)
            .Build();

        await _container.StartAsync();

        var port = _container.GetMappedPublicPort(1433);
        _connectionString = $"Server=localhost,{port};Database=TestDb;"
            + "User Id=sa;Password=Your_password123;TrustServerCertificate=true";
    }

    [Fact]
    public async Task Migrations_ShouldRunSuccessfully()
    {
        var optionsBuilder = new DbContextOptionsBuilder<AppDbContext>();
        optionsBuilder.UseSqlServer(_connectionString);

        using var context = new AppDbContext(optionsBuilder.Options);

        await context.Database.MigrateAsync();

        var canConnect = await context.Database.CanConnectAsync();
        Assert.True(canConnect);

        var tables = await context.Database.SqlQueryRaw<string>(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES").ToListAsync();

        Assert.Contains("Orders", tables);
        Assert.Contains("Customers", tables);
    }

    public async Task DisposeAsync()
    {
        await _container.DisposeAsync();
    }
}
```

## Respawn Configuration Options

```csharp
var respawner = await Respawner.CreateAsync(connectionString, new RespawnerOptions
{
    // Tables to preserve (reference data, migrations history)
    TablesToIgnore = new Table[]
    {
        "__EFMigrationsHistory",
        new Table("public", "lookup_data"),  // Schema-qualified
    },

    // Schemas to clean (default: all schemas)
    SchemasToInclude = new[] { "public", "app" },

    // Or exclude specific schemas
    SchemasToExclude = new[] { "audit", "logging" },

    // Database adapter
    DbAdapter = DbAdapter.Postgres,  // or SqlServer, MySql

    // Handle circular foreign keys
    WithReseed = true  // Reset identity columns (SQL Server)
});
```

### Data Reset Strategy Comparison

| Approach | Speed | Pros | Cons |
|----------|-------|------|------|
| **New container per test** | ~15s | Complete isolation | Slow |
| **Respawn** | ~50ms | Fast, preserves schema/migrations | Requires careful table exclusion |
| **Transaction rollback** | ~1ms | Fastest | Can't test commit behavior |

**Use Respawn when:**
- Tests share a container via xUnit collection fixture
- You need to test actual commits (not just rollbacks)
- Container startup time is a bottleneck

## CI/CD Integration

### GitHub Actions

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest  # Has Docker pre-installed

    steps:
    - uses: actions/checkout@v3

    - name: Setup .NET
      uses: actions/setup-dotnet@v3
      with:
        dotnet-version: 9.0.x

    - name: Run Integration Tests
      run: |
        dotnet test tests/YourApp.IntegrationTests \
          --filter Category=Integration \
          --logger trx

    - name: Cleanup Containers
      if: always()
      run: docker container prune -f
```

## Performance Tips

1. **Reuse containers** — Share fixtures across tests in a collection
2. **Use Respawn** — Reset data without recreating containers
3. **Parallel execution** — Testcontainers handles port conflicts automatically
4. **Use lightweight images** — Alpine versions are smaller and faster
5. **Cache images** — Docker caches pulled images locally
6. **Limit container resources** — Set CPU/memory limits if needed:

```csharp
.WithResourceMapping(new CpuCount(2))
.WithResourceMapping(new MemoryLimit(512 * 1024 * 1024)) // 512MB
```
