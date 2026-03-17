# Skills ディレクトリ

 GitHub Copilot Agent Skills — 21スキル

## 📋 概要

**設計方針**: 「1 Skill = 1 Workflow」— 各スキルは単一ワークフローに特化し、詳細は `references/` へ逃がします。

## 📦 スキル一覧

### スキルメタ系（単一入口）

| Skill | 説明 |
| --- | --- |
| [skill](skill/) | スキルの作成・改善・検証・評価を統合管理するルーター。`sub_skills/`、`_foundation/`、`_eval/`、`scripts/` を内包 |

### 言語別入口

| Skill | 説明 |
| --- | --- |
| [dotnet](dotnet/) | 広い `.NET` / `C#` / `WPF` 相談を既存 dotnet skill や deploy workflow へ案内する薄い入口 skill |

### 日常運用入口

| Skill | 説明 |
| --- | --- |
| [github](github/) | 「プルリクして」「レビュー対応して」「Issue登録して」などの広い GitHub 依頼を既存 workflow skill へ案内する薄い入口 skill |

### Git / GitHub ワークフロー

| Skill | 説明 |
| --- | --- |
| [github](github/) | GitHub 日常運用の薄い入口 |
| [git-commit-practices](git-commit-practices/) | Conventional Commits + アトミックコミット |
| [git-init-to-github](git-init-to-github/) | ローカル初期化 → GitHub push（新規プロジェクト） |
| [git-initial-setup](git-initial-setup/) | init/clone 後の main 保護設定 |
| [git-ops-folder-init](git-ops-folder-init/) | 業務フォルダの git 初期化（製造業向け） |
| [github-pr-workflow](github-pr-workflow/) | PR 作成 → Issue 連携 → レビュー待機 |
| [github-pr-review-response](github-pr-review-response/) | レビューコメント分類・修正・再レビュー依頼 |
| [github-issue-intake](github-issue-intake/) | スコープ外作業を GitHub Issue に起票 |
| [github-quality-gate-setup](github-quality-gate-setup/) | gitleaks + textlint CI 設定 |
| [github-repo-label-setup](github-repo-label-setup/) | プレフィックス命名のラベル体系構築 |

### セッション・オーケストレーション

| Skill | 説明 |
| --- | --- |
| [session-issue-autopilot](session-issue-autopilot/) | Issue→実装→PR→レビュー応答のフル自動操縦 |
| [agent-batch-workflow](agent-batch-workflow/) | 並列エージェントによるバッチ処理 |
| [agent-explain-on-demand](agent-explain-on-demand/) | エージェント動作のオンデマンド説明 |

### デプロイ

| Skill | 説明 |
| --- | --- |
| [dotnet-skill-deploy](dotnet-skill-deploy/) | .NET スキルをプロジェクトに配備 |
| [python-skill-deploy](python-skill-deploy/) | Python スキルをプロジェクトに配備 |

### ドメイン特化

| Skill | 説明 |
| --- | --- |
| [furikaeri-practice](furikaeri-practice/) | KPT/YWT によるふりかえりワークフロー |
| [knowledge-capture](knowledge-capture/) | 匿名化ゲート付きナレッジキャプチャ |
| [notion-safe-operations](notion-safe-operations/) | Notion MCP 操作のプリフライトチェック |
| [project-dev-constitution](project-dev-constitution/) | プロジェクト固有の開発憲法づくり |

## 🚀 標準ワークフロー

### 新しい Skill を作成・改善する場合

1. `skill` で現在地点を判定する
2. `skill/sub_skills/new` または `skill/sub_skills/improve` へ進む
3. `skill/_eval/scripts/validate_skill.py` で L1-L2 を確認する
4. 振る舞い確認が必要なら `skill/sub_skills/evaluate` へ進む

### GitHub 実装→PR→レビュー応答

| フェーズ | スキル | 役割 |
| --- | --- | --- |
| 入口 | `github` | 広い GitHub 依頼を PR / review / issue workflow に振り分ける |
| コミット整形 | `git-commit-practices` | 「コミットして」を atomic commit 標準として解釈 |
| PR作成 + 待機 | `github-pr-workflow` | ブランチ状態確認、PR作成、シグナル駆動待機 |
| レビュー応答 | `github-pr-review-response` | コメント分類、修正、再レビュー依頼 |
| マージ判断 | Human handoff | 人間が判断 |
| セッション包み | `session-issue-autopilot` | 上位オーケストレーター |

### Daily operations quick map

| ユーザーの言い方 | 第一入口 | 標準解釈 |
| --- | --- | --- |
| 「コミットして」 | `git-commit-practices` | 原則として atomic commit を作る依頼 |
| 「プルリクして」 | `github` または `github-pr-workflow` | PR 作成 + review waiting |
| 「PRレビュー待機して」 | `github` または `github-pr-workflow` | signal-driven waiting |
| 「レビュー対応して」 | `github` または `github-pr-review-response` | review signal 対応 |
| 「Issue登録して」 | `github` または `github-issue-intake` | actionable issue 起票 |
| 「Issueタスクを進めましょう」 | `session-issue-autopilot` | issue 実行セッション開始 |

