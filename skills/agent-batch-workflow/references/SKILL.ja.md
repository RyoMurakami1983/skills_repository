---
name: agent-batch-workflow
description: >
  Run multi-file batch operations with parallel agents and structured progress reporting.
  Use when processing multiple skills, files, or components in a single session with
  quality gates and branch-first discipline.
metadata:
  author: RyoMurakami1983
  tags: [agent, batch, parallel, workflow, horenso, branch-management]
  invocable: true
---

# Agent Batch Workflow

並列AIエージェントを活用した大規模バッチ操作のワークフロー。コスモス化移行のふりかえりで実証された3つの実践を体系化：ブランチファースト規律、3エージェント並列実行（作業2 + レビュー1）、5分間隔の報連相。

## When to Use This Skill

このスキルを使う場面：
- 1セッションで5つ以上のファイルやスキルを処理する
- 複数コンポーネントの一括モダン化・リファクタリング・移行
- コードベース全体へのバッチバリデーション・更新・生成
- 長時間のエージェント操作中に構造化された進捗の可視性が必要
- 作業とコミットの間に品質ゲート（レビューエージェント）を挟みたい

使わない場面：
- 単一ファイルの作業（通常ワークフローで十分）
- 変更前にドメイン調査が必要（先にexploreエージェントを使う）
- 変更が相互依存的で順次実行が必須（並列化の恩恵なし）

## Related Skills

- **`github-pr-workflow`** — バッチ完了後のPR作成（Step 5）
- **`git-commit-practices`** — バッチコミットのフォーマット
- **`git-initial-setup`** — このワークフローが尊重するブランチ保護
- **`furikaeri-practice`** — このワークフローを生み出したふりかえり

---

## Dependencies

- Git 2.30+
- GitHub CLI (`gh`) — `gh auth status` で確認
- SQLツール（タスク追跡用セッションデータベース）
- Taskツール（`general-purpose` と `code-review` エージェントタイプ）

---

## Core Principles

1. **Branch First**（基礎と型）— mainでの作業は一切行わない。`git switch -c` が最初のコマンド。
2. **Decompose Before Executing**（温故知新）— 実行前に作業を追跡可能な単位に分解する。
3. **Parallel With Review**（成長の複利）— 作業2、レビュー1。品質がスピードと共にスケールする。
4. **Report Without Stopping**（継続は力）— 進捗は可視化するが、エージェントは報告のために止まらない。
5. **Batch Commits**（ニュートラルな視点）— 関連変更をアトミックでレビュー可能なコミットにまとめる。

---

## Workflow: バッチ操作の実行

### Step 1: Branch First

変更作業の前にフィーチャーブランチを作成する。これは交渉不可のゲート。

すべてのバッチ操作の開始時に使用。必ず最初に実行するステップ。

> **Values**: 基礎と型 — ブランチが基盤。ブランチなければ作業なし。

```bash
# クリーンな状態を確認
git status --short

# フィーチャーブランチを作成・切替
git switch -c feature/<操作の概要>
```

**命名規則：**
- `feature/cosmos-migration-phase-2` — 新機能・移行
- `refactor/modernize-wpf-skills` — 構造改善
- `fix/validate-frontmatter-all` — バッチバグ修正

**ゲート**: `git switch -c` が失敗したら（ワーキングツリーが汚れている）、stashまたはコミットしてから進む。mainでは絶対に進めない。

### Step 2: Task Decomposition

バッチをSQL todosで追跡可能な単位に分解する。並列実行のために2〜3アイテムずつのバッチにグループ化。

作業の全体スコープを把握した後に使用。エージェント起動前に必ず実行。

> **Values**: 温故知新 — 過去の経験から、追跡されないバッチ作業は漏れや重複を招く。

