---
name: github-repo-label-setup
description: プレフィックス命名規則でリポジトリのラベルを標準化し、IssueとPRの管理を統一する。ラベルの初期設定や移行時に使う。
metadata:
  author: RyoMurakami1983
  tags: [github, labels, issue-management, repository-setup, conventions]
  invocable: false
---

# GitHub リポジトリ ラベルセットアップ

プレフィックス命名規則（`p/`, `t/`, `s/`, `a/`）を使い、リポジトリのラベルを標準化します。プロジェクト横断でIssueとPRの管理を一貫させるためのワークフローです。

## このスキルを使うとき

以下の状況で活用してください：
- 新しいGitHubリポジトリでラベル体系を定義するとき
- GitHubデフォルトラベルからプレフィックス規則に移行するとき
- 組織内の複数リポジトリでラベルを統一したいとき
- チームに一貫したIssueトリアージフローを導入するとき
- 既存ラベルの不整合や重複を監査するとき
- CONTRIBUTING.mdやREADMEにラベル規約を記録するとき

## 関連スキル

- **`github-issue-intake`** - ラベルを活用したIssue作成とトリアージ
- **`github-pr-workflow`** - PR作成とマージフロー
- **`git-initial-setup`** - リポジトリの初期設定と保護
- **`skills-author-skill`** - Skill執筆の標準

---

## 依存関係

- GitHub CLI (`gh`) — `gh auth status` で事前確認
- GitHubリポジトリへの管理者またはWrite権限
- BashまたはPowerShell（バッチ作成スクリプト用）

## コア原則

1. **プレフィックス規約** (基礎と型) - `p/`, `t/`, `s/`, `a/`のプレフィックスで、ソート可能・人間可読なラベル体系を実現する。なぜプレフィックスか？ — フリーテキストのラベル名は検索しづらく、カテゴリが曖昧になる。プレフィックスにより機械的なフィルタリングと視覚的なグループ化が同時に可能になる
2. **冪等な作成** (継続は力) - `--force`フラグでスクリプトを何度でもエラーなく実行可能にする。なぜ冪等性か？ — 複数リポジトリへの展開や再実行時に「既に存在する」エラーで止まらないため
3. **色のセマンティクス** (ニュートラル) - カテゴリごとに色スペクトラムを統一し、一目でカテゴリが判別できるようにする。赤＝優先度、青＝種別、黄＝状態、緑＝領域
4. **最小限の実用セット** (余白の設計) - 必要最低限のラベルから始め、本当に必要になったら追加する。過剰なラベルは「選択疲れ」を起こし、結局使われなくなる
5. **ドキュメント優先** (成長の複利) - ラベル規約を記録し、新しいコントリビューターが迷わず適用できるようにする。ルールが頭の中にしかなければ、属人化し再現できない

---

## ワークフロー: リポジトリラベルのセットアップ

### Step 1: 既存ラベルの監査

現在のラベルを一覧し、GitHubデフォルトと比較します。新しい規則を適用する前に、残す・改名する・削除するラベルを判断します。

```bash
# リポジトリの全ラベルを一覧
gh label list --repo OWNER/REPO

# 既存ラベル数をカウント
gh label list --repo OWNER/REPO --json name --jq 'length'
```

```powershell
# PowerShell版
gh label list --repo OWNER/REPO
gh label list --repo OWNER/REPO --json name --jq 'length'
```

| デフォルトラベル | 判断 | 理由 |
|-----------------|------|------|
| bug | `t/bug`に置換 | プレフィックス規約 |
| enhancement | `t/feature`に置換 | 統一命名 |
| documentation | `t/docs`に置換 | 短縮プレフィックス |
| good first issue | 残す | コミュニティ標準 |
| help wanted | 残す | コミュニティ標準 |
| duplicate | 削除 | Issueクローズ理由で代替 |
| invalid | 削除 | Issueクローズ理由で代替 |
| wontfix | 削除 | Issueクローズ理由で代替 |
| question | 削除 | Discussionsで代替 |

