---
name: dotnet-ocr-matching-workflow
description: 基盤・インフラ・プレゼンテーションの各スキルをエンドツーエンドで合成し、OCR→DBマッチングの完全なシステムをオーケストレーションします。
author: RyoMurakami1983
tags: [dotnet, wpf, csharp, ddd, ocr, matching, workflow, orchestration]
invocable: false
version: 1.0.0
---

# OCRマッチングシステムをエンドツーエンドで構築

個別スキルを組み合わせて、OCRマッチングのフルパイプラインを構築するワークフローオーケストレーターです。DDDプロジェクトのセットアップ、セキュア設定、Oracle DB統合、Dify APIによるOCR抽出、重み付きフィールドマッチング、WPF比較UI、CSVエクスポートまでを、依存性注入（DI）で一貫して配線します。

## このスキルを使うタイミング

以下の場合にこのスキルを使用してください：
- OCR抽出データをデータベースレコードと照合する新しいWPFアプリケーションを構築するとき
- 複数の既存スキル（secure-config、oracle、dify、matching、comparison）を1つのシステムとして構成するとき
- 4レイヤーすべてをエンドツーエンドに配線したグリーンフィールドのDDDプロジェクトをセットアップするとき
- 空のソリューションから本番投入可能なOCRマッチングまでの手順書が必要なとき
- 新しいチームメンバーのオンボーディングとして、全体がどのように組み合わさるかを理解してもらうとき

**前提条件**:
- .NET 8+ SDKがインストールされていること
- Oracleデータベースにアクセス可能であること（参照データ用）
- Dify APIエンドポイントが設定されていること（OCR抽出用）
- DDDのレイヤードアーキテクチャを理解していること

---

## 関連スキル

- **`dotnet-wpf-secure-config`** — DPAPI暗号化の基盤（Step 2）
- **`dotnet-oracle-wpf-integration`** — Oracle DB接続 + リポジトリ（Step 2）
- **`dotnet-wpf-dify-api-integration`** — Dify APIクライアント + SSEストリーミング（Step 2）
- **`dotnet-wpf-employee-input`** — 社員番号入力と保存（Step 3）
- **`dotnet-wpf-pdf-preview`** — PDFアップロードとWebView2プレビュー（Step 4）
- **`dotnet-wpf-ocr-parameter-input`** — OCRパラメータ入力タブ（Step 5）
- **`dotnet-generic-matching`** — Domainレイヤーの重み付きフィールドマッチング（Step 6）
- **`dotnet-wpf-comparison-view`** — 結果を左右に並べて比較するUI（Step 7）
- **`tdd-standard-practice`** — Red-Green-Refactorで生成コードをテスト
- **`git-commit-practices`** — 各ステップをアトミックな変更としてコミット

---

## コア原則

1. **オーケストレーションし、重複実装しない** — このスキルは他のスキルを参照し、内容を再実装しません（ニュートラル）
2. **依存順序** — スキルは厳密な依存順序（foundation → infrastructure → presentation）で適用します（基礎と型）
3. **レイヤー分離** — DDD各レイヤーは許される依存方向が1つだけです（基礎と型）
4. **統合前にテスト** — レイヤーを配線する前に、各スキルの出力を独立して検証します（継続は力）
5. **DIによる合成** — レイヤー間の配線はDIコンテナ経由のみで行い、直接newしません（成長の複利）

---

## ワークフロー：OCRマッチングシステムを構築

### Step 1 — DDDプロジェクト構造をセットアップ

新しいソリューションを作成する場合、または既存のソリューションが4レイヤーDDD構造に従っているかを確認する場合に使用します。

ソリューションと4つのプロジェクトを作成します。Domainレイヤーは技術的関心ではなく、**ユースケース**単位で整理します。

