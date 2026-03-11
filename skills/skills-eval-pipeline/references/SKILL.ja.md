---
name: skills-eval-pipeline
description: "スキルの有効性をテストケースで評価したいとき、またはスキルあり・なしの応答品質を比較してベンチマークレポートを生成したいときに使用。"
---

# スキル評価パイプライン（Skills Eval Pipeline）

SKILL.md がエージェント出力の品質を向上させるかどうかを計測するパイプライン。テストケースを「スキルあり」と「スキルなし（ベースライン）」の両モードで実行し、応答を採点、統計集計し、HTMLビジュアルレポートを生成する。

## このスキルを使うとき

このスキルを使う場面:
- SKILL.md が実際にエージェントの応答を改善するか数値で計測する
- 「スキルあり」vs「ベースライン（スキルなし）」のパフォーマンスを定量比較する
- 変更済みスキルをマージ前にベンチマーク証拠付きで検証する
- どのテストケースが失敗しているか、なぜスキルが機能しないか診断する
- まだ eval カバレッジのないスキルに `evals.json` テストスイートを構築する
- ベンチマーク結果をステークホルダーと共有できるHTMLレポートを生成する

> **スコープ**: テストケース設計 → 実行 → 採点 → 集計 → 可視化 → フィードバックループ。Phase 4.2（Tauri/WPF ネイティブ GUI）はこのバージョンのスコープ外。

## 関連スキル

- **`skills-author-skill`** — テスト対象スキルの新規作成
- **`skills-validate-skill`** — 静的バリデーション（eval パイプラインの前に実行）
- **`skills-revise-skill`** — `feedback.json` の項目を反映してスキルを改訂
- **`skill-quality-validation`** — validate_skill.py 静的チェック（eval の補完）

---

## 依存関係

- Python 3.10+
- `uv`（または `pip`）でスクリプトを実行
- 外部 API 呼び出し不要 — エージェント応答は `task tool` サブエージェントが処理

---

## 核心原則

1. **スキーマファースト** (基礎と型) — すべてのデータ契約を実装前に `references/schemas.md` で定義する
2. **並列実行** (継続は力) — スキルあり・ベースラインを同時実行してレイテンシを最小化する
3. **人間参加型ループ** (余白の設計) — パイプラインはデータを生成する。受け入れるかどうかは人間が判断する
4. **疎結合設計** (成長の複利) — 各エージェント（runner/grader/analyzer）は独立して再利用可能
5. **部分障害への許容** (温故知新) — ケース単位のエラーは全体実行を止めない。セットアップエラーのみ中断

---

## 判断テーブル

現在の状態から次のステップを選択する。

| 現在の状態 | 次のステップ |
|-----------|-------------|
| `evals.json` がない | ステップ1: テストケース設計 |
| `evals.json` あり、`runs/` なし | ステップ2: 評価実行 |
| `runs/` あり、`benchmark_summary.json` なし | ステップ3: 集計 |
| `benchmark_summary.json` あり、ビューアなし | ステップ4: HTMLビューア生成 |
| ビューア生成済み、`feedback.json` なし | ステップ5: 分析・フィードバック生成 |
| `feedback.json` あり | ステップ6: フィードバックに基づいて行動 |

---

## ディレクトリ構造

```
skills/skills-eval-pipeline/
├── SKILL.md                    # このファイル — オーケストレーター
├── agents/
│   ├── runner.md               # スキルあり + ベースラインのサブエージェントを起動
│   ├── grader.md               # 1件の応答をアサーションに対して採点
│   └── analyzer.md             # ベンチマーク結果から feedback.json を生成
├── scripts/
│   ├── aggregate_benchmark.py  # 採点結果を集計 → benchmark_summary.json
│   └── generate_viewer.py      # benchmark_summary.json → HTML ビューア
├── viewer/
│   └── index.html              # HTML ビューアテンプレート（自己完結）
└── references/
    ├── schemas.md              # 全データファイルの JSON 契約
    └── SKILL.ja.md             # このファイル（日本語版）
```

### eval 出力ディレクトリ

| スキル種別 | eval ディレクトリ | Git 追跡 |
|------------|-----------------|---------|
| 公開スキル（`skills/`, `production/`） | `evals/<skill_id>/` | ✅ コミット（evals.json のみ） |
| プライベートスキル（`local_private_skills/`） | `local_private_skill_evals/<skill_id>/` | ❌ 全内容 git 無視 |

ディレクトリを切り替えるには `--evals-dir` オプションを使用（ステップ3・4 参照）。

---

## ワークフロー: スキルを評価する

### ステップ1 — テストケースを設計する

`evals/<skill_id>/evals.json` を最低3ケースで作成する。

> **プライベートスキルの場合**: `local_private_skill_evals/<skill_id>/evals.json` に保存する。このディレクトリは git 無視で、コミットされない。

**アサーション種別**（`references/schemas.md` より）:

| 種別 | 使う場面 |
|------|---------|
| `contains` | 出力に必須の文字列が含まれているか確認 |
| `not_contains` | 出力に含まれてはいけない文字列の確認 |
| `llm_grade` | ルーブリックに基づく意味的品質の判断 |
| `regex` | ID・フォーマット等のパターンマッチング |

