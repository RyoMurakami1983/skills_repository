---
name: dotnet-wpf-secure-config
description: WPFアプリにDPAPI暗号化設定管理を追加。セキュアな資格情報保存が必要な場合に使用。
author: RyoMurakami1983
tags: [dotnet, wpf, csharp, security, dpapi, configuration]
invocable: false
version: 1.0.0
---

# WPFアプリケーションへのセキュア設定管理の追加

.NET WPFアプリケーションにWindows DPAPI暗号化設定管理を追加するワークフロー：資格情報の暗号化保存、`%LOCALAPPDATA%`へのJSON永続化、拡張可能な`AppConfigModel`、DI登録。

## When to Use This Skill

このスキルを使用する場面：
- WPFアプリケーションにセキュアな資格情報保存（パスワード、APIキー、トークン）を追加する場合
- Oracle、Dify等のサービス統合前に、DPAPI暗号化設定基盤をセットアップする場合
- 複数の統合スキルが共有する再利用可能な`SecureConfigService`を作成する場合
- 既存の`Infrastructure/Configuration/`層を新しいWPFプロジェクトに移植する場合
- 平文の`appsettings.json`資格情報をDPAPI暗号化に置き換える場合

**このスキルが前提となるスキル**：
- `dotnet-oracle-wpf-integration` — このセキュリティ基盤を使用してOracle DB接続を追加
- `dotnet-wpf-dify-api-integration` — このセキュリティ基盤を使用してDify API統合を追加

---

## Related Skills

- **`dotnet-oracle-wpf-integration`** — このセキュリティ基盤を使用してOracle DB接続を追加
- **`dotnet-wpf-dify-api-integration`** — このセキュリティ基盤を使用してDify APIを追加
- **`tdd-standard-practice`** — 生成コードをRed-Green-Refactorでテスト
- **`git-commit-practices`** — 各ステップを原子的変更としてコミット

---

## Core Principles

1. **Security by Default** — すべての秘密情報にDPAPI暗号化を適用。平文保存は禁止（ニュートラル）
2. **Reusable Foundation** — DpapiEncryptorとSecureConfigServiceはどのWPFプロジェクトでも動作する再利用可能な基盤（成長の複利）
3. **Extensible Config** — AppConfigModelは既存の設定を壊さずに新しい統合を追加できる（基礎と型）
4. **Layered Architecture** — 設定はInfrastructure層に配置し、インターフェース経由で利用（基礎と型）
5. **Single Source of Truth** — 1つの`config.json`ファイルで全サービスの資格情報を管理（継続は力）

---

## Workflow: WPFへのセキュア設定追加

### Step 1 — Set Up Configuration Structure

設定の暗号化に必要なフォルダ構造とNuGet依存関係を初期化する場合に使用。

`Infrastructure/Configuration/`フォルダを作成し、必要なパッケージをインストールする。

```
YourApp/
└── Infrastructure/
    └── Configuration/
        ├── DpapiEncryptor.cs         # DPAPI暗号化/復号化ユーティリティ
        ├── ISecureConfigService.cs   # サービスインターフェース
        ├── SecureConfigService.cs    # JSON永続化 + 暗号化
        └── AppConfigModel.cs         # 拡張可能な設定ルート
```

```powershell
# DPAPI（System.Security.Cryptography.ProtectedData）に必要
Install-Package System.Security.Cryptography.ProtectedData
# DI登録に必要
Install-Package Microsoft.Extensions.DependencyInjection
```

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Implement DpapiEncryptor

すべての設定モデルが共有するWindows DPAPI暗号化ユーティリティを追加する場合に使用。

`Encrypt`、`Decrypt`、`MaskSensitive`メソッドを持つ静的暗号化ヘルパーを作成する。

