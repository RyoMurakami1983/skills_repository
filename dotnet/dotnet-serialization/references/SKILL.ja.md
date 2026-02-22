<!-- このドキュメントは dotnet-serialization の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-serialization
description: >
  .NET アプリケーションに最適なシリアライゼーション形式を選択し、安全に実装する。
  API・メッセージング・永続化のシリアライゼーション選定、Newtonsoft.Jsonからの移行、
  ソースジェネレーターによるAOT対応シリアライゼーション実装時に使用。
metadata:
  author: RyoMurakami1983
  tags: [dotnet, serialization, json, protobuf, messagepack, aot, system-text-json]
  invocable: false
---

# .NET シリアライゼーション

REST API・gRPC・アクターメッセージング・イベントソーシングに対応するシリアライゼーション形式の選定・実装・進化。System.Text.Json ソースジェネレーター、Protocol Buffers、MessagePack、Newtonsoft.Json からの移行、ワイヤー互換性パターンをカバーする。

## When to Use This Skill

以下の場合にこのスキルを使用してください：

- REST API、gRPC サービス、またはアクターメッセージングシステムのシリアライゼーション形式を選択するとき
- System.Text.Json ソースジェネレーターで AOT 対応 JSON シリアライゼーションを実装するとき
- 既存コードベースを Newtonsoft.Json から System.Text.Json に段階的に移行するとき
- 読み手を壊さずに進化する必要がある分散システムのワイヤーフォーマットを設計するとき
- Protocol Buffers や MessagePack による高性能バイナリシリアライゼーションを実装するとき
- Akka.NET アクターシステムのシリアライゼーションバインディングをスキーマベース形式で構成するとき
- パフォーマンスクリティカルなホットパスでシリアライゼーションのスループットとペイロードサイズを最適化するとき

---

## Related Skills

- **`dotnet-project-structure`** — NuGet パッケージ管理と Directory.Build.props のセットアップ
- **`dotnet-type-design-performance`** — sealed クラス、readonly 構造体、record 型の設計
- **`dotnet-csharp-concurrency-patterns`** — 並行システムでのシリアライゼーション向け非同期パターン
- **`dotnet-extensions-dependency-injection`** — シリアライザーコンテキストの DI コンテナ登録

---

## Core Principles

1. **Schema Over Reflection（スキーマ優先）** — リフレクションベースではなくスキーマベース（Protobuf、MessagePack、ソースジェネレーターJSON）を使用し、安全性・性能・AOT互換性を確保（基礎と型）
2. **Explicit Wire Contracts（明示的ワイヤー契約）** — フィールド番号、プロパティ名、ディスクリミネーターを明示的に定義し、.NET 型名をペイロードに埋め込まない（温故知新）
3. **Read Before Write（読み手先行デプロイ）** — 新フォーマットのデシリアライザーをシリアライザーの前にデプロイし、ローリングアップグレード時の後方互換性を確保（余白の設計）
4. **Tolerant Reader（寛容な読み手）** — 未知のフィールドを安全に無視するよう構成し、プロデューサーが既存リーダーを壊さずに新データを追加可能に（ニュートラルな視点）
5. **Compile-Time Verification（コンパイル時検証）** — ランタイム発見よりソースジェネレーターとコンパイル時契約を優先し、シリアライゼーションエラーを早期に検出（基礎と型）

---

## Workflow: Choose and Implement .NET Serialization

### Step 1 — シリアライゼーション要件の評価

プロセス境界を越えてデータを送信する新しいサービスや機能を開始するときに使用します。

シナリオを分類して適切な形式を決定します：

| シナリオ | 人間可読？ | バージョニング必要度 | 性能 | 推奨形式 |
|----------|-----------|-------------------|------|----------|
| REST API | ✅ はい | 中 | 中 | System.Text.Json（ソースジェネレーター） |
| gRPC | いいえ | 高 | 高 | Protocol Buffers |
| アクターメッセージング | いいえ | 高 | 非常に高 | MessagePack または Protobuf |
| イベントソーシング | いいえ | 最重要 | 高 | Protobuf または MessagePack |
| キャッシュ | いいえ | 低 | 非常に高 | MessagePack |
| 設定ファイル | ✅ はい | 低 | 低 | JSON（System.Text.Json） |

