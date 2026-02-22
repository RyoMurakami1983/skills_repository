---
name: dotnet-database-performance
description: >
  Optimize .NET database access with CQRS read/write separation, N+1 prevention,
  AsNoTracking, row limits, and SQL-side joins. Use when designing data access layers,
  optimizing slow queries, or choosing between EF Core and Dapper.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [cqrs, ef-core, dapper, performance, database]
  invocable: false
---

<!-- このドキュメントは dotnet-database-performance の日本語版です。英語版: ../SKILL.md -->

# Database Performance Patterns

.NET データベースアクセスを最適化するための実証済みパターン集。CQRS（コマンドクエリ責務分離）によるリード/ライトモデルの分離、N+1 クエリの防止、AsNoTracking によるリード最適化、必須の行数制限、SQL サイドでの結合を網羅します。EF Core と Dapper の両方に対応。.NET 8+ が必要です。

## When to Use This Skill

- 読み取りと書き込みを分離したデータアクセス層の設計（パフォーマンス分離のため）
- N+1 パターンの排除と不要なトラッキングの除去によるクエリ最適化
- 同一プロジェクト内での EF Core と Dapper の使い分け判断
- すべてのクエリに必須の行数制限を持つカーソルベースまたはオフセットページネーションの実装
- 複数の Include 呼び出しによるデカルト積爆発リスクの既存コードレビュー
- 汎用リポジトリパターンをクエリ最適化されたリードストアに置き換える

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-modern-csharp-coding-standards` | Record 型、パターンマッチング、Result\<T\> エラーハンドリング |
| `dotnet-type-design-performance` | Span\<T\>、Memory\<T\>、ゼロアロケーションパターン |
| `dotnet-project-structure` | ソリューション構成、プロジェクト構成、依存関係管理 |

## Core Principles

1. **Separate Read and Write Models** — クエリとコマンドに異なる型を使用する。読み取りモデルは非正規化されたプロジェクション、書き込みモデルはバリデーションと不変条件を強制する。
2. **Think in Batches** — 関連データはバルククエリで取得し、一件ずつ取得しない。N+1 クエリは線形のデータベースラウンドトリップを引き起こし、負荷時のパフォーマンスを破壊する。
3. **Only Retrieve What You Need** — 特定のカラムだけをプロジェクションし、すべての読み取りに行数制限を適用する。未使用データの転送は帯域幅、メモリ、データベース I/O を浪費する。
4. **Do Joins in SQL** — アプリケーションメモリ内でコレクションを結合しない。データベースエンジンはインデックスで結合を最適化するが、アプリケーション側の結合は O(n×m) の総当たりになる。
5. **Disable Tracking for Reads** — すべての読み取り専用クエリで AsNoTracking を使用する。変更追跡はすべてのエンティティのスナップショットコピーを割り当て、メモリ使用量を倍増させる。

> **Values**: 基礎と型の追求（最小形式で最大可能性を生む設計思想）, 温故知新（SQL の基本原則を EF Core/Dapper の最新 API で活かす）

## Workflow: Optimize Database Access

### Step 1: Separate Read and Write Stores

CQRS を適用し、読み取りと書き込み操作に別々のインターフェースを作成する。新しいデータアクセス層を設計する場合、または単一のリポジトリを最適化されたクエリパスにリファクタリングする場合に使用する。

```csharp
// 読み取りモデル：ユースケースごとの特化プロジェクション
public interface IUserReadStore
{
    Task<UserProfile?> GetByIdAsync(UserId id, CancellationToken ct = default);
    Task<IReadOnlyList<UserSummary>> GetAllAsync(int limit, UserId? cursor = null, CancellationToken ct = default);
    Task<bool> EmailExistsAsync(EmailAddress email, CancellationToken ct = default);
}

// 書き込みモデル：型付きコマンドを受け取り、最小限のデータを返す
public interface IUserWriteStore
{
    Task<UserId> CreateAsync(CreateUserCommand command, CancellationToken ct = default);
    Task UpdateAsync(UserId id, UpdateUserCommand command, CancellationToken ct = default);
    Task DeleteAsync(UserId id, CancellationToken ct = default);
}
```

**構造的な違い：**
- **リードストア**は複数の DTO 型（UserProfile、UserSummary、bool）を返す — ステートレスなプロジェクション
- **ライトストア**は最小限のデータ（作成時は UserId、更新時は void）を返す — コマンド中心
- 読み取りと書き込みで異なるデータベースやテーブルを使用可能（結果整合性パターン）

> **Values**: 基礎と型の追求（読み取りと書き込みの責務を分離し、各モデルを最適化する型設計）

### Step 2: Apply Row Limits and Pagination

すべての読み取りメソッドに必須の `limit` パラメータを適用する。コレクションを返すクエリを設計する場合に使用する — 無制限の結果セットは本番障害の原因となる。

```csharp
public interface IOrderReadStore
{
    // limit は必須パラメータ（オプションではない）
    Task<IReadOnlyList<OrderSummary>> GetByCustomerAsync(
        CustomerId customerId, int limit,
        OrderId? cursor = null, CancellationToken ct = default);
}
```

**カーソルベースページネーション（Dapper）：**

```csharp
const string sql = """
    SELECT id, customer_id, total, status, created_at
    FROM orders
    WHERE customer_id = @CustomerId
    AND (@Cursor IS NULL OR created_at < (SELECT created_at FROM orders WHERE id = @Cursor))
    ORDER BY created_at DESC
    LIMIT @Limit
    """;