**最小構成テストスイート（3ケース推奨）**:
1. **ハッピーパス** — 標準ユースケース。出力の主要構造要素が存在するか確認
2. **エッジケース** — 曖昧な入力。適切に処理されるか確認
3. **アンチパターン** — スキルを発火させるべきでない入力。非リグレッション確認

このステップを使う理由: テストケースは評価の根拠。先に定義しないと「何を改善したいのか」が不明確になる。

> **Values**: 基礎と型

### ステップ2 — 評価を実行する

`task tool` サブエージェントを通じて `agents/runner.md` を呼び出す。渡すもの:
- `skill_id` — テスト対象スキルのディレクトリ名
- `evals_path` — `evals.json` へのパス
- `run_id` — 一意の実行識別子（例: `run-YYYYMMDD-NNN`）

ランナーは**テストケースごとに2つのサブエージェントを並列起動**する:

```
各ケースに対して:
  ├── task(with_skill): プロンプト + SKILL.md の内容 → 応答 → grader
  └── task(baseline):   プロンプトのみ              → 応答 → grader
```

各サブエージェントの応答は `agents/grader.md` に渡され、`grading_result.json` が返される。

結果の書き込み先: `evals/<skill_id>/runs/`

このステップを使う理由: 並列実行は同等条件での比較を最小レイテンシで実現する。

> **Values**: 継続は力

### ステップ3 — 結果を集計する

```bash
# Bash / macOS / Linux — 公開スキル
python skills/skills-eval-pipeline/scripts/aggregate_benchmark.py \
  --skill-id skills-author-skill \
  --run-id run-20260310-001

# Bash / macOS / Linux — プライベートスキル
python skills/skills-eval-pipeline/scripts/aggregate_benchmark.py \
  --skill-id facility-create-knowledge-index \
  --run-id run-20260310-001 \
  --evals-dir local_private_skill_evals
```

```powershell
# PowerShell (Windows) — 公開スキル
python skills\skills-eval-pipeline\scripts\aggregate_benchmark.py `
  --skill-id skills-author-skill `
  --run-id run-20260310-001

# PowerShell (Windows) — プライベートスキル
python skills\skills-eval-pipeline\scripts\aggregate_benchmark.py `
  --skill-id facility-create-knowledge-index `
  --run-id run-20260310-001 `
  --evals-dir local_private_skill_evals
```

出力: `evals/<skill_id>/benchmark_summary.json`

| フィールド | 意味 |
|-----------|------|
| `verdict` | `improved` / `neutral` / `degraded` |
| `delta` | `with_skill.mean - baseline.mean` |
| `improvement_pct` | `delta / baseline.mean × 100` |

このステップを使う理由: 集計によって個別ケーススコアでは見えないパターンが浮かび上がる。

> **Values**: 温故知新

### ステップ4 — HTML ビューアを生成する

```bash
# Bash / macOS / Linux — 公開スキル
python skills/skills-eval-pipeline/scripts/generate_viewer.py \
  --skill-id skills-author-skill

# Bash / macOS / Linux — プライベートスキル
python skills/skills-eval-pipeline/scripts/generate_viewer.py \
  --skill-id facility-create-knowledge-index \
  --evals-dir local_private_skill_evals
```

```powershell
# PowerShell (Windows) — 公開スキル
python skills\skills-eval-pipeline\scripts\generate_viewer.py `
  --skill-id skills-author-skill

# PowerShell (Windows) — プライベートスキル
python skills\skills-eval-pipeline\scripts\generate_viewer.py `
  --skill-id facility-create-knowledge-index `
  --evals-dir local_private_skill_evals
```

出力: `evals/<skill_id>/viewer.html` — ブラウザで開くだけ、サーバー不要。

ビューアに表示される情報:
- 判定バッジ（✅ Improved / ⚠️ Neutral / ❌ Degraded）
- スキルあり vs ベースライン の mean と delta
- ケース別スコア比較テーブル

このステップを使う理由: 視覚的なサマリーが人間の素早い判断を可能にする（余白の設計）。

> **Values**: 余白の設計

### ステップ5 — 分析してフィードバックを生成する

`task tool` サブエージェントを通じて `agents/analyzer.md` を呼び出す。渡すもの:
- `benchmark_summary.json` のパス
- `evals.json` のパス（アサーションのコンテキスト用）
- オプション: 詳細分析用の `grading_result.json` ファイル群

出力: `evals/<skill_id>/feedback.json` — KPT（Keep / Problem / Try）分類の改善提案。

KPT とは「続けること（Keep）・問題（Problem）・改善提案（Try）」の振り返りフレームワーク。

| `next_action` | 意味 |
|---------------|------|
| `accept` | delta > 0.1 かつ劣化ケースなし — スキルは有効 |
| `revise_skill` | リグレッションまたは問題発見 — `skills-revise-skill` に委譲 |
| `add_cases` | neutral 判定 — テストケースを追加してシグナルを強化 |
| `escalate` | 深刻なリグレッション（delta < -0.2）— 手動レビューが必要 |

