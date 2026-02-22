---
name: dotnet-csharp-concurrency-patterns
description: >
  .NET の並行処理抽象を正しく選択する — async/await、Channels、Akka.NET Streams、
  Reactive Extensions、Akka.NET Actors。Use when 並行処理の設計判断、ツール選定、
  または複数エンティティの状態管理が必要な場合。
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [csharp, concurrency, async-await, channels, akka-net, reactive-extensions]
  invocable: false
---

<!-- このドキュメントは dotnet-csharp-concurrency-patterns の日本語版です。英語版: ../SKILL.md -->

# .NET Concurrency: Choosing the Right Tool

.NET における並行処理の正しい抽象選択ガイド。I/O 向けの async/await から、プロデューサー/コンシューマー向けの Channels、状態管理向けの Akka.NET Actors まで。ロックや手動同期は最後の手段。

**略語**: I/O (Input/Output)、CPU (Central Processing Unit)、Rx (Reactive Extensions)、DI (Dependency Injection)、UI (User Interface)。

## When to Use This Skill

- .NET アプリケーションで I/O バウンドまたは CPU バウンドの並行処理方法を決定する場合
- async/await、Channels、Akka.NET Streams、Actors のどれを使うか評価する場合
- バックプレッシャーと制限付きバッファリングを持つプロデューサー/コンシューマーパターンの実装
- Actor モデルパターンを使った数千エンティティの独立した状態管理
- バッチ処理、スロットリング、マージを含むサーバーサイドストリーム処理パイプラインの設計
- デバウンス、スロットリング、複数ソースの結合を用いた UI イベントストリームの合成

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-modern-csharp-coding-standards` | Records、パターンマッチング、Result\<T\> エラーハンドリング |
| `dotnet-type-design-performance` | Span\<T\>、Memory\<T\>、ゼロアロケーションパターン |
| `dotnet-project-structure` | ソリューション構成、名前空間規約、ファイル構成 |

## Core Principles

1. **Start Simple, Escalate When Needed** — async/await をデフォルトとし、シンプルなツールで対応できない具体的な必要性がある場合のみ、Channels、Streams、Actors へ段階的に進む。
2. **Avoid Shared Mutable State** — 不変データ、メッセージパッシング、隔離された状態（Actor）は、並行処理バグのカテゴリ全体を排除する。ロックに手を伸ばす前に設計を見直す。
3. **Use the Right Level of Abstraction** — 問題にツールを合わせる：I/O 待機 → async/await、ワークキュー → Channels、ストリーム処理 → Akka.NET Streams、状態管理 → Actors。
4. **Prefer Message Passing Over Synchronization** — Channels と Actors はメッセージを通じてアクセスを直列化する。ロックは最後の手段であり、低レベルのインフラコードに限定する。
5. **Always Support Cancellation** — すべての非同期メソッドで `CancellationToken` を受け取る。協調的キャンセルはレスポンシブで行儀のよい .NET アプリに不可欠。

> **Values**: 基礎と型の追求（async/await という基礎を徹底し、必要な時だけ高度な抽象へ段階的に進む）, ニュートラルな視点（ツールに偏らず、問題に応じて最適な抽象度を選択する）

## Workflow: Choose and Apply Concurrency Patterns

### Step 1: Use async/await for I/O Operations

すべての I/O バウンド操作のデフォルト選択として async/await を適用する。独立した並列操作には `Task.WhenAll` を使用。なぜ：async/await は追加の複雑さなしに、ほとんどの並行処理ニーズに対応できる。

```csharp
// シンプルな非同期 I/O — 常に CancellationToken を受け取る
public async Task<Order> GetOrderAsync(string orderId, CancellationToken ct)
{
    var order = await _database.GetAsync(orderId, ct);
    var customer = await _customerService.GetAsync(order.CustomerId, ct);
    return order with { Customer = customer };
}

