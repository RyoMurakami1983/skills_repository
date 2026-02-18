---
name: dotnet-wpf-pdf-preview
description: WPFアプリにPDFアップロードとWebView2プレビューを追加。MVVMファイル選択と非同期初期化対応。
author: RyoMurakami1983
tags: [dotnet, wpf, csharp, mvvm, webview2, pdf]
invocable: false
version: 1.0.0
---

# WPFアプリケーションへのPDFアップロードとWebView2プレビュー追加

.NET WPFアプリケーションにPDFファイルアップロードとインラインプレビューを追加するためのエンドツーエンドワークフロー：WebView2ベースのPDFレンダリング、`CommunityToolkit.Mvvm`によるMVVMファイル選択、イベントベースのViewModel→View通信、エラーハンドリング付き非同期WebView2初期化。

## このスキルを使うタイミング

以下の場合にこのスキルを使用してください：
- WPFアプリケーションにPDFアップロードとプレビューパネルを追加するとき
- Microsoft Edge WebView2を使用してPDFファイルをインライン表示するとき
- 左側にPDFプレビュー、右側にコンテンツの分割パネルレイアウトを構築するとき
- ViewModelでファイル選択を実装し、WebView2をcode-behindに保持するとき
- アップロードしたドキュメントを表示する注文書アップロードUIを作成するとき

---

## 関連スキル

- **`dotnet-wpf-secure-config`** — DPAPI暗号化基盤（認証情報の保存用）
- **`dotnet-wpf-dify-api-integration`** — アップロードしたPDFをDify APIに送信してOCR抽出
- **`dotnet-oracle-wpf-integration`** — 抽出したPDFデータをOracleデータベースに保存
- **`git-commit-practices`** — 各ステップをアトミックな変更としてコミット

---

## コア原則

1. **MVVM規律** — ViewModelがファイル選択ロジックを所有し、ViewがWebView2レンダリングを所有（基礎と型）
2. **最小限のcode-behind** — WebView2の初期化とナビゲーションのみをcode-behindに配置（基礎と型）
3. **イベントベース通信** — ViewModelがイベントでViewに通知。コントロールへの直接アクセスは禁止（ニュートラル）
4. **デフォルトで非同期** — WebView2の初期化は非同期。UIスレッドのブロック禁止（継続は力）
5. **グレースフルデグラデーション** — WebView2 Runtimeが見つからない場合もクラッシュしない（ニュートラル）

---

## ワークフロー: WPFにPDFプレビューを追加

### Step 1 — WebView2のインストールとレイアウトセットアップ

WebView2 NuGetパッケージを追加し、分割パネルのXAMLレイアウトを作成するときに使用します。

WebView2パッケージをインストールし、左側にPDFプレビュー、右側にコンテンツエリアの2カラムGridを作成します。

```powershell
# Install WebView2 NuGet package
Install-Package Microsoft.Web.WebView2
```

```
YourApp/
├── Views/
│   └── MainWindow.xaml          # 🆕 WebView2付き2カラムレイアウト
│   └── MainWindow.xaml.cs       # 🆕 WebView2初期化 + ナビゲーション
└── ViewModels/
    └── MainViewModel.cs         # 🆕 ファイル選択 + パス管理
```

**XAMLレイアウトテンプレート** — 2カラム分割パネル：

```xml
<Window x:Class="YourApp.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:wv2="clr-namespace:Microsoft.Web.WebView2.Wpf;assembly=Microsoft.Web.WebView2.Wpf"
        Title="PDF Preview" Height="700" Width="1200">
    <Grid>
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="1*"/>   <!-- Left: PDF Preview -->
            <ColumnDefinition Width="1.5*"/> <!-- Right: Content -->
        </Grid.ColumnDefinitions>

        <Grid Grid.Column="0" Margin="5">
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>  <!-- Upload Button -->
                <RowDefinition Height="*"/>     <!-- PDF Preview -->
            </Grid.RowDefinitions>

            <Button Grid.Row="0" Content="Upload PDF"
                    Command="{Binding UploadPdfCommand}"
                    Background="#2196F3" Foreground="White" FontWeight="Bold"/>

            <Border Grid.Row="1" BorderBrush="#CCCCCC" BorderThickness="1">
                <wv2:WebView2 x:Name="PdfWebView" />
            </Border>
        </Grid>

        <!-- Right column: your content area -->
        <Grid Grid.Column="1" Margin="5">
            <!-- Add your application content here -->
        </Grid>
    </Grid>
</Window>
```

