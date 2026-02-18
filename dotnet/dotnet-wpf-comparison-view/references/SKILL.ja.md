---
name: dotnet-wpf-comparison-view
description: WPFでサイドバイサイド比較ビューを構築。不一致ハイライトとチェックボックス検証付きのマッチング結果表示。
author: RyoMurakami1983
tags: [dotnet, wpf, csharp, mvvm, comparison-view, matching, community-toolkit]
invocable: false
version: 1.0.0
---

# WPFでサイドバイサイド比較ビューを構築

マッチング結果をサイドバイサイドで表示する比較ビュー構築のエンドツーエンドワークフロー：スコア追跡付き比較項目ViewModel、3カラムXAMLレイアウト（フィールド名 / ソースA / ソースB）、背景色による不一致ハイライト、ライブスコア再計算付き編集可能フィールド、エクスポート前のチェックボックスベースのユーザー検証。

## このスキルを使うタイミング

以下の場合にこのスキルを使用してください：
- 2つのデータソースからのマッチング結果をサイドバイサイド比較UIで表示するとき
- ユーザーが各マッチングフィールドを確認・承認する検証ワークフローを構築するとき
- 不一致フィールドを色分け背景でハイライトするとき（ピンク＝不一致、グリーン＝検証済み）
- ライブスコア再計算をトリガーする編集可能フィールドを実装するとき
- すべての項目のチェックとスコア閾値超過を必須とするエクスポートゲートを作成するとき

**前提条件**:
- `CommunityToolkit.Mvvm`がインストール済みのWPFアプリケーション
- マッチングサービスからのマッチング結果（例：`dotnet-generic-matching`）
- ObservableObjectベースのViewModelを使用するMVVMアーキテクチャ

---

## 関連スキル

- **`dotnet-generic-matching`** — このビューで表示するマッチング結果を提供
- **`dotnet-wpf-pdf-preview`** — 比較ビューと並べて表示するPDFプレビューパネル
- **`dotnet-oracle-wpf-integration`** — OracleからソースA候補データを読み込み
- **`dotnet-wpf-dify-api-integration`** — AI OCR経由でソースBデータを抽出
- **`git-commit-practices`** — 各ステップをアトミックな変更としてコミット

---

## コア原則

1. **MVVMバインディングのみ** — すべてのUI更新はデータバインディング経由；`x:Name`でのコントロール操作は禁止（基礎と型）
2. **視覚フィードバック優先** — 背景色（#F8D7DA ピンク、#BBF7D0 グリーン）で不一致/検証済みステータスを即座に表示（ニュートラル）
3. **ライブ再計算** — 編集可能フィールドの変更時にスコアを即座に更新（継続は力）
4. **ゲート付きエクスポート** — すべてのチェックボックスがチェック済み ＋ すべてのスコアが閾値以上でエクスポート許可（基礎と型）
5. **関心の分離** — 比較ロジックはViewModelに配置；Viewはバインディングの描画のみ（成長の複利）

---

## ワークフロー: 比較ビューの構築

### Step 1 — 比較項目ViewModelの作成

スコア、ソースフィールド、背景色、チェックボックスを持つ単一の比較行を表すViewModelを定義するときに使用します。

`ObservableObject`を継承した`ComparisonItemViewModel`を作成します。各インスタンスは1つのマッチングペアを保持：ソースAフィールド（例：データベースレコード）、ソースBフィールド（例：OCR抽出データ）、不一致ハイライト用の背景色、ユーザー検証用のチェックボックスプロパティ。

```
YourApp/
├── ViewModels/
│   ├── ComparisonItemViewModel.cs   # 🆕 Single comparison row
│   └── ComparisonTabViewModel.cs    # 🆕 Parent with ObservableCollection
└── Views/
    └── ComparisonView.xaml          # 🆕 3-column layout
```

**ComparisonItemViewModel.cs** — コア構造：

