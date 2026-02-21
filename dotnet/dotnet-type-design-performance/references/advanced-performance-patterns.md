# Advanced Performance Patterns

Extended patterns for `dotnet-type-design-performance`. These topics complement the main workflow steps.

## ValueTask vs Task

Use `ValueTask` for hot paths that often complete synchronously. For real I/O, just use `Task`.

```csharp
// DO: ValueTask for cached/synchronous paths
public ValueTask<User?> GetUserAsync(UserId id)
{
    if (_cache.TryGetValue(id, out var user))
    {
        return ValueTask.FromResult<User?>(user);  // No allocation
    }

    return new ValueTask<User?>(FetchUserAsync(id));
}

// DO: Task for real I/O (simpler, no footguns)
public Task<Order> CreateOrderAsync(CreateOrderCommand cmd)
{
    // This always hits the database
    return _repository.CreateAsync(cmd);
}
```

**ValueTask rules**:
- Never await a ValueTask more than once
- Never use `.Result` or `.GetAwaiter().GetResult()` before completion
- If in doubt, use Task

## Span&lt;T&gt; and Memory&lt;T&gt;

Use `Span<T>` and `Memory<T>` instead of `byte[]` for low-level operations.

```csharp
// DO: Accept Span for synchronous operations
public static int ParseInt(ReadOnlySpan<char> text)
{
    return int.Parse(text);
}

// DO: Accept Memory for async operations
public async Task WriteAsync(ReadOnlyMemory<byte> data)
{
    await _stream.WriteAsync(data);
}

// DON'T: Force array allocation
public static int ParseInt(string text)  // String allocated
{
    return int.Parse(text);
}
```

### Common Span Patterns

```csharp
// Slice without allocation
ReadOnlySpan<char> span = "Hello, World!".AsSpan();
var hello = span[..5];  // No allocation

// Stack allocation for small buffers
Span<byte> buffer = stackalloc byte[256];

// Use ArrayPool for larger buffers
var buffer = ArrayPool<byte>.Shared.Rent(4096);
try
{
    // Use buffer...
}
finally
{
    ArrayPool<byte>.Shared.Return(buffer);
}
```

## Async Enumeration

Be careful with async and IEnumerable:

```csharp
// DON'T: Async in LINQ — hidden allocations
var results = orders
    .Select(async o => await ProcessOrderAsync(o))  // Task per item!
    .ToList();
await Task.WhenAll(results);

// DO: Use IAsyncEnumerable for streaming
public async IAsyncEnumerable<OrderResult> ProcessOrdersAsync(
    IEnumerable<Order> orders,
    [EnumeratorCancellation] CancellationToken ct = default)
{
    foreach (var order in orders)
    {
        ct.ThrowIfCancellationRequested();
        yield return await ProcessOrderAsync(order, ct);
    }
}

// DO: Batch processing for parallelism
var results = await Task.WhenAll(
    orders.Select(o => ProcessOrderAsync(o)));
```
