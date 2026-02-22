---
name: dotnet-type-design-performance
description: >
  Design .NET types for performance with sealed classes, readonly structs,
  static functions, deferred enumeration, and immutable collections.
  Use when designing new types, reviewing performance, or choosing between class/struct/record.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, csharp, performance, type-design, sealed, readonly-struct, collections]
  invocable: false
---

# Design Types for Performance in .NET

Practical patterns for designing .NET types that maximize JIT optimization, minimize allocations, and communicate clear API intent. Covers sealing, value types, pure functions, deferred enumeration, and collection return types.

## When to Use This Skill

Use this skill when:
- Designing new types and choosing between class, struct, and record types
- Reviewing existing code for performance improvement opportunities in hot paths
- Working with collections and enumerables that require deferred materialization
- Establishing type design conventions for a .NET project across the team
- Choosing the right async return type between Task and ValueTask for APIs

Prerequisites: .NET 6+ project with basic understanding of C# type system (class, struct, record).

---

## Related Skills

- **`dotnet-generic-matching`** — Uses readonly structs and immutable collections for matching results
- **`tdd-standard-practice`** — Test performance-critical code with Red-Green-Refactor
- **`git-commit-practices`** — Commit each refactoring step as an atomic change

---

## Core Principles

1. **Seal by Default** — Unless explicitly designed for inheritance, seal your types to enable JIT devirtualization (基礎と型)
2. **Value Semantics for Small Data** — Use readonly structs for small, immutable data to avoid heap allocations (基礎と型)
3. **Explicit Dependencies** — Prefer static pure functions that make all inputs visible (ニュートラル)
4. **Defer Materialization** — Don't enumerate until you must; let the caller decide when to materialize (余白の設計)
5. **Immutable API Boundaries** — Return `IReadOnlyList<T>` from public APIs to prevent unintended mutation (成長の複利)

---

## Workflow: Design Types for Performance

### Step 1 — Seal Classes by Default

Use when creating new classes or records not designed for inheritance.

Sealing enables JIT (Just-In-Time) devirtualization — the compiler can inline method calls instead of using vtable lookups.

```csharp
// DO: Seal classes not designed for inheritance
public sealed class OrderProcessor
{
    public void Process(Order order) { /* ... */ }
}

// DO: Seal records (they're classes underneath)
public sealed record OrderCreated(OrderId Id, CustomerId CustomerId);
```

```csharp
// DON'T: Leave unsealed without reason
public class OrderProcessor  // Can be subclassed — intentional?
{
    public virtual void Process(Order order) { }  // Virtual = slower
}
```

**Why seal?** The JIT compiler can devirtualize sealed method calls, producing faster execution. Sealing also communicates "this is not an extension point" and prevents accidental breaking changes from subclassing.

> **Values**: 基礎と型（型を明示することで意図が伝わり、JITが最適化できる）

### Step 2 — Use Readonly Structs for Value Types

Use when defining small, immutable data types with value semantics.

Mark structs `readonly` to prevent defensive copies when passed by `in` reference or stored in readonly fields.

```csharp
// DO: Readonly record struct for identifiers
public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
    public override string ToString() => Value.ToString();
}

// DO: Readonly struct for small value objects
public readonly struct Money
{
    public decimal Amount { get; }
    public string Currency { get; }

    public Money(decimal amount, string currency)
    {
        Amount = amount;
        Currency = currency;
    }
}
```

```csharp
// DON'T: Mutable struct (causes defensive copies)
public struct Point  // Not readonly!
{
    public int X { get; set; }  // Mutable = defensive copies
    public int Y { get; set; }
}
```

**Why readonly?** The compiler creates hidden defensive copies for non-readonly structs in readonly contexts, silently doubling memory usage.

| Criteria | Use Struct | Use Class |
|----------|------------|-----------|
| Size | Small (≤ 16 bytes) | Larger objects |
| Lifetime | Short-lived | Long-lived / shared references |
| Semantics | Value semantics | Identity semantics |
| Mutability | Immutable | Mutable state needed |

