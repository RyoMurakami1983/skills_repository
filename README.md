# GitHub Copilot Skills Collection

高品質なGitHub Copilot Agent Skillsのコレクション

## 📋 概要

このリポジトリは、GitHub Copilot Agentで使用できる高品質なSkillsを集約・管理するためのものです。現在は**Meta-Skills**（Skill作成支援システム）を提供しており、今後さまざまな言語・ドメイン特化のSkillsを追加予定です。

### 🎯 プロジェクトの目的

- **高品質なSkillsの提供**: 実用的で保守性の高いSkillsを開発・共有
- **体系的な管理**: カテゴリ別に整理されたSkillsコレクション
- **開発支援**: Skill作成を支援するMeta-Skillsの提供
- **継続的な改善**: フィードバックに基づく品質向上

## 🗂️ カテゴリ

現在利用可能なカテゴリ：

| カテゴリ | 説明 | 配置先 | Skills数 | 詳細 |
|---------|------|--------|---------|------|
| `skills/` | Skill作成支援（Meta-Skills） | グローバル（~/.copilot/skills/） | 5 | [SKILLS_README.md](skills/SKILLS_README.md) |

### 📌 今後追加予定のカテゴリ

以下のカテゴリを順次追加予定です：

- **pythons/** - Python開発パターン（Pandas、FastAPI、Pytest等）
- **dotnets/** - .NET/C#開発パターン（WPF、EF Core、ASP.NET Core等）
- **typescripts/** - TypeScript/Node.js開発パターン（React、Next.js、Express等）
- **data-engineering/** - データエンジニアリング特化Skills
- **finance/** - 金融業務特化Skills
- **その他ドメイン別Skills**

## 🚀 インストール

### グローバルインストール（全プロジェクト共通）

**Meta-Skills（Skill作成支援）をグローバルに配置**:

```bash
# リポジトリをクローン
git clone https://github.com/your-org/skills-repository.git /tmp/skills-repository

# グローバルスキルディレクトリにコピー
mkdir -p ~/.copilot/skills
cp -r /tmp/skills-repository/skills/* ~/.copilot/skills/

# 確認
ls ~/.copilot/skills/
# skill-writing-guide/
# skill-quality-validation/
# skill-template-generator/
# skill-revision-guide/
# skill-git-initial-setup/
```

**Windowsの場合**:

```powershell
# リポジトリをクローン
git clone https://github.com/your-org/skills-repository.git C:\temp\skills-repository

# グローバルスキルディレクトリにコピー
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\skills
Copy-Item -Recurse C:\temp\skills-repository\skills\* $env:USERPROFILE\.copilot\skills\

# 確認
Get-ChildItem $env:USERPROFILE\.copilot\skills\
```

### プロジェクトインストール（プロジェクト固有） - 今後対応予定

今後追加される言語別Skillsは、プロジェクトの`.github/skills/`にコピーして使用します。

**例: Python Skillsをプロジェクトに追加**（今後実装予定）:
```bash
# Python skills をプロジェクトにコピー
mkdir -p .github/skills
cp -r /tmp/skills-repository/pythons/* .github/skills/
```

## 🛠️ 使い方

### Skill作成支援（Meta-Skills）

グローバルにインストールしたMeta-Skillsを使用して、新しいSkillを作成できます。

#### 1. テンプレート生成
```bash
# Skillテンプレートの自動生成
python ~/.copilot/skills/skill-template-generator/scripts/generate_template.py
```

#### 2. 品質検証
```bash
# 作成したSkillの品質を64項目でチェック
python ~/.copilot/skills/skill-quality-validation/scripts/validate_skill.py path/to/SKILL.md
```

#### 3. GitHub Copilot Chat内で使用
GitHub Copilot Chat内で直接Meta-Skillsを呼び出すことができます：

- `@workspace /skill-writing-guide` - Skill執筆ガイドの確認
- `@workspace /skill-quality-validation` - Skillの品質検証
- `@workspace /skill-template-generator` - テンプレート生成支援
- `@workspace /skill-revision-guide` - Skillの修正・バージョン管理
- `@workspace /skill-git-initial-setup` - git init/clone時の保護を標準化

## 📚 ドキュメント

- **[repository-structure-plan.md](repository-structure-plan.md)** - リポジトリ構造の詳細設計
- **[skills/SKILLS_README.md](skills/SKILLS_README.md)** - Meta-Skills詳細情報
- **[skill-quality-gaps-analysis.md](skill-quality-gaps-analysis.md)** - 品質分析レポート

## 🤝 貢献

新しいSkillの追加や既存Skillの改善に貢献する方法：

### 新しいSkillを追加する

1. **適切なカテゴリを選択** - 現在は`skills/`のみ、今後他カテゴリも追加予定
2. **テンプレート生成** - `skill-template-generator`を使用
3. **内容を作成** - `skill-writing-guide`を参考に記述
4. **品質検証** - `skill-quality-validation`で64項目チェック
5. **Pull Request作成** - レビュー後にマージ

### 既存Skillを改善する

1. **Issue作成** - 改善提案や不具合報告
2. **修正作業** - `skill-revision-guide`を参考に修正
3. **品質再検証** - 変更後も品質基準を満たすか確認
4. **Pull Request作成** - 変更内容を説明

### 貢献ガイドライン

- 日本語と英語の両方でドキュメント作成（SKILL.mdとSKILL.ja.md）
- 品質検証で80点以上のスコアを維持
- 明確なコミットメッセージ
- テスト・サンプルコードの提供

## 📄 ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。

## 👤 作成者

**RyoMurakami1983**

## 📞 連絡先・サポート

- **Issues**: バグ報告や機能リクエストは[GitHubのIssues](https://github.com/your-org/skills-repository/issues)へ
- **Discussions**: 質問や議論は[GitHub Discussions](https://github.com/your-org/skills-repository/discussions)へ

## 🔄 バージョン履歴

### v1.0.0 (2026-02-12)
- 初回リリース
- Meta-Skills 5種を収録
  - skill-writing-guide
  - skill-quality-validation
  - skill-template-generator
  - skill-revision-guide
  - skill-git-initial-setup
- リポジトリ構造確立
- Git管理開始

---

**Note**: このリポジトリは現在開発中です。今後、Python、.NET、TypeScript等の言語別Skillsカテゴリを追加予定です。
