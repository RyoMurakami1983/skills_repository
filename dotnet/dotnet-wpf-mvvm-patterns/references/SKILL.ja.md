---
name: dotnet-wpf-mvvm-patterns
description: >
  CommunityToolkit.Mvvmを使ったWPFアプリケーションのMVVM分離、コマンド、バリデーション、
  ダイアログパターンを実装する。
  Use when 新しいWPFビューを実装するとき、またはコードビハインドをViewModel-firstアーキテクチャにリファクタリングするとき。
metadata:
  author: RyoMurakami1983
  tags: [wpf, mvvm, csharp, communitytoolkit, xaml, dotnet]
  invocable: false
---

# WPF MVVMパターン

CommunityToolkit.Mvvmを使ったクリーンなMVVMアーキテクチャでWPFアプリケーションを構築するワークフロー。すべてのWPFモジュールに必要な基本パターン（Observable Property、コマンド、バリデーション、ViewModel構成）をカバーします。

## When to Use This Skill

以下の場合に使用：
- 新しいWPFビューをViewModel-firstアーキテクチャで作成するとき
- コードビハインドのロジックを適切なMVVM分離にリファクタリングするとき
- CanExecute制御付きの非同期コマンドを実装するとき
- WPFフォームにフィールドレベルバリデーションを追加するとき
- 親子ViewModel階層を構成するとき
- MVVM準拠のダイアログ戻り値パターンが必要なとき

以下では使わない：
- コンソールやWeb APIアプリケーション（XAMLなし）
- BlazorやMAUI（異なるUIフレームワーク）
- ユーザー操作のない純粋な静的ビュー

## Related Skills

- **`dotnet-wpf-secure-config`** — このスキルのMVVMパターンを使った設定ダイアログ
- **`dotnet-wpf-employee-input`** — バリデーションパターンを適用した単一フィールドダイアログ
- **`dotnet-wpf-dify-api-integration`** — 非同期コマンドを使ったAPIクライアント
- **`dotnet-oracle-wpf-integration`** — MVVM設定UIを使ったRepositoryパターン

---

## Dependencies

- .NET 8+（または .NET 9）
- CommunityToolkit.Mvvm 8.x (`dotnet add package CommunityToolkit.Mvvm`)
- Microsoft.Extensions.DependencyInjection（DI登録用）

---

## Core Principles

1. **ViewModelが全状態を所有** — Viewはプロパティにバインド。コードビハインドにビジネスロジックなし（基礎と型）
2. **コマンドがイベントハンドラを置換** — すべてのボタンクリックは`[RelayCommand]`、`Click="Button_Click"`は使わない（基礎と型）
3. **バリデーションは宣言的** — `ObservableValidator`とデータアノテーションを使う。アドホックな文字列チェックではない（ニュートラルな視点）
4. **継承より構成** — 小さく焦点の定まったViewModelで複雑な画面を構築（成長の複利）
5. **デフォルトで非同期** — すべてのI/Oバウンドコマンドは`async Task`メソッドに`[RelayCommand]`（継続は力）

---

## Workflow: WPFモジュールにMVVMを実装する

### Step 1: ViewModelベースの設定

CommunityToolkit.Mvvmソースジェネレータを使ってViewModelクラスを作成。これが後続ステップすべての基盤。

新しいWPFビューを開始するとき、または既存のコードビハインドをMVVMに変換するときに使用。

> **Values**: 基礎と型 — `[ObservableProperty]`と`[RelayCommand]`属性がボイラープレートを排除し、正しいパターンを強制する。

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace MyApp.ViewModels;

public partial class CustomerViewModel : ObservableObject
{
    [ObservableProperty]
    private string _name = string.Empty;

    [ObservableProperty]
    private string _email = string.Empty;

    // 生成: public string Name { get; set; } with PropertyChanged
    // 生成: public string Email { get; set; } with PropertyChanged

    // プロパティ変更に反応
    partial void OnNameChanged(string value)
    {
        // Name設定後に実行 — 依存状態の更新はここで
        SaveCommand.NotifyCanExecuteChanged();
    }
}
```

**重要ルール：**
- `ObservableObject`（バリデーションなし）または `ObservableValidator`（バリデーションあり）を継承
- `[ObservableProperty]`はprivateフィールドに付与 — ジェネレータがpublicプロパティを生成
- フィールド命名: `_camelCase` → `PascalCase`プロパティを生成
- 副作用には`partial void OnXxxChanged()`を使用。手動の`PropertyChanged`呼び出しは不要

### Step 2: コマンドの追加

すべてのイベントハンドラをコマンドに置換。同期コマンドは`[RelayCommand]`、非同期コマンドは`async Task`メソッドに`[RelayCommand]`。

ビューにボタン、メニュー項目、またはユーザートリガーアクションがある場合に使用。

> **Values**: 温故知新 — ICommandパターンはWPF誕生以来のMVVMの根幹。CommunityToolkitが原理を保ちつつ実装を近代化する。

```csharp
public partial class CustomerViewModel : ObservableObject
{
    [ObservableProperty]
    private string _name = string.Empty;

