---
name: dotnet-efcore-patterns
description: >
  Entity Framework Core のベストプラクティスを適用する。NoTracking デフォルト、
  クエリ分割、マイグレーション管理、専用マイグレーションサービスを含む。
  Use when EF Core のセットアップ、クエリ最適化、データベースマイグレーション管理時に使用。
metadata:
  author: RyoMurakami1983
  tags: [efcore, entity-framework, dotnet, database, migrations, aspire]
  invocable: false
---

<!-- このドキュメントは dotnet-efcore-patterns の日本語版です。英語版: ../SKILL.md -->

# Entity Framework Core Patterns

EF Core（Entity Framework Core）開発のための簡潔なガードレール。NoTracking デフォルト、マイグレーション管理、クエリ分割、一時的障害ハンドリングをカバーします。.NET 8+ と PostgreSQL（Npgsql）を対象とし、.NET Aspire によるマイグレーションオーケストレーションと統合します。

## When to Use This Skill

- 新しい .NET プロジェクトでパフォーマンス重視のデフォルト設定で EF Core DbContext をセットアップする
- NoTracking 動作をグローバルに設定して読み取り中心のクエリパフォーマンスを最適化する
- EF Core CLI コマンドを使用して手動編集なしでデータベースマイグレーションを安全に管理する
- .NET Aspire オーケストレーションパイプラインと EF Core マイグレーション実行を統合する
- 変更追跡の設定ミスに起因するサイレント書き込み失敗をデバッグする
- ExecuteUpdate と ExecuteDelete を使用して一括更新・削除操作を実装する
- 複数のナビゲーションコレクションをEager Loadingする際のデカルト積爆発を防ぐ

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-project-structure` | .NET ソリューションレイアウト、プロジェクト参照、レイヤー分離 |
| `dotnet-modern-csharp-coding-standards` | Record 型、パターンマッチング、Result エラーハンドリング |

## Core Principles

1. **NoTracking by Default** — ほとんどのクエリは読み取り専用。変更追跡をグローバルに無効化し、書き込みが必要な場合のみ `.AsTracking()` でオプトインする。不要なオーバーヘッドを排除するため。
2. **Never Edit Migrations Manually** — マイグレーションの作成・削除・適用には必ず `dotnet ef` CLI コマンドを使用する。手動編集はスナップショットを破損するため。
3. **Dedicated Migration Service** — ホステッドサービスを使用してマイグレーション実行をアプリケーション起動から分離する。アプリがリクエストを受け付ける前にマイグレーションを完了させるため。
4. **ExecutionStrategy for Retries** — 一時的障害が発生しうる操作を `CreateExecutionStrategy()` でラップする。本番環境では一時的なデータベース障害は避けられないため。
5. **Explicit Updates with NoTracking** — NoTracking が有効な場合、保存前に明示的に `.Update()` を呼ぶか `.AsTracking()` を使用する。サイレント保存失敗は最も一般的な EF Core バグのため。

> **Values**: 基礎と型の追求（NoTracking やマイグレーション CLI という「型」を守ることで、安全で高速な DB 操作の基盤を築く）, 温故知新（EF Core の進化した機能を活かしつつ、変更追跡の基本原則を忠実に守る）

## Workflow: Apply EF Core Patterns

### Step 1: Configure NoTracking by Default

DbContext コンストラクタで NoTracking をグローバルに適用する。ほとんどのクエリは読み取り専用で、追跡は不要なオーバーヘッドを追加するため。

```csharp
public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
        // 読み取りパフォーマンス向上のため変更追跡をデフォルトで無効化
        ChangeTracker.QueryTrackingBehavior = QueryTrackingBehavior.NoTracking;
    }

    public DbSet<Order> Orders => Set<Order>();
    public DbSet<Customer> Customers => Set<Customer>();
}
```

**追跡が必要な場合：**

| シナリオ | 追跡する？ | 理由 |
|----------|-----------|------|
| UI でのデータ表示 | いいえ | 読み取り専用、更新不要 |
| API GET エンドポイント | いいえ | データ返却、変更なし |
| 単一エンティティの更新 | はい or `.Update()` | 変更を永続化する必要 |
| ナビゲーション付き複雑な更新 | はい | 追跡がリレーションを処理 |
| バッチ操作 | いいえ + `ExecuteUpdate` | 単一 SQL、より効率的 |

書き込み操作には `.AsTracking()` または明示的な `.Update()` を使用：

```csharp
// ✅ 明示的 Update — NoTracking でも動作
var order = await db.Orders.FirstOrDefaultAsync(o => o.Id == id);
order.Status = OrderStatus.Shipped;
db.Orders.Update(order);
await db.SaveChangesAsync();

