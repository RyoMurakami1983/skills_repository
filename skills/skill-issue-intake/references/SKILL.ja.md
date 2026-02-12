---
name: skill-issue-intake
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

- **`skill-git-commit-practices`** - コミット運用と実践
- **`skill-github-pr-workflow`** - PR運用とマージ方針
- **`skill-git-review-standards`** - レビュー標準とPRサイズ
- **`skill-git-initial-setup`** - リポジトリ初期保護
- **`skill-revision-guide`** - 変更管理と履歴整理
- **`skill-quality-validation`** - ドキュメント品質検証

---

## 依存関係

- GitHubアカウント（リポジトリ権限）
- GitHub CLI (gh)（CLI作成時）
- チームのラベル/優先度規約

---

## コア原則

1. **行動可能性** - 次にやるべきことが明確（基礎と型）
2. **スコープ分離** - 今やる/後でやるを分ける
3. **トレーサビリティ** - IssueとPRを必ず紐付け（成長の複利）
4. **一貫性** - ラベルとテンプレを統一
5. **低摩擦** - 早く記録して忘れない（継続は力）

---

## パターン1: 今直すかIssue化するか判断

### 概要

今修正するか、Issueとして記録するかを判断します。

### 基本例

| 質問 | Yes | No |
|------|-----|----|
| リリースを止めるか | 今直す | Issue化 |
| 設計議論が必要か | Issue化 | 今直す |
| 30分以上かかるか | Issue化 | 今直す |

```text
# ✅ CORRECT - スコープ外はIssue化
Issue: "Bug: CSV import fails on UTF-8 BOM"
Scope: 現PRでは不要
Action: Issueを作成して続行

# ❌ WRONG - TODOで埋める
// TODO: fix later
```

### 中級例

- 30分のタイムボックスを設定
- 超えたらIssue化して続行

### 上級例

| 影響度 | 工数 | 判断 |
|--------|------|------|
| 高 | 高 | Issue化 + スケジュール |
| 高 | 低 | 今直す |
| 低 | 高 | Issue化 |

### 使うとき

- PR中にスコープ外の問題を見つけた
- 修正がリリースを遅らせる可能性がある

**Why**: スコープを分けるとPRが安定する。

---

## パターン2: Issueタイトルと本文テンプレ

### 概要

検索しやすく実行可能なIssueを作るため、タイトルと本文を標準化します。

### 基本例

```markdown
# ✅ CORRECT - 明確なタイトル
Title: "Bug: CSV import fails on UTF-8 BOM"

# ❌ WRONG - あいまい
Title: "Bug"
```

### 中級例

```markdown
## Summary
## Steps to Reproduce
## Expected Result
## Actual Result
## Impact
```

### 上級例

```markdown
## Acceptance Criteria
- [ ] Repro steps documented
- [ ] Fix implemented
- [ ] Tests added
```

```yaml
# .github/ISSUE_TEMPLATE/bug.yml
name: Bug Report
description: Report a reproducible bug
body:
  - type: textarea
    id: repro
    attributes:
      label: Steps to Reproduce
      required: true
```

**Why**: 統一テンプレで確認コストを減らす。

---

## パターン3: ラベルと優先度トリアージ

### 概要

ラベルと優先度を揃えて、キューを整理します。

### 基本例

```yaml
# ✅ CORRECT
labels: [bug, priority/P1, area/import]

# ❌ WRONG
labels: []
```

### 中級例

| 優先度 | 意味 | 目安 |
|--------|------|------|
| P0 | 本番停止 | 当日 |
| P1 | 重大影響 | 1-3日 |
| P2 | 標準バグ | 1-2スプリント |
| P3 | 軽微 | バックログ |

### 上級例

- `type/bug`, `type/debt`, `type/feature` を追加
- `status/triage`, `status/ready`, `status/blocked` を追加

**Why**: 優先度が揃うと計画が立てやすい。

---

## パターン4: 再現手順と証拠

### 概要

次の担当者がすぐ修正できるよう再現手順と証拠を残します。

### 基本例

```markdown
## Steps to Reproduce
1. Upload CSV with UTF-8 BOM
2. Click Import
3. Observe error in UI

## Expected
Import succeeds

## Actual
"Invalid encoding" error
```

### 中級例

- ログやスクリーンショットを添付
- リクエストIDを記載

### 上級例