```

> **Values**: 継続は力（すべてのクエリに制限を適用する習慣が、本番障害を未然に防ぐ）

### Step 3: Use AsNoTracking for Read Queries

すべての読み取り専用の EF Core クエリに `AsNoTracking()` を適用する。変更しないデータを取得する場合に使用する — 変更追跡はエンティティのスナップショットを保存するためメモリ使用量が倍増する。

```csharp
// ✅ 読み取りではトラッキングを無効化
var users = await _context.Users
    .AsNoTracking()
    .Where(u => u.IsActive)
    .ToListAsync();

// ❌ 変更しないエンティティをトラッキング — 無駄
var users = await _context.Users
    .Where(u => u.IsActive)
    .ToListAsync();  // 変更追跡が有効
```

**読み取り中心のアプリケーションではデフォルト動作を設定：**

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    optionsBuilder.UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking);
}
```

> **Values**: ニュートラルな視点（デフォルトを NoTracking にし、追跡が必要な箇所だけ明示する偏りのない設計）

### Step 4: Prevent N+1 Queries

アイテムごとのクエリの代わりにバッチロードまたはイーガーロードを適用する。リストとその関連データを取得する場合に使用する — N+1 パターンはアイテムごとに1つのクエリを発生させ、データサイズに比例して線形にスケールする。

```csharp
// ❌ N+1 クエリ — 各イテレーションでデータベースにアクセス
var orders = await _context.Orders.ToListAsync();
foreach (var order in orders)
{
    var items = await _context.OrderItems
        .Where(i => i.OrderId == order.Id).ToListAsync();
}

// ✅ EF Core: JOIN による単一クエリ
var orders = await _context.Orders
    .AsNoTracking()
    .Include(o => o.Items)
    .ToListAsync();
```

**Dapper バッチアプローチ（2クエリ、N+1 なし）：**

```csharp
const string sql = """
    SELECT id, customer_id, total FROM orders WHERE customer_id = @CustomerId;
    SELECT oi.* FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.id WHERE o.customer_id = @CustomerId;
    """;

using var multi = await connection.QueryMultipleAsync(sql, new { CustomerId = customerId });
var orders = (await multi.ReadAsync<OrderRow>()).ToList();
var items = (await multi.ReadAsync<OrderItemRow>()).ToList();
```

> **Values**: 成長の複利（N+1 を見抜く力が、あらゆるデータアクセス層の品質を底上げする）

### Step 5: Perform Joins in SQL and Avoid Cartesian Explosions

SQL サイドの結合を適用し、複数の Include 呼び出しには `AsSplitQuery()` または明示的プロジェクションを使用する。関連エンティティを結合する場合に使用する — アプリケーション側の結合はメモリと CPU を浪費する。

```csharp
// ❌ アプリケーション側の結合 — 2つのフルテーブルスキャン、メモリ内で O(n×m)
var customers = await _context.Customers.ToListAsync();
var orders = await _context.Orders.ToListAsync();
var result = customers.Select(c => new {
    Customer = c,
    Orders = orders.Where(o => o.CustomerId == c.Id).ToList()
});

// ✅ SQL 結合 — 単一クエリ、データベース最適化
var result = await _context.Customers
    .AsNoTracking()
    .Include(c => c.Orders)
    .ToListAsync();
```

**AsSplitQuery でデカルト積爆発を回避：**

```csharp
// ✅ 分割: 4つの個別クエリ、合計約125行
var product = await _context.Products
    .AsSplitQuery()
    .Include(p => p.Reviews).Include(p => p.Images).Include(p => p.Categories)
    .FirstOrDefaultAsync(p => p.Id == id);
```

> **Values**: 余白の設計（プロジェクションで必要なデータだけ取得し、将来のスケーリングに余白を残す）

## Good Practices

- ✅ 読み取り/書き込みストアインターフェースを分離する — 同じエンティティを両方に使い回さない
- ✅ EF Core のすべての読み取り専用クエリに `AsNoTracking()` を適用する
- ✅ 複数の `Include` 呼び出しでデカルト積のリスクがある場合は `AsSplitQuery()` を使用する
- ✅ コレクションを返すすべての読み取りメソッドに必須の `limit` パラメータを適用する
- ✅ 大規模データセットにはオフセットページネーションよりカーソルベースページネーションを使用する
- ✅ 複雑な読み取りクエリには明示的 SQL がクリーンで高速な Dapper を使用する
- ✅ バリデーションやドメイン中心の操作を伴う書き込みには EF Core を使用する
- ✅ EF Core モデル設定で `HasMaxLength()` を使用してカラムサイズを制約する
- ✅ 汎用 `IRepository<T>` を避け、目的別のリードストアを構築する
- ✅ すべての非同期データアクセスメソッドで `CancellationToken` を受け入れる

