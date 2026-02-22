<!-- このドキュメントは dotnet-oracle-wpf-integration の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-oracle-wpf-integration
description: >
  Add Oracle DB connection to WPF apps with repository pattern and CRUD operations.
  Use when integrating Oracle Database into existing WPF applications with MVVM settings
  dialog, repository pattern, and secure DPAPI-encrypted configuration.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, wpf, oracle, csharp, mvvm, repository-pattern]
  invocable: false
---

# WPFアプリケーションへのOracle Database接続の追加

既存の.NET WPFアプリケーションにOracle Database接続を追加するワークフロー：DPAPI暗号化によるOracleConfigModel、接続テスト付きMVVM設定ダイアログ、データアクセス用リポジトリパターン、ORA-*エラーハンドリング付きSQL実行。

## When to Use This Skill

このスキルを使用する場面：
- 既存のWPFアプリケーションにOracle Database接続を追加する場合
- 接続テスト付きのOracle接続管理MVVM設定ダイアログを作成する場合
- Oracleデータアクセス用のリポジトリパターン（ISofRepository + SofDatabaseOracle）を実装する場合
- `dotnet-access-to-oracle-migration`で検証済みのOracle SQLをWPFアプリで実行する場合
- パラメータ化クエリと接続プーリングによるデータアクセス層を構築する場合

**前提条件**：
- `dotnet-wpf-secure-config` を先に適用すること（DPAPI暗号化基盤）
- Oracle SQLは`dotnet-access-to-oracle-migration`で準備済みであること（Access → Oracle変換）

---

## Related Skills

- **`dotnet-wpf-secure-config`** — 必須：DPAPI暗号化基盤（先に適用）
- **`dotnet-access-to-oracle-migration`** — Step 5で使用するOracle SQLをAccess SQLから変換
- **`dotnet-wpf-dify-api-integration`** — 同じアプリで使用時にSecureConfigServiceを共有
- **`tdd-standard-practice`** — 生成コードをRed-Green-Refactorでテスト
- **`git-commit-practices`** — 各ステップを原子的変更としてコミット

---

## Core Principles

1. **Layered Architecture** — Domain（ISofRepository）、Infrastructure（SofDatabaseOracle）、Presentation（ViewModel）を分離（基礎と型）
2. **Security by Default** — パスワードはDPAPIで暗号化。接続文字列は実行時に構築し、保存しない（ニュートラル）
3. **Progressive Integration** — 設定 → UI → リポジトリ → SQL、一層ずつ段階的に実装（継続は力）
4. **MVVM Discipline** — ViewModelがすべてのUIロジックを駆動。コードビハインドは最小限（基礎と型）
5. **Reusable Components** — リポジトリと設定パターンは他のWPFプロジェクトでも動作（成長の複利）

---

## Workflow: Integrate Oracle DB into WPF

### Step 1 — Set Up Project Structure

Oracle統合用のフォルダ構造とNuGet依存関係を初期化する場合に使用。

`dotnet-wpf-secure-config`の既存プロジェクト構造にOracle固有のフォルダを追加：
- `Infrastructure/Configuration/OracleConfigModel.cs` — Oracle設定モデル
- `Infrastructure/Repositories/ISofRepository.cs` + `SofDatabaseOracle.cs` — データアクセス
- `Presentation/ViewModels/OracleConfigViewModel.cs` — 設定ViewModel
- `Presentation/Views/OracleConfigDialog.xaml` — 設定ダイアログ

```powershell
# Oracleデータアクセスプロバイダー
Install-Package Oracle.ManagedDataAccess.Core
# MVVMフレームワーク（dotnet-wpf-secure-configでインストール済みの場合はスキップ）
Install-Package CommunityToolkit.Mvvm
```

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Add Oracle Config Model

DPAPI暗号化パスワード付きのOracle接続設定を定義する場合に使用。

`OracleConfigModel`を作成し、`dotnet-wpf-secure-config`の既存`AppConfigModel`に統合する。

**OracleConfigModel.cs**：

