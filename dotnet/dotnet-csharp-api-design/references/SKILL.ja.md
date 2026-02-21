<!-- このドキュメントは dotnet-csharp-api-design の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-csharp-api-design
description: >
  NuGet パッケージおよび分散システム向けの安定した互換性のあるパブリック API を設計する。
  API サーフェスの計画、破壊的変更の管理、ワイヤー互換性の実装、
  API 互換性に関するプルリクエストレビュー時に使用。
metadata:
  author: RyoMurakami1983
  tags: [dotnet, csharp, api-design, compatibility, versioning, nuget, wire-format]
  invocable: false
---

# C# パブリック API 設計と互換性

NuGet パッケージおよび分散システム向けのパブリック API サーフェスの設計・進化・保護。API 互換性、バイナリ互換性、ワイヤー互換性、拡張専用設計、API 承認テスト、非推奨化ワークフロー、セマンティックバージョニングをカバーする。

## When to Use This Skill

以下の場合にこのスキルを使用してください：

- NuGet パッケージまたは共有ライブラリの新しいパブリック API サーフェスをゼロから設計するとき
- パブリック型メンバーやメソッドシグネチャの追加・変更・削除を含むプルリクエストをレビューするとき
- ローリングアップグレードを安全に行う必要がある分散システムのワイヤーフォーマット変更を計画するとき
- PublicApiGenerator による API 承認テストを実装して偶発的な破壊的変更を防止するとき
- 既存のパブリック API を非推奨化し、コンシューマーを代替メソッドや型に移行するとき
- 破壊的変更と拡張を明確に伝えるバージョニング戦略を選択するとき
- 内部実装の詳細をカプセル化してパブリック API サーフェス領域を削減するとき
- 後方互換性と前方互換性を維持しながらシリアライズされたメッセージフォーマットを進化させるとき

---

## Related Skills

- **`dotnet-serialization`** — .NET のシリアライゼーション形式とワイヤー互換性パターン
- **`dotnet-type-design-performance`** — sealed クラス、readonly 構造体、record 型の設計
- **`dotnet-project-structure`** — NuGet パッケージ管理と Directory.Build.props のセットアップ
- **`dotnet-modern-csharp-coding-standards`** — C# 言語規約とコーディング標準

---

## Core Principles

1. **Extend-Only Design（拡張専用設計）** — リリース済みの API サーフェスを削除・変更せず、新しいオーバーロード、型、オプトイン機能を追加する。一度公開された機能は不変（基礎と型の追求）
2. **Explicit Compatibility Contracts（明示的な互換性契約）** — API（ソース）互換性、バイナリ互換性、ワイヤー互換性を区別する。いずれかを破るとコンシューマーにアップグレードの摩擦が生じる（温故知新）
3. **Deprecate Before Remove（削除前に非推奨化）** — 次のメジャーバージョンでの削除前に、少なくとも1つのマイナーバージョンで `[Obsolete]` をマークし、コンシューマーに移行の時間を与える（余白の設計）
4. **Automated Surface Verification（自動サーフェス検証）** — リリース後の発見ではなく、ビルド時に API 承認テストで偶発的な破壊的変更を検出する（基礎と型の追求）
5. **Chesterton's Fence（チェスタートンの柵）** — パブリック API を削除・変更する前に、その存在理由を理解し、誰かが依存していることを前提とする（ニュートラルな視点）

---

## Workflow: Design and Maintain Stable Public APIs

### Step 1 — 互換性要件の分類

新しいライブラリの開始時、または既存パブリック API への変更評価時に使用します。

シナリオに該当する互換性の種類を判断します：

| 種類 | 定義 | スコープ | 例 |
|------|------|---------|-----|
| **API（ソース）** | 新バージョンに対してコードがコンパイルできる | パブリックメソッドシグネチャ、型 | 必須パラメータの追加 |
| **バイナリ** | コンパイル済みコードが新バージョンで実行できる | アセンブリレイアウト、メソッドトークン | 戻り値型の変更 |
| **ワイヤー** | シリアライズされたデータが各バージョンで読み取れる | ネットワークプロトコル、永続化 | JSON プロパティ名の変更 |

