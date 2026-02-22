<!-- このドキュメントは dotnet-wpf-ocr-parameter-input の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-wpf-ocr-parameter-input
description: WPFにOCR実行パラメータ入力UIタブを構築。進捗表示付き。OCR処理タブに設定可能な入力フィールドを追加する際に使用。
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, wpf, csharp, mvvm, ocr, progress, tab]
  invocable: false
---

# OCR実行パラメータ入力タブの構築（進捗表示付き）

.NET WPFアプリケーションにOCR実行パラメータ入力UIタブを追加するエンドツーエンドワークフロー：設定可能な入力フィールド（ComboBox、TextBox、CheckBox）、`IProgress<T>`による非同期OCR実行、リアルタイム進捗バーとログ表示、イベントベースの結果ハンドオフ（親ViewModelへの受け渡し）。

## When to Use This Skill

以下の場合にこのスキルを使用してください：
- ユーザー設定可能な入力パラメータ付きOCR処理タブを追加するとき
- 長時間実行されるOCR処理に進捗表示（バー＋ログ）を構築するとき
- 実行前に選択フィールド、テキストフィールド、トグルを収集するタブUIを作成するとき
- リアルタイム進捗レポート付きの非同期OCR実行を実装するとき
- OCR完了イベントを親ViewModelに接続して結果を処理するとき

---

## Related Skills

- **`dotnet-wpf-pdf-preview`** — PDFアップロードとWebView2プレビュー（PDFパス入力を提供）
- **`dotnet-wpf-dify-api-integration`** — OCR抽出バックエンド用Dify API連携
- **`dotnet-oracle-wpf-integration`** — OCR結果をOracleデータベースに保存
- **`dotnet-wpf-comparison-view`** — OCR結果を元のPDFと並べて比較表示
- **`git-commit-practices`** — 各ステップをアトミックな変更としてコミット

---

## Dependencies

- .NET + WPF (Windows Presentation Foundation)
- `CommunityToolkit.Mvvm` (ObservableObject, `[ObservableProperty]`, `[RelayCommand]`)
- OCR実行ユースケースインターフェース（例：`IOcrUseCase`）とOCRバックエンド（Dify等）

---

## Core Principles

1. **まず聞く、次に作る** — 入力フィールドはユースケースごとに異なるため、コード生成前に必ずユーザーに必要なフィールドを確認する（ニュートラル）
2. **MVVM規律** — ViewModelがすべての入力状態とOCR実行ロジックを所有し、Viewは純粋な宣言的XAML（基礎と型）
3. **非同期進捗レポート** — 非同期OCR操作からのスレッドセーフな進捗更新に`IProgress<T>`を使用（継続は力）
4. **イベントベースのハンドオフ** — OCR結果は直接結合ではなくイベント経由で親ViewModelに流れる（ニュートラル）
5. **再利用可能なスケルトン** — タブパターン（入力→進捗→結果）はOCRだけでなく、あらゆる長時間処理に適用可能（成長の複利）

---

## Workflow: Add OCR Parameter Input Tab to WPF

### Step 1 — 入力フィールド要件の定義

コード作成前にOCRタブに必要な入力フィールドを決定するときに使用します。

⚠️ **ユーザーに確認してください** — 必要な入力フィールドを確認します。具体的なフィールドはユースケースにより異なるため、仮定しないでください。まず要件を収集し、それからコードを生成します。

**一般的なフィールドタイプ**：
- **選択フィールド**（ComboBox） — 例：分類カテゴリ、ドキュメントタイプ
- **テキストフィールド**（TextBox） — 例：追加指示、備考、参照番号
- **トグルフィールド**（CheckBox） — 例：国内/輸出選択、優先フラグ

**フィールド定義テンプレート**：

```csharp
public class OcrInputField
{
    public string Label { get; set; }
    public string FieldType { get; set; } // "ComboBox", "TextBox", "CheckBox"
    public List<string>? Options { get; set; } // For ComboBox
}
```

**要件収集の例**：

