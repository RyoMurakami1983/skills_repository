---
name: dotnet-csharp-api-design
description: >
  Design stable, compatible public APIs for NuGet packages and distributed systems.
  Use when planning API surfaces, managing breaking changes, implementing wire compatibility,
  or reviewing pull requests for API compatibility issues.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, csharp, api-design, compatibility, versioning, nuget, wire-format]
  invocable: false
---

# C# Public API Design and Compatibility

Design, evolve, and protect public API surfaces for NuGet packages and distributed systems. Covers API compatibility, binary compatibility, wire compatibility, extend-only design, API approval testing, deprecation workflows, and semantic versioning.

## When to Use This Skill

- Designing a new public API surface for a NuGet package or shared library from scratch
- Reviewing pull requests that add, change, or remove public type members or method signatures
- Planning wire format changes for distributed systems that require rolling upgrades safely
- Implementing API approval testing with PublicApiGenerator to prevent accidental breaking changes
- Deprecating existing public APIs and migrating consumers to replacement methods or types
- Choosing a versioning strategy that communicates breaking changes and extensions clearly
- Encapsulating internal implementation details to reduce the public API surface area scope
- Evolving serialized message formats while maintaining backward and forward compatibility

---

## Related Skills

- **`dotnet-serialization`** — Serialization formats and wire compatibility patterns for .NET
- **`dotnet-type-design-performance`** — Sealed classes, readonly structs, and record type design
- **`dotnet-project-structure`** — NuGet package management and Directory.Build.props setup
- **`dotnet-modern-csharp-coding-standards`** — C# language conventions and coding standards

---

## Core Principles

1. **Extend-Only Design** — Never remove or modify released API surface; add new overloads, types, and opt-in features instead. Previous functionality is immutable once published（基礎と型の追求）
2. **Explicit Compatibility Contracts** — Distinguish API (source), binary, and wire compatibility; breaking any type creates upgrade friction for consumers（温故知新）
3. **Deprecate Before Remove** — Mark APIs with `[Obsolete]` for at least one minor version before removal in the next major version, giving consumers migration time（余白の設計）
4. **Automated Surface Verification** — Use API approval tests to detect accidental breaking changes at build time instead of discovering them after release（基礎と型の追求）
5. **Chesterton's Fence** — Before removing or changing a public API, understand why it exists and assume someone depends on it（ニュートラルな視点）

---

## Workflow: Design and Maintain Stable Public APIs

### Step 1 — Classify Compatibility Requirements

Use when starting a new library or evaluating changes to an existing public API.

Determine which compatibility types apply to your scenario:

| Type | Definition | Scope | Example |
|------|------------|-------|---------|
| **API (Source)** | Code compiles against newer version | Public method signatures, types | Adding required parameter |
| **Binary** | Compiled code runs against newer version | Assembly layout, method tokens | Changing return type |
| **Wire** | Serialized data readable across versions | Network protocols, persistence | Renaming JSON property |

**Why classify first**: Each compatibility type has different rules — an API-safe change can still break binary compatibility, and a source-compatible change can break wire formats.

> **Values**: 基礎と型の追求（classification is the foundation of every compatibility decision）

### Step 2 — Design an Extend-Only API Surface

Use when adding new functionality to an existing public API without breaking consumers.

Apply the three pillars of extend-only design:

```csharp
// ✅ ADD new overloads with default parameters
public void Process(Order order, CancellationToken ct = default);

// ✅ ADD new optional parameters to existing methods
public void Send(Message msg, Priority priority = Priority.Normal);

// ✅ ADD new types, interfaces, enums
public interface IOrderValidator { }
public enum OrderStatus { Pending, Complete, Cancelled }

// ✅ ADD new members to existing types
public class Order
{
    public DateTimeOffset? ShippedAt { get; init; }  // New property
}
```

Avoid changes that break callers:

```csharp
// ❌ REMOVE or RENAME public members
public void ProcessOrder(Order order);  // Was: Process()

// ❌ CHANGE parameter types or order
public void Process(int orderId);  // Was: Process(Order order)

// ❌ CHANGE return types
public Order? GetOrder(string id);  // Was: public Order GetOrder()

// ❌ ADD required parameters without defaults
public void Process(Order order, ILogger logger);  // Breaks callers
```