```
YourApp/
├── YourApp.Domain/           # Domain Layer (no dependencies)
│   └── YourUseCase/          # Use-case based organization
│       ├── Services/
│       ├── ValueObjects/
│       ├── Specifications/
│       └── Interfaces (IRepository, IExtractor)
├── YourApp.Application/      # Application Layer (depends on Domain)
│   └── UseCases/YourUseCase/
├── YourApp.Infrastructure/   # Infrastructure Layer (implements Domain)
│   ├── Configuration/
│   ├── ExternalApis/         # Dify API etc.
│   ├── Databases/            # Oracle etc.
│   └── FileSystem/
└── YourApp.Presentation.Wpf/ # Presentation Layer (depends on Application)
    ├── ViewModels/
    ├── Views/
    ├── Converters/
    └── Services/
```

依存関係ルールを強制するため、プロジェクト参照を設定します：

```xml
<!-- YourApp.Application.csproj -->
<ProjectReference Include="..\YourApp.Domain\YourApp.Domain.csproj" />

<!-- YourApp.Infrastructure.csproj -->
<ProjectReference Include="..\YourApp.Domain\YourApp.Domain.csproj" />

<!-- YourApp.Presentation.Wpf.csproj -->
<ProjectReference Include="..\YourApp.Application\YourApp.Application.csproj" />
<ProjectReference Include="..\YourApp.Infrastructure\YourApp.Infrastructure.csproj" />
```

**依存関係ルール**:
- **Domain** → なし（純粋なビジネスロジック）
- **Application** → Domainのみ（ユースケースのオーケストレーション）
- **Infrastructure** → Domainのみ（インターフェースの実装）
- **Presentation** → Application + Infrastructure（DI登録のみ）

> **Values**: 基礎と型 / 成長の複利

### Step 2 — 基盤スキルを適用

後続ステップすべてが依存する、3つのインフラ基盤をセットアップするときに使用します。

以下の既存スキルを**この順序どおりに**適用してください。各スキルは前のスキルの上に構築されます：

| 順序 | スキル | 提供内容 | レイヤー |
|-------|-------|-----------------|-------|
| 1番目 | **`dotnet-wpf-secure-config`** | `DpapiEncryptor`, `SecureConfigService`, `AppConfigModel` | インフラ |
| 2番目 | **`dotnet-oracle-wpf-integration`** | Oracle接続、リポジトリ実装、接続テストダイアログ | インフラ |
| 3番目 | **`dotnet-wpf-dify-api-integration`** | `DifyApiService`, SSEストリーミング、APIテストダイアログ | インフラ |

🆕 **この順序が重要な理由**: OracleスキルとDifyスキルはいずれも`SecureConfigService`で認証情報を保存するため、secure-configが先に必要です。OracleとDifyは互いに独立ですが、どちらも設定基盤に依存します。

3つすべてを適用したら、各スキルが提供するテストダイアログで検証します：
- ✅ Oracle接続テストが成功する
- ✅ Dify API pingが応答を返す
- ✅ `%LOCALAPPDATA%` に設定ファイルが作成される

> **Values**: 基礎と型 / 継続は力

### Step 3 — 社員番号設定を追加

システムが「どのユーザーが文書を処理しているか」を識別する必要がある場合に使用します。

適用：**`dotnet-wpf-employee-input`**

既存インフラへの配線：
- （Step 2の）`AppConfigModel`に社員番号フィールドを追加
- （Step 2の）`SecureConfigService`で暗号化して保存
- メインウィンドウのSettingsメニューに追加

```csharp
// AppConfigModel extension (added by employee-input skill)
public class AppConfigModel
{
    // ... existing Oracle/Dify properties from Step 2
    public string? EmployeeId { get; set; }        // 🆕 Added
    public string? EmployeeName { get; set; }       // 🆕 Added
}
```

> **Values**: ニュートラル / 継続は力

### Step 4 — PDFアップロードとプレビューを追加

ドキュメント入力インターフェース（メインウィンドウ左側）を追加する場合に使用します。

適用：**`dotnet-wpf-pdf-preview`**

レイアウト統合：

