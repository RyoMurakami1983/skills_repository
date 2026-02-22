<!-- このドキュメントは dotnet-type-design-performance の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-type-design-performance
description: >
  .NETの型をパフォーマンス重視で設計する。sealed クラス、readonly 構造体、
  静的関数、遅延列挙、不変コレクションを活用。
  Use when designing new types, reviewing performance, or choosing between class/struct/record.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, csharp, performance, type-design, sealed, readonly-struct, collections]
  invocable: false
---

# .NETにおけるパフォーマンスのための型設計

JIT最適化を最大化し、アロケーションを最小化し、明確なAPI意図を伝える.NET型設計の実践パターン。シーリング、値型、純粋関数、遅延列挙、コレクション返却型をカバーします。

## When to Use This Skill

以下の場合にこのスキルを使用してください：
- 新しい型を設計し、class / struct / record の選択を行うとき
- 既存コードのパフォーマンス改善機会をレビューするとき
- ホットパスでコレクションやenumerableを扱うとき
- .NETプロジェクトの型設計規約を確立するとき
- 非同期戻り値型（`Task` vs `ValueTask`）を選択するとき

**前提条件**：
- .NET 6+ プロジェクト
- C# 型システム（class, struct, record）の基本的な理解

---

## Related Skills

- **`dotnet-generic-matching`** — readonly構造体と不変コレクションをマッチング結果に活用
- **`tdd-standard-practice`** — パフォーマンス重要なコードをRed-Green-Refactorでテスト
- **`git-commit-practices`** — 各リファクタリングステップをアトミックな変更としてコミット

---

## Core Principles

1. **デフォルトでシール** — 継承を意図して設計していない限り、型をsealしてJITのdevirtualizationを有効化（基礎と型）
2. **小さなデータには値セマンティクス** — 小さな不変データにはreadonly構造体を使い、ヒープアロケーションを回避（基礎と型）
3. **依存の明示** — すべての入力を可視化する静的純粋関数を優先（ニュートラル）
4. **マテリアライズの遅延** — 必要になるまで列挙しない。呼び出し側にマテリアライズのタイミングを委ねる（余白の設計）
5. **不変なAPI境界** — パブリックAPIからは`IReadOnlyList<T>`を返し、意図しない変更を防止（成長の複利）

**Why — なぜこれらの原則が重要か**：

.NETのJITコンパイラは「型が何であるか」を知ることで最適化を行います。sealedクラスはvtableルックアップを排除し、readonly構造体は防御コピーを排除します。これは「基礎と型」の哲学そのものです — 正しい型を選ぶことが、すべての応用（パフォーマンス最適化）の基盤になります。

また、APIから不変コレクションを返すことは「成長の複利」です。最初は面倒に感じても、長期的にバグを防ぎ、信頼性を積み上げます。

---

## Workflow: Design Types for Performance

### Step 1 — デフォルトでクラスをシールする

継承を意図していない新しいクラスやレコードを作成するときに使用します。

シーリングによりJITのdevirtualizationが有効になります — コンパイラがvtableルックアップの代わりにメソッド呼び出しをインライン化できます。

```csharp
// DO: 継承を意図しないクラスはシールする
public sealed class OrderProcessor
{
    public void Process(Order order) { /* ... */ }
}

// DO: レコードもシールする（内部的にはクラス）
public sealed record OrderCreated(OrderId Id, CustomerId CustomerId);
```

```csharp
// DON'T: 理由なくシールしない
public class OrderProcessor  // サブクラス化可能 — 意図的？
{
    public virtual void Process(Order order) { }  // Virtual = 遅い
}
```

**Why**: `sealed`は「このクラスは拡張ポイントではない」と明示的に宣言します。JITはこの情報を使ってメソッド呼び出しを最適化します。型を明示する行為そのものが、基礎と型の実践です。

> **Values**: 基礎と型（型を明示することで意図が伝わり、JITが最適化できる）

### Step 2 — 値型にはReadonly構造体を使用する

小さな不変データ型を値セマンティクスで定義するときに使用します。

構造体を`readonly`にマークすることで、`in`参照渡しやreadonlyフィールドに格納された際の防御コピーを防ぎます。

```csharp
// DO: 識別子にはreadonly record struct
public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
    public override string ToString() => Value.ToString();
}

// DO: 小さな値オブジェクトにはreadonly struct
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
// DON'T: ミュータブルな構造体（防御コピーが発生）
public struct Point  // readonlyではない！
{
    public int X { get; set; }  // ミュータブル = 防御コピー
    public int Y { get; set; }
}
```

