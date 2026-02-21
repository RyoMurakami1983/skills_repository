# Stream Patterns — Akka.NET Streams & Reactive Extensions

Reference material for `dotnet-csharp-concurrency-patterns` Step 4.

## Akka.NET Streams: Throttling

```csharp
using Akka.Streams;
using Akka.Streams.Dsl;

public Source<Request, NotUsed> ThrottleRequests(
    Source<Request, NotUsed> requests)
{
    return requests
        .Throttle(10, TimeSpan.FromSeconds(1), 5, ThrottleMode.Shaping);
}
```

## Akka.NET Streams: Parallel Processing with Order

```csharp
public Source<ProcessedItem, NotUsed> ProcessWithParallelism(
    Source<Item, NotUsed> items)
{
    return items
        .SelectAsync(4, async item => await ProcessAsync(item));
}
```

## Akka.NET Streams: Complex Pipeline

```csharp
public IRunnableGraph<Task<Done>> CreatePipeline(
    Source<RawEvent, NotUsed> events,
    Sink<ProcessedEvent, Task<Done>> sink)
{
    return events
        .Where(e => e.IsValid)
        .GroupedWithin(50, TimeSpan.FromMilliseconds(500))
        .SelectAsync(4, batch => ProcessBatchAsync(batch))
        .SelectMany(results => results)
        .ToMaterialized(sink, Keep.Right);
}
```

## Akka.NET Streams Strengths

- Batching with size AND time limits
- Throttling and rate limiting
- Backpressure that propagates through the entire pipeline
- Merging/splitting streams
- Parallel processing with ordering guarantees
- Error handling with supervision

## Reactive Extensions: UI Event Composition

```csharp
using System.Reactive.Linq;

// Combining multiple UI events
public IObservable<bool> CanSubmit =>
    Observable.CombineLatest(
        UsernameValid,
        PasswordValid,
        EmailValid,
        (user, pass, email) => user && pass && email);

// Double-click detection
public IObservable<Point> DoubleClicks =>
    MouseClicks
        .Buffer(TimeSpan.FromMilliseconds(300))
        .Where(clicks => clicks.Count >= 2)
        .Select(clicks => clicks.Last());

// Auto-save with debouncing
public IDisposable AutoSave =>
    DocumentChanges
        .Throttle(TimeSpan.FromSeconds(2))
        .Subscribe(async doc => await SaveAsync(doc));
```

## Rx Ideal Use Cases

- UI event composition (WPF, WinForms, MAUI, Blazor)
- Search-as-you-type with debouncing
- Combining multiple event sources
- Time-windowed operations in UI
- Drag-and-drop gesture detection
- Real-time data visualization

## Rx vs Akka.NET Streams

**Rule of thumb:** Rx for UI/client, Akka.NET Streams for server-side pipelines.