```text
Log: 2026-02-12T12:03:11Z ERROR import failed (BOM detected)
```

**Why**: 再現性が高いほど修正が早い。

---

## パターン5: GitHub CLIでIssue作成

### 概要

GitHub CLI (command-line interface, CLI)で素早くIssueを作成します。

### 基本例

```bash
# ✅ CORRECT
gh issue create --title "Bug: CSV import fails on UTF-8 BOM" --body "See repro steps"
```

### 中級例

```bash
gh issue create \
  --title "Bug: CSV import fails on UTF-8 BOM" \
  --body-file issue.md \
  --label bug,priority/P1,area/import \
  --assignee @me
```

Why: ラベルと担当を明確にしてトリアージを早める。

### 上級例

```python
# ✅ CORRECT - Issue本文を自動生成
import textwrap
from pathlib import Path

body = textwrap.dedent("""\
## Summary
CSV import fails on UTF-8 BOM.

## Steps to Reproduce
1. Upload CSV with UTF-8 BOM
2. Click Import

## Expected
Import succeeds

## Actual
"Invalid encoding" error
""")

try:
    Path("issue.md").write_text(body, encoding="utf-8")
except OSError as exc:
    raise SystemExit(f"Failed to write issue body: {exc}")
```

```csharp
// ✅ CORRECT - Issueテンプレートサービスを登録
using Microsoft.Extensions.DependencyInjection;

services.AddSingleton<IssueTemplateService>();
```

**Why**: 自動化で漏れを減らし、テンプレを統一する。

---

## パターン6: GitHub Web UIでIssue作成

### 概要

GUIで素早く整理したい場合はWeb UIを使います。

### 基本例

1. リポジトリ → Issues → New issue
2. テンプレを選択
3. 必須項目を埋めて送信

### 中級例

- ラベルとマイルストーンを追加
- 担当者を割り当てる

### 上級例

- PRコメントからIssue参照を作る
- Projectボードにリンクする

**Why**: UIは文脈のある情報に向く。

---

## パターン7: IssueとPRの連携・クローズ

### 概要

PRにクローズキーワードを入れて自動クローズします。

### 基本例

```markdown
## Related
Closes #123
```

### 中級例

```markdown
## Related
Closes #123
Refs #130
```

### 上級例

```markdown
## Related
Fixes owner/repo#123
Relates-to owner/repo#130
```

### 使うとき

- PRでIssueを直接解決する場合
- リポジトリ間の追跡性が必要

**Why**: 自動クローズでバックログを正確に保つ。

---

## ベストプラクティス

- タイトルは動詞で開始（Fix, Add, Remove）
- 1 Issue = 1 問題に絞る
- 影響度と優先度を先に付ける
- 再現手順か証拠を必ず記載
- PRにクローズキーワードを入れる
テンプレを使い、ラベル付け後に担当を割り当てる。

---

## よくある落とし穴

- "Bug"のような曖昧なタイトル
- 再現手順がない断続的障害
- 1つのIssueに複数問題を混在

Fix: テンプレを使いスコープを分割する。 
Fix: 再現手順か証拠リンクを追加する。 
Fix: ラベルを付けてから担当を割り当てる。

---

## アンチパターン

- TODOコメントでIssueを作らない
- 次のアクションがないIssueを作る
- 解決内容を残さずIssueを閉じる

---

## FAQ

**Q: いつIssue化すべき？**  
A: タイムボックスを超える場合やスコープ外ならIssue化。

**Q: 必須ラベルは？**  
A: 最低限、typeとpriorityを付ける。

**Q: PRからIssueを作れる？**  
A: 可能。PR本文にクローズキーワードを入れる。

---

## クイックリファレンス

| 手順 | アクション | 結果 |
|------|------------|------|
| 1 | 今直すか判断 | スコープ確定 |
| 2 | テンプレ適用 | 明確な本文 |
| 3 | ラベル付与 | 優先度が可視化 |
| 4 | PR連携 | マージで自動クローズ |

```bash
# CLIで即作成
gh issue create --title "Bug: ..." --body-file issue.md
```

---

## リソース

- [About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues)
- [Closing issues with keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)
- [GitHub CLI issue create](https://cli.github.com/manual/gh_issue_create)

---

## 変更履歴

### Version 1.0.0 (2026-02-12)
- 初版リリース
- 判断、テンプレ、ラベル、PR連携のパターン
- CLI/GUIのIssue作成手順