| フィールド名 | タイプ | オプション | 必須 |
|-------------|--------|-----------|------|
| カテゴリ | ComboBox | ユーザーに確認 | ✅ |
| ドキュメントタイプ | ComboBox | ユーザーに確認 | ✅ |
| 備考 | TextBox | 自由入力 | ❌ |
| 輸出フラグ | CheckBox | オン/オフ | ❌ |

```
YourApp/
├── Views/
│   └── OcrProcessTabView.xaml          # 🆕 入力フィールド＋進捗付きタブUI
│   └── OcrProcessTabView.xaml.cs       # 🆕 最小限のcode-behind
├── ViewModels/
│   └── OcrProcessTabViewModel.cs       # 🆕 入力状態＋OCR実行＋進捗
└── Models/
    └── ProgressLogItem.cs              # 🆕 進捗ログエントリモデル
```

> **Values**: ニュートラル / 基礎と型

### Step 2 — タブViewModelの作成

入力フィールド、OCR実行、進捗追跡を管理するViewModelを実装するときに使用します。

`CommunityToolkit.Mvvm`を使用して`OcrProcessTabViewModel`を作成します。入力フィールドのプロパティはユースケースごとにカスタマイズします（Step 1の結果）。進捗追跡とOCR実行は固定パターンに従います。

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;

namespace YourApp.ViewModels
{
    public partial class OcrProcessTabViewModel : ObservableObject
    {
        private readonly IOcrUseCase _useCase;

        // --- Input fields (customize per use case from Step 1) ---
        [ObservableProperty] private string selectedCategory = "";
        [ObservableProperty] private string selectedType = "";
        [ObservableProperty] private string remarks = "";

        // --- Progress tracking (fixed pattern) ---
        [ObservableProperty] private int progressValue;
        [ObservableProperty] private string progressMessage = "";
        [ObservableProperty] private bool isProcessing;
        [ObservableProperty] private bool canStartOcr;

        // --- Collections ---
        public ObservableCollection<string> CategoryItems { get; } = new();
        public ObservableCollection<string> TypeItems { get; } = new();
        public ObservableCollection<ProgressLogItem> ProgressItems { get; } = new();

        /// <summary>
        /// Raised when OCR completes. Parent ViewModel subscribes to handle results.
        /// </summary>
        public event EventHandler<IEnumerable<object>>? OcrCompleted;

        public OcrProcessTabViewModel(IOcrUseCase useCase)
            => _useCase = useCase;

        [RelayCommand(CanExecute = nameof(CanStartOcr))]
        private async Task StartOcrAsync()
        {
            IsProcessing = true;
            ProgressValue = 0;
            ProgressItems.Clear();

            var progress = new Progress<(int percent, string message)>(p =>
            {
                ProgressValue = p.percent;
                ProgressMessage = p.message;
                ProgressItems.Add(new ProgressLogItem(DateTime.Now, "🔄", p.message, "Running"));
            });

            try
            {
                var results = await _useCase.ExecuteAsync(/* params */, progress);
                ProgressItems.Add(new ProgressLogItem(DateTime.Now, "✅", "OCR completed", "Done"));
                ProgressValue = 100;
                OcrCompleted?.Invoke(this, results);
            }
            catch (Exception ex)
            {
                ProgressItems.Add(new ProgressLogItem(DateTime.Now, "❌", ex.Message, "Error"));
            }
            finally
            {
                IsProcessing = false;
            }
        }

        /// <summary>
        /// Called by parent ViewModel when a PDF is uploaded.
        /// Enables the Start button.
        /// </summary>
        public void OnPdfUploaded(string pdfPath)
        {
            CanStartOcr = true;
            StartOcrCommand.NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Resets all progress state for re-execution.
        /// </summary>
        public void Reset()
        {
            ProgressItems.Clear();
            ProgressValue = 0;
            ProgressMessage = "";
            CanStartOcr = false;
            StartOcrCommand.NotifyCanExecuteChanged();
        }
    }
}
```

**`CanExecute`をコマンドに使用する理由**: PDFがアップロードされるまでStartボタンは無効化されます。`CanStartOcr`が変更されたとき、`NotifyCanExecuteChanged()`がボタンの状態を更新します。

> **Values**: 基礎と型 / 継続は力

### Step 3 — XAMLタブViewの構築

入力フィールド、進捗バー、進捗ログ、Startボタンを持つタブUIを作成するときに使用します。

タブレイアウトは4行Gridを使用：入力フィールドセクション、パーセンテージオーバーレイ付き進捗バー、スクロール可能な進捗ログ（GridViewカラム付きListView）、PDFアップロード後に有効化されるStartボタン。

```xml
<UserControl x:Class="YourApp.Views.OcrProcessTabView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>  <!-- Input Fields -->
            <RowDefinition Height="Auto"/>  <!-- Progress Bar -->
            <RowDefinition Height="*"/>     <!-- Progress Log -->
            <RowDefinition Height="Auto"/>  <!-- Start Button -->
        </Grid.RowDefinitions>