```sql
-- 全作業アイテムを登録
INSERT INTO todos (id, title, description, status) VALUES
  ('skill-a', 'スキルA モダン化', 'フロントマター更新、JA追加、バリデーション', 'pending'),
  ('skill-b', 'スキルB モダン化', 'フロントマター更新、JA追加、バリデーション', 'pending'),
  ('skill-c', 'スキルC モダン化', 'フロントマター更新、JA追加、バリデーション', 'pending');

-- 依存関係を定義（必要に応じて）
INSERT INTO todo_deps (todo_id, depends_on) VALUES
  ('skill-c', 'skill-a');  -- CはAに依存

-- バッチにグループ化
-- バッチ1: skill-a + skill-b（独立、並列化可能）
-- バッチ2: skill-c（skill-aに依存）
```

**バッチ分割ルール：**
- 独立したアイテムを2〜3個ずつのバッチにグループ化
- 依存関係のあるアイテムは後のバッチへ
- 同種の変更（同じタイプの変更）をまとめる

### Step 3: Parallel Execution

バッチごとに作業エージェント2 + レビューエージェント1を起動。作業者が変更を実行し、レビュー担当が完了した作業を検証。

バッチの実行準備ができたら使用。これがコアの処理ステップ。

> **Values**: 成長の複利 — 並列実行がスループットを倍増。レビューエージェントが品質の複利を保証する。速度だけでなく。

**エージェント構成：**

```
作業Agent 1 (general-purpose) ──→ アイテムA ──→ 完了
作業Agent 2 (general-purpose) ──→ アイテムB ──→ 完了
レビューAgent (code-review)   ──→ A & B を検証
```

**実行フロー：**
1. Worker 1 + Worker 2 を `mode: "sync"` タスクとして起動
2. 両方完了後、レビューエージェントを起動
3. レビューで問題発見 → 修正エージェントを起動 → 再レビュー
4. SQLでアイテムを `done` にマーク

```sql
UPDATE todos SET status = 'in_progress' WHERE id IN ('skill-a', 'skill-b');
-- エージェント完了後：
UPDATE todos SET status = 'done' WHERE id IN ('skill-a', 'skill-b');
```

### Step 4: Progress Reporting (報連相)

5分間隔で進捗を報告。報連相プロトコルで作業の可視性を保ちつつ、エージェントをブロックしない。

バッチ実行が5分を超える場合に使用。全体を通じて可視性を維持。

> **Values**: 継続は力 — 継続的な小さな報告が信頼を築き、問題を早期に発見する。毎回の更新で止まることは、持続的な作業の複利効果を無駄にする。

**報連相プロトコル：**

| 種類 | 説明 | アクション | タイミング |
|------|------|-----------|----------|
| **報告** | 状況を共有 | 作業を止めない | 5分ごと or バッチ完了時 |
| **連絡** | 事実・変化を共有 | 作業を止めない | 予期しないことが起きた時 |
| **相談** | 方向性を確認 | 作業を止めて確認 | 判断が必要な時 |

**判断ルール：**
- 1アイテム失敗 → 連絡（通知）、スキップして続行
- 3+アイテム同じ失敗 → 相談（停止）、ユーザーに確認
- 予期しないスコープ変更発見 → 相談（停止）、確認

### Step 5: Commit and PR

完了したバッチをConventional Commitsでコミットし、PRを作成。

全バッチ完了かつレビューエージェントの検証後に使用。

> **Values**: ニュートラルな視点 — 各コミットがレビュー可能な単位。PRが全体のストーリーを伝える。

**バッチ単位のコミット：**