```csharp
using System;
using System.Security.Cryptography;
using System.Text;

namespace YourApp.Infrastructure.Configuration
{
    /// <summary>
    /// Windows DPAPI暗号化ユーティリティ
    /// CurrentUserスコープ：暗号化データは別ユーザー・別PCでは復号化不可
    /// </summary>
    public static class DpapiEncryptor
    {
        // ✅ アプリケーションごとに変更すること — Step 6参照
        private static readonly byte[] Entropy
            = Encoding.UTF8.GetBytes("YourApp_Config_Salt_2026");

        public static string Encrypt(string plainText)
        {
            if (string.IsNullOrEmpty(plainText)) return string.Empty;
            byte[] encrypted = ProtectedData.Protect(
                Encoding.UTF8.GetBytes(plainText),
                Entropy, DataProtectionScope.CurrentUser);
            return Convert.ToBase64String(encrypted);
        }

        public static string Decrypt(string encryptedText)
        {
            if (string.IsNullOrEmpty(encryptedText)) return string.Empty;
            try
            {
                byte[] decrypted = ProtectedData.Unprotect(
                    Convert.FromBase64String(encryptedText),
                    Entropy, DataProtectionScope.CurrentUser);
                return Encoding.UTF8.GetString(decrypted);
            }
            catch (CryptographicException ex)
            {
                throw new InvalidOperationException(
                    "復号化に失敗しました。別のユーザーで暗号化されている可能性があります。", ex);
            }
            catch (FormatException ex)
            {
                throw new InvalidOperationException(
                    "暗号化データのフォーマットが不正です。", ex);
            }
        }

        /// <summary>
        /// センシティブな値をマスク（ログ出力用、例："abcd****"）
        /// </summary>
        public static string MaskSensitive(string value)
        {
            if (string.IsNullOrEmpty(value) || value.Length <= 4)
                return "****";
            return value[..4] + "****";
        }
    }
}
```

**なぜ完全なエラーハンドリングが必要か**：`CryptographicException`はユーザーAで暗号化したデータをユーザーBが復号化しようとした場合（プロファイル移行後など）に発生する。これをキャッチしないと、再入力を促す代わりにアプリが起動時にクラッシュする。

> **Values**: ニュートラル / 基礎と型

### Step 3 — Define Config Models

拡張可能な設定データ構造を定義する場合に使用。

`AppConfigModel`をルートとし、ドメイン固有モデルをプロパティとして追加する。各統合スキルが独自のモデルを追加する。

**AppConfigModel.cs** — 拡張可能なルート：

```csharp
namespace YourApp.Infrastructure.Configuration
{
    /// <summary>
    /// アプリケーション設定ルート
    /// 新サービス統合時にプロパティを追加する
    /// </summary>
    public class AppConfigModel
    {
        // ✅ 新サービス統合時にここにプロパティを追加
        // public OracleConfigModel OracleDb { get; set; } = new();  // dotnet-oracle-wpf-integrationが追加
        // public DifyConfigModel DifyApi { get; set; } = new();     // dotnet-wpf-dify-api-integrationが追加

        public string Version { get; set; } = "1.0";
    }
}
```

**設定モデルのパターン** — 各サービスは以下のテンプレートに従う：

```csharp
/// <summary>
/// ドメイン固有設定モデルのテンプレート
/// "Service"を統合名に置き換える
/// </summary>
public class ServiceConfigModel
{
    public string Endpoint { get; set; } = string.Empty;
    public string CredentialEncrypted { get; set; } = string.Empty;

    public string GetDecryptedCredential()
        => DpapiEncryptor.Decrypt(CredentialEncrypted);

    public void SetCredential(string plainCredential)
        => CredentialEncrypted = DpapiEncryptor.Encrypt(plainCredential);

    public bool IsValid()
        => !string.IsNullOrWhiteSpace(Endpoint)
        && !string.IsNullOrWhiteSpace(CredentialEncrypted);
}
```

**なぜ拡張可能なルートにするか**：OracleとDifyを同時に使用する場合、`AppConfigModel`が両方を保持する：