        <!-- Input Fields (customize per use case) -->
        <StackPanel Grid.Row="0" Margin="10">
            <TextBlock Text="Category" FontWeight="Bold"/>
            <ComboBox ItemsSource="{Binding CategoryItems}"
                      SelectedItem="{Binding SelectedCategory}"
                      Margin="0,4,0,10"/>

            <TextBlock Text="Document Type" FontWeight="Bold"/>
            <ComboBox ItemsSource="{Binding TypeItems}"
                      SelectedItem="{Binding SelectedType}"
                      Margin="0,4,0,10"/>

            <TextBlock Text="Remarks" FontWeight="Bold"/>
            <TextBox Text="{Binding Remarks, UpdateSourceTrigger=PropertyChanged}"
                     AcceptsReturn="True" Height="60"
                     Margin="0,4,0,0"/>
        </StackPanel>

        <!-- Progress Bar with Percentage Overlay -->
        <Grid Grid.Row="1" Margin="10,5">
            <ProgressBar Value="{Binding ProgressValue}" Maximum="100" Height="20"/>
            <TextBlock Text="{Binding ProgressValue, StringFormat='{}{0}%'}"
                       HorizontalAlignment="Center" VerticalAlignment="Center"
                       FontWeight="Bold"/>
        </Grid>

        <!-- Progress Log -->
        <ListView Grid.Row="2" ItemsSource="{Binding ProgressItems}" Margin="10,5">
            <ListView.View>
                <GridView>
                    <GridViewColumn Header="Time" Width="80"
                        DisplayMemberBinding="{Binding Timestamp, StringFormat='{}{0:HH:mm:ss}'}"/>
                    <GridViewColumn Header="" Width="30"
                        DisplayMemberBinding="{Binding Icon}"/>
                    <GridViewColumn Header="Message" Width="200"
                        DisplayMemberBinding="{Binding Message}"/>
                    <GridViewColumn Header="Status" Width="80"
                        DisplayMemberBinding="{Binding Status}"/>
                </GridView>
            </ListView.View>
        </ListView>

        <!-- Start Button (enabled after PDF upload) -->
        <Button Grid.Row="3" Content="Start OCR"
                Command="{Binding StartOcrCommand}"
                Background="#4CAF50" Foreground="White" FontWeight="Bold"
                Margin="10" Padding="15,8" FontSize="14"/>
    </Grid>
</UserControl>
```

**WindowではなくUserControlを使用する理由**: タブは親の`TabControl`に埋め込まれます。`UserControl`は自然に統合されますが、`Window`は別ウィンドウ管理が必要になります。

> **Values**: 基礎と型 / ニュートラル

### Step 4 — 進捗ログアイテムモデルの作成

ListViewに表示される個々の進捗ログエントリのデータモデルを定義するときに使用します。

進捗ログの各行に対するシンプルなイミュータブルモデルを作成します。コンストラクタにより、作成時にすべてのフィールドが設定されることを保証します。

```csharp
namespace YourApp.Models
{
    public class ProgressLogItem
    {
        public DateTime Timestamp { get; }
        public string Icon { get; }
        public string Message { get; }
        public string Status { get; }

