---
name: skill-git-initial-setup
description: git init/clone後のmain保護をデフォルト化する設定ガイド。初期セットアップで使う。
author: RyoMurakami1983
tags: [git, github, branch-protection, hooks, bootstrap]
invocable: false
version: 1.2.0
---

# Git初期セットアップ（main保護）

git init/clone後のmain保護をデフォルト化するため、GitHubブランチ保護（Option A）とグローバルなフック設定、ローカルpre-commit/pre-push（Option B）を組み合わせます。

## このスキルを使うとき

以下の状況で活用してください：
- git init/cloneの初期段階で保護をデフォルト化したい
- グローバルフック設定をチームに展開したい
- mainへのPull Request (PR)マージだけを強制したい
- リリース前の誤コミット/誤プッシュを防止したい
- privateリポジトリでローカル保護を補完したい
- 大型リリース前に保護状況を監査したい

## 関連スキル

- **`skill-git-japanese-practices`** - Git運用とコードレビューの実践
- **`skill-writing-guide`** - Skill執筆の標準
- **`skill-quality-validation`** - Skill品質の検証

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

## パターン1: ベースラインのブランチ保護ルール

### 概要

mainに対する最小限の保護ルールを作成し、PR必須を徹底します。

### 基本例

```txt
# ✅ CORRECT - mainのPR必須化
Settings > Branches > Add rule
Branch name pattern: main
Enable: Require a pull request before merging

# ❌ WRONG - mainを無保護のまま運用
No branch protection rule set
```

### 中級例

- 承認数を1に設定
- Code Ownersレビューを必須化
- 会話の解決を必須化

### 上級例

- 管理者も保護対象に含める
- 線形履歴を必須化
- 直接プッシュ可能ユーザーを制限（空欄で全ブロック）

Why: PR運用で変更の追跡性と安全性を高める。

### 使うとき

| シナリオ | 推奨 | 理由 |
|----------|------|------|
| 小規模チーム | 基本 | 低コストで最小保護 |
| 中〜大規模チーム | 中級 | レビュー責任を明確化 |
| 監査・規制環境 | 上級 | 強い統制と追跡性 |

**Values**: 基礎と型 / 継続は力

---

## パターン2: Pull Requestレビュー基準

### 概要

mainへのマージを意図的かつ追跡可能にするため、レビュー基準を整備します。

### 基本例

- 承認数を1に設定
- デフォルトレビュアーを指定

### 中級例

- Code Ownersを有効化
- 追加コミットで承認を無効化

### 上級例

- 保護パスにCode Ownerレビューを必須化
- 全ての会話解決を必須化

### 使うとき

- mainのマージ責任を明確化したい
- チーム全体でレビュー品質を揃えたい

**Values**: 成長の複利 / ニュートラル

---

## パターン3: 必須ステータスチェック

### 概要

継続的インテグレーション（CI）チェックを必須化し、破損ビルドがmainに入るのを防ぎます。

### 基本例

- 1つのビルドチェックを必須化（例: `ci/build`）

```yaml
# ✅ CORRECT - ビルドとテストを必須化
required_status_checks:
  - ci/build
  - ci/test

# ❌ WRONG - 必須チェックなし
required_status_checks: []
```

Why: 破損した変更をmainに入れない。

### 中級例

- テストとlintを必須化
- ブランチの最新化を必須化

### 上級例

- プラットフォーム別の必須チェックを分離
- リリース用タグに専用チェックを追加

Why: mainの品質を継続的に担保する。

### 使うとき

| シナリオ | 推奨 | 理由 |
|----------|------|------|
| 高速開発チーム | 基本 | 速度と品質のバランス |
| 本番サービス | 中級 | 回帰を防止 |
| 複数プラットフォーム | 上級 | 安定性を担保 |

**Values**: 継続は力 / 基礎と型

---

## パターン4: プッシュ権限の制限と管理者保護

### 概要

直接プッシュ権限を限定し、管理者にも保護を適用します。

### 基本例

- "Include administrators" を有効化

### 中級例

- 直接プッシュ可能ユーザーを制限
- リリース自動化アカウントのみ許可

### 上級例

- 緊急バイパス手順を文書化
- 管理者バイパス時に書面承認を必須化

### 使うとき

- main保護を強制したい
- 監査対象の運用が必要

**Values**: ニュートラル / 基礎と型

---

## パターン5: ローカルpre-commit/pre-pushフック（Option B）

### 概要

ローカルフックでmainへのコミットとプッシュをネットワーク前に遮断します。

### 基本例

```bash
# ✅ CORRECT - 対象リポジトリにフックを導入
./scripts/setup.sh

# ❌ WRONG - 何もしないままmainへpush
git push origin main
```

