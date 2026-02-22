<!-- このドキュメントは dotnet-wpf-dify-api-integration の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-wpf-dify-api-integration
description: WPFアプリにDify APIを追加。DPAPI設定とSSEストリーミング対応。Dify連携構築時に使用。
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, wpf, dify, csharp, mvvm]
  invocable: false
---

# WPFアプリケーションへのDify API連携追加

WPFアプリケーションにDify API連携を追加するためのエンドツーエンドワークフロー：DPAPIによるセキュア設定、MVVM設定UI、ファイルアップロード、SSEベースのワークフローストリーミング。

## When to Use This Skill

以下の場合にこのスキルを使用してください：
- 既存のWPFアプリケーションにDify API連携を追加するとき
- SSEストリーミング経由でDifyワークフローを呼び出す新規WPFプロジェクトを作成するとき
- Dify設定用のDPAPI暗号化APIキー保存を生成するとき
- Dify API接続管理用のMVVM設定ダイアログを構築するとき
- リアルタイム進捗表示付きのファイルアップロードとストリーミングワークフロー実行を実装するとき

---

## Related Skills

- **`dotnet-wpf-secure-config`** — 必須：DPAPI暗号化基盤（先に適用）
- **`dotnet-oracle-wpf-integration`** — 同じアプリでSecureConfigServiceを共有
- **`tdd-standard-practice`** — Red-Green-Refactorで生成コードをテスト
- **`git-commit-practices`** — 各ステップをアトミックな変更としてコミット
- **`skills-validate-skill`** — このスキルの品質を検証

---

## Core Principles

1. **階層化アーキテクチャ** — Presentation、Infrastructure、Domainの関心事を分離（基礎と型）
2. **デフォルトでセキュア** — APIキーはDPAPI暗号化。平文保存は禁止（ニュートラル）
3. **段階的な統合** — 設定 → クライアント → UI、一層ずつ確実に（継続は力）
4. **MVVM規律** — ViewModelがすべてのUIロジックを駆動。code-behindは最小限（基礎と型）
5. **再利用可能なコンポーネント** — 各クラスがWPFプロジェクト間で独立して動作（成長の複利）

---

## Workflow: Integrate Dify API into WPF

### Step 1 — プロジェクト構造のセットアップ

### Step 1 — 前提条件確認とDify固有ファイル追加

`dotnet-wpf-secure-config` 適用済みプロジェクトにDify固有ファイルを追加するときに使用します。

**前提条件**（先に完了必須）:
- `dotnet-wpf-secure-config` スキル適用済み
- `Infrastructure/Configuration/` フォルダに以下が存在:
  - `DpapiEncryptor.cs`
  - `SecureConfigService.cs`
  - `ISecureConfigService.cs`
  - `AppConfigModel.cs`

**追加するファイル**（Dify固有）:

```
YourApp/
├── Infrastructure/
│   ├── Configuration/
│   │   └── DifyConfigModel.cs           # 🆕 追加
│   └── Difys/                            # 🆕 フォルダ作成
│       └── DifyApiService.cs             # 🆕 追加
└── Presentation/
    ├── ViewModels/
    │   └── DifyConfigViewModel.cs        # 🆕 追加
    └── Views/
        ├── DifyConfigDialog.xaml         # 🆕 追加
        └── DifyConfigDialog.xaml.cs      # 🆕 追加
```

**NuGetパッケージ**（未インストールの場合）:

```powershell
Install-Package CommunityToolkit.Mvvm
Install-Package Microsoft.Extensions.DependencyInjection
```

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Dify設定モデルの追加

DPAPI暗号化APIキー付きのDify API設定を定義するときに使用します。

**前提条件**：先に`dotnet-wpf-secure-config`を適用して`DpapiEncryptor`、`SecureConfigService`、`AppConfigModel`をセットアップしてください。

**DifyConfigModel.cs** — Dify固有の設定データ（`Infrastructure/Configuration/`に追加）：

```csharp
public class DifyConfigModel
{
    public string BaseUrl { get; set; } = string.Empty;
    public string ApiKeyEncrypted { get; set; } = string.Empty;
    // ✅ Difyログ用に社員番号を使用（Windows ユーザー名はPII漏洩リスク）
    public string EmployeeId { get; set; } = string.Empty;

    public string GetDecryptedApiKey()
        => DpapiEncryptor.Decrypt(ApiKeyEncrypted);

    public void SetApiKey(string plainApiKey)
        => ApiKeyEncrypted = DpapiEncryptor.Encrypt(plainApiKey);

    public bool IsValid()
        => !string.IsNullOrWhiteSpace(BaseUrl)
        && !string.IsNullOrWhiteSpace(ApiKeyEncrypted);
}
```

**AppConfigModelを更新**（Difyプロパティを追加）：

