---
name: dotnet-wpf-employee-input
description: >
  こんなときに使う: WPFアプリケーションに社員番号入力ダイアログを追加し、
  DPAPIで暗号化された設定として社員IDを安全に保存したいとき。
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, wpf, csharp, mvvm, employee, dpapi, configuration]
  invocable: false
---
# WPFアプリケーションへの社員番号入力ダイアログ追加

WPFアプリケーションに社員番号（社員番号）入力ダイアログを追加するためのエンドツーエンドワークフロー：4桁バリデーション、`SecureConfigService`によるDPAPI暗号化保存、MVVM設定UI、メニューバー統合。

## こんなときに使う

以下の場合にこのスキルを使用してください：
- WPFアプリケーションに社員番号設定ダイアログを追加するとき
- 社員IDをDPAPI暗号化で安全に保存するとき（平文保存は不可）
- 固定長数値入力を検証する設定ダイアログを構築するとき
- 社員番号の設定・更新・リセット用ユーザー向けUIを提供するとき
- Dify API呼び出しやその他サービスに社員識別を統合するとき

---

## Related Skills

- **`dotnet-wpf-secure-config`** — 必須：DPAPI暗号化基盤（先に適用）
- **`dotnet-wpf-dify-api-integration`** — Dify API呼び出しの`user`フィールドに社員番号を使用
- **`dotnet-oracle-wpf-integration`** — 同じアプリでSecureConfigServiceを共有
- **`tdd-standard-practice`** — Red-Green-Refactorで生成コードをテスト
- **`git-commit-practices`** — 各ステップをアトミックな変更としてコミット

---

## Core Principles

1. **デフォルトでセキュア** — 社員番号はDPAPIで保存。平文設定ファイルには保存しない（ニュートラル）
2. **MVVM規律** — ViewModelがすべての保存/読み込み/リセットロジックを駆動。code-behindは最小限（基礎と型）
3. **永続化前にバリデーション** — SecureConfigService呼び出し前にViewModelでフォーマット検証を実施（基礎と型）
4. **段階的な統合** — 前提条件 → ViewModel → View → 配線 → メニュー、一層ずつ確実に（継続は力）
5. **再利用可能なパターン** — ダイアログパターンは任意の単一フィールドセキュア設定入力に適用可能（成長の複利）

---

## Workflow: Add Employee Number Dialog to WPF

### Step 1 — 前提条件のセットアップ

`dotnet-wpf-secure-config` 適用済みプロジェクトに社員番号ファイルを追加するときに使用します。

**前提条件**（先に完了必須）:
- `dotnet-wpf-secure-config` スキル適用済み
- `Infrastructure/Configuration/` フォルダに以下が存在:
  - `DpapiEncryptor.cs`
  - `SecureConfigService.cs`
  - `ISecureConfigService.cs`
  - `AppConfigModel.cs`

**追加するファイル**（社員番号固有）:

```
Presentation/
├── ViewModels/
│   └── EmployeeNumberConfigViewModel.cs  🆕
└── Views/
    ├── EmployeeNumberConfigDialog.xaml    🆕
    └── EmployeeNumberConfigDialog.xaml.cs 🆕
```

**NuGetパッケージ**（未インストールの場合）:

```powershell
Install-Package CommunityToolkit.Mvvm
Install-Package Microsoft.Extensions.DependencyInjection
```

> **Values**: 基礎と型 / 成長の複利

### Step 2 — ViewModelの作成

バリデーション、保存、リセット機能を持つ社員番号入力ロジックを実装するときに使用します。

フォーマット検証、オープン時の読み込み、保存、リセット機能を持つ`EmployeeNumberConfigViewModel`を作成します。ViewModelはすべての永続化を`ISecureConfigService`に委譲します。

**EmployeeNumberConfigViewModel.cs**:

