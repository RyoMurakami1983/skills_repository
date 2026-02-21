---
name: dotnet-marketplace-publishing
description: >
  Publish skills and agents to the dotnet-skills Claude Code marketplace.
  Use when adding new skills, registering agents, updating plugin.json,
  or releasing a new marketplace version.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, marketplace, publishing, claude-code, skills]
  invocable: false
---

<!-- このドキュメントは dotnet-marketplace-publishing の日本語版です。英語版: ../SKILL.md -->

# Marketplace Publishing Workflow

dotnet-skills Claude Code マーケットプレイスへスキルやエージェントを公開するためのステップバイステップガイドです。フォルダ構成、SKILL.md の作成、plugin.json 登録、バリデーション、セマンティックバージョニングによるリリースをカバーします。

**略語**: YAML（YAML Ain't Markup Language）、JSON（JavaScript Object Notation）、CLI（Command-Line Interface）、CI（Continuous Integration）、DI（Dependency Injection）。

## When to Use This Skill

- マーケットプレイスリポジトリに新しいスキルフォルダと SKILL.md を追加する場合
- エージェント定義を agents ディレクトリと plugin.json レジストリに登録する場合
- 新しく作成したスキルやエージェントのパスを plugin.json に追加する場合
- バリデーションスクリプトでマーケットプレイス構造を検証してからコミットする場合
- plugin.json のセマンティックバージョンを更新し、配布用リリースタグを作成する場合
- マーケットプレイスインストール後にスキルが見つからない、またはバリデーションエラーが出る場合のトラブルシューティング
- 新しいスキルの技術ドメインに基づいて正しいカテゴリフォルダを選択する場合
- 既存のスキル投稿のフロントマターと完全性をレビューする場合

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-modern-csharp-coding-standards` | スキルコンテンツで参照される C# コーディング標準 |
| `dotnet-project-structure` | スキル例で使用される .NET プロジェクトレイアウト規約 |
| `dotnet-package-management` | スキル内の NuGet 依存関係ドキュメント |

## Core Principles

1. **Single Source of Truth** — すべてのスキルとエージェントを `plugin.json` に登録する。マーケットプレイスカタログはこのファイルを読んで利用可能なコンテンツを検出するため、重複や孤立エントリはインストール失敗の原因になる。
2. **Convention Over Configuration** — `skills/<category>/<name>/SKILL.md` のパス規約に従う。一貫した構造により自動バリデーションが可能になり、コントリビューターのオンボーディング負荷が低減される。
3. **Atomic Commits** — スキルフォルダと `plugin.json` の更新を同時にコミットする。別々のコミットではレジストリが不整合状態になり、存在しないファイルを参照するパスが残る。
4. **Semantic Versioning** — すべてのリリースタグに MAJOR.MINOR.PATCH バージョニングを適用する。利用者はバージョン番号を見て更新判断や破壊的変更の有無を確認する。

> **Values**: 基礎と型の追求（規約に従った構造が、自動バリデーションと再利用性を最大化する）, 継続は力（小さなスキルをコツコツ追加し、マーケットプレイスの価値を複利で積み上げる）

## Workflow: Publish to Marketplace

### Step 1: Choose the Category Folder

`skills/` 配下の適切なカテゴリフォルダを選択する。該当するドメインがなければ新規フォルダを作成する。

| カテゴリ | 用途 | スキル例 |
|----------|------|----------|
| `akka/` | Akka.NET アクターパターン、クラスタリング、テスト | `best-practices`, `testing-patterns` |
| `aspire/` | .NET Aspire オーケストレーションと設定 | `service-defaults`, `dashboard` |
| `csharp/` | C# 言語機能とコーディング標準 | `modern-csharp`, `pattern-matching` |
| `testing/` | テストフレームワーク（xUnit、Playwright） | `testcontainers`, `snapshot-testing` |
| `meta/` | マーケットプレイス自体に関するメタスキル | `marketplace-publishing` |

```bash
# カテゴリの確認
ls skills/

# 必要に応じて新規カテゴリを作成
mkdir -p skills/newcategory/
```

> **Values**: 余白の設計（カテゴリ構造に余白を残し、将来のドメイン拡張を容易にする）

### Step 2: Create the Skill Folder and SKILL.md

ケバブケースのフォルダを作成し、その中に `SKILL.md` ファイルを1つ配置する。バリデーションスクリプトはこの構造を前提としている。

```bash
# スキルフォルダの作成
mkdir -p skills/akka/cluster-sharding/
```

有効な YAML フロントマターを含む SKILL.md を記述する：

```yaml
---
name: cluster-sharding
description: >
  Implement Akka.NET Cluster Sharding for distributed
  entity management. Use when designing sharded actors.
