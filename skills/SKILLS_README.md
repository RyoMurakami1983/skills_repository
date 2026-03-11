# Skills ディレクトリ

GitHub Copilot Agent Skills — 24スキル + 2スクリプトライブラリ

## 📋 概要

**設計方針**: 「1 Skill = 1 Workflow」— 各スキルは単一ワークフローに特化し、SKILL.mdは500行以内を目標。

## 📦 スキル一覧

### スキルメタ系（スキルの作成・検証・管理）

| Skill | 説明 |
|-------|------|
| [skills-author-skill](skills-author-skill/) | 新規SKILL.mdをゼロから書く |
| [skills-validate-skill](skills-validate-skill/) | 品質検証（58項目チェック、85%/80%閾値） |
| [skills-revise-skill](skills-revise-skill/) | 改訂・発見性最適化・EN/JAパリティ維持 |
| [skills-generate-skill-suite](skills-generate-skill-suite/) | 関連スキル群の一括生成 |
| [skills-review-skill-enterprise-readiness](skills-review-skill-enterprise-readiness/) | エンタープライズ導入準備評価 |
| [skills-index-snippets](skills-index-snippets/) | AGENTS.md / CLAUDE.md スニペット管理 |

### Git / GitHub ワークフロー

| Skill | 説明 |
|-------|------|
| [git-commit-practices](git-commit-practices/) | Conventional Commits + アトミックコミット |
| [git-init-to-github](git-init-to-github/) | ローカル初期化 → GitHub push（新規プロジェクト） |
| [git-initial-setup](git-initial-setup/) | init/clone 後のmain保護設定 |
| [git-ops-folder-init](git-ops-folder-init/) | 業務フォルダのgit初期化（製造業向け） |
| [github-pr-workflow](github-pr-workflow/) | PR作成 → Issue連携 → レビュー待機 |
| [github-pr-review-response](github-pr-review-response/) | レビューコメント分類・修正・再レビュー依頼 |
| [github-issue-intake](github-issue-intake/) | スコープ外作業をGitHub Issueに起票 |
| [github-quality-gate-setup](github-quality-gate-setup/) | gitleaks + textlint CI 設定 |
| [github-repo-label-setup](github-repo-label-setup/) | プレフィックス命名のラベル体系構築 |

### セッション・オーケストレーション

| Skill | 説明 |
|-------|------|
| [session-issue-autopilot](session-issue-autopilot/) | Issue→実装→PR→レビュー応答のフル自動操縦 |
| [agent-batch-workflow](agent-batch-workflow/) | 並列エージェントによるバッチ処理 |
| [agent-explain-on-demand](agent-explain-on-demand/) | エージェント動作のオンデマンド説明 |

### デプロイ

| Skill | 説明 |
|-------|------|
| [dotnet-skill-deploy](dotnet-skill-deploy/) | .NETスキルをプロジェクトに配備 |
| [python-skill-deploy](python-skill-deploy/) | Pythonスキルをプロジェクトに配備 |

### ドメイン特化

| Skill | 説明 |
|-------|------|
| [furikaeri-practice](furikaeri-practice/) | KPT/YWTによるふりかえりワークフロー |
| [knowledge-capture](knowledge-capture/) | 匿名化ゲート付きナレッジキャプチャ |
| [notion-safe-operations](notion-safe-operations/) | Notion MCP操作のプリフライトチェック |

### スクリプトライブラリ（SKILL.mdなし）

| ディレクトリ | 内容 |
|------------|------|
| [skill-quality-validation](skill-quality-validation/) | `validate_skill.py` + `analyze_skill_gaps.py` |
| [skill-template-generator](skill-template-generator/) | `generate_template.py` テンプレート生成 |

## 🚀 標準ワークフロー

### 新しいSkillを作成する場合

1. `skills-author-skill` でエンドツーエンド執筆
2. `skills-validate-skill` で品質検証（88%以上を目標）
3. `skills-revise-skill` で改訂・EN/JA同期

### GitHub 実装→PR→レビュー応答

| フェーズ | スキル | 役割 |
|---|---|---|
| PR作成 + 待機 | `github-pr-workflow` | ブランチ状態確認、PR作成、シグナル駆動待機 |
| レビュー応答 | `github-pr-review-response` | コメント分類、修正、再レビュー依頼 |
| マージ判断 | Human handoff | 人間が判断 |
| セッション包み | `session-issue-autopilot` | 上位オーケストレーター |

## 📊 品質基準

- ✅ **1 Skill = 1 Workflow**: 単一ワークフローに特化
- ✅ **500行以内**: SKILL.md本体は簡潔に（超過分はreferences/へ）
- ✅ **合格条件**: validate_skill.py 全体スコア ≥85%、各カテゴリ ≥80%
- ✅ **推奨目標**: 全体スコア ≥88%（スキルメタ系は特に高品質を維持）
- ✅ **憲法との整合**: PHILOSOPHY.md の Values と明示的に接続
- ✅ **国際化**: 英日両言語対応

---

**最終更新**: 2026-03-10
**管理者**: RyoMurakami1983