```csharp
public partial class EmployeeNumberConfigViewModel : ObservableObject
{
    private readonly ISecureConfigService _configService;

    [ObservableProperty] private string employeeNumber = string.Empty;
    [ObservableProperty] private string statusMessage = string.Empty;

    public EmployeeNumberConfigViewModel(ISecureConfigService configService)
        => _configService = configService;

    public async Task LoadConfigAsync()
    {
        var config = await _configService.LoadDifyConfigAsync();
        EmployeeNumber = config.EmployeeNumber;
        StatusMessage = "Settings loaded.";
    }

    [RelayCommand]
    private async Task SaveAsync()
    {
        // ✅ Validate format before persisting
        if (!IsValidEmployeeNumber(EmployeeNumber))
        { StatusMessage = "Enter a 4-digit employee number."; return; }

        var config = await _configService.LoadDifyConfigAsync();
        config.EmployeeNumber = EmployeeNumber.Trim();
        await _configService.SaveDifyConfigAsync(config);
        StatusMessage = "Saved.";
    }

    [RelayCommand]
    private async Task ResetAsync()
    {
        var config = await _configService.LoadDifyConfigAsync();
        config.EmployeeNumber = string.Empty;
        await _configService.SaveDifyConfigAsync(config);
        EmployeeNumber = string.Empty;
        StatusMessage = "Reset complete.";
    }

    /// <summary>
    /// Validates employee number format: exactly 4 digits.
    /// </summary>
    private static bool IsValidEmployeeNumber(string number)
        => !string.IsNullOrWhiteSpace(number)
        && number.Trim().Length == 4
        && number.Trim().All(char.IsDigit);
}
```

**ViewModelでバリデーションを行う理由**: Viewをロジックフリーに保ち、実行中のWPFウィンドウなしでバリデーションをテスト可能にします。`IsValidEmployeeNumber`メソッドは`static`なので単体テストで分離テストできます。

> **Values**: 基礎と型 / ニュートラル

### Step 3 — XAMLダイアログの作成

社員番号入力用のWPFウィンドウを構築するときに使用します。

入力フィールド、ステータスメッセージ、アクションボタンを持つコンパクトなモーダルダイアログを作成します。すべてのコントロールはViewModelプロパティにバインド — `x:Name`操作は不要です。

**EmployeeNumberConfigDialog.xaml**:

```xml
<Window Title="Employee Number Settings"
        Height="260" Width="420"
        WindowStartupLocation="CenterOwner"
        ResizeMode="NoResize"
        Loaded="Window_Loaded">
    <Grid Margin="20">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <!-- Header -->
        <TextBlock Text="Employee Number"
                   FontSize="16" FontWeight="Bold"/>

        <!-- Input -->
        <StackPanel Grid.Row="1" Margin="0,10,0,0">
            <TextBlock Text="Employee Number *"/>
            <TextBox Text="{Binding EmployeeNumber, UpdateSourceTrigger=PropertyChanged}"
                     Margin="0,4,0,0"/>
            <TextBlock Text="Enter 4-digit number"
                       Foreground="Gray" FontSize="10" Margin="0,2,0,0"/>
        </StackPanel>

        <!-- Status -->
        <TextBlock Grid.Row="2"
                   Text="{Binding StatusMessage}"
                   Foreground="Blue"
                   VerticalAlignment="Bottom" Margin="0,0,0,8"/>

        <!-- Actions -->
        <StackPanel Grid.Row="3" Orientation="Horizontal"
                    HorizontalAlignment="Right">
            <Button Content="Save"
                    Command="{Binding SaveCommand}"
                    Margin="0,0,8,0" Padding="16,4"/>
            <Button Content="Reset"
                    Command="{Binding ResetCommand}"
                    Margin="0,0,8,0" Padding="16,4"/>
            <Button Content="Close"
                    Click="Close_Click"
                    Padding="16,4"/>
        </StackPanel>
    </Grid>
</Window>
```

**`UpdateSourceTrigger=PropertyChanged`を使う理由**: これがないと、WPFはフォーカス喪失時のみバインディングを更新します。リアルタイムバリデーションにはViewModelへの文字単位の更新が必要です。

> **Values**: 基礎と型 / 成長の複利

### Step 4 — code-behindの配線

最小限のcode-behindでダイアログウィンドウをViewModelに接続するときに使用します。

code-behindは2つのことだけを処理します：`Window_Loaded`での設定読み込みとウィンドウのクローズ。すべてのビジネスロジックはViewModelに残ります。

**EmployeeNumberConfigDialog.xaml.cs**:

```csharp
public partial class EmployeeNumberConfigDialog : Window
{
    public EmployeeNumberConfigDialog(EmployeeNumberConfigViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }

    private async void Window_Loaded(object sender, RoutedEventArgs e)
        => await ((EmployeeNumberConfigViewModel)DataContext).LoadConfigAsync();

    private void Close_Click(object sender, RoutedEventArgs e)
        => Close();
}
```

**`Window_Loaded`で設定を読み込む理由**: コンストラクタでの読み込みはUIスレッドをブロックし、ウィンドウ描画を遅延させます。`Window_Loaded`はウィンドウ表示後に発火するため、視覚的な遅延なく非同期読み込みが可能です。

> **Values**: 基礎と型 / 継続は力

### Step 5 — メニューバーとの統合

