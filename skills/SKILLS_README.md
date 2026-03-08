# Meta-Skills: Skill作成支援システム

GitHub Copilot Agent Skillsを作成・管理するための支援システム

## 📋 概要

このカテゴリには、高品質なSkillを作成・検証・管理するためのMeta-Skillsが含まれています。

**設計方針**: 「1 Skill = 1 Workflow」— 各スキルは単一のワークフローに特化し、SKILL.mdは500行以内を目標とします。

## 🎯 用途

**グローバルインストール推奨** - 全プロジェクトで共通利用

これらのMeta-Skillsは特定のプロジェクトに依存せず、開発環境全体で使用することを想定しています。`~/.copilot/skills/`にインストールすることで、あらゆるプロジェクトでSkill作成支援機能を利用できます。

## 📦 収録Skills

### Skills-System ワークフロースキル（新規）

| Skill名 | ワークフロー | 説明 |
|---------|-------------|------|
| [skills-author-skill](skills-author-skill/) | スキル執筆 | SKILL.mdを一から書き上げるエンドツーエンドワークフロー |
| [skills-refactor-skill-to-single-workflow](skills-refactor-skill-to-single-workflow/) | レガシー移行 | 複数パターンスキルを単一ワークフローに変換 |
| [skills-optimize-skill-discoverability](skills-optimize-skill-discoverability/) | 発見性最適化 | 命名・タグ・説明文の最適化 |
| [skills-validate-skill](skills-validate-skill/) | 品質検証 | 37項目チェックリストによる品質検証 |
| [skills-remediate-validation-findings](skills-remediate-validation-findings/) | 検証結果修正 | 検証レポートに基づく体系的修正 |
| [skills-generate-skill-template](skills-generate-skill-template/) | テンプレート生成 | 単一スキルの骨格生成 |
| [skills-generate-skill-suite](skills-generate-skill-suite/) | スイート生成 | 関連スキル群の一括生成 |

### ルータースキル（後方互換性）

| Skill名 | 役割 | ルーティング先 |
|---------|------|---------------|
| [skill-writing-guide](skill-writing-guide/) | 🔀 ルーター | → skills-author-skill, skills-refactor-*, skills-optimize-* |
| [skill-quality-validation](skill-quality-validation/) | 🔀 ルーター | → skills-validate-skill, skills-remediate-* |
| [skill-template-generator](skill-template-generator/) | 🔀 ルーター | → skills-generate-skill-template, skills-generate-skill-suite |

### Enterprise向けスキル

| Skill名 | ワークフロー | 説明 |
|---------|-------------|------|
| [skills-review-skill-enterprise-readiness](skills-review-skill-enterprise-readiness/) | エンタープライズ適合評価 | 34項目チェックリストによる企業導入準備評価 |

### エージェント UX スキル

| Skill名 | ワークフロー | 説明 |
|---------|-------------|------|
| [agent-explain-on-demand](agent-explain-on-demand/) | Explain on Demand | 動作・モード・変更点・能力をオンデマンドで説明（短答先出し） |

### Git/GitHub/Issue ワークフロースキル（移行済み・リネーム済み）

| Skill名 | ワークフロー | 状態 |
|---------|-------------|------|
| [git-commit-practices](git-commit-practices/) | Write Quality Commits | ✅ 移行済み |
| [git-initial-setup](git-initial-setup/) | Protect Main Branch | ✅ 移行済み |
| [github-pr-workflow](github-pr-workflow/) | Ship via Pull Request | ✅ 標準PR作成 + 待機 |
| [github-pr-review-response](github-pr-review-response/) | Respond to PR Review | ✅ 標準レビュー応答 |
| [session-issue-autopilot](session-issue-autopilot/) | Run Session Issue Autopilot | ✅ セッションラッパー |
| [github-issue-intake](github-issue-intake/) | Capture Deferred Work as Issues | ✅ 移行済み |
| [skills-revise-skill](skills-revise-skill/) | Revise and Version Skills | ✅ 移行済み |

### 削除済み旧スキル

- Git系の旧 archive skill は、現行の `git-commit-practices` / `github-pr-workflow` / `github-pr-review-response` へ整理済み

## 🔧 依存関係

### 必須環境
- **GitHub Copilot Agent** - これらのSkillsを実行するための基盤

### オプション（スクリプト実行用）
- **Python 3.8+** - 自動化スクリプトを使用する場合
- **標準ライブラリのみ** - 外部パッケージのインストール不要

> **Note**: スクリプトを使用しない場合、PythonなしでもGitHub Copilot Chat内で直接Skillsを呼び出せます。

## 📖 Skills-System ワークフロー詳細

### skills-author-skill

**SKILL.mdを一から書き上げるエンドツーエンドワークフロー**

スキルの構想から完成版まで、単一ワークフローで執筆を完結させます。

詳細: [skills-author-skill/SKILL.md](skills-author-skill/SKILL.md) | [日本語版](skills-author-skill/references/SKILL.ja.md)

### skills-validate-skill

**37項目チェックリストによる品質検証**

