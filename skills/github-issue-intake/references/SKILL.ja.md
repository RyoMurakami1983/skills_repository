---
name: github-issue-intake
description: スコープ外作業をIssueとして記録するためのガイド。判断と作成手順に使う。
author: RyoMurakami1983
tags: [github, issues, triage, workflow, documentation]
invocable: false
version: 1.0.0
---

# Issueインテーク

スコープ外のバグや改善を、再現可能で追跡可能なGitHub Issueとして記録します。

## このスキルを使うとき

以下の状況で活用してください：
- Pull Request (PR)レビュー中に見つけたバグを切り分けたい
- 今すぐ対応しない修正をスプリント後に回したい
- Issueのタイトル、ラベル、優先度を標準化したい
- 断続的な障害の再現手順を記録したい
- サポート依頼を開発タスクとして追跡したい
- フォローアップ作業を別担当に引き渡したい

## 関連スキル

- **`git-commit-practices`** - コミット運用と実践
- **`github-pr-workflow`** - PR運用とマージ方針
- **`git-initial-setup`** - リポジトリ初期保護
- **`skills-revise-skill`** - 変更管理と履歴整理
- **`skills-validate-skill`** - ドキュメント品質検証

---

## 依存関係

- GitHubアカウント（リポジトリ権限）
- GitHub CLI (gh)（CLI作成時）
- チームのラベル/優先度規約

---

## コア原則

1. **行動可能性** - すべてのIssueに明確な次のステップを含める（基礎と型）
2. **スコープ分離** - 今の作業をブロックせずに後続作業を追跡する（ニュートラル）
3. **トレーサビリティ** - IssueをPRと証拠に紐付ける（成長の複利）
4. **一貫性** - 標準ラベル・優先度・テンプレートを使う（温故知新）
5. **低摩擦** - 素早く記録して忘れない（継続は力）

---

## ワークフロー: 先送りした作業をIssueとして記録する

### Step 1: 今直すかIssue化するか判断

インラインで修正するか先送りするかを判断します。影響度・工数・スコープ関連性に基づくシンプルな判断マトリクスを使います。スコープ外または30分のタイムボックスを超える場合はIssue化します。

```text
# ✅ CORRECT - スコープ外はIssue化
Issue: "Bug: CSV import fails on UTF-8 BOM"
Scope: 現PRでは不要
Action: Issueを作成して続行

# ❌ WRONG - TODOで埋める
// TODO: fix later
```

**いつ**: PR中にスコープクリープを発見した場合、または修正が現リリースを遅延させるリスクがある場合。

### Step 2: タイトルと本文を書く

型プレフィックス付きの明確で検索しやすいタイトルと、構造化された本文を書きます。良いタイトルは `Bug:`、`Feature:`、`Chore:` で始まり、具体的な説明が続きます。テンプレート本文にはSummary、Steps to Reproduce、Expected/Actual Result、Impactのセクションを含めます。

```markdown
Title: "Bug: CSV import fails on UTF-8 BOM"

## Summary
CSV import rejects files with UTF-8 BOM encoding.

## Steps to Reproduce
1. Upload CSV with UTF-8 BOM
2. Click Import

## Expected Result
Import succeeds.

## Actual Result
"Invalid encoding" error displayed.

## Impact
Blocks users with Excel-exported CSVs.
```

**いつ**: すべての新規Issue — 小さなバグでもテンプレートを省略しない。

### Step 3: ラベルと優先度を付与

バックログをソート可能にするため、種別・優先度・領域のラベルを付与します。最低限、すべてのIssueに種別ラベルと優先度ラベルが必要です。

| 優先度 | 意味 | SLA |
|--------|------|-----|
| P0 | 本番停止 | 当日 |
| P1 | 重大影響 | 1–3日 |
| P2 | 標準バグ | 1–2スプリント |
| P3 | 軽微/整理 | バックログ |

```yaml
# ✅ CORRECT
labels: [bug, priority/P1, area/import]

# ❌ WRONG
labels: []
```

**いつ**: トリアージミーティング前、または別メンバーへの引き渡し時。

### Step 4: 再現手順と証拠を追加

番号付きの再現手順、期待結果と実際の結果、裏付け証拠（ログ、スクリーンショット、リクエストID）を含めます。次の担当者がフォローアップの質問なしで問題を再現できるようにします。

```markdown
## Steps to Reproduce
1. Upload CSV with UTF-8 BOM
2. Click Import
3. Observe error in UI

## Expected
Import succeeds

## Actual
"Invalid encoding" error

## Evidence
Log: 2026-02-12T12:03:11Z ERROR import failed (BOM detected)
```