---
```

**要件チェックリスト：**

| フィールド | ルール | 例 |
|-----------|--------|-----|
| `name` | 小文字ケバブケース、フォルダ名と一致 | `cluster-sharding` |
| `description` | 1〜2文、"use when" トリガーを含む | 上記参照 |
| コンテンツ | 10〜40 KB、具体的なコード例 | C# 12+ パターン |

> **Values**: 基礎と型の追求（フロントマターの型を守ることで、自動検出と品質検証が機能する）

### Step 3: Register the Skill in plugin.json

`.claude-plugin/plugin.json` の `skills` 配列にスキルパスを追加する。未登録のスキルはマーケットプレイスインストーラーから見えない。

```json
{
  "skills": [
    "./skills/akka/best-practices",
    "./skills/akka/cluster-sharding"
  ]
}
```

- ✅ `./skills/` で始まる相対パスを使用する
- ✅ SKILL.md ファイルではなくフォルダを指定する
- ❌ 末尾カンマは使わない — JSON では許可されていない
- ❌ 重複エントリは避ける — 各パスは一意であること

> **Values**: ニュートラルな視点（plugin.json は機械可読な唯一の登録簿であり、曖昧さを排除する）

### Step 4: Add an Agent (Optional)

`/agents/` にモデルと説明のメタデータを含むエージェント Markdown ファイルを作成する。エージェントは専門的なドメイン知識でマーケットプレイスを拡張する。

```markdown
---
name: akka-net-specialist
description: >
  Expert in Akka.NET actor model patterns.
  Use for actor design and cluster configuration.
model: sonnet
color: blue
---

You are an Akka.NET specialist with deep expertise in actor systems.
```

plugin.json にエージェントを登録する：

```json
{
  "agents": [
    "./agents/akka-net-specialist"
  ]
}
```

| フィールド | 必須 | 値 |
|-----------|------|-----|
| `name` | はい | 小文字ケバブケース |
| `description` | はい | 1〜2文、"use for" トリガーを含む |
| `model` | はい | `haiku`、`sonnet`、または `opus` |
| `color` | いいえ | UI 表示ヒント |

> **Values**: 成長の複利（エージェントを追加するほど、チーム全体が利用できる専門知識が増幅する）

### Step 5: Validate the Marketplace

コミット前にバリデーションスクリプトを実行する。CI がインバリッドな構造を拒否するため、ローカルでエラーを検出することで時間を節約できる。

```bash
# マーケットプレイスバリデーション実行
./scripts/validate-marketplace.sh

# JSON 構文を個別にチェック
jq . .claude-plugin/plugin.json
```

**バリデーション項目：**

- SKILL.md に `name` と `description` を含む有効な YAML フロントマターがある
- スキルフォルダが適切なカテゴリ配下にある
- plugin.json のパスが実際のフォルダ構造と一致する
- エージェントファイルに有効な `model` 値が指定されている
- 孤立エントリがない（存在しないフォルダを指すパスがない）

> **Values**: 温故知新（バリデーションスクリプトという「型」を守ることで、過去の失敗パターンを繰り返さない）

### Step 6: Commit and Release

スキルとレジストリの更新をアトミックにコミットする。別々のコミットはマーケットプレイスを不整合状態にするリスクがある。

```bash
# アトミックコミット — スキルとレジストリを一緒に
git add skills/akka/cluster-sharding/ .claude-plugin/plugin.json
git commit -m "feat: add cluster-sharding skill for Akka.NET Cluster Sharding"

# リリース用バージョンバンプ
# まず plugin.json のバージョンを更新してから：
git add .claude-plugin/plugin.json
git commit -m "chore: bump version to 1.1.0"

