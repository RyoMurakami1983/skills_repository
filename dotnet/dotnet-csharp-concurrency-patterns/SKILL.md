---
name: dotnet-csharp-concurrency-patterns
description: >
  Choose the right .NET concurrency abstraction — async/await, Channels, Akka.NET Streams,
  Reactive Extensions, or Akka.NET Actors. Use when deciding how to handle concurrent operations,
  evaluating concurrency tools, or managing state across multiple concurrent entities.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [csharp, concurrency, async-await, channels, akka-net, reactive-extensions]
  invocable: false
---

# .NET Concurrency: Choosing the Right Tool

Choose the right concurrency abstraction in .NET — from async/await for I/O to Channels for producer/consumer to Akka.NET for stateful entity management. Avoid locks and manual synchronization unless absolutely necessary.

**Acronyms**: I/O (Input/Output), CPU (Central Processing Unit), Rx (Reactive Extensions), DI (Dependency Injection), UI (User Interface).

## When to Use This Skill

- Deciding how to handle concurrent I/O-bound or CPU-bound operations in .NET applications
- Evaluating whether to use async/await, Channels, Akka.NET Streams, or Actors for a scenario
- Implementing producer/consumer patterns with backpressure and bounded buffering in C#
- Managing independent state for thousands of entities using the actor model pattern
- Designing server-side stream processing pipelines with batching, throttling, or merging
- Composing UI event streams with debouncing, throttling, or combining multiple sources

## Related Skills

| Skill | Scope | When |
|-------|-------|------|
| `dotnet-modern-csharp-coding-standards` | Records, pattern matching, Result\<T\> error handling | Writing new C# code |
| `dotnet-type-design-performance` | Span\<T\>, Memory\<T\>, zero-allocation patterns | Optimizing hot paths |
| `dotnet-project-structure` | Solution layout, namespace conventions, file organization | Structuring projects |

## Core Principles

1. **Start Simple, Escalate When Needed** — Use async/await by default. Only reach for Channels, Streams, or Actors when you have a concrete need that simpler tools cannot address cleanly.
2. **Avoid Shared Mutable State** — Immutable data, message passing, and isolated state (actors) eliminate entire categories of concurrency bugs. Redesign before reaching for locks.
3. **Use the Right Level of Abstraction** — Match the tool to the problem: I/O waits → async/await, work queues → Channels, stream processing → Akka.NET Streams, stateful entities → Actors.
4. **Prefer Message Passing Over Synchronization** — Channels and Actors serialize access through messages. Locks should be the last resort, reserved for low-level infrastructure code.
5. **Always Support Cancellation** — Accept `CancellationToken` in every async method. Cooperative cancellation is essential for responsive, well-behaved .NET applications.

> **Values**: 基礎と型の追求（async/await という基礎を徹底し、必要な時だけ高度な抽象へ段階的に進む）, ニュートラルな視点（ツールに偏らず、問題に応じて最適な抽象度を選択する）

## Workflow: Choose and Apply Concurrency Patterns

### Step 1: Use async/await for I/O Operations

Apply async/await as the default choice for all I/O-bound operations. Use `Task.WhenAll` for independent parallel operations. Why: async/await handles most concurrency needs without additional complexity.

```csharp
// Simple async I/O — always accept CancellationToken
public async Task<Order> GetOrderAsync(string orderId, CancellationToken ct)
{
    var order = await _database.GetAsync(orderId, ct);
    var customer = await _customerService.GetAsync(order.CustomerId, ct);
    return order with { Customer = customer };
}

// Parallel independent operations with Task.WhenAll
public async Task<Dashboard> LoadDashboardAsync(string userId, CancellationToken ct)
{
    var ordersTask = _orderService.GetRecentOrdersAsync(userId, ct);
    var notificationsTask = _notificationService.GetUnreadAsync(userId, ct);
    var statsTask = _statsService.GetUserStatsAsync(userId, ct);

    await Task.WhenAll(ordersTask, notificationsTask, statsTask);

    return new Dashboard(
        Orders: await ordersTask,
        Notifications: await notificationsTask,
        Stats: await statsTask);
}
```