```csharp
namespace YourApp.Infrastructure.Configuration
{
    public class OracleConfigModel
    {
        public string UserId { get; set; } = string.Empty;
        public string PasswordEncrypted { get; set; } = string.Empty;
        // EZ Connect形式が必要: "host:port/service"。tnspingでTNS名を解決する。
        public string DataSource { get; set; } = string.Empty;

        public string GetDecryptedPassword()
            => DpapiEncryptor.Decrypt(PasswordEncrypted);
        public void SetPassword(string plainPassword)
            => PasswordEncrypted = DpapiEncryptor.Encrypt(plainPassword);
        public bool IsValid()
            => !string.IsNullOrWhiteSpace(UserId)
            && !string.IsNullOrWhiteSpace(PasswordEncrypted)
            && !string.IsNullOrWhiteSpace(DataSource);
    }
}
```

**AppConfigModelを更新**（Oracleプロパティを追加）：

```csharp
public class AppConfigModel
{
    public OracleConfigModel OracleDb { get; set; } = new();  // 🆕 追加
    // public DifyConfigModel DifyApi { get; set; } = new();  // Difyスキルが追加
    public string Version { get; set; } = "1.0";
}
```

**ISecureConfigServiceとSecureConfigServiceを更新**（Oracleメソッドを追加）：

```csharp
// ISecureConfigService — 追加:
Task<OracleConfigModel> LoadOracleConfigAsync();
Task SaveOracleConfigAsync(OracleConfigModel config);

// SecureConfigService — 実装:
public async Task<OracleConfigModel> LoadOracleConfigAsync()
{
    var appConfig = await LoadAppConfigAsync();
    return appConfig.OracleDb;
}
public async Task SaveOracleConfigAsync(OracleConfigModel config)
{
    var appConfig = await LoadAppConfigAsync();
    appConfig.OracleDb = config;
    await SaveAppConfigAsync(appConfig);
}
```

> **Values**: 基礎と型 / ニュートラル

### Step 3 — Create Settings UI

接続テスト付きのOracle接続設定ダイアログを構築する場合に使用。

MVVMパターンに従ってViewModelとXAMLダイアログを作成する。