```
┌──────────────────────────────────────────────────┐
│  Main Window                                      │
│  ┌───────────────────┬──────────────────────────┐ │
│  │  Left Column       │  Right Column            │ │
│  │  ┌───────────────┐ │  ┌────────────────────┐  │ │
│  │  │ Upload Button  │ │  │ TabControl         │  │ │
│  │  ├───────────────┤ │  │  ┌──────┬─────────┐ │  │ │
│  │  │               │ │  │  │OCR   │Results   │ │  │ │
│  │  │  WebView2     │ │  │  │Input │Comparison│ │  │ │
│  │  │  PDF Preview  │ │  │  │(Stp5)│(Step 7)  │ │  │ │
│  │  │               │ │  │  └──────┴─────────┘ │  │ │
│  │  └───────────────┘ │  └────────────────────┘  │ │
│  └───────────────────┴──────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

PDFプレビュースキルは左カラム用に`PdfPreviewService`を提供します。右カラムのTabControlには、Step 5とStep 7のタブを配置します。

> **Values**: 基礎と型 / ニュートラル

### Step 5 — OCRパラメータ入力タブを構築

右カラム最初のタブ（ユーザーがOCRパラメータを指定し、抽出をトリガーする画面）を作成する場合に使用します。

適用：**`dotnet-wpf-ocr-parameter-input`**

🆕 **ユーザーに確認**: どの分類フィールド／選択フィールドが必要かを確認してください。よくある例：

| フィールド種別 | 例 | バインド先 |
|-----------|---------|----------|
| カテゴリドロップダウン | "商品種別", "部署" | DB参照クエリ |
| 自由入力 | "備考", "特記事項" | Dify APIプロンプトパラメータ |
| 日付ピッカー | "注文日", "納期" | フィルタ条件 |

既存サービスへの配線：
- 「Execute OCR」ボタンを（Step 2の）`DifyApiService`に接続
- （Step 4の）`PdfPreviewService`から選択済みPDFパスを渡す
- `IProgress<(int, string)>`パターンで進捗を表示

```csharp
// ViewModel wiring — connects OCR tab to Dify API
[RelayCommand]
private async Task ExecuteOcrAsync()
{
    var progress = new Progress<(int percent, string message)>(p =>
    {
        ProgressValue = p.percent;
        StatusText = p.message;
    });

    // PdfPath comes from Step 4, DifyApiService from Step 2
    var results = await _processDocumentUseCase.ExecuteAsync(
        PdfPath, SelectedCategory, Remarks, progress);
}
```

> **Values**: 成長の複利 / ニュートラル

### Step 6 — Domainマッチングロジックを実装

OCR抽出データをデータベースレコードと比較する中核ビジネスロジックを構築するときに使用します。

適用：**`dotnet-generic-matching`**

🆕 **ユーザーに確認**: 照合対象フィールドと、その相対的重要度（重み）を確認してください：

| 質問 | 回答例 | 対応先 |
|----------|---------------|---------|
| レコードを識別するフィールドは？ | "商品名、得意先コード" | 重み 2.5–3.0 |
| 一致を確定するフィールドは？ | "単価、数量" | 重み 1.5–2.5 |
| 補助的なフィールドは？ | "寸法、備考" | 重み 0.5–1.5 |

`dotnet-generic-matching`スキルは、Domainレイヤーに以下のコンポーネントを作成します：

```
YourApp.Domain/
└── YourUseCase/
    ├── ValueObjects/
    │   ├── FieldComparison.cs
    │   └── MatchingScore.cs
    ├── Services/
    │   ├── SimilarityCalculator.cs
    │   └── FieldMatchingService<TSource, TCandidate>.cs
    └── Specifications/
        └── HighQualityMatchingSpecification.cs