```csharp
using CommunityToolkit.Mvvm.ComponentModel;

namespace YourApp.ViewModels
{
    public partial class ComparisonItemViewModel : ObservableObject
    {
        // === Score ===
        [ObservableProperty] private int index;
        [ObservableProperty] private double scorePercent;
        [ObservableProperty] private bool isSuccessful;
        [ObservableProperty] private string scoreColor = "Black";

        // === Source A fields (read-only, e.g., database record) ===
        [ObservableProperty] private string sourceAField1 = "";
        [ObservableProperty] private string sourceAField2 = "";
        [ObservableProperty] private string sourceAField3 = "";

        // === Source B fields (e.g., OCR-extracted data) ===
        [ObservableProperty] private string sourceBField1 = "";
        [ObservableProperty] private string sourceBField2 = "";
        [ObservableProperty] private string sourceBField3 = "";

        // === Background colors for mismatch highlighting ===
        [ObservableProperty] private string sourceBField1Background = "Transparent";
        [ObservableProperty] private string sourceBField2Background = "Transparent";
        [ObservableProperty] private string sourceBField3Background = "Transparent";

        // === Checkbox verification per field ===
        [ObservableProperty] private bool isField1Checked;
        [ObservableProperty] private bool isField2Checked;
        [ObservableProperty] private bool isField3Checked;

        // === Editable fields (trigger recalculation) ===
        [ObservableProperty] private decimal editableUnitPrice;
        [ObservableProperty] private string editableDeliveryDate = "";
        [ObservableProperty] private bool isModified = false;

        // === Editable field backgrounds ===
        [ObservableProperty] private string editableUnitPriceBackground = "White";

        partial void OnEditableUnitPriceChanged(decimal value)
        {
            IsModified = true;
            UpdateMismatchBackgrounds();
            RecalculateMatchingScore();
        }

        partial void OnIsField1CheckedChanged(bool value)
        {
            UpdateMismatchBackgrounds();
        }

        /// <summary>
        /// Update backgrounds: pink (#F8D7DA) for mismatch, green (#BBF7D0) when checked, Transparent otherwise.
        /// </summary>
        public void UpdateMismatchBackgrounds()
        {
            SourceBField1Background = IsField1Checked ? "#BBF7D0"
                : IsMismatch(SourceAField1, SourceBField1) ? "#F8D7DA"
                : "Transparent";

            SourceBField2Background = IsField2Checked ? "#BBF7D0"
                : IsMismatch(SourceAField2, SourceBField2) ? "#F8D7DA"
                : "Transparent";

            SourceBField3Background = IsField3Checked ? "#BBF7D0"
                : IsMismatch(SourceAField3, SourceBField3) ? "#F8D7DA"
                : "Transparent";
        }

        private static bool IsMismatch(string? a, string? b)
            => (a ?? string.Empty) != (b ?? string.Empty);

        /// <summary>
        /// Count visible fields that have not been checked by the user.
        /// </summary>
        public int GetUncheckedVisibleCount()
        {
            int count = 0;
            if (HasDisplayValue(SourceAField1) && !IsField1Checked) count++;
            if (HasDisplayValue(SourceAField2) && !IsField2Checked) count++;
            if (HasDisplayValue(SourceAField3) && !IsField3Checked) count++;
            return count;
        }

        /// <summary>
        /// Recalculate matching score after editable field changes.
        /// Delegate to domain matching service with updated values.
        /// </summary>
        private void RecalculateMatchingScore()
        {
            // Re-run matching with updated values via domain service
            // ScorePercent = newResult.Score.ScorePercent;
            // IsSuccessful = ScorePercent >= 80.0;
            // ScoreColor = IsSuccessful ? "Green" : "Red";
        }

        public void UpdateScoreColor()
        {
            ScoreColor = IsSuccessful ? "Green" : (ScorePercent >= 60 ? "Orange" : "Red");
        }

        // === Visibility (HasDisplayValue pattern) ===
        public bool IsField1Visible => HasDisplayValue(SourceAField1);
        public bool IsField2Visible => HasDisplayValue(SourceAField2);
        public bool IsField3Visible => HasDisplayValue(SourceAField3);

        private static bool HasDisplayValue(string? value)
        {
            if (string.IsNullOrWhiteSpace(value)) return false;
            return value.Trim() != "-";
        }

        partial void OnSourceAField1Changed(string value)
        {
            OnPropertyChanged(nameof(IsField1Visible));
        }
    }
}
```

**Mercuryの`MatchingResultItemViewModel`からの主要パターン**：
- `partial void OnXxxChanged()`フックによる変更追跡と再計算
- `HasDisplayValue()`で空値/ダッシュ値を表示から除外
- 背景色は文字列バインディングを使用（`"Transparent"`、`"#F8D7DA"`、`"#BBF7D0"`）
- `GetUncheckedVisibleCount()`でエクスポート前にすべての表示フィールドがチェック済みか検証