**なぜ最初に分類するのか**: 各互換性の種類には異なるルールがある — API 安全な変更がバイナリ互換性を破ることもあり、ソース互換な変更がワイヤーフォーマットを破ることもある。

> **Values**: 基礎と型の追求（分類はすべての互換性判断の基盤）

### Step 2 — 拡張専用 API サーフェスの設計

既存のパブリック API にコンシューマーを壊さずに新機能を追加するときに使用します。

拡張専用設計の3つの柱を適用します：

```csharp
// ✅ デフォルトパラメータで新しいオーバーロードを追加
public void Process(Order order, CancellationToken ct = default);

// ✅ 既存メソッドに新しいオプションパラメータを追加
public void Send(Message msg, Priority priority = Priority.Normal);

// ✅ 新しい型、インターフェース、列挙型を追加
public interface IOrderValidator { }
public enum OrderStatus { Pending, Complete, Cancelled }

// ✅ 既存型に新しいメンバーを追加
public class Order
{
    public DateTimeOffset? ShippedAt { get; init; }  // 新プロパティ
}
```

呼び出し元を壊す変更を避ける：

```csharp
// ❌ パブリックメンバーの削除またはリネーム
public void ProcessOrder(Order order);  // 旧: Process()

// ❌ パラメータの型や順序の変更
public void Process(int orderId);  // 旧: Process(Order order)

// ❌ 戻り値型の変更
public Order? GetOrder(string id);  // 旧: public Order GetOrder()

// ❌ デフォルトなしの必須パラメータ追加
public void Process(Order order, ILogger logger);  // 呼び出し元を壊す
```

**なぜ拡張専用か**: 古いコードは引き続き動作し、新旧のパスが共存し、ユーザーは自分のスケジュールでアップグレードできる。

> **Values**: 温故知新（実証済みの設計 — リリース後の振る舞いとシグネチャは固定される）

### Step 3 — API 承認テストの実装

NuGet パッケージやライブラリを偶発的な破壊的変更から保護するときに使用します。

必要なパッケージをインストール：

```bash
dotnet add package PublicApiGenerator
dotnet add package Verify.Xunit
```

API サーフェステストを作成：

```csharp
using PublicApiGenerator;
using VerifyXunit;

[Fact]
public Task ApprovePublicApi()
{
    // パブリック API 全体のテキストスナップショットを生成
    var api = typeof(MyLibrary.PublicClass).Assembly.GeneratePublicApi();
    return Verify(api);
}
```

`ApprovePublicApi.verified.txt` が生成され、完全なパブリック API サーフェスが記録される：

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

**なぜ API 承認テストか**: API の変更はテストを失敗させる — レビュアーは PR の差分でサーフェスの変更を正確に確認し、明示的に承認する必要がある。

> **Values**: 基礎と型の追求（自動検証が手動レビューでは見逃すものを検出する）

### Step 4 — 分散システムのワイヤー互換性管理

ゼロダウンタイムのローリングアップグレードが必要なシステムのメッセージフォーマット設計時に使用します。

Read-Before-Write デプロイパターンを実装：

```csharp
// フェーズ1: V2フォーマットのリーダーをすべてのノードにデプロイ（オプトイン）
public object Deserialize(byte[] data, string manifest) => manifest switch
{
    "Heartbeat" => DeserializeV1(data),    // 旧フォーマット
    "HeartbeatV2" => DeserializeV2(data),  // 新フォーマット — リーダーを先にデプロイ
    _ => throw new NotSupportedException($"Unknown manifest: {manifest}")
};

// フェーズ2: V2ライターを有効化（次のリリース、全ノードがV2を読めるようになった後）
public (byte[] data, string manifest) Serialize(Heartbeat hb) =>
    _useV2 ? (SerializeV2(hb), "HeartbeatV2") : (SerializeV1(hb), "Heartbeat");
```

