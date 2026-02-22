---
name: dotnet-serialization
description: >
  Choose the right serialization format for .NET applications and implement it safely.
  Use when selecting serialization for APIs, messaging, or persistence, migrating from
  Newtonsoft.Json, or implementing AOT-compatible serialization with source generators.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, serialization, json, protobuf, messagepack, aot, system-text-json]
  invocable: false
---

# Serialization in .NET

Select, implement, and evolve serialization formats for .NET applications — from REST APIs and gRPC to actor messaging and event sourcing. Covers System.Text.Json source generators, Protocol Buffers, MessagePack, migration from Newtonsoft.Json, and wire compatibility patterns.

## When to Use This Skill

- Choosing a serialization format for REST APIs, gRPC services, or actor messaging systems
- Implementing AOT-compatible JSON serialization with System.Text.Json source generators
- Migrating an existing codebase from Newtonsoft.Json to System.Text.Json step by step
- Designing wire formats for distributed systems that must evolve without breaking readers
- Implementing Protocol Buffers or MessagePack for high-performance binary serialization
- Configuring serialization bindings for Akka.NET actor systems with schema-based formats
- Optimizing serialization throughput and payload size on performance-critical hot paths

---

## Related Skills

- **`dotnet-project-structure`** — NuGet package management and Directory.Build.props setup
- **`dotnet-type-design-performance`** — Sealed classes, readonly structs, and record types
- **`dotnet-csharp-concurrency-patterns`** — Async patterns for serialization in concurrent systems
- **`dotnet-extensions-dependency-injection`** — Registering serializer contexts in DI containers

---

## Core Principles

1. **Schema Over Reflection** — Use schema-based serialization (Protobuf, MessagePack, source-gen JSON) instead of reflection-based approaches for safety, performance, and AOT compatibility（基礎と型）
2. **Explicit Wire Contracts** — Define field numbers, property names, and discriminators explicitly; never embed .NET type names in serialized payloads（温故知新）
3. **Read Before Write** — Deploy deserializers for new formats before serializers to ensure backward compatibility during rolling upgrades（余白の設計）
4. **Tolerant Reader** — Consumers must safely ignore unknown fields so producers can add new data without breaking existing readers（ニュートラルな視点）
5. **Compile-Time Verification** — Prefer source generators and compile-time contracts over runtime discovery to catch serialization errors early（基礎と型）

---

## Workflow: Choose and Implement .NET Serialization

### Step 1 — Evaluate Serialization Requirements

Use when starting a new service or feature that sends data across process boundaries.

Classify your scenario to determine the right format:

| Scenario | Human-Readable? | Versioning Need | Performance | Recommended |
|----------|-----------------|-----------------|-------------|-------------|
| REST API | ✅ Yes | Medium | Medium | System.Text.Json (source gen) |
| gRPC | No | High | High | Protocol Buffers |
| Actor messaging | No | High | Very High | MessagePack or Protobuf |
| Event sourcing | No | Critical | High | Protobuf or MessagePack |
| Caching | No | Low | Very High | MessagePack |
| Configuration | ✅ Yes | Low | Low | JSON (System.Text.Json) |

**Why classify first**: The wrong format creates technical debt that compounds — migrating wire formats in production systems with stored data is extremely costly.

> **Values**: 基礎と型の追求（requirements analysis is the foundation of every design decision）

### Step 2 — Implement System.Text.Json with Source Generators

Use when building REST APIs or any JSON scenario that requires AOT compatibility.

Define a `JsonSerializerContext` with all serializable types:

```csharp
using System.Text.Json;
using System.Text.Json.Serialization;

// Register all types for source generation
[JsonSerializable(typeof(Order))]
[JsonSerializable(typeof(OrderItem))]
[JsonSerializable(typeof(List<Order>))]
[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
public partial class AppJsonContext : JsonSerializerContext { }
```

Serialize and deserialize using the generated context:

```csharp
// ✅ Serialize with source-gen context — no reflection
var json = JsonSerializer.Serialize(order, AppJsonContext.Default.Order);

// ✅ Deserialize with source-gen context
var order = JsonSerializer.Deserialize(json, AppJsonContext.Default.Order);
```

Register the context in ASP.NET Core:

```csharp
// Wire into ASP.NET Core pipeline
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.TypeInfoResolverChain.Insert(0, AppJsonContext.Default);
});
```

**Why source generators**: No reflection at runtime, AOT compatible, faster serialization, and trim-safe — the linker knows exactly what code is needed.

> **Values**: 基礎と型（source generators replace runtime magic with compile-time certainty）

### Step 3 — Implement Protocol Buffers for Versioned Wire Formats

Use when designing gRPC services, actor messages, or event-sourced systems that must evolve safely.

Install packages:

