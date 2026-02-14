---
name: github-pr-workflow
description: ブランチからマージまでのPR運用ガイド。GitHub Flow標準化に使う。
author: RyoMurakami1983
tags: [github, pull-requests, workflow, git, collaboration]
invocable: false
version: 1.0.0
---

# GitHub PR Workflow

再現可能なPRワークフロー：ブランチ作成、push、レビュー、マージ、main同期を安全に行います。

**Pull Request (PR)**: GitHub上でレビューする変更提案。
**Branch Protection**: 直接pushや未承認マージを防ぐルール。
**Continuous Integration (CI)**: PRに対する自動チェック。

## このスキルを使うとき

以下の状況で活用してください：
- 複数リポジトリ・チーム間でPRフローを統一し、共有オーナーシップを確立したい
- タイトル・本文・Issue連携を標準化し、追跡性を確保したい
- mainへのマージ前にレビューとCI（継続的インテグレーション）チェックを必須化したい
- マージ時にIssueを自動クローズし、計画ボードを最新に保ちたい
- レビュアーがマージした後にローカルmainを同期し、古い履歴での作業を避けたい
- hotfixを保護ルールや必須承認を迂回せずに運用したい

## 関連スキル

- **`git-commit-practices`** - コミット形式と原子的コミット
- **`git-initial-setup`** - ブランチ保護の初期設定
- **`github-issue-intake`** - Issue作成とトリアージ

---

## 依存関係

- Git 2.30+
- GitHubリポジトリ権限
- GitHub CLI (gh)（CLIワークフロー用、任意）

---

## コア原則

1. **ブランチ優先** (基礎と型) - mainはレビュー済みのみ。ブランチ優先パターンがすべてのPRの基盤
2. **追跡性** (成長の複利) - PRとIssueを紐付け、将来の開発者が変更理由を学べるようにする
3. **レビューゲート** (ニュートラル) - 承認とCIチェックで偏りのない品質基準でmainを守る
4. **mainを清潔に** (継続は力) - 検証済みの変更のみマージ。着実な規律がコードベースを健全に保つ
5. **即座に同期** (温故知新) - マージ後にローカルmainを更新し、最新の共有履歴の上に構築する

---

## ワークフロー: プルリクエストで出荷する

### Step 1: 状態を検知してルーティングする

作業開始前に、現在のgit状態を確認し、適切なアクションを取ります。

```bash
# 1. 現在のブランチを確認
git branch --show-current

# 2. 未コミットの変更を確認
git status --short

# 3. 未pushのコミットを確認
git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null

# 4. 既存PRの確認
gh pr list --head $(git branch --show-current) --state open
```

| 状態 | アクション |
|------|-----------|
| mainブランチにいる | まず feature branch を作成（Step 2） |
| 未コミットの変更あり | `git-commit-practices` に委譲してコミット後、ここに戻る |
| コミット済・未push | `git push -u origin BRANCH` してから Step 3 へ |
| push済・PR未作成 | Step 3（PR作成）へ進む |
| PR既存 | PRステータスとURLを報告 |

> **重要**: 未コミットの変更がある場合は `git-commit-practices` ワークフローに委譲してください（先にコミット、その後戻る）。mainにいる場合は、コミット前に必ず feature branch を作成してください。

「プルリクして」「PR作成して」等のPR関連リクエスト時に使用します。

> **Values**: 基礎と型 / 継続は力

### Step 2: フィーチャーブランチの作成

作業開始前に最新のmainからブランチを作成します。追跡性のためにIssue番号付きの説明的プレフィックス（`feature/`、`fix/`、`docs/`）を使用します。

```bash
git checkout main
git pull --ff-only
git checkout -b feature/issue-123
git push -u origin feature/issue-123
```

複数の開発者が同じリポジトリで共同作業する場合や、ブランチ保護がmainへの直接pushをブロックしている場合に使用します。

### Step 3: 明確な文脈でPRを作成

アクション指向のタイトルと、レビュアーに全体像を伝える本文でPRを作成します。Summary、Why、Testing、関連Issueを含めます。