```

ユーザー指定の重みでフィールド定義を構成します：

```csharp
var fields = new List<FieldDefinition<ExtractedItem, ReferenceRecord>>
{
    new()
    {
        FieldName = "ProductName",        // 🆕 User-specified
        SourceExtractor = s => s.Name,
        CandidateExtractor = c => c.ProductName,
        CompareFunction = SimilarityCalculator.StringSimilarity,
        Weight = 3.0                       // 🆕 User-specified
    },
    new()
    {
        FieldName = "UnitPrice",
        SourceExtractor = s => s.Price.ToString(),
        CandidateExtractor = c => c.UnitPrice.ToString(),
        CompareFunction = (a, b) =>
            SimilarityCalculator.NumericSimilarityDecimal(
                decimal.Parse(a), decimal.Parse(b)),
        Weight = 2.0
    }
};
```

> **Values**: 基礎と型 / 成長の複利

### Step 7 — 結果比較ビューを構築

マッチング結果を左右に並べて表示する2つ目のタブを作成する場合に使用します。

適用：**`dotnet-wpf-comparison-view`**

比較ビューはStep 6の`MatchingResult<TSource, TCandidate>`を受け取り、以下をレンダリングします：

```
┌─────────────────────────────────────────────────────┐
│  Results Tab                                         │
│  ┌────────┬──────────────┬──────────┬───────┬─────┐ │
│  │ ☐      │ DB Record    │ OCR Data │ Score │ Edit│ │
│  ├────────┼──────────────┼──────────┼───────┼─────┤ │
│  │ ☑      │ Widget A     │ Widget A │ 95.2% │  ✎  │ │
│  │ ☐      │ Gadget B     │ Gadget C │ 67.1% │  ✎  │ │
│  │ ☑      │ Part X       │ Part X   │ 100%  │  ✎  │ │
│  └────────┴──────────────┴──────────┴───────┴─────┘ │
│                                                      │
│  [Export CSV]                                        │
└─────────────────────────────────────────────────────┘
```

comparison-viewスキルが提供する主な機能：
- ✅ データベースレコードとOCR抽出データの左右比較
- ✅ 編集時に**スコア再計算**を行う編集可能フィールド
- ✅ ユーザー承認用のチェックボックス検証カラム
- ✅ スコアの色分け（緑 ≥ 80%、黄 ≥ 60%、赤 < 60%）

> **Values**: ニュートラル / 継続は力

### Step 8 — Applicationユースケースを作成

Applicationレイヤーで処理パイプライン全体を配線する（DomainとInfrastructureの接着剤）場合に使用します。

参照データ読み込み → OCR抽出 → マッチング、という全フローをオーケストレーションするユースケースを作成します。

```csharp
namespace YourApp.Application.UseCases.YourUseCase
{
    public class ProcessDocumentUseCase
    {
        private readonly IDocumentExtractor _extractor;    // Dify API (Infrastructure)
        private readonly IDataRepository _repository;       // Oracle DB (Infrastructure)
        private readonly FieldMatchingService<ExtractedItem, ReferenceRecord> _matcher; // Domain

        public ProcessDocumentUseCase(
            IDocumentExtractor extractor,
            IDataRepository repository,
            FieldMatchingService<ExtractedItem, ReferenceRecord> matcher)
        {
            _extractor = extractor;
            _repository = repository;
            _matcher = matcher;
        }

