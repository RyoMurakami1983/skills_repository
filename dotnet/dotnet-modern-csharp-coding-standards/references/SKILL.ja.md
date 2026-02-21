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

<!-- このドキュメントは dotnet-modern-csharp-coding-standards の日本語版です。英語版: ../SKILL.md -->

# Modern C# Coding Standards

モダン C#（12+）で慣用的なコードを書くための簡潔なガードレール。record によるデータモデリング、パターンマッチング、合成優先の設計、Railway 指向のエラーハンドリングをカバーします。

## When to Use This Skill

- 新規 C# コードの作成、または既存コードのモダンなイディオムへのリファクタリング
- 強い型付けと不変性を持つドメインモデルの設計
- `record`、`record struct`、`class`、`struct` の使い分け判断
- パターンマッチングによる制御フローの簡潔化
- 例外の代わりに `Result<T, TError>` でエラーハンドリング
- C# コードのアンチパターン（可変 DTO、深い継承、リフレクション マッピング）のレビュー

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-type-design-performance` | Span\<T\>、Memory\<T\>、ArrayPool、ゼロアロケーションパターン |
| `dotnet-csharp-api-design` | API パラメータ/戻り値の型契約、メソッドシグネチャ |
| `dotnet-csharp-concurrency-patterns` | async/await ベストプラクティス、CancellationToken、IAsyncEnumerable |

## Core Principles

1. **Immutability by Default** — `record` 型と `init` 専用プロパティを使用。可変状態は並行処理バグとロジックバグの最大の原因。
2. **Type Safety** — nullable 参照型、`readonly record struct` による値オブジェクト、強く型付けされた ID を活用し、コンパイル時にエラーを検出。
3. **Modern Pattern Matching** — `if`/`else` チェーンを `switch` 式とリレーショナル/プロパティ/リストパターンに置き換え、表現力豊かで網羅的な分岐を実現。
4. **Composition Over Inheritance** — 抽象基底クラスよりインターフェース＋合成を優先。フラットな構造はテスト、拡張、理解が容易。
5. **Railway Error Handling** — 予期されるエラー（バリデーション、ビジネスルール）には `Result<T, TError>` を使用。例外は本当に予期しない障害にのみ。
6. **Explicit Over Magic** — リフレクションベースのライブラリ（AutoMapper、Mapster）よりコンパイル時チェック可能な明示的マッピングを優先。可視性は利便性に勝る。

> **Values**: 基礎と型の追求（最小形式で最大可能性を生む設計思想）, 温故知新（C# の進化を活かしつつ堅実な原則を守る）

## Workflow: Write Modern C#

### Step 1: Model Data with Records

DTO、メッセージ、ドメインエンティティには `record` を使用。値オブジェクトには `readonly record struct` を使用。

```csharp
// 不変 DTO
public record CustomerDto(string Id, string Name, string Email);

// 値オブジェクト — 常に readonly record struct
public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
    public override string ToString() => Value.ToString();
}

// バリデーション付き値オブジェクト
public readonly record struct Money(decimal Amount, string Currency)
{
    public Money(decimal amount, string currency) : this(
        amount >= 0 ? amount : throw new ArgumentException("Amount cannot be negative"),
        currency is { Length: 3 } ? currency.ToUpperInvariant()
            : throw new ArgumentException("Currency must be 3-letter code"))
    { }
}
```

**使い分けガイド：**

| 型 | 使用場面 |
|----|----------|
| `record class` | エンティティ、DTO、複数プロパティを持つ集約 |
| `readonly record struct` | 値オブジェクト、強く型付けされた ID、小さな不変値 |
| `class` | 可変サービス、フレームワーク要求の基底クラス |
| `struct` | パフォーマンスクリティカル、小データ（≤16 バイト）、ID なし |

> ⚠️ **値オブジェクトに暗黙的変換は禁止** — コンパイル時の型安全性を無効化します。詳細は [language-patterns.md](language-patterns.md) を参照。

> **Values**: 基礎と型の追求（型で不変条件を守り、コンパイラを味方にする）

### Step 2: Apply Pattern Matching & Nullable Types

分岐ロジックには `switch` 式を使用。プロジェクト全体で `<Nullable>enable</Nullable>` を有効化。

```csharp
// プロパティパターンによる switch 式
public decimal CalculateDiscount(Order order) => order switch
{
    { Total: > 1000m } => order.Total * 0.15m,
    { Total: > 500m }  => order.Total * 0.10m,
    { Total: > 100m }  => order.Total * 0.05m,
    _ => 0m
};