```bash
gh pr create --title "feat: 支払い画面を改善" --body "## Summary
Redesigned payment form layout.

## Why
Current layout causes 15% drop-off at checkout.

## Testing
Manual test on staging.

## Related
Closes #123"
```

レビュアーが素早く文脈を把握する必要がある場合や、チーム全体でPR内容を統一したい場合に使用します。

### Step 4: レビューとCIゲートを通過

マージ前に承認とCIチェックの通過を必須化します。ブランチ保護でこれらのゲートを自動的に強制します。

```yaml
# .github/workflows/ci.yml
name: ci
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test
```

mainを常にデプロイ可能に保つ必要がある場合や、監査対応のレビュー証跡が必要な場合に使用します。

### Step 5: クローズキーワードでIssueを連携

PR本文にクローズキーワードを追加し、マージ時にIssueを自動クローズします。解決済みには`Closes`、関連文脈には`Refs`を使用します。

```markdown
## Related
Closes #123
Refs #130
```

Issue起点の作業で、Issueからマージ済みコードまでのエンドツーエンドの追跡性が必要な場合に使用します。

### Step 6: マージ戦略を選択

リポジトリポリシーに合ったマージ戦略を選択します。

| 戦略 | 使う場面 | 結果 |
|------|---------|------|
| Squash | 小さなPR | 1コミット化 |
| Merge | 履歴保持 | 全コミット保持 |
| Rebase | 直線履歴 | マージコミットなし |

一貫した履歴パターンが必要な場合や、コンプライアンスで特定のマージ方式が求められる場合に使用します。

### Step 7: 同期と整理

マージ後にローカルmainを同期し、マージ済みブランチを削除してワークスペースを整理します。

```bash
git checkout main
git pull --ff-only
git branch -d feature/issue-123
git push origin --delete feature/issue-123
```

古い履歴での作業を避けるため、PRマージ後に毎回実行します。

### Step 8: Hotfix対応

緊急の本番修正にはhotfixブランチを作成します。通常のPRプロセスに従い、ブランチ保護を決して迂回しません。

```bash
git checkout main
git pull --ff-only
git checkout -b hotfix/issue-999
# 修正、コミット、pushし、通常通りPRを作成
git push -u origin hotfix/issue-999
```

本番がダウンしているがブランチ保護を維持する必要がある場合に使用します。

---

## ベストプラクティス

- アクション指向のPRタイトルで素早く内容を把握
- PRテンプレートでテスト結果の記載を必須化
- クローズキーワードでIssueを最新に保つ
- 承認またはCIなしのマージを避ける
- マージ後に毎回ローカルmainを同期

---

## よくある落とし穴

1. **CIチェックのスキップ**
   修正: ブランチ保護でCIを必須化する。

2. **レビューなしでマージ**
   修正: 承認とコードオーナーを必須化する。

3. **main同期の忘れ**
   修正: マージ後に`--ff-only`でmainをpullする。

---

## アンチパターン

- ブランチ保護なしでmainへ直接push
- 失敗したチェックのままマージ
- マージ済みブランチの放置

---

## クイックリファレンス

### PRフローチェックリスト

- [ ] 状態を検知（未コミット / 未push / PR無し）
- [ ] 必要なら `git-commit-practices` でコミット
- [ ] ブランチをoriginにpush
- [ ] PRを作成し `Closes #` キーワードを追加
- [ ] CIと承認を通過
- [ ] ポリシーに従いマージ
- [ ] mainをpullしブランチを削除

### マージ判断テーブル

| 状況 | マージ方式 | 理由 |
|------|-----------|------|
| 小さな機能 | Squash | ノイズ削減 |
| リリースブランチ | Merge | コミット保持 |
| 線形履歴が必須 | Rebase | マージコミット回避 |

---

## FAQ

**Q: すべてのPRでIssueをクローズすべき？**
A: Issue起点の作業ならクローズキーワードを使用します。

**Q: CIが失敗していてもマージできる？**
A: できません。CIを修正するか例外を記録してください。

**Q: ブランチはいつ削除する？**
A: マージ後に削除してリモートを整理します。

---

## リソース

- https://docs.github.com/en/pull-requests
- https://cli.github.com/manual/gh_pr_create
