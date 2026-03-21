---
name: github-quality-gate-setup
description: >
  gitleaks と textlint の品質ゲート CI を GitHub リポジトリへ導入する。Use when: 新しいリポジトリに品質ゲートを入れたいとき、既存リポジトリのシークレット漏洩対策や Markdown チェックを強化したいとき。
---
# GitHub 品質ゲートのセットアップ

gitleaks（シークレット検出）とオプションの textlint（Markdown チェック）を
任意の GitHub リポジトリに追加するワークフロー。

**品質ゲート**: PRのたびに自動実行されるチェック。マージ前にセキュリティ問題・
コンテンツ問題を検出する。

## こんなときに使う
このスキルを使うのは：
- 既存リポジトリへの品質ゲートCI追加
- テンプレートリポジトリから作成したリポジトリのカスタマイズ
- `github-repo-template` が提供する内容の確認・変更
- 品質ゲートルールの更新・拡張

> **Tip**: 新規リポジトリの場合は [`github-repo-template`](https://github.com/RyoMurakami1983/github-repo-template) から作成する方が速い。すべてが最初から設定済みで届く。

## Related Skills

- **`git-initial-setup`** — ブランチ保護と `.gitattributes`/`.editorconfig` の設定（事前前提）
- **`knowledge-capture`** — ドキュメントコミット前の匿名化ゲート
- **`github-issue-intake`** — 匿名化チェック付き Issue 起票

---

## Dependencies

- Git 2.30+
- GitHub CLI (`gh`) — `gh auth status` で確認
- textlint 使用時: Node.js 18+

---

## Core Principles

1. **多層防御** (基礎と型) — シークレット検出 + コンテンツ lint の2層で守る。なぜ？ 1つのツールでは検出できない問題を補完できる。
2. **PRでフェールファースト** (継続は力) — すべての PRをゲートする。問題を main に届けない。なぜ？ main へ入ってしまったら修正コストが格段に上がる。
3. **ノイズを最小化** (余白の設計) — Allowlist で誤検知を防ぐ。なぜ？ 誤検知が多いとエンジニアがアラートを無視し始め、ゲートが形骸化する。
4. **言語非依存のコア** (ニュートラル) — gitleaks は任意のリポジトリに適用可能。textlint は Markdown があるときだけ追加。なぜ？ 不要なジョブは CI 時間とメンテコストを増やすだけ。
5. **Allowlist を育てる** (温故知新) — `.gitleaks.toml` を徐々に育てることでゲートが賢くなる。なぜ？ 最初から完璧なルールはない。実運用でのフィードバックが品質を作る。

---

## Workflow: 品質ゲートCIの追加

### Step 1: スコープを確認する

リポジトリの内容に応じて、追加するジョブを決める。

| ジョブ | 追加する条件 |
|--------|------------|
| **gitleaks** | 常に追加 — すべてのリポジトリ |
| **textlint** | Markdownが多いとき（ドキュメント・スキル集・README重視のリポジトリ） |

```bash
# Markdownファイルの量を確認する
find . -name "*.md" | grep -v "^./README.md" | head -5
```

README 以外の `.md` ファイルが複数あれば textlint を追加する。
純粋なコードリポジトリ（dotnet / Python でドキュメントなし）なら gitleaks のみで十分。

> **Values**: 基礎と型

### Step 2: Gitleaks を追加する

ワークフローテンプレートをコピーし、allowlist をカスタマイズする。

```bash
mkdir -p .github/workflows
cp /path/to/skills/github-quality-gate-setup/scripts/quality.yml \
   .github/workflows/quality.yml
cp /path/to/skills/github-quality-gate-setup/scripts/.gitleaks.toml \
   .gitleaks.toml
```

`.gitleaks.toml` を開き、プロジェクト固有の allowlist エントリを追加する：

```toml
[[allowlists]]
description = "プロジェクト固有のプレースホルダー"
regexes = [
  # ドキュメント例示に使っているが本物のシークレットではないパターンを追加
  '''YOUR[_-]?API[_-]?KEY''',
]
```

> **Note**: `pull_request` トリガーで実行すると、gitleaks は自動的に PR 差分のみをスキャンする。追加設定は不要。

> **Values**: 基礎と型 / 余白の設計

### Step 3: Textlint を追加する（省略可）

リポジトリに Markdown コンテンツが少ない場合はスキップする。

```bash
cp /path/to/skills/github-quality-gate-setup/scripts/.textlintrc.json .
cp /path/to/skills/github-quality-gate-setup/scripts/package.json .
npm install
```

次に、`.github/workflows/quality.yml` の **textlint ジョブのコメントを外す**：

```yaml
# コメントマーカーを外して textlint ジョブを有効化
  textlint:
    name: textlint
    ...
```

ローカルで確認（省略可 — CI が正式なチェック）：

```bash
npx textlint "**/*.md" --ignore-path .gitignore
```

> **Values**: ニュートラル

### Step 4: コミット & プッシュ → PR

```bash
# フィーチャーブランチを作成
git switch -c feature/add-quality-gate

git add .github/workflows/quality.yml .gitleaks.toml

# textlint を追加した場合:
git add .textlintrc.json package.json package-lock.json

git commit -m "feat: gitleaks + textlint 品質ゲートCIを追加

Why: PR での固有名詞・シークレット漏洩を自動検出するゲートを設置。

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git push -u origin feature/add-quality-gate
```

その後、`github-pr-workflow` スキルで PR を作成する。

> **Values**: 継続は力

### Step 5: Branch Protection を設定する（手動）

CI ワークフローが main にマージされた後、手動でブランチ保護を設定する：

1. GitHub → Settings → Branches → `main` ルールを編集
2. **Require status checks to pass before merging** を有効化
3. `gitleaks` を検索して追加
4. textlint を追加した場合は `textlint` も追加
5. 保存

> **Values**: 基礎と型

---

## Best Practices

- まず gitleaks のみで始め、Markdown が多ければ textlint を追加する
- `.gitleaks.toml` の allowlist は段階的に育てる — 誤検知が出たタイミングで追加
- ドキュメント例示には `YOUR_API_KEY_HERE` スタイルのプレースホルダーを使い誤検知を防ぐ
- textlint を使う場合は `package-lock.json` をコミットする — `npm ci` に必要
- Markdown がないリポジトリは gitleaks のみにして CI オーバーヘッドを最小化

### Preflight Checklist

- [ ] `gh auth status` が成功している（workflow スコープが必要）
- [ ] フィーチャーブランチを作成済み（main ではない）
- [ ] `.gitleaks.toml` の allowlist をリポジトリのドキュメント例示に合わせてチューニング済み
- [ ] textlint: Markdownの量に応じて追加するか判断済み

### Self-Review Checklist

- [ ] `.github/workflows/quality.yml` が `pull_request` トリガーで動作する
- [ ] gitleaks ジョブが `gitleaks-action@v2` + `GITHUB_TOKEN` を使用している
- [ ] textlint を追加した場合: `package-lock.json` がコミット済み、既存ファイルでルールが通る
- [ ] マージ後に Branch Protection を更新した

---

## Common Pitfalls

1. **`.github/workflows/*` へのプッシュが拒否される**
   原因: トークンに `workflow` スコープがない。
   対処: `gh auth refresh -h github.com -s workflow`

2. **textlint「No rules found」エラー**
   原因: `filters.comments` など、未インストールのフィルタパッケージを参照している。
   対処: 該当のフィルタエントリを削除するか、パッケージをインストールする。

3. **gitleaks がドキュメント例示で誤検知する**
   原因: Markdown 内の例示 API キー / トークンが gitleaks パターンにマッチ。
   対処: `.gitleaks.toml` の `[[allowlists]]` にパターンを追加。

4. **textlint `no-empty-section` エラー**
   原因: 見出しの後、次の見出しまでにコンテンツがない（空セクション）。
   対処: 空の見出しを削除するかコンテンツを追加。

---

## Anti-Patterns

- `.github/workflows/` の変更をマージしたのに Branch Protection の必須チェックを設定しない
- allowlist を空にして、全 gitleaks 検知をグローバル ignore で抑制する
- Markdown がほとんどないリポジトリに textlint を追加して不要な CI オーバーヘッドを作る

---

## Quick Reference

### 判断テーブル（Decision Table）: gitleaks のみ vs. gitleaks + textlint

```
リポジトリに README 以外の .md ファイルが多い？
  ├── YES → gitleaks + textlint
  └── NO  → gitleaks のみ
```

### gitleaks のみの最小ワークフロー

```yaml
name: Quality Gate
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  gitleaks:
    name: gitleaks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### テンプレートファイルの場所

```
skills/github-quality-gate-setup/scripts/
├── quality.yml         # フルワークフロー（textlintジョブはコメントアウト）
├── .gitleaks.toml      # 基本 allowlist
├── .textlintrc.json    # textlint ルール
└── package.json        # textlint npm 依存関係
```

---

## FAQ

**Q: gitleaks に有料ライセンスは必要？**
A: 不要。公開リポジトリでは `gitleaks-action@v2` は `GITHUB_TOKEN` だけで動作する。

**Q: textlint に禁止語辞書を追加するには？**
A: `textlint-rule-no-restricted-syntax` をインストールするか、カスタムワードリストファイルを作成して `.textlintrc.json` で参照する。

**Q: gitleaks が履歴に含まれる本物のシークレットを見つけた場合は？**
A: 即座にシークレットをローテーション（無効化）する。その後 `git filter-repo` または BFG で履歴から削除し、force-push する。

**Q: detect-secrets との使い分けは？**
A: gitleaks が導入が軽くて始めやすい。detect-secrets はベースラインファイル（`.secrets.baseline`）で「許容済み」のものを管理できるため、誤検知の多い環境では有効。

---

## Resources

- [gitleaks-action](https://github.com/gitleaks/gitleaks-action)
- [gitleaks 設定ガイド](https://github.com/gitleaks/gitleaks#configuration)
- [textlint ルール一覧](https://github.com/textlint/textlint/wiki/Collection-of-textlint-rule)
- [github-repo-template](https://github.com/RyoMurakami1983/github-repo-template)