// null 安全なパターン
public decimal GetDiscount(Customer? customer) => customer switch
{
    null                   => 0m,
    { IsVip: true }        => 0.20m,
    { OrderCount: > 10 }   => 0.10m,
    _                      => 0.05m
};
```

リストパターン、タプルパターン、nullable 処理の詳細は [language-patterns.md](language-patterns.md) を参照。

> **Values**: 成長の複利（パターンマッチングの習得が、あらゆる分岐ロジックの品質を底上げする）

### Step 3: Prefer Composition Over Inheritance

```csharp
// ❌ 抽象基底クラス階層
public abstract class PaymentProcessor
{
    public abstract Task<PaymentResult> ProcessAsync(Money amount);
    protected async Task<bool> ValidateAsync(Money amount) { /* ... */ }
}

// ✅ インターフェースによる合成
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

**継承が許容される場面：**
- フレームワーク要件（例：ASP.NET Core の `ControllerBase`）
- ライブラリ統合（例：`Exception` からのカスタム例外）
- アプリケーションコードでは **まれ** であるべき

> **Values**: 余白の設計（合成可能な小さな部品が、将来の変化に対応する余白を生む）

### Step 4: Handle Errors with Result Types

予期されるエラーには `Result<T, TError>` を使用。予期しない障害には例外を使用。

```csharp
// エラー型
public readonly record struct OrderError(string Code, string Message);

// Result を返すサービス
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

// Result のパターンマッチング
return result.Match(
    onSuccess: order => new OkObjectResult(order),
    onFailure: error => error.Code switch
    {
        "VALIDATION_ERROR" => new BadRequestObjectResult(error.Message),
        "NOT_FOUND"        => new NotFoundObjectResult(error.Message),
        _                  => new ObjectResult(error.Message) { StatusCode = 500 }
    });
```

| 状況 | 使用するもの |
|------|------------|
| バリデーション失敗、ビジネスルール違反、見つからない | `Result<T, TError>` |
| ネットワーク障害、null 参照、OOM、プログラミングバグ | Exception |

完全な `Result<T, TError>` 実装と Railway 合成は [error-handling-patterns.md](error-handling-patterns.md) を参照。

> **Values**: ニュートラルな視点（例外と Result を状況に応じて使い分け、偏りのない設計を保つ）

### Step 5: Organize Code Files

一貫した名前空間とファイルレイアウトに従います：

```
Domain/
  Orders/
    Order.cs          # 主要ドメイン型 + 関連 record
    OrderService.cs   # ドメインロジック
    IOrderRepository.cs
```

**型ファイル内の順序：**
1. 主要ドメイン型（record/class）
2. 状態の enum
3. 関連 record（アイテム、イベント）
4. 値オブジェクト（readonly record struct）
5. エラー型

```csharp
namespace MyApp.Domain.Orders;

// 1. 主要型
public record Order(OrderId Id, CustomerId CustomerId, Money Total, IReadOnlyList<OrderItem> Items)
{
    public bool IsCompleted => Status is OrderStatus.Completed;
}

// 2. Enum
public enum OrderStatus { Draft, Submitted, Processing, Completed, Cancelled }

// 3. 関連 record
public record OrderItem(ProductId ProductId, Quantity Quantity, Money UnitPrice)
{
    public Money Total => new(UnitPrice.Amount * Quantity.Value, UnitPrice.Currency);
}

// 4. 値オブジェクト
public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
}

// 5. エラー
public readonly record struct OrderError(string Code, string Message);
```

> **Values**: 継続は力（一貫したファイル構成が、日々のコードリーディングを高速化する）

## Good Practices

- ✅ DTO、メッセージ、ドメインエンティティには `record` を使用
- ✅ 値オブジェクトと強く型付けされた ID には `readonly record struct` を使用
- ✅ `if`/`else` より `switch` 式によるパターンマッチングを活用
- ✅ nullable 参照型を有効にし、警告を尊重（`<Nullable>enable</Nullable>`）
- ✅ すべての非同期メソッドで `CancellationToken` を受け取る
- ✅ API からは `List<T>` ではなく `IReadOnlyList<T>` を返す
- ✅ 予期されるエラーには `Result<T, TError>` を使用
- ✅ 継承階層よりインターフェースと合成を優先
- ✅ リフレクションベースのマッパーではなく明示的なマッピングメソッドを使用
- ✅ シンプルなサービスクラスにはプライマリコンストラクタ（C# 12+）を使用