**Key rules:** Always accept `CancellationToken`. Use `ConfigureAwait(false)` in library code. Never block on async code (no `.Result` or `.Wait()`).

> **Values**: 基礎と型の追求（async/await を基本の型として徹底し、すべての応用の土台とする）

### Step 2: Scale CPU Work with Parallel.ForEachAsync

Apply `Parallel.ForEachAsync` for CPU-bound parallel processing with controlled concurrency. Why: it combines async support with bounded parallelism, preventing thread pool starvation.

```csharp
public async Task ProcessOrdersAsync(IEnumerable<Order> orders, CancellationToken ct)
{
    await Parallel.ForEachAsync(
        orders,
        new ParallelOptions
        {
            MaxDegreeOfParallelism = Environment.ProcessorCount,
            CancellationToken = ct
        },
        async (order, token) =>
        {
            await ProcessOrderAsync(order, token);
        });
}
```

**Use when:** CPU-bound work across collections. **Avoid when:** pure I/O (async/await suffices), order matters, or you need backpressure.

> **Values**: 継続は力（並列処理の基本パターンを身につけ、日常的な処理の高速化に活かす）

### Step 3: Decouple with System.Threading.Channels

Apply `Channel<T>` for producer/consumer patterns, work queues, and decoupling component speeds. Use bounded channels for backpressure. Why: Channels provide thread-safe, lock-free communication between producers and consumers.

```csharp
public class OrderProcessor
{
    private readonly Channel<Order> _channel;

    public OrderProcessor()
    {
        // Bounded channel provides backpressure
        _channel = Channel.CreateBounded<Order>(new BoundedChannelOptions(100)
        {
            FullMode = BoundedChannelFullMode.Wait
        });
    }

    // Producer
    public async Task EnqueueOrderAsync(Order order, CancellationToken ct)
        => await _channel.Writer.WriteAsync(order, ct);

    // Consumer (run as background task)
    public async Task ProcessOrdersAsync(CancellationToken ct)
    {
        await foreach (var order in _channel.Reader.ReadAllAsync(ct))
        {
            await ProcessOrderAsync(order, ct);
        }
    }

    public void Complete() => _channel.Writer.Complete();
}
```

**Use when:** decoupling producer/consumer speeds, buffering work, fan-out to multiple workers. **Avoid when:** complex stream operations (batching, windowing) or stateful entity processing.

See [references/channel-patterns.md](references/channel-patterns.md) for multi-consumer worker pools and advanced patterns.

> **Values**: 成長の複利（Channel の習得がメッセージパッシングの理解を深め、Actor モデルへの橋渡しになる）

### Step 4: Process Streams with Akka.NET Streams or Rx

Apply Akka.NET Streams for server-side pipelines needing backpressure, batching, or throttling. Apply Reactive Extensions (Rx) for UI event composition. Why: these tools handle complex stream operations that Channels cannot express cleanly.

```csharp
using Akka.Streams;
using Akka.Streams.Dsl;

// Server-side: batching with timeout
public Source<IReadOnlyList<Event>, NotUsed> BatchEvents(
    Source<Event, NotUsed> events)
{
    return events
        .GroupedWithin(100, TimeSpan.FromSeconds(1))
        .Select(batch => batch.ToList() as IReadOnlyList<Event>);
}

// Client-side: search-as-you-type with Rx
public IObservable<IList<SearchResult>> CreateSearch(
    IObservable<string> searchText, ISearchService searchService)
{
    return searchText
        .Throttle(TimeSpan.FromMilliseconds(300))
        .DistinctUntilChanged()
        .Where(text => text.Length >= 3)
        .SelectMany(text => searchService.SearchAsync(text).ToObservable());
}
```

