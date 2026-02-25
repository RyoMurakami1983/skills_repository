---
name: git-initial-setup
description: git init/clone後のmain保護をデフォルト化し、環境差異を吸収する設定ガイド。初期セットアップで使う。
metadata:
  author: RyoMurakami1983
  tags: [git, github, branch-protection, hooks, bootstrap]
  invocable: false
---

# Git初期セットアップ（main保護）

git init/clone後のmain保護をデフォルト化するため、GitHubブランチ保護（Option A）とグローバルなフック設定、ローカルpre-commit/pre-push（Option B）を組み合わせます。さらに `.gitattributes` と `.editorconfig` でクロスプラットフォームの環境差異を吸収します。

## このスキルを使うとき

以下の状況で活用してください：
- git init/cloneの初期段階で保護をデフォルト化したい
- グローバルフック設定をチームに展開したい
- mainへのPull Request (PR)マージだけを強制したい
- リリース前の誤コミット/誤プッシュを防止したい
- チームのOS・エディタ・AIエージェントの違いによる環境差異を吸収したい
- privateリポジトリでローカル保護を補完したい
- 大型リリース前に保護状況を監査したい

## 関連スキル

- **`git-commit-practices`** - コミット運用と規約
- **`github-pr-workflow`** - PR作成とマージフロー
- **`skills-author-skill`** - Skill執筆の標準
- **`skills-validate-skill`** - Skill品質の検証

---

## 依存関係

- Git 2.30+（必須）
- BashまたはPowerShell（フックスクリプト用）
- GitHubの管理権限（ブランチ保護設定用）

## コア原則

1. **多層防御** - サーバー側とローカル保護を組み合わせる（基礎と型）
2. **最小権限** - mainへ直接プッシュできる人を最小化
3. **明確なワークフロー** - PR運用を明文化（成長の複利）
4. **例外の透明性** - 緊急時の手順を明記（ニュートラル）
5. **自動化優先** - 反復スクリプトでヒューマンエラー低減（継続は力）

---

## ワークフロー: メインブランチを保護する

### Step 1: ブランチ保護ルールの設定

mainに対する最小限の保護ルールを作成し、PRを必須化します。これが基盤です — この設定がなければ、誰でもmainに直接プッシュできます。

```txt
Settings > Branches > Add rule
Branch name pattern: main
Enable: Require a pull request before merging
```

新規リポジトリのセットアップや、既存リポジトリへの保護追加時に使います。

> **Values**: 基礎と型 / 継続は力

### Step 2: リポジトリ環境ファイルの生成

`.gitattributes` と `.editorconfig` を追加し、クロスプラットフォームの差異を吸収します。これらがないと、異なるOSやAIエージェントのサンドボックスからcloneしたメンバーが全ファイルmodifiedになる問題が発生します。

**.gitattributes**（改行コード正規化）:

```
* text=auto eol=lf
*.ps1 text eol=crlf
*.bat text eol=crlf
*.cmd text eol=crlf
*.sln text eol=crlf
*.png binary
*.jpg binary
*.ico binary
```

**.editorconfig**（エディタ設定正規化）:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true