```csharp
public class AppConfigModel
{
    public DifyConfigModel DifyApi { get; set; } = new();  // 🆕 追加
    // public OracleConfigModel OracleDb { get; set; } = new();  // Oracleスキルが追加
    public string Version { get; set; } = "1.0";
}
```

**ISecureConfigServiceとSecureConfigServiceを更新**（Difyメソッドを追加）：

```csharp
// ISecureConfigService — 追加:
Task<DifyConfigModel> LoadDifyConfigAsync();
Task SaveDifyConfigAsync(DifyConfigModel config);

// SecureConfigService — 実装:
public async Task<DifyConfigModel> LoadDifyConfigAsync()
{
    var appConfig = await LoadAppConfigAsync();
    return appConfig.DifyApi;
}

public async Task SaveDifyConfigAsync(DifyConfigModel config)
{
    var appConfig = await LoadAppConfigAsync();
    appConfig.DifyApi = config;
    await SaveAppConfigAsync(appConfig);
}
```

`DpapiEncryptor`、`SecureConfigService`フレームワーク、`AppConfigModel`ベースについては`dotnet-wpf-secure-config`を参照してください。

> **Values**: 基礎と型 / ニュートラル

### Step 3 — APIクライアントの実装（アップロード + SSE）

Dify APIへのファイルアップロードとワークフロー実行を接続するときに使用します。

ファイルアップロードとストリーミングワークフロー実行を持つ`DifyApiService`を作成します。

> **注意**: サンプルでは簡潔さのため`using var client = new HttpClient()`を使用しています。本番環境ではソケット枯渇を防ぐため、DIに登録した`IHttpClientFactory`の使用を推奨します。

**ファイルアップロード** (`/v1/files/upload`)：

```csharp
public class DifyApiService
{
    private readonly ISecureConfigService _configService;

    public DifyApiService(ISecureConfigService configService)
        => _configService = configService;

    public async Task<string> UploadFileAsync(string filePath)
    {
        var config = await _configService.LoadDifyConfigAsync();
        string apiKey = config.GetDecryptedApiKey();
        string baseUrl = config.BaseUrl.TrimEnd('/');

        using var client = new HttpClient();
        client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

        using var form = new MultipartFormDataContent();
        // ✅ 社員番号を使用 — Windowsユーザー名の外部サービスへの漏洩を防止
        form.Add(new StringContent(config.EmployeeId), "user");
        var fileContent = new ByteArrayContent(await File.ReadAllBytesAsync(filePath));
        fileContent.Headers.ContentType = new MediaTypeHeaderValue("application/pdf");
        form.Add(fileContent, "file", Path.GetFileName(filePath));

        var res = await client.PostAsync($"{baseUrl}/v1/files/upload", form);
        res.EnsureSuccessStatusCode();
        var json = JsonDocument.Parse(await res.Content.ReadAsStringAsync());
        return json.RootElement.GetProperty("id").GetString()!;
    }
}
```

**SSE付きワークフロー実行** (`/v1/workflows/run`)：

```csharp
public async Task<string> RunWorkflowStreamingAsync(
    string uploadFileId, Dictionary<string, object> inputs,
    IProgress<string>? progress = null)
{
    var config = await _configService.LoadDifyConfigAsync();
    string apiKey = config.GetDecryptedApiKey();
    string baseUrl = config.BaseUrl.TrimEnd('/');

    // 長時間実行ワークフロー用に5分タイムアウト
    using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(300) };
    client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

    inputs["pdf_file"] = new {
        transfer_method = "local_file", upload_file_id = uploadFileId, type = "document"
    };
    // ✅ Difyログ用に社員番号を使用（追跡可能だが悪用不可）
    var body = new { inputs, response_mode = "streaming",
        user = config.EmployeeId };

    var content = new StringContent(
        JsonSerializer.Serialize(body), Encoding.UTF8, "application/json");
    using var req = new HttpRequestMessage(HttpMethod.Post,
        $"{baseUrl}/v1/workflows/run") { Content = content };

    // ResponseHeadersReadでSSEストリーム全体のバッファリングを回避
    var res = await client.SendAsync(req, HttpCompletionOption.ResponseHeadersRead);
    res.EnsureSuccessStatusCode();
    return await ReadSseStreamAsync(res, progress);
}
```