```json
{
  "OracleDb": {
    "UserId": "SCOTT",
    "PasswordEncrypted": "AQAAANCMnd8B..."
  },
  "DifyApi": {
    "BaseUrl": "https://api.dify.ai",
    "ApiKeyEncrypted": "AQAAANCMnd8B..."
  },
  "Version": "1.0"
}
```

> **Values**: 成長の複利 / 基礎と型

### Step 4 — Build SecureConfigService

DPAPI暗号化資格情報サポート付きのJSON永続化サービスを実装する場合に使用。

`ISecureConfigService`インターフェースと`SecureConfigService`実装を作成する。サービスは`AppConfigModel`全体を管理し、各統合向けの型付きload/saveメソッドを公開する。

**ISecureConfigService.cs**：

```csharp
using System.Threading.Tasks;

namespace YourApp.Infrastructure.Configuration
{
    public interface ISecureConfigService
    {
        bool ConfigExists();
        Task ResetConfigAsync();

        // ✅ 統合ごとに型付きload/saveメソッドを追加
        // Task<OracleConfigModel> LoadOracleConfigAsync();
        // Task SaveOracleConfigAsync(OracleConfigModel config);
        // Task<DifyConfigModel> LoadDifyConfigAsync();
        // Task SaveDifyConfigAsync(DifyConfigModel config);
    }
}
```

**SecureConfigService.cs**：

```csharp
using System;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

namespace YourApp.Infrastructure.Configuration
{
    public class SecureConfigService : ISecureConfigService
    {
        private readonly string _configDirectory;
        private readonly string _configFilePath;

        public SecureConfigService()
        {
            // ✅ "YourAppName"を変更 — Step 6参照
            string localAppData = Environment.GetFolderPath(
                Environment.SpecialFolder.LocalApplicationData);
            _configDirectory = Path.Combine(localAppData, "YourAppName", "config");
            _configFilePath = Path.Combine(_configDirectory, "config.json");
        }

        public bool ConfigExists() => File.Exists(_configFilePath);

        public async Task ResetConfigAsync()
        {
            if (File.Exists(_configFilePath))
                await Task.Run(() => File.Delete(_configFilePath));
        }

        // ✅ 統合ごとに型付きメソッドを追加（Oracleの例）：
        //
        // public async Task<OracleConfigModel> LoadOracleConfigAsync()
        // {
        //     var appConfig = await LoadAppConfigAsync();
        //     return appConfig.OracleDb;
        // }
        //
        // public async Task SaveOracleConfigAsync(OracleConfigModel config)
        // {
        //     var appConfig = await LoadAppConfigAsync();
        //     appConfig.OracleDb = config;
        //     await SaveAppConfigAsync(appConfig);
        // }

        protected async Task<AppConfigModel> LoadAppConfigAsync()
        {
            if (!File.Exists(_configFilePath))
                return new AppConfigModel();

            try
            {
                string json = await File.ReadAllTextAsync(_configFilePath);
                return JsonSerializer.Deserialize<AppConfigModel>(json)
                       ?? new AppConfigModel();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException(
                    $"設定ファイルの読み込みに失敗しました: {_configFilePath}", ex);
            }
        }

        protected async Task SaveAppConfigAsync(AppConfigModel appConfig)
        {
            if (!Directory.Exists(_configDirectory))
                Directory.CreateDirectory(_configDirectory);

            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder
                    .UnsafeRelaxedJsonEscaping
            };

            string json = JsonSerializer.Serialize(appConfig, options);
            await File.WriteAllTextAsync(_configFilePath, json);
        }
    }
}
```

**なぜLoad/SaveAppConfigAsyncが`protected`か**：統合スキル（Oracle、Dify）が型付きメソッドを追加してこれらの内部ヘルパーを呼び出す。`protected`にすることでサブクラス化を可能にしつつ、公開APIをクリーンに保つ。

> **Values**: 基礎と型 / 継続は力

