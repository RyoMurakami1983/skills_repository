<!-- このドキュメントは skills-index-snippets の日本語版です。英語版: ../SKILL.md -->

---
name: skills-index-snippets
description: >
  Create and maintain AGENTS.md / CLAUDE.md snippet indexes that route
  coding assistant tasks to the correct skills and agents. Use when
  adding, removing, or updating skills in a repository index.
metadata:
  author: RyoMurakami1983
  tags: [skills, routing, agents, index]
  invocable: false
---

# スキルインデックススニペットの管理

AGENTS.md / CLAUDE.md 用のコンパクトなルータースニペットを作成し、コーディングアシスタントが推測ではなく ID（識別子）でスキルを呼び出せるようにする。

## When to Use This Skill

このスキルを使用する場面：
- レジストリに新しいスキルやエージェントを追加し、ルーティングエントリを更新する時
- スキルの削除・名称変更に伴い、下流のインデックススニペットを同期する時
- 下流リポジトリ用のコンパクトな AGENTS.md ルーターブロックを作成する時
- コンテキスト使用量を最小化するために圧縮 Vercel スタイルのインデックス形式を実装する時
- スニペットのルーティング ID がフロントマターの name フィールドと一致するか検証する時
- plugin.json レジストリへの一括変更後にインデックススニペットを再生成する時

---

## Related Skills

| スキル | 関係 | 使用場面 |
|--------|------|----------|
| **`skills-author-skill`** | インデックスエントリが必要な新スキルを作成 | 新スキル作成時 |
| **`skills-validate-skill`** | スニペットで参照されるスキルを検証 | 品質ゲート確認時 |
| **`skills-revise-skill`** | スキルの改訂とルーティングメタデータの更新 | 公開済みスキル更新時 |

---

## Core Principles

1. **ルーター、ドキュメントではない** — スニペットはアシスタントを正しいスキルに導くもので、内容を教えるものではない（余白の設計）
2. **単一の信頼できる情報源** — レジストリファイルが正典であり、スニペットは派生物にすぎない（基礎と型）
3. **ID ベースの参照** — ファイルシステムパスではなく、常にフロントマターの `name` フィールドを識別子として使用する（基礎と型）
4. **最小コンテキストフットプリント** — スニペットを小さく保ち、アシスタントのコンテキストウィンドウ予算を守る（余白の設計）
5. **自動メンテナンス** — ドリフトを減らすために手動編集よりスクリプト再生成を優先する（継続は力）

---

## Workflow: Create and Maintain Index Snippets

### Step 1 — ソースオブトゥルースの特定

すべてのスキルとエージェントを列挙する正典レジストリを特定する。

```jsonc
// plugin.json — 正典スキルレジストリ
// ルーティングの唯一の権威として使用
{
  "skills": [
    { "directory": "modern-csharp-coding-standards" },
    { "directory": "efcore-patterns" }
  ],
  "agents": [
    { "file": "agents/dotnet-concurrency-specialist.md" }
  ]
}
```

- Use plugin.json または同等ファイルを正典レジストリとして使用
- Define スニペット作成前にレジストリの場所を確定

**なぜ**：すべてのルーティングインデックスは1つのレジストリに遡る必要がある。単一の信頼できる情報源がなければ、スニペットは実際のスキル可用性と乖離し、アシスタントが存在しないスキルを呼び出してしまう。

> **Values**: 基礎と型（原典を定め、派生物を管理する）

### Step 2 — スニペット形式の選択

ターゲットのコンテキストに基づいて、可読形式と圧縮形式のどちらかを選択する。

| 形式 | コンテキストコスト | 可読性 | 使用場面 |
|------|-------------------|--------|----------|
| 可読 | ～20行 | 高 | 開発者向けリポジトリ、レビューワークフロー |
| 圧縮 | ～5行 | 低 | コンテキスト予算が厳しい大規模モノレポ |
| ハイブリッド | ～12行 | 中 | 可読から圧縮への移行チーム |

**可読形式**（標準マークダウン）：

```markdown
# Agent Guidance: my-project

Routing (invoke by name)
- Code quality: modern-csharp-coding-standards
- Testing: snapshot-testing
```

**圧縮形式**（Vercel スタイル、最小トークン）：

