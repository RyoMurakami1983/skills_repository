---
name: dotnet-access-to-oracle-migration
description: >
  Migrate Access SQL to Oracle, generate .NET C# code.
  Use when converting Access queries to Oracle.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, oracle, access, csharp, database-migration]
  invocable: false
---

<!-- このドキュメントは dotnet-access-to-oracle-migration の日本語版です。英語版: ../SKILL.md -->

# Access SQLからOracle移行

AccessデータベースクエリをOracleに移行し、.NET（C#）IOracle実装クラスを生成するためのエンドツーエンドワークフロー。TNS解決、VIEW/SYNONYM検出、SQL変換、レコード数検証をカバー。

## When to Use This Skill

以下の場合にこのスキルを使用してください：
- .NETアプリケーション向けにAccessデータベースクエリをOracleに移行する場合
- Access SQLをOracle互換SQLに変換する場合（適切なクォート処理付き）
- 検証済みOracle SQLからC# IOracle実装クラスを生成する場合
- Accessリンクテーブルが隠すVIEW/SYNONYM構造を検出する場合
- tnspingとEZ Connect形式でOracle接続を検証する場合
- AccessとOracle間のデータ整合性をNear Equal検証で確認する場合

## Related Skills

- **`skill-quality-validation`** — スキル品質の検証
- **`skill-writing-guide`** — スキル作成のベストプラクティス

---

## Core Principles

1. **Error-Driven Approach** — ORA-*エラーからDSN・認証・スキーマの問題を学ぶ（基礎と型）
2. **Structural Awareness** — TABLEと決めつけずVIEW/SYNONYMを検出する（ニュートラル）
3. **Access Naming Translation** — `.` → `_`変換を逆転してOracle形式に戻す（基礎と型）
4. **Progressive Validation** — 接続 → 検出 → 検証 → 変換 → 生成（継続は力）
5. **Near Equal Tolerance** — タイミング/データ更新による±5件差を許容（成長の複利）

---

## Dependencies

- **.NET 6.0+** + Oracle.ManagedDataAccess.Core（NuGet）
- **Oracle Instant Client**（`tnsping`コマンド用）
- **Accessデータベース**（リンクテーブル付き）

---

## Workflow: Access SQLからOracle移行

### Step 1 — 情報収集

Oracle接続を試行する前に、必要な情報をすべて事前に収集する。

ユーザーから収集する項目：
1. **Access SQL**: 完全なクエリ（Access構文）
2. **レコード数**: Accessからの件数
3. **TNS/DSN名**: 例：PROD_DSN
4. **Oracle認証情報**: ユーザー名とパスワード

**Why**: 事前に情報を集めないと、複数回の往復が発生する（TNS名違い → 再確認、認証情報不足 → 再確認）。一括収集により1パスで移行完了できる。

> **Values**: 基礎と型 / 継続は力

### Step 2 — tnspingでTNS名を解決

`tnsping`を実行して、TNS/DSN名をOracle.ManagedDataAccess.Coreが必要とするEZ Connect形式に変換する。

```powershell
# ✅ 正解 — TNS名をEZ Connect形式に解決
tnsping PROD_DSN
```

**出力から抽出**:
- HOST: `192.0.2.10`, PORT: `1521`, SERVICE_NAME: `prod_service`
- **EZ Connect**: `192.0.2.10:1521/prod_service`

**Why**: Oracle.ManagedDataAccess.CoreはEZ Connect形式を要求する。形式を推測するとORA-50201エラーが発生し、デバッグ時間を浪費する。

> **Values**: 基礎と型 / ニュートラル

### Step 3 — 接続テストとエラー処理

ORA-*エラーコードを学習シグナルとして活用し、DSN・認証・ネットワークの問題を修正する。

```powershell
# ✅ 正解 — エラーハンドリング付き接続テスト
Add-Type -Path "Oracle.ManagedDataAccess.dll"
$conn = New-Object Oracle.ManagedDataAccess.Client.OracleConnection
$conn.ConnectionString = "User Id=SCHEMA_A;Password=your_password;Data Source=192.0.2.10:1521/prod_service"

try {
    $conn.Open()
    Write-Host "✓ 接続成功"
    $conn.Close()
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
```

| Error Code | Cause | Solution |
|------------|-------|----------|
| ORA-50201 | DSN形式不正 | `tnsping`でEZ Connect取得 |
| ORA-01017 | 認証情報誤り | ユーザー名/パスワード再確認 |
| ORA-12154/12545 | TNS/ネットワーク問題 | EZ Connectまたはファイアウォール確認 |

> **Values**: 基礎と型 / 成長の複利

### Step 4 — Accessテーブル名の変換

Accessの `.` → `_` 変換を逆転：`SCHEMA_A_production_info` → `SCHEMA_A."production_info"`