// ✅ AsTracking — 特定クエリでオプトイン
var order = await db.Orders.AsTracking()
    .FirstOrDefaultAsync(o => o.Id == id);
order.Status = OrderStatus.Shipped;
await db.SaveChangesAsync();
```

> **Values**: 基礎と型の追求（NoTracking をデフォルトにする「型」が、読み取り性能の基盤を作る）

### Step 2: Manage Migrations with CLI

`dotnet ef` CLI コマンドのみを使用する。マイグレーションファイルの手動編集・削除・名前変更は絶対にしない。スナップショットファイルは累積状態を追跡しており、手動変更は破損を引き起こすため。

```bash
# 新しいマイグレーションを作成
dotnet ef migrations add AddCustomerTable \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# 未適用の最後のマイグレーションを削除
dotnet ef migrations remove \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# 保留中のすべてのマイグレーションを適用
dotnet ef database update \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# べき等 SQL スクリプトを生成（複数回実行しても安全）
dotnet ef migrations script --idempotent \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api
```

ロールバックコマンドとマルチコンテキストシナリオは [references/detailed-patterns.md](detailed-patterns.md) を参照。

> **Values**: 継続は力（CLI コマンドという決まった手順をコツコツ守ることで、マイグレーション事故を防ぐ）

### Step 3: Separate Migration Service with Aspire

メインアプリケーション起動前に実行される専用マイグレーションランナーを作成する。クリーンな分離により、リクエスト処理開始前にマイグレーションが完了することを保証するため。

```csharp
using Microsoft.EntityFrameworkCore;

// MigrationWorker.cs — マイグレーション実行後に停止
public class MigrationWorker(
    IServiceProvider serviceProvider,
    IHostApplicationLifetime lifetime,
    ILogger<MigrationWorker> logger) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        using var scope = serviceProvider.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        var strategy = db.Database.CreateExecutionStrategy();

        await strategy.ExecuteAsync(async () =>
        {
            await db.Database.MigrateAsync(ct);
            logger.LogInformation("Migrations applied successfully.");
        });

        lifetime.StopApplication();
    }
}
```

Aspire AppHost で依存関係の順序をオーケストレーション：

```csharp
// AppHost — マイグレーション完了後に API 起動
var db = builder.AddPostgres("postgres").AddDatabase("appdb");

var migrations = builder.AddProject<Projects.MyApp_MigrationService>("migrations")
    .WaitFor(db).WithReference(db);

builder.AddProject<Projects.MyApp_Api>("api")
    .WaitForCompletion(migrations)  // マイグレーション完了を待機
    .WithReference(db);
```

完全な `Program.cs` セットアップとプロジェクト構造は [references/detailed-patterns.md](detailed-patterns.md) を参照。

> **Values**: 余白の設計（マイグレーションを分離することで、アプリ起動の順序に余白と安全性を確保する）

### Step 4: Handle Transient Failures

一時的障害に対する自動リトライのため、データベース操作を `CreateExecutionStrategy()` でラップする。ネットワークの瞬断や短時間のデータベース不可用は本番環境では通常の事象のため。

```csharp
// ✅ リトライ安全な更新
var strategy = db.Database.CreateExecutionStrategy();

await strategy.ExecuteAsync(async () =>
{
    var order = await db.Orders.AsTracking()
        .FirstOrDefaultAsync(o => o.Id == id);
    if (order is null) return;

    order.Status = OrderStatus.Shipped;
    await db.SaveChangesAsync();
});