    [ObservableProperty]
    private bool _isBusy;

    // CanExecute付き同期コマンド
    [RelayCommand(CanExecute = nameof(CanSave))]
    private void Save()
    {
        // 保存ロジック
    }

    private bool CanSave() => !string.IsNullOrWhiteSpace(Name);

    // 非同期コマンド — IsBusy的な動作を自動処理
    [RelayCommand]
    private async Task LoadDataAsync(CancellationToken token)
    {
        IsBusy = true;
        try
        {
            // 非同期I/O
            await Task.Delay(1000, token);
        }
        finally
        {
            IsBusy = false;
        }
    }
}
```

**XAMLバインディング：**

```xml
<Button Content="保存"
        Command="{Binding SaveCommand}" />

<Button Content="読込"
        Command="{Binding LoadDataCommand}" />

<!-- 読込中スピナー表示 -->
<ProgressBar IsIndeterminate="True"
             Visibility="{Binding IsBusy, Converter={StaticResource BoolToVisibility}}" />
```

**重要ルール：**
- `private void Xxx()` に `[RelayCommand]` → `XxxCommand` を生成
- `private async Task XxxAsync()` に `[RelayCommand]` → `XxxCommand` を生成（Asyncサフィックスは除去）
- `CanExecute`は`bool`を返すメソッドを参照 — 条件変更時に`XxxCommand.NotifyCanExecuteChanged()`を呼ぶ
- 非同期コマンドは実行中の二重実行を自動的に防止

### Step 3: バリデーションの追加

`ObservableValidator`とデータアノテーションでフィールドレベルバリデーション。WPFの`INotifyDataErrorInfo`と統合。

ビューに保存前バリデーションが必要な入力フィールドがある場合に使用。

> **Values**: ニュートラルな視点 — 宣言的バリデーションルールは客観的でテスト可能。コードビハインドの主観的アドホックチェックを排除する。

```csharp
using System.ComponentModel.DataAnnotations;

public partial class CustomerViewModel : ObservableValidator
{
    [ObservableProperty]
    [NotifyDataErrorInfo]
    [Required(ErrorMessage = "名前は必須です。")]
    [MinLength(2, ErrorMessage = "名前は2文字以上必要です。")]
    private string _name = string.Empty;

    [ObservableProperty]
    [NotifyDataErrorInfo]
    [EmailAddress(ErrorMessage = "メールアドレスの形式が不正です。")]
    private string _email = string.Empty;

    [RelayCommand(CanExecute = nameof(CanSave))]
    private void Save()
    {
        ValidateAllProperties();
        if (HasErrors) return;

        // 保存処理
    }

    private bool CanSave() => !HasErrors && !string.IsNullOrWhiteSpace(Name);
}
```

**バリデーション表示XAML：**

```xml
<TextBox x:Name="NameTextBox"
         Text="{Binding Name, UpdateSourceTrigger=PropertyChanged,
                ValidatesOnDataErrors=True}" />

<!-- バリデーションエラー表示 -->
<TextBlock Text="{Binding (Validation.Errors)[0].ErrorContent,
                  ElementName=NameTextBox}"
           Foreground="Red"
           Visibility="{Binding (Validation.HasError),
                        ElementName=NameTextBox,
                        Converter={StaticResource BoolToVisibility}}" />
```

**重要ルール：**
- `ObservableObject`の代わりに`ObservableValidator`を継承
- バリデーション対象フィールドには`[NotifyDataErrorInfo]`を`[ObservableProperty]`と併用
- 保存操作前に`ValidateAllProperties()`を呼ぶ
- `CanExecute`メソッドで`HasErrors`をチェック

### Step 4: Dependency Injectionへの登録

DIコンテナにViewModelとViewを登録。サービスにはコンストラクタインジェクションを使用。

アプリケーションが`Microsoft.Extensions.DependencyInjection`を使用する場合に使用（すべての非自明アプリで推奨）。

> **Values**: 成長の複利 — DIはテスト可能なViewModelと実装の差し替えを実現。この投資はアプリケーションライフサイクル全体で配当を生む。

```csharp
// App.xaml.cs
public partial class App : Application
{
    private readonly IServiceProvider _serviceProvider;

