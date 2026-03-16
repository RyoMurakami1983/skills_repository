# Skills ディレクトリ

GitHub Copilot Agent Skills — 19スキル

## 📋 概要

**設計方針**: 「1 Skill = 1 Workflow」— 各スキルは単一ワークフローに特化し、詳細は `references/` へ逃がします。

## 📦 スキル一覧

### スキルメタ系（単一入口）

| Skill | 説明 |
| --- | --- |
| [skill](skill/) | スキルの作成・改善・検証・評価を統合管理するルーター。`sub_skills/`、`_foundation/`、`_eval/`、`scripts/` を内包 |

### Git / GitHub ワークフロー

| Skill | 説明 |
| --- | --- |
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
| PR作成 + 待機 | `github-pr-workflow` | ブランチ状態確認、PR作成、シグナル駆動待機 |
| レビュー応答 | `github-pr-review-response` | コメント分類、修正、再レビュー依頼 |
| マージ判断 | Human handoff | 人間が判断 |
| セッション包み | `session-issue-autopilot` | 上位オーケストレーター |

## 📊 品質基準

- ✅ **1 Skill = 1 Workflow**
- ✅ **Critical 5項目**: `skill/_foundation/QUALITY.md` の必須項目を全PASS
- ✅ **Recommended 10項目**: readability と reuse の改善シグナルとして確認
- ✅ **コンパクトな hot path**: 詳細は `references/` へ分離
- ✅ **国際化は必要に応じて**: `references/SKILL.ja.md` を追加

---

**最終更新**: 2026-03-15
**管理者**: RyoMurakami1983
