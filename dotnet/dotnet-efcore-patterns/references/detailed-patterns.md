# EF Core Detailed Patterns

Overflow reference for [dotnet-efcore-patterns](../SKILL.md). Contains full code examples and advanced scenarios.

## Migration Service Full Setup

### Project Structure

```
src/
├── MyApp.AppHost/           # Aspire orchestration
├── MyApp.Api/               # Main application
├── MyApp.Infrastructure/    # DbContext and migrations
└── MyApp.MigrationService/  # Dedicated migration runner
```

### MigrationService Program.cs

```csharp
using MyApp.Infrastructure.Data;
using MyApp.MigrationService;
using Microsoft.EntityFrameworkCore;

var builder = Host.CreateApplicationBuilder(args);

// Add Aspire service defaults
builder.AddServiceDefaults();

// Add PostgreSQL DbContext
var connectionString = builder.Configuration.GetConnectionString("appdb")
    ?? throw new InvalidOperationException("Connection string 'appdb' not found.");

builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString, npgsqlOptions =>
        npgsqlOptions.MigrationsAssembly("MyApp.Infrastructure")));

// Add the migration worker
builder.Services.AddHostedService<MigrationWorker>();

var host = builder.Build();
host.Run();
```

### Full MigrationWorker with Logging

```csharp
public class MigrationWorker : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly IHostApplicationLifetime _hostApplicationLifetime;
    private readonly ILogger<MigrationWorker> _logger;

    public MigrationWorker(
        IServiceProvider serviceProvider,
        IHostApplicationLifetime hostApplicationLifetime,
        ILogger<MigrationWorker> logger)
    {
        _serviceProvider = serviceProvider;
        _hostApplicationLifetime = hostApplicationLifetime;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Migration service starting...");

        try
        {
            using var scope = _serviceProvider.CreateScope();
            var dbContext = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

            await RunMigrationsAsync(dbContext, stoppingToken);

            _logger.LogInformation("Migration service completed successfully.");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Migration service failed: {Error}", ex.Message);
            throw;
        }
        finally
        {
            _hostApplicationLifetime.StopApplication();
        }
    }

    private async Task RunMigrationsAsync(ApplicationDbContext dbContext, CancellationToken ct)
    {
        var strategy = dbContext.Database.CreateExecutionStrategy();

        await strategy.ExecuteAsync(async () =>
        {
            var pendingMigrations = await dbContext.Database.GetPendingMigrationsAsync(ct);

            if (pendingMigrations.Any())
            {
                _logger.LogInformation("Applying {Count} pending migrations...",
                    pendingMigrations.Count());

                await dbContext.Database.MigrateAsync(ct);

                _logger.LogInformation("Migrations applied successfully.");
            }
            else
            {
                _logger.LogInformation("No pending migrations. Database is up to date.");
            }
        });
    }
}
```

## Advanced Migration Commands

### Rollback and Multi-Context Scenarios

```bash
# Rollback to a specific migration
dotnet ef database update PreviousMigrationName \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# With a specific DbContext (if you have multiple)
dotnet ef migrations add AddCustomerTable \
    --context ApplicationDbContext \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# Generate SQL script for all migrations
dotnet ef migrations script \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api \
    --output migrations.sql
```

## DbContext Lifetime Patterns

### ASP.NET Core (Scoped by Default)

```csharp
// Scoped = one instance per HTTP request
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString));
```

### Background Services (Create Scope)

```csharp
public class MyBackgroundService : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // Create scope for each unit of work
        using var scope = _serviceProvider.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        // ... use dbContext ...
    }
}
```

### Actors / Long-Lived Objects (Factory Pattern)

```csharp
public class OrderActor : ReceiveActor
{
    private readonly IDbContextFactory<ApplicationDbContext> _dbFactory;

    public OrderActor(IDbContextFactory<ApplicationDbContext> dbFactory)
    {
        _dbFactory = dbFactory;

        ReceiveAsync<GetOrder>(async msg =>
        {
            // Create fresh context for each operation
            await using var db = await _dbFactory.CreateDbContextAsync();
            var order = await db.Orders.FindAsync(msg.OrderId);
            Sender.Tell(order);
        });
    }
}

// Registration
builder.Services.AddDbContextFactory<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString));
```

## Explicit Add/Update/Delete Pattern

Full CRUD pattern when NoTracking is the default:

```csharp
public class OrderService
{
    private readonly ApplicationDbContext _db;

    // CREATE — Always use Add (works regardless of tracking)
    public async Task<Order> CreateOrderAsync(Order order)
    {
        _db.Orders.Add(order);
        await _db.SaveChangesAsync();
        return order;
    }

    // UPDATE — Explicitly mark as modified
    public async Task UpdateOrderStatusAsync(Guid orderId, OrderStatus newStatus)
    {
        var order = await _db.Orders.FirstOrDefaultAsync(o => o.Id == orderId)
            ?? throw new NotFoundException($"Order {orderId} not found");

        order.Status = newStatus;
        order.UpdatedAt = DateTimeOffset.UtcNow;

        _db.Orders.Update(order);
        await _db.SaveChangesAsync();
    }

    // DELETE — Attach and remove
    public async Task DeleteOrderAsync(Guid orderId)
    {
        var order = new Order { Id = orderId };
        _db.Orders.Remove(order);
        await _db.SaveChangesAsync();
    }
}
```

## Query Splitting Details

### When to Prefer SingleQuery

- Small, well-understood navigation graphs (2-3 levels)
- Queries where all related data is always needed
- Performance-critical paths where round-trip cost is lower than cartesian explosion

### When to Prefer SplitQuery

- Large or unpredictable navigation graphs
- Many-to-many relationships
- Queries loading collections that may not all be needed

## Testing with EF Core

### In-Memory Provider (Unit Tests Only)

```csharp
// Only for simple unit tests — doesn't match real database behavior
var options = new DbContextOptionsBuilder<ApplicationDbContext>()
    .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
    .Options;

using var context = new ApplicationDbContext(options);
```

### Real Database with TestContainers (Integration Tests)

See the `testcontainers-integration-tests` skill for proper database testing.

```csharp
// Use real PostgreSQL in container
var container = new PostgreSqlBuilder()
    .WithImage("postgres:16-alpine")
    .Build();

await container.StartAsync();

var options = new DbContextOptionsBuilder<ApplicationDbContext>()
    .UseNpgsql(container.GetConnectionString())
    .Options;
```