| Scenario | Rx | Akka.NET Streams |
|----------|----|--------------------|
| UI events (debounce, throttle) | ✅ Best choice | Overkill |
| Client-side composition | ✅ Best choice | Overkill |
| Server-side pipelines | Limited | ✅ Better backpressure |
| Distributed processing | ❌ Not designed for | ✅ Built for this |

See [references/stream-patterns.md](references/stream-patterns.md) for throttling, parallel processing, complex pipelines, and Rx examples.

> **Values**: 温故知新（Rx の成熟したイベント合成技術と Akka.NET の分散ストリーム処理を、用途に応じて使い分ける）

### Step 5: Manage Stateful Entities with Akka.NET Actors

Apply Akka.NET Actors when you need isolated state per entity, state machines with `Become()`, or distributed entity management. Why: actors provide natural isolation — each entity gets its own actor with no locks needed.

```csharp
// Entity-per-actor: each order has isolated state
public class OrderActor : ReceiveActor
{
    private OrderState _state;

    public OrderActor(string orderId)
    {
        _state = new OrderState(orderId);

        Receive<AddItem>(msg =>
        {
            _state = _state.AddItem(msg.Item);
            Sender.Tell(new ItemAdded(msg.Item));
        });

        Receive<Checkout>(msg =>
        {
            if (_state.CanCheckout)
            {
                _state = _state.Checkout();
                Sender.Tell(new CheckoutSucceeded(_state.Total));
            }
            else
            {
                Sender.Tell(new CheckoutFailed("Cart is empty"));
            }
        });

        Receive<GetState>(_ => Sender.Tell(_state));
    }
}
```

| Scenario | Why Actors? | Alternative |
|----------|-------------|-------------|
| Many entities with independent state | Natural isolation, no locks | ConcurrentDictionary + locks |
| State machines | `Become()` models transitions elegantly | Manual state enum |
| Supervision requirements | Parent actors restart children on failure | Try/catch + retry |
| Distributed systems | Cluster Sharding distributes across nodes | External orchestrator |

**The Actor Mindset:** Use when you have thousands of entities needing independent state, lifecycle behaviors, push-based updates, or fault isolation. If none of these apply, use simpler tools.

See [references/actor-patterns.md](references/actor-patterns.md) for state machines with Become, Cluster Sharding, and async local functions in actors.

> **Values**: 余白の設計（Actor の隔離境界が、各エンティティに独立した変更・障害の余白を与える）

## Good Practices

- Use async/await as the default concurrency tool for I/O operations
- Apply `CancellationToken` in every async method signature
- Use `ConfigureAwait(false)` in library code to avoid deadlocks
- Apply bounded `Channel<T>` for producer/consumer with backpressure
- Use async local functions instead of `Task.Run(async () => ...)` for clarity
- Avoid raw `List<T>` in parallel code; use `ConcurrentBag<T>` or `ConcurrentDictionary<K,V>`
- Use Rx for UI events (debounce, throttle) and Akka.NET Streams for server-side
- Consider actors when entities need independent state, lifecycle, or fault isolation

## Common Pitfalls

1. **Blocking on async** — Calling `.Result` or `.Wait()` causes deadlocks. Use `async` all the way through the call chain.
2. **Unbounded channels** — Using `Channel.CreateUnbounded<T>()` without considering memory. Use bounded channels with `BoundedChannelFullMode.Wait`.
3. **Over-engineering** — Reaching for Actors or Streams when async/await would suffice. Start simple and escalate only with concrete need.
4. **Manual thread creation** — Using `new Thread()` instead of `Task.Run` or higher abstractions. Let the thread pool manage threads.
5. **Shared mutable state in parallel loops** — Using `List<T>.Add()` inside `Parallel.ForEachAsync`. Use `ConcurrentBag<T>` instead.
6. **ContinueWith chains** — Using `.ContinueWith()` for sequencing instead of `await`. Async local functions are clearer and safer.

## Anti-Patterns

### ❌ Locks for Business Logic → ✅ Actor or Channel

