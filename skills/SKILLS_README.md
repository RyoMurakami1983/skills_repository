# Meta-Skills: Skill作成支援システム

GitHub Copilot Agent Skillsを作成・管理するための支援システム

## 📋 概要

このカテゴリには、高品質なSkillを作成・検証・管理するためのMeta-Skillsが含まれています。これらは新しいSkillを開発する際の強力な支援ツールとして機能します。

## 🎯 用途

**グローバルインストール推奨** - 全プロジェクトで共通利用

これらのMeta-Skillsは特定のプロジェクトに依存せず、開発環境全体で使用することを想定しています。`~/.copilot/skills/`にインストールすることで、あらゆるプロジェクトでSkill作成支援機能を利用できます。

## 📦 収録Skills

| Skill名 | 説明 | バージョン | 主な機能 |
|---------|------|-----------|---------|
| [skill-writing-guide](skill-writing-guide/) | Skill執筆ガイド | 1.0.0 | ベストプラクティス、構造化手法、文章作成支援 |
| [skill-quality-validation](skill-quality-validation/) | 64項目品質検証 | 2.0.0 | 自動品質チェック、スコアリング、改善提案 |
| [skill-template-generator](skill-template-generator/) | テンプレート自動生成 | 1.0.0 | SKILL.md/SKILL.ja.md雛形生成、構造作成 |
| [skill-revision-guide](skill-revision-guide/) | 修正・バージョン管理 | 1.0.0 | 変更管理、CHANGELOG、英日同期支援 |
| [skill-git-commit-practices](skill-git-commit-practices/) | Gitコミット実践 | 1.0.0 | Conventional Commits、原子的コミット、コミット文脈 |
| [skill-github-pr-workflow](skill-github-pr-workflow/) | GitHub PRワークフロー | 1.0.0 | PR作成、レビュー、マージ、Issue連携 |
| [skill-git-review-standards](skill-git-review-standards/) | Gitレビュー標準 | 1.0.0 | レビュー目的、PRサイズ、承認SLA |
| [skill-git-history-learning](skill-git-history-learning/) | Git履歴学習 | 1.0.0 | 履歴学習、オンボーディング、リリースノート |
| [skill-git-initial-setup](skill-git-initial-setup/) | git初期セットアップ | 1.2.0 | git init/clone初期保護、GitHub保護ルール、フック設定 |
| [skill-issue-intake](skill-issue-intake/) | Issueインテーク | 1.0.0 | Issue作成判断、テンプレ、ラベル/優先度、CLI/GUI手順 |

## 🔧 依存関係

### 必須環境
- **GitHub Copilot Agent** - これらのSkillsを実行するための基盤

### オプション（スクリプト実行用）
- **Python 3.8+** - 自動化スクリプトを使用する場合
- **標準ライブラリのみ** - 外部パッケージのインストール不要

> **Note**: スクリプトを使用しない場合、PythonなしでもGitHub Copilot Chat内で直接Skillsを呼び出せます。

## 📖 各Skillの詳細

### 1. skill-writing-guide

**Skill執筆のためのベストプラクティスガイド**

- 新しいSkillを作成する際の指針
- 構造化されたSKILL.mdの書き方
- 効果的な例文・サンプルコードの作成方法
- 日本語/英語の両言語対応手法

**使い方**:
```
@workspace /skill-writing-guide 新しいPython用のSkillを作成したい
```

詳細: [skill-writing-guide/SKILL.md](skill-writing-guide/SKILL.md) | [日本語版](skill-writing-guide/references/SKILL.ja.md)

### 2. skill-quality-validation

**64項目の品質検証システム**

- 構造の完全性チェック（15項目）
- 内容の品質評価（20項目）
- ベストプラクティス準拠（20項目）
- 自動スコアリング（100点満点）
- 具体的な改善提案

**使い方**:
```bash
# スクリプトで自動検証
python ~/.copilot/skills/skill-quality-validation/scripts/validate_skill.py path/to/SKILL.md

# またはCopilot Chat内で
@workspace /skill-quality-validation このSkillを検証してください
```

詳細: [skill-quality-validation/SKILL.md](skill-quality-validation/SKILL.md) | [日本語版](skill-quality-validation/references/SKILL.ja.md)

### 3. skill-template-generator

**SKILL.md/SKILL.ja.mdテンプレート自動生成**

- 標準的な構造を持つテンプレート生成
- 日本語版と英語版の両方作成
- カスタマイズ可能なセクション
- ベストプラクティスに準拠した雛形

**使い方**:
```bash
# スクリプトでテンプレート生成
python ~/.copilot/skills/skill-template-generator/scripts/generate_template.py

# またはCopilot Chat内で
@workspace /skill-template-generator FastAPI用のSkillテンプレートを生成
```

詳細: [skill-template-generator/SKILL.md](skill-template-generator/SKILL.md) | [日本語版](skill-template-generator/references/SKILL.ja.md)

### 4. skill-revision-guide

**Skillの修正・バージョン管理ガイド**

- 既存Skillの効果的な修正方法
- CHANGELOGの適切な管理
- 英語版と日本語版の同期保持
- バージョニング戦略
- 特定作者（RyoMurakami1983）のSkill管理強化

