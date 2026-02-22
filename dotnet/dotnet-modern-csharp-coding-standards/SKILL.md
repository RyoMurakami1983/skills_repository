---
name: dotnet-modern-csharp-coding-standards
description: >
  Write modern, high-performance C# code using records, pattern matching, composition,
  and Result-type error handling. Use when writing new C# code, designing APIs,
  or refactoring to C# 12+ idioms.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [csharp, coding-standards, modern-csharp, best-practices]
  invocable: false
---

# Modern C# Coding Standards

A concise guardrail for writing idiomatic, modern C# (12+). Covers data modelling with records, pattern matching, composition-first design, and railway-oriented error handling. Requires .NET 8+ and C# 12+. No external dependencies — uses only BCL (Base Class Library) types.

**Acronyms**: DTO (Data Transfer Object), API (Application Programming Interface), DI (Dependency Injection), BCL (Base Class Library), GC (Garbage Collector).

## When to Use This Skill

- Writing new C# code or refactoring existing code to modern idioms
- Designing domain models with strong typing and immutability
- Choosing between `record`, `record struct`, `class`, or `struct`
- Applying pattern matching for cleaner control flow
- Implementing error handling with `Result<T, TError>` instead of exceptions
- Reviewing C# code for anti-patterns (mutable DTOs, deep inheritance, reflection mapping)

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-type-design-performance` | Span\<T\>, Memory\<T\>, ArrayPool, zero-allocation patterns |
| `dotnet-csharp-api-design` | API parameter/return type contracts, method signatures |
| `dotnet-csharp-concurrency-patterns` | Async/await best practices, CancellationToken, IAsyncEnumerable |

## Core Principles

1. **Immutability by Default** — Use `record` types and `init`-only properties. Why: mutable state is the root cause of most concurrency and logic bugs.
2. **Type Safety** — Leverage nullable reference types, value objects as `readonly record struct`, and strongly-typed IDs. Why: catch errors at compile time instead of runtime.
3. **Modern Pattern Matching** — Replace `if`/`else` chains with `switch` expressions and relational/property/list patterns. Why: exhaustive matching prevents missed cases.
4. **Composition Over Inheritance** — Prefer interfaces + composition over abstract base classes. Why: flat structures are easier to test, extend, and reason about.
5. **Railway Error Handling + Explicit Mapping** — Use `Result<T, TError>` for expected errors; use explicit mapping methods instead of reflection-based libraries. Why: compile-time safety and visibility beat convenience.

> **Values**: 基礎と型の追求（最小形式で最大可能性を生む設計思想）, 温故知新（C# の進化を活かしつつ堅実な原則を守る）

## Workflow: Write Modern C#

### Step 1: Model Data with Records

Apply `record` for DTO types, messages, and domain entities. Apply `readonly record struct` for value objects. Choose the right type based on the decision guide below.

```csharp
// Immutable DTO
public record CustomerDto(string Id, string Name, string Email);

// Value object — always readonly record struct
public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
    public override string ToString() => Value.ToString();
}

// Value object with validation
public readonly record struct Money(decimal Amount, string Currency)
{
    public Money(decimal amount, string currency) : this(
        amount >= 0 ? amount : throw new ArgumentException("Amount cannot be negative"),
        currency is { Length: 3 } ? currency.ToUpperInvariant()
            : throw new ArgumentException("Currency must be 3-letter code"))
    { }
}
```

**Decision guide:**

| Type | When to use |
|------|-------------|
| `record class` | Entities, DTOs, aggregates with multiple properties |
| `readonly record struct` | Value objects, strongly-typed IDs, small immutable values |
| `class` | Mutable services, framework-required base classes |
| `struct` | Performance-critical, tiny data (≤16 bytes), no identity |

> ⚠️ **NO implicit conversions** on value objects — they defeat compile-time safety. See [references/language-patterns.md](references/language-patterns.md) for full examples.

> **Values**: 基礎と型の追求（型で不変条件を守り、コンパイラを味方にする）

### Step 2: Apply Pattern Matching & Nullable Types

Apply `switch` expressions for branching logic. Enable `<Nullable>enable</Nullable>` project-wide. Why: exhaustive pattern matching eliminates entire classes of bugs that `if`/`else` chains miss.

```csharp
// Switch expression with property patterns
public decimal CalculateDiscount(Order order) => order switch
{
    { Total: > 1000m } => order.Total * 0.15m,
    { Total: > 500m }  => order.Total * 0.10m,
    { Total: > 100m }  => order.Total * 0.05m,
    _ => 0m
};

// Relational + logical patterns
public string ClassifyTemperature(int temp) => temp switch
{
    < 0            => "Freezing",
    >= 0 and < 20  => "Cool",
    >= 20 and < 30 => "Warm",
    >= 30          => "Hot"
};