**SSEストリームリーダー** — `data:`行を解析し、`workflow_started` / `node_started` / `node_finished` / `workflow_finished`イベントを`IProgress<string>`にルーティングします。完全な実装は[references/detailed-patterns.md](detailed-patterns.md#sse-stream-reader)を参照してください。

> **Values**: 継続は力 / 温故知新

### Step 4 — MVVM設定UIの構築

Dify API設定ダイアログを作成・更新するときに使用します。

Dify API設定用のViewModelとXAMLダイアログを作成します。

**DifyConfigViewModel.cs**：

```csharp
public partial class DifyConfigViewModel : ObservableObject
{
    private readonly ISecureConfigService _configService;

    [ObservableProperty] private string baseUrl = string.Empty;
    [ObservableProperty] private string apiKey = string.Empty;
    [ObservableProperty] private string employeeId = string.Empty;
    [ObservableProperty] private string statusMessage = string.Empty;
    [ObservableProperty] private bool isSaving;

    public DifyConfigViewModel(ISecureConfigService configService)
        => _configService = configService;

    public async Task LoadConfigAsync()
    {
        var cfg = await _configService.LoadDifyConfigAsync();
        BaseUrl = cfg.BaseUrl;
        EmployeeId = cfg.EmployeeId;
        try
        {
            ApiKey = cfg.GetDecryptedApiKey();
        }
        catch (CryptographicException)
        {
            // ユーザープロファイルやマシンが変更された場合、DPAPI復号化に失敗
            ApiKey = string.Empty;
            StatusMessage = "保存されたAPIキーの復号化に失敗しました。再入力してください。";
        }
    }

    [RelayCommand]
    private async Task SaveAsync()
    {
        if (string.IsNullOrWhiteSpace(BaseUrl) || string.IsNullOrWhiteSpace(ApiKey))
        { StatusMessage = "ベースURLとAPIキーは必須です。"; return; }

        IsSaving = true;
        try
        {
            var config = new DifyConfigModel
                { BaseUrl = BaseUrl, EmployeeId = EmployeeId };
            config.SetApiKey(ApiKey);
            await _configService.SaveDifyConfigAsync(config);
            StatusMessage = "保存しました。";
        }
        catch (Exception ex)
        {
            StatusMessage = $"保存に失敗しました: {ex.Message}";
        }
        finally
        {
            IsSaving = false;
        }
    }
}
```

**DifyConfigDialog.xaml.cs** — 最小限のcode-behind（PasswordBoxブリッジのみ）：

```csharp
public partial class DifyConfigDialog : Window
{
    public DifyConfigDialog(DifyConfigViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
        // PasswordBoxはネイティブで双方向バインディングをサポートしない
        Loaded += async (_, _) => await viewModel.LoadConfigAsync();
        viewModel.PropertyChanged += (_, e) =>
        { if (e.PropertyName == nameof(viewModel.ApiKey)) ApiKeyBox.Password = viewModel.ApiKey; };
        ApiKeyBox.PasswordChanged += (_, _) => viewModel.ApiKey = ApiKeyBox.Password;
    }
    private void Close_Click(object sender, RoutedEventArgs e) => Close();
}
```

> **Values**: 基礎と型 / 成長の複利

### Step 5 — DI配線と起動

サービスを登録し、設定ダイアログを初めて起動するときに使用します。

`App.xaml.cs`でサービスを登録し、設定ダイアログを接続します。

```csharp
// App.xaml.cs
protected override void OnStartup(StartupEventArgs e)
{
    base.OnStartup(e);
    var services = new ServiceCollection();
    services.AddSingleton<ISecureConfigService, SecureConfigService>();
    services.AddSingleton<DifyApiService>();
    services.AddTransient<DifyConfigViewModel>();
    _serviceProvider = services.BuildServiceProvider();
}
```

```csharp
// 任意のウィンドウから起動
var vm = _serviceProvider.GetRequiredService<DifyConfigViewModel>();
new DifyConfigDialog(vm).ShowDialog();
```

> **Values**: 成長の複利 / 継続は力

### Step 6 — アプリケーション固有のカスタマイズ

生成されたコードを本番デプロイ用に準備するときに使用します。

出荷前にこれらのプレースホルダーを置き換えてください：

| 項目 | ファイル | 変更内容 |
|------|---------|---------|
| アプリ名 | `SecureConfigService.cs` | 設定パス内の`"YourAppName"` |
| ソルト値 | `DpapiEncryptor.cs` | `Entropy`バイト配列の値 |
| 名前空間 | 全`.cs`ファイル | `YourApp` → 実際の名前空間 |
| ワークフロー入力 | `DifyApiService.cs` | `inputs`辞書のキー |
| 社員番号 | `DifyConfigDialog.xaml` | 社員番号入力用TextBox追加 |

> **Values**: ニュートラル / 基礎と型

---

## Good Practices

### 1. 保存前にBaseUrlスキームを検証

**What**: ViewModelの`SaveAsync`メソッドでHTTPS以外のURLを拒否します。

**Why**: APIキーはネットワーク上を流れるため、HTTPでは傍受のリスクがあります。

**Values**: ニュートラル（セキュリティを標準化）

### 2. 操作ごとに明示的なタイムアウトを設定

**What**: ワークフロー300秒、アップロード30秒、接続テスト10秒。

**Why**: 無限ハングを防止し、ユーザー体験を改善します。

**Values**: 継続は力（安定した動作を継続）

### 3. すべての長時間操作でIProgress<string>を使用

**What**: 開始と終了だけでなく、各SSEイベントで進捗をレポートします。

**Why**: ユーザーは固まった画面ではなく、ノードレベルの進捗を確認できます。

**Values**: 成長の複利（UXの知見がチームに蓄積）

---

## Common Pitfalls

### 1. appsettings.jsonにAPIキーを保存

**Problem**: ソース管理される設定ファイルに平文のAPIキー。

**Solution**: Step 2の`DpapiEncryptor` + `SecureConfigService`を使用します。

```csharp
// ❌ 間違い - 設定ファイルに平文
{ "DifyApi": { "ApiKey": "app-xxxxxxxxxxxx" } }

// ✅ 正しい - DPAPIで暗号化
{ "DifyApi": { "ApiKeyEncrypted": "AQAAANCMnd8B..." } }
```

### 2. SSEストリーミング中にUIスレッドをブロック

**Problem**: 非同期SSE呼び出しに`.Result`や`.Wait()`を使用するとUIがフリーズ。

**Solution**: `await`と`IProgress<string>`でノンブロッキング更新を行います。

```csharp
// ❌ 間違い
var result = difyService.RunWorkflowStreamingAsync(...).Result;

// ✅ 正しい
var result = await difyService.RunWorkflowStreamingAsync(..., progress);
```

### 3. CryptographicExceptionを無視

**Problem**: ユーザーAが暗号化したDPAPIデータはユーザーBでは復号化できない。

**Solution**: 例外をキャッチし、ユーザーに認証情報の再入力を促します。

### 4. BaseUrlを設定なしでハードコード

**Problem**: `https://api.dify.ai`がソースコードに埋め込まれ、環境ごとの変更が不可能。

**Solution**: 常に`SecureConfigService`から読み取り、設定ダイアログで変更を管理します。

---

## Anti-Patterns

### code-behindにビジネスロジック

**What**: `.xaml.cs`のイベントハンドラに保存/読み込みロジックを直接記述。

**Why It's Wrong**: 実行中のWPFウィンドウなしではテスト不可能。MVVM分離に違反。

**Better Approach**: `[RelayCommand]`とデータバインディングですべてのロジックをViewModelに委譲。

### タイムアウトなしの単一HttpClient

**What**: SSE呼び出しに`Timeout`を設定せずに`new HttpClient()`を作成。

**Why It's Wrong**: デフォルトタイムアウト（100秒）は長時間ワークフローを中断。タイムアウトなしは無限ハング。

**Better Approach**: 操作タイプごとに明示的なタイムアウトを設定。プーリングには`IHttpClientFactory`を検討。

---

## Quick Reference

### 実装チェックリスト

- [ ] NuGetインストール: `CommunityToolkit.Mvvm`、`Microsoft.Extensions.DependencyInjection`
- [ ] `Infrastructure/Configuration/`に4ファイル作成（Step 2）
- [ ] `Infrastructure/Difys/DifyApiService.cs`作成（Step 3）
- [ ] `Presentation/ViewModels/DifyConfigViewModel.cs`作成（Step 4）
- [ ] `Presentation/Views/DifyConfigDialog.xaml` + `.xaml.cs`作成（Step 4）
- [ ] `App.xaml.cs`でサービス登録（Step 5）
- [ ] すべての`YourApp` / `YourAppName`プレースホルダーを置換（Step 6）
- [ ] テスト: 設定保存 → リロード → 復号化確認
- [ ] テスト: ファイルアップロード → ワークフロー実行 → SSE進捗確認

---

## Resources

- `local_docs/DifyAPI実装ガイド.md` — 完全な実装リファレンス（社内限定ドキュメント、本リポジトリ外）
- `local_docs/共通セキュリティコンポーネント.md` — DPAPI詳細（社内限定ドキュメント、本リポジトリ外）
- [CommunityToolkit.Mvvm ドキュメント](https://learn.microsoft.com/ja-jp/dotnet/communitytoolkit/mvvm/)
- [Dify APIドキュメント](https://docs.dify.ai/)

---

## Changelog

### バージョン 1.0.0 (2026-02-15)
- 初回リリース: 単一ワークフローDify API連携ガイド
- 6ステップワークフロー: 構造 → 設定 → クライアント → UI → DI → カスタマイズ
- CurrentUserスコープでのDPAPI暗号化
- リアルタイム進捗レポート付きSSEストリーミング
- CommunityToolkit.Mvvm統合

<!--
English version: ../SKILL.md
英語版: ../SKILL.md
-->