**使い方**:
```
@workspace /skill-revision-guide このSkillを更新したい
```

詳細: [skill-revision-guide/SKILL.md](skill-revision-guide/SKILL.md) | [日本語版](skill-revision-guide/references/SKILL.ja.md)

### 5. skill-git-commit-practices

**Gitコミット実践ガイド**

- Conventional Commits形式の実践
- 日本語コミットメッセージの明確化
- 原子的コミットの作り方
- Whyを残すコミット文化

**使い方**:
```
@workspace /skill-git-commit-practices コミット規約を標準化したい
```

詳細: [skill-git-commit-practices/SKILL.md](skill-git-commit-practices/SKILL.md) | [日本語版](skill-git-commit-practices/references/SKILL.ja.md)

### 6. skill-github-pr-workflow

**GitHub PRワークフロー標準化**

- PR作成からマージまでの流れ
- Issueクローズキーワードの運用
- CIと承認ゲートの標準化
- マージ後のmain同期

**使い方**:
```
@workspace /skill-github-pr-workflow PR運用を標準化したい
```

詳細: [skill-github-pr-workflow/SKILL.md](skill-github-pr-workflow/SKILL.md) | [日本語版](skill-github-pr-workflow/references/SKILL.ja.md)

### 7. skill-git-review-standards

**Gitレビュー標準ガイド**

- レビュー目的とチェックリスト
- PRサイズ基準とSLA
- フィードバック表現の統一
- 形骸化レビューの防止

**使い方**:
```
@workspace /skill-git-review-standards レビュー品質を上げたい
```

詳細: [skill-git-review-standards/SKILL.md](skill-git-review-standards/SKILL.md) | [日本語版](skill-git-review-standards/references/SKILL.ja.md)

### 8. skill-git-history-learning

**Git履歴学習ガイド**

- 履歴から学ぶオンボーディング
- リリースノート生成
- 意思決定の記録と共有
- 履歴を学習資産に変換

**使い方**:
```
@workspace /skill-git-history-learning 履歴を学習資産にしたい
```

詳細: [skill-git-history-learning/SKILL.md](skill-git-history-learning/SKILL.md) | [日本語版](skill-git-history-learning/references/SKILL.ja.md)

### 9. skill-git-initial-setup

**git init/clone時のmain保護デフォルト設定ガイド**

- GitHubブランチ保護ルールの設定
- pre-commit/pre-pushフックの導入
- core.hooksPath / init.templateDir の初期設定

**使い方**:
```
@workspace /skill-git-initial-setup git init/clone時の保護を標準化したい
```

詳細: [skill-git-initial-setup/SKILL.md](skill-git-initial-setup/SKILL.md) | [日本語版](skill-git-initial-setup/references/SKILL.ja.md)

### 10. skill-issue-intake

**Issue作成とトリアージの実践ガイド**

- 今直すかIssue化するかの判断基準
- タイトル/本文テンプレと優先度ラベル
- GitHub CLI/GUIでの作成手順

**使い方**:
```
@workspace /skill-issue-intake スコープ外作業をIssue化したい
```

詳細: [skill-issue-intake/SKILL.md](skill-issue-intake/SKILL.md) | [日本語版](skill-issue-intake/references/SKILL.ja.md)

## 🚀 ワークフロー例

### 新しいSkillを作成する場合

1. **テンプレート生成** - `skill-template-generator`で雛形作成
2. **執筆ガイド参照** - `skill-writing-guide`でベストプラクティス確認
3. **内容作成** - 実際のSkill内容を記述
4. **品質検証** - `skill-quality-validation`で64項目チェック
5. **改善反映** - スコア80点以上を目指して修正
6. **完成・公開**

### 既存Skillを更新する場合

1. **修正ガイド参照** - `skill-revision-guide`で変更管理手法確認
2. **内容修正** - 必要な変更を実施
3. **品質再検証** - `skill-quality-validation`で品質維持確認
4. **CHANGELOG更新** - 変更内容を記録
5. **英日同期** - 両言語版の整合性確保

## 📊 品質基準

このMeta-Skillsシステムを使用することで、以下の品質基準を達成できます：

- ✅ **構造の完全性**: 必須セクションの完備
- ✅ **内容の充実度**: 具体例、サンプルコードの提供
- ✅ **保守性**: 明確なバージョン管理、変更履歴
- ✅ **国際化**: 日英両言語対応
- ✅ **ベストプラクティス準拠**: 業界標準に沿った記述

目標スコア: **80点以上** (skill-quality-validationの評価)

## 🔗 関連リソース

- **ルートREADME**: [../README.md](../README.md) - プロジェクト全体概要
- **構造設計**: [../repository-structure-plan.md](../repository-structure-plan.md) - リポジトリ構造詳細
- **品質分析**: [../skill-quality-gaps-analysis.md](../skill-quality-gaps-analysis.md) - 品質ギャップ分析

## 🤝 貢献

Meta-Skillsの改善提案や新機能追加のアイデアがありましたら、ぜひIssueやPull Requestでお知らせください。

## 📝 ライセンス

これらのMeta-SkillsはMITライセンスの下で提供されています。詳細は[../LICENSE](../LICENSE)を参照してください。

---

**最終更新**: 2026-02-12  
**管理者**: RyoMurakami1983
