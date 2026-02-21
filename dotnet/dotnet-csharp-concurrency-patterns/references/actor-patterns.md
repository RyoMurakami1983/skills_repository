# Actor Patterns — Akka.NET Advanced Examples

Reference material for `dotnet-csharp-concurrency-patterns` Step 5.

## State Machines with Become

Actors excel at implementing state machines using `Become()` to switch message handlers:

```csharp
public class PaymentActor : ReceiveActor
{
    private PaymentData _payment;

    public PaymentActor(string paymentId)
    {
        _payment = new PaymentData(paymentId);
        Pending();
    }

    private void Pending()
    {
        Receive<AuthorizePayment>(msg =>
        {
            _payment = _payment with { Amount = msg.Amount };
            Become(Authorizing);
            Self.Tell(new ProcessAuthorization());
        });

        Receive<CancelPayment>(_ =>
        {
            Become(Cancelled);
            Sender.Tell(new PaymentCancelled(_payment.Id));
        });
    }

    private void Authorizing()
    {
        Receive<ProcessAuthorization>(async _ =>
        {
            var result = await _gateway.AuthorizeAsync(_payment);
            if (result.Success)
            {
                _payment = _payment with { AuthCode = result.AuthCode };
                Become(Authorized);
            }
            else
            {
                Become(Failed);
            }
        });

        Receive<CancelPayment>(_ =>
        {
            Sender.Tell(new PaymentError("Cannot cancel during authorization"));
        });
    }

    private void Authorized()
    {
        Receive<CapturePayment>(_ =>
        {
            Become(Capturing);
            Self.Tell(new ProcessCapture());
        });

        Receive<VoidPayment>(_ =>
        {
            Become(Voiding);
            Self.Tell(new ProcessVoid());
        });
    }

    private void Capturing() { /* ... */ }
    private void Voiding() { /* ... */ }
    private void Cancelled() { /* Only responds to GetState */ }
    private void Failed() { /* Only responds to GetState, Retry */ }
}
```

## Distributed Entities with Cluster Sharding

```csharp
// Using Cluster Sharding for distributed entities
builder.WithShardRegion<OrderActor>(
    typeName: "orders",
    entityPropsFactory: (_, _, resolver) =>
        orderId => Props.Create(() => new OrderActor(orderId)),
    messageExtractor: new OrderMessageExtractor(),
    shardOptions: new ShardOptions());

// Send message to any order — sharding routes to correct node
var orderRegion = registry.Get<OrderActor>();
orderRegion.Tell(new ShardingEnvelope("order-123", new AddItem(item)));
```

## When to Use vs Not Use Actors

**Use Akka.NET Actors when you have:**

| Scenario | Why Actors? |
|----------|-------------|
| Many entities with independent state | Each entity gets its own actor — no locks |
| State machines | `Become()` models state transitions elegantly |
| Push-based/reactive updates | Actors naturally support tell-don't-ask |
| Supervision requirements | Parent actors supervise children, automatic restart |
| Distributed systems | Cluster Sharding distributes entities across nodes |
| Long-running workflows | Actors + persistence = durable workflows |
| Real-time systems | Message-driven, non-blocking by design |
| IoT / device management | Each device = one actor, scales to millions |

**Don't use Akka.NET when:**

| Scenario | Better Alternative |
|----------|-------------------|
| Simple work queue | `Channel<T>` |
| Request/response API | `async/await` |
| Batch processing | `Parallel.ForEachAsync` or Akka.NET Streams |
| UI event handling | Reactive Extensions |
| Shared state (single instance) | Service with `Channel` for serialization |
| CRUD operations | Standard async services |

## Async Local Functions in Actors

Use async local functions instead of `Task.Run(async () => ...)` when using `PipeTo`:

```csharp
private void HandleSync(StartSync cmd)
{
    async Task<SyncResult> PerformSyncAsync()
    {
        await using var scope = _scopeFactory.CreateAsyncScope();
        var service = scope.ServiceProvider.GetRequiredService<ISyncService>();
        var count = await service.SyncAsync(cmd.EntityId);
        return new SyncResult(cmd.EntityId, count);
    }

    PerformSyncAsync().PipeTo(Self);
}
```

| Benefit | Description |
|---------|-------------|
| **Readability** | Named functions are self-documenting |
| **Debugging** | Stack traces show meaningful names instead of `<>c__DisplayClass` |
| **Exception handling** | Cleaner try/catch without `AggregateException` unwrapping |
| **Scope clarity** | Local functions make captured variables explicit |
| **Testability** | Easier to extract and unit test the async logic |

## The Actor Mindset

Think of actors when your problem looks like:
- "I have **thousands** of [orders/users/devices] that need independent state"
- "Each [entity] goes through a **lifecycle** with different behaviors at each stage"
- "I need to **push updates** to interested parties when something changes"
- "If processing fails, I want to **restart** just that entity, not the whole system"
- "This needs to work across **multiple servers**"

If none of these apply, you probably don't need actors.