// Task.WhenAll で独立した操作を並列実行
public async Task<Dashboard> LoadDashboardAsync(string userId, CancellationToken ct)
{
    var ordersTask = _orderService.GetRecentOrdersAsync(userId, ct);
    var notificationsTask = _notificationService.GetUnreadAsync(userId, ct);
    var statsTask = _statsService.GetUserStatsAsync(userId, ct);

    await Task.WhenAll(ordersTask, notificationsTask, statsTask);

    return new Dashboard(
        Orders: await ordersTask,
        Notifications: await notificationsTask,
        Stats: await statsTask);
}
```

**基本ルール：** 常に `CancellationToken` を受け取る。ライブラリコードでは `ConfigureAwait(false)` を使用。非同期コードをブロックしない（`.Result` や `.Wait()` は禁止）。

> **Values**: 基礎と型の追求（async/await を基本の型として徹底し、すべての応用の土台とする）

### Step 2: Scale CPU Work with Parallel.ForEachAsync

CPU バウンドの並列処理に制御された並行度で `Parallel.ForEachAsync` を適用する。なぜ：非同期サポートと制限付き並列度を組み合わせ、スレッドプール枯渇を防止する。

```csharp
public async Task ProcessOrdersAsync(IEnumerable<Order> orders, CancellationToken ct)
{
    await Parallel.ForEachAsync(
        orders,
        new ParallelOptions
        {
            MaxDegreeOfParallelism = Environment.ProcessorCount,
            CancellationToken = ct
        },
        async (order, token) =>
        {
            await ProcessOrderAsync(order, token);
        });
}
```

**使用場面：** コレクション全体の CPU バウンド処理。**避ける場面：** 純粋な I/O（async/await で十分）、順序が重要、バックプレッシャーが必要。

> **Values**: 継続は力（並列処理の基本パターンを身につけ、日常的な処理の高速化に活かす）

### Step 3: Decouple with System.Threading.Channels

プロデューサー/コンシューマーパターン、ワークキュー、コンポーネント速度の分離に `Channel<T>` を適用する。バックプレッシャーには制限付きチャネルを使用。なぜ：Channels はプロデューサーとコンシューマー間のスレッドセーフでロックフリーな通信を提供する。

```csharp
public class OrderProcessor
{
    private readonly Channel<Order> _channel;

    public OrderProcessor()
    {
        // 制限付きチャネルでバックプレッシャーを実現
        _channel = Channel.CreateBounded<Order>(new BoundedChannelOptions(100)
        {
            FullMode = BoundedChannelFullMode.Wait
        });
    }

    // プロデューサー
    public async Task EnqueueOrderAsync(Order order, CancellationToken ct)
        => await _channel.Writer.WriteAsync(order, ct);

    // コンシューマー（バックグラウンドタスクとして実行）
    public async Task ProcessOrdersAsync(CancellationToken ct)
    {
        await foreach (var order in _channel.Reader.ReadAllAsync(ct))
        {
            await ProcessOrderAsync(order, ct);
        }
    }

    public void Complete() => _channel.Writer.Complete();
}
```

**使用場面：** プロデューサー/コンシューマーの速度分離、バックプレッシャー付きバッファリング、複数ワーカーへのファンアウト。**避ける場面：** 複雑なストリーム操作（バッチ、ウィンドウ処理）やエンティティ毎の状態管理。

詳細は [references/channel-patterns.md](references/channel-patterns.md) を参照。

> **Values**: 成長の複利（Channel の習得がメッセージパッシングの理解を深め、Actor モデルへの橋渡しになる）

### Step 4: Process Streams with Akka.NET Streams or Rx

サーバーサイドのバックプレッシャー、バッチ処理、スロットリングには Akka.NET Streams を適用する。UI イベント合成には Reactive Extensions (Rx) を適用する。なぜ：これらのツールは Channels では綺麗に表現できない複雑なストリーム操作を扱う。

```csharp
using Akka.Streams;
using Akka.Streams.Dsl;

// サーバーサイド：タイムアウト付きバッチ処理
public Source<IReadOnlyList<Event>, NotUsed> BatchEvents(
    Source<Event, NotUsed> events)
{
    return events
        .GroupedWithin(100, TimeSpan.FromSeconds(1))
        .Select(batch => batch.ToList() as IReadOnlyList<Event>);
}