新規リポジトリのセットアップ時、または既存リポジトリをプレフィックス規約に移行するときに使用します。

> **Values**: 基礎と型 / 温故知新

### Step 2: ラベルセットの選定

リポジトリに適用するラベルカテゴリと具体的なラベルを選びます。以下の表を標準セットとして使用してください。

| カテゴリ | ラベル | 色 | 用途 |
|---------|--------|-----|------|
| 優先度 | `p/critical`, `p/high`, `p/medium`, `p/low` | 赤系 (`#B60205`, `#D93F0B`, `#FBCA04`, `#0E8A16`) | トリアージ優先度 |
| 種別 | `t/bug`, `t/feature`, `t/docs`, `t/chore`, `t/refactor` | 青系 (`#1D76DB`, `#0075CA`, `#5319E7`, `#006B75`, `#0366D6`) | 作業分類 |
| 状態 | `s/in-progress`, `s/review`, `s/blocked` | 黄系 (`#FEF2C0`, `#D4C5F9`, `#E4E669`) | ワークフロー状態 |
| 領域 | `a/skills`, `a/dotnet`, `a/python`, `a/docs` | 緑系 (`#22863A`, `#1A7F37`, `#2DA44E`, `#3FB950`) | ドメイン所有権 |

Areaラベルはプロジェクトに合わせてカスタマイズしてください。Priority、Type、Statusラベルはリポジトリ横断で統一を推奨します。

このステップは初めてラベル規約を定義するとき、またはラベルセットの完全性を見直すときに使用します。

> **Values**: 基礎と型 / 余白の設計

### Step 3: ラベルの一括作成

`gh label create`に`--force`フラグを付けて全ラベルを作成します。`--force`は既存ラベルをエラーなく更新します。

```bash
# 優先度ラベル
gh label create "p/critical" --color "B60205" --description "Critical priority" --force
gh label create "p/high"     --color "D93F0B" --description "High priority" --force
gh label create "p/medium"   --color "FBCA04" --description "Medium priority" --force
gh label create "p/low"      --color "0E8A16" --description "Low priority" --force

# 種別ラベル
gh label create "t/bug"      --color "1D76DB" --description "Bug report" --force
gh label create "t/feature"  --color "0075CA" --description "Feature request" --force
gh label create "t/docs"     --color "5319E7" --description "Documentation" --force
gh label create "t/chore"    --color "006B75" --description "Maintenance task" --force
gh label create "t/refactor" --color "0366D6" --description "Code refactoring" --force

# 状態ラベル
gh label create "s/in-progress" --color "FEF2C0" --description "Work in progress" --force
gh label create "s/review"      --color "D4C5F9" --description "Ready for review" --force
gh label create "s/blocked"     --color "E4E669" --description "Blocked by dependency" --force

# 領域ラベル（プロジェクトに合わせてカスタマイズ）
gh label create "a/skills"  --color "22863A" --description "Skills domain" --force
gh label create "a/dotnet"  --color "1A7F37" --description ".NET domain" --force
gh label create "a/python"  --color "2DA44E" --description "Python domain" --force
gh label create "a/docs"    --color "3FB950" --description "Documentation domain" --force
```

```powershell
# PowerShell — gh CLIはクロスプラットフォームで同じコマンドが使えます
gh label create "p/critical" --color "B60205" --description "Critical priority" --force
gh label create "p/high"     --color "D93F0B" --description "High priority" --force
gh label create "p/medium"   --color "FBCA04" --description "Medium priority" --force
gh label create "p/low"      --color "0E8A16" --description "Low priority" --force
```

ラベルが定義済みで適用準備ができたときに使用します。いつでも安全に再実行できます。

> **Values**: 継続は力 / 基礎と型

### Step 4: 既存Issueのトリアージ

既存の未ラベルIssueにラベルを付与します（任意）。`gh issue list`の`--json`で未ラベルIssueを特定し、適切なラベルを割り当てます。