# タグ作成とプッシュ
git tag v1.1.0
git push origin master --tags
```

**セマンティックバージョニングルール：**

| 変更種別 | バージョンバンプ | 例 |
|----------|-----------------|-----|
| 破壊的変更（スキルの名前変更/削除） | MAJOR | 1.0.0 → 2.0.0 |
| 新しいスキルまたはエージェントの追加 | MINOR | 1.0.0 → 1.1.0 |
| 既存コンテンツの修正 | PATCH | 1.0.0 → 1.0.1 |

GitHub Actions が自動的に構造をバリデーションし、リリースノート付きのリリースを作成する。

> **Values**: 継続は力（小さなリリースをコツコツ積み上げることで、マーケットプレイスの信頼性が向上する）

## Good Practices

- ✅ フロントマターの `name` をケバブケースのフォルダ名と完全一致させる
- ✅ スキル説明に "use when" トリガーフレーズを含めて発見可能性を高める
- ✅ スキルフォルダと plugin.json の変更を単一のアトミックコミットにまとめる
- ✅ セマンティックバージョニングを一貫して適用する — 新コンテンツは MINOR、修正は PATCH
- ✅ プッシュ前にローカルで `validate-marketplace.sh` を実行して CI 失敗を防ぐ
- ✅ スキルコンテンツにモダン C# パターンの具体的なコード例を含める
- ✅ スキルトピックごとに 10〜40 KB の包括的なカバレッジを提供する
- ✅ スキルコンテンツで略語を初出時に展開する（例：DI、DTO、CI）

## Common Pitfalls

1. **plugin.json 更新忘れ** — スキルフォルダを追加したが登録を忘れた。インストーラーからスキルが見えなくなる。修正：両方を常に一緒にコミットする。
2. **JSON の末尾カンマ** — JSON は配列の末尾カンマを許可しない。修正：コミット前に `jq .` で構文を検証する。
3. **名前の不一致** — フロントマターの `name` がフォルダ名と異なる。修正：両者のケバブケースの完全一致を確認する。
4. **SKILL.md の欠落** — フォルダは作成したが中に SKILL.md ファイルがない。修正：マーケットプレイススクリプトでバリデーションする。
5. **コミット分割** — スキルフォルダと plugin.json を別々にコミットする。修正：両方を `git add` してから単一の `git commit` を実行する。
6. **不正な model 値** — エージェントメタデータでサポートされていないモデル名を使用する。修正：`haiku`、`sonnet`、`opus` のみ使用する。

## Anti-Patterns

### ❌ Orphan Registry Entry → ✅ Validated Path

```json
// ❌ BAD — 存在しないフォルダを指すパス
{ "skills": ["./skills/akka/nonexistent-skill"] }
// ✅ GOOD — 実際のフォルダ構造と一致するパス
{ "skills": ["./skills/akka/cluster-sharding"] }
```

孤立エントリはサイレントなインストール失敗を引き起こす。バリデーションスクリプトで検出可能。

### ❌ Split Commits → ✅ Atomic Commit

```bash
# ❌ BAD — 2つの別々のコミットでレジストリが不整合に
git add skills/akka/cluster-sharding/
git commit -m "Add skill"
git add .claude-plugin/plugin.json
git commit -m "Register skill"

# ✅ GOOD — 単一のアトミックコミット
git add skills/akka/cluster-sharding/ .claude-plugin/plugin.json
git commit -m "feat: add cluster-sharding skill"
```

最初のコミットが2番目なしでデプロイされると、レジストリが壊れる。

### ❌ Unversioned Release → ✅ Semantic Version Tag

```bash
# ❌ BAD — plugin.json のバージョンバンプなしのタグ
git tag latest
# ✅ GOOD — バージョンバンプ + semver タグ
# (plugin.json のバージョンを 1.1.0 に更新後)
git tag v1.1.0
```

利用者は semver を見て破壊的変更の有無を判断する。

## Quick Reference

### Publishing Decision Table

| タスク | 主なアクション | コミット対象 |
|--------|---------------|-------------|
| スキル追加 | `skills/<cat>/<name>/SKILL.md` を作成 | スキルフォルダ + plugin.json |
| エージェント追加 | `agents/<name>.md` を作成 | エージェントファイル + plugin.json |
| 既存スキル修正 | SKILL.md コンテンツを編集 | スキルファイルのみ |
| バージョンリリース | バージョンバンプ、タグ作成 | plugin.json + git タグ |

### User Installation Commands

```bash
# マーケットプレイスを追加（初回のみ）
/plugin marketplace add Aaronontheweb/dotnet-skills

# プラグインをインストール（全スキル・エージェント取得）
/plugin install dotnet-skills

# 最新バージョンに更新
/plugin marketplace update
```

### Troubleshooting Quick Reference

| 問題 | 原因 | 修正方法 |
|------|------|----------|
| スキルが表示されない | plugin.json エントリ欠落 | パスを追加して再インストール |
| バリデーションエラー | JSON 構文が無効 | `jq .` を実行してエラーを特定 |
| リリースが作成されない | タグ形式が不正 | `v1.0.0` の semver 形式を使用 |
| エージェントが読み込めない | `model` フィールド欠落 | `haiku`、`sonnet`、`opus` を追加 |

## Resources

- [Claude Code Plugin System](https://docs.anthropic.com/claude-code/plugins) — 公式プラグインドキュメント
- [Semantic Versioning 2.0.0](https://semver.org/) — バージョニング仕様
- [Conventional Commits](https://www.conventionalcommits.org/) — リリースで使用されるコミットメッセージ形式
- [JSON Specification](https://www.json.org/) — plugin.json 編集のための JSON 構文リファレンス