// ✅ ストラテジーコールバック内のトランザクション
await strategy.ExecuteAsync(async () =>
{
    await using var tx = await db.Database.BeginTransactionAsync();
    try
    {
        // ... 操作 ...
        await db.SaveChangesAsync();
        await tx.CommitAsync();
    }
    catch
    {
        await tx.RollbackAsync();
        throw;
    }
});
```

> **Values**: ニュートラルな視点（一時的障害を「異常」ではなく「日常」と捉え、偏りなく対処する設計）

### Step 5: Optimize with Bulk Operations and Query Splitting

エンティティをロードする代わりに `ExecuteUpdateAsync` / `ExecuteDeleteAsync` でバルク操作を適用する。複数の `Include()` 呼び出しによるデカルト積爆発を防ぐため、`SplitQuery` をグローバルに適用する。

```csharp
// ❌ 遅い — すべてのエンティティをメモリにロード
var expired = await db.Orders
    .Where(o => o.ExpiresAt < DateTimeOffset.UtcNow).ToListAsync();
foreach (var o in expired) o.Status = OrderStatus.Expired;
await db.SaveChangesAsync();

// ✅ 高速 — 単一 SQL UPDATE、エンティティロードなし
await db.Orders
    .Where(o => o.ExpiresAt < DateTimeOffset.UtcNow)
    .ExecuteUpdateAsync(s => s
        .SetProperty(o => o.Status, OrderStatus.Expired)
        .SetProperty(o => o.UpdatedAt, DateTimeOffset.UtcNow));

// ✅ 高速 — 単一 SQL DELETE
await db.Orders
    .Where(o => o.Status == OrderStatus.Cancelled)
    .ExecuteDeleteAsync();
```

**クエリ分割の設定：**

```csharp
// グローバル SplitQuery — デカルト積爆発を防止
services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString, npgsql =>
        npgsql.UseQuerySplittingBehavior(QuerySplittingBehavior.SplitQuery)));

// 単一クエリが効率的な場合のクエリ単位オーバーライド
var orders = await db.Orders
    .Include(o => o.Items)
    .Include(o => o.Payments)
    .AsSingleQuery()
    .ToListAsync();
```

| 動作 | メリット | デメリット |
|------|---------|-----------|
| SplitQuery | デカルト積爆発なし、大コレクションに有利 | 複数ラウンドトリップ |
| SingleQuery | 単一ラウンドトリップ、トランザクション一貫性 | デカルト積爆発リスク |

> **Values**: 成長の複利（バルク操作と SplitQuery の習得が、すべてのクエリ設計の品質を底上げする）

## Good Practices

- ✅ NoTracking をデフォルトにし、書き込み時のみ追跡をオプトイン
- ✅ マイグレーション管理には `dotnet ef` CLI コマンドのみを使用
- ✅ 本番デプロイメントには専用マイグレーションサービスを実装
- ✅ 本番環境のすべてのデータベース操作に `CreateExecutionStrategy()` を使用
- ✅ バルクデータ操作には `ExecuteUpdateAsync` / `ExecuteDeleteAsync` を使用
- ✅ グローバルに `SplitQuery` を使用し、適切な場合に `AsSingleQuery()` でオーバーライド
- ✅ 長寿命サービスやアクターには `IDbContextFactory<T>` を実装
- ✅ ASP.NET Core ではスコープ付き DbContext ライフタイムを使用（HTTP リクエストごとに1つ）
- ✅ すべての非同期データベースメソッドで `CancellationToken` を受け入れる
- ✅ 手動作成した DbContext インスタンスには `await using` を使用

## Common Pitfalls

1. **NoTracking での Update 忘れ** — エンティティを変更して `.Update()` や `.AsTracking()` なしで `SaveChangesAsync()` を呼び出す。変更がサイレントに失われる。対策：常に明示的にエンティティの更新をマークする。
2. **N+1 クエリ問題** — `.Include()` なしでループ内のナビゲーションプロパティにアクセスする。対策：`.Include()` でEager Loadingするか、明示的な `.Select()` プロジェクションを使用。
3. **非同期のブロッキング** — 非同期コンテキストで `.Result` や `.Wait()` を呼ぶとデッドロックが発生する。対策：呼び出しチェーン全体で一貫して `await` を使用。
4. **ループ内のクエリ** — 単一の `Where` + `Contains` の代わりにイテレーションごとに `FindAsync` を実行する。対策：`Where(o => ids.Contains(o.Id))` でクエリをバッチ化。
5. **マイグレーションの手動編集** — マイグレーションファイルの直接編集・削除はモデルスナップショットを破損する。対策：`dotnet ef migrations remove` で最後のマイグレーションを取り消す。

## Anti-Patterns

### ❌ Silent Save with NoTracking → ✅ Explicit Update

```csharp
// ❌ BAD — エンティティが追跡されていない、SaveChanges は何もしない
var customer = await db.Customers.FindAsync(id);
customer.Name = "New Name";
await db.SaveChangesAsync(); // サイレント失敗！