pre-commitとpre-pushの両方を導入します。

### 中級例

保護対象ブランチを拡張：

```bash
protected_branches=("main" "release")
```

### 上級例

Gitテンプレートに組み込み、新規リポジトリで自動継承。

Why: ネットワークに届く前に誤操作を止める。

### 使うとき

- privateリポジトリでの保護代替
- 新メンバーの誤操作防止
- mainへのコミットをローカルで止めたい
- GitHub設定前の暫定保護

**Values**: 継続は力 / 基礎と型

---

## パターン6: git init/cloneのデフォルト化（グローバルフック）

### 概要

グローバルなフック設定で、新規リポジトリに保護を自動適用します。

### 基本例

既存リポジトリにも効くグローバルフックパスを設定：

```bash
# ✅ CORRECT - 全リポジトリにフックを適用
git config --global core.hooksPath "~/.githooks"
```

Why: 端末上の全リポジトリでフックが有効になる。

### 中級例

git init用のテンプレートを設定（新規のみ）：

```bash
# ✅ CORRECT - 新規リポジトリ向けのテンプレート
git config --global init.templateDir "~/.git-template"
mkdir -p ~/.git-template/hooks
cp scripts/pre-commit scripts/pre-push ~/.git-template/hooks/
```

Why: git init時のデフォルト保護を実現する。

### 上級例

チーム用の初期化スクリプトでcore.hooksPathとコピーを一括実行。

```python
# ✅ CORRECT - 端末用ブートストラップ
import shutil
from pathlib import Path

# Dependencies: Python 3.9+, Git 2.30+
hooks_dir = Path.home() / ".githooks"
hooks_dir.mkdir(parents=True, exist_ok=True)
shutil.copy("scripts/pre-commit", hooks_dir / "pre-commit")
shutil.copy("scripts/pre-push", hooks_dir / "pre-push")
```

Why: 初期セットアップの漏れを防ぐ。

オプション: DIを使った自動化ツール例

```csharp
// ✅ CORRECT - フック設定をDIで注入
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

services.Configure<HookOptions>(config.GetSection("Hooks"));
services.AddSingleton<HookInstaller>();
```

### 使うとき

- git init/clone時にデフォルトで保護したい
- 同一端末で複数リポジトリを扱う

**Values**: 基礎と型 / 継続は力

---

## パターン7: チーム展開戦略

### 概要

コミュニケーションとオンボーディングを含めて保護を展開します。

### 基本例

- PR運用の告知
- セットアップ手順を共有
- オンボーディング資料を更新

### 中級例

- PRチェックリストを導入
- 運用手順書に設定を記録

### 上級例

- 四半期ごとに保護設定をレビュー
- リポジトリ単位で監査

### 使うとき

- 複数リポジトリを管理している
- チーム間で統一した運用が必要

**Values**: 成長の複利 / 継続は力

---

## パターン8: トラブルシューティングと緊急対応

### 概要

保護を無効化せずに問題を解消し、緊急対応を安全に行います。

### 基本例

- フックが動かない: `core.hooksPath` と実行権限を確認

### 中級例

- ルールが効かない: `main` との一致を確認
- 必須チェック未登録: 必須チェック一覧を更新

### 上級例

- 緊急修正: 管理者バイパス + 事後レビュー
- ローカル回避: `git push --no-verify` は明示承認のみ

### 使うとき

- 緊急修正で保護が障害になった
- 環境ごとに挙動が違う

**Values**: ニュートラル / 温故知新

---

## ベストプラクティス

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

### パターン要約

| パターン | 目的 | 使うとき |
|---------|------|----------|
| 1 | ブランチ保護ルール | PR運用を徹底したい |
| 3 | 必須ステータスチェック | ビルド/テストを必須化 |
| 5 | ローカルフック | ローカル安全策が必要 |
| 6 | グローバルデフォルト | git init/cloneを標準化 |

### 判断テーブル

| 状況 | 推奨 | 理由 |
|------|------|------|
| 新規リポジトリ | core.hooksPath設定 | 全体デフォルト化 |
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

## 変更履歴

### Version 1.2.0 (2026-02-12)
- skill名をgit初期セットアップに変更
- git init/clone向けのグローバルフック設定を追加

### Version 1.1.0 (2026-02-12)
- mainへのコミットを止めるpre-commitを追加
- セットアップでpre-commit + pre-pushを導入

### Version 1.0.0 (2026-02-12)
- 初版リリース
- ブランチ保護ルール + pre-pushフックを整理
- Bash/PowerShellスクリプト同梱