このステップを使う理由: 構造化フィードバックが次のイテレーションをガイドする。

> **Values**: 余白の設計 / 成長の複利

### ステップ6 — フィードバックに基づいて行動する

| `next_action` | 次のアクション |
|---------------|--------------|
| `accept` | `evals/` ディレクトリをコミット、ベンチマーク証拠付きで PR 作成 |
| `revise_skill` | `feedback.json` の項目を入力として `skills-revise-skill` を呼び出す |
| `add_cases` | ステップ1に戻り、エッジケースを追加する |
| `escalate` | runner/grader の出力を手動確認。プロンプトインジェクションのリスクも確認 |

✅ **良い例**: `feedback.json` の項目を根拠としてスキルを改訂する
❌ **悪い例**: 1回の eval で「neutral」が出て、何もせずに終わりにする

このステップを使う理由: フィードバックループが複利成長を生む。1回で完璧を目指さない。

> **Values**: 継続は力

---

## アンチパターン

### アーキテクチャレベル

- **runner と grader を1つのエージェントに統合する** — runner は応答収集、grader は採点という責務を分離することで再利用性とデバッグ容易性を確保している。統合すると採点ロジックが再利用不能になる。

- **schemas.md を無視してアドホックな JSON を使う** — 全データフローは `references/schemas.md` で定義された契約を通じる。独自形式は `aggregate_benchmark.py` とビューアを無音で壊す。

- **eval パイプラインを静的バリデーションの代替として使う** — `skills-validate-skill`（構造・言語チェック）を先に実行してから `skills-eval-pipeline`（振る舞いチェック）を実行する。eval はフロントマターエラーを検出しない。

- **イテレーションなしの一発 eval** — このパイプラインは「実行 → 分析 → 改訂 → 再実行」のループとして設計されている。1回で最終判断を下すのはフィードバックループの設計を無駄にする。

---

## ベストプラクティス

- テストケースごとに最低1つの `llm_grade` アサーションを入れる（意味的カバレッジ）
- `run_id` に日付スタンプを使う（例: `run-20260310-001`）
- `evals/<skill_id>/evals.json` をコミットしてテスト履歴を管理する。`runs/` は `.gitignore` に追加
- `skills-eval-pipeline` の前に `skills-validate-skill` を実行して静的問題を先に修正する
- 予期しない振る舞いを発見したとき、リグレッション後だけでなくリアルタイムでテストケースを追加する
- ビューアHTML実装では、HTML挿入が不要な箇所は `textContent` を優先する
- `innerHTML` に変数を埋め込む場合は、すべての変数を `escHtml()` でエスケープしてから挿入する

---

## よくある落とし穴

1. **ベースラインとの差異がない**: スキルありとベースラインが同じ出力を返す → アサーションが差別化できない。
   修正方法: スキル固有の振る舞いに紐付いた `llm_grade` ルーブリックを追加する。

2. **採点の形骸化**: 単純すぎる `contains`（例: `"the"` を含む）はあらゆる応答で合格。
   修正方法: 正しく整形された出力にしか現れないスキル固有の構造マーカーを使う。

3. **1回の実行での結論**: LLM（大規模言語モデル）の出力は確率的。1回は「シグナル」。
   修正方法: 3回以上実行して mean/stddev を確認してから判断する。

4. **evals ディレクトリ未コミット**: テストケースを失うと再現性が壊れる。
   修正方法: `evals/<skill_id>/evals.json` をコミット。`runs/` と `viewer.html` は `.gitignore` に追加。

5. **`innerHTML` への変数埋め込みでエスケープしていない**
   修正方法: 可能なら `textContent` を使う。`innerHTML` が必要な場合は、埋め込む全変数を `escHtml()` で必ずエスケープする。

---

## 事前チェックリスト

- [ ] テスト対象スキルの SKILL.md が `skills/<skill_id>/SKILL.md` に存在する
- [ ] `evals/<skill_id>/evals.json` が有効な JSON で ≥3 テストケースある
- [ ] 各テストケースに ≥1 の `llm_grade` アサーションがある
- [ ] `skills-validate-skill` がテスト対象スキルで PASS している
- [ ] Python 3.10+ が使用可能（`python --version` で確認）
- [ ] ビューア実装のセルフチェック: `innerHTML` へ変数を埋め込む箇所は全変数を `escHtml()` 済み、または `textContent` を使用している

---

## クイックリファレンス

```
ステップ1: evals.json 設計（≥3ケース、llm_grade を含める）
ステップ2: runner.md → スキルあり + ベースラインの並列実行
ステップ3: aggregate_benchmark.py → benchmark_summary.json
ステップ4: generate_viewer.py → viewer.html（ブラウザで開く）
ステップ5: analyzer.md → feedback.json（KPT + next_action）
ステップ6: next_action に従って行動（accept / revise / ケース追加）
```

---

## リソース

- `references/schemas.md` — 全データファイルの JSON 契約
- `agents/runner.md` — スキルあり + ベースライン実行プロトコル
- `agents/grader.md` — アサーション評価 + スコアリング計算式
- `agents/analyzer.md` — ベンチマークデータから KPT フィードバック生成