### Git / GitHub skill topology

router 化を検討する前に、まず既存の flat skill がどの入口を持つかを明示する。

| Skill | Primary trigger | Lifecycle stage | Upstream / wrapper | Typical next step | Current judgment |
| --- | --- | --- | --- | --- | --- |
| `git-init-to-github` | 新規ローカルディレクトリを GitHub に公開したい | repo bootstrap | なし | `git-initial-setup` / `github-quality-gate-setup` / `github-repo-label-setup` | flat 維持 |
| `git-initial-setup` | main 保護や hook を標準化したい | repo protection | `git-init-to-github` 後に呼ばれやすい | `github-quality-gate-setup` / `github-repo-label-setup` | flat 維持 |
| `git-ops-folder-init` | 業務フォルダを allowlist 方式で git 管理したい | local ops bootstrap | なし | 必要なら `git-init-to-github` | flat 維持 |
| `github` | GitHub 周りを広く頼みたい | thin entry | なし | `github-pr-workflow` / `github-pr-review-response` / `github-issue-intake` | thin entry として追加 |
| `git-commit-practices` | コミット規約・粒度を整えたい / 「コミットして」と頼みたい | local delivery hygiene | 多くの skill から補助的に参照 | `github-pr-workflow` | flat 維持 |
| `github-pr-workflow` | 実装済みの変更を PR にしたい | delivery | `session-issue-autopilot` から委譲されうる | `github-pr-review-response` | flat 維持 |
| `github-pr-review-response` | review signal に応答したい | review response | `github-pr-workflow` の downstream | Human merge handoff / `github-issue-intake` | flat 維持 |
| `github-issue-intake` | スコープ外や後続対応を issue 化したい | deferral / triage | `github-pr-review-response` や通常作業から派生 | backlog / owner handoff | flat 維持 |
| `github-quality-gate-setup` | gitleaks / textlint CI を入れたい | repo hardening | `git-init-to-github` / `git-initial-setup` 後に呼ばれやすい | `github-repo-label-setup` は任意 | flat 維持 |
| `github-repo-label-setup` | label taxonomy を標準化したい | repo triage bootstrap | `git-init-to-github` / `git-initial-setup` 後に呼ばれやすい | `github-issue-intake` 運用へ接続 | flat 維持 |
| `session-issue-autopilot` | issue を 1 セッションで end-to-end 進めたい | session orchestrator | greeting trigger | `github-pr-workflow` -> `github-pr-review-response` | orchestrator 維持 |

### Routerization gate criteria

現状の git / github skill 群は top-level 直呼びの利点が大きいため、`github` のような薄い入口は追加しても、次の条件を満たすまで物理 router 化はしない。

| Gate | Question | Evidence needed |
| --- | --- | --- |
| Shared entry point | 複数 skill が同じ曖昧 prompt から頻繁に競合するか | 実例または eval で competing prompts が繰り返し観測される |
| Discoverability failure | flat 名称だけでは正しい skill に到達しづらいか | near-miss で誤起動率や迷いが高い |
| Shared logic density | 3 skill 以上で同種の decision table や glossary が重複しているか | 重複セクションの棚卸し |
| Eval benefit | 仮想 router のほうが routing 精度や到達手数で勝つか | flat vs router 比較 eval |

### Pre-router eval sketch

router 化を議論するときは、少なくとも次の prompt 群で flat 現行構成と仮想 router 構成を比較する。

| Case type | Example prompt | What to measure |
| --- | --- | --- |
| should-trigger | 「PR を作ってレビュー待ちにしたい」 | 正しい skill 到達率 |
| should-trigger | 「レビューコメントに応答したい」 | downstream skill の選択精度 |
| near-miss | 「GitHub 周りを整理したい」 | 不要な router 分岐の有無 |
| near-miss | 「repo をちゃんと整えたい」 | bootstrap 系の案内精度 |
| mixed-intent | 「新規 repo を公開して quality gate と labels も入れたい」 | 分割案内の明快さ |
| false-positive guard | 「commit message の規約だけ知りたい」 | 不要な repo/router 案内抑制 |

評価観点は `route precision`、`false positive rate`、`first useful action`、`explanation overhead` を基本とする。

`github` 薄い入口の初期評価ケースは `evals/github/evals.json` に追加し、日常運用フレーズ（「プルリクして」「レビュー対応して」「Issue登録して」「コミットして」など）を直接比較できるようにした。

## 📊 品質基準

- ✅ **1 Skill = 1 Workflow**
- ✅ **Critical 5項目**: `skill/_foundation/QUALITY.md` の必須項目を全PASS
- ✅ **Recommended 10項目**: readability と reuse の改善シグナルとして確認
- ✅ **コンパクトな hot path**: 詳細は `references/` へ分離
- ✅ **国際化は必要に応じて**: `references/SKILL.ja.md` を追加

---

**最終更新**: 2026-03-15
**管理者**: RyoMurakami1983