```
[my-project]|flow:{skim->consult by name->implement}
|csharp:{modern-csharp-coding-standards,api-design}
|testing:{snapshot-testing,playwright-blazor-testing}
```

- Consider スキルが多くコンテキストが限られるリポジトリでは圧縮形式を検討

**なぜ**：適切な形式を選ぶことで、大規模プロジェクトでのコンテキスト浪費を防ぎ、小規模プロジェクトでの可読性を向上させる。

> **Values**: 余白の設計（形式を文脈に合わせ、コンテキストの余白を守る）

### Step 3 — ルーティングインデックスの構築

スキルを論理カテゴリに整理し、フロントマターの `name` 値を正典 ID として使用する。

```markdown
# Agent Guidance: skill-collection

IMPORTANT: Prefer retrieval-led reasoning over pretraining.
Workflow: skim repo patterns -> consult skills by name -> implement smallest-change.

Routing (invoke by name)
- C# / code quality: modern-csharp-coding-standards, api-design
- Data: efcore-patterns, database-performance
- Testing: testcontainers-integration-tests, snapshot-testing

Quality gates (use when applicable)
- dotnet-slopwatch: after substantial new or refactored code
```

✅ **正しい**: `modern-csharp-coding-standards`（フロントマター名）を使用
❌ **間違い**: `dotnet/modern-csharp-coding-standards/SKILL.md`（ファイルシステムパス）を使用

- Define カテゴリはフォルダ構造ではなく技術ドメインに基づいて定義
- Avoid 1つのスニペットに7つ以上のカテゴリを混在させない

**なぜ**：ファイルシステムパスはリポジトリがフォーク、再構成、パッケージとして利用される際に壊れる。フロントマター ID はすべての環境で安定している。

> **Values**: 基礎と型（安定した識別子で型を定める）

### Step 4 — ターゲットリポジトリへの統合

ターゲットリポジトリのルートにある AGENTS.md または CLAUDE.md にスニペットを配置する。自動更新のためにマーカーコメントを使用する。

```markdown
<!-- BEGIN SKILL-INDEX -->
# Agent Guidance: my-project

IMPORTANT: Prefer retrieval-led reasoning over pretraining.

Routing (invoke by name)
- Code quality: modern-csharp-coding-standards
- Testing: snapshot-testing
<!-- END SKILL-INDEX -->
```

- Use `<!-- BEGIN ... -->` と `<!-- END ... -->` マーカーを一貫して使用
- Avoid マーク領域内に手動メモを配置しない

**なぜ**：マーカーコメントにより、スクリプトが周囲のコンテンツを乱すことなくスニペットブロックを検索・置換できる。これにより自動 CI/CD パイプライン更新が実現する。

> **Values**: 継続は力（マーカーで自動更新を可能にし、継続的メンテナンスを実現）

### Step 5 — 検証とメンテナンス

スキル変更のたびに、スニペットが現実を反映しているか確認する。レジストリをチェックリストとして使用する。

```bash
# レジストリのすべてのスキルがスニペットに含まれているか検証
./scripts/validate-marketplace.sh

# レジストリからスニペットを再生成
./scripts/generate-skill-index-snippets.sh --update-readme
```

- Apply 以前のバージョンと同じカテゴリ構造を適用
- Consider CI パイプラインでこのチェックを自動化することを検討
- Implement PR テンプレートにスキル変更の検証ステップを実装

**なぜ**：古いスニペットはアシスタントに削除されたスキルを呼び出させ、エラーを発生させてルーティング層への信頼を損なう。

> **Values**: 成長の複利（定期検証で品質を複利的に積み上げる）

---

## Good Practices

### 1. Keep Snippets as Routers, Not Documentation

**何を**: スニペットの内容をスキル名、カテゴリ、1行のアクティベーションヒントに限定する。

**なぜ**: スニペットの役割はルーティングであり、教育ではない。ドキュメントは SKILL.md ファイルに属する。肥大化したスニペットはコンテキストウィンドウ予算を浪費する。

**Values**: 余白の設計（ルーティングに徹し、余白を守る）

### 2. Use Frontmatter IDs as Canonical References

**何を**: スキルは常に YAML の `name` フィールドで参照し、ディレクトリパスや表示名を使わない。