> **Values**: 基礎と型 / 成長の複利

### Step 2 — 3カラムXAMLレイアウトの構築

フィールド名、ソースA、ソースBの列を持つItemsControlベースの比較ビューを作成するときに使用します。

スクロール可能な`ItemsControl`と、3カラムGridを含む`DataTemplate`を作成します。各マッチング結果はスコアヘッダーとフィールド行を持つボーダー付きカードとして描画されます。

**ComparisonView.xaml** — レイアウトテンプレート：

```xml
<UserControl x:Class="YourApp.Views.ComparisonView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <UserControl.Resources>
        <Style x:Key="FieldNameStyle" TargetType="TextBlock">
            <Setter Property="FontSize" Value="11"/>
            <Setter Property="Padding" Value="5,2"/>
            <Setter Property="Background" Value="#F5F5F5"/>
        </Style>
        <Style x:Key="ValueStyle" TargetType="TextBlock">
            <Setter Property="FontSize" Value="11"/>
            <Setter Property="Padding" Value="5,2"/>
            <Setter Property="TextWrapping" Value="Wrap"/>
        </Style>
    </UserControl.Resources>

    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>

        <TextBlock Grid.Row="0" FontSize="16" FontWeight="Bold"
                   Text="Comparison Results" Margin="0,0,0,10"/>

        <ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto">
            <ItemsControl ItemsSource="{Binding ComparisonItems}">
                <ItemsControl.ItemTemplate>
                    <DataTemplate>
                        <Border BorderBrush="#CCCCCC" BorderThickness="1"
                                Margin="0,0,0,15" Padding="10"
                                Background="#FAFAFA" CornerRadius="5">
                            <StackPanel>
                                <!-- Score Header -->
                                <Grid Margin="0,0,0,10">
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="*"/>
                                        <ColumnDefinition Width="Auto"/>
                                    </Grid.ColumnDefinitions>
                                    <TextBlock Grid.Column="0" FontSize="14" FontWeight="Bold"
                                               Text="{Binding Index, StringFormat='#{0}'}"/>
                                    <StackPanel Grid.Column="1" Orientation="Horizontal">
                                        <TextBlock Text="Score: " FontSize="12"/>
                                        <TextBlock Text="{Binding ScorePercent, StringFormat={}{0:F1}%}"
                                                   FontSize="12" FontWeight="Bold"
                                                   Foreground="{Binding ScoreColor}"/>
                                    </StackPanel>
                                </Grid>

                                <Separator Margin="0,0,0,10"/>

                                <!-- 3-Column Comparison Grid -->
                                <Grid>
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="140"/> <!-- Field Name -->
                                        <ColumnDefinition Width="*"/>   <!-- Source A -->
                                        <ColumnDefinition Width="*"/>   <!-- Source B -->
                                    </Grid.ColumnDefinitions>

                                    <!-- Column Headers -->
                                    <TextBlock Grid.Column="0" Grid.Row="0"
                                               Text="Field" FontWeight="Bold" FontSize="11"/>
                                    <TextBlock Grid.Column="1" Grid.Row="0"
                                               Text="Source A" FontWeight="Bold" FontSize="11"/>
                                    <TextBlock Grid.Column="2" Grid.Row="0"
                                               Text="Source B" FontWeight="Bold" FontSize="11"/>

                                    <!-- Field Row Example -->
                                    <TextBlock Grid.Column="0" Grid.Row="1"
                                               Text="Field 1" Style="{StaticResource FieldNameStyle}"/>
                                    <TextBlock Grid.Column="1" Grid.Row="1"
                                               Text="{Binding SourceAField1}"
                                               Style="{StaticResource ValueStyle}"/>
                                    <TextBlock Grid.Column="2" Grid.Row="1"
                                               Text="{Binding SourceBField1}"
                                               Background="{Binding SourceBField1Background}"
                                               Style="{StaticResource ValueStyle}"/>

                                    <!-- Add Grid.RowDefinitions and more rows per field... -->
                                </Grid>
                            </StackPanel>
                        </Border>
                    </DataTemplate>
                </ItemsControl.ItemTemplate>
            </ItemsControl>
        </ScrollViewer>
    </Grid>
</UserControl>
```