**WebView2でx:Nameを使用する理由**: WebView2は命令的な初期化（`EnsureCoreWebView2Async`）とナビゲーション（`CoreWebView2.Navigate`）が必要です。これらのAPIにはバインド可能な代替がないため、`x:Name`はMVVMの許容される例外です。

> **Values**: 基礎と型 / 継続は力

### Step 2 — ViewModelの実装（ファイル選択 + パス管理）

`OpenFileDialog`によるPDFファイル選択を処理し、Viewに通知するViewModelを作成するときに使用します。

`CommunityToolkit.Mvvm`を使用して`MainViewModel`を作成し、`[ObservableProperty]`で状態管理、`[RelayCommand]`でアップロードアクションを実装します。`PdfPathChanged`イベントがViewModel→View通信を橋渡しします。

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;

namespace YourApp.ViewModels
{
    public partial class MainViewModel : ObservableObject
    {
        /// <summary>
        /// Event to notify View when a new PDF is selected.
        /// Code-behind subscribes to this for WebView2 navigation.
        /// </summary>
        public event EventHandler<string>? PdfPathChanged;

        [ObservableProperty]
        private string pdfFilePath = string.Empty;

        [ObservableProperty]
        private bool isPdfLoaded;

        [RelayCommand]
        private void UploadPdf()
        {
            var dialog = new Microsoft.Win32.OpenFileDialog
            {
                Filter = "PDF files (*.pdf)|*.pdf",
                Title = "Select PDF file"
            };
            if (dialog.ShowDialog() == true)
            {
                PdfFilePath = dialog.FileName;
                IsPdfLoaded = true;
                PdfPathChanged?.Invoke(this, PdfFilePath);
            }
        }
    }
}
```

**バインディングではなくイベントパターンを使用する理由**: WebView2の`Source`プロパティはローカルファイルURLに対する信頼性の高い双方向バインディングをサポートしていません。イベントパターンによりナビゲーションのタイミングとエラーハンドリングを明示的に制御できます。

> **Values**: 基礎と型 / ニュートラル

### Step 3 — WebView2の初期化（code-behind）

ウィンドウのcode-behindでWebView2の初期化とPDFナビゲーションを配線するときに使用します。

WebView2を非同期で初期化し、ViewModelの`PdfPathChanged`イベントをサブスクライブしてナビゲーションする最小限のcode-behindを作成します。

```csharp
using System;
using System.Windows;

namespace YourApp.Views
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            var viewModel = new MainViewModel();
            DataContext = viewModel;
            InitializeWebView();
            viewModel.PdfPathChanged += OnPdfPathChanged;
        }

        private async void InitializeWebView()
        {
            try
            {
                await PdfWebView.EnsureCoreWebView2Async(null);
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"WebView2 Runtime not found.\n\n" +
                    $"Please install the WebView2 Runtime from:\n" +
                    $"https://developer.microsoft.com/microsoft-edge/webview2/\n\n" +
                    $"Error: {ex.Message}",
                    "WebView2 Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Warning);
            }
        }

        private void OnPdfPathChanged(object? sender, string pdfPath)
        {
            if (PdfWebView.CoreWebView2 != null)
            {
                PdfWebView.CoreWebView2.Navigate($"file:///{pdfPath}");
            }
        }
    }
}
```

**ここでasync voidが許容される理由**: `InitializeWebView`はファイア・アンド・フォーゲットのUI初期化です。`try/catch`がすべての失敗ケースを処理します。これは`async void`が適切な数少ないケースの一つ — イベント的なUI起動です。

> **Values**: ニュートラル / 基礎と型

### Step 4 — XAML名前空間の追加と配線

すべてのXAML名前空間とバインディングが正しく接続されていることを確認するときに使用します。

WebView2のXAML名前空間が宣言され、ボタンコマンドがViewModelにバインドされていることを確認します。

**必須XAML名前空間**（Windowタグ内）：

```xml
xmlns:wv2="clr-namespace:Microsoft.Web.WebView2.Wpf;assembly=Microsoft.Web.WebView2.Wpf"
```

**バインディングチェックリスト**：

```xml
<!-- ✅ 正しい — ボタンがViewModelコマンドにバインド -->
<Button Command="{Binding UploadPdfCommand}" Content="Upload PDF" />