```csharp
// ✅ 正解 — 最初のアンダースコアでのみ分割
var parts = "SCHEMA_A_production_info".Split('_', 2);
string oracleFormat = $"{parts[0]}.\"{parts[1]}\"";  // SCHEMA_A."production_info"
```

**Why**: Accessはリンクテーブル名の`.`を暗黙的に`_`に変換する。これを逆転しなければ、すべてのOracleクエリが「テーブルが見つからない」エラーになる。

> **Values**: 基礎と型

### Step 5 — VIEW/SYNONYM構造の検出

TABLEと決めつけずオブジェクトタイプを確認する。Accessはすべてのリンクオブジェクトを「テーブル」として表示し、Oracleの実際の構造を隠す。

```sql
-- ✅ 正解 — TABLEと決めつけずオブジェクトタイプを確認
SELECT owner, object_name, object_type
FROM all_objects
WHERE object_name IN ('production_info', 'detasheet_info')
  AND owner IN ('SCHEMA_A', 'SCHEMA_B', 'PUBLIC')
ORDER BY owner, object_name;
```

**Why**: このステップを飛ばすと、カラムクエリとSQL変換で連鎖的なエラーが発生する。

> **Values**: ニュートラル / 基礎と型

### Step 6 — カラム存在検証

**実際のテーブル所有者**（SYNONYM所有者ではない）で`all_tab_columns`を照会し、正確なカラム名を取得する。

```sql
-- ✅ 正解 — 実際のテーブル所有者からカラムを照会
SELECT column_id, column_name, data_type, data_length
FROM all_tab_columns
WHERE table_name = 'production_info'
  AND owner = 'SCHEMA_B'  -- SYNONYM所有者ではなく実際の所有者
ORDER BY column_id;
```

**Why**: Oracleのカラム名は大文字小文字を区別する。カラムの欠落やスペルミスはサイレントなデータ損失やクエリエラーの原因になる。

> **Values**: 基礎と型 / 継続は力

### Step 7 — SQL構文変換（3ルール）

3つのルールを一貫して適用し、Access SQLをOracle SQLに変換する。

**Rule 1**: テーブル名 — `SCHEMA_A_production_info` → `SCHEMA_A."production_info"`
**Rule 2**: カラム名 — `ship_date` → `"ship_date"`
**Rule 3**: 文字列リテラル — `"202601"` → `'202601'`

```sql
-- ❌ 誤り — Access SQL
SELECT SCHEMA_A_production_info.ship_date
FROM SCHEMA_A_production_info
WHERE SCHEMA_A_production_info.ship_date >= "202601"

-- ✅ 正解 — 適切なクォートを使用したOracle SQL
SELECT s."ship_date"
FROM SCHEMA_A."production_info" s
WHERE s."ship_date" >= '202601'
```

**Why**: AccessとOracleは逆のクォート規則を使用する。3ルールを一貫して適用することで、最も一般的なSQL変換エラーを防止できる。

> **Values**: 基礎と型 / ニュートラル

### Step 8 — Near Equal検証

変換したSQLをOracleで実行し、レコード数をAccess件数と比較する。±5件差を許容。

```powershell
# ✅ 正解 — Oracleレコード数を取得して比較
$cmd = $conn.CreateCommand()
$cmd.CommandText = 'SELECT COUNT(*) FROM SCHEMA_A."production_info" s WHERE s."ship_date" >= ''202601'''
$oracleCount = [int]$cmd.ExecuteScalar()
$accessCount = 178

$diff = [Math]::Abs($oracleCount - $accessCount)
if ($diff -le 5) {
    Write-Host "✓ Near Equal: Access=$accessCount, Oracle=$oracleCount (diff=$diff)"
} else {
    Write-Host "⚠ Difference too large (diff=$diff)"
}
```

**Why**: 正確な件数一致は稀である（AccessとOracleは異なるタイミングでクエリを実行するため）。Near Equalは同一スナップショットを要求せずに正確性を検証する。

> **Values**: 成長の複利 / 継続は力

### Step 9 — C# IOracle実装の生成

検証済みOracle SQLを使用して、IOracleインターフェースを実装するC#クラスを作成する。

```csharp
// ✅ 正解 — IOracle実装テンプレート
using System;

namespace OracleApp
{
    internal class SampleDataExtractor : IOracle
    {
        string IOracle.User => Environment.GetEnvironmentVariable("ORA_USER") ?? "SCHEMA_A";
        string IOracle.Password => Environment.GetEnvironmentVariable("ORA_PW") ?? "your_password";
        string IOracle.Dsn => Environment.GetEnvironmentVariable("ORA_DSN") ?? "192.0.2.10:1521/prod_service";

        // C# verbatim strings (@"") require doubling internal quotes
        public string Sql => @"
SELECT
   s.""ship_date"",
   s.""prod_number""
FROM SCHEMA_A.""production_info"" s
WHERE s.""ship_date"" >= '202601'";
    }
}
```