## Common Pitfalls

1. **無制限の結果セット** — `LIMIT` 句なしですべての行を返すと、本番環境でメモリ不足が発生する。修正：`limit` を必須のメソッドパラメータにする。
2. **読み取り専用エンティティのトラッキング** — EF Core の変更追跡はメモリ使用量を倍増させる。修正：すべての読み取り専用クエリに `AsNoTracking()` を適用する。
3. **N+1 クエリループ** — `foreach` ループ内で関連データを取得すると、アイテムごとに1つのクエリが生成される。修正：`Include()` またはバッチクエリを使用する。
4. **アプリケーション側の結合** — 2つのフルテーブルをロードして LINQ で結合するのは O(n×m)。修正：SQL `JOIN` または EF Core `Include()` を使用する。
5. **複数 Include によるデカルト積爆発** — 3つの `Include` 呼び出しが行を指数的に増加させる可能性がある。修正：`AsSplitQuery()` または明示的プロジェクションを使用する。
6. **汎用リポジトリによる複雑性の隠蔽** — `IRepository<T>.GetAll()` は制限の強制やクエリの最適化を不可能にする。修正：目的別ストアを設計する。

## Anti-Patterns

### ❌ Generic Repository → ✅ Purpose-Built Stores

```csharp
// ❌ BAD — 最適化不可、制限なし、N+1 を隠蔽
public interface IRepository<T>
{
    Task<T?> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();  // 制限なし！
}

// ✅ GOOD — クエリ固有、制限を強制、最適化可能
public interface IOrderReadStore
{
    Task<OrderDetail?> GetByIdAsync(OrderId id, CancellationToken ct = default);
    Task<IReadOnlyList<OrderSummary>> GetByCustomerAsync(
        CustomerId id, int limit, CancellationToken ct = default);
}
```

**汎用リポジトリのアーキテクチャレベルの問題：**
- 特定のクエリパターンの最適化や行数制限の強制ができない
- 抽象化レイヤーの背後に N+1 問題を隠蔽する
- 利便性メソッドを通じて過剰なデータ取得を助長する

### ❌ SELECT * → ✅ Explicit Column Projection

```csharp
// ❌ BAD — 大きなテキストフィールドを含む全カラムを取得
var users = await _context.Users.ToListAsync();

// ✅ GOOD — 必要なカラムだけをプロジェクション
var users = await _context.Users
    .AsNoTracking()
    .Select(u => new UserSummary(u.Id, u.Name, u.Email))
    .ToListAsync();
```

### ❌ Unconstrained Strings → ✅ MaxLength Configuration

```csharp
// ✅ カラムサイズを設定してオーバーサイズデータを防止
builder.Property(u => u.Email).HasMaxLength(254).IsRequired();
builder.Property(u => u.Name).HasMaxLength(100).IsRequired();
builder.Property(u => u.Notes).HasColumnType("text");
```

## Quick Reference

### EF Core vs Dapper Decision Table

| Scenario | Recommendation | Why |
|----------|---------------|-----|
| Simple CRUD operations | EF Core | 変更追跡とマイグレーションが書き込みを簡素化 |
| Complex read queries | Dapper | 明示的 SQL でパフォーマンスを完全制御 |
| Writes with domain validation | EF Core | エンティティ設定が制約を強制 |
| Bulk insert/update operations | Dapper or raw SQL | エンティティごとのトラッキングオーバーヘッドを回避 |
| Reporting and analytics queries | Dapper | 複雑な集計は生 SQL の方がクリーン |
| Mixed read/write project | Both | 書き込みに EF Core、読み取りに Dapper |

### Anti-Pattern Quick Fix Table

| Anti-Pattern | Fix | Instead |
|--------------|-----|---------|
| No row limit | `limit` パラメータ追加 | すべての読み取りメソッドに制限を必須化 |
| SELECT * | カラムプロジェクション | `.Select()` で特定フィールドを指定 |
| N+1 queries | バッチまたは Include | `.Include()` またはマルチクエリを使用 |
| Application joins | SQL JOIN | `.Include()` または `INNER JOIN` を使用 |
| Cartesian explosion | AsSplitQuery | `.AsSplitQuery()` またはプロジェクション |
| Tracking reads | AsNoTracking | 読み取りクエリに `.AsNoTracking()` を使用 |
| Generic repository | 目的別ストア | クエリ固有のインターフェースを設計 |

## Resources

- [EF Core Performance](https://learn.microsoft.com/en-us/ef/core/performance/) — 公式パフォーマンスガイド
- [Dapper](https://github.com/DapperLib/Dapper) — 高パフォーマンスリード向けマイクロ ORM
- [AsSplitQuery](https://learn.microsoft.com/en-us/ef/core/querying/single-split-queries) — 分割 vs 単一クエリのガイダンス
- [references/cqrs-patterns.md](references/cqrs-patterns.md) — CQRS フォルダ構造と Dapper 実装の詳細