```bash
# 未ラベルのIssueを一覧
gh issue list --label "" --json number,title --jq '.[] | "\(.number)\t\(.title)"'

# 特定のIssueにラベルを追加
gh issue edit 42 --add-label "t/bug,p/medium"

# キーワードで一括ラベル付け（例）
for issue in $(gh issue list --search "is:open no:label" --json number --jq '.[].number'); do
  echo "Review issue #$issue"
done
```

```powershell
# PowerShell版
$issues = gh issue list --search "is:open no:label" --json number --jq '.[].number'
foreach ($issue in $issues) {
    Write-Host "Review issue #$issue"
}
```

新しいラベル規約への移行時に、既存Issueの分類が必要な場合に使用します。完全自動の一括ラベル付けは避け、手動レビューを推奨します。なぜ手動か？ — 文脈を理解しないままラベルを付けると、誤分類が蔓延し、ラベル体系への信頼を損なうため。

> **Values**: ニュートラル / 成長の複利

### Step 5: ラベル規約のドキュメント化

CONTRIBUTING.mdまたはREADMEにラベル規約を記録し、コントリビューターが一貫してラベルを使えるようにします。ラベル表とトリアージガイドラインを含めます。

```markdown
## ラベル規約

このリポジトリではプレフィックス型のラベルを使用しています：

| プレフィックス | カテゴリ | 例 | いつ使うか |
|---------------|---------|-----|-----------|
| `p/` | 優先度 | `p/high` | トリアージ時に緊急度を設定 |
| `t/` | 種別 | `t/bug` | Issue作成・分類時 |
| `s/` | 状態 | `s/review` | ワークフロー状態の更新時 |
| `a/` | 領域 | `a/python` | ドメイン所有権の割り当て |

### トリアージチェックリスト
- [ ] `t/`ラベルを1つ付与（必須）
- [ ] `p/`ラベルを1つ付与（バグは必須）
- [ ] `a/`ラベルを1つ付与（推奨）
- [ ] 作業進行に合わせて`s/`ラベルを更新
```

ラベル作成後、コントリビューターやメンテナーが共有リファレンスを持てるように使用します。なぜドキュメント化するか？ — 「暗黙知の形式知化」こそが成長の複利を生む。頭の中のルールは再現できないが、書かれたルールはチーム全体で再利用できる。

> **Values**: 成長の複利 / 継続は力

---

## 判断テーブル

| 状況 | ラベルカテゴリ | 理由 |
|------|--------------|------|
| 個人プロジェクト | `t/` + `p/`のみ | 最小限の管理コストで十分な分類 |
| 小規模チーム（2-5人） | `t/` + `p/` + `a/` | ドメイン所有権がルーティングを助ける |
| クロスファンクショナルチーム | 全4カテゴリ | 完全なトリアージワークフロー |
| OSSプロジェクト | 全4カテゴリ + コミュニティラベル | `good first issue` + プレフィックスラベル |
| モノレポ | 全4カテゴリ（`a/`を拡張） | Areaラベルをパッケージパスに対応 |

---

## ベストプラクティス

- `gh label create`に`--force`フラグを使って冪等なスクリプトにする
- ラベル説明は100文字以内に収める
- カテゴリごとに一貫した色スペクトラムで視覚的に走査しやすく
- ソート可能性のためフリーフォーム名よりプレフィックス（`p/`, `t/`）を優先
- ラベル規約をCONTRIBUTING.mdに記録する
- 四半期ごとに未使用ラベルを棚卸しする
- `good first issue`と`help wanted`はコミュニティ標準として維持する

---

## よくある落とし穴

1. **再実行時に`--force`フラグが抜けている**
   Fix: 常に`--force`を付ける — 既存ラベルをエラーなく更新する。

2. **コミュニティラベル（`good first issue`、`help wanted`）を削除する**
   Fix: これらはGitHubのUIやコントリビューターガイドで認識される標準ラベル。残すこと。