## Common Pitfalls

1. **async のブロッキング** — `.Result` や `.Wait()` の呼び出しはデッドロックを引き起こす。最後まで `async` を貫く。
2. **可変 DTO** — `record` の代わりに `{ get; set; }` を持つ `class` を使用。意図しない変更につながる。
3. **値オブジェクトの暗黙的変換** — `implicit operator` はコンパイル時の型安全性を無効化する。
4. **深い継承** — `Entity → AggregateRoot → Order → CustomerOrder`。フラットな合成を使用する。
5. **null の無視** — パターンマッチングで処理する代わりに nullable 警告を無視する。
6. **予期されるエラーへの throw** — バリデーション/見つからないケースに `Result<T, TError>` ではなく例外を使用。

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
// ❌ BAD — ヒープ割り当て、参照等価
public class OrderId { public string Value { get; } }
// ✅ GOOD — スタック割り当て、値等価
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
// ❌ BAD — ランタイムエラー、隠れたマッピング
var dto = _mapper.Map<UserDto>(entity);
// ✅ GOOD — コンパイル時チェック、デバッグ可能
public static UserDto ToDto(this UserEntity e) => new(e.Id.ToString(), e.FullName, e.EmailAddress);
```

詳細はソースジェネレータと UnsafeAccessor について [anti-reflection-patterns.md](anti-reflection-patterns.md) を参照。

### ❌ Returning Mutable Collections

```csharp
// ❌ BAD — 内部リストを公開
public List<Order> GetOrders() => _orders;
// ✅ GOOD — 読み取り専用ビュー
public IReadOnlyList<Order> GetOrders() => _orders;
```

### ❌ Blocking on Async

```csharp
// ❌ BAD — デッドロックの危険
public Order GetOrder(OrderId id) => GetOrderAsync(id).Result;
// ✅ GOOD — 最後まで async
public async Task<Order> GetOrderAsync(OrderId id, CancellationToken ct = default)
    => await _repository.GetAsync(id, ct);
```

## Quick Reference

### When to Use record vs class vs struct

| 必要なもの | 型 | 理由 |
|-----------|------|------|
| DTO / メッセージ / イベント | `record` | 不変、値等価、`with` サポート |
| ドメインエンティティ | `record` | 同上 + 計算プロパティ |
| 値オブジェクト / 型付き ID | `readonly record struct` | スタック割り当て、値セマンティクス |
| DI 付き可変サービス | `class`（sealed） | 可変状態 / ライフサイクルが必要 |
| 小さな数学データ（≤16 バイト） | `struct` | パフォーマンスクリティカル、ID なし |

### When to Use Result vs Exception

| 状況 | 仕組み | 理由 |
|------|--------|------|
| バリデーション失敗 | `Result<T, TError>` | 予期される、呼び出し元が処理すべき |
| ビジネスルール違反 | `Result<T, TError>` | 通常のフローの一部 |
| エンティティが見つからない | `Result<T, TError>` | 予期されるクエリ結果 |
| ネットワーク / I/O 障害 | Exception | 予期しないインフラエラー |
| null 参照 / OOM | Exception | プログラミングバグ / システムエラー |

### File Ordering in a Type File

```
1. 主要ドメイン型（record/class）
2. Enum
3. 関連 record
4. 値オブジェクト（readonly record struct）
5. エラー型
```

## Resources

- [C# Language Reference](https://learn.microsoft.com/en-us/dotnet/csharp/)
- [Pattern Matching](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/functional/pattern-matching)
- [Nullable Reference Types](https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references)
- [language-patterns.md](language-patterns.md) — record、パターンマッチング、nullable の完全な例
- [error-handling-patterns.md](error-handling-patterns.md) — Result\<T, TError\> 実装と Railway パターン
- [anti-reflection-patterns.md](anti-reflection-patterns.md) — ソースジェネレータ、UnsafeAccessor、明示的マッピング