// クライアントサイド：Rx による検索候補表示
public IObservable<IList<SearchResult>> CreateSearch(
    IObservable<string> searchText, ISearchService searchService)
{
    return searchText
        .Throttle(TimeSpan.FromMilliseconds(300))
        .DistinctUntilChanged()
        .Where(text => text.Length >= 3)
        .SelectMany(text => searchService.SearchAsync(text).ToObservable());
}
```

| シナリオ | Rx | Akka.NET Streams |
|----------|----|--------------------|
| UI イベント（デバウンス、スロットル） | ✅ 最適 | 過剰 |
| クライアントサイド合成 | ✅ 最適 | 過剰 |
| サーバーサイドパイプライン | 限定的 | ✅ バックプレッシャーに優れる |
| 分散処理 | ❌ 非対応 | ✅ 設計目的 |

詳細は [references/stream-patterns.md](references/stream-patterns.md) を参照。

> **Values**: 温故知新（Rx の成熟したイベント合成技術と Akka.NET の分散ストリーム処理を、用途に応じて使い分ける）

### Step 5: Manage Stateful Entities with Akka.NET Actors

エンティティ毎の隔離された状態、`Become()` による状態マシン、分散エンティティ管理が必要な場合に Akka.NET Actors を適用する。なぜ：Actor は自然な隔離を提供し、各エンティティが独自の Actor を持ち、ロックが不要になる。

```csharp
// エンティティ毎の Actor：各注文が隔離された状態を持つ
public class OrderActor : ReceiveActor
{
    private OrderState _state;

