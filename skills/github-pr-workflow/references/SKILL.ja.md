---
name: github-pr-workflow
description: "Use when リポジトリ状態からPRを作成し、Issue連携まで安全に進めたいとき。"
metadata:
  author: RyoMurakami1983
  tags: [github, pull-requests, workflow, git, pr-create]
  invocable: false
  tool_versions:
    git: ">=2.30"
    gh: ">=2.0"
  last_reviewed: "2026-03-01"
---

# GitHub PR Workflow

状態検知からPR作成・Issueクローズまでを自動化するワークフロー。

**Pull Request (PR)**: GitHub上でレビューする変更提案。

先に状態を検知してください。PRは必ず feature branch から作成してください。複数行本文は `--body-file` を使ってください。

## このスキルを使うとき

以下の状況で活用してください：
- feature branch の作業がレビュー準備完了になり、PRを作成するとき
- 未コミット・未push の変更をPR作成前にルーティングするとき
- `Closes #N` や `Refs #N` で Issue 連携しながらPRを作成するとき
- `gh pr create` 前にブランチ状態と認証状態を確認するとき
- マージ判断を自動化せず、レビュー待ちへ安全に引き渡すとき

> **スコープ**: このスキルは状態検知からPR作成・Issue連携・低消費なレビュー待機への受け渡しまでを扱います。詳細なレビュー対応・マージ戦略・マージ後同期はスコープ外です。

## 関連スキル

- **`git-commit-practices`** - コミット形式と原子的コミット（Step 1から委譲）
- **`git-initial-setup`** - ブランチ保護の初期設定
- **`github-issue-intake`** - Issue作成とトリアージ

---

## 依存関係

- Git 2.30+
- GitHub CLI (`gh`) — `gh auth status` で事前確認
- GitHubリポジトリへのpush権限

---

## コア原則

1. **ブランチ優先** (基礎と型) - mainはレビュー済みのみ
2. **追跡性** (成長の複利) - PRとIssueを紐付け、将来の開発者が変更理由を学べるように
3. **日本語PR本文** (ニュートラル) - チーム標準としてPR本文を日本語で記述
4. **mainを清潔に** (継続は力) - 検証済みの変更のみmainに到達させる
5. **状態駆動** (温故知新) - 現在の状態を検知し、適切なアクションにルーティング
6. **イベント駆動で待つ** (余白の設計) - 同じPRを何度も見に行かず、レビューのシグナルを待つ

---

## 判断テーブル

次の一手をひと目で決めるためのテーブルです。

| 現在の状態 | 次のアクション | 理由 |
|---|---|---|
| `main` にいる | 先に feature branch を作る | default branch にレビュー前の作業を置かないため |
| 未コミット変更あり | PR前にコミットする | 追跡可能な状態を保つため |
| ローカルコミットのみ | 先に push する | `gh pr create` にはリモートブランチが必要なため |
| PR未作成 | PRを作成する | レビューフローとIssue連携を開くため |
| PR既存 | 状態を報告して止まる | 重複PRを防ぐため |

---

## ワークフロー: プルリクエストで出荷する

### Step 1: 状態を検知してルーティングする

現在のgit状態を確認し、適切なアクションを取ります。

```bash
# 1. 現在のブランチを確認
BRANCH=$(git branch --show-current)

# 2. 未コミットの変更を確認
git status --short

# 3. 未pushのコミットを確認
git log "origin/${BRANCH}..HEAD" --oneline 2>/dev/null

# 4. 既存PRの確認
gh pr list --head "$BRANCH" --state open
```

```powershell
# PowerShell版
$Branch = git branch --show-current

git status --short

git log "origin/$Branch..HEAD" --oneline 2>$null

gh pr list --head $Branch --state open
```