MainWindowから社員番号ダイアログを起動するメニュー項目を追加するときに使用します。

ViewModelをDIに登録し、メニューコマンドからダイアログを起動します。

**App.xaml.cs** — DI登録の追加:

```csharp
// App.xaml.cs — add to OnStartup
services.AddTransient<EmployeeNumberConfigViewModel>();
```

**MainWindowメニュー** — メニュー項目の追加:

```xml
<MenuItem Header="Settings">
    <MenuItem Header="Employee Number..."
              Command="{Binding OpenEmployeeNumberConfigCommand}"/>
</MenuItem>
```

**MainViewModel** — 起動コマンドの追加:

```csharp
[RelayCommand]
private void OpenEmployeeNumberConfig()
{
    var vm = _serviceProvider.GetRequiredService<EmployeeNumberConfigViewModel>();
    new EmployeeNumberConfigDialog(vm) { Owner = Application.Current.MainWindow }
        .ShowDialog();
}
```

> **Values**: 成長の複利 / 継続は力

### Step 6 — アプリケーション固有のカスタマイズ

組織の要件に合わせて社員番号フォーマットを調整するときに使用します。

⚠️ **ユーザーに確認** — 社員IDフォーマットに使用する桁数とバリデーションルールを確認してください。

組織の要件に基づいてこれらのデフォルトを置き換えてください：

| 項目 | ファイル | デフォルト | 変更内容 |
|------|---------|-----------|---------|
| 桁数 | `IsValidEmployeeNumber` | 4桁 | フォーマットに合わせて`Length == 4`を調整 |
| バリデーションルール | `IsValidEmployeeNumber` | 数字のみ | 必要に応じてプレフィックス/サフィックスルールを追加 |
| 保存場所 | `DifyConfigModel` | `EmployeeNumber`プロパティ | 必要に応じてプロパティ名を変更 |
| フィールドラベル | `Dialog.xaml` | "Employee Number" | ローカライズまたはリネーム |
| ウィンドウタイトル | `Dialog.xaml` | "Employee Number Settings" | アプリの命名規則に合わせる |

**カスタマイズ例**:

```csharp
// 6-digit employee number
private static bool IsValidEmployeeNumber(string number)
    => !string.IsNullOrWhiteSpace(number)
    && number.Trim().Length == 6
    && number.Trim().All(char.IsDigit);

// Alphanumeric with prefix (e.g., "EMP-1234")
private static bool IsValidEmployeeNumber(string number)
    => !string.IsNullOrWhiteSpace(number)
    && Regex.IsMatch(number.Trim(), @"^EMP-\d{4}$");
```

> **Values**: ニュートラル / 基礎と型

---

## Good Practices

### 1. 保存前にフォーマットを検証

**What**: `SaveDifyConfigAsync`呼び出し前に、ViewModelで桁数と文字種をチェックします。

**Why**: 無効なデータが設定ファイルに到達するのを防ぎ、ユーザーに即座にフィードバックを提供します。

**Values**: 基礎と型（バリデーションを型として定着）

### 2. ダイアログオープン時に既存値を読み込み

**What**: `Window_Loaded`で`LoadConfigAsync()`を呼び出し、保存済みの値でTextBoxを表示します。

**Why**: ユーザーが現在の設定を確認・更新できます。空フィールドによる混乱を回避します。

**Values**: 継続は力（既存設定の継続性を保つ）

### 3. リセット機能の提供

**What**: `SecureConfigService`経由で保存値をクリアするリセットボタンを含めます。

**Why**: ユーザーが設定ファイルを手動編集せずに社員番号を削除できます。

**Values**: ニュートラル（安全なリセット手段を標準提供）

---

## Common Pitfalls

### 1. Window_Loadedで設定を読み込まない

**Problem**: 値が既に保存されているにもかかわらず、ダイアログが空のTextBoxで開きます。

**Solution**: コンストラクタではなく、必ず`Window_Loaded`イベントで`LoadConfigAsync()`を呼び出します。

```csharp
// ❌ WRONG — Blocks UI thread, may miss async completion
public EmployeeNumberConfigDialog(EmployeeNumberConfigViewModel vm)
{
    InitializeComponent();
    DataContext = vm;
    vm.LoadConfigAsync().Wait(); // Deadlock risk
}

// ✅ CORRECT — Async load after window renders
private async void Window_Loaded(object sender, RoutedEventArgs e)
    => await ((EmployeeNumberConfigViewModel)DataContext).LoadConfigAsync();
```

### 2. UpdateSourceTrigger=PropertyChangedの未設定

**Problem**: バリデーションがキーストロークごとではなく、TextBoxのフォーカス喪失時にのみトリガーされます。

