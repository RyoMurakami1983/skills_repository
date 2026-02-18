---
name: git-init-to-github
description: >
  ローカルディレクトリをgit初期化してGitHubにpushするワークフロー。
  まだgit管理されていないプロジェクトを一からGitHubリポジトリとして公開する際に使用。
metadata:
  author: RyoMurakami1983
  tags: [git, github, repository, bootstrap, push]
  invocable: false
---

# Git Init to GitHub Push

未管理のローカルディレクトリをGitHubリポジトリにする一連のワークフロー。`.gitignore`作成、初回コミット、`gh`によるリモート作成、初回push、オプションのmainブランチ保護フックまでをカバーする。

## このスキルを使うとき

- `.git/` フォルダが存在しないプロジェクトをgit管理したいとき
- GitHubリポジトリを新規作成してローカルファイルを初めてpushしたいとき
- プロジェクトの技術スタックに合った `.gitignore` を作成したいとき
- public / private の判断をユーザーに確認して進めたいとき
- 初回push後にmainブランチへの直接コミット禁止フックを入れたいとき

## 関連スキル

- **`git-initial-setup`** — mainブランチ保護の包括設定（サーバー＋ローカルフック）
- **`git-commit-practices`** — Conventional Commitsとアトミックな変更
- **`github-pr-workflow`** — PR作成とマージフロー

---

## 基本原則

1. **推測せず確認する** — リポジトリ名・オーナー・公開設定はユーザーの判断。必ずインタラクティブに確認する（ニュートラル）
2. **シンプルなコマンド優先** — `git` と `gh` CLIのみ使用。複雑なスクリプトはツールに任せる（基礎と型）
3. **段階的な安全策** — まず動くpushを完成させ、その後に保護フックを追加。初回pushを過剰設計で妨げない（余白の設計）
4. **多層防御** — 初回push後にローカルのpre-commit/pre-pushフックでmainへの直接コミットを防止（基礎と型）

---

## ワークフロー: 初期化からGitHub Pushまで

### Step 1 — ユーザーから情報を収集

新しいプロジェクトを始めるとき、リポジトリ設定をインタラクティブに収集する。

以下を1つずつ質問する：

| 質問 | 例 | デフォルト |
|------|-----|----------|
| GitHubオーナー（ユーザーまたはorg） | `RyoMurakami1983` | —（必須） |
| リポジトリ名 | `my-project` | カレントディレクトリ名 |
| 公開設定 | `private` / `public` | `private` |
| 説明文 | `"素晴らしいプロジェクト"` | `""`（空） |
| mainブランチ保護フックを入れるか？ | `yes` / `no` | `yes` |

```markdown
// ✅ 正解 - 1つずつ選択肢付きで聞く
ask_user: "リポジトリはpublicとprivateどちらにしますか？"
  choices: ["private（推奨）", "public"]

// ❌ 間違い - 全部まとめて聞く
"オーナー、名前、公開設定、説明、フック設定を教えてください"
```

> **Values**: ニュートラルな視点 / 余白の設計

### Step 2 — `.gitignore` を作成

`.gitignore` がないか、技術スタックに対して不完全な場合に使用する。

既存ファイルからプロジェクトの技術スタックを検出し、適切な `.gitignore` を生成する。

**検出ヒューリスティック**：

| 検出ファイル | `.gitignore` に追加 |
|-------------|-------------------|
| `package.json` | `node_modules/` |
| `requirements.txt` / `pyproject.toml` | `__pycache__/`, `.venv/`, `*.egg-info/` |
| `*.csproj` / `*.sln` | `bin/`, `obj/` |
| `go.mod` | （Goバイナリは通常コミットしない） |
| `Cargo.toml` | `target/` |

常に含めるもの：
```gitignore
# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
```

`.gitignore` が既に存在する場合は上書き前にユーザーに確認する。

> **Values**: 基礎と型の追求 / ニュートラルな視点

### Step 3 — Git初期化と初回コミット

`.gitignore` が準備でき、全ファイルが初回コミットの準備が整ったときに使用する。