    public App()
    {
        var services = new ServiceCollection();

        // サービス登録
        services.AddSingleton<ICustomerRepository, CustomerRepository>();
        services.AddSingleton<IDialogService, DialogService>();

        // ViewModel登録
        services.AddTransient<CustomerViewModel>();
        services.AddTransient<MainViewModel>();

        // View登録
        services.AddTransient<MainWindow>();

        _serviceProvider = services.BuildServiceProvider();
    }

    protected override void OnStartup(StartupEventArgs e)
    {
        var mainWindow = _serviceProvider.GetRequiredService<MainWindow>();
        mainWindow.Show();
    }
}
```

```csharp
// 依存関係がインジェクトされたViewModel
public partial class CustomerViewModel : ObservableObject
{
    private readonly ICustomerRepository _repository;

    public CustomerViewModel(ICustomerRepository repository)
    {
        _repository = repository;
    }

    [RelayCommand]
    private async Task LoadAsync(CancellationToken token)
    {
        var customers = await _repository.GetAllAsync(token);
        // ...
    }
}
```

**重要ルール：**
- ViewModelは`Transient`（共有状態が必要でない限り毎回新規インスタンス）
- サービス（リポジトリ、APIクライアント）は`Singleton`または`Scoped`
- Viewはコンストラクタ経由でViewModelを受け取る: `public MainWindow(MainViewModel vm) { DataContext = vm; }`
- `ServiceLocator`パターンは使わない — 常にコンストラクタインジェクション

### Step 5: 親子ViewModelの構成

ViewModelを構成して複雑な画面を構築。親が子コレクションを所有し、子はイベントまたはMessengerで上方向に通信。

ビューにサブビュー（タブ、詳細パネル付きリスト、マスター/詳細レイアウト）が含まれる場合に使用。

> **Values**: 余白の設計 — 小さく焦点の定まったViewModelが変化の余地を残す。モノリシックなViewModelは硬直する。構成されたものは適応する。

```csharp
public partial class MainViewModel : ObservableObject
{
    [ObservableProperty]
    private ObservableCollection<CustomerViewModel> _customers = [];

    [ObservableProperty]
    private CustomerViewModel? _selectedCustomer;

    [RelayCommand]
    private void AddCustomer()
    {
        var newCustomer = new CustomerViewModel { Name = "新規顧客" };
        Customers.Add(newCustomer);
        SelectedCustomer = newCustomer;
    }

    [RelayCommand]
    private void RemoveCustomer()
    {
        if (SelectedCustomer is null) return;
        Customers.Remove(SelectedCustomer);
        SelectedCustomer = Customers.FirstOrDefault();
    }
}
```

**マスター/詳細XAML：**

```xml
<Grid>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="250" />
        <ColumnDefinition Width="*" />
    </Grid.ColumnDefinitions>

    <!-- マスターリスト -->
    <ListBox Grid.Column="0"
             ItemsSource="{Binding Customers}"
             SelectedItem="{Binding SelectedCustomer}"
             DisplayMemberPath="Name" />

    <!-- 詳細パネル -->
    <ContentControl Grid.Column="1"
                    Content="{Binding SelectedCustomer}" />