<!-- ❌ 間違い — code-behindのクリックハンドラ -->
<Button Click="OnUploadClick" Content="Upload PDF" />
```

```xml
<!-- ✅ 正しい — WebView2はx:Nameを使用（MVVM例外） -->
<wv2:WebView2 x:Name="PdfWebView" />

<!-- ❌ 間違い — Sourceを直接バインドしようとしている -->
<wv2:WebView2 Source="{Binding PdfFileUri}" />
```

> **Values**: 基礎と型 / ニュートラル

### Step 5 — エッジケースの処理

デプロイメントと実運用シナリオの堅牢性を追加するときに使用します。

3つの主な障害シナリオを処理します：ランタイム不在、大きなファイル、再アップロード状態。

**WebView2 Runtimeが見つからない場合**：

```csharp
// ✅ Graceful fallback when WebView2 Runtime is not installed
private async void InitializeWebView()
{
    try
    {
        await PdfWebView.EnsureCoreWebView2Async(null);
    }
    catch (Exception)
    {
        // Show fallback UI or download link
        PdfWebView.Visibility = Visibility.Collapsed;
        // Show a TextBlock with download instructions instead
    }
}
```

**再アップロード（状態リセット）**：

```csharp
[RelayCommand]
private void UploadPdf()
{
    var dialog = new Microsoft.Win32.OpenFileDialog
    {
        Filter = "PDF files (*.pdf)|*.pdf",
        Title = "Select PDF file"
    };
    if (dialog.ShowDialog() == true)
    {
        // ✅ Reset state before loading new PDF
        PdfFilePath = dialog.FileName;
        IsPdfLoaded = true;
        PdfPathChanged?.Invoke(this, PdfFilePath);
    }
}
```

**大きなPDFファイル** — WebView2はChromium内蔵のPDFビューアを通じて大きなPDFをネイティブに処理します。特別な処理は不要ですが、ローディングインジケータの表示を検討してください：

```csharp
private void OnPdfPathChanged(object? sender, string pdfPath)
{
    if (PdfWebView.CoreWebView2 != null)
    {
        // Chromium PDF viewer handles large files with streaming
        PdfWebView.CoreWebView2.Navigate($"file:///{pdfPath}");
    }
}
```

> **Values**: ニュートラル / 継続は力

### Step 6 — アプリケーション固有のカスタマイズ

生成されたコードを本番デプロイ用に準備するときに使用します。

出荷前にこれらのプレースホルダーを置き換えてください：

| 項目 | ファイル | 変更内容 | スキップした場合の影響 |
|------|---------|---------|----------------------|
| 名前空間 | 全`.cs`ファイル | `YourApp` → 実際の名前空間 | ビルドエラー |
| ウィンドウタイトル | `MainWindow.xaml` | `"PDF Preview"` → 実際のタイトル | 汎用的なウィンドウタイトル |
| カラム比率 | `MainWindow.xaml` | `1*` / `1.5*` → 希望の比率 | レイアウトの不一致 |
| ボタンスタイル | `MainWindow.xaml` | テーマに合わせた色とフォント | UIの不統一 |
| アップロードフィルタ | `MainViewModel.cs` | 他のファイル種別を受け付ける場合のフィルタ | 不正なファイル種別 |

**カスタマイズチェックリスト**：

```powershell
# Verify all placeholders are replaced
Select-String -Path "Views/*.xaml","Views/*.cs","ViewModels/*.cs" -Pattern "YourApp" -SimpleMatch
# Expected: 0 matches after customization
```

> **Values**: 基礎と型 / 成長の複利

---

## グッドプラクティス

### 1. WebView2コードはcode-behindに保持

**What**: WebView2の初期化とナビゲーションは`MainWindow.xaml.cs`に配置し、ViewModelには置かない。

**Why**: WebView2は`x:Name`と命令的なAPI呼び出し（`EnsureCoreWebView2Async`、`CoreWebView2.Navigate`）が必要です。これはMVVMの許容される例外 — code-behindがViewModelイベントとWebView2 API間の薄いアダプタとして機能します。

**Values**: 基礎と型（MVVM例外の型）

### 2. ViewModel→View通信にイベントパターンを使用

**What**: ViewModelが`PdfPathChanged`イベントを発行し、code-behindがサブスクライブしてWebView2をナビゲート。

**Why**: ViewModelをテスト可能に保ちつつ（UI依存なし）、Viewにナビゲーションタイミングの明示的な制御を与えます。代替手段（Messenger、Behavior）はこのユースケースではメリットなく複雑さが増します。

**Values**: ニュートラル / 基礎と型

### 3. ウィンドウロード時にWebView2を非同期初期化

**What**: `EnsureCoreWebView2Async`をコンストラクタまたは`Loaded`イベントで呼び出し、最初のPDFアップロード時には呼び出さない。

**Why**: WebView2の初期化には100〜500msかかります。事前に実行することで、ユーザーが最初にアップロードをクリックしたときの目に見える遅延を回避します。

**Values**: 継続は力（先回りの準備）

---

## よくある落とし穴

### 1. デプロイ先のマシンにWebView2 Runtimeをインストールし忘れる

**Problem**: WebView2 RuntimeはWindows 11にはプリインストールされていますが、Windows 10やロックダウンされた企業マシンでは欠落している場合があります。

**Solution**: インストーラにWebView2 Evergreen Bootstrapperを含めるか、ダウンロードリンクを検出してユーザーに提示します。`EnsureCoreWebView2Async`は常にtry/catchで囲みます。

```csharp
// ❌ 間違い — エラーハンドリングなし、Runtimeのないマシンでクラッシュ
await PdfWebView.EnsureCoreWebView2Async(null);