        public async Task<IEnumerable<MatchingResult<ExtractedItem, ReferenceRecord>>> ExecuteAsync(
            string pdfPath, string category, string remarks,
            IProgress<(int percent, string message)>? progress = null)
        {
            // 1. Load reference data from DB (10%)
            progress?.Report((10, "Loading reference data..."));
            var referenceData = await _repository.GetByCategoryAsync(category);

            // 2. Extract data from PDF via OCR (30-60%)
            progress?.Report((30, "Running OCR extraction..."));
            var extractedItems = await _extractor.ExtractAsync(
                pdfPath, remarks, progress);

            // 3. Match extracted items against reference data (80%)
            progress?.Report((80, "Matching records..."));
            var results = _matcher.MatchAll(extractedItems, referenceData);

            progress?.Report((100, "Complete"));
            return results;
        }
    }
}
```

🆕 **このユースケースは実装ではなくインターフェースに依存します** — DIコンテナ（Step 9）が具体的なサービスを提供します。

> **Values**: 基礎と型 / 成長の複利

### Step 9 — DIコンテナを配線

これまでのステップで作成したすべてのサービスをDIコンテナに登録する場合に使用します。

依存の流れに沿って、`App.xaml.cs`でサービスを登録します：

```csharp
protected override void OnStartup(StartupEventArgs e)
{
    var services = new ServiceCollection();

    // ── Foundation (Step 2) ──
    services.AddSingleton<ISecureConfigService, SecureConfigService>();

    // ── Infrastructure (Steps 2-3) ──
    services.AddSingleton<IDataRepository, OracleDatabaseRepository>();
    services.AddSingleton<IDocumentExtractor, DifyApiService>();

    // ── Domain (Step 6) ──
    services.AddSingleton(provider =>
    {
        var fields = BuildFieldDefinitions(); // User-configured weights
        return new FieldMatchingService<ExtractedItem, ReferenceRecord>(
            fields, successThreshold: 70.0);
    });

    // ── Application (Step 8) ──
    services.AddTransient<ProcessDocumentUseCase>();

    // ── Presentation (Steps 4-5, 7) ──
    services.AddTransient<MainWindowViewModel>();
    services.AddTransient<OcrProcessTabViewModel>();
    services.AddTransient<ResultTabViewModel>();

    _serviceProvider = services.BuildServiceProvider();

    var mainWindow = new MainWindow
    {
        DataContext = _serviceProvider.GetRequiredService<MainWindowViewModel>()
    };
    mainWindow.Show();
}
```

**DI登録の順序が重要なのは可読性のため**であり、実行時ではありません。依存フローと同じ順序で登録します：

```
SecureConfigService → OracleRepository → DifyApiService → MatchingService → UseCase → ViewModels
```

> **Values**: 成長の複利 / 基礎と型

### Step 10 — エクスポート機能を追加（任意）

ユーザーがマッチング結果を検証した後に、CSVやRPA出力を追加する場合に使用します。

エクスポート前に、すべての品質ゲートを通過していることを要求します：

```csharp
public class ExportService
{
    public void ExportToCsv(
        IEnumerable<MatchingResult<ExtractedItem, ReferenceRecord>> results,
        string outputPath)
    {
        // Quality gate checks
        var resultList = results.ToList();

        if (resultList.Any(r => !r.IsVerified))
            throw new InvalidOperationException(
                "All rows must be verified (checkbox) before export.");

        if (resultList.Any(r => r.Score.OverallPercentage < 70.0))
            throw new InvalidOperationException(
                "All matching scores must meet the quality threshold.");

        // RFC 4180 compliant CSV output
        using var writer = new StreamWriter(outputPath, false, Encoding.UTF8);
        writer.WriteLine(BuildHeaderRow());

        foreach (var result in resultList)
        {
            writer.WriteLine(BuildDataRow(result));
        }
    }