```bash
git add <バッチ1のファイル>
git commit -m "refactor(scope): アイテムA・Bをモダン化

- フロントマターをnested metadata形式に更新
- JA版を追加（バイリンガル対応）
- バリデーション ≥90% PASS

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

**最終確認：**

```sql
-- 全アイテムがdoneか確認
SELECT id, status FROM todos WHERE status != 'done';
-- 0行が返るべき
```

**PR作成：** `github-pr-workflow` スキルに委譲、または `gh pr create` を直接使用。

---

## Best Practices

- **小さく始める**: 最初のバッチは最も簡単なアイテムでプロセスを検証
- **同質バッチ**: 同じタイプの変更を必要とするアイテムをグループ化
- **コミット前にレビュー**: レビューエージェントの承認なしにコミットしない
- **すべてを追跡**: SQL todosが進捗の唯一の信頼できる情報源
- **素早く失敗、優雅にスキップ**: 1アイテムがブロックされたらスキップして続行

## Common Pitfalls

1. **ブランチステップのスキップ**
   修正: `git switch -c` を文字通り最初のコマンドにする。例外なし。

2. **バッチの過積載**
   修正: バッチは2〜3アイテムに保つ。4以上の並列エージェントは品質を下げる。

3. **毎回の報告で作業を止める**
   修正: デフォルトは報告/連絡。相談のみ停止が必要。

4. **レビューエージェントなし**
   修正: 常にcode-reviewエージェントを1つ含める。品質なき速度はやり直しを生む。

5. **一括コミット**
   修正: バッチ単位でコミット。アトミックなコミットがロールバックとレビューを容易にする。

## Anti-Patterns

- ブランチなしでmainで作業する（このワークフローの意味がなくなる）
- 5+並列エージェントの起動（収穫逓減、コンテキスト混乱）
- 報連相を省略可能と扱う（見えない進捗は重複努力を招く）
- SQL追跡のスキップ（「覚えてる」— 15アイテム目には覚えていない）
- 最終レビューなしでマージ（最後のバッチが最も雑になりがち）

---

## Quick Reference

### 起動チェックリスト

```markdown
1. [ ] `git switch -c feature/xxx`
2. [ ] SQL todosに依存関係付きで登録
3. [ ] バッチにグループ化（2-3アイテム）
4. [ ] 作業エージェントのプロンプト準備
5. [ ] レビューエージェントの基準定義
```

### 報連相 判断テーブル

| 状況 | 種類 | アクション |
|------|------|-----------|
| バッチ正常完了 | 報告 | 進捗報告、続行 |
| 予期しないファイル形式発見 | 連絡 | 通知、適応、続行 |
| 3+アイテム同じ失敗 | 相談 | 停止、ユーザーに確認 |
| スコープが予想より大きい | 相談 | 停止、新スコープ確認 |
| 1アイテム失敗 | 連絡 | 通知、スキップ、続行 |

### Agent Topology

```
┌─────────────────────────────────────────┐
│        バッチコントローラー               │
│（あなた — ワークフローを統制）            │
├──────────┬──────────┬───────────────────┤
│ 作業者1   │ 作業者2   │ レビュー担当      │
│ (gen-p)  │ (gen-p)  │ (code-review)    │
│ アイテムA │ アイテムB │ A & B を検証      │
└──────────┴──────────┴───────────────────┘
```

---

## FAQ

**Q: 1セッションで何アイテム処理できる？**
A: コスモス化移行で22アイテムまでテスト済み。2〜3個のバッチ＋5分報連相で管理可能だった。

**Q: レビューエージェントが問題を見つけたら？**
A: 特定の問題に対して修正エージェントを起動、その後修正ファイルのみ再レビュー。

**Q: 作業エージェントを3つ以上使える？**
A: 非推奨。作業2＋レビュー1がテスト済みのスイートスポット。エージェント増加はコンテキスト混乱とコンフリクトを増やす。

**Q: `git checkout -b` ではなく `git switch -c` を使う理由は？**
A: `git switch -c` はモダンなGitコマンド（2.23+）。このワークフローはこれを標準とする。

**Q: アイテムが外部依存でブロックされたら？**
A: SQLで `blocked` にマーク、descriptionにメモ、バッチからスキップ。バッチ完了後に対処。

---

## Resources

- [コスモス化移行ふりかえり](../../docs/furikaeri/2026-02-22-cosmos-migration.md) — このワークフローの起源
- [Git Switch ドキュメント](https://git-scm.com/docs/git-switch) — モダンなブランチコマンド
- [報連相](https://ja.wikipedia.org/wiki/%E5%A0%B1%E9%80%A3%E7%9B%B8) — 日本のビジネスコミュニケーションプロトコル