        public ProgressLogItem(DateTime timestamp, string icon, string message, string status)
        {
            Timestamp = timestamp;
            Icon = icon;
            Message = message;
            Status = status;
        }
    }
}
```

**アイコン規約**：

| アイコン | 意味 |
|---------|------|
| 🔄 | 処理中 / 進行中 |
| ✅ | 正常完了 |
| ❌ | エラー発生 |
| ⚠️ | 警告 |

> **Values**: 基礎と型 / 成長の複利

### Step 5 — イベント接続とタブ統合

OCRタブを親ViewModelに接続し、`TabControl`に統合するときに使用します。

親ViewModelがタブViewModelを作成し、`OcrCompleted`をサブスクライブしてタブ切り替えを管理します。PDFアップロードイベントは`OnPdfUploaded`経由で親からOCRタブに流れます。

**親ViewModelの接続** — `OcrCompleted`をサブスクライブし、`OnPdfUploaded`を呼び出す：

```csharp
OcrTab = new OcrProcessTabViewModel(useCase);
OcrTab.OcrCompleted += OnOcrCompleted;
```

**イベントフロー**：

```
PDF Upload → Parent.NotifyPdfUploaded() → OcrTab.OnPdfUploaded()
                                            ↓ (enables Start button)
User clicks Start → OcrTab.StartOcrAsync() → IProgress updates UI
                                            ↓ (on completion)
OcrTab.OcrCompleted event → Parent.OnOcrCompleted() → Switch to results tab
```

完全な接続例（親ViewModel、TabControl、状態リセット）: [`references/detailed-patterns.md`](../references/detailed-patterns.md)

> **Values**: ニュートラル / 継続は力

### Step 6 — 入力フィールドのカスタマイズ

Step 1で収集した具体的なユースケース要件に合わせて、生成されたスケルトンを適用するときに使用します。

⚠️ **プレースホルダーフィールドを置換してください** — Step 1で特定した実際のフィールドに置き換えます。以下の表がカスタマイズのガイドです：

| カスタマイズ項目 | ファイル | 変更内容 |
|----------------|---------|---------|
| 入力フィールドプロパティ | `OcrProcessTabViewModel.cs` | `[ObservableProperty]`フィールドの追加/削除 |
| ComboBoxオプション | `OcrProcessTabViewModel.cs` | `ObservableCollection`アイテムの設定 |
| XAML入力セクション | `OcrProcessTabView.xaml` | ComboBox、TextBox、CheckBoxコントロールの追加/削除 |
| ユースケースパラメータ | `StartOcrAsync()` | `_useCase.ExecuteAsync()`に正しい入力値を渡す |
| バリデーションルール | `OcrProcessTabViewModel.cs` | OCR実行前のフィールドバリデーション追加 |

**CheckBoxトグルフィールドの追加**：

```csharp
// ViewModel
[ObservableProperty] private bool isExport;
```

```xml
<!-- XAML -->
<CheckBox Content="Export" IsChecked="{Binding IsExport}" Margin="0,10,0,0"/>
```

**必須フィールドバリデーションの追加**：

```csharp
[RelayCommand(CanExecute = nameof(CanStartOcr))]
private async Task StartOcrAsync()
{
    // ✅ Validate required fields before execution
    if (string.IsNullOrWhiteSpace(SelectedCategory))
    {
        ProgressItems.Add(new ProgressLogItem(DateTime.Now, "⚠️", "Category is required", "Validation"));
        return;
    }
    // ... proceed with OCR
}
```

> **Values**: ニュートラル / 基礎と型

---

## Good Practices

### 1. 非同期進捗レポートにIProgress\<T\>を使用

**What**: スレッドセーフな進捗コールバックのために`IProgress<(int percent, string message)>`をユースケースに渡します。

**Why**: `IProgress<T>`は作成時に`SynchronizationContext`をキャプチャし、UIスレッドへのコールバックディスパッチを自動的に行います。手動の`Dispatcher.Invoke`は不要です。

**Values**: 継続は力（非同期の型を正しく使う）

### 2. 進捗更新をUIスレッドにディスパッチ

**What**: コールバックが自動的にマーシャリングされるよう、UIスレッド上で`Progress<T>`インスタンスを作成します。

**Why**: `Progress<T>`がバックグラウンドスレッドで作成されると、コールバックはそのスレッドで実行され、`ObservableCollection`の更新時に例外をスローします。

```csharp
// ✅ CORRECT — Created on UI thread, callbacks auto-dispatch
var progress = new Progress<(int percent, string message)>(p =>
{
    ProgressValue = p.percent;
    ProgressItems.Add(new ProgressLogItem(DateTime.Now, "🔄", p.message, "Running"));
});

// ❌ WRONG — Created inside Task.Run, callbacks on background thread
await Task.Run(() =>
{
    var progress = new Progress<(int, string)>(...); // Wrong thread
});
```

**Values**: 基礎と型（スレッド安全の型）

### 3. 処理中はStartボタンを無効化

**What**: 開始時に`IsProcessing = true`を設定し、`CanExecute`で重複実行を防止します。

**Why**: OCR実行中にStartをダブルクリックすると、並列プロセスが起動し、結果が破損し、進捗表示が混乱する可能性があります。

**Values**: ニュートラル（安全なUI操作）

### 4. 再実行のための状態リセット

**What**: 新しいPDFがアップロードされたときに`ProgressItems`をクリアし、`ProgressValue`をリセットし、`CanStartOcr`を更新します。

**Why**: 前回実行の古い進捗がユーザーを誤解させます。クリーンな状態により、各実行が新鮮な状態で開始されます。

**Values**: 継続は力（再実行の信頼性）

---

## Common Pitfalls

### 1. 非同期コールバックからUIスレッドにディスパッチしない

**Problem**: バックグラウンドスレッドから`ObservableCollection`や`ObservableProperty`を更新すると`InvalidOperationException`がスローされます。

**Solution**: `Progress<T>`をUIスレッド上（`await`の前）で作成します。バックグラウンドスレッドからの`IProgress<T>.Report()`呼び出しは、キャプチャされた`SynchronizationContext`に自動的にディスパッチされます。

```csharp
// ❌ WRONG — Direct collection update from background thread
await Task.Run(() =>
{
    ProgressItems.Add(new ProgressLogItem(...)); // Throws!
});

// ✅ CORRECT — IProgress<T> handles marshaling
var progress = new Progress<(int percent, string message)>(p =>
{
    ProgressItems.Add(new ProgressLogItem(DateTime.Now, "🔄", p.message, "Running"));
});
await _useCase.ExecuteAsync(progress); // Reports from background thread safely
```

### 2. 完了後にStartボタンを再有効化し忘れ

**Problem**: `IsProcessing`が`true`に設定されたまま例外時にリセットされず、Startボタンが永久に無効化されます。

**Solution**: 常に`finally`ブロックで`IsProcessing`をリセットします。

```csharp
// ❌ WRONG — IsProcessing stuck on exception
IsProcessing = true;
var results = await _useCase.ExecuteAsync(progress);
IsProcessing = false; // Never reached on exception

// ✅ CORRECT — finally guarantees reset
try { var results = await _useCase.ExecuteAsync(progress); }
finally { IsProcessing = false; }
```

### 3. 再実行時に進捗ログをクリアしない

**Problem**: 前回実行のログエントリが新しい実行と混在し、ユーザーが混乱します。

**Solution**: 実行開始時に毎回`ProgressItems.Clear()`と`ProgressValue = 0`を呼び出します。

```csharp
[RelayCommand(CanExecute = nameof(CanStartOcr))]
private async Task StartOcrAsync()
{
    // ✅ Always clear before starting
    ProgressItems.Clear();
    ProgressValue = 0;
    // ... execute OCR
}
```

---

## Anti-Patterns

### 同期処理によるUIスレッドのブロック

**What**: UIスレッドから非同期OCR操作に対して`.Wait()`や`.Result`を呼び出すこと。

**Why It's Wrong**: UIスレッドをブロックし、ウィンドウがフリーズし、進捗バーの更新が妨げられ、`SynchronizationContext`でデッドロックを引き起こす可能性があります。

**Better Approach**: 全体を通して`async Task`と`await`を使用します。`[RelayCommand]`属性は非同期実行を正しく処理する`IAsyncRelayCommand`を生成します。

```csharp
// ❌ WRONG — Blocks UI, no progress updates
[RelayCommand]
private void StartOcr()
{
    var results = _useCase.ExecuteAsync(progress).Result; // Deadlock risk
}

// ✅ CORRECT — Non-blocking, progress updates flow
[RelayCommand(CanExecute = nameof(CanStartOcr))]
private async Task StartOcrAsync()
{
    var results = await _useCase.ExecuteAsync(progress);
}
```

### 入力フィールドを設定可能にせずハードコード

**What**: ユーザーに確認せずに、特定のフィールド名とオプションをViewModelに直接埋め込むこと。

**Why It's Wrong**: ユースケースごとに入力要件が異なります。ハードコードされたフィールドは、要件変更時にタブ全体のリファクタリングを強制します。

**Better Approach**: Step 1に従い、ユーザーに必要なフィールドを確認します。ユーザーの要件からViewModelとXAMLを生成します。硬直的な実装ではなく、スケルトンパターンを提供してください。

---

## Quick Reference

### 実装チェックリスト

- [ ] ユーザーに必要な入力フィールドを確認（Step 1）
- [ ] `ProgressLogItem`モデルクラスを作成（Step 4）
- [ ] 入力フィールド＋進捗付き`OcrProcessTabViewModel`を作成（Step 2）
- [ ] 4行Gridレイアウトの`OcrProcessTabView.xaml`を作成（Step 3）
- [ ] 親ViewModelで`OcrCompleted`イベントを接続（Step 5）
- [ ] タブを`TabControl`に統合（Step 5）
- [ ] 親のPDFアップロードフローから`OnPdfUploaded`を接続（Step 5）
- [ ] ユースケースに合わせて入力フィールドをカスタマイズ（Step 6）
- [ ] テスト: PDFアップロードまでStartボタンが無効
- [ ] テスト: OCR実行中に進捗バーが更新される
- [ ] テスト: 進捗ログにタイムスタンプ付きエントリが表示される
- [ ] テスト: 処理中はStartボタンが無効
- [ ] テスト: 再アップロードで前回の進捗がクリアされる

### ファイル構造

| ファイル | 目的 | レイヤー |
|---------|------|---------|
| `OcrProcessTabView.xaml` | 入力フィールド＋進捗表示付きタブUI | View |
| `OcrProcessTabView.xaml.cs` | 最小限のcode-behind | View (code-behind) |
| `OcrProcessTabViewModel.cs` | 入力状態＋OCR実行＋進捗 | ViewModel |
| `ProgressLogItem.cs` | 進捗ログエントリモデル | Model |

### 進捗アイコンリファレンス

| アイコン | 用途 | タイミング |
|---------|------|-----------|
| 🔄 | 進行中 | 各進捗コールバック |
| ✅ | 成功 | OCR完了 |
| ❌ | エラー | 例外キャッチ |
| ⚠️ | 警告 | バリデーション失敗 |

---

## Resources

- **`dotnet-wpf-pdf-preview`** — このタブに入力を提供するPDFアップロード
- **`dotnet-wpf-dify-api-integration`** — OCR実行用Dify APIバックエンド
- [CommunityToolkit.Mvvm ドキュメント](https://learn.microsoft.com/ja-jp/dotnet/communitytoolkit/mvvm/)
- [IProgress\<T\> パターン](https://learn.microsoft.com/ja-jp/dotnet/api/system.progress-1)
- [WPF TabControl](https://learn.microsoft.com/ja-jp/dotnet/desktop/wpf/controls/tabcontrol)

---

## Changelog

### バージョン 1.0.0 (2026-02-18)
- 初回リリース: 進捗表示付きOCR実行パラメータ入力タブ
- 6ステップワークフロー: 要件定義 → ViewModel → XAML → モデル → イベント → カスタマイズ
- 設定可能な入力フィールドパターン（まずユーザーに確認）
- IProgress\<T\>による非同期進捗レポート（UIスレッド安全）
- 進捗バー＋タイムスタンプ付きログListView
- イベントベースのOCR結果ハンドオフ（親ViewModelへの受け渡し）
- CommunityToolkit.Mvvm統合（`[RelayCommand]`と`[ObservableProperty]`）

<!-- 英語版は ../SKILL.md を参照してください -->