    private static string EscapeCsvField(string field)
    {
        if (field.Contains(',') || field.Contains('"') || field.Contains('\n'))
            return $"\"{field.Replace("\"", "\"\"")}\"";
        return field;
    }
}
```

✅ エクスポート前の品質チェック：
- すべてのマッチングスコアが閾値以上（例：70%）
- すべての行がユーザーのチェックボックスで検証済み
- RFC 4180準拠のCSVフィールドエスケープ（カンマ、クォート、改行）

> **Values**: 継続は力 / ニュートラル

### Step 11 — エンドツーエンドでテスト

すべてのスキルが正しく統合され、パイプライン全体が動作することを検証する場合に使用します。

以下のテストチェックリストを順番に実行します：

| # | テスト | 確認方法 | 依存 |
|---|------|--------------|------------|
| 1 | Oracle接続 | 設定（Settings）→ 接続テスト（Test Connection）ボタン | Step 2 |
| 2 | Dify API接続 | 設定（Settings）→ APIテスト（Test API）ボタン | Step 2 |
| 3 | 社員番号の永続化 | IDを入力 → アプリを再起動 → 復元されることを確認 | Step 3 |
| 4 | PDFアップロード + プレビュー | PDFを選択し、WebView2で表示されることを確認 | Step 4 |
| 5 | OCRパラメータ入力 | フィールドを入力し、実行（Execute）をクリック | Step 5 |
| 6 | OCR進捗表示 | プログレスバーとステータステキストを確認 | Step 5, 8 |
| 7 | マッチング結果表示 | 左右比較テーブルが表示されることを確認 | Step 6, 7 |
| 8 | 編集時の再計算 | フィールドを編集し、スコア更新を確認 | Step 7 |
| 9 | チェックボックス検証 | 全行にチェックし、エクスポート（Export）が有効になることを確認 | Step 7 |
| 10 | CSVエクスポート | エクスポートしてExcelで開く | Step 10 |

🆕 **いずれかのテストが失敗した場合**は、レイヤーを切り分けてデバッグします：
- インフラの問題 → 設定内の接続文字列とAPIキーを確認
- ドメインの問題 → 既知の入力でマッチングサービスをユニットテスト
- プレゼンテーションの問題 → XAMLのViewModelバインディングを確認

> **Values**: 継続は力 / 基礎と型

### Step 12 — 本番向けにカスタマイズ

特定の業務ドメイン向けにシステムを適用する場合に使用します。

| カスタマイズ | 変更箇所 | スキル参照 |
|---------------|----------------|-----------------|
| OCRパラメータの追加/削除 | `OcrProcessTabViewModel` | `dotnet-wpf-ocr-parameter-input` |
| マッチング対象フィールド/重みの変更 | DI内の`FieldDefinition`リスト | `dotnet-generic-matching` |
| 品質閾値の調整 | `FieldMatchingService`コンストラクタ | `dotnet-generic-matching` |
| 新しいDBカラムの追加 | リポジトリ + Domainモデル | `dotnet-oracle-wpf-integration` |
| DifyワークフローIDの変更 | `AppConfigModel` + Settings UI | `dotnet-wpf-dify-api-integration` |
| エクスポート形式の変更 | `ExportService` | このスキルのStep 10 |
| 比較カラムの追加 | `ResultTabViewModel` + XAML | `dotnet-wpf-comparison-view` |

🆕 **本番運用の堅牢化チェックリスト**:
- [ ] 各ユースケースにエラーハンドリング（try-catch + ユーザー向けメッセージ）
- [ ] 構造化ログイベントでのロギング
- [ ] 設定バックアップ/復元の仕組み
- [ ] OracleおよびDify API呼び出しのタイムアウト設定

> **Values**: 成長の複利 / 継続は力

---

## グッドプラクティス

### 1. 依存順序どおりにスキルを適用

✅ まず基盤スキル、次にインフラ、最後にプレゼンテーションを適用してください。依存チェーンは厳密です：

```
secure-config → oracle + dify → employee-input → pdf-preview → ocr-input → matching → comparison
```

先に進めすぎると、インターフェース不足やコンパイルエラーの原因になります。

### 2. 統合前に各レイヤーを独立してテスト

✅ 各スキルにはそれぞれのテスト手段（接続テストダイアログ、ユニットテストパターン）が用意されています。次のステップへ進む前に、スキル単体で動作することを確認してください。

```
Step 2: Test Oracle connection → Pass ✅
Step 2: Test Dify API → Pass ✅
Step 4: Test PDF preview → Pass ✅
Step 8: Wire together → Confidence ✅
```

### 3. すべてのレイヤー間依存はDIで解決

✅ ViewModelやユースケース内でインフラサービスを直接newしないでください。常にコンストラクタ注入し、DIコンテナ（Step 9）に登録します。

```csharp
// ✅ CORRECT — Constructor injection
public ProcessDocumentUseCase(
    IDocumentExtractor extractor,
    IDataRepository repository,
    FieldMatchingService<ExtractedItem, ReferenceRecord> matcher)