**Why extend-only**: Old code continues working, new and old pathways coexist, and users upgrade on their own schedule.

> **Values**: 温故知新（proven design — once released, behavior and signatures are locked）

### Step 3 — Implement API Approval Testing

Use when protecting a NuGet package or library against accidental breaking changes.

Install the required packages:

```bash
dotnet add package PublicApiGenerator
dotnet add package Verify.Xunit
```

Create an API surface test:

```csharp
using PublicApiGenerator;
using VerifyXunit;

[Fact]
public Task ApprovePublicApi()
{
    // Generate a text snapshot of the entire public API
    var api = typeof(MyLibrary.PublicClass).Assembly.GeneratePublicApi();
    return Verify(api);
}
```

This creates `ApprovePublicApi.verified.txt` containing the full public API surface:

```csharp
namespace MyLibrary
{
    public class OrderProcessor
    {
        public OrderProcessor() { }
        public void Process(Order order) { }
        public Task ProcessAsync(Order order, CancellationToken ct = default) { }
    }
}
```

**Why API approval tests**: Any API change fails the test — reviewers see exact surface changes in the PR diff and must explicitly approve them.

> **Values**: 基礎と型の追求（automated verification catches what manual review misses）

### Step 4 — Manage Wire Compatibility for Distributed Systems

Use when designing message formats for systems that require zero-downtime rolling upgrades.

Implement the Read-Before-Write deployment pattern:

```csharp
// Phase 1: Deploy readers for V2 format everywhere (opt-in)
public object Deserialize(byte[] data, string manifest) => manifest switch
{
    "Heartbeat" => DeserializeV1(data),    // Old format
    "HeartbeatV2" => DeserializeV2(data),  // New format — readers deployed first
    _ => throw new NotSupportedException($"Unknown manifest: {manifest}")
};

// Phase 2: Enable V2 writers (next release, after all nodes read V2)
public (byte[] data, string manifest) Serialize(Heartbeat hb) =>
    _useV2 ? (SerializeV2(hb), "HeartbeatV2") : (SerializeV1(hb), "Heartbeat");
```

Use explicit discriminators instead of type names:

```csharp
// ❌ Type name in payload — renaming class breaks wire format
{ "$type": "MyApp.Order, MyApp", "Id": 123 }

// ✅ Explicit discriminator — refactoring safe
{ "type": "order", "id": 123 }
```

Both backward compatibility (old writers → new readers) and forward compatibility (new writers → old readers) are required for rolling upgrades.

> **Values**: 余白の設計（Read-Before-Write creates space for safe evolution）

### Step 5 — Apply Deprecation and Versioning Strategy

Use when removing or replacing existing public APIs across semantic versions.

Follow the deprecation lifecycle:

```csharp
// Step A: Mark as obsolete with version context (any release)
[Obsolete("Obsolete since v1.5.0. Use ProcessAsync instead.")]
public void Process(Order order) { }

// Step B: Add the new recommended API (same release)
public Task ProcessAsync(Order order, CancellationToken ct = default);

// Step C: Remove in next major version (v2.0+ only)
// Only after consumers have had time to migrate
```

Apply Semantic Versioning (SemVer) consistently:

| Version | Changes Allowed | Example |
|---------|----------------|---------|
| **Patch** (1.0.x) | Bug fixes, security patches | Fix null-reference in GetOrder |
| **Minor** (1.x.0) | New features, deprecations | Add ProcessAsync, obsolete Process |
| **Major** (x.0.0) | Breaking changes, API removal | Remove Process, rename types |

**Why deprecate before remove**: Consumers need time to plan upgrades — announce changes, document migration paths, and provide a deprecation period of at least one minor version.

> **Values**: 継続は力（gradual evolution preserves trust and enables compound adoption）

---

## Good Practices