**Why**: C#コンパイラは、readonlyではない構造体がreadonly文脈で使用されると、自動的に防御コピーを作成します。これはコードからは見えませんが、メモリ使用量を2倍にし、パフォーマンスを低下させます。正しい型選択（readonly）がこの問題の根本的な解決策です。

| 構造体を使う場面 | クラスを使う場面 |
|------------------|------------------|
| 小さい（≤ 16バイト） | 大きなオブジェクト |
| 短命 | 長期間・共有参照 |
| 値セマンティクス | アイデンティティセマンティクス |
| 不変 | ミュータブルな状態が必要 |

> **Values**: 基礎と型（正しい型選択が防御コピーを排除し、性能の基盤となる）

### Step 3 — 静的純粋関数を優先する

副作用なしで入力を変換するロジックを書くときに使用します。

隠れた状態を持たない静的メソッドは高速（vtableルックアップなし）で、本質的にスレッドセーフで、テストが容易です。

```csharp
// DO: 静的純粋関数 — すべての依存が明示的
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
// DON'T: 依存を隠すインスタンスメソッド
public class OrderCalculator
{
    private readonly ITaxService _taxService;          // 隠れている
    private readonly IDiscountService _discountService; // 隠れている

    public Money CalculateTotal(IReadOnlyList<OrderItem> items)
    {
        // 実際に何に依存しているのか？不明。
    }
}
```

**Why**: 依存を隠さず明示することは「ニュートラルな視点」の実践です。誰がコードを読んでも、そのメソッドが何を必要とし、何を返すかが一目で分かります。これは個人の好みではなく、普遍的に理解しやすい設計です。

> **Values**: ニュートラル（依存を隠さず明示することで、誰でも理解できる普遍的な設計になる）

### Step 4 — 列挙を遅延させる

LINQクエリやコレクションパイプラインを扱うときに使用します。

必要になるまでenumerableをマテリアライズしないでください。まず操作をチェーンし、最後に`.ToList()`を一度だけ呼びます。

```csharp
// DON'T: 複数回のマテリアライズ
public IReadOnlyList<Order> GetActiveOrders()
{
    return _orders
        .Where(o => o.IsActive)
        .ToList()                    // ここでマテリアライズ！
        .OrderBy(o => o.CreatedAt)
        .ToList();                   // 再びマテリアライズ！
}

// DO: 最後に一度だけマテリアライズ
public IReadOnlyList<Order> GetActiveOrders()
{
    return _orders
        .Where(o => o.IsActive)
        .OrderBy(o => o.CreatedAt)
        .ToList();  // 一度だけ
}

// DO: 呼び出し側がすべてのアイテムを必要としない場合はIEnumerableを返す
public IEnumerable<Order> GetActiveOrders()
{
    return _orders
        .Where(o => o.IsActive)
        .OrderBy(o => o.CreatedAt);
    // 呼び出し側がマテリアライズのタイミングを決める
}
```

**Why**: 列挙を遅延させることは「余白の設計」です。呼び出し側に「いつデータを確定するか」という判断の余白を残します。すべてを先に確定してしまうと、柔軟性が失われます。

> **Values**: 余白の設計（列挙を遅延させることで、呼び出し側に判断の余白を残す）

### Step 5 — コレクション返却型を選択する

パブリックAPIのコレクション返却型を定義するときに使用します。

パブリックAPIからは不変なコレクションインターフェースを返します。構築中は内部的にミュータブルな型を使用して構いません。

```csharp
// DO: APIから不変コレクションを返す
public IReadOnlyList<Order> GetOrders()
{
    return _orders.ToList();  // 呼び出し側は内部状態を変更できない
}

// DO: 静的ルックアップデータにはFrozenDictionary（.NET 8+）
private static readonly FrozenDictionary<string, Handler> _handlers =
    new Dictionary<string, Handler>
    {
        ["create"] = new CreateHandler(),
        ["update"] = new UpdateHandler(),
    }.ToFrozenDictionary();
```

```csharp
// DON'T: パブリックAPIからミュータブルなコレクションを返す
public List<Order> GetOrders()
{
    return _orders;  // 呼び出し側が内部状態を変更できてしまう！
}
```

**Why**: 不変なAPIを積み上げることは「成長の複利」です。最初の実装では少し手間がかかりますが、プロジェクトが成長するにつれて、バグの防止効果が複利的に増加します。