[*.{yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

既存リポジトリに導入する場合は、`.gitattributes` 追加後に `git add --renormalize .` で追跡ファイルを再正規化してください。

新規リポジトリ作成時、または異なるOS・エディタ・AIエージェントを使うメンバーのオンボーディング時に使います。

> **Values**: 基礎と型 / 余白の設計

### Step 3: レビュー要件の設定

mainへのマージを意図的かつ追跡可能にするため、レビュー要件を定義します。Code Ownersを有効化し、新コミット時に既存の承認を無効化して責任を明確にします。

```txt
Require a pull request before merging:
  ✅ Require approvals: 1
  ✅ Dismiss stale pull request approvals when new commits are pushed
  ✅ Require review from Code Owners
```

mainマージの責任を明確化し、レビュー品質を統一したいときに使います。

> **Values**: 成長の複利 / ニュートラル

### Step 4: 必須ステータスチェックの設定

CIチェックでマージをゲートし、壊れたビルドをmainに入れません。必須チェックでmainをグリーンに保ち、ロールバックリスクを低減します。

```yaml
required_status_checks:
  - ci/build
  - ci/test
```

CIパイプラインがあり、リグレッションを防ぎたいときに使います。

> **Values**: 継続は力 / 基礎と型

### Step 5: プッシュ権限の制限

直接プッシュ権限を制限し、管理者にも保護を適用します。"Include administrators"を有効化し、プッシュ可能なユーザーを制限します。

```txt
✅ Include administrators
✅ Restrict who can push to matching branches
   Allowed: release-bot only
```

規制環境や監査対象の運用で強い統制が必要なときに使います。

> **Values**: ニュートラル / 基礎と型

### Step 6: ローカルフックの導入

pre-commitとpre-pushフックを導入し、変更がリモートに届く前にmainへのコミット・プッシュをブロックします。

```bash
# このリポジトリにフックを導入
./scripts/setup.sh
```

privateリポジトリの保護代替、ローカル安全策、またはリリースウィンドウ中に使います。

> **Note**: `.git/hooks/` にコピーする代わりに、リポジトリレベルのフックディレクトリを `git config core.hooksPath .githooks` で指定できます。フックがバージョン管理され、clone後にセットアップスクリプト不要で自動適用されます。

> **トラブルシューティング（Windows）**: `setup.ps1` がセキュリティエラーで失敗する場合、PowerShellの実行ポリシーが `Restricted` になっている可能性があります。`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` を実行してローカルスクリプトを許可してから再試行してください。

> **Values**: 継続は力 / 基礎と型

### Step 7: グローバルフックのデフォルト設定

`core.hooksPath`でグローバルフックを設定し、新規リポジトリに保護を自動継承させます。

```bash
git config --global core.hooksPath "~/.githooks"
```

同一端末で複数リポジトリを管理し、自動保護を適用したいときに使います。

> **Values**: 基礎と型 / 継続は力

### Step 8: チームへの展開

明確なコミュニケーションで保護を展開します：PR運用ポリシーの告知、セットアップスクリプトの共有、オンボーディング資料の更新を行います。

```markdown
## オンボーディングチェックリスト
- [ ] `./scripts/setup.sh` を実行してフックを導入
- [ ] mainのブランチ保護が有効か確認
- [ ] github-pr-workflowでPR運用を確認
```

複数リポジトリの管理や、チーム間で統一した保護が必要なときに使います。

> **Values**: 成長の複利 / 継続は力

### Step 9: 緊急対応

保護を恒久的に無効化せずに問題を解消します。緊急ホットフィックスでは、管理者バイパスと事後レビューを組み合わせます。

```bash
# 緊急ホットフィックス: 明示的な承認のみでバイパス
git push --no-verify origin hotfix/critical-fix
# 事後: バイパスのレビューと記録
```

保護が緊急修正をブロックしたとき、または環境間でフックの動作が異なるときに使います。

> **Values**: ニュートラル / 温故知新

---

## ベストプラクティス

- リポジトリ作成時に `.gitattributes` と `.editorconfig` を追加する
- 先にグローバルフックを設定してから新規リポジトリを作成
- リモート作成後にGitHub保護を有効化
- mainマージに最低1承認を必須化
- 保護設定を運用ドキュメントに記録
- 組織変更後に保護設定を再確認
- 緊急バイパス手順を運用書に明記

core.hooksPath を全リポジトリに適用する。  
init.templateDir を新規リポジトリに適用する。  
mainへの直接プッシュを避ける。

---

## よくある落とし穴

- 管理者保護のチェック漏れ
- 便利だからと直接プッシュを残し続ける
- ローカルフックだけで全体保護を期待する

Fix: "Include administrators" を必ず有効化し、権限を記録する。  
Fix: mainの直接プッシュ権限を段階的に撤廃する。  
Fix: GitHubの保護ルールでチーム全体を強制する。

---

## アンチパターン

- チーム全員が同じOS・エディタ設定であると暗黙に仮定する（暗黙の環境前提）
- 早く直したいから保護を一時解除する
- `--no-verify`を常用フローにする
- mainへの直接プッシュを自由化する

---

## FAQ

**Q: 無料プランのprivateリポジトリでも保護できますか？**  
A: GitHubのブランチ保護は有料プランが必要です。ローカルフックで代替してください。

**Q: WindowsでPowerShellフックは自動実行されますか？**  
A: Git for WindowsはBashでフックを実行します。Bash版を使うか共有フックパスに配置してください。

**Q: git initで自動的にフックは入りますか？**  
A: core.hooksPath または init.templateDir をグローバル設定した場合のみ自動適用されます。

**Q: 管理者もブロックされますか？**  
A: ルールで"Include administrators"を有効化した場合のみ対象になります。

---

## クイックリファレンス

### ステップ要約

| ステップ | 目的 | 使うとき |
|----------|------|----------|
| 1 | ブランチ保護ルール | PR運用を徹底したい |
| 2 | 環境ファイル | クロスプラットフォーム統一 |
| 4 | 必須ステータスチェック | ビルド/テストを必須化 |
| 6 | ローカルフック | ローカル安全策が必要 |
| 7 | グローバルデフォルト | git init/cloneを標準化 |

### 判断テーブル

| 状況 | 推奨 | 理由 |
|------|------|------|
| 新規リポジトリ | .gitattributes + .editorconfig追加 | 初日から環境差異を吸収 |
| マルチOSチーム | core.hooksPath設定 | 全体デフォルト化 |
| 新規のみ適用 | init.templateDir設定 | 既存に影響なし |
| private/無料プラン | ローカルフック | サーバー保護不可 |
| チーム運用 | PR必須化 | 変更の追跡性向上 |

```bash
# フック導入（pre-commit + pre-push）（macOS/Linux/Git Bash）
./scripts/setup.sh

# フック導入（PowerShell）
.\scripts\setup.ps1

# グローバルフック設定（全リポジトリ）
git config --global core.hooksPath "~/.githooks"

# initテンプレート設定（新規のみ）
git config --global init.templateDir "~/.git-template"

# 現在のブランチ確認
git branch --show-current
```

---

## リソース

- [GitHub Protected Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Git Hooks Documentation](https://git-scm.com/docs/githooks)

---