型名ではなく明示的なディスクリミネーターを使用：

```csharp
// ❌ ペイロード内の型名 — クラスリネームでワイヤーフォーマットが壊れる
{ "$type": "MyApp.Order, MyApp", "Id": 123 }

// ✅ 明示的なディスクリミネーター — リファクタリング安全
{ "type": "order", "id": 123 }
```

後方互換性（旧ライター → 新リーダー）と前方互換性（新ライター → 旧リーダー）の両方がローリングアップグレードに必要。

> **Values**: 余白の設計（Read-Before-Write が安全な進化のための余白を作る）

### Step 5 — 非推奨化とバージョニング戦略の適用

セマンティックバージョン間で既存のパブリック API を削除・置換するときに使用します。

非推奨化ライフサイクルに従う：

```csharp
// ステップA: バージョンコンテキスト付きで非推奨マーク（任意のリリース）
[Obsolete("Obsolete since v1.5.0. Use ProcessAsync instead.")]
public void Process(Order order) { }

// ステップB: 推奨される新しい API を追加（同じリリース）
public Task ProcessAsync(Order order, CancellationToken ct = default);

// ステップC: 次のメジャーバージョンで削除（v2.0+ のみ）
// コンシューマーが移行する時間を確保した後に限る
```

セマンティックバージョニング (SemVer) を一貫して適用：

| バージョン | 許可される変更 | 例 |
|-----------|--------------|-----|
| **パッチ** (1.0.x) | バグ修正、セキュリティパッチ | GetOrder のヌル参照修正 |
| **マイナー** (1.x.0) | 新機能、非推奨化 | ProcessAsync 追加、Process 非推奨化 |
| **メジャー** (x.0.0) | 破壊的変更、API 削除 | Process 削除、型のリネーム |

**なぜ削除前に非推奨化するのか**: コンシューマーはアップグレードを計画する時間が必要 — 変更を告知し、移行パスを文書化し、少なくとも1つのマイナーバージョンの非推奨化期間を設ける。

> **Values**: 継続は力（段階的な進化が信頼を保ち、複利的な採用を可能にする）

---

## Good Practices

- 継承を想定していないクラスには `sealed` を使用する — なぜ: ユーザーのサブクラス化を防ぎ、将来の変更を可能にする
- 小さく焦点を絞ったインターフェース（`IOrderReader`、`IOrderWriter`）を使用する — なぜ: 大きなインターフェースへのメソッド追加はすべての実装を壊す
- 非パブリック API には `[InternalApi]` 属性または `.Internal` 名前空間を使用する — なぜ: 予告なく変更される可能性があることを示す
- すべての非同期パブリックメソッドに `CancellationToken ct = default` を使用する — なぜ: 拡張専用互換で一貫性がある
- CI パイプラインで API 承認テストを使用する — なぜ: マージ前に破壊的変更を検出する
- `TypeNameHandling` ではなく明示的な `[JsonDerivedType]` ディスクリミネーターを使用する — なぜ: リファクタリング安全なワイヤーフォーマット
- `.Internal` 名前空間の型はリリース間で予告なく変更される可能性があることを文書化する

---

## Common Pitfalls

| 落とし穴 | 問題 | 修正方法 |
|---------|------|---------|
| 必須パラメータの追加 | コンパイル時にすべての既存呼び出し元を壊す | デフォルトパラメータ値を使用する |
| メソッド戻り値型の変更 | コンパイル済みアセンブリのバイナリ互換性を壊す | 新しい戻り値型の新メソッドを追加する |
| パブリッククラスの未 sealed 化 | ユーザーが継承し内部リファクタリングを妨げる | デフォルトで seal する |
| リーダーより先にライターをデプロイ | 旧ノードが新ワイヤーフォーマットを解析できない | リーダーを先にデプロイ（Read-Before-Write） |
| .NET 型名のワイヤー埋め込み | クラスリネームでデシリアライゼーションが壊れる | 明示的な文字列ディスクリミネーターを使用 |
| 非推奨化期間のスキップ | コンシューマーがアップグレードを計画できない | 少なくとも1マイナーバージョンで `[Obsolete]` をマーク |

