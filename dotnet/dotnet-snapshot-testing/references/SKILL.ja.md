---
name: dotnet-snapshot-testing
description: >
  Verify スナップショットテストを使用して、レンダリング出力・API サーフェス・HTTP レスポンス・
  シリアライズされたオブジェクトを承認する。人間がレビューしたベースラインとして出力をキャプチャし、
  差分比較で意図しない変更を検出する。
  Use when 手動アサーションが非実用的な複雑出力を検証する場合に使用。
metadata:
  author: RyoMurakami1983
  tags: [verify, snapshot-testing, xunit, dotnet, api-approval, email-testing, regression]
  invocable: false
---

<!-- このドキュメントは dotnet-snapshot-testing の日本語版です。英語版: ../SKILL.md -->

# Snapshot Testing with Verify

出力をキャプチャし、人間が承認したベースラインと比較する。Verify は初回実行時に `.received.` ファイルを生成し、開発者がそれを `.verified.` ファイルとして承認し、以降の実行で差分比較により意図しない変更を検出する。.NET 8+ と xUnit を対象とする。

**略語**: API（Application Programming Interface）、CI（Continuous Integration）、HTML（HyperText Markup Language）、MJML（Mailjet Markup Language）、DI（Dependency Injection）。

## When to Use This Skill

- レンダリングされた HTML メール出力を検証し、CSS やレイアウトのリグレッションを自動検出する
- パブリック API サーフェスを承認し、リリース前に意図しない破壊的変更を検出する
- HTTP レスポンスのボディとヘッダーをエンドポイントごとに単一の検証済みスナップショットとしてテストする
- シリアライズ出力フォーマットを検証し、バージョン間のワイヤー互換性を保証する
- 手動アサーションを書かずに複雑なオブジェクトグラフの意図しない変更を検出する
- 生成されたコードやレポート出力を承認済みベースラインと比較してリグレッションを検出する

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-testcontainers` | Docker 実インフラを使った統合テスト |
| `dotnet-serialization` | シリアライズ戦略、JSON/XML フォーマット設定 |
| `dotnet-csharp-api-design` | パブリック API 設計、バージョニング、破壊的変更防止 |

## Core Principles

1. **Human-Approved Baselines** — すべてのスナップショットはベースラインになる前に開発者の明示的な承認を必要とする。理由：レビューなしの誤ったベースラインがコミットされるのを防ぐため。
2. **Diff-Based Regression Detection** — 変更はサイレントなアサーション失敗ではなく、差分ツールを通じて表面化する。理由：視覚的な差分により意図しない変更が即座に明確になるため。
3. **Scrub Dynamic Values** — タイムスタンプ、GUID、非決定的データを安定したプレースホルダーに置換する。理由：スナップショットが実行環境に関わらず同一結果を生成することを保証するため。
4. **One Snapshot Per Concern** — 各テストは単一の論理的出力を検証する。理由：スナップショットが失敗した時にリグレッションの正確な原因を特定するため。
5. **Version Control Integration** — `.verified.` ファイルをコミットし、`.received.` ファイルを無視する。理由：ベースラインが PR でレビューされ、履歴で追跡されるため。

> **Values**: 基礎と型の追求（Verify の「型」—承認ベースライン・スクラブ・差分検出—を守ることで、再現可能なリグレッション検出基盤を築く）, ニュートラルな視点（手動アサーションの偏りを排し、差分ベースの客観的な比較で品質基準を保つ）

## Workflow: Snapshot Testing with Verify

### Step 1: Install Verify and Configure ModuleInitializer

Verify NuGet パッケージをインストールし、プロジェクトレベルの設定を構成する。理由：集中設定により全テストで一貫したスナップショット動作を保証するため。

```bash
dotnet add package Verify.Xunit
# or: dotnet add package Verify.NUnit / Verify.MSTest
```

```csharp
using System.Runtime.CompilerServices;