**C#文字列エスケープルール**: Oracle `"ship_date"` → C# `@""ship_date""`（引用符を二重にする！）

**Why**: コード生成は最終ステップ。SQL検証前にコードを生成すると、SQLレベルの失敗より追跡が困難なランタイムエラーが発生する。

> **Values**: 継続は力 / 成長の複利

---

## Good Practices

### 1. 接続解決にはtnspingを必ず使用

**What**: 接続前に`tnsping`を実行してTNS/DSN名をEZ Connect形式に解決する。

**Why**: ORA-50201エラーを排除し、正確なHOST/PORT/SERVICE_NAMEを取得できる。

**Values**: 基礎と型（再現可能な型）

### 2. クエリ前にオブジェクトタイプを検出

**What**: カラムやデータをクエリする前に`all_objects`と`all_synonyms`を確認する。

**Why**: AccessはOracleのVIEW/SYNONYM構造を隠す。TABLEと決めつけると連鎖的なエラーが発生する。

**Values**: ニュートラル（偏らない検証）/ 基礎と型

### 3. SQL変換前にカラムを検証

**What**: SQL変換前にすべてのAccessカラムがOracleに正確なスペルで存在することを確認する。

**Why**: 大文字小文字区別のカラム名はサイレントなデータ損失を引き起こす。早期検証が遅い失敗を防ぐ。

**Values**: 継続は力（段階的検証）

---

## Common Pitfalls

### 1. ODBC DSNを直接使用

**Problem**: Oracle.ManagedDataAccess.Coreに`Data Source=PROD_DSN`を渡す。

```csharp
// ❌ 誤り — ODBC DSN名はORA-50201の原因
var connStr = "User Id=SCHEMA_A;Password=your_password;Data Source=PROD_DSN";
```

**Solution**: `tnsping`でEZ Connect形式を取得する。

```csharp
// ✅ 正解 — EZ Connect形式
var connStr = "User Id=SCHEMA_A;Password=your_password;Data Source=192.0.2.10:1521/prod_service";
```

### 2. タイプ検出せずテーブルと決めつけ

**Problem**: 実際のテーブルが`SCHEMA_B`にあるのに`owner = 'SCHEMA_A'`で`all_tab_columns`をクエリ。

**Solution**: まず`all_objects`を確認し、次に`all_synonyms`で実際のテーブル所有者を取得。

### 3. C#でダブルクォートのエスケープ忘れ

**Problem**: Oracle SQLをC#にコピー＆ペーストする際に引用符を二重にしない。

**Solution**: C# `@""`文字列内のすべての`"`を二重にする: `s."ship_date"` → `s.""ship_date""`

---

## Anti-Patterns

### tnspingを省略してEZ Connectを推測

**What**: `Data Source=PROD_DSN`が`Data Source=someserver:1521/PROD_DSN`を意味すると仮定する。

**Why It's Wrong**: TNS名は予測可能なパターンに従わない。ホスト名はIP、DNS名、エイリアスの場合がある。

**Better Approach**: 常に`tnsping`を実行して正確なHOST/PORT/SERVICE_NAMEを取得する。

---

## Quick Reference

### 移行チェックリスト

- [ ] 収集: Access SQL、レコード数、TNS名、認証情報
- [ ] TNS解決 → `tnsping` → EZ Connect形式
- [ ] 接続テスト → ORA-*エラー対応
- [ ] Accessテーブル名変換 → `SCHEMA."table_name"`形式
- [ ] 構造検出 → `all_objects`（VIEW/SYNONYM/TABLE）
- [ ] カラム検証 → `all_tab_columns`（実際の所有者で）
- [ ] SQL変換 → 3ルール（テーブル/カラム/リテラルのクォート）
- [ ] 検証 → COUNT(*) ≈ Access件数（±5）
- [ ] C#生成 → IOracle実装（`""`エスケープ付き）

### 変換チートシート

| Access | Oracle | C# @"" 文字列 |
|--------|--------|---------------|
| `SCHEMA_A_production_info` | `SCHEMA_A."production_info"` | `SCHEMA_A.""production_info""` |
| `ship_date` | `"ship_date"` | `""ship_date""` |
| `"202601"` | `'202601'` | `'202601'` |

---

## Resources

- [references/advanced-examples.md](references/advanced-examples.md) — 本番レベルの例
- [references/advanced-examples-part2.md](references/advanced-examples-part2.md) — 追加例

---

## Changelog

### Version 2.0.0 (2026-02-15)
- **Breaking**: パターン形式からワークフロー形式に変換
- Core PrinciplesとすべてのステップにValues統合を追加
- Good Practices、Common Pitfalls、Anti-Patternsセクションを追加
- 依存関係セクションと移行チェックリストを追加

### Version 1.0.0 (2026-02-12)
- 初期リリース（パターン形式）
- 完全な移行ワークフローをカバーする9パターン
