# CQRS Patterns — Detailed Implementation

## Folder Structure

```
src/
  MyApp.Data/
    Users/
      # Read side — multiple optimized projections
      IUserReadStore.cs
      PostgresUserReadStore.cs

      # Write side — command handlers
      IUserWriteStore.cs
      PostgresUserWriteStore.cs

      # Read DTOs — lightweight, denormalized
      UserProfile.cs
      UserSummary.cs

      # Write commands — validation-focused
      CreateUserCommand.cs
      UpdateUserCommand.cs
    Orders/
      IOrderReadStore.cs
      IOrderWriteStore.cs
      (similar structure...)
```

## Dapper Read Store Implementation

```csharp
public sealed class PostgresUserReadStore : IUserReadStore
{
    private readonly NpgsqlDataSource _dataSource;

    public PostgresUserReadStore(NpgsqlDataSource dataSource)
    {
        _dataSource = dataSource;
    }

    public async Task<UserProfile?> GetByIdAsync(UserId id, CancellationToken ct = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(ct);

        const string sql = """
            SELECT id, email, name, bio, created_at
            FROM users
            WHERE id = @Id
            """;

        var row = await connection.QuerySingleOrDefaultAsync<UserRow>(
            sql, new { Id = id.Value });

        return row?.ToUserProfile();
    }

    // Internal row type for Dapper mapping
    private sealed class UserRow
    {
        public Guid id { get; set; }
        public string email { get; set; } = null!;
        public string name { get; set; } = null!;
        public string? bio { get; set; }
        public DateTime created_at { get; set; }

        public UserProfile ToUserProfile() => new(
            Id: new UserId(id),
            Email: new EmailAddress(email),
            Name: new PersonName(name),
            Bio: bio,
            CreatedAt: new DateTimeOffset(created_at, TimeSpan.Zero));
    }
}
```

## Cursor-Based Pagination Implementation

```csharp
public async Task<IReadOnlyList<OrderSummary>> GetByCustomerAsync(
    CustomerId customerId,
    int limit,
    OrderId? cursor = null,
    CancellationToken ct = default)
{
    await using var connection = await _dataSource.OpenConnectionAsync(ct);

    const string sql = """
        SELECT id, customer_id, total, status, created_at
        FROM orders
        WHERE customer_id = @CustomerId
        AND (@Cursor IS NULL OR created_at < (SELECT created_at FROM orders WHERE id = @Cursor))
        ORDER BY created_at DESC
        LIMIT @Limit
        """;

    var rows = await connection.QueryAsync<OrderRow>(sql, new
    {
        CustomerId = customerId.Value,
        Cursor = cursor?.Value,
        Limit = limit
    });

    return rows.Select(r => r.ToOrderSummary()).ToList();
}
```

## EF Core Offset Pagination with PaginatedList

```csharp
public async Task<PaginatedList<OrderSummary>> GetOrdersAsync(
    CustomerId customerId,
    Paginator paginator,
    CancellationToken ct = default)
{
    var query = _context.Orders
        .AsNoTracking()
        .Where(o => o.CustomerId == customerId.Value)
        .OrderByDescending(o => o.CreatedAt);

    var totalCount = await query.CountAsync(ct);

    var orders = await query
        .Skip((paginator.PageNumber - 1) * paginator.PageSize)
        .Take(paginator.PageSize)
        .Select(o => new OrderSummary(
            new OrderId(o.Id),
            o.Total,
            o.Status,
            o.CreatedAt))
        .ToListAsync(ct);

    return new PaginatedList<OrderSummary>(
        orders,
        totalCount,
        paginator.PageSize,
        paginator.PageNumber);
}
```

## EF Core Column Size Configuration

```csharp
public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.Property(u => u.Email)
            .HasMaxLength(254)  // RFC 5321 limit
            .IsRequired();

        builder.Property(u => u.Name)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(u => u.Bio)
            .HasMaxLength(500);

        // For truly large content, use text type explicitly
        builder.Property(u => u.Notes)
            .HasColumnType("text");
    }
}
```