**DataGridではなくItemsControlを使う理由**：DataGridは選択、ソート、編集用のUIクロムを追加し、カスタム比較レイアウトと競合します。`ItemsControl`はアイテムごとの`DataTemplate`を完全に制御できます。

> **Values**: 基礎と型 / ニュートラル

### Step 3 — スコアカラーコンバーターの追加

閾値に基づいてスコア値に色分けスタイルを適用するときに使用します。

スコア色ロジックをViewModel内に実装します（`IValueConverter`としてではなく）。これによりテスト容易性が向上します。ViewModelは`ScoreColor`文字列プロパティを公開し、XAMLが`Foreground`にバインドします。

```csharp
// In ComparisonItemViewModel
public void UpdateScoreColor()
{
    // ✅ Green ≥80%, Orange 60–79%, Red <60%
    ScoreColor = IsSuccessful ? "Green" : (ScorePercent >= 60 ? "Orange" : "Red");
}
```

```xml
<!-- ✅ CORRECT — Bind to ViewModel color property -->
<TextBlock Text="{Binding ScorePercent, StringFormat={}{0:F1}%}"
           Foreground="{Binding ScoreColor}" FontWeight="Bold"/>

<!-- ❌ WRONG — IValueConverter for simple threshold logic -->
<TextBlock Foreground="{Binding ScorePercent, Converter={StaticResource ScoreColorConverter}}"/>
```

**IValueConverterではなくViewModelプロパティを使う理由**：3段階の閾値ロジック（Green/Orange/Red）はドメイン的に意味があります。ViewModelに配置することで、XAMLインフラなしでテスト可能になります。

> **Values**: 基礎と型 / ニュートラル

### Step 4 — 編集可能フィールドの実装

ユーザーが変更可能なTextBoxバインディングを追加し、黄色背景とライブ再計算を実現するときに使用します。

即座のフィードバックのために`TwoWay`バインディングと`UpdateSourceTrigger=PropertyChanged`を使用します。編集可能フィールドは読み取り専用フィールドと視覚的に区別するため、独自の背景色（黄色`#FFFFCC`または白）を持ちます。

```xml
<!-- ✅ Editable field with TwoWay binding and yellow background -->
<TextBox Grid.Column="2" Grid.Row="5"
         Text="{Binding EditableUnitPrice, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged,
                StringFormat={}{0:N0}}"
         Background="{Binding EditableUnitPriceBackground}"
         FontSize="11" Padding="3,1"/>

<!-- ✅ Read-only field (TextBlock, not TextBox) -->
<TextBlock Grid.Column="2" Grid.Row="1"
           Text="{Binding SourceBField1}"
           Background="{Binding SourceBField1Background}"
           Style="{StaticResource ValueStyle}"/>
```

**ViewModelの変更ハンドラー** — 編集時に再計算をトリガー：

```csharp
partial void OnEditableUnitPriceChanged(decimal value)
{
    IsModified = true;
    UpdateMismatchBackgrounds();
    RecalculateMatchingScore();
}
```

**主要ポイント**：
- 金額フィールドには`decimal`を使用（`float`や`double`は使用禁止）
- `UpdateSourceTrigger=PropertyChanged`はキーストロークごとに発火しライブ更新を実現
- `IsModified`フラグで編集可能フィールドの変更を追跡

> **Values**: 継続は力 / 基礎と型

### Step 5 — チェックボックス検証の追加

ユーザーがフィールドを確認したことを示すために、フィールドごとのチェックボックスを追加するときに使用します。

手動検証が必要なフィールドに`CheckBox`列（またはインラインCheckBox）を追加します。チェック時に背景がグリーン（#BBF7D0）に変わります。`GetUncheckedVisibleCount()`メソッドで、エクスポート前にすべての表示フィールドがチェック済みか検証します。

```xml
<!-- Checkbox column (between Source A and Source B, or after Source B) -->
<CheckBox Grid.Column="3" Grid.Row="1"
          IsChecked="{Binding IsField1Checked}"
          VerticalAlignment="Center" HorizontalAlignment="Center"/>
```

**ViewModel — チェックボックスが背景更新をトリガー**：