**なぜ最初に分類するのか**: 誤った形式の選択は複利的に技術的負債を生む — 本番システムで保存済みデータのワイヤーフォーマットを移行するコストは極めて高い。

> **Values**: 基礎と型の追求（要件分析はすべての設計判断の基盤）

### Step 2 — System.Text.Json ソースジェネレーターの実装

REST API や AOT 互換性が必要な JSON シナリオで使用します。

シリアライズ可能なすべての型を `JsonSerializerContext` に登録します：

```csharp
using System.Text.Json;
using System.Text.Json.Serialization;

// ソースジェネレーション用にすべての型を登録
[JsonSerializable(typeof(Order))]
[JsonSerializable(typeof(OrderItem))]
[JsonSerializable(typeof(List<Order>))]
[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
public partial class AppJsonContext : JsonSerializerContext { }
```

生成されたコンテキストでシリアライズ・デシリアライズ：

```csharp
// ✅ ソースジェネレーターコンテキストでシリアライズ — リフレクションなし
var json = JsonSerializer.Serialize(order, AppJsonContext.Default.Order);

// ✅ ソースジェネレーターコンテキストでデシリアライズ
var order = JsonSerializer.Deserialize(json, AppJsonContext.Default.Order);
```

ASP.NET Core にコンテキストを登録：

```csharp
// ASP.NET Core パイプラインに接続
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.TypeInfoResolverChain.Insert(0, AppJsonContext.Default);
});
```

**なぜソースジェネレーターか**: ランタイムリフレクション不要、AOT 互換、高速シリアライゼーション、トリム安全 — リンカーが必要なコードを正確に把握する。

> **Values**: 基礎と型（ソースジェネレーターがランタイムの魔術をコンパイル時の確実性に置き換える）

### Step 3 — Protocol Buffers によるバージョン管理されたワイヤーフォーマットの実装

gRPC サービス、アクターメッセージ、イベントソーシングシステムの安全な進化が必要なときに使用します。

パッケージのインストール：

```bash
dotnet add package Google.Protobuf
dotnet add package Grpc.Tools
```

明示的なフィールド番号でスキーマを定義：

```protobuf
// orders.proto
syntax = "proto3";

message Order {
    string id = 1;
    string customer_id = 2;
    repeated OrderItem items = 3;
    int64 created_at_ticks = 4;
    string notes = 5;  // v2で追加 — 旧リーダーは無視する
}

message OrderItem {
    string product_id = 1;
    int32 quantity = 2;
    int64 price_cents = 3;
}
```

バージョニングルールを厳守：

| 操作 | 安全？ | 理由 |
|------|--------|------|
| 新番号で新フィールド追加 | ✅ はい | 旧リーダーは未知フィールドをスキップ |
| フィールド削除＋番号予約 | ✅ はい | `reserved 2;` で再利用を防止 |
| フィールド型の変更 | ❌ いいえ | バイナリエンコーディングが非互換 |
| フィールド番号の再利用 | ❌ いいえ | 旧データが誤った型でデコードされる |

> **Values**: 温故知新（Protobuf のフィールド番号設計は数十年の実績がある安定性を持つ）

### Step 4 — MessagePack による高性能シリアライゼーションの実装

コンパクトなペイロードと最大スループットが重要な場合に使用 — アクターメッセージング、キャッシュ、リアルタイムシステム。

パッケージのインストール：

```bash
dotnet add package MessagePack
dotnet add package MessagePack.Annotations
```

明示的なキーインデックスでコントラクトを定義：

```csharp
using MessagePack;

[MessagePackObject]
public sealed class Order
{
    [Key(0)] public required string Id { get; init; }
    [Key(1)] public required string CustomerId { get; init; }
    [Key(2)] public required IReadOnlyList<OrderItem> Items { get; init; }
    [Key(3)] public required DateTimeOffset CreatedAt { get; init; }
    [Key(4)] public string? Notes { get; init; }  // v2 — 旧リーダーはスキップ
}

// ✅ シリアライズ/デシリアライズ — コンパクトバイナリ形式
var bytes = MessagePackSerializer.Serialize(order);
var order = MessagePackSerializer.Deserialize<Order>(bytes);
```

AOT 互換のためソースジェネレーターを使用：

```csharp
[MessagePackObject]
public partial class Order { }  // partial でソースジェネレーター有効化

var options = MessagePackSerializerOptions.Standard
    .WithResolver(CompositeResolver.Create(
        GeneratedResolver.Instance,
        StandardResolver.Instance));
```

