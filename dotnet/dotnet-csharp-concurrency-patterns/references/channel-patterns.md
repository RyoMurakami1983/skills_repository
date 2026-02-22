# Channel Patterns — Advanced Examples

Reference material for `dotnet-csharp-concurrency-patterns` Step 3.

## Multi-Consumer Worker Pool

```csharp
public class WorkerPool
{
    private readonly Channel<WorkItem> _channel;
    private readonly List<Task> _workers = new();

    public WorkerPool(int workerCount)
    {
        _channel = Channel.CreateUnbounded<WorkItem>();

        for (int i = 0; i < workerCount; i++)
        {
            _workers.Add(Task.Run(() => ConsumeAsync()));
        }
    }

    private async Task ConsumeAsync()
    {
        await foreach (var item in _channel.Reader.ReadAllAsync())
        {
            await ProcessAsync(item);
        }
    }

    public ValueTask EnqueueAsync(WorkItem item)
        => _channel.Writer.WriteAsync(item);
}
```

## When to Use Channels

**Good for:**
- Decoupling producer speed from consumer speed
- Buffering work with backpressure
- Simple fan-out to multiple workers
- Background processing queues

**Not good for:**
- Complex stream operations (batching, windowing, merging)
- Stateful processing per entity
- Sophisticated error handling/supervision