```bash
git init
git add .
git commit -m "feat: initial commit

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

**コミットメッセージのルール**：
- Conventional Commits形式（`feat:`, `chore:` 等）
- Copilotが支援した場合は `Co-authored-by` トレイラーを含める
- 件名は可能な限り50文字以内

> **Values**: 基礎と型の追求 / 継続は力

### Step 4 — GitHubリポジトリを作成

初回コミットが存在し、リモートリポジトリを作成する準備ができたときに使用する。

```bash
# ✅ 正解 - 明示的なフラグ指定
gh repo create <owner>/<repo> --private --description "<description>"

# ❌ 間違い - インタラクティブモード（エージェント環境で不安定）
gh repo create
```

**事前チェック**：
1. `gh auth status` でログイン状態を確認
2. リポジトリが既存でないことを確認：`gh repo view <owner>/<repo>` がエラーを返すこと

**エラー対応**：
- `gh auth status` 失敗 → ユーザーに `gh auth login` を案内
- リポジトリが既存 → 既存を使うか新しい名前にするかユーザーに確認

> **Values**: ニュートラルな視点 / 基礎と型の追求

### Step 5 — リモート追加とPush

GitHubリポジトリが作成され、初回pushの準備ができたときに使用する。

HTTPS優先（`gh` 認証と最も相性が良い）：

```bash
# ✅ 正解 - HTTPSを先に試す
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

**フォールバック**（HTTPS失敗時）：
```bash
git remote set-url origin git@github.com:<owner>/<repo>.git
git push -u origin main
```

SSH も失敗した場合：
```
SSHキーが設定されていません。以下を実行してください: gh auth setup-git
その後再試行: git push -u origin main
```

> **Values**: 基礎と型の追求 / 余白の設計

### Step 6 — 確認

pushが完了し、すべてが正しいことを確認するときに使用する。

```bash
gh repo view <owner>/<repo>
git --no-pager log --oneline -1
```

ユーザーに報告する内容：
- リポジトリURL
- 公開設定（public/private）
- ブランチ名
- コミットされたファイル数

> **Values**: 継続は力 / 成長の複利

### Step 7 — mainブランチ保護フックのインストール（オプション）

Step 1でユーザーが希望した場合にローカルブランチ保護を追加するときに使用する。

mainへの直接コミット・pushを防止するローカルフックを設置する。

**Pre-commitフック** (`.git/hooks/pre-commit`):

```bash
#!/bin/sh
branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$branch" = "main" ]; then
  echo "ERROR: mainへの直接コミットは許可されていません。"
  echo "ブランチを作成してください: git checkout -b <branch-name>"
  exit 1
fi
```

**Pre-pushフック** (`.git/hooks/pre-push`):

```bash
#!/bin/sh
branch="$(git rev-parse --abbrev-ref HEAD)"
while read local_ref local_sha remote_ref remote_sha; do
  if echo "$remote_ref" | grep -q "refs/heads/main"; then
    echo "ERROR: mainへの直接pushは許可されていません。"
    echo "featureブランチにpushしてPRを作成してください。"
    exit 1
  fi
done
```

Git for Windowsに含まれるPOSIXシェルがこれらを実行するため、Windowsでもそのまま動作する。

設置後の検証：
```bash
# mainでコミットがブロックされることを確認
git checkout main
echo "test" >> test.txt && git add test.txt && git commit -m "test"
# 期待: ERROR: mainへの直接コミットは許可されていません。
```

> **Values**: 基礎と型の追求 / 成長の複利

---

## よい習慣

### 1. HTTPS優先

**何を**: リモートURLはHTTPSをデフォルトにし、失敗時のみSSHにフォールバック。

**なぜ**: `gh` CLIがHTTPS認証ヘルパーを自動設定するため。SSHは別途鍵設定が必要。

**価値観**: 基礎と型（最小構成で確実に動く）

### 2. 破壊的操作前に確認

**何を**: `.gitignore` の上書きやforce-pushの前にユーザーに確認する。

**なぜ**: 作業ディレクトリの予期しないデータ損失を防ぐ。

**価値観**: ニュートラル（偏らない判断）

### 3. 関心の分離：まずpush、保護は後から