**なぜ MessagePack か**: JSON と比較して 2-5 倍高速、30-50% 小さいペイロード — 高スループットアクターシステムで効果は大きい。

> **Values**: 継続は力（性能向上が高スループットシステムのすべてのメッセージに複利的に蓄積される）

### Step 5 — バージョン間のワイヤー互換性の確保

ローリングアップグレード環境で新しいシリアライゼーション形式をデプロイするときに使用します。

**Tolerant Reader** — 未知フィールドを無視するようコンシューマーを構成：

```csharp
// System.Text.Json: マッピングされていないメンバーをスキップ
var options = new JsonSerializerOptions
{
    UnmappedMemberHandling = JsonUnmappedMemberHandling.Skip
};
// Protobuf/MessagePack: 自動 — 設計上、未知フィールドはスキップされる
```

**Read Before Write** — デシリアライザーをシリアライザーの前にデプロイ：

```csharp
// フェーズ1: すべてのノードに V2 リーダーをデプロイ
public Order Deserialize(byte[] data, string manifest) => manifest switch
{
    "Order.V1" => DeserializeV1(data),
    "Order.V2" => DeserializeV2(data),  // NEW — V2 を読める
    _ => throw new NotSupportedException($"Unknown manifest: {manifest}")
};

// フェーズ2: V2 ライターを有効化（次リリース、全ノードが V2 を読めた後）
public (byte[] data, string manifest) Serialize(Order order) =>
    _useV2Format
        ? (SerializeV2(order), "Order.V2")
        : (SerializeV1(order), "Order.V1");
```

**型名をワイヤーペイロードに埋め込まない**：

```csharp
// ❌ ペイロード内の型名 — クラス名変更でワイヤーフォーマットが壊れる
{ "$type": "MyApp.Order, MyApp.Core", "id": "123" }

// ✅ 明示的ディスクリミネーター — リファクタリング安全
{ "type": "order", "id": "123" }
```

> **Values**: 余白の設計（Read-Before-Write パターンが安全な進化の余地を生む）

### Step 6 — Newtonsoft.Json から System.Text.Json への移行

既存コードベースで Newtonsoft.Json を System.Text.Json に置き換えるときに使用します。

主要な差異のマッピング：

| Newtonsoft | System.Text.Json | 対応方法 |
|------------|------------------|----------|
| `JsonProperty` | `JsonPropertyName` | 属性の変更 |
| `$type` ポリモーフィズム | `[JsonDerivedType]`（.NET 7+） | 明示的ディスクリミネーター |
| `DefaultValueHandling` | `DefaultIgnoreCondition` | API の変更 |
| プライベートセッター | `[JsonInclude]` | 明示的オプトイン |

モデルクラスの移行：

```csharp
// ❌ Newtonsoft（リフレクションベース）
public class Order
{
    [JsonProperty("order_id")]
    public string Id { get; set; }

    [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
    public string? Notes { get; set; }
}

// ✅ System.Text.Json（ソースジェネレーター互換）
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

ディスクリミネーターによるポリモーフィズム（.NET 7+）：

```csharp
// ✅ 明示的ディスクリミネーター — 型安全、リファクタリング安全
[JsonDerivedType(typeof(CreditCardPayment), "credit_card")]
[JsonDerivedType(typeof(BankTransferPayment), "bank_transfer")]
public abstract record Payment(decimal Amount);

public sealed record CreditCardPayment(decimal Amount, string Last4)
    : Payment(Amount);
public sealed record BankTransferPayment(decimal Amount, string AccountNumber)
    : Payment(Amount);