```bash
dotnet add package Google.Protobuf
dotnet add package Grpc.Tools
```

Define the schema with explicit field numbers:

```protobuf
// orders.proto
syntax = "proto3";

message Order {
    string id = 1;
    string customer_id = 2;
    repeated OrderItem items = 3;
    int64 created_at_ticks = 4;
    string notes = 5;  // Added in v2 — old readers ignore it
}

message OrderItem {
    string product_id = 1;
    int32 quantity = 2;
    int64 price_cents = 3;
}
```

Follow versioning rules strictly:

| Operation | Safe? | Why |
|-----------|-------|-----|
| Add new field with new number | ✅ Yes | Old readers skip unknown fields |
| Remove field, reserve number | ✅ Yes | `reserved 2;` prevents reuse |
| Change field type | ❌ No | Binary encoding is incompatible |
| Reuse a field number | ❌ No | Old data decodes incorrectly |

> **Values**: 温故知新（Protobuf's field-number design has decades of proven stability）

### Step 4 — Implement MessagePack for High-Performance Scenarios

Use when compact payloads and maximum throughput matter — actor messaging, caching, real-time systems.

Install packages:

```bash
dotnet add package MessagePack
dotnet add package MessagePack.Annotations
```

Define contracts with explicit key indices:

```csharp
using MessagePack;

[MessagePackObject]
public sealed class Order
{
    [Key(0)] public required string Id { get; init; }
    [Key(1)] public required string CustomerId { get; init; }
    [Key(2)] public required IReadOnlyList<OrderItem> Items { get; init; }
    [Key(3)] public required DateTimeOffset CreatedAt { get; init; }
    [Key(4)] public string? Notes { get; init; }  // v2 — old readers skip
}

// ✅ Serialize/deserialize — compact binary format
var bytes = MessagePackSerializer.Serialize(order);
var order = MessagePackSerializer.Deserialize<Order>(bytes);
```

For AOT compatibility, use the source generator:

```csharp
[MessagePackObject]
public partial class Order { }  // partial enables source gen

var options = MessagePackSerializerOptions.Standard
    .WithResolver(CompositeResolver.Create(
        GeneratedResolver.Instance,
        StandardResolver.Instance));
```

**Why MessagePack**: 2-5× faster than JSON with 30-50% smaller payloads — significant for high-throughput actor systems.

> **Values**: 継続は力（performance gains compound across every message in a high-throughput system）

### Step 5 — Ensure Wire Compatibility Across Versions

Use when deploying new serialization formats in a rolling-upgrade environment.

**Tolerant Reader** — configure consumers to ignore unknown fields:

```csharp
// System.Text.Json: skip unmapped members
var options = new JsonSerializerOptions
{
    UnmappedMemberHandling = JsonUnmappedMemberHandling.Skip
};
// Protobuf/MessagePack: automatic — unknown fields are skipped by design
```

**Read Before Write** — deploy deserializers before serializers:

```csharp
// Phase 1: Deploy readers for V2 everywhere
public Order Deserialize(byte[] data, string manifest) => manifest switch
{
    "Order.V1" => DeserializeV1(data),
    "Order.V2" => DeserializeV2(data),  // NEW — can read V2
    _ => throw new NotSupportedException($"Unknown manifest: {manifest}")
};

// Phase 2: Enable V2 writers (next release, after all nodes read V2)
public (byte[] data, string manifest) Serialize(Order order) =>
    _useV2Format
        ? (SerializeV2(order), "Order.V2")
        : (SerializeV1(order), "Order.V1");
```

**Never embed type names** in wire payloads:

```csharp
// ❌ Type name in payload — renaming class breaks wire format
{ "$type": "MyApp.Order, MyApp.Core", "id": "123" }

// ✅ Explicit discriminator — refactoring safe
{ "type": "order", "id": "123" }
```

> **Values**: 余白の設計（Read-Before-Write creates space for safe evolution）

### Step 6 — Migrate from Newtonsoft.Json to System.Text.Json

Use when replacing Newtonsoft.Json with System.Text.Json in an existing codebase.

Map the key differences:

| Newtonsoft | System.Text.Json | Fix |
|------------|------------------|-----|
| `JsonProperty` | `JsonPropertyName` | Different attribute |
| `$type` polymorphism | `[JsonDerivedType]` (.NET 7+) | Explicit discriminators |
| `DefaultValueHandling` | `DefaultIgnoreCondition` | Different API |
| Private setters | `[JsonInclude]` | Explicit opt-in |

Migrate model classes:

```csharp
// ❌ Newtonsoft (reflection-based)
public class Order
{
    [JsonProperty("order_id")]
    public string Id { get; set; }

    [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
    public string? Notes { get; set; }
}

// ✅ System.Text.Json (source-gen compatible)
public sealed record Order(
    [property: JsonPropertyName("order_id")] string Id,
    string? Notes
);

[JsonSerializable(typeof(Order))]
[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.SnakeCaseLower,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
public partial class OrderJsonContext : JsonSerializerContext { }
```