**何を**: pushワークフローを完了してからブランチ保護を追加する。

**なぜ**: フックエラーで初回pushがブロックされることを防ぎ、段階的に構築する。

**価値観**: 余白の設計（変化の起点を守る）

---

## よくある落とし穴

### 1. SSH Permission Denied

**問題**: `git@github.com:...` でSSH鍵が未設定のため失敗。

**解決**: HTTPS URLを先に使う。SSHを希望する場合は `gh auth setup-git` を案内。

### 2. `node_modules/` の `.gitignore` 忘れ

**問題**: 大量ファイルがステージされ、コミットが遅延または失敗。

**解決**: `git add .` の前に必ず `.gitignore` を作成する。

### 3. Unixでフックに実行権限がない

**問題**: pre-commit/pre-pushフックが実行権限不足で無視される。

**解決**: `chmod +x .git/hooks/pre-commit .git/hooks/pre-push` を作成後に実行。

---

## Anti-Patterns

### 1. フラグなしの `gh repo create`

```bash
# ❌ アンチパターン - エージェント/CI環境で不安定
gh repo create

# ✅ 修正 - 常に明示的フラグを指定
gh repo create owner/repo --private --description "desc"
```

**なぜ**: インタラクティブモードはstdinプロンプトに依存し、エージェントでは確実に処理できない。

### 2. 確認なしのforce-push

```bash
# ❌ アンチパターン - データ損失リスク
git push --force origin main

# ✅ 修正 - ユーザーの明示的同意なしにforce-pushしない
ask_user: "force-pushはリモート履歴を上書きします。実行しますか？"
```

**なぜ**: mainへのforce-pushはコラボレーターの作業を不可逆的に破壊する可能性がある。

### 3. `.gitignore` 作成前の初回コミット

```bash
# ❌ アンチパターン - 秘密情報やビルド成果物をコミット
git init && git add . && git commit -m "init"

# ✅ 修正 - 必ず.gitignoreを先に作成
# .gitignore作成 → git init → git add . → git commit
```

**なぜ**: 誤ってコミットされたファイル（`node_modules/`、`.env`等）をgit履歴から削除するのは困難でエラーが起きやすい。

---

## クイックリファレンス

### 判断テーブル

| 状況 | アクション | 理由 |
|------|----------|------|
| `.git/` フォルダがない | Step 1から開始 | フルワークフローが必要 |
| `.git/` はあるがリモートなし | Step 4にスキップ | ローカルリポジトリは初期化済み |
| リモートはあるがpush失敗 | Step 5のフォールバック確認 | HTTPS/SSH認証の問題 |
| ブランチ保護を希望 | Step 7を実施 | mainへの直接コミットを防止 |
| `.gitignore` が既に存在 | 上書き前にユーザー確認 | ユーザーのカスタマイズを保持 |
| `gh auth status` 失敗 | `gh auth login` を案内 | 認証なしではリポジトリ作成不可 |

### チェックリスト

- [ ] 収集済み: オーナー、リポジトリ名、公開設定、説明文
- [ ] `.gitignore` を技術スタックに合わせて作成
- [ ] `git init` 完了
- [ ] `git add .` + 初回コミット作成
- [ ] `gh repo create` 成功
- [ ] `git remote add origin`（HTTPS）
- [ ] `git push -u origin main` 成功
- [ ] `gh repo view` でリポジトリ存在確認
- [ ] （オプション）Pre-commitフック設置
- [ ] （オプション）Pre-pushフック設置
- [ ] （オプション）mainでのテストコミットでブロック確認

### コマンドまとめ

```bash
git init
git add .
git commit -m "feat: initial commit"
gh repo create <owner>/<repo> --private --description "<desc>"
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
gh repo view <owner>/<repo>
```

---

## リソース

- [gh repo create ドキュメント](https://cli.github.com/manual/gh_repo_create)
- [git init ドキュメント](https://git-scm.com/docs/git-init)
- [gitignore パターン](https://git-scm.com/docs/gitignore)
- [Git Hooks ドキュメント](https://git-scm.com/docs/githooks)
- **`git-initial-setup`** スキル — サーバーサイド＋ローカルの包括保護

---