> **Values**: 基礎と型（正しい型選択が防御コピーを排除し、性能の基盤となる）

### Step 3 — Prefer Static Pure Functions

Use when writing logic that transforms inputs without side effects.

Static methods with no hidden state are faster (no vtable lookup), inherently thread-safe, and easier to test.

```csharp
// DO: Static pure function — all dependencies explicit
public static class OrderCalculator
{
    public static Money CalculateTotal(
        IReadOnlyList<OrderItem> items,
        decimal taxRate,
        decimal discountPercent)
    {
        var subtotal = items.Sum(i => i.Price * i.Quantity);
        var discounted = subtotal * (1 - discountPercent / 100);
        var total = discounted * (1 + taxRate / 100);
        return new Money(total, "USD");
    }
}
```

```csharp
// DON'T: Instance method hiding dependencies
public class OrderCalculator
{
    private readonly ITaxService _taxService;          // Hidden
    private readonly IDiscountService _discountService; // Hidden

    public Money CalculateTotal(IReadOnlyList<OrderItem> items)
    {
        // What does this actually depend on? Unclear.
    }
}
```

**Why static?** Static pure functions have no vtable lookup, are inherently thread-safe, and force explicit dependencies. Use instance methods only when you genuinely need polymorphism or the object manages meaningful state.

> **Values**: ニュートラル（依存を隠さず明示することで、誰でも理解できる普遍的な設計になる）

### Step 4 — Defer Enumeration

Use when working with LINQ queries and collection pipelines.

Don't materialize enumerables until necessary. Chain operations first, then call `.ToList()` once at the end. Why? Each intermediate `.ToList()` allocates a new list and iterates the entire sequence unnecessarily.

```csharp
// DON'T: Multiple materializations
public IReadOnlyList<Order> GetActiveOrders()
{
    return _orders
        .Where(o => o.IsActive)
        .ToList()                    // Materialized here!
        .OrderBy(o => o.CreatedAt)
        .ToList();                   // Materialized again!
}

// DO: Single materialization at the end
public IReadOnlyList<Order> GetActiveOrders()
{
    return _orders
        .Where(o => o.IsActive)
        .OrderBy(o => o.CreatedAt)
        .ToList();  // Single materialization
}

// DO: Return IEnumerable if caller might not need all items
public IEnumerable<Order> GetActiveOrders()
{
    return _orders
        .Where(o => o.IsActive)
        .OrderBy(o => o.CreatedAt);
    // Caller decides when to materialize
}
```

> **Values**: 余白の設計（列挙を遅延させることで、呼び出し側に判断の余白を残す）

### Step 5 — Choose Collection Return Types

Use when defining public API return types for collections.

Return immutable collection interfaces from public APIs. Use mutable types internally during construction.

```csharp
// DO: Return immutable collection from API
public IReadOnlyList<Order> GetOrders()
{
    return _orders.ToList();  // Caller can't modify internal state
}

// DO: Use FrozenDictionary for static lookup data (.NET 8+)
private static readonly FrozenDictionary<string, Handler> _handlers =
    new Dictionary<string, Handler>
    {
        ["create"] = new CreateHandler(),
        ["update"] = new UpdateHandler(),
    }.ToFrozenDictionary();
```

```csharp
// DON'T: Return mutable collection from public API
public List<Order> GetOrders()
{
    return _orders;  // Caller can modify your internal state!
}
```

**Why immutable returns?** Exposing mutable collections lets callers corrupt your internal state. Immutable APIs build long-term reliability.

| Scenario | Return Type | Reason |
|----------|-------------|--------|
| API boundary | `IReadOnlyList<T>` | Prevent caller mutation |
| Static lookup data | `FrozenDictionary<K,V>` | Fastest read performance |
| Internal building | `List<T>` → return readonly | Mutable during construction only |
| Single item or none | `T?` (nullable) | Avoid wrapper allocations |
| Zero or more, lazy | `IEnumerable<T>` | Defer materialization |