// ❌ WRONG — Direct instantiation
public ProcessDocumentUseCase()
{
    _extractor = new DifyApiService(new SecureConfigService()); // Tight coupling
}
```

---

## よくある落とし穴

### 1. 基盤スキルをスキップする

**問題**: `dotnet-wpf-secure-config`を先にセットアップせずに、OracleまたはDify統合へ進んでしまうこと。どちらのスキルも暗号化された認証情報の保存に`SecureConfigService`へ依存します。

**解決策**: 常にStep 2から順番に開始してください。認証情報を保存するサービスを使う前に、secure-configスキルを適用する必要があります。

```
❌ Step 2b (Oracle) → Error: ISecureConfigService not found
✅ Step 2a (secure-config) → Step 2b (Oracle) → Works
```

### 2. レイヤー間の密結合

**問題**: ViewModelがApplicationレイヤーのユースケースを介さずに、Oracleの`DbConnection`やDifyの`HttpClient`を直接参照してしまうこと。

**解決策**: ViewModelはApplicationレイヤーのユースケースにのみ依存させます。ユースケースがDomainとInfrastructureのサービスを調整します。

```csharp
// ❌ WRONG — ViewModel calls Infrastructure directly
public class OcrViewModel
{
    private readonly DifyApiService _dify; // Infrastructure type in Presentation!
}

// ✅ CORRECT — ViewModel calls Application layer
public class OcrViewModel
{
    private readonly ProcessDocumentUseCase _useCase; // Application type
}
```

### 3. 統合前に個別コンポーネントをテストしない

**問題**: 7個以上のスキルを一気に配線して、複数レイヤーをまたぐ不具合をデバッグすること。

**解決策**: Step 11のテストチェックリストに従ってください。エンドツーエンドが失敗する場合は、まずインフラ接続、次にドメインロジック、最後にプレゼンテーションのバインディング、という順に壊れているレイヤーを切り分けます。

---

## アンチパターン

### Applicationレイヤーを迂回する

**内容**: ViewがInfrastructureサービスを直接呼び出す（例：ViewModelが`OracleConnection`を生成し、クエリを実行する）。

**問題点**: DDDのレイヤリングに違反します。ビジネスロジックがViewModelに散らばり、テスト不能・再利用不能になります。

**より良いアプローチ**: Applicationレイヤーにユースケースを作成し、DomainとInfrastructureサービスを調整します。ViewModelはユースケースのみを呼び出します。

### DomainレイヤーがInfrastructure型に依存する

**内容**: Domainモデルが`Oracle.ManagedDataAccess`や`System.Net.Http`をimportする。

**問題点**: Domainレイヤーは外部依存ゼロでなければなりません。Domainにインフラ型が混入すると、DBやAPIなしでユニットテストできなくなります。

**より良いアプローチ**: Domainにインターフェース（`IDataRepository`、`IDocumentExtractor`）を定義し、Infrastructureで実装します。DIで登録します。

```csharp
// ❌ WRONG — Domain depends on Oracle
namespace YourApp.Domain.Matching
{
    using Oracle.ManagedDataAccess.Client; // Infrastructure leak!
    public class MatchingService { ... }
}