// ✅ 正しい — グレースフルフォールバック
try { await PdfWebView.EnsureCoreWebView2Async(null); }
catch (Exception ex) { ShowWebView2MissingMessage(ex); }
```

### 2. WebView2のSourceプロパティを直接バインドしようとする

**Problem**: ローカルファイルURLに対して`<wv2:WebView2 Source="{Binding PdfUri}" />`を使用しても確実に動作しない。

**Solution**: イベントパターン（Step 2〜3）と`CoreWebView2.Navigate()`を使用して、ローカルファイルの確実なナビゲーションを実現します。

```csharp
// ❌ 間違い — ローカルファイルにSourceをバインド
<wv2:WebView2 Source="{Binding PdfFileUri}" />

// ✅ 正しい — イベント経由の命令的ナビゲーション
PdfWebView.CoreWebView2.Navigate($"file:///{pdfPath}");
```

### 3. WebView2初期化の失敗を処理しない

**Problem**: WebView2 Runtimeが見つからないか破損している場合、`EnsureCoreWebView2Async`が例外をスローし、未処理の例外クラッシュを引き起こす。

**Solution**: 常にtry/catchで囲み、RuntimeダウンロードURLを含むユーザーフレンドリーなメッセージを表示します。

---

## アンチパターン

### ファイルダイアログロジックをcode-behindに配置

**What**: `MainWindow.xaml.cs`のボタンクリックハンドラで`OpenFileDialog`を直接開く。

**Why It's Wrong**: MVVM分離に違反。ファイル選択はアプリケーションロジックであり、UIレンダリングではありません。code-behindのファイルダイアログロジックはユニットテスト不可能です。

**Better Approach**: ViewModelの`[RelayCommand]`でファイル選択を処理。ダイアログ結果がViewModelプロパティを更新し、Viewがそれを監視します。

### WebView2以外のコントロールにx:Nameを使用

**What**: TextBox、Button、DataGridに`x:Name`を追加してcode-behindで操作する。

**Why It's Wrong**: データバインディングをバイパスし、UIがcode-behindに密結合になります。すべての`x:Name`参照はバインディングの機会を逃しています。

**Better Approach**: すべての標準WPFコントロールに`{Binding}`を使用。命令的APIが必要なコントロール（WebView2）にのみ`x:Name`を限定使用します。

```csharp
// ❌ 間違い — 名前でコントロールを操作
StatusLabel.Text = "PDF loaded";
UploadButton.IsEnabled = false;