- Use `sealed` on classes not designed for inheritance — why: prevents users from subclassing and blocking future changes
- Use small, focused interfaces (`IOrderReader`, `IOrderWriter`) — why: adding methods to large interfaces breaks all implementors
- Use `[InternalApi]` attribute or `.Internal` namespaces for non-public APIs — why: signals that types may change without notice
- Use `CancellationToken ct = default` on all async public methods — why: extend-only compatible and consistent
- Use API approval tests in CI pipelines — why: catches breaking changes before merge
- Use explicit `[JsonDerivedType]` discriminators instead of `TypeNameHandling` — why: refactoring-safe wire format
- Document that `.Internal` namespace types may change between releases without notice

---

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Adding required parameters | Breaks all existing callers at compile time | Use default parameter values |
| Changing method return types | Breaks binary compatibility for compiled assemblies | Add new method with new return type |
| Unsealed public classes | Users inherit, blocking internal refactoring | Seal classes by default |
| Deploying writer before reader | Old nodes cannot parse new wire format | Deploy readers first (Read-Before-Write) |
| Embedding .NET type names in wire | Class rename breaks deserialization | Use explicit string discriminators |
| Skipping deprecation period | Consumers cannot plan upgrade timeline | Mark `[Obsolete]` for at least one minor version |

---

## Anti-Patterns

### ❌ Breaking Changes Disguised as Bug Fixes

Changing a synchronous method to async as a "fix" — this design breaks all callers who depend on the synchronous signature. The correct approach is to add a new async method and deprecate the old one.

```csharp
// ❌ "Fixed" to be async — breaks all callers
public async Task<Order> GetOrderAsync(OrderId id) { }

// ✅ Correct: Add new method, deprecate old
[Obsolete("Use GetOrderAsync instead")]
public Order GetOrder(OrderId id) => GetOrderAsync(id).Result;
public async Task<Order> GetOrderAsync(OrderId id) { }
```

**Instead**: Always add new APIs alongside existing ones. Deprecate the old API explicitly.

### ❌ Silent Default Value Changes

Changing the default value of an existing parameter — this design silently alters behavior for all callers who relied on the previous default. The correct approach is to add a new parameter with the desired default.

```csharp
// ❌ Changed default from false to true — silent behavior change
public void Configure(bool enableCaching = true);

// ✅ Correct: Preserve original, add new parameter
public void Configure(
    bool enableCaching = false,       // Original default preserved
    bool enableNewCaching = true);    // New behavior opt-in
```

**Instead**: Never change defaults. Add new parameters with new names for new behavior.

### ❌ Monolithic Interface Growth

Adding methods to a large public interface — this architecture breaks every implementation. The correct approach is interface segregation with small, focused contracts.

```csharp
// ❌ Adding methods breaks all implementations
public interface IOrderRepository
{
    Order? GetById(OrderId id);
    Task SaveAsync(Order order);
    // Adding SearchAsync breaks all existing implementations!
}

// ✅ Correct: Segregated interfaces
public interface IOrderReader { Order? GetById(OrderId id); }
public interface IOrderWriter { Task SaveAsync(Order order); }
public interface IOrderSearcher { Task<IReadOnlyList<Order>> SearchAsync(string query); }
```

**Instead**: Design small interfaces from the start. Extend by creating new interfaces.

---

## Quick Reference

| Decision | Recommendation |
|----------|---------------|
| Adding new functionality | Add overloads, new types, or default parameters |
| Removing public API | Deprecate with `[Obsolete]`, remove in next major |
| Changing method signature | Add new overload, deprecate old signature |
| Changing wire format | Read-Before-Write: deploy readers first |
| Preventing accidental breaks | API approval tests with PublicApiGenerator |
| Sealing vs unsealing classes | Seal by default; unseal only when designed for inheritance |
| Interface evolution | Segregated interfaces; never add methods to existing ones |
| Versioning strategy | SemVer: patch=fixes, minor=features+deprecations, major=breaks |

---

## Resources

- [Making Public API Changes (Akka.NET)](https://getakka.net/community/contributing/api-changes-compatibility.html)
- [Wire Format Changes (Akka.NET)](https://getakka.net/community/contributing/wire-compatibility.html)
- [Extend-Only Design](https://aaronstannard.com/extend-only-design/)
- [OSS Compatibility Standards](https://aaronstannard.com/oss-compatibility-standards/)
- [Semantic Versioning](https://semver.org/)
- [PublicApiGenerator](https://github.com/PublicApiGenerator/PublicApiGenerator)