```bash
# スクリプトで自動検証（スクリプトはskill-quality-validationに配置）
uv run python skill-quality-validation/scripts/validate_skill.py path/to/SKILL.md
```

詳細: [skills-validate-skill/SKILL.md](skills-validate-skill/SKILL.md) | [日本語版](skills-validate-skill/references/SKILL.ja.md)

### skills-generate-skill-template

**単一スキルの骨格を生成**

```bash
# スクリプトで生成（スクリプトはskill-template-generatorに配置）
uv run python skill-template-generator/scripts/generate_template.py --name "git-protect-main"
```

詳細: [skills-generate-skill-template/SKILL.md](skills-generate-skill-template/SKILL.md) | [日本語版](skills-generate-skill-template/references/SKILL.ja.md)

## 🚀 ワークフロー例

### 新しいSkillを作成する場合

1. **テンプレート生成** - `skills-generate-skill-template`で骨格作成
2. **執筆** - `skills-author-skill`でエンドツーエンドの執筆ワークフロー
3. **品質検証** - `skills-validate-skill`で37項目チェック
4. **修正** - `skills-remediate-validation-findings`で検証結果に基づく修正
5. **完成・公開**

### 関連スキル群を作成する場合

1. **スイート設計** - `skills-generate-skill-suite`で複数スキルを一括生成
2. **各スキル執筆** - `skills-author-skill`で個別に執筆
3. **発見性最適化** - `skills-optimize-skill-discoverability`で命名・タグ調整
4. **品質検証** - `skills-validate-skill`で一括検証

### レガシースキルを移行する場合

1. **分析** - `skills-refactor-skill-to-single-workflow`で移行方法を決定
2. **分割・再構成** - 複数パターンを単一ワークフローに分割
3. **ルーター作成** - 元スキルをルータースキルに変換
4. **検証** - `skills-validate-skill`で新基準に適合確認

### 既存Skillを更新する場合

1. **修正ガイド参照** - `skills-revise-skill`で変更管理手法確認
2. **内容修正** - 必要な変更を実施
3. **品質再検証** - `skills-validate-skill`で品質維持確認
4. **CHANGELOG更新** - 変更内容を記録

### GitHub実装→PR→レビュー応答の標準ルート（Option A）

| フェーズ | 使うスキル | 役割 |
|---|---|---|
| 実装・検証 | （各実装スキル / セッション作業） | 変更を実装し、テスト・lint・検証を通す |
| PR作成 + 待機 | `github-pr-workflow` | ブランチ状態確認、PR作成、Issue連携、シグナル駆動のレビュー待機 |
| レビュー応答 | `github-pr-review-response` | レビューコメント分類、修正、返信、再レビュー依頼 |
| マージ判断 | Human handoff | GitHub上のマージ可否は人間が判断する |
| セッション全体の包み | `session-issue-autopilot` | 挨拶トリガーから上記フローへ委譲する高レベルラッパー |

ポイント:
- `session-issue-autopilot` は上位のセッションオーケストレーターであり、PR標準そのものではありません。
- 待機はシグナル駆動です。レビュー到着前に同じPRを繰り返し見に行きません。
- 再レビュー依頼は、新しいコミットまたは実質的な返信がそろったときだけ行います。

## 📊 品質基準

このMeta-Skillsシステムを使用することで、以下の品質基準を達成できます：

- ✅ **1 Skill = 1 Workflow**: 単一ワークフローに特化
- ✅ **500行以内**: SKILL.md本体は簡潔に（超過分はreferences/へ）
- ✅ **構造の完全性**: 必須セクション完備（frontmatter, When to Use, Core Principles, Workflow）
- ✅ **憲法との整合**: PHILOSOPHY.md の Values と明示的に接続
- ✅ **国際化**: 英日両言語対応
- ✅ **作者帰属**: `author: RyoMurakami1983`

## 🏗️ 命名規則

新規スキルは `<context>-<workflow>` 形式で命名：

| コンテキスト | 対象領域 | 例 |
|-------------|---------|-----|
| `skills-` | スキルシステム | skills-author-skill, skills-validate-skill |
| `git-` | ローカルGit操作 | git-protect-main |
| `github-` | GitHub操作 | github-review-pr |
| `dotnet-` | .NET実装 | dotnet-apply-mvvm |
| `python-` | Python実装 | python-create-cli |

ワークフロー名は動詞で開始（generate-, validate-, author-, refactor-, optimize-）

## 🔗 関連リソース

- **ルートREADME**: [../README.md](../README.md) - プロジェクト全体概要
- **構造設計**: [../repository-structure-plan.md](../repository-structure-plan.md) - リポジトリ構造詳細
- **品質分析**: [../skill-quality-gaps-analysis.md](../skill-quality-gaps-analysis.md) - 品質ギャップ分析

## 🤝 貢献

Meta-Skillsの改善提案や新機能追加のアイデアがありましたら、ぜひIssueやPull Requestでお知らせください。

## 📝 ライセンス

これらのMeta-SkillsはMITライセンスの下で提供されています。詳細は[../LICENSE](../LICENSE)を参照してください。

---

**最終更新**: 2026-02-13
**管理者**: RyoMurakami1983