// Null-safe patterns
public decimal GetDiscount(Customer? customer) => customer switch
{
    null                   => 0m,
    { IsVip: true }        => 0.20m,
    { OrderCount: > 10 }   => 0.10m,
    _                      => 0.05m
};
```

See [references/language-patterns.md](references/language-patterns.md) for list patterns, tuple patterns, and nullable handling details.

> **Values**: 成長の複利（パターンマッチングの習得が、あらゆる分岐ロジックの品質を底上げする）

### Step 3: Prefer Composition Over Inheritance

```csharp
// ❌ Abstract base class hierarchy
public abstract class PaymentProcessor
{
    public abstract Task<PaymentResult> ProcessAsync(Money amount);
    protected async Task<bool> ValidateAsync(Money amount) { /* ... */ }
}

// ✅ Composition with interfaces
public interface IPaymentProcessor
{
    Task<PaymentResult> ProcessAsync(Money amount, CancellationToken ct);
}

public sealed class CreditCardProcessor(
    IPaymentValidator validator,
    ICreditCardGateway gateway) : IPaymentProcessor
{
    public async Task<PaymentResult> ProcessAsync(Money amount, CancellationToken ct)
    {
        var validation = await validator.ValidateAsync(amount, ct);
        if (!validation.IsValid)
            return PaymentResult.Failed(validation.Error);
        return await gateway.ChargeAsync(amount, ct);
    }
}
```

**When inheritance is acceptable:**
- Framework requirements (e.g., `ControllerBase` in ASP.NET Core)
- Library integration (e.g., custom exceptions from `Exception`)
- These should be **rare** in application code

> **Values**: 余白の設計（合成可能な小さな部品が、将来の変化に対応する余白を生む）

### Step 4: Handle Errors with Result Types

Apply `Result<T, TError>` for expected errors. Reserve exceptions for unexpected failures. Why: Result types make error paths explicit in the type system, preventing silent failures.

```csharp
// Error type
public readonly record struct OrderError(string Code, string Message);

// Service returning Result
public async Task<Result<Order, OrderError>> CreateOrderAsync(
    CreateOrderRequest request, CancellationToken ct)
{
    var validation = ValidateRequest(request);
    if (validation.IsFailure)
        return Result<Order, OrderError>.Failure(validation.Error);

    var order = new Order(OrderId.New(), new CustomerId(request.CustomerId), request.Items);
    await _repository.SaveAsync(order, ct);
    return Result<Order, OrderError>.Success(order);
}

// Pattern matching on Result
return result.Match(
    onSuccess: order => new OkObjectResult(order),
    onFailure: error => error.Code switch
    {
        "VALIDATION_ERROR" => new BadRequestObjectResult(error.Message),
        "NOT_FOUND"        => new NotFoundObjectResult(error.Message),
        _                  => new ObjectResult(error.Message) { StatusCode = 500 }
    });
```

| Situation | Use |
|-----------|-----|
| Validation failure, business rule violation, "not found" | `Result<T, TError>` |
| Network failure, null-ref, out-of-memory, programming bug | Exception |

See [references/error-handling-patterns.md](references/error-handling-patterns.md) for full `Result<T, TError>` implementation and railway composition.

> **Values**: ニュートラルな視点（例外と Result を状況に応じて使い分け、偏りのない設計を保つ）

### Step 5: Organize Code Files

Adopt a consistent namespace and file layout. Why: predictable structure accelerates code navigation and onboarding.

```
Domain/
  Orders/
    Order.cs          # Primary domain type + related records
    OrderService.cs   # Domain logic
    IOrderRepository.cs
```

**File ordering within a type file:**
1. Primary domain type (record/class)
2. Enums for state
3. Related records (items, events)
4. Value objects
5. Error types

```csharp
namespace MyApp.Domain.Orders;

// 1. Primary type
public record Order(OrderId Id, CustomerId CustomerId, Money Total, IReadOnlyList<OrderItem> Items)
{
    public bool IsCompleted => Status is OrderStatus.Completed;
}

// 2. Enum
public enum OrderStatus { Draft, Submitted, Processing, Completed, Cancelled }

// 3. Related record
public record OrderItem(ProductId ProductId, Quantity Quantity, Money UnitPrice)
{
    public Money Total => new(UnitPrice.Amount * Quantity.Value, UnitPrice.Currency);
}

// 4. Value object
public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
}