**Solution**: `TextBox`バインディングに`UpdateSourceTrigger=PropertyChanged`を設定します。

```xml
<!-- ❌ WRONG — Updates only on LostFocus -->
<TextBox Text="{Binding EmployeeNumber}"/>

<!-- ✅ CORRECT — Updates on every keystroke -->
<TextBox Text="{Binding EmployeeNumber, UpdateSourceTrigger=PropertyChanged}"/>
```

### 3. SecureConfigService経由の永続化を忘れる

**Problem**: ViewModelプロパティを更新したが、`config.json`に保存していない。

**Solution**: 設定モデル変更後は必ず`SaveDifyConfigAsync()`を呼び出します。

```csharp
// ❌ WRONG — Property updated but not persisted
EmployeeNumber = "1234";

// ✅ CORRECT — Persist through SecureConfigService
var config = await _configService.LoadDifyConfigAsync();
config.EmployeeNumber = EmployeeNumber.Trim();
await _configService.SaveDifyConfigAsync(config);
```

---

## Anti-Patterns

### 社員番号を平文設定ファイルに保存

**What**: 社員番号を`appsettings.json`やカスタム`.txt`ファイルに書き込む。

**Why It's Wrong**: 平文ファイルはファイルシステムにアクセスできる誰でも読み取り可能。保存時の暗号化がない。

**Better Approach**: `SecureConfigService`とDPAPI暗号化を使用して`%LOCALAPPDATA%`に保存。

### code-behindに保存ロジックを記述

**What**: 保存/バリデーション/リセットロジックを`.xaml.cs`のイベントハンドラに直接記述。

**Why It's Wrong**: 実行中のWPFウィンドウなしではテスト不可能。MVVM分離に違反。ロジックがファイル間に散在。

**Better Approach**: `[RelayCommand]`とデータバインディングですべてのロジックをViewModelに委譲。code-behindは`Window_Loaded`と`Close_Click`のみを処理。

---

## Quick Reference

### 実装チェックリスト

- [ ] `dotnet-wpf-secure-config` スキル適用済み（前提条件）
- [ ] `AppConfigModel`に`EmployeeNumber`フィールドあり（`DifyConfigModel`または専用モデル経由）
- [ ] `EmployeeNumberConfigViewModel.cs`を作成（Load / Save / Reset）（Step 2）
- [ ] `EmployeeNumberConfigDialog.xaml`をバインドされたコントロールで作成（Step 3）
- [ ] `EmployeeNumberConfigDialog.xaml.cs`を最小限のcode-behindで作成（Step 4）
- [ ] DIコンテナにViewModelを登録（Step 5）
- [ ] ダイアログ起動用メニュー項目を追加（Step 5）
- [ ] 桁数とバリデーションをフォーマットに合わせてカスタマイズ（Step 6）
- [ ] テスト: 保存 → 閉じる → 再オープン → 値が読み込まれることを確認
- [ ] テスト: 無効な入力 → エラーメッセージが表示されることを確認
- [ ] テスト: リセット → UIと設定ファイルの両方で値がクリアされることを確認

### バリデーション判定表

| フォーマット | バリデーションルール | 例 |
|------------|-------------------|-----|
| 4桁数値 | `Length == 4 && All(IsDigit)` | `1234` |
| 6桁数値 | `Length == 6 && All(IsDigit)` | `001234` |
| 英数字プレフィックス | `Regex(@"^EMP-\d{4}$")` | `EMP-1234` |
| フリーフォーム | `!IsNullOrWhiteSpace` | 任意の非空文字列 |

---

## Resources

- `dotnet-wpf-secure-config` — このスキルが使用するDPAPI暗号化基盤
- `dotnet-wpf-dify-api-integration` — Dify APIの`user`フィールドに社員番号を使用
- [CommunityToolkit.Mvvm ドキュメント](https://learn.microsoft.com/ja-jp/dotnet/communitytoolkit/mvvm/)
- [Microsoft: Data Protection API (DPAPI)](https://docs.microsoft.com/windows/win32/seccng/data-protection-api)

---

## Changelog

### バージョン 1.0.0 (2026-02-15)
- 初回リリース: 社員番号入力ダイアログスキル
- 6ステップワークフロー: 前提条件 → ViewModel → XAML → code-behind → メニュー → カスタマイズ
- SecureConfigServiceによるDPAPI暗号化保存
- カスタマイズガイダンス付き4桁バリデーション
- CommunityToolkit.MvvmによるMVVMパターン

<!-- 英語版は ../SKILL.md を参照してください -->