```csharp
// ❌ BAD — locks to protect shared state
private readonly object _lock = new();
private Dictionary<string, Order> _orders = new();
public void UpdateOrder(string id, Action<Order> update)
{
    lock (_lock) { if (_orders.TryGetValue(id, out var order)) update(order); }
}
// ✅ GOOD — actor per entity, no locks needed
// Each order gets its own OrderActor with isolated state
```

### ❌ Blocking in Async Code → ✅ Async All the Way

```csharp
// ❌ BAD — deadlock risk
var result = GetDataAsync().Result;
// ✅ GOOD — async all the way
var result = await GetDataAsync();
```

### ❌ Shared Mutable Collections → ✅ Thread-Safe Alternatives

```csharp
// ❌ BAD — race condition in parallel loop
var results = new List<Result>();
await Parallel.ForEachAsync(items, async (item, ct) =>
{
    results.Add(await ProcessAsync(item, ct)); // Race condition!
});
// ✅ GOOD — use ConcurrentBag
var results = new ConcurrentBag<Result>();
```

### ❌ Manual Threads → ✅ Task-Based Abstractions

```csharp
// ❌ BAD — manual thread management
var thread = new Thread(() => ProcessOrders());
thread.Start();
// ✅ GOOD — task-based abstraction
_ = Task.Run(() => ProcessOrdersAsync(ct));
```

### ❌ Anonymous Async Lambda → ✅ Async Local Function

```csharp
// ❌ BAD — anonymous lambda obscures intent
_ = Task.Run(async () => { var r = await DoWorkAsync(); return new WorkCompleted(r); }).PipeTo(Self);
// ✅ GOOD — named async local function
async Task<WorkCompleted> ExecuteAsync()
{
    var result = await DoWorkAsync();
    return new WorkCompleted(result);
}
ExecuteAsync().PipeTo(Self);
```

## Quick Reference

### Decision Tree

```
What are you trying to do?
│
├─► Wait for I/O?                    → async/await
├─► Process collection in parallel?  → Parallel.ForEachAsync
├─► Producer/consumer work queue?    → Channel<T>
├─► UI event composition?            → Reactive Extensions (Rx)
├─► Server-side stream processing?   → Akka.NET Streams
├─► State machines / entity state?   → Akka.NET Actors
├─► Fire multiple async ops?         → Task.WhenAll
├─► Race multiple async ops?         → Task.WhenAny
└─► Periodic work?                   → PeriodicTimer
```

### Which Tool When

| Need | Tool | Example |
|------|------|---------|
| Wait for I/O | `async/await` | HTTP calls, database queries |
| Parallel CPU work | `Parallel.ForEachAsync` | Image processing, calculations |
| Work queue | `Channel<T>` | Background job processing |
| UI events | Reactive Extensions | Search-as-you-type, auto-save |
| Server-side batching | Akka.NET Streams | Event aggregation, rate limiting |
| State machines | Akka.NET Actors | Payment flows, order lifecycles |
| Entity management | Akka.NET Actors | Order state, user sessions |

### Escalation Path

```
async/await (start here)
    ├─► Need parallelism?            → Parallel.ForEachAsync
    ├─► Need producer/consumer?      → Channel<T>
    ├─► Need UI event composition?   → Reactive Extensions
    ├─► Need server-side streaming?  → Akka.NET Streams
    └─► Need stateful entities?      → Akka.NET Actors
```

## Resources

- [Async/Await Best Practices](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/)
- [System.Threading.Channels](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels)
- [Akka.NET Documentation](https://getakka.net/articles/intro/what-is-akka.html)
- [Reactive Extensions](https://github.com/dotnet/reactive)
- [references/channel-patterns.md](references/channel-patterns.md) — Multi-consumer pools, advanced Channel patterns
- [references/stream-patterns.md](references/stream-patterns.md) — Akka.NET Streams pipelines, Rx UI patterns
- [references/actor-patterns.md](references/actor-patterns.md) — Become state machines, Cluster Sharding, async local functions