// ✅ CORRECT — Domain depends only on its own interfaces
namespace YourApp.Domain.Matching
{
    public class MatchingService
    {
        private readonly IDataRepository _repository; // Domain interface
    }
}
```

### このオーケストレーターにスキル内容を複製する

**内容**: `dotnet-generic-matching`や`dotnet-wpf-secure-config`の実装コードを、このワークフロースキルに丸ごとコピーする。

**問題点**: メンテナンス負荷が増大します。元スキルが変更されても、このスキルに反映されません。オーケストレーターは複製ではなく参照が目的です。

**より良いアプローチ**: 各ステップで「Apply: **`skill-name`**」と書き、配線／統合ポイントのみを説明します。

---

## クイックリファレンス

### 実装チェックリスト

- [ ] 4レイヤーDDDソリューション構造を作成（Step 1）
- [ ] `dotnet-wpf-secure-config`を適用 — DPAPI基盤（Step 2）
- [ ] `dotnet-oracle-wpf-integration`を適用 — Oracleリポジトリ（Step 2）
- [ ] `dotnet-wpf-dify-api-integration`を適用 — Dify APIクライアント（Step 2）
- [ ] `dotnet-wpf-employee-input`を適用 — 社員番号（Step 3）
- [ ] `dotnet-wpf-pdf-preview`を適用 — PDFアップロード + WebView2（Step 4）
- [ ] `dotnet-wpf-ocr-parameter-input`を適用 — OCRパラメータタブ（Step 5）
- [ ] `dotnet-generic-matching`を適用 — Domainマッチングロジック（Step 6）
- [ ] `dotnet-wpf-comparison-view`を適用 — 結果比較タブ（Step 7）
- [ ] Applicationレイヤーに`ProcessDocumentUseCase`を作成（Step 8）
- [ ] `App.xaml.cs`でDIコンテナを配線（Step 9）
- [ ] エクスポート機能を追加（Step 10、任意）
- [ ] エンドツーエンドのテストチェックリストを実行（Step 11）
- [ ] 本番向けにフィールド・重み・閾値をカスタマイズ（Step 12）

### スキル依存関係グラフ

```
dotnet-wpf-secure-config          (foundation — no dependencies)
    ├── dotnet-oracle-wpf-integration     (needs secure-config)
    ├── dotnet-wpf-dify-api-integration   (needs secure-config)
    └── dotnet-wpf-employee-input         (needs secure-config)

dotnet-wpf-pdf-preview            (independent — UI only)

dotnet-wpf-ocr-parameter-input   (needs dify-api, pdf-preview)

dotnet-generic-matching            (independent — Domain only)

dotnet-wpf-comparison-view        (needs generic-matching)
```

### レイヤー責務表

| レイヤー | 含むもの | 依存先 | クラス例 |
|-------|----------|-----------|-----------------|
| 🆕 ドメイン | ビジネスロジック、インターフェース、値オブジェクト | なし | `FieldMatchingService`, `IDataRepository` |
| ✅ アプリケーション | ユースケース、オーケストレーション | ドメイン | `ProcessDocumentUseCase` |
| ✅ インフラ | DBアクセス、APIクライアント、設定 | ドメイン | `OracleDatabaseRepository`, `DifyApiService` |
| ❌ プレゼンテーション | ViewModels、Views、XAML | アプリケーション | `MainWindowViewModel`, `ResultTabView` |

### 統合配線サマリー

| From（提供側） | To（利用側） | 経由 | 登録箇所 |
|-----------------|--------------|-----|---------------|
| `SecureConfigService` | Oracle、Dify、社員情報 | `ISecureConfigService` | DI（Step 9） |
| `OracleDatabaseRepository` | `ProcessDocumentUseCase` | `IDataRepository` | DI（Step 9） |
| `DifyApiService` | `ProcessDocumentUseCase` | `IDocumentExtractor` | DI（Step 9） |
| `FieldMatchingService` | `ProcessDocumentUseCase` | 直接（ドメイン） | DI（Step 9） |
| `ProcessDocumentUseCase` | `OcrProcessTabViewModel` | コンストラクタ注入 | DI（Step 9） |

---

## リソース

- `dotnet-wpf-secure-config` — DPAPI暗号化と設定管理
- `dotnet-oracle-wpf-integration` — Oracleデータベース統合
- `dotnet-wpf-dify-api-integration` — Dify APIによるOCR抽出
- `dotnet-generic-matching` — 汎用の重み付きフィールドマッチング
- `dotnet-wpf-comparison-view` — 左右比較の結果UI
- [Microsoft DI Documentation](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection)
- [Domain-Driven Design Reference (Eric Evans)](https://www.domainlanguage.com/ddd/reference/)

---

## 変更履歴

| バージョン | 日付 | 変更 |
|---------|------|---------|
| 1.0.0 | 2025-07-13 | 🆕 初回リリース — OCRマッチングシステム用の12ステップ・オーケストレーター |

<!-- 英語版は ../SKILL.md を参照してください -->