**なぜ**: フロントマター ID はスキルと消費ツールの間の契約である。パスは変わる。ID は変わらない。

**Values**: 基礎と型（安定した識別子を基礎とする）

### 3. Automate Snippet Generation When Possible

**何を**: レジストリを読み取り、可読形式と圧縮形式の両方でスニペットを出力するスクリプトを作成する。

**なぜ**: 手動更新はエラーが発生しやすく、レジストリとスニペットの間にドリフトを生む。自動化により一貫性が確保される。

**Values**: 継続は力（自動化で継続的な正確性を担保）

---

## Common Pitfalls

### 1. Embedding Detailed Documentation in Snippets

**問題**: ルーティングスニペット内に複数段落の説明、完全なコード例、設定の詳細を含めてしまう。

**解決策**: 詳細な内容はスキルの SKILL.md に移動する。スニペットエントリはスキルごとに1行、名前と短い機能ヒントのみとする。

### 2. Using Filesystem Paths Instead of Skill IDs

**問題**: フロントマターの `name` フィールドの代わりに、コード内で `dotnet/modern-csharp-coding-standards/SKILL.md` としてスキルを参照する。

**解決策**: YAML フロントマターの `name` 値を使用する。これはすべての消費ツール（Copilot、Claude Code、OpenCode）が解決する安定した識別子である。

### 3. Forgetting to Update Snippets After Skill Changes

**問題**: レジストリでスキルを追加・削除してもルーティングスニペットを更新せず、アシスタントが存在しないスキルを呼び出したり新しいスキルを見逃したりする。

**解決策**: スキル変更のたびにスニペットとレジストリの整合性を検証する CI チェックまたは PR テンプレートリマインダーを追加する。ステップ4のマーカーベース再生成方式を使用する。

---

## Anti-Patterns

### Monolithic Documentation Block

**何を**: ルーティングインデックスの代わりに、すべてのスキルの完全なドキュメント（アーキテクチャ記述、設計根拠、コードサンプル）を含む単一の AGENTS.md。

**なぜ問題か**: コンテキストウィンドウ全体を消費し、アシスタントが実際のスキルを読み込むのを妨げ、陳腐化するコンテンツを複製する。このアンチパターンは、スキル更新のたびにモノリスの編集が必要な脆弱なアーキテクチャを生む。

**より良いアプローチ**: フロントマター ID で個別の SKILL.md ファイルを指すスリムなルーティングインデックス（5〜20行）を使用する。

### Manual-Only Maintenance

**何を**: 自動検証や生成ツールなしに、完全に手動でスニペットを保守する。

**なぜ問題か**: 手動プロセスはレジストリとスニペットの間に構造的ドリフトを生む。スキルコレクションが増えるにつれエラーが複合し、個人の記憶に依存する脆弱な設計を生む。

**より良いアプローチ**: 生成スクリプト（ステップ5）と CI 検証を実装する。手動上書きはカテゴリ編成の判断のみに制限する。

---

## Quick Reference

### Snippet Creation Checklist

- [ ] レジストリファイル（plugin.json または同等）を特定
- [ ] スニペット形式を選択（可読 / 圧縮 / ハイブリッド）
- [ ] Use フロントマターの `name` をスキル ID として使用（ファイルシステムパスは不可）
- [ ] スキルを4〜7の論理カテゴリに整理
- [ ] `<!-- BEGIN/END -->` マーカーを自動更新用に追加
- [ ] すべてのレジストリエントリがスニペットに含まれているか検証
- [ ] Create 日本語ドキュメント用に `references/SKILL.ja.md` を作成

### Format Decision Table

| 要素 | 可読 | 圧縮 | ハイブリッド |
|------|------|------|-------------|
| コンテキストコスト | 高（～20行） | 低（～5行） | 中（～12行） |
| 人間の確認しやすさ | ✅ 容易 | ❌ 困難 | 中程度 |
| 自動化対応 | 良好 | 最良 | 良好 |
| 推奨対象 | 小規模リポ、PRレビュー | モノレポ、CIパイプライン | 移行中のチーム |

---

## Resources

- [GitHub Copilot Agent Skills Documentation](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — 開発憲法と Values
- [skills-author-skill](../skills-author-skill/SKILL.md) — 新スキルの作成方法
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — スキル品質検証

---