### Step 5 — Register DI Container

`SecureConfigService`をWPFアプリケーションの依存性注入に接続する場合に使用。

`App.xaml.cs`で`ISecureConfigService`をシングルトンとして登録する：

```csharp
// App.xaml.cs
using Microsoft.Extensions.DependencyInjection;

public partial class App : Application
{
    private ServiceProvider? _serviceProvider;

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        var services = new ServiceCollection();

        // ✅ シングルトン：1つの設定ファイル、1つのサービスインスタンス
        services.AddSingleton<ISecureConfigService, SecureConfigService>();

        // 統合スキルがここにサービスを追加：
        // services.AddSingleton<DifyApiService>();           // Dify統合
        // services.AddTransient<ISofRepository, SofDatabaseOracle>(); // Oracle統合

        _serviceProvider = services.BuildServiceProvider();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _serviceProvider?.Dispose();
        base.OnExit(e);
    }
}
```

**なぜシングルトンか**：すべての統合が同じ`config.json`ファイルを共有する。複数インスタンスは同時書き込みの競合リスクを生む。

> **Values**: 成長の複利 / 基礎と型

### Step 6 — Customize for Your App

生成コードを本番デプロイ用に準備する場合に使用。

出荷前に以下のプレースホルダーを置き換える：

| 項目 | ファイル | 変更内容 | 未変更時の影響 |
|------|---------|---------|--------------|
| アプリ名 | `SecureConfigService.cs` | `"YourAppName"` → 実際のアプリ名 | 設定が間違ったフォルダに保存 |
| ソルト | `DpapiEncryptor.cs` | `Entropy`のバイト配列値 | 共有ソルトで分離が弱まる |
| 名前空間 | 全`.cs`ファイル | `YourApp` → 実際の名前空間 | ビルドエラー |

**カスタマイズ確認**：

```powershell
# プレースホルダーが残っていないか確認
Select-String -Path "Infrastructure/Configuration/*.cs" -Pattern "YourApp" -SimpleMatch
# カスタマイズ後の期待結果：0件
```

⚠️ **重要**：暗号化済みデータがある状態で`Entropy`値を変更すると、既存の暗号化データは回復不可能になる。初回使用前に一度だけ設定すること。

> **Values**: ニュートラル / 基礎と型

---

## Common Pitfalls

### 1. 暗号化後のエントロピー変更

**問題**：資格情報が保存された後にDpapiEncryptorのソルト値を更新してしまう。

**解決策**：初回デプロイ前にエントロピー値を一度設定する。変更が必要な場合は、旧ソルトで復号化し新ソルトで再暗号化するマイグレーションを実装する。

### 2. CurrentUserの代わりにLocalMachineスコープを使用

**問題**：`DataProtectionScope.LocalMachine`は同じPC上の全ユーザーが復号化可能。

**解決策**：ユーザー単位の資格情報分離には常に`DataProtectionScope.CurrentUser`を使用する。

```csharp
// ❌ 間違い — このPC上の全ユーザーが復号化可能
ProtectedData.Protect(data, entropy, DataProtectionScope.LocalMachine);

// ✅ 正しい — 暗号化したユーザーのみ復号化可能
ProtectedData.Protect(data, entropy, DataProtectionScope.CurrentUser);
```

### 3. 復号化された秘密情報のログ出力

**問題**：平文のパスワードやAPIキーをログファイルに書き込む。

**解決策**：ログ出力には常に`DpapiEncryptor.MaskSensitive()`を使用する。

```csharp
// ❌ 間違い — ログに秘密情報が漏洩
logger.LogInformation($"Password: {password}");

// ✅ 正しい — マスク出力
logger.LogInformation($"Password: {DpapiEncryptor.MaskSensitive(password)}");
// 出力: "Password: abcd****"
```

### 4. CryptographicExceptionの無視

**問題**：復号化エラーを無視して空文字列を返す。