| 状態 | アクション |
|------|-----------|
| mainブランチにいる | feature branch を作成（Step 2） |
| 未コミットの変更あり | `git-commit-practices` に委譲してコミット後、戻る |
| コミット済・未push | `git push -u origin BRANCH` してから Step 3 へ |
| push済・PR未作成 | Step 3（PR作成）へ進む |
| PR既存 | PRステータスとURLを報告 |

> **重要**: 未コミットの変更がある場合は `git-commit-practices` ワークフローに委譲してください（先にコミット、その後戻る）。mainにいる場合は、コミット前に必ず feature branch を作成してください。

「プルリクして」「PR作成して」等のPR関連リクエスト時に使用します。Why: 状態検知を先に行うと、誤った分岐や重複PR作成を防げます。

> **Values**: 基礎と型 / 継続は力

### Step 2: フィーチャーブランチの作成

最新のmainからブランチを作成します。追跡性のためにIssue番号付きの説明的プレフィックス（`feature/`、`fix/`、`docs/`）を使用します。

```bash
# ブランチ作成前に認証確認（push失敗を防ぐ）
gh auth status
git switch main
git pull --ff-only
git switch -c feature/issue-123
git push -u origin feature/issue-123
```

新しい作業を開始するとき、または Step 1 で main にいることが検知された場合に使用します。Why: 先にブランチを切ると、その後のコミット履歴がきれいに保てます。

> **Values**: 基礎と型

### Step 3: PR作成とIssue連携

日本語の本文でPRを作成します。`Closes` でマージ時にIssueを自動クローズします。

**インライン本文**（短いPR向け）:

```bash
gh pr create \
  --title "feat: 支払い画面にフィルタを追加" \
  --body "## 概要
注文履歴画面に検索フィルタを追加。

## 理由
サポートから検索要求が多く、対応工数を削減するため。

## テスト
ローカルで動作確認済み。

## 関連
Closes #123
Refs #130"
```

**ファイル経由の本文**（Windowsでの UTF-8 安全推奨）:

```bash
# 本文を一時ファイルに書き出す
cat > pr_body.md << 'EOF'
## 概要
注文履歴画面に検索フィルタを追加。

## 理由
サポートから検索要求が多く、対応工数を削減するため。

## テスト
ローカルで動作確認済み。

## 関連
Closes #123
Refs #130
EOF

gh pr create --title "feat: 支払い画面にフィルタを追加" --body-file pr_body.md
```

| キーワード | 効果 |
|-----------|------|
| `Closes #N` | マージ時にIssue #N を自動クローズ |
| `Refs #N` | Issue #N へのリンク（クローズしない） |

ブランチがpush済みでPRが未作成の場合に使用します。

> **Values**: 成長の複利 / ニュートラル

✅ **良い例**: PRを1回作成し、URLを記録して待機モードへ受け渡す。
❌ **悪い例**: 状態変化がないのにPR作成や確認コマンドを何度も繰り返す。
Why: きれいな受け渡しの方が追跡性を保ち、重複作業を防げるからです。

### Step 4: 低コストでレビュー待機モードに入る

PRを開いたら、能動的なポーリングを止めます。具体的なシグナルが来たときだけ `github-pr-review-response` へ受け渡します。

```bash
# PR URL を1回だけ記録し、その後はループ確認を止める
gh pr view --json url,updatedAt --jq '{url: .url, updatedAt: .updatedAt}'

# 自然な作業区切りでのみ、まとめて1回確認
gh pr status
```

| トリガー | アクション | 避けること |
|---------|-----------|-----------|
| 新しいレビュー通知、またはユーザーからレビュー到着の共有 | `github-pr-review-response` を開き、コメントを1回確認 | シグナル前の再確認 |
| 別タスク完了後の定期的なまとめ確認 | `gh pr status` を1回だけ実行 | PRごとの細かいポーリング |
| 新しい活動シグナルなし | 待機を継続 | 「念のためもう1回」の確認 |
| PRがクローズ/マージ済み | 待機を終了 | レビュー確認を続ける |