// シリアライズ結果: { "$type": "credit_card", "amount": 100, "last4": "1234" }
```

> **Values**: 温故知新（レガシーからモダンへ、既存のコンシューマーを壊さず段階的に移行）

---

## Good Practices

- ✅ すべての System.Text.Json シリアライゼーションにソースジェネレーターを使用 — リフレクションを排除
- ✅ バージョン安全性のため明示的フィールド番号を使用（Protobuf `= N`、MessagePack `[Key(N)]`）
- ✅ 不変メッセージコントラクトに `sealed record` 型を使用 — 偶発的変更を防止
- ✅ 削除フィールド番号を予約（`reserved 2;`）して偶発的再利用を防止
- ✅ 新ワイヤーフォーマットバージョンではデシリアライザーをシリアライザーの前にデプロイ
- ✅ `UnmappedMemberHandling.Skip` を設定し、コンシューマーが未知フィールドを許容するように

---

## Common Pitfalls

| 落とし穴 | 問題 | 対処法 |
|----------|------|--------|
| ソースジェネレーターコンテキスト未設定 | リフレクションにフォールバックし AOT が壊れる | すべての型を `[JsonSerializable]` に追加 |
| Protobuf フィールド番号の再利用 | 旧データが誤った型でデコードされる | 削除フィールドに `reserved` を使用 |
| .NET 型名の埋め込み | クラス名変更でワイヤーフォーマットが壊れる | 明示的文字列ディスクリミネーターを使用 |
| リーダーより先にライターをデプロイ | 旧ノードが新フォーマットを解析できない | 常にリーダーを先にデプロイ |
| `BinaryFormatter` の使用 | セキュリティ脆弱性（CVE）、非推奨 | MessagePack または Protobuf に置換 |

---

## Anti-Patterns

### ❌ ホットパスでのリフレクションベースシリアライゼーション

高スループットコードパスで `JsonConvert.SerializeObject()` やリフレクションベースの `JsonSerializer.Serialize()` を使用する設計。呼び出しごとにランタイム型検査が発生し、AOT コンパイルを妨げ、GC 圧力を増加させる。

**代わりに**: ホットパスにはソースジェネレーター `JsonSerializerContext` またはバイナリ形式（MessagePack、Protobuf）を使用。

### ❌ 型名をワイヤー契約として使用

Newtonsoft.Json で `TypeNameHandling.All` を設定するか、アセンブリ修飾型名をペイロードに埋め込むアーキテクチャ。シリアライズされたデータを内部クラス構造に結合し、名前変更・名前空間移動・アセンブリ変更でデシリアライゼーションが壊れる。

**代わりに**: `[JsonDerivedType]` による明示的文字列ディスクリミネーター、または Protobuf `oneof` を使用。

### ❌ ビッグバン形式移行

すべてのプロデューサーとコンシューマーを1回のデプロイで新シリアライゼーション形式に切り替えるレイヤー横断的変更。ローリングアップグレード中に異なるバージョンのノードが通信する際に障害を引き起こす。

**代わりに**: Read-Before-Write パターンを使用 — まずリーダーをデプロイし、次にライターを有効化。

---

## Quick Reference

| 判断ポイント | 推奨 |
|-------------|------|
| REST API シリアライゼーション | System.Text.Json + ソースジェネレーター |
| gRPC ワイヤーフォーマット | Protocol Buffers（ネイティブ） |
| アクター/メッセージング形式 | MessagePack または Protobuf |
| イベントストア形式 | Protobuf（最良のバージョニング） |
| キャッシュシリアライゼーション | MessagePack（最速、最小） |
| 設定/ログ形式 | System.Text.Json（人間可読） |
| AOT 互換性が必要 | ソースジェネレーター（JSON）または Protobuf/MessagePack |
| Newtonsoft からの移行 | System.Text.Json + `[JsonDerivedType]`（ポリモーフィズム用） |

**性能比較**（相対スループット）：

| 形式 | 速度 | ペイロードサイズ | AOT 互換 |
|------|------|----------------|----------|
| MessagePack | ★★★★★ | ★★★★★ | ✅ はい |
| Protobuf | ★★★★★ | ★★★★★ | ✅ はい |
| System.Text.Json（ソースジェネレーター） | ★★★★☆ | ★★★☆☆ | ✅ はい |
| System.Text.Json（リフレクション） | ★★★☆☆ | ★★★☆☆ | ❌ いいえ |
| Newtonsoft.Json | ★★☆☆☆ | ★★★☆☆ | ❌ いいえ |

---

## Resources

- **System.Text.Json Source Generation**: https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/source-generation
- **Protocol Buffers**: https://protobuf.dev/
- **MessagePack-CSharp**: https://github.com/MessagePack-CSharp/MessagePack-CSharp
- **Akka.NET Serialization**: https://getakka.net/articles/networking/serialization.html
- **Wire Compatibility**: https://getakka.net/community/contributing/wire-compatibility.html