// ✅ 正しい — ViewModelプロパティにバインド
[ObservableProperty] private string statusText = "Ready";
[ObservableProperty] private bool canUpload = true;
```

---

## クイックリファレンス

### 実装チェックリスト

- [ ] `Microsoft.Web.WebView2` NuGetパッケージをインストール
- [ ] WebView2用の`wv2` XAML名前空間を追加
- [ ] 2カラムGridレイアウトを作成（プレビュー + コンテンツ）
- [ ] `x:Name="PdfWebView"`で`WebView2`コントロールを追加
- [ ] アップロード用の`[RelayCommand]`を持つViewModelを作成
- [ ] ViewModelに`PdfPathChanged`イベントを追加
- [ ] code-behindでイベントをサブスクライブ
- [ ] try/catch付きでWebView2を非同期初期化
- [ ] `CoreWebView2.Navigate()`でPDFにナビゲート
- [ ] WebView2 Runtimeが見つからないシナリオでテスト

### ファイル構造

| ファイル | 目的 | レイヤー |
|---------|------|---------|
| `MainWindow.xaml` | 2カラムレイアウト + WebView2 | View |
| `MainWindow.xaml.cs` | WebView2初期化 + ナビゲーション | View（code-behind） |
| `MainViewModel.cs` | ファイル選択 + 状態管理 | ViewModel |

### WebView2ナビゲーションパターン

| シナリオ | コード |
|---------|-------|
| ローカルPDFファイル | `CoreWebView2.Navigate($"file:///{path}")` |
| 空白ページ | `CoreWebView2.Navigate("about:blank")` |
| 準備状態の確認 | `if (PdfWebView.CoreWebView2 != null)` |

---

## リソース

- [Microsoft WebView2 SDKドキュメント](https://docs.microsoft.com/microsoft-edge/webview2/)
- [WebView2 NuGetパッケージ](https://www.nuget.org/packages/Microsoft.Web.WebView2)
- [WebView2 Runtimeダウンロード](https://developer.microsoft.com/microsoft-edge/webview2/)
- [CommunityToolkit.Mvvm ドキュメント](https://learn.microsoft.com/ja-jp/dotnet/communitytoolkit/mvvm/)

---

## 変更履歴

### バージョン 1.0.0 (2026-02-15)
- 初回リリース: 単一ワークフローPDFアップロード + WebView2プレビューガイド
- 6ステップワークフロー: レイアウト → ViewModel → code-behind → 名前空間 → エッジケース → カスタマイズ
- イベントベースのViewModel→View通信パターン
- エラーハンドリング付きWebView2非同期初期化
- CommunityToolkit.Mvvm統合（`[RelayCommand]`と`[ObservableProperty]`）

<!--
English version available at ../SKILL.md
英語版は ../SKILL.md を参照してください
-->