**主要な実装ポイント**（完全なコード → [references/detailed-patterns.md](detailed-patterns.md#step-3--oracleconfigviewmodel)）：
- `[ObservableProperty]` — UserId, Password, DataSource, StatusMessage, IsSaving
- `[RelayCommand]` — SaveAsync, TestConnectionAsync
- DPAPI復号化失敗時のグレースフル対応（パスワード再入力プロンプト）
- 接続テスト：`SELECT SYSDATE FROM DUAL`（10秒タイムアウト）
- コードビハインドでPasswordBoxブリッジ（WPFネイティブバインディング非対応）

> **Values**: 基礎と型 / 成長の複利

### Step 4 — Build Data Access Layer

Oracleデータアクセス用のリポジトリパターンを実装する場合に使用。

Domain層に`ISofRepository`インターフェース、Infrastructure層に`SofDatabaseOracle`実装を作成する。

**ISofRepository.cs** — ドメインインターフェース（Oracle依存なし）：

```csharp
namespace YourApp.Infrastructure.Repositories
{
    public interface ISofRepository
    {
        // 行をList<Dictionary<column_name, value>>で返す
        Task<List<Dictionary<string, object?>>> QueryAsync(
            string sql, Dictionary<string, object>? parameters = null);
        // 影響行数を返す
        Task<int> ExecuteAsync(
            string sql, Dictionary<string, object>? parameters = null);
    }
}
```

**SofDatabaseOracle.cs** — Infrastructure実装：

```csharp
using Oracle.ManagedDataAccess.Client;

namespace YourApp.Infrastructure.Repositories
{
    public class SofDatabaseOracle : ISofRepository
    {
        private readonly ISecureConfigService _configService;
        public SofDatabaseOracle(ISecureConfigService configService)
            => _configService = configService;

        public async Task<List<Dictionary<string, object?>>> QueryAsync(
            string sql, Dictionary<string, object>? parameters = null)
        {
            var results = new List<Dictionary<string, object?>>();
            await using var conn = await CreateConnectionAsync();
            await using var cmd = conn.CreateCommand();
            cmd.CommandText = sql;
            BindParameters(cmd, parameters);
            await using var reader = await cmd.ExecuteReaderAsync();
            while (await reader.ReadAsync())
            {
                var row = new Dictionary<string, object?>();
                for (int i = 0; i < reader.FieldCount; i++)
                    row[reader.GetName(i)] = reader.IsDBNull(i) ? null : reader.GetValue(i);
                results.Add(row);
            }
            return results;
        }

        public async Task<int> ExecuteAsync(
            string sql, Dictionary<string, object>? parameters = null)
        {
            await using var conn = await CreateConnectionAsync();
            await using var cmd = conn.CreateCommand();
            cmd.CommandText = sql;
            BindParameters(cmd, parameters);
            return await cmd.ExecuteNonQueryAsync();
        }

        private async Task<OracleConnection> CreateConnectionAsync()
        {
            var config = await _configService.LoadOracleConfigAsync();
            if (!config.IsValid())
                throw new InvalidOperationException(
                    "Oracle接続が未設定です。設定画面から接続情報を入力してください。");
            string password = config.GetDecryptedPassword();
            var conn = new OracleConnection(
                $"User Id={config.UserId};Password={password};Data Source={config.DataSource};");
            await conn.OpenAsync();
            return conn;
        }

        private static void BindParameters(
            OracleCommand cmd, Dictionary<string, object>? parameters)
        {
            if (parameters == null) return;
            // ✅ 常にパラメータ化クエリを使用 — SQLインジェクション対策
            foreach (var (key, value) in parameters)
                cmd.Parameters.Add(new OracleParameter(key, value ?? DBNull.Value));
        }
    }
}
```

**なぜリポジトリパターンか**：ドメイン層は`ISofRepository`（インターフェース）に依存し、`OracleConnection`（インフラストラクチャ）には依存しない。これによりモックリポジトリでのテストや、ビジネスロジックを変更せずにデータベースを切り替えることが可能になる。

> **Values**: 基礎と型 / 成長の複利

### Step 5 — Implement SQL Execution

検証済みOracle SQLでCRUD操作を実行する場合に使用。

`dotnet-access-to-oracle-migration`で準備したSQLを`ISofRepository`メソッドで使用する。

**SELECTクエリ**（データ読み取り）：

```csharp
// dotnet-access-to-oracle-migrationで検証済みのSQL
string sql = @"
SELECT s.""ship_date"", s.""prod_number"", s.""quantity""
FROM SCHEMA_A.""production_info"" s
WHERE s.""ship_date"" >= :shipDate";

var results = await _repository.QueryAsync(sql,
    new Dictionary<string, object> { { ":shipDate", "202601" } });

foreach (var row in results)
{
    string shipDate = row["ship_date"]?.ToString() ?? "";
    string prodNumber = row["prod_number"]?.ToString() ?? "";
}
```

**INSERT/UPDATE/DELETE**（トランザクション付き書き込み）：

```csharp
await using var conn = new OracleConnection(connectionString);
await conn.OpenAsync();
await using var transaction = conn.BeginTransaction();
try
{
    await using var cmd = conn.CreateCommand();
    cmd.Transaction = transaction;
    cmd.CommandText = @"UPDATE SCHEMA_A.""production_info""
        SET ""status"" = :status WHERE ""prod_number"" = :prodNo";
    cmd.Parameters.Add(new OracleParameter(":status", "SHIPPED"));
    cmd.Parameters.Add(new OracleParameter(":prodNo", "P-001"));
    await cmd.ExecuteNonQueryAsync();
    await transaction.CommitAsync();
}
catch { await transaction.RollbackAsync(); throw; }
```

**Oracle引用符ルール**（`dotnet-access-to-oracle-migration`より）：
- テーブル名：`SCHEMA_A."production_info"`（スキーマ + ダブルクォート小文字）
- カラム名：`"ship_date"`（ダブルクォート小文字）
- 文字列リテラル：`'202601'`（シングルクォート、ダブルではない）
- C#逐語的文字列：`@"s.""ship_date"""`（ダブルクォートを二重にする）

> **Values**: 基礎と型 / 継続は力

### Step 6 — Error Handling

接続やクエリ実行時のOracle固有エラーを処理する場合に使用。

ORA-*エラーコードをアクション可能な解決策にマッピングする。完全なエラーコード表は**Quick Reference**を参照。

```csharp
catch (OracleException ex)
{
    string message = ex.Number switch
    {
        1017 => "認証失敗。ユーザーIDとパスワードを確認してください。",
        12154 => "TNS名が見つかりません。EZ Connect形式（host:port/service）を使用してください。",
        12545 => "ネットワークエラー。ホスト、ポート、ファイアウォールを確認してください。",
        50201 => "無効なData Source形式です。tnspingを実行してEZ Connect文字列を取得してください。",
        12170 => "接続タイムアウト。ネットワークを確認するかタイムアウトを延長してください。",
        _ => $"Oracleエラー ORA-{ex.Number:D5}: {ex.Message}"
    };
    throw new InvalidOperationException(message, ex);
}
```

**TNS vs EZ Connect**：`Oracle.ManagedDataAccess.Core` NuGetパッケージはODBC DSNやTNS名を解決できない。`tnsping DSN名`を実行してEZ Connect形式（`host:port/service_name`）を取得する。

> **Values**: 温故知新 / 基礎と型

### Step 7 — Register DI and Test End-to-End

OracleサービスをDIに接続し、統合全体を検証する場合に使用。

`dotnet-wpf-secure-config`の既存DI設定にOracleサービスを追加する。

```csharp
// App.xaml.cs — 既存のOnStartupに追加
protected override void OnStartup(StartupEventArgs e)
{
    base.OnStartup(e);
    var services = new ServiceCollection();
    // ✅ dotnet-wpf-secure-configから（登録済み）
    services.AddSingleton<ISecureConfigService, SecureConfigService>();
    // 🆕 Oracle統合（Transient: 操作ごとに新しい接続）
    services.AddTransient<ISofRepository, SofDatabaseOracle>();
    services.AddTransient<OracleConfigViewModel>();
    _serviceProvider = services.BuildServiceProvider();
}
```

```csharp
// 設定ダイアログを起動
var vm = _serviceProvider.GetRequiredService<OracleConfigViewModel>();
new OracleConfigDialog(vm).ShowDialog();

// スモークテスト: 接続 + パラメータ化クエリ
var repo = _serviceProvider.GetRequiredService<ISofRepository>();
var sysdate = await repo.QueryAsync("SELECT SYSDATE FROM DUAL");
Debug.Assert(sysdate.Count == 1, "SYSDATEクエリは1行返すべき");
```

**テストシーケンス**：設定ダイアログ（保存/リロード/復号化）→ 接続テスト（`SELECT SYSDATE FROM DUAL`）→ `dotnet-access-to-oracle-migration`のSQLでクエリ → エラーハンドリング（誤った資格情報 → ORA-01017）。

> **Values**: 成長の複利 / 継続は力

---

## Common Pitfalls

### 1. Using TNS Names with Oracle.ManagedDataAccess.Core

**問題**：`Data Source=PROD_DSN`がORA-50201で失敗する。NuGetパッケージはODBC DSNやTNS名を解決できない。

**解決策**：`tnsping PROD_DSN`を実行してEZ Connect形式を取得し、`Data Source=192.0.2.10:1521/prod_service`を使用する。

### 2. Connection Pool Leaks

**問題**：`OracleConnection`の`using`/`Dispose()`を忘れると接続プールが枯渇する。
**解決策**：常に`await using var conn = ...`を使用して接続がプールに戻ることを保証する。

```csharp
// ❌ 間違い — 例外発生時に接続がリークする
var conn = new OracleConnection(connStr);
conn.Open();

// ✅ 正しい — 接続は常にプールに戻る
await using var conn = new OracleConnection(connStr);
await conn.OpenAsync();
```

### 3. Oracle Double-Quote Escaping in C#

**問題**：C#逐語的文字列は`"`文字の二重化が必要で、Oracleの引用符付き識別子が読みにくくなる。
**解決策**：`@""`構文を一貫して使用し、意図するOracle SQLをコメントで記述する。

```csharp
// Oracle SQL: SELECT s."ship_date" FROM SCHEMA_A."production_info" s
string sql = @"SELECT s.""ship_date"" FROM SCHEMA_A.""production_info"" s";
```

### 4. Hardcoding Connection Strings

**問題**：`User Id=SCOTT;Password=tiger`をC#コードに直接埋め込む。
**解決策**：常に`ISecureConfigService`から読み取り、実行時に接続文字列を構築する。

---

## Anti-Patterns

### SQL in ViewModel

**何が問題か**：ViewModelやコードビハインドにOracleクエリを直接書くこと。
**なぜ問題か**：プレゼンテーションとデータアクセスの関心事が混在し、データベースなしではテスト不可能。
**正しいアプローチ**：すべてのSQLはInfrastructure層の`ISofRepository`を経由する。

### Ignoring Parameterized Queries

**何が問題か**：ユーザー入力をSQLクエリに文字列連結すること。
**なぜ問題か**：SQLインジェクション脆弱性。
**正しいアプローチ**：動的な値には常に`OracleParameter`を使用する。

```csharp
// ❌ 間違い — SQLインジェクションリスク
cmd.CommandText = $"SELECT * FROM users WHERE name = '{userInput}'";
// ✅ 正しい — パラメータ化クエリ
cmd.CommandText = "SELECT * FROM users WHERE name = :name";
cmd.Parameters.Add(new OracleParameter(":name", userInput));
```

### Skipping DPAPI for Oracle Passwords

**何が問題か**：Oracleパスワードを平文の設定ファイルや環境変数に保存すること。
**なぜ問題か**：ファイルシステムアクセス権を持つ誰でもパスワードを読める。
**正しいアプローチ**：`OracleConfigModel.SetPassword()`を使用する（内部で`DpapiEncryptor`で暗号化）。

---

## Quick Reference

### ORA-* Error Code Quick Reference

| コード | メッセージ | 修正方法 |
|--------|----------|---------|
| ORA-01017 | 無効なユーザー名/パスワード | 設定ダイアログで再入力 |
| ORA-12154 | TNS解決不可 | EZ Connect形式を使用 |
| ORA-12545 | 接続失敗 | ホスト/ポート/ファイアウォール確認 |
| ORA-50201 | 無効なDSN | `tnsping`でEZ Connect取得 |
| ORA-00942 | テーブルが存在しない | スキーマ + ダブルクォート確認 |
| ORA-00904 | 無効な識別子 | カラム名の大小文字確認 |
| ORA-12170 | 接続タイムアウト | タイムアウト延長/ネットワーク確認 |

### TNS vs EZ Connect Decision

| シナリオ | 形式 | 例 |
|---------|------|-----|
| TNS名のみある | 先に`tnsping`実行 | `tnsping PROD_DSN` |
| ホスト/ポート/サービスがある | EZ Connectを直接使用 | `192.0.2.10:1521/prod_service` |
| Oracle Instant Clientインストール済み | TNSが動作する可能性 | `Data Source=PROD_DSN` |
| NuGetパッケージのみ | EZ Connect必須 | `Data Source=host:port/service` |

### Implementation Checklist

- [ ] NuGetインストール：`Oracle.ManagedDataAccess.Core`、`CommunityToolkit.Mvvm`
- [ ] `OracleConfigModel.cs`作成、`AppConfigModel`更新（Step 2）
- [ ] `ISecureConfigService`と`SecureConfigService`にOracleメソッド追加（Step 2）
- [ ] 接続テスト付き`OracleConfigViewModel.cs`作成（Step 3）
- [ ] `OracleConfigDialog.xaml` + `.xaml.cs`作成（Step 3）
- [ ] `ISofRepository` + `SofDatabaseOracle`作成（Step 4）
- [ ] ORA-*エラーハンドリング追加（Step 6）
- [ ] サービス登録とエンドツーエンドテスト（Step 7）
- [ ] すべての`YourApp`名前空間プレースホルダーを置き換え

---

## Resources

- `dotnet-access-to-oracle-migration` — OracleクエリをAccess SQLから変換するワークフロー
- [Oracle.ManagedDataAccess.Core NuGet](https://www.nuget.org/packages/Oracle.ManagedDataAccess.Core)