public static class ModuleInitializer
{
    [ModuleInitializer]
    public static void Init()
    {
        // 検証済みファイルを専用ディレクトリに格納
        VerifyBase.UseProjectRelativeDirectory("Snapshots");
    }
}
```

> **Values**: 基礎と型の追求（ModuleInitializer という初期化の「型」を最初に整えることで、全テストの一貫性を保証する）

### Step 2: Write Basic Snapshot Tests

テストメソッドから `Verify(object)` を返してスナップショットファイルを生成する。理由：Verify がオブジェクトをシリアライズし、承認済みベースラインと自動比較するため。

```csharp
// ✅ GOOD — 記述的なテスト名がスナップショットファイル名になる
[Fact]
public Task VerifyUserDto()
{
    var user = new UserDto(
        Id: "user-123",
        Name: "John Doe",
        Email: "john@example.com",
        CreatedAt: new DateTime(2025, 1, 15));

    return Verify(user);
}
```

初回実行で `VerifyUserDto.received.txt` が作成される。承認すると `VerifyUserDto.verified.txt` になる：

```json
{
  Id: user-123,
  Name: John Doe,
  Email: john@example.com,
  CreatedAt: 2025-01-15T00:00:00
}
```

非テキストコンテンツには `extension` パラメータを使用する：

```csharp
[Fact]
public async Task VerifyRenderedEmail()
{
    var html = await _emailRenderer.RenderAsync("Welcome", new { Name = "John" });
    await Verify(html, extension: "html");
}
```

> **Values**: 温故知新（テストの命名規則という「過去の知恵」を、スナップショットファイル名の自動生成という新技術と結びつける）

### Step 3: Scrub Dynamic Values for Deterministic Snapshots

非決定的データを安定したプレースホルダーに置換する。理由：タイムスタンプと GUID はスクラブなしでは毎回変化し、偽の失敗を引き起こすため。

```csharp
[Fact]
public Task VerifyOrder()
{
    var order = new Order
    {
        Id = Guid.NewGuid(),        // 毎回異なる
        CreatedAt = DateTime.UtcNow, // 毎回異なる
        Total = 99.99m
    };

    return Verify(order)
        .ScrubMember("Id")
        .ScrubMember("CreatedAt");
}
```

繰り返しを避けるため `ModuleInitializer` でグローバルスクラブを設定する：

```csharp
[ModuleInitializer]
public static void Init()
{
    VerifierSettings.ScrubMembersWithType<DateTime>();
    VerifierSettings.ScrubMembersWithType<DateTimeOffset>();
    VerifierSettings.ScrubMembersWithType<Guid>();

    // 特定パターンのスクラブ（トークン、セッション ID）
    VerifierSettings.AddScrubber(s =>
        Regex.Replace(s, @"token=[a-zA-Z0-9]+", "token=SCRUBBED"));
}
```

> **Values**: 余白の設計（動的値をスクラブすることで、環境差異に対する余白を確保し、どの環境でも同一結果を保証する）

### Step 4: Apply to Domain-Specific Scenarios

メールテンプレート、API サーフェス、HTTP レスポンスに Verify を適用する。理由：各ドメインが視覚的な差分レビューとバージョン管理されたベースラインの恩恵を受けるため。

**メールテンプレート検証：**

```csharp
[Fact]
public async Task UserSignupInvitation_RendersCorrectly()
{
    var renderer = _services.GetRequiredService<IMjmlTemplateRenderer>();
    var variables = new Dictionary<string, string>
    {
        { "OrganizationName", "Acme Corporation" },
        { "InviteeName", "John Doe" },
        { "InvitationLink", "https://example.com/invite/abc123" },
        { "ExpirationDate", "December 31, 2025" }
    };

    var html = await renderer.RenderTemplateAsync(
        "UserInvitations/UserSignupInvitation", variables);
    await Verify(html, extension: "html");
}
```

**パブリック API サーフェス承認：**

```csharp
[Fact]
public Task ApprovePublicApi()
{
    var api = typeof(MyPublicClass).Assembly.GeneratePublicApi();
    return Verify(api);
}
```

**HTTP レスポンス検証：**

```csharp
[Fact]
public async Task GetUser_ReturnsExpectedResponse()
{
    var client = _factory.CreateClient();
    var response = await client.GetAsync("/api/users/123");

    await Verify(new
    {
        StatusCode = response.StatusCode,
        Headers = response.Headers
            .Where(h => h.Key.StartsWith("X-"))
            .ToDictionary(h => h.Key, h => h.Value.First()),
        Body = await response.Content.ReadAsStringAsync()
    });
}
```

> **Values**: 成長の複利（一つの Verify パターンを習得すれば、メール・API・HTTP の各ドメインに横展開でき、知識が複利的に増幅する）

### Step 5: Configure File Organization and CI Integration

スナップショットファイルを整理し、差分ツールを起動せずに失敗するよう CI を設定する。理由：適切なファイル整理がリポジトリの混乱を防ぎ、CI のハングを防止するため。

**推奨プロジェクト構成：**

```
tests/
  MyApp.Tests/
    Snapshots/
      EmailTests/
        WelcomeEmail.verified.html
      ApiTests/
        GetUser.verified.txt
    EmailTests.cs
    ApiTests.cs
    ModuleInitializer.cs