// ✅ GOOD — 明示的に変更済みとマーク
var customer = await db.Customers.FindAsync(id);
customer.Name = "New Name";
db.Customers.Update(customer);
await db.SaveChangesAsync();
```

### ❌ Loading Entities for Bulk Ops → ✅ ExecuteUpdate

```csharp
// ❌ BAD — すべてのエンティティをメモリにロード、N+1 書き込み
var orders = await db.Orders.Where(o => o.IsExpired).ToListAsync();
foreach (var o in orders) { o.Status = OrderStatus.Expired; }
await db.SaveChangesAsync();

// ✅ GOOD — 単一 SQL UPDATE 文
await db.Orders.Where(o => o.IsExpired)
    .ExecuteUpdateAsync(s => s.SetProperty(o => o.Status, OrderStatus.Expired));
```

### ❌ Manual Migration File Deletion → ✅ CLI Remove

```bash
# ❌ BAD — モデルスナップショットを破損
rm Migrations/20240101_AddCustomerTable.cs

# ✅ GOOD — 安全にマイグレーションを削除しスナップショットを更新
dotnet ef migrations remove
```

### ❌ N+1 Lazy Loading → ✅ Eager Loading

```csharp
// ❌ BAD — 顧客ごとに1クエリ
var customers = await db.Customers.ToListAsync();
foreach (var c in customers) { var orders = c.Orders; } // N+1!

// ✅ GOOD — Include で単一クエリ
var customers = await db.Customers
    .Include(c => c.Orders)
    .ToListAsync();
```

## Quick Reference

### DbContext Lifetime by Scenario

| シナリオ | ライフタイム | 登録方法 |
|----------|------------|---------|
| ASP.NET Core コントローラ | スコープ（リクエスト単位） | `AddDbContext<T>()` |
| バックグラウンドサービス | 作業単位ごとにスコープ作成 | `IServiceProvider.CreateScope()` |
| アクター / 長寿命オブジェクト | 操作ごとにファクトリ | `AddDbContextFactory<T>()` |

### NoTracking Decision Guide

| 操作 | アプローチ | 理由 |
|------|----------|------|
| 読み取り専用クエリ | NoTracking（デフォルト） | オーバーヘッドなし |
| 単一エンティティ更新 | `.AsTracking()` or `.Update()` | 変更検出が必要 |
| バルク更新 / 削除 | `ExecuteUpdate` / `ExecuteDelete` | 単一 SQL 文 |
| 複雑なナビゲーション書き込み | `.AsTracking()` | リレーション処理 |

### Migration Command Cheat Sheet

| タスク | コマンド |
|--------|---------|
| マイグレーション作成 | `dotnet ef migrations add <Name>` |
| 最後のマイグレーション削除 | `dotnet ef migrations remove` |
| 保留中をすべて適用 | `dotnet ef database update` |
| SQL スクリプト生成 | `dotnet ef migrations script --idempotent` |
| 特定マイグレーションにロールバック | `dotnet ef database update <PreviousName>` |

## Resources

- [EF Core ドキュメント](https://learn.microsoft.com/ja-jp/ef/core/)
- [EF Core の変更追跡](https://learn.microsoft.com/ja-jp/ef/core/change-tracking/)
- [ExecuteUpdate と ExecuteDelete](https://learn.microsoft.com/ja-jp/ef/core/saving/execute-insert-update-delete)
- [クエリ分割](https://learn.microsoft.com/ja-jp/ef/core/querying/single-split-queries)
- [.NET Aspire 概要](https://learn.microsoft.com/ja-jp/dotnet/aspire/get-started/aspire-overview)
- [references/detailed-patterns.md](detailed-patterns.md) — 完全なマイグレーションサービスコード、DbContext ライフタイム例、テストパターン