| シナリオ | 返却型 |
|----------|--------|
| API境界 | `IReadOnlyList<T>`, `IReadOnlyCollection<T>` |
| 静的ルックアップ | `FrozenDictionary<K,V>`, `FrozenSet<T>` |
| 内部構築 | `List<T>` → readonlyとして返却 |
| 単一またはなし | `T?`（nullable） |
| 0個以上、遅延 | `IEnumerable<T>` |

> **Values**: 成長の複利（不変なAPIは変更に強く、長期的な信頼性を積み上げる）

---

## Good Practices

### 1. 新しいクラスはデフォルトでシール

✅ すべての新しいクラスに`sealed`を付けることから始めます。継承の具体的な必要性が生じたときだけ外します。「拡張に開く」という判断を偶然ではなく明示的にします。

### 2. IDにはreadonly record structを優先

✅ ドメイン識別子（`OrderId`、`CustomerId`）には`readonly record struct`を使用します。値の等価性、`ToString()`、ゼロヒープアロケーションを一つの宣言で得られます。

### 3. パイプライン末尾でSingle ToList

✅ すべてのLINQ操作（`Where`、`OrderBy`、`Select`）をチェーンしてから、`.ToList()`を一度だけ呼びます。中間の`.ToList()`はそれぞれ新しいリストを割り当て、シーケンス全体を反復します。

### 4. キャッシュされたホットパスにはValueTaskを使用

✅ メソッドが同期的に返すことが多い場合（例：キャッシュヒット）、`ValueTask<T>`を使って`Task`のアロケーションを回避します。常に非同期のI/O操作には`Task<T>`を使用します。詳細は[応用パターン](advanced-performance-patterns.md)を参照。

---

## Common Pitfalls

### 1. ミュータブルな構造体による防御コピー

readonlyではない構造体が`readonly`フィールドに格納されたり、`in`で渡されたりすると、コンパイラは変更を防ぐために隠れたコピーを作成します。これはメモリ使用量を無言で2倍にします。

**解決策**: 変更が意図的に必要な場合を除き、常に構造体を`readonly`にマークします。

### 2. パブリックAPIからList&lt;T&gt;を返す

`List<T>`を公開すると、呼び出し側が`Add()`、`Remove()`、`Clear()`で内部コレクションを操作でき、カプセル化が壊れます。

**解決策**: `IReadOnlyList<T>`または`IReadOnlyCollection<T>`を返します。

### 3. 非同期パイプラインでの早期列挙

`.Select(async o => await ProcessAsync(o)).ToList()`はアイテムごとに1つの`Task`を作成し、即座にマテリアライズします。

**解決策**: ストリーミングには`IAsyncEnumerable<T>`、バッチ並列処理には`Task.WhenAll`を使用します。詳細は[応用パターン](advanced-performance-patterns.md)を参照。

---

## Anti-Patterns

```csharp
// ❌ 理由なくシールしないクラス
public class OrderService { }  // → sealed を追加

// ❌ ミュータブルな構造体
public struct Point { public int X; public int Y; }  // → readonlyにする

// ❌ 静的にできるインスタンスメソッド
public int Add(int a, int b) => a + b;  // → staticにする

// ❌ 複数回のToList()呼び出し
items.Where(...).ToList().OrderBy(...).ToList();  // → 最後に一度だけ

// ❌ パブリックAPIからミュータブルなコレクションを返す
public List<Order> GetOrders();  // → IReadOnlyList<T>

// ❌ 常に非同期な操作にValueTask
public ValueTask<Order> CreateOrderAsync();  // → Taskを使用
```

---

## Quick Reference

| パターン | 効果 |
|----------|------|
| `sealed class` | Devirtualization、明確なAPI意図 |
| `readonly record struct` | 防御コピーなし、値セマンティクス |
| 静的純粋関数 | vtableなし、テスト可能、スレッドセーフ |
| `.ToList()`の遅延 | 一度のマテリアライズ、アロケーション削減 |
| ホットパスに`ValueTask` | 同期時のTaskアロケーション回避 |
| バイトに`Span<T>` | スタックアロケーション、コピーなし |
| `IReadOnlyList<T>`返却 | 不変なAPI契約 |
| `FrozenDictionary` | 静的データ最速ルックアップ（.NET 8+） |

---

## Resources

- **パフォーマンスベストプラクティス**: https://learn.microsoft.com/en-us/dotnet/standard/performance/
- **Sealedクラス**: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/sealed
- **Span&lt;T&gt;ガイダンス**: https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/
- **Frozenコレクション**: https://learn.microsoft.com/en-us/dotnet/api/system.collections.frozen
- **応用パターン**: [ValueTask、Span、非同期列挙](advanced-performance-patterns.md)