</Grid>
```

**重要ルール：**
- 親ViewModelは子コレクションを`ObservableCollection<T>`で所有
- `SelectedItem`バインディングには`[ObservableProperty]`を使用
- ViewModel間通信には直接参照より`WeakReferenceMessenger`を推奨
- 子ViewModelは自己完結的に — 親を参照しない

---

## Best Practices

- 新しいビューはXAMLを書く前にStep 1（ViewModelベース）から始める
- `[ObservableProperty]`を排他的に使用 — 手動の`OnPropertyChanged`呼び出しは書かない
- ViewModelは200行以下に保つ。複雑なロジックはサービスに抽出
- XAMLなしでViewModelをテスト — コマンド呼び出しとプロパティ変更のアサート
- すべての非同期コマンドで`CancellationToken`を使用して適切なキャンセルサポート

## Common Pitfalls

1. **コードビハインドにビジネスロジック**
   - ❌ `private void Button_Click(object sender, RoutedEventArgs e) { SaveToDatabase(); }`
   - ✅ `[RelayCommand] private async Task SaveAsync() { await _repo.SaveAsync(); }`
   - Why: コードビハインドはユニットテストできない。ViewModelはできる。

2. **`NotifyCanExecuteChanged()`の呼び忘れ**
   - ❌ `Name`を変更してもSaveボタンが無効のまま
   - ✅ `partial void OnNameChanged(string value) { SaveCommand.NotifyCanExecuteChanged(); }`
   - Why: WPFはプロパティ変更時にCanExecuteを自動再評価しない。

3. **バリデーションが必要なのに`ObservableObject`を使用**
   - ❌ `public partial class FormVm : ObservableObject` + 手動エラー文字列
   - ✅ `public partial class FormVm : ObservableValidator` + `[NotifyDataErrorInfo]`
   - Why: `ObservableValidator`はWPF組み込みのバリデーション表示パイプラインと統合される。

4. **ソースジェネレータと手動`PropertyChanged`の混在**
   - ❌ `[ObservableProperty]`と`OnPropertyChanged("Name");`の併用
   - ✅ 手動呼び出しを削除 — ジェネレータが処理する
   - Why: 二重発火は冗長なUI更新と微妙なバグを引き起こす。

5. **500行超のモノリシックViewModel**
   - ❌ すべてのプロパティ、コマンド、子ロジックが1つのViewModel
   - ✅ 親ViewModelが子ViewModelを構成（Step 5）
   - Why: 大きなViewModelは変更に抵抗し、テストを困難にする。

## Anti-Patterns

- **ViewModel内のServiceLocator** — `App.Current.Services.GetService<T>()`ではなくコンストラクタインジェクションを使う
- **すべてにTwo-wayバインディング** — ユーザー入力フィールドのみ`TwoWay`、表示専用は`OneWay`（デフォルト）
- **ViewModelにView参照を渡す** — ViewModelは`Window`、`UserControl`、いかなるXAML型も知ってはならない
- **God ViewModel** — 単純な画面では1View=1ViewModelで良いが、複雑な画面には構成（Step 5）が必要

---

## Quick Reference

### CommunityToolkit.Mvvm チートシート

| パターン | 属性/クラス | 生成されるもの |
|---------|------------|--------------|
| Observable property | `[ObservableProperty]` on `private string _name` | `public string Name { get; set; }` + `PropertyChanged` |
| プロパティ変更フック | `partial void OnNameChanged(string value)` | Nameセッター後に呼ばれる |
| 同期コマンド | `[RelayCommand]` on `private void Save()` | `public IRelayCommand SaveCommand` |
| 非同期コマンド | `[RelayCommand]` on `private async Task LoadAsync()` | `public IAsyncRelayCommand LoadCommand` |
| CanExecute | `[RelayCommand(CanExecute = nameof(CanSave))]` | ゲート付きコマンド |
| バリデーション | `[NotifyDataErrorInfo]` + `[Required]` | `INotifyDataErrorInfo`実装 |
| ベース（バリデーションなし） | `ObservableObject` | — |
| ベース（バリデーションあり） | `ObservableValidator` | — |

### Decision Table

| 状況 | パターン | ステップ |
|------|---------|---------|
| 入力フィールドのある新規ビュー | ObservableValidator + commands | Steps 1-3 |
| 表示専用ビュー | ObservableObject + load command | Steps 1-2 |
| サブビュー/タブのあるビュー | 親子構成 | Step 5 |
| 外部サービスが必要なビュー | DI登録 | Step 4 |
| コードビハインドの変換 | ViewModelへ抽出 | Steps 1-2 |

---

## FAQ

**Q: `ObservableObject`と`ObservableValidator`、どちらを使うべき？**
A: ユーザー入力のバリデーションが必要なビューは`ObservableValidator`。表示専用やコマンドのみのViewModelは`ObservableObject`。

**Q: ViewModelからダイアログを表示するには？**
A: `IDialogService`インターフェースをインジェクト。実装（View層）が`Window.ShowDialog()`を処理。ViewModelは`_dialogService.ShowConfirmation("message")`を呼び、`bool`結果を受け取る。

**Q: `Messenger`と直接イベント、どちらを使うべき？**
A: 直接の親子関係がないViewModel間通信には`WeakReferenceMessenger`。親子関係がある場合は直接プロパティバインディングがシンプル。

**Q: ViewModelからウィンドウを閉じるには？**
A: `ICloseable`インターフェースまたは`WeakReferenceMessenger.Send(new CloseWindowMessage())`を使用。Viewはコードビハインドで1行のハンドラを登録。