```csharp
partial void OnIsField1CheckedChanged(bool value)
{
    UpdateMismatchBackgrounds();
}

public void UpdateMismatchBackgrounds()
{
    // Green when checked, pink when mismatched, transparent when matching
    SourceBField1Background = IsField1Checked ? "#BBF7D0"
        : IsMismatch(SourceAField1, SourceBField1) ? "#F8D7DA"
        : "Transparent";
}
```

**色の凡例**：

| 色 | 16進コード | 意味 |
|------|----------|---------|
| 🆕 ピンク | `#F8D7DA` | ソースAとソースBの間で不一致を検出 |
| ✅ グリーン | `#BBF7D0` | ユーザーがフィールドを検証・チェック済み |
| 透明 | `Transparent` | フィールドが一致（対応不要） |

> **Values**: ニュートラル / 基礎と型

### Step 6 — 結果の接続とエクスポート

比較ビューを親ViewModelに接続し、結果を展開し、エクスポートゲートを実装するときに使用します。

`ObservableCollection<ComparisonItemViewModel>`と`SetResults`メソッドを持つ親`ComparisonTabViewModel`を作成します。各アイテムの`PropertyChanged`をサブスクライブしてライブプレビュー更新を実現します。全チェック済み＋全スコア閾値超過でエクスポートをゲートします。

**ComparisonTabViewModel.cs**：

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;

namespace YourApp.ViewModels
{
    public partial class ComparisonTabViewModel : ObservableObject
    {
        public ObservableCollection<ComparisonItemViewModel> ComparisonItems { get; } = new();

        [ObservableProperty]
        private string qualityMessage = string.Empty;

        public event EventHandler<string>? ExportCompleted;

        /// <summary>
        /// Populate from matching results with PropertyChanged subscription.
        /// </summary>
        public void SetResults(IEnumerable<MatchingResultData> results)
        {
            ComparisonItems.Clear();

            int idx = 1;
            foreach (var result in results)
            {
                var item = new ComparisonItemViewModel
                {
                    Index = idx++,
                    ScorePercent = result.ScorePercent,
                    IsSuccessful = result.ScorePercent >= 80.0,
                    SourceAField1 = result.SourceAField1,
                    SourceBField1 = result.SourceBField1,
                    // ... map remaining fields
                };
                item.UpdateScoreColor();
                item.UpdateMismatchBackgrounds();

                // ✅ Subscribe for live preview updates
                item.PropertyChanged += (s, e) => UpdateExportPreview();

                ComparisonItems.Add(item);
            }

            UpdateExportPreview();
        }

        private void UpdateExportPreview()
        {
            int total = ComparisonItems.Count;
            int qualified = ComparisonItems.Count(i => i.IsSuccessful);

            QualityMessage = qualified == total
                ? $"✅ All scores ≥80% ({qualified}/{total}). Export ready."
                : $"⚠ {qualified}/{total} items ≥80%. All must pass before export.";
        }

        [RelayCommand]
        private void Export()
        {
            // Gate 1: All checkboxes must be checked
            var unchecked = ComparisonItems.Sum(i => i.GetUncheckedVisibleCount());
            if (unchecked > 0)
            {
                ExportCompleted?.Invoke(this,
                    $"❌ {unchecked} unchecked items remain. Check all before export.");
                return;
            }

            // Gate 2: All scores must be ≥ threshold
            int total = ComparisonItems.Count;
            int qualified = ComparisonItems.Count(i => i.IsSuccessful);
            if (qualified < total)
            {
                ExportCompleted?.Invoke(this,
                    $"❌ {qualified}/{total} items ≥80%. All must pass.");
                return;
            }

            // Execute export
            // var outputPath = _exportUseCase.Execute(results);
            ExportCompleted?.Invoke(this, $"✅ Exported {total} items.");
        }
    }
}
```

**2つのエクスポートゲートを設ける理由**：ゲート1（チェックボックス）はユーザーがすべてのフィールドを目視確認したことを保証します。ゲート2（スコア閾値）はデータ品質を保証します。両方を通過する必要があります — これはMercuryの`ResultTabViewModel.ExportRpaData`パターンに倣っています。

> **Values**: 基礎と型 / 継続は力

---

## グッドプラクティス

### 1. マッチングフィードバックに背景色を使用

✅ 不一致フィールドに`#F8D7DA`（ピンク）、検証済みフィールドに`#BBF7D0`（グリーン）、一致フィールドに`Transparent`を適用します。背景をViewModelの文字列プロパティにバインドします。