以下のいずれかで待機モードを終了します：
- 対応が必要な新規レビューまたは review request が来た
- PRがクローズまたはマージされた
- ユーザーがセッションの優先順位を変更した

PR作成後、作業が「作成」から「待機」へ移るときに使います。

> **Values**: 余白の設計 / 継続は力

---

## ベストプラクティス

- PR本文は日本語で記述する（チーム標準）
- タイトルは Conventional Commits 形式（`feat:`, `fix:` 等）
- `Closes #N` で Issue を自動クローズする
- Windows では `--body-file` で UTF-8 を確実に扱う
- `gh auth status` で認証を事前確認する
- レビュー待機はイベント駆動を優先し、シグナルなしの再確認を繰り返さない
- PRごとのポーリングではなく、自然な区切りでまとめ確認する

### 事前チェックリスト（`gh pr create` 前）

- [ ] feature branch 上で作業している（`main` ではない）
- [ ] `gh auth status` が対象アカウントで成功する
- [ ] ブランチをリモートへ push できる（保護ルールに抵触しない）
- [ ] `.github/workflows/*` を変更する場合、トークンに `workflow` scope がある
- [ ] 対象ブランチに既存のOpen PRがないことを確認済み（`gh pr list --head BRANCH --state open`）

---

## よくある落とし穴

1. **PR本文が英語になる**
   修正: テンプレ見出しを日本語で統一（概要/理由/テスト/関連）。

2. **Issueリンクの忘れ**
   修正: `## 関連` セクションに `Closes #N` を必ず含める。

3. **mainブランチから直接PRを作る**
   修正: Step 1 の状態検知で feature branch 作成に誘導。

4. **数分おきにレビューを確認し続ける**
   修正: イベント駆動の待機に切り替え、計画した区切りでのみまとめ確認する。

## トラブルシューティング

- **Actions実行時に `workflow ... not found on the default branch` が出る**
  - 原因: `workflow_dispatch` は default branch 上に存在する workflow を対象にする。
  - 対処: 先に workflow ファイルを default branch にマージしてから手動実行する。

- **`.github/workflows/*` を含む push が権限エラーで拒否される**
  - 原因: トークンに `workflow` scope が不足している。
  - 対処: `gh auth refresh -h github.com -s workflow` で再認証する。

---

## アンチパターン

- main に直接 push してから PR を作る
- Issue 番号なしで PR を作成する
- PR 本文を空にする

---

## クイックリファレンス

### PRフローチェックリスト

- [ ] `gh auth status` で認証を確認
- [ ] 状態を検知（未コミット / 未push / PR無し）
- [ ] 必要なら `git-commit-practices` でコミット
- [ ] ブランチを origin に push
- [ ] `gh pr create` で PR 作成（日本語本文 + `Closes #N`）
- [ ] PR URL を記録したら、レビューシグナルが来るまで待機する

### セルフレビューチェックリスト（完了前）

- [ ] PR本文に「意図・理由・テスト・Issueリンク」が揃っている
- [ ] 自動化/workflow変更では必要な出力先ディレクトリ準備がある
- [ ] GitHub API の create 処理が冪等（422競合など）になっている
- [ ] ラベル名・色がリポジトリ規約に一致している

### PR本文テンプレート

```markdown
## 概要
（何を変更したか）

## 理由
（なぜこの変更が必要か）

## テスト
（どう検証したか）

## 関連
Closes #N
```

---

## FAQ

**Q: PR本文は英語でも良い？**
A: チームポリシーとして日本語で統一しています。

**Q: レビューやマージはこのスキルで扱う？**
A: このスキルはPR作成までです。レビュー対応・マージは将来の別スキルで扱います。

**Q: `gh` が未インストールの場合は？**
A: `gh auth status` でエラーになります。[GitHub CLI](https://cli.github.com/) をインストールしてください。

---

## リソース

- https://docs.github.com/en/pull-requests
- https://cli.github.com/manual/gh_pr_create
