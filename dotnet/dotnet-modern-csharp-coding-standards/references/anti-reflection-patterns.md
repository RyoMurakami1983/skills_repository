# Anti-Reflection Patterns（詳細リファレンス）

<!-- Parent skill: ../SKILL.md (dotnet-modern-csharp-coding-standards) -->

このファイルでは、reflection-based mapping を避けるべき理由、explicit mapping の書き方、source generator の使いどころ、そして正当な低レベルアクセスにおける `UnsafeAccessorAttribute` の使い方を扱います。

---

## 使用禁止ライブラリ

| Library | 問題点 |
|---------|---------|
| **AutoMapper** | reflection magic、隠れた mapping、runtime failure、debug の難しさ |
| **Mapster** | AutoMapper と同種の問題 |
| **ExpressMapper** | 同上 |

---

## Reflection Mapping が破綻しやすい理由

```csharp
// AutoMapper を使うと、コンパイルは通るが実行時に壊れうる
public record UserDto(string Id, string Name, string Email);
public record UserEntity(Guid Id, string FullName, string EmailAddress);

// この mapping は静かに不正な値を作りうる:
// - Id: string と Guid が不一致
// - Name と FullName: 対応せず null/default になる
// - Email と EmailAddress: 対応せず null/default になる
var dto = _mapper.Map<UserDto>(entity);  // コンパイルは通るが実行時に破綻する。
```

---

## 代わりに Explicit Mapping Method を使う

```csharp
// Extension method — コンパイル時に検査でき、見つけやすく、debug しやすい
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

// 使用例 — 明示的で追跡しやすい
var dto = entity.ToDto();
var entity = request.ToEntity();
```

### Explicit Mapping の利点

| 観点 | AutoMapper | Explicit Methods |
|--------|------------|------------------|
| **Compile-time safety** | なし — runtime error になる | あり — compiler が不整合を検出 |
| **Discoverability** | profile に隠れる | `Go to Definition` が効く |
| **Debugging** | black box | step 実行できる |
| **Refactoring** | rename が静かに壊れる | IDE が正しく rename する |
| **Performance** | reflection overhead あり | 直接 property にアクセス |
| **Testing** | integration test が要りやすい | 単純な unit test で済む |

### 複雑な Mapping

変換が複雑になるほど、explicit code の価値は高まります。

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

この形には次の利点があります。
- **Readable**: 変換内容を誰でも読める
- **Debuggable**: breakpoint を置いて値を追える
- **Testable**: `Order` を渡して結果をそのまま検証できる
- **Refactorable**: property 名を変えると compiler が影響箇所を教えてくれる

---

## Reflection が許容される場面

| Use Case | 許容可否 |
|----------|-------------|
| Serialization (System.Text.Json, Newtonsoft) | Yes — 実績があり、source generator も使える |
| Dependency injection container | Yes — framework infrastructure の一部 |
| ORM entity mapping (EF Core) | Yes — database abstraction に必要 |
| Test fixtures and builders | Sometimes — test 内の利便性に限る |
| **DTO / domain object mapping** | **No — explicit method を使う** |

---

## Source Generator vs Reflection

動的な振る舞いが必要でも、runtime reflection より source generator を優先します。

```csharp
// System.Text.Json source generator — AOT 対応で reflection 不要
[JsonSerializable(typeof(OrderDto))]
[JsonSerializable(typeof(CustomerDto))]
public partial class AppJsonContext : JsonSerializerContext { }

// 使用例
var json = JsonSerializer.Serialize(order, AppJsonContext.Default.OrderDto);
var dto = JsonSerializer.Deserialize(json, AppJsonContext.Default.OrderDto);
```

source generator には次の利点があります。
- **Compile-time code generation** — runtime reflection が不要
- **AOT compatibility** — NativeAOT trimming と相性がよい
- **Better performance** — reflection overhead がない
- **Compile-time errors** — build 時に不整合を検出できる

---

## `UnsafeAccessorAttribute`（.NET 8+）

private / internal member に本当にアクセスする必要がある場合（serializer、test helper、framework code など）は、従来の reflection ではなく `UnsafeAccessorAttribute` を使います。これにより **zero-overhead かつ AOT-compatible** な member access ができます。

```csharp
// ❌ 非推奨: 従来の reflection — 遅く、allocation が発生し、AOT も壊しやすい
var field = typeof(Order).GetField("_status", BindingFlags.NonPublic | BindingFlags.Instance);
var status = (OrderStatus)field!.GetValue(order)!;

// ✅ 推奨: UnsafeAccessor — zero overhead で AOT-compatible
[UnsafeAccessor(UnsafeAccessorKind.Field, Name = "_status")]
static extern ref OrderStatus GetStatusField(Order order);

var status = GetStatusField(order);  // 直接アクセスでき、reflection は不要
```

### 利用できる Accessor Kind

```csharp
// private field へのアクセス
[UnsafeAccessor(UnsafeAccessorKind.Field, Name = "_items")]
static extern ref List<OrderItem> GetItemsField(Order order);

// private method へのアクセス
[UnsafeAccessor(UnsafeAccessorKind.Method, Name = "Recalculate")]
static extern void CallRecalculate(Order order);

// private static field へのアクセス
[UnsafeAccessor(UnsafeAccessorKind.StaticField, Name = "_instanceCount")]
static extern ref int GetInstanceCount(Order order);

// private constructor の呼び出し
[UnsafeAccessor(UnsafeAccessorKind.Constructor)]
static extern Order CreateOrder(OrderId id, CustomerId customerId);
```

### Reflection より UnsafeAccessor を選ぶ理由

| 観点 | Reflection | UnsafeAccessor |
|--------|------------|----------------|
| Performance | 遅い（100–1000×） | Zero overhead |
| AOT compatible | No | Yes |
| Allocations | あり（boxing、array など） | なし |
| Compile-time checked | No | 一部あり（signature） |

### 主な Use Case

- private backing field にアクセスする serializer
- internal state を検証する test helper
- 可視性を越えてアクセスする必要がある framework code

### 参考リンク

- [A new way of doing reflection with .NET 8](https://steven-giesel.com/blogPost/05ecdd16-8dc4-490f-b1cf-780c994346a4)
- [Accessing private members without reflection in .NET 8.0](https://www.strathweb.com/2023/10/accessing-private-members-without-reflection-in-net-8-0/)
- [Modern .NET Reflection with UnsafeAccessor](https://blog.ndepend.com/modern-net-reflection-with-unsafeaccessor/)
