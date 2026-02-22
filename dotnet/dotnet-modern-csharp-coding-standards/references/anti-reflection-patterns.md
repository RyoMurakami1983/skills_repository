# Anti-Reflection Patterns — Detailed Reference

<!-- Parent skill: ../SKILL.md (dotnet-modern-csharp-coding-standards) -->

This file covers why reflection-based mapping should be avoided, how to use explicit mappings, source generators, and the `UnsafeAccessorAttribute` for legitimate low-level access.

---

## Banned Libraries

| Library | Problem |
|---------|---------|
| **AutoMapper** | Reflection magic, hidden mappings, runtime failures, hard to debug |
| **Mapster** | Same issues as AutoMapper |
| **ExpressMapper** | Same issues |

---

## Why Reflection Mapping Fails

```csharp
// With AutoMapper — compiles fine, fails at runtime
public record UserDto(string Id, string Name, string Email);
public record UserEntity(Guid Id, string FullName, string EmailAddress);

// This mapping silently produces garbage:
// - Id: string vs Guid mismatch
// - Name vs FullName: no match, null/default
// - Email vs EmailAddress: no match, null/default
var dto = _mapper.Map<UserDto>(entity);  // Compiles! Breaks at runtime.
```

---

## Use Explicit Mapping Methods Instead

```csharp
// Extension method — compile-time checked, easy to find, easy to debug
public static class UserMappings
{
    public static UserDto ToDto(this UserEntity entity) => new(
        Id: entity.Id.ToString(),
        Name: entity.FullName,
        Email: entity.EmailAddress);

    public static UserEntity ToEntity(this CreateUserRequest request) => new(
        Id: Guid.NewGuid(),
        FullName: request.Name,
        EmailAddress: request.Email);
}

// Usage — explicit and traceable
var dto = entity.ToDto();
var entity = request.ToEntity();
```

### Benefits of Explicit Mappings

| Aspect | AutoMapper | Explicit Methods |
|--------|------------|------------------|
| **Compile-time safety** | No — runtime errors | Yes — compiler catches mismatches |
| **Discoverability** | Hidden in profiles | "Go to Definition" works |
| **Debugging** | Black box | Step through code |
| **Refactoring** | Rename breaks silently | IDE renames correctly |
| **Performance** | Reflection overhead | Direct property access |
| **Testing** | Need integration tests | Simple unit tests |

### Complex Mappings

For complex transformations, explicit code is even more valuable:

```csharp
public static OrderSummaryDto ToSummary(this Order order) => new(
    OrderId: order.Id.Value.ToString(),
    CustomerName: order.Customer.FullName,
    ItemCount: order.Items.Count,
    Total: order.Items.Sum(i => i.Quantity * i.UnitPrice),
    Status: order.Status switch
    {
        OrderStatus.Pending   => "Awaiting Payment",
        OrderStatus.Paid      => "Processing",
        OrderStatus.Shipped   => "On the Way",
        OrderStatus.Delivered => "Completed",
        _                     => "Unknown"
    },
    FormattedDate: order.CreatedAt.ToString("MMMM d, yyyy"));
```

This is:
- **Readable**: Anyone can understand the transformation
- **Debuggable**: Set a breakpoint, inspect values
- **Testable**: Pass an Order, assert on the result
- **Refactorable**: Change a property name, compiler tells you everywhere it's used

---

## When Reflection is Acceptable

| Use Case | Acceptable? |
|----------|-------------|
| Serialization (System.Text.Json, Newtonsoft) | Yes — well-tested, source generators available |
| Dependency injection container | Yes — framework infrastructure |
| ORM entity mapping (EF Core) | Yes — necessary for database abstraction |
| Test fixtures and builders | Sometimes — for convenience in tests only |
| **DTO / domain object mapping** | **No — use explicit methods** |

---

## Source Generators vs Reflection

For scenarios where you need dynamic behavior, prefer source generators over runtime reflection:

```csharp
// System.Text.Json source generator — AOT-friendly, zero reflection
[JsonSerializable(typeof(OrderDto))]
[JsonSerializable(typeof(CustomerDto))]
public partial class AppJsonContext : JsonSerializerContext { }

// Usage
var json = JsonSerializer.Serialize(order, AppJsonContext.Default.OrderDto);
var dto = JsonSerializer.Deserialize(json, AppJsonContext.Default.OrderDto);
```

Source generators provide:
- **Compile-time code generation** — no runtime reflection
- **AOT compatibility** — works with NativeAOT trimming
- **Better performance** — no reflection overhead
- **Compile-time errors** — mismatches caught at build time

---

## UnsafeAccessorAttribute (.NET 8+)

When you genuinely need to access private or internal members (serializers, test helpers, framework code), use `UnsafeAccessorAttribute` instead of traditional reflection. It provides **zero-overhead, AOT-compatible** member access.

```csharp
// ❌ AVOID: Traditional reflection — slow, allocates, breaks AOT
var field = typeof(Order).GetField("_status", BindingFlags.NonPublic | BindingFlags.Instance);
var status = (OrderStatus)field!.GetValue(order)!;

// ✅ PREFER: UnsafeAccessor — zero overhead, AOT-compatible
[UnsafeAccessor(UnsafeAccessorKind.Field, Name = "_status")]
static extern ref OrderStatus GetStatusField(Order order);

var status = GetStatusField(order);  // Direct access, no reflection
```

### Supported Accessor Kinds

```csharp
// Private field access
[UnsafeAccessor(UnsafeAccessorKind.Field, Name = "_items")]
static extern ref List<OrderItem> GetItemsField(Order order);

// Private method access
[UnsafeAccessor(UnsafeAccessorKind.Method, Name = "Recalculate")]
static extern void CallRecalculate(Order order);

// Private static field
[UnsafeAccessor(UnsafeAccessorKind.StaticField, Name = "_instanceCount")]
static extern ref int GetInstanceCount(Order order);

// Private constructor
[UnsafeAccessor(UnsafeAccessorKind.Constructor)]
static extern Order CreateOrder(OrderId id, CustomerId customerId);
```

### Why UnsafeAccessor Over Reflection

| Aspect | Reflection | UnsafeAccessor |
|--------|------------|----------------|
| Performance | Slow (100–1000×) | Zero overhead |
| AOT compatible | No | Yes |
| Allocations | Yes (boxing, arrays) | None |
| Compile-time checked | No | Partially (signature) |

### Use Cases

- Serializers accessing private backing fields
- Test helpers verifying internal state
- Framework code that needs to bypass visibility

### Resources

- [A new way of doing reflection with .NET 8](https://steven-giesel.com/blogPost/05ecdd16-8dc4-490f-b1cf-780c994346a4)
- [Accessing private members without reflection in .NET 8.0](https://www.strathweb.com/2023/10/accessing-private-members-without-reflection-in-net-8-0/)
- [Modern .NET Reflection with UnsafeAccessor](https://blog.ndepend.com/modern-net-reflection-with-unsafeaccessor/)