**いつ**: バグの場合は常に。機能の場合はユーザーシナリオのコンテキストを代わりに含める。

### Step 5: CLIでIssueを作成

`gh issue create` を使い、ターミナルから素早く反復可能なIssue作成を行います。ラベル、担当者、本文ファイルを1コマンドで指定します。

```bash
gh issue create \
  --title "Bug: CSV import fails on UTF-8 BOM" \
  --body-file issue.md \
  --label bug,priority/P1,area/import \
  --assignee @me
```

**いつ**: ターミナルで作業中で、フォーマットより速度を重視する場合。

### Step 6: Web UIでIssueを作成

ドラッグ＆ドロップのスクリーンショット、リッチMarkdownプレビュー、テンプレート選択が必要な場合はGitHub Web UIを使います。Issues → New issue に移動し、テンプレートを選択、必須項目を入力、ラベルとマイルストーンを追加してから送信します。

```text
1. リポジトリ → Issues → New issue を開く
2. テンプレートを選択（例: Bug Report）
3. 必須項目を入力し、スクリーンショットを添付
4. ラベル、マイルストーン、担当者を追加
5. 送信
```

**いつ**: 埋め込み画像、複雑なフォーマット、またはブラウザからのトリアージが必要な場合。

### Step 7: IssueをPRにリンク

PR説明文にクローズキーワードを使ってIssueを参照し、マージ時に自動クローズさせます。直接修正には `Closes #N`、関連コンテキストには `Refs #N` を使います。

```markdown
## Related
Closes #123
Refs #130
```

クロスリポジトリ参照には完全な `owner/repo#N` 構文を使います：

```markdown
Fixes owner/repo#123
```

**いつ**: 追跡対象のIssueを解決または関連するすべてのPR。

---

## ベストプラクティス

- タイトルは動詞で開始（Fix, Add, Remove）
- 1 Issue = 1 問題に絞る
- トリアージミーティング前に影響度と優先度を付ける
- 可能な限り再現手順か証拠を記載
- PRにクローズキーワードを入れる
- テンプレートを使い、ラベル付け後に担当を割り当てる

---

## よくある落とし穴

- "Bug" や "Fix later" のような曖昧なタイトル
- 断続的障害で再現手順を省略する
- 1つのIssueに複数の問題を混在させる

Fix: 標準テンプレートを使い、スコープ別にIssueを分割する。
Fix: 再現手順か証拠リンクを必ず追加する。
Fix: 担当を割り当てる前にラベルを付ける。

---

## アンチパターン

- TODOコメントでIssueを作らない
- 明確な次のアクションがないIssueを作る
- 解決内容を記録せずIssueを閉じる

---

## FAQ

**Q: 今直すかIssue化するか、いつ判断すべき？**
A: 修正がスコープ外、またはタイムボックスを超える場合はIssue化する。

**Q: 必須ラベルは？**
A: 最低限、種別（type）と優先度（priority）ラベルを付ける。

**Q: PRからIssueを作成できる？**
A: 可能。PR本文でIssueを参照し、クローズキーワードを使う。

---

## クイックリファレンス

| Step | アクション | 結果 |
|------|------------|------|
| 1 | 今直すかIssue化か判断 | 判断を記録 |
| 2 | タイトルと本文を作成 | 検索可能なIssue |
| 3 | ラベルと優先度を付与 | ソート可能なバックログ |
| 4 | 再現手順と証拠を追加 | 再現可能なレポート |
| 5 | CLIで作成 | 高速ターミナルワークフロー |
| 6 | Web UIで作成 | リッチフォーマットのIssue |
| 7 | PRにリンク | マージで自動クローズ |

```bash
# CLIで即作成
gh issue create --title "Bug: ..." --body-file issue.md --label bug,priority/P1
```

---

## リソース

- [About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues)
- [Closing issues with keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)
- [GitHub CLI issue create](https://cli.github.com/manual/gh_issue_create)

---

## 変更履歴

### Version 2.0.0 (2026-02-12)
- 7パターン形式からStep 1–7の単一ワークフローに移行
- 例を圧縮：各ステップにベストな例を1つ
- コア原則に日本語Valuesタグを追加

### Version 1.0.0 (2026-02-12)
- 初版リリース
- 判断、テンプレ、ラベル、PR連携のパターン
- CLI/GUIのIssue作成手順