// 5. Error
public readonly record struct OrderError(string Code, string Message);
```

> **Values**: 継続は力（一貫したファイル構成が、日々のコードリーディングを高速化する）

## Good Practices

- ✅ Use `record` for DTOs, messages, and domain entities
- ✅ Use `readonly record struct` for value objects and strongly-typed IDs
- ✅ Leverage pattern matching with `switch` expressions over `if`/`else`
- ✅ Enable and respect nullable reference types (`<Nullable>enable</Nullable>`)
- ✅ Accept `CancellationToken` in all async methods
- ✅ Return `IReadOnlyList<T>` from APIs instead of `List<T>`
- ✅ Use `Result<T, TError>` for expected errors (validation, business rules)
- ✅ Prefer composition and interfaces over inheritance hierarchies
- ✅ Use explicit mapping methods instead of reflection-based mappers
- ✅ Use primary constructors (C# 12+) for simple service classes

## Common Pitfalls

1. **Blocking on async** — Calling `.Result` or `.Wait()` causes deadlocks. Use `async` all the way.
2. **Mutable DTOs** — Using `class` with `{ get; set; }` instead of `record`. Leads to accidental mutation.
3. **Implicit conversions on value objects** — `implicit operator` defeats compile-time type safety.
4. **Deep inheritance** — `Entity → AggregateRoot → Order → CustomerOrder`. Use flat composition instead.
5. **Swallowing nulls** — Ignoring nullable warnings instead of handling them with pattern matching.
6. **Throwing for expected errors** — Using exceptions for validation/not-found instead of `Result<T, TError>`.

## Anti-Patterns

### ❌ Mutable DTOs → ✅ Immutable Records

```csharp
// ❌ BAD
public class CustomerDto { public string Id { get; set; } public string Name { get; set; } }
// ✅ GOOD
public record CustomerDto(string Id, string Name);
```

### ❌ Class Value Objects → ✅ Readonly Record Structs

```csharp
// ❌ BAD — heap allocation, reference equality
public class OrderId { public string Value { get; } }
// ✅ GOOD — stack allocation, value equality
public readonly record struct OrderId(string Value);
```

### ❌ Deep Inheritance → ✅ Flat Composition

```csharp
// ❌ BAD
public abstract class Entity { }
public abstract class AggregateRoot : Entity { }
public class CustomerOrder : AggregateRoot { }
// ✅ GOOD
public interface IEntity { Guid Id { get; } }
public record Order(OrderId Id, CustomerId CustomerId) : IEntity { Guid IEntity.Id => Id.Value; }
```

### ❌ Reflection Mapping → ✅ Explicit Methods

```csharp
// ❌ BAD — runtime failure, hidden mapping
var dto = _mapper.Map<UserDto>(entity);
// ✅ GOOD — compile-time checked, debuggable
public static UserDto ToDto(this UserEntity e) => new(e.Id.ToString(), e.FullName, e.EmailAddress);
```

See [references/anti-reflection-patterns.md](references/anti-reflection-patterns.md) for details on source generators and UnsafeAccessor.

### ❌ Returning Mutable Collections

```csharp
// ❌ BAD — exposes internal list
public List<Order> GetOrders() => _orders;
// ✅ GOOD — read-only view
public IReadOnlyList<Order> GetOrders() => _orders;
```

### ❌ Blocking on Async

```csharp
// ❌ BAD — deadlock risk
public Order GetOrder(OrderId id) => GetOrderAsync(id).Result;
// ✅ GOOD — async all the way
public async Task<Order> GetOrderAsync(OrderId id, CancellationToken ct = default)
    => await _repository.GetAsync(id, ct);
```

## Quick Reference

### When to Use record vs class vs struct

| Need | Type | Reason |
|------|------|--------|
| DTO / message / event | `record` | Immutable, value equality, `with` support |
| Domain entity | `record` | Same + computed properties |
| Value object / typed ID | `readonly record struct` | Stack-allocated, value semantics |
| Mutable service with DI | `class` (sealed) | Needs mutable state / lifecycle |
| Tiny math data (≤16 bytes) | `struct` | Perf-critical, no identity |

### When to Use Result vs Exception

| Situation | Mechanism | Why |
|-----------|-----------|-----|
| Validation failure | `Result<T, TError>` | Expected, caller must handle |
| Business rule violation | `Result<T, TError>` | Part of normal flow |
| Entity not found | `Result<T, TError>` | Expected query outcome |
| Network / I/O failure | Exception | Unexpected, infrastructure error |
| Null reference / OOM | Exception | Programming bug / system error |

### File Ordering in a Type File

```
1. Primary domain type (record/class)
2. Enums
3. Related records
4. Value objects (readonly record struct)
5. Error types
```

## Resources

- [C# Language Reference](https://learn.microsoft.com/en-us/dotnet/csharp/)
- [Pattern Matching](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/functional/pattern-matching)
- [Nullable Reference Types](https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references)
- [references/language-patterns.md](references/language-patterns.md) — Full record, pattern matching, and nullable examples
- [references/error-handling-patterns.md](references/error-handling-patterns.md) — Result\<T, TError\> implementation and railway patterns
- [references/anti-reflection-patterns.md](references/anti-reflection-patterns.md) — Source generators, UnsafeAccessor, explicit mapping