**解決策**：エラーをユーザーに表示し、資格情報の再入力を促す。

---

## Anti-Patterns

### appsettings.jsonへの資格情報保存

**何が問題か**：平文のパスワードやAPIキーをソース管理対象の設定ファイルに保存すること。

**なぜ問題か**：リポジトリアクセス権を持つ全員が読める。デプロイ成果物も暗号化されていないことが多い。

**正しいアプローチ**：`DpapiEncryptor` + `SecureConfigService`を使い、暗号化値を`%LOCALAPPDATA%`に保存する。

### サービスごとに別々の設定ファイル

**何が問題か**：`oracle-config.json`、`dify-config.json`など統合ごとに別ファイルを作成すること。

**なぜ問題か**：ファイルI/Oロジックが重複し、競合状態が発生し、バックアップ/リセットが困難になる。

**正しいアプローチ**：サービスごとに型付きプロパティを持つ単一の`AppConfigModel`を1つの`config.json`に永続化する。

### ソースコードへの資格情報ハードコード

**何が問題か**：接続文字列やAPIキーをC#コードに直接埋め込むこと。

**なぜ問題か**：削除後もバージョン管理の履歴に資格情報が残る。

**正しいアプローチ**：実行時に常に`ISecureConfigService`から読み取る。

---

## Quick Reference

### Migration Checklist（新アプリへの移植）

- [ ] `Infrastructure/Configuration/`フォルダをコピー（4ファイル）
- [ ] 名前空間をソースアプリからターゲットアプリに変更
- [ ] `SecureConfigService`コンストラクタのアプリ名を変更（`"YourAppName"`）
- [ ] `DpapiEncryptor`のエントロピー値を変更（アプリ固有のソルトを設定）
- [ ] `AppConfigModel`に統合用の設定モデルプロパティを追加
- [ ] `ISecureConfigService`と`SecureConfigService`に型付きload/saveメソッドを追加
- [ ] DIコンテナに`ISecureConfigService`を登録
- [ ] テスト：暗号化 → 保存 → 再読み込み → 復号化サイクル

### Security Checklist

- [ ] すべてのパスワードとAPIキーが`DpapiEncryptor.Encrypt()`で保存前に暗号化されている
- [ ] ログ出力で資格情報に`MaskSensitive()`を使用している
- [ ] エラーメッセージに復号化された秘密情報が含まれていない
- [ ] `DataProtectionScope.CurrentUser`を使用している（`LocalMachine`ではない）
- [ ] エントロピー値がアプリケーション固有である
- [ ] 設定ファイルが`%LOCALAPPDATA%`に保存されている（Windowsによるユーザー分離）

### What to Encrypt — 暗号化対象判定表

| データ種別 | 暗号化？ | 理由 |
|-----------|---------|------|
| パスワード | ✅ 必須 | 認証資格情報 |
| APIキー | ✅ 必須 | サービスアクセストークン |
| トークン/秘密鍵 | ✅ 必須 | ベアラー資格情報 |
| URL/エンドポイント | ❌ 不要 | 公開情報 |
| ユーザーID/名前 | ⚠️ ポリシー依存 | 個人情報の可能性 |
| タイムアウト値 | ❌ 不要 | 非機密設定 |

### DPAPI Security Properties

| 項目 | 値 |
|------|-----|
| 暗号化スコープ | ユーザー単位（CurrentUser） |
| 鍵管理 | 自動（Windows管理） |
| ポータブル？ | ❌ 別PC・別ユーザーでは復号化不可 |
| クラウド同期？ | ❌ 非対応（マシン鍵が異なるため） |
| バックアップ戦略 | リストア後に資格情報を再入力 |

---

## Resources

- 共通セキュリティコンポーネント — 完全な実装リファレンス（内部ドキュメント、このリポジトリ外で管理）
- [Microsoft: Data Protection API (DPAPI)](https://docs.microsoft.com/windows/win32/seccng/data-protection-api)
