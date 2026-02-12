---
name: skill-github-pr-workflow
description: ブランチからマージまでのPR運用ガイド。GitHub Flow標準化に使う。
author: RyoMurakami1983
tags: [github, pull-requests, workflow, git, collaboration]
invocable: false
version: 1.0.0
---

# GitHub PR運用フロー

ブランチ作成からPR、レビュー、マージ、main同期までを標準化します。

**Pull Request (PR)**: GitHub上でレビューする変更提案。
**Branch Protection**: 直接pushや未承認マージを防ぐルール。
**Continuous Integration (CI)**: PRに対する自動チェック。

Progression: Simple → Intermediate → Advanced で段階的に強化します。
Reason: 段階的な強化でmain保護の漏れを防ぎます。

## このスキルを使うとき

以下の状況で活用してください：
- リポジトリ間でPRフローを統一したい
- タイトル/本文/Issue連携を標準化したい
- 継続的インテグレーション（CI）を必須化したい
- マージ時にIssueを自動クローズしたい
- 他者がマージした後にmainを同期したい
- hotfixを保護ルールを保ったまま運用したい

## 関連スキル

- **`skill-git-commit-practices`** - コミット形式と原子的コミット
- **`skill-git-review-standards`** - レビュー品質とPRサイズ
- **`skill-git-initial-setup`** - ブランチ保護の初期設定
- **`skill-issue-intake`** - Issue作成とトリアージ

---

## 依存関係

- Git 2.30+
- GitHubリポジトリ権限
- GitHub CLI (gh)（任意）

---

## コア原則

1. **ブランチ優先** - mainはレビュー済みのみ
2. **追跡性** - PRとIssueを紐付ける
3. **レビューゲート** - 承認とCIで守る
4. **mainを清潔に** - 失敗変更を入れない
5. **同期を習慣化** - マージ後にmainを更新

---

## パターン1: ブランチ作成とpush

### 概要

mainから分岐してブランチをpushします。

### 基本例

```bash
# ✅ CORRECT
git checkout main
git pull --ff-only
git checkout -b feature/issue-123
git push -u origin feature/issue-123

# ❌ WRONG
git checkout main
git push origin main
```

### 中級例

- `feature/`, `fix/`, `docs/` を使う
- ブランチ名にIssue番号を入れる

### 上級例

- 事前にmain保護ルールを設定する

### 使うとき

- PR運用を再現可能にしたい
- チームで同時開発する

---

## パターン2: PR作成と文脈の明確化

### 概要

明確なタイトルと本文でPRを作成します。

### 基本例

```bash
# ✅ CORRECT
gh pr create --title "feat: 支払い画面を改善" --body "Closes #123"

# ❌ WRONG
gh pr create --title "update" --body ""
```

### 中級例

```markdown
## Summary
## Why
## Testing
## Related
Closes #123

Why: レビュアーの文脈を揃えるため。
```

### 上級例

```bash
# 失敗時に中断
if ! gh pr create --title "feat: 支払い画面を改善" --body "Closes #123"; then
  echo "PR creation failed"; exit 1
fi
```

### 使うとき

- PRの文脈を素早く伝えたい
- レビュー時間を短縮したい

---

## パターン3: レビューゲートとCIチェック

### 概要

レビュー承認とCIを必須化します。

### 基本例

CI設定ファイル（configuration）の例:

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

### 中級例

- 1〜2名の承認を必須化
- 会話解決を必須化

### 上級例

```csharp
// ✅ CORRECT - PRゲート登録
using Microsoft.Extensions.DependencyInjection;

services.AddSingleton<PullRequestGate>();
```

### 使うとき

- mainを常にデプロイ可能に保つ
- 監査対応が必要

---

## パターン4: Issueクローズのキーワード

### 概要

クローズキーワードでIssueを自動クローズします。

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

Why: Issue追跡をPR本文で見える化するため。
```

### 上級例

```markdown
## Related
Fixes owner/repo#123
Relates-to owner/repo#130
```

### 使うとき

- Issue起点の作業
- 追跡性が必要

---

## パターン5: マージ戦略の選択

### 概要

ポリシーに応じてマージ方法を選びます。

### 基本例

| 戦略 | 使う場面 | 結果 |
|------|---------|------|
| Squash | 小さなPR | 1コミット化 |
| Merge | 履歴保持 | マージコミット |
| Rebase | 直線履歴 | マージなし |

### 中級例

- 機能PRはsquash
- リリース系はmerge

### 上級例

- ブランチ保護で線形履歴を必須化

### 使うとき

- 履歴ポリシーが明確なとき
- 監査やリリースで一貫性が必要

---

## パターン6: マージ後の同期と整理

### 概要

マージ後にmainを同期し、ブランチを整理します。

### 基本例

```bash
# ✅ CORRECT
git checkout main
git pull --ff-only
git branch -d feature/issue-123

# ❌ WRONG
git checkout main
git pull
```

### 中級例

```bash
# リモートブランチ削除
git push origin --delete feature/issue-123
```

### 上級例

- 変更履歴やリリースノートを更新

### 使うとき

- 他者がPRをマージした後
- ローカルmainを最新に保つ

---

## パターン7: Hotfix運用

### 概要

緊急対応でも保護を崩さず運用します。

### 基本例

```bash
# ✅ CORRECT
git checkout -b hotfix/issue-999
```

### 中級例

```bash
# Cherry-pickで適用
git cherry-pick <commit>
```

### 上級例

```python
# ✅ CORRECT - hotfix証跡を保存
from pathlib import Path

Path("hotfix.txt").write_text("hotfix applied", encoding="utf-8")
```

### 使うとき

- 本番障害の即時対応
- main保護を維持したい

---

## ベストプラクティス

- Use: PRタイトルを動詞で始める
- Define: テスト結果を必ず書く
- Apply: Issueクローズキーワードを使う
- Avoid: 承認/CIなしのマージ
- Consider: マージ後にmainをpullする

---

## よくある落とし穴

1. **CIを無視する**  
Fix: ブランチ保護で必須化する。

2. **レビューなしでマージ**  
Fix: 承認を必須化する。

3. **main同期の忘れ**  
Fix: マージ後にpullする。

---

## アンチパターン

- main保護アーキテクチャを無視した直接push
- 失敗したCIのままマージ
- マージ済みブランチの放置

---

## クイックリファレンス

### PRフローチェック

- [ ] mainから分岐
- [ ] ブランチをpushしてPR作成
- [ ] `Closes #` を追加
- [ ] CIと承認を通過
- [ ] ポリシー通りにマージ
- [ ] マージ後にmainをpull

### マージ判断テーブル

| 状況 | マージ方式 | Decision |
|------|-----------|----------|
| 小さなPR | Squash | Decision: ノイズ削減 |
| リリース系 | Merge | Decision: 履歴保持 |
| 線形必須 | Rebase | Decision: 直線化 |

---

## FAQ

**Q: すべてのPRでIssueをクローズする？**  
A: Issue起点ならクローズキーワードを入れます。

**Q: CIが失敗していてもマージできる？**  
A: できません。修正か例外の記録が必要です。

**Q: ブランチ削除はいつ？**  
A: マージ後に削除して整理します。

---

## リソース

- https://docs.github.com/en/pull-requests
- https://cli.github.com/manual/gh_pr_create