```csharp
// ✅ CORRECT — ViewModel drives background color via binding
SourceBField1Background = IsField1Checked ? "#BBF7D0"
    : IsMismatch(SourceAField1, SourceBField1) ? "#F8D7DA"
    : "Transparent";
```

**Values**: ニュートラル（即座の視覚フィードバック）

### 2. 編集可能フィールドの変更時にスコアを再計算

✅ `partial void OnXxxChanged()`フックを使用して、ユーザーがフィールドを編集した際に即座に`RecalculateMatchingScore()`をトリガーします。これにより、編集がマッチングを改善したかどうかの即座のフィードバックが得られます。

```csharp
partial void OnEditableUnitPriceChanged(decimal value)
{
    IsModified = true;
    UpdateMismatchBackgrounds();
    RecalculateMatchingScore();
}
```

**Values**: 継続は力（リアルタイム再計算）

### 3. エクスポート前にすべてのチェックボックスを検証

✅ `GetUncheckedVisibleCount()`を使用して、すべての表示フィールドが確認済みであることを保証します。`HasDisplayValue`がtrueを返すフィールドのみカウントし、空値やプレースホルダー値はスキップします。

```csharp
var unchecked = ComparisonItems.Sum(i => i.GetUncheckedVisibleCount());
if (unchecked > 0) { /* Block export */ }
```

**Values**: 基礎と型（品質ゲート）

---

## よくある落とし穴

### 1. ライブプレビュー更新のためのPropertyChangedサブスクライブ漏れ

**問題**：ユーザーがフィールドを編集したりチェックボックスをチェックしても、エクスポートプレビューが更新されない。親ViewModelが子アイテムの変更をリッスンしていないことが原因。

**解決策**：`SetResults()`内で各`ComparisonItemViewModel.PropertyChanged`をサブスクライブします。

```csharp
// ❌ WRONG — No subscription, preview is stale
ComparisonItems.Add(item);

// ✅ CORRECT — Subscribe for live updates
item.PropertyChanged += (s, e) => UpdateExportPreview();
ComparisonItems.Add(item);
```

### 2. 背景バインディングの代わりにハードコードされた色を使用

**問題**：XAMLで静的な値で背景色を直接設定。データ変更時に不一致ハイライトが更新されない。

**解決策**：`Background`を`UpdateMismatchBackgrounds()`が動的に更新するViewModelの文字列プロパティにバインドします。

```xml
<!-- ❌ WRONG — Static background, never updates -->
<TextBlock Background="#F8D7DA" Text="{Binding SourceBField1}"/>

<!-- ✅ CORRECT — Dynamic background via binding -->
<TextBlock Background="{Binding SourceBField1Background}" Text="{Binding SourceBField1}"/>
```

### 3. 新規データ読み込み時の状態リセット漏れ

**問題**：ユーザーが新しいデータセットを読み込んだ際に以前のマッチング結果が残り、古いデータで混乱を招く。

**解決策**：`SetResults()`の先頭で`ComparisonItems.Clear()`を呼び出し、すべての品質メッセージをリセットします。

```csharp
public void SetResults(IEnumerable<MatchingResultData> results)
{
    // ✅ Always clear previous state first
    ComparisonItems.Clear();
    QualityMessage = string.Empty;
    // ... populate new results
}
```

---

## アンチパターン

### ViewModelからの直接UI操作

**What**：データバインディングの代わりに`x:Name`を使用してcode-behindからTextBlockの色や背景を直接設定。

**Why It's Wrong**：MVVM違反。ViewModelがUIコントロールに依存するとユニットテストができません。背景色ロジックがテストから見えなくなります。

**Better Approach**：ViewModelで色を文字列プロパティとして公開。XAMLで`Background="{Binding FieldBackground}"`にバインド。ViewModelプロパティを直接テスト。

```csharp
// ❌ WRONG — Direct UI manipulation
Field1TextBlock.Background = new SolidColorBrush(Colors.Pink);

// ✅ CORRECT — ViewModel property with binding
[ObservableProperty] private string sourceBField1Background = "Transparent";
```

### View層に比較ロジックを配置

**What**：XAMLトリガー、code-behind、またはバリューコンバーターで不一致ステータスやスコアを計算。

**Why It's Wrong**：比較ロジックはアプリケーション/ドメインロジックです。View層に配置するとテスト不能になり、ビジネスルールがUIフレームワークに結合されます。