3. **規約をドキュメント化せずにラベルを適用する**
   Fix: ラベル作成の前後にCONTRIBUTING.mdを更新する。ドキュメント化が最終ステップである理由 — 最終状態を正確に記録するため。

---

## アンチパターン

- 命名規約なしに大量のラベルを作成する
- カテゴリの意味を持たないランダムな色を使う
- コミュニティ規約を理解せずにデフォルトラベルを全削除する
- 手動レビューなしにIssueの一括ラベル付けを完全自動化する
- 意味が重複するラベルを共存させる（例：`bug`と`t/bug`の両方）

---

## FAQ

**Q: GitHubのデフォルトラベルは削除すべき？**
A: `good first issue`と`help wanted`はコミュニティ標準として残します。`bug`、`enhancement`、`documentation`はプレフィックス付きに置換します。`duplicate`、`invalid`、`wontfix`、`question`は削除します。

**Q: 既存リポジトリでラベル作成スクリプトを実行できる？**
A: はい。`--force`フラグが既存ラベルを更新するため、重複作成エラーが起きません。いつでも安全に再実行できます。

**Q: 標準の`a/`ラベル以外にプロジェクト固有のドメインがある場合は？**
A: プロジェクト固有の`a/`ラベル（例：`a/api`、`a/frontend`、`a/infra`）を追加してください。プレフィックス規約は統一を維持します。

**Q: 4つのラベルカテゴリすべてが必要？**
A: いいえ。最小セットは`t/`と`p/`です。ワークフローが求めたら`s/`と`a/`を追加してください。判断テーブルを参照してください。

---

## クイックリファレンス

### ステップ要約

| ステップ | 目的 | 使うとき |
|----------|------|----------|
| 1 | 既存ラベルの監査 | セットアップ・移行時 |
| 2 | ラベルセットの選定 | 規約定義時 |
| 3 | ラベルの一括作成 | リポジトリへの適用時 |
| 4 | 既存Issueのトリアージ | 新規約への移行時 |
| 5 | 規約のドキュメント化 | コントリビューター受入時 |

### ラベルセットアップチェックリスト

- [ ] `gh label list`で既存ラベルを監査
- [ ] 標準テーブルからラベルセットを定義
- [ ] `--force`付きでバッチ作成スクリプトを実行
- [ ] 未ラベルIssueをトリアージ（任意）
- [ ] CONTRIBUTING.mdに規約を記録

### バッチ作成スクリプト（コピー＆ペースト用）

```bash
# 優先度
gh label create "p/critical" --color "B60205" --description "Critical priority" --force
gh label create "p/high"     --color "D93F0B" --description "High priority" --force
gh label create "p/medium"   --color "FBCA04" --description "Medium priority" --force
gh label create "p/low"      --color "0E8A16" --description "Low priority" --force

# 種別
gh label create "t/bug"      --color "1D76DB" --description "Bug report" --force
gh label create "t/feature"  --color "0075CA" --description "Feature request" --force
gh label create "t/docs"     --color "5319E7" --description "Documentation" --force
gh label create "t/chore"    --color "006B75" --description "Maintenance task" --force
gh label create "t/refactor" --color "0366D6" --description "Code refactoring" --force

# 状態
gh label create "s/in-progress" --color "FEF2C0" --description "Work in progress" --force
gh label create "s/review"      --color "D4C5F9" --description "Ready for review" --force
gh label create "s/blocked"     --color "E4E669" --description "Blocked by dependency" --force

# 領域（プロジェクトに合わせてカスタマイズ）
gh label create "a/skills"  --color "22863A" --description "Skills domain" --force
gh label create "a/dotnet"  --color "1A7F37" --description ".NET domain" --force
gh label create "a/python"  --color "2DA44E" --description "Python domain" --force
gh label create "a/docs"    --color "3FB950" --description "Documentation domain" --force
```

---

## リソース

- [GitHub CLI Label Commands](https://cli.github.com/manual/gh_label)
- [Managing Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub Default Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels#about-default-labels)

---