> **Values**: 成長の複利（不変なAPIは変更に強く、長期的な信頼性を積み上げる）

---

## Good Practices

### 1. Seal New Classes by Default

- Apply `sealed` on every new class from the start
- Avoid removing `sealed` unless a concrete inheritance need is identified
- Consider sealing records as well since they are reference types underneath

### 2. Prefer readonly record struct for IDs

- Use `readonly record struct` for domain identifiers (`OrderId`, `CustomerId`)
- Avoid plain `struct` for identifiers since it lacks built-in value equality
- Define a static factory method (`New()`) for consistent construction

### 3. Single ToList at Pipeline End

- Avoid intermediate `.ToList()` calls between LINQ (Language Integrated Query) operations
- Use a single `.ToList()` at the end of the pipeline to minimize allocations
- Consider returning `IEnumerable<T>` when the caller may not need all items

### 4. Use ValueTask for Cached Hot Paths

- Use `ValueTask<T>` for methods that often return synchronously (e.g., cache hit)
- Avoid `ValueTask` for always-async I/O operations — use `Task<T>` instead
- Apply caution: never await a `ValueTask` more than once. See [Advanced Patterns](references/advanced-performance-patterns.md)

---

## Common Pitfalls

### 1. Mutable Structs Causing Defensive Copies

When a non-readonly struct is stored in a `readonly` field or passed by `in`, the compiler creates a hidden copy to prevent mutation. This silently doubles memory usage.

**Solution**: Always mark structs `readonly` unless mutation is intentionally required.

### 2. Returning List&lt;T&gt; from Public APIs

Exposing `List<T>` allows callers to `Add()`, `Remove()`, or `Clear()` your internal collection, breaking encapsulation.

**Solution**: Return `IReadOnlyList<T>` or `IReadOnlyCollection<T>`.

### 3. Premature Enumeration in Async Pipelines

Using `.Select(async o => await ProcessAsync(o)).ToList()` creates one `Task` per item and materializes immediately.

**Solution**: Use `IAsyncEnumerable<T>` for streaming or `Task.WhenAll` for batched parallelism. See [Advanced Patterns](references/advanced-performance-patterns.md).

---

## Anti-Patterns

```csharp
// ❌ Unsealed class without reason
public class OrderService { }  // → Add sealed

// ❌ Mutable struct
public struct Point { public int X; public int Y; }  // → Make readonly

// ❌ Instance method that could be static
public int Add(int a, int b) => a + b;  // → Make static

// ❌ Multiple ToList() calls
items.Where(...).ToList().OrderBy(...).ToList();  // → Single ToList at end

// ❌ Return mutable collection from API
public List<Order> GetOrders();  // → IReadOnlyList<T>

// ❌ ValueTask for always-async operations
public ValueTask<Order> CreateOrderAsync();  // → Use Task
```

---

## Quick Reference

| Pattern | Benefit | Why It Matters |
|---------|---------|----------------|
| `sealed class` | Devirtualization, clear API intent | JIT inlines calls |
| `readonly record struct` | No defensive copies, value semantics | Compiler skips copies |
| Static pure functions | No vtable, testable, thread-safe | All inputs visible |
| Defer `.ToList()` | Single materialization, less allocation | Avoid duplicate iteration |
| `ValueTask` for hot paths | Avoid Task allocation when often synchronous | Zero-alloc sync path |
| `Span<T>` for bytes | Stack allocation, no copying | No heap pressure |
| `IReadOnlyList<T>` return | Immutable API contract | Prevents state corruption |
| `FrozenDictionary` | Fastest lookup for static data (.NET 8+) | Optimized hash layout |

---

## Resources

- **Performance Best Practices**: https://learn.microsoft.com/en-us/dotnet/standard/performance/
- **Sealed Classes**: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/sealed
- **Span&lt;T&gt; Guidance**: https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/
- **Frozen Collections**: https://learn.microsoft.com/en-us/dotnet/api/system.collections.frozen
- **Advanced Patterns**: [ValueTask, Span, and Async Enumeration](references/advanced-performance-patterns.md)