**Better Approach**：`IsMismatch()`、`UpdateMismatchBackgrounds()`、`RecalculateMatchingScore()`をViewModelに配置。Viewは結果のプロパティにバインドするのみ。

```csharp
// ❌ WRONG — Mismatch check in IValueConverter
public object Convert(object[] values, ...) =>
    values[0]?.ToString() != values[1]?.ToString() ? Brushes.Pink : Brushes.Transparent;

// ✅ CORRECT — Mismatch check in ViewModel
private static bool IsMismatch(string? a, string? b)
    => (a ?? string.Empty) != (b ?? string.Empty);
```

---

## クイックリファレンス

### 実装チェックリスト

- [ ] スコア、ソースA/Bフィールド、背景色を持つ`ComparisonItemViewModel`を作成（Step 1）
- [ ] ピンク/グリーン/透明ロジックの`UpdateMismatchBackgrounds()`を追加（Step 1）
- [ ] エクスポート検証用の`GetUncheckedVisibleCount()`を追加（Step 1）
- [ ] 条件付きフィールド表示の`HasDisplayValue`可視性パターンを追加（Step 1）
- [ ] `ItemsControl`と`DataTemplate`による3カラムXAMLレイアウトを構築（Step 2）
- [ ] `FieldNameStyle`と`ValueStyle`リソーススタイルを追加（Step 2）
- [ ] Green/Orange/Red閾値の`UpdateScoreColor()`を実装（Step 3）
- [ ] `TwoWay` + `UpdateSourceTrigger=PropertyChanged`の編集可能`TextBox`フィールドを追加（Step 4）
- [ ] `partial void OnXxxChanged()`を`RecalculateMatchingScore()`に接続（Step 4）
- [ ] 検証対象フィールドごとに`IsFieldXChecked`にバインドした`CheckBox`を追加（Step 5）
- [ ] `ObservableCollection`と`SetResults()`を持つ親ViewModelを作成（Step 6）
- [ ] ライブプレビュー用に各アイテムの`PropertyChanged`をサブスクライブ（Step 6）
- [ ] デュアルエクスポートゲートを実装：全チェック済み＋全スコア閾値超過（Step 6）
- [ ] 確認：新データ読み込み前に`ComparisonItems.Clear()`が呼ばれること

### ファイル構成

| ファイル | 目的 | レイヤー |
|------|---------|-------|
| `ComparisonItemViewModel.cs` | スコア＋背景色付き単一比較行 | ViewModel |
| `ComparisonTabViewModel.cs` | 親コレクション＋エクスポートゲート | ViewModel |
| `ComparisonView.xaml` | ItemsControl付き3カラムレイアウト | View |

### 色リファレンス

| 色 | 16進 | 適用タイミング |
|------|-----|--------------|
| 🆕 ピンク | `#F8D7DA` | 不一致：ソースA ≠ ソースB |
| ✅ グリーン | `#BBF7D0` | ユーザーが検証チェックボックスをチェック |
| ❌ レッド | `Red` | スコア < 60% |
| オレンジ | `Orange` | スコア 60–79% |
| グリーン | `Green` | スコア ≥ 80% |
| 透明 | `Transparent` | フィールドが一致（ハイライトなし） |
| イエロー | `#FFFFCC` | 編集可能フィールドの背景 |

---

## リソース

- [CommunityToolkit.Mvvm ドキュメント](https://learn.microsoft.com/ja-jp/dotnet/communitytoolkit/mvvm/)
- [WPF ItemsControlとDataTemplate](https://learn.microsoft.com/ja-jp/dotnet/desktop/wpf/controls/itemscontrol)
- [ObservableObjectとソースジェネレーター](https://learn.microsoft.com/ja-jp/dotnet/communitytoolkit/mvvm/observableobject)
- `dotnet-generic-matching` — このビューで表示する結果を生成するマッチングサービス
- `dotnet-wpf-pdf-preview` — 比較結果と並べて表示するPDFプレビューパネル

---

## 変更履歴

| バージョン | 日付 | 変更内容 |
|---------|------|---------|
| 1.0.0 | 2025-07-13 | 🆕 初回リリース — 不一致ハイライト付きサイドバイサイド比較ビュー |

<!-- 英語版は ../SKILL.md を参照してください -->