```

**`.gitignore` — received ファイルを除外：**

```gitignore
*.received.*
```

**`.gitattributes` — PR 差分で verified ファイルを折りたたむ：**

```gitattributes
*.verified.txt linguist-generated=true
*.verified.html linguist-generated=true
```

**ModuleInitializer での CI 設定：**

```csharp
[ModuleInitializer]
public static void Init()
{
    if (Environment.GetEnvironmentVariable("CI") == "true")
    {
        // 差分ツール起動の代わりにインライン差分出力を使用
        VerifyDiffPlex.UseDiffPlex(OutputType.Minimal);
        DiffRunner.Disabled = true;
    }
}
```

> **Values**: 継続は力（CI パイプラインでのスナップショット検証を自動化し、継続的にリグレッションを検出する仕組みを構築する）

## Good Practices

- ✅ 記述的なテスト名を使用する — スナップショットファイル名として識別が容易になる
- ✅ `ModuleInitializer` でグローバルに動的値をスクラブし、テストごとの繰り返しを避ける
- ✅ HTML、JSON、XML コンテンツには `extension` パラメータを使用して適切にレンダリングする
- ✅ `.verified.*` ファイルをソース管理にコミットし、PR で変更をレビューする
- ✅ `.gitattributes` で `linguist-generated=true` を使用して PR のスナップショット差分を折りたたむ
- ✅ CI では `DiffRunner.Disabled = true` で差分ツール起動を無効化する
- ✅ テストメソッドごとに一つのスナップショットを保持してリグレッション源を分離する
- ✅ `VerifyBase.UseProjectRelativeDirectory` で IDE 間で一貫したファイルパスを使用する

## Common Pitfalls

1. **Unscrubbed Dynamic Values** — GUID やタイムスタンプがスナップショットを毎回失敗させる。修正：`ModuleInitializer` で `ScrubMember` や `ScrubMembersWithType<T>()` を使用する。
2. **Committing Received Files** — `*.received.*` をソース管理に追加するとノイズとマージコンフリクトが発生する。修正：直ちに `*.received.*` を `.gitignore` に追加する。
3. **Diff Tool Launches in CI** — Verify が差分ツールを開こうとし、CI が無期限にハングする。修正：`CI` 環境変数を検出して `DiffRunner.Disabled = true` を設定する。
4. **Overly Broad Snapshots** — レスポンスオブジェクト全体を検証すると無関係なフィールドまでキャプチャされる。修正：テスト対象のフィールドのみを持つ匿名型にプロジェクションする。
5. **Generic Test Names** — `Test1` のような名前は識別不可能なスナップショットファイルを生成する。修正：`UserRegistration_WithValidData_ReturnsConfirmation` のような記述的な名前を使用する。

## Anti-Patterns

### ❌ Verifying Without Scrubbing → ✅ Scrub Dynamic Values

```csharp
// ❌ BAD — Id と CreatedAt が毎回変わるため毎回失敗する
var order = new Order { Id = Guid.NewGuid(), CreatedAt = DateTime.UtcNow };
await Verify(order);