---

## Anti-Patterns

### ❌ Breaking Changes Disguised as Bug Fixes

同期メソッドを「修正」として非同期に変更する — この設計は同期シグネチャに依存するすべての呼び出し元を壊す。正しいアプローチは新しい非同期メソッドを追加し、古いものを非推奨化すること。

```csharp
// ❌ 「修正」で非同期化 — すべての呼び出し元を壊す
public async Task<Order> GetOrderAsync(OrderId id) { }

// ✅ 正解: 新メソッドを追加し、旧メソッドを非推奨化
[Obsolete("Use GetOrderAsync instead")]
public Order GetOrder(OrderId id) => GetOrderAsync(id).Result;
public async Task<Order> GetOrderAsync(OrderId id) { }
```

**代わりに**: 常に既存の API と並行して新しい API を追加する。古い API は明示的に非推奨化する。

### ❌ Silent Default Value Changes

既存パラメータのデフォルト値を変更する — この設計は以前のデフォルトに依存していたすべての呼び出し元の動作を暗黙的に変更する。正しいアプローチは目的のデフォルトで新しいパラメータを追加すること。

```csharp
// ❌ デフォルトを false から true に変更 — 暗黙的な動作変更
public void Configure(bool enableCaching = true);

// ✅ 正解: オリジナルを保持し、新パラメータを追加
public void Configure(
    bool enableCaching = false,       // 元のデフォルトを保持
    bool enableNewCaching = true);    // 新動作はオプトイン
```

**代わりに**: デフォルト値を変更しない。新しい動作には新しい名前の新パラメータを追加する。

### ❌ Monolithic Interface Growth

大きなパブリックインターフェースにメソッドを追加する — このアーキテクチャはすべての実装を壊す。正しいアプローチは小さく焦点を絞った契約によるインターフェース分離。

```csharp
// ❌ メソッド追加がすべての実装を壊す
public interface IOrderRepository
{
    Order? GetById(OrderId id);
    Task SaveAsync(Order order);
    // SearchAsync の追加が既存のすべての実装を壊す！
}

// ✅ 正解: 分離されたインターフェース
public interface IOrderReader { Order? GetById(OrderId id); }
public interface IOrderWriter { Task SaveAsync(Order order); }
public interface IOrderSearcher { Task<IReadOnlyList<Order>> SearchAsync(string query); }
```

**代わりに**: 最初から小さなインターフェースを設計する。新しいインターフェースの作成で拡張する。

---

## Quick Reference

| 判断 | 推奨 |
|------|------|
| 新機能の追加 | オーバーロード、新しい型、またはデフォルトパラメータを追加 |
| パブリック API の削除 | `[Obsolete]` で非推奨化、次のメジャーで削除 |
| メソッドシグネチャの変更 | 新しいオーバーロードを追加、古いシグネチャを非推奨化 |
| ワイヤーフォーマットの変更 | Read-Before-Write: リーダーを先にデプロイ |
| 偶発的な破壊の防止 | PublicApiGenerator による API 承認テスト |
| クラスの seal/unseal | デフォルトで seal、継承設計時のみ unseal |
| インターフェースの進化 | 分離されたインターフェース、既存への追加は禁止 |
| バージョニング戦略 | SemVer: パッチ=修正、マイナー=機能+非推奨化、メジャー=破壊的変更 |

---

## Resources

- [Making Public API Changes (Akka.NET)](https://getakka.net/community/contributing/api-changes-compatibility.html)
- [Wire Format Changes (Akka.NET)](https://getakka.net/community/contributing/wire-compatibility.html)
- [Extend-Only Design](https://aaronstannard.com/extend-only-design/)
- [OSS Compatibility Standards](https://aaronstannard.com/oss-compatibility-standards/)
- [Semantic Versioning](https://semver.org/)
- [PublicApiGenerator](https://github.com/PublicApiGenerator/PublicApiGenerator)