Implement polymorphism with discriminators (.NET 7+):

```csharp
// ✅ Explicit discriminator — type-safe, refactoring-safe
[JsonDerivedType(typeof(CreditCardPayment), "credit_card")]
[JsonDerivedType(typeof(BankTransferPayment), "bank_transfer")]
public abstract record Payment(decimal Amount);

public sealed record CreditCardPayment(decimal Amount, string Last4)
    : Payment(Amount);
public sealed record BankTransferPayment(decimal Amount, string AccountNumber)
    : Payment(Amount);
// Serializes as: { "$type": "credit_card", "amount": 100, "last4": "1234" }
```

> **Values**: 温故知新（migrate incrementally from legacy to modern without breaking existing consumers）

---

## Good Practices

- Use source generators for all System.Text.Json serialization — why: eliminates reflection overhead
- Use explicit field numbers (Protobuf `= N`, MessagePack `[Key(N)]`) for version safety
- Use `sealed record` types for immutable message contracts — why: prevents accidental mutation
- Avoid embedding .NET type names in wire payloads — why: class renames break deserialization
- Reserve removed field numbers (`reserved 2;`) — why: prevents accidental reuse across versions
- Deploy deserializers before serializers for new wire format versions
- Configure `UnmappedMemberHandling.Skip` so consumers tolerate unknown fields

---

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Missing source-gen context | Falls back to reflection, breaks AOT | Add all types to `[JsonSerializable]` |
| Reusing Protobuf field numbers | Old data decodes as wrong type | Use `reserved` for removed fields |
| Embedding .NET type names | Class rename breaks wire format | Use explicit string discriminators |
| Deploying writer before reader | Old nodes cannot parse new format | Always deploy readers first |
| Using `BinaryFormatter` | Security vulnerability (CVE), deprecated | Replace with MessagePack or Protobuf |

---

## Anti-Patterns

### ❌ Reflection-Based Serialization on Hot Paths

Using `JsonConvert.SerializeObject()` or reflection-based `JsonSerializer.Serialize()` on high-throughput code paths. This design causes runtime type inspection on every call, prevents AOT compilation, and adds GC pressure.

**Instead**: Use source-generated `JsonSerializerContext` or binary formats (MessagePack, Protobuf) for hot paths.

### ❌ Type Names as Wire Contracts

Setting `TypeNameHandling.All` in Newtonsoft.Json or embedding assembly-qualified type names in payloads. This architecture couples serialized data to internal class structure — any rename, namespace move, or assembly change breaks deserialization.

**Instead**: Use explicit string discriminators with `[JsonDerivedType]` or Protobuf `oneof`.

### ❌ Big Bang Format Migration

Switching all producers and consumers to a new serialization format in a single deployment. This layer-crossing change causes failures when nodes at different versions communicate during rolling upgrades.

**Instead**: Use the Read-Before-Write pattern — deploy readers first, then enable writers.

---

## Quick Reference

| Decision | Recommendation |
|----------|---------------|
| REST API serialization | System.Text.Json + source generators |
| gRPC wire format | Protocol Buffers (native) |
| Actor/messaging format | MessagePack or Protobuf |
| Event store format | Protobuf (best versioning) |
| Cache serialization | MessagePack (fastest, smallest) |
| Config/logging format | System.Text.Json (human-readable) |
| AOT compatibility needed | Source generators (JSON) or Protobuf/MessagePack |
| Migrating from Newtonsoft | System.Text.Json + `[JsonDerivedType]` for polymorphism |

**Performance comparison** (relative throughput):

| Format | Speed | Payload Size | AOT Compatible |
|--------|-------|-------------|----------------|
| MessagePack | ★★★★★ | ★★★★★ | ✅ Yes |
| Protobuf | ★★★★★ | ★★★★★ | ✅ Yes |
| System.Text.Json (source gen) | ★★★★☆ | ★★★☆☆ | ✅ Yes |
| System.Text.Json (reflection) | ★★★☆☆ | ★★★☆☆ | ❌ No |
| Newtonsoft.Json | ★★☆☆☆ | ★★★☆☆ | ❌ No |

---

## Resources

- **System.Text.Json Source Generation**: https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/source-generation
- **Protocol Buffers**: https://protobuf.dev/
- **MessagePack-CSharp**: https://github.com/MessagePack-CSharp/MessagePack-CSharp
- **Akka.NET Serialization**: https://getakka.net/articles/networking/serialization.html
- **Wire Compatibility**: https://getakka.net/community/contributing/wire-compatibility.html