// ✅ GOOD — 動的値を安定したプレースホルダーに置換
await Verify(order).ScrubMember("Id").ScrubMember("CreatedAt");
```

理由：スクラブされていない動的値はスナップショットを非決定的にし、偽の失敗を生む。

### ❌ Snapshot for Simple Values → ✅ Use Direct Assertions

```csharp
// ❌ BAD — 単純な値チェックにスナップショットのオーバーヘッド
await Verify(result.Count);

// ✅ GOOD — 直接アサーションの方が明確で高速
Assert.Equal(5, result.Count);
```

理由：スナップショットのファイル管理オーバーヘッドは、複雑な構造検証にのみ正当化される。

### ❌ Monolithic Snapshots → ✅ Focused Projections

```csharp
// ❌ BAD — 無関係なヘッダーを含むレスポンス全体をキャプチャ
await Verify(response);

// ✅ GOOD — 重要なフィールドにフォーカス
await Verify(new { response.StatusCode, Body = await response.Content.ReadAsStringAsync() });
```

理由：モノリシックなスナップショットはあらゆる変更で壊れ、実際のリグレッション特定を困難にする。

## Quick Reference

### Snapshot Testing Decision Table

| Scenario | Use Snapshot? | Why |
|----------|--------------|-----|
| Rendered HTML emails | ✅ Yes | 視覚・レイアウトのリグレッションを検出 |
| Public API surfaces | ✅ Yes | 意図しない破壊的変更を防止 |
| Serialization output | ✅ Yes | ワイヤーフォーマット互換性を検証 |
| Complex object graphs | ✅ Yes | 数十の手動アサーションより容易 |
| Simple value checks | ❌ No | `Assert.Equal` を直接使用 |
| Business logic results | ❌ No | 明確性のため明示的アサーションを使用 |
| Performance metrics | ❌ No | 代わりにベンチマークを使用 |

### Verify API Cheat Sheet

| Method | Purpose | Example |
|--------|---------|---------|
| `Verify(object)` | シリアライズ可能なオブジェクトのスナップショット | `return Verify(dto);` |
| `Verify(string, extension)` | ファイルタイプ付きスナップショット | `await Verify(html, extension: "html");` |
| `.ScrubMember("Name")` | 特定フィールドの置換 | `Verify(obj).ScrubMember("Id");` |
| `ScrubMembersWithType<T>()` | 型の全フィールドをスクラブ | `VerifierSettings.ScrubMembersWithType<Guid>();` |
| `AddScrubber(Action)` | カスタム正規表現スクラブ | `VerifierSettings.AddScrubber(...)` |
| `DiffRunner.Disabled` | CI で差分ツール無効化 | `DiffRunner.Disabled = true;` |

### File Naming Convention

| Input | Output File |
|-------|-------------|
| `[Fact] VerifyUserDto()` | `VerifyUserDto.verified.txt` |
| `Verify(html, extension: "html")` | `MethodName.verified.html` |
| Parameterized test | `MethodName_ParameterValue.verified.txt` |

## Resources

- [Verify GitHub](https://github.com/VerifyTests/Verify) — メインリポジトリとドキュメント
- [Verify.Xunit](https://github.com/VerifyTests/Verify.Xunit) — xUnit 統合パッケージ
- [PublicApiGenerator](https://github.com/PublicApiGenerator/PublicApiGenerator) — API サーフェス承認
- [Verify.DiffPlex](https://github.com/VerifyTests/Verify.DiffPlex) — CI 環境向けインライン差分