    public OrderActor(string orderId)
    {
        _state = new OrderState(orderId);

        Receive<AddItem>(msg =>
        {
            _state = _state.AddItem(msg.Item);
            Sender.Tell(new ItemAdded(msg.Item));
        });

        Receive<Checkout>(msg =>
        {
            if (_state.CanCheckout)
            {
                _state = _state.Checkout();
                Sender.Tell(new CheckoutSucceeded(_state.Total));
            }
            else
            {
                Sender.Tell(new CheckoutFailed("Cart is empty"));
            }
        });

        Receive<GetState>(_ => Sender.Tell(_state));
    }
}
```

| シナリオ | なぜ Actor？ |
|----------|-------------|
| 独立状態を持つ多数のエンティティ | 自然な隔離、ロック不要 |
| 状態マシン | `Become()` が遷移を優雅にモデル化 |
| 監視要件 | 親 Actor が子を障害時に再起動 |
| 分散システム | Cluster Sharding がノード間に分散 |

**Actor の思考法：** 数千のエンティティが独立した状態、ライフサイクル、プッシュベースの更新、障害隔離を必要とする場合に使用。いずれにも該当しなければ、よりシンプルなツールを使用する。

詳細は [references/actor-patterns.md](references/actor-patterns.md) を参照。

> **Values**: 余白の設計（Actor の隔離境界が、各エンティティに独立した変更・障害の余白を与える）

## Good Practices

- ✅ I/O 操作のデフォルト並行処理ツールとして async/await を使用
- ✅ すべての非同期メソッドシグネチャで `CancellationToken` を受け取る
- ✅ ライブラリコードでデッドロック回避のため `ConfigureAwait(false)` を使用
- ✅ バックプレッシャー付きプロデューサー/コンシューマーに制限付き `Channel<T>` を使用
- ✅ `Task.Run(async () => ...)` の代わりに非同期ローカル関数を使用
- ✅ スレッドセーフなコレクションに `ConcurrentBag<T>` や `ConcurrentDictionary<K,V>` を使用
- ✅ UI イベントには Rx、サーバーサイドには Akka.NET Streams を使用
- ✅ 独立した状態・ライフサイクル・障害隔離が必要なエンティティには Actor を使用

## Common Pitfalls

1. **非同期コードのブロック** — `.Result` や `.Wait()` はデッドロックを引き起こす。コールチェーン全体で `async` を徹底する。
2. **無制限チャネル** — メモリを考慮せず `Channel.CreateUnbounded<T>()` を使用。`BoundedChannelFullMode.Wait` 付き制限付きチャネルを使う。
3. **過剰設計** — async/await で十分なのに Actor や Streams に手を伸ばす。シンプルに始め、具体的な必要性がある場合のみ段階を上げる。
4. **手動スレッド作成** — 上位の抽象の代わりに `new Thread()` を使用。スレッドプールにスレッド管理を任せる。
5. **並列ループ内の共有可変状態** — `Parallel.ForEachAsync` 内で `List<T>.Add()` を使用。代わりに `ConcurrentBag<T>` を使う。
6. **ContinueWith チェーン** — シーケンスに `await` の代わりに `.ContinueWith()` を使用。非同期ローカル関数の方が明確で安全。

## Anti-Patterns

### ❌ Locks for Business Logic → ✅ Actor or Channel

```csharp
// ❌ BAD — 共有状態を保護するロック
private readonly object _lock = new();
private Dictionary<string, Order> _orders = new();
public void UpdateOrder(string id, Action<Order> update)
{
    lock (_lock) { if (_orders.TryGetValue(id, out var order)) update(order); }
}
// ✅ GOOD — エンティティ毎の Actor、ロック不要
// 各注文が隔離された状態を持つ OrderActor を使用
```

### ❌ Blocking in Async Code → ✅ Async All the Way

```csharp
// ❌ BAD — デッドロックのリスク
var result = GetDataAsync().Result;
// ✅ GOOD — async を徹底
var result = await GetDataAsync();
```

### ❌ Shared Mutable Collections → ✅ Thread-Safe Alternatives

```csharp
// ❌ BAD — 並列ループでの競合状態
var results = new List<Result>();
await Parallel.ForEachAsync(items, async (item, ct) =>
{
    results.Add(await ProcessAsync(item, ct)); // 競合状態！
});
// ✅ GOOD — ConcurrentBag を使用
var results = new ConcurrentBag<Result>();
```

### ❌ Manual Threads → ✅ Task-Based Abstractions

```csharp
// ❌ BAD — 手動スレッド管理
var thread = new Thread(() => ProcessOrders());
thread.Start();
// ✅ GOOD — タスクベースの抽象
_ = Task.Run(() => ProcessOrdersAsync(ct));
```

### ❌ Anonymous Async Lambda → ✅ Async Local Function

```csharp
// ❌ BAD — 匿名ラムダは意図を曖昧にする
_ = Task.Run(async () => { var r = await DoWorkAsync(); return new WorkCompleted(r); }).PipeTo(Self);
// ✅ GOOD — 名前付き非同期ローカル関数
async Task<WorkCompleted> ExecuteAsync()
{
    var result = await DoWorkAsync();
    return new WorkCompleted(result);
}
ExecuteAsync().PipeTo(Self);
```

## Quick Reference

### Decision Tree

```
何をしようとしている？
│
├─► I/O を待つ？                     → async/await
├─► コレクションを並列処理？          → Parallel.ForEachAsync
├─► プロデューサー/コンシューマー？    → Channel<T>
├─► UI イベント合成？                 → Reactive Extensions (Rx)
├─► サーバーサイドストリーム処理？     → Akka.NET Streams
├─► 状態マシン / エンティティ状態？   → Akka.NET Actors
├─► 複数の非同期操作を同時実行？      → Task.WhenAll
├─► 複数の非同期操作をレース？        → Task.WhenAny
└─► 定期的な処理？                    → PeriodicTimer
```

### Which Tool When

| ニーズ | ツール | 例 |
|--------|--------|-----|
| I/O 待機 | `async/await` | HTTP 呼び出し、データベースクエリ |
| 並列 CPU 処理 | `Parallel.ForEachAsync` | 画像処理、計算 |
| ワークキュー | `Channel<T>` | バックグラウンドジョブ処理 |
| UI イベント | Reactive Extensions | 検索候補表示、自動保存 |
| サーバーサイドバッチ | Akka.NET Streams | イベント集約、レート制限 |
| 状態マシン | Akka.NET Actors | 決済フロー、注文ライフサイクル |
| エンティティ管理 | Akka.NET Actors | 注文状態、ユーザーセッション |

### Escalation Path

```
async/await（ここから始める）
    ├─► 並列処理が必要？             → Parallel.ForEachAsync
    ├─► プロデューサー/コンシューマー？ → Channel<T>
    ├─► UI イベント合成が必要？       → Reactive Extensions
    ├─► サーバーサイドストリーミング？  → Akka.NET Streams
    └─► 状態管理が必要？              → Akka.NET Actors
```

## Resources

- [Async/Await Best Practices](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/)
- [System.Threading.Channels](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels)
- [Akka.NET Documentation](https://getakka.net/articles/intro/what-is-akka.html)
- [Reactive Extensions](https://github.com/dotnet/reactive)
- [references/channel-patterns.md](references/channel-patterns.md) — マルチコンシューマープール、高度な Channel パターン
- [references/stream-patterns.md](references/stream-patterns.md) — Akka.NET Streams パイプライン、Rx UI パターン
- [references/actor-patterns.md](references/actor-patterns.md) — Become 状態マシン、Cluster Sharding、Actor 内非同期ローカル関数
