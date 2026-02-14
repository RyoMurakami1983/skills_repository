# GitHub Copilot Skills Collection

高品質なGitHub Copilot Agent Skillsのコレクション

## 📋 概要

このリポジトリは、GitHub Copilot Agentで使用できる高品質なSkillsを集約・管理するためのものです。
**「1 Skill = 1 Workflow」** 標準に基づき設計されており、各スキルは1つのワークフローに特化しています。

### 🎯 設計思想

- **1 Skill = 1 Workflow**: 各スキルは単一のワークフローに集中し、≤500行で記述
- **DDD命名規則**: `<context>-<workflow>` 形式（例: `skills-author-skill`, `git-protect-main`）
- **バイリンガル**: 英語 `SKILL.md` + 日本語 `references/SKILL.ja.md`
- **憲法連携**: すべてのスキルが [PHILOSOPHY.md](PHILOSOPHY.md) のValuesと接続

## 🗂️ カテゴリ

| カテゴリ | 説明 | 配置先 | Skills数 | 詳細 |
|---------|------|--------|---------|------|
| `skills/` | Skill作成支援 + Git/GitHub ワークフロー | グローバル（~/.copilot/skills/） | 18 | [SKILLS_README.md](skills/SKILLS_README.md) |
| `production/` | MVP/本番向け開発プラクティス | プロジェクト（.github/skills/） | 1 | [PRODUCTION_SKILLS_README.md](production/PRODUCTION_SKILLS_README.md) |

### 📌 今後追加予定のカテゴリ

- **python/** - Python開発ワークフロー（FastAPI、Pytest等）
- **dotnet/** - .NET/C#開発ワークフロー（WPF、EF Core等）
- **typescript/** - TypeScript/Node.js開発ワークフロー

## 🏁 Developer Quickstart

### 前提ツール

- **Git** — バージョン管理
- **[uv](https://docs.astral.sh/uv/)** — Python ランタイム管理（`winget install astral-sh.uv`）
- **[gh](https://cli.github.com/)** — GitHub CLI（`winget install GitHub.cli`）

### セットアップ（Windows PowerShell）

```powershell
# 1. クローン
git clone https://github.com/RyoMurakami1983/skills_repository.git
cd skills_repository

# 2. 依存関係の同期
uv sync

# 3. 動作確認：スキル検証を実行
uv run python skills\skill-quality-validation\scripts\validate_skill.py skills\git-initial-setup\SKILL.md
```

### よく使うコマンド

```powershell
# スキル検証
uv run python skills\skill-quality-validation\scripts\validate_skill.py path\to\SKILL.md

# テスト実行
uv run pytest

# JSON形式で出力
uv run python skills\skill-quality-validation\scripts\validate_skill.py path\to\SKILL.md --json
```

> 📖 Windows固有の設定（UTF-8、改行コード等）は [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) を参照

## 🚀 インストール

### グローバルインストール（全プロジェクト共通）

**Meta-Skills（Skill作成支援）をグローバルに配置（Windows推奨: 安全同期）**:

```powershell
# 1) 専用のローカルcloneを作成（初回のみ）
git clone https://github.com/RyoMurakami1983/skills_repository.git C:\tools\skills_repository

# 2) 同期先フォルダを作成（初回のみ）
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\skills | Out-Null

# 3) 初回同期（不要ファイル削除も含めて完全同期）
robocopy C:\tools\skills_repository\skills $env:USERPROFILE\.copilot\skills /MIR
```

**更新時（常に最新へ安全同期）**:

```powershell
Set-Location C:\tools\skills_repository
git pull --ff-only
robocopy C:\tools\skills_repository\skills $env:USERPROFILE\.copilot\skills /MIR
```

> 注意: `/MIR` は同期先の不要ファイルを削除します。`$env:USERPROFILE\.copilot\skills` を専用同期先として使用してください。

**Linux/macOS（初回）**:

```bash
git clone https://github.com/RyoMurakami1983/skills_repository.git /tmp/skills-repository
mkdir -p ~/.copilot/skills
cp -r /tmp/skills-repository/skills/* ~/.copilot/skills/
```

**Linux/macOS（更新時）**:

```bash
cd /tmp/skills-repository
git pull --ff-only
rsync -a --delete /tmp/skills-repository/skills/ ~/.copilot/skills/
```

> 注意: `cp -r` の再実行だけでは削除済みSkillが同期先に残る場合があります。更新時は `rsync --delete` を使用してください。

### プロジェクトインストール（プロジェクト固有）

production/ や言語別Skillsは、プロジェクトの`.github/skills/`にコピーして使用します。

```bash
mkdir -p .github/skills
cp -r /tmp/skills-repository/production/* .github/skills/
```

## 🛠️ 使い方

### Skill作成ワークフロー

#### 1. テンプレート生成
```bash
uv run python ~/.copilot/skills/skill-template-generator/scripts/generate_template.py
```

#### 2. 品質検証
```bash
uv run python ~/.copilot/skills/skill-quality-validation/scripts/validate_skill.py path/to/SKILL.md
```

#### 3. GitHub Copilot Chat内で使用

**スキル作成系 (`skills-*`)**:
- `skills-author-skill` — 新しいスキルを一から執筆
- `skills-validate-skill` — スキルの品質検証
- `skills-remediate-validation-findings` — 検証結果の修正
- `skills-generate-skill-template` — テンプレート生成
- `skills-generate-skill-suite` — 関連スキル群を一括生成
- `skills-refactor-skill-to-single-workflow` — レガシー形式から移行
- `skills-optimize-skill-discoverability` — 発見性を改善
- `skills-review-skill-enterprise-readiness` — エンタープライズ適性レビュー

**Git/GitHub系**:
- `git-commit-practices` — コミット規約と原子性
- `git-initial-setup` — git init/clone時のブランチ保護
- `github-pr-workflow` — PRフローの標準化
- `github-issue-intake` — スコープ外作業のIssue化
- `skills-revise-skill` — スキルの修正・バージョン管理

**ルータースキル**（後方互換）:
- `skill-writing-guide` → skills-* 系へ振り分け
- `skill-quality-validation` → skills-validate-skill / skills-remediate-validation-findings へ
- `skill-template-generator` → skills-generate-skill-template / skills-generate-skill-suite へ

## 📚 ドキュメント

- **[PHILOSOPHY.md](PHILOSOPHY.md)** - 開発憲法（Values / Mission / Vision）
- **[skills/SKILLS_README.md](skills/SKILLS_README.md)** - Skills詳細情報・一覧
- **[production/PRODUCTION_SKILLS_README.md](production/PRODUCTION_SKILLS_README.md)** - Production Skills詳細情報

## 🤝 貢献

### 新しいSkillを追加する

1. `skills-generate-skill-template` でテンプレート生成
2. `skills-author-skill` を参考に1ワークフローを記述
3. `skills-validate-skill` で品質検証（80点以上）
4. Pull Request作成

### 貢献ガイドライン

- **1 Skill = 1 Workflow** を厳守
- 日本語と英語の両方でドキュメント作成
- 品質検証で80点以上のスコアを維持
- Conventional Commits形式でコミット

## 📄 ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。

## 👤 作成者

**RyoMurakami1983**

## 📞 連絡先・サポート

- **Issues**: バグ報告や機能リクエストは[GitHubのIssues](https://github.com/your-org/skills-repository/issues)へ
- **Discussions**: 質問や議論は[GitHub Discussions](https://github.com/your-org/skills-repository/discussions)へ

## 🔄 バージョン履歴

### v2.0.0 (2026-02-xx)
- **「1 Skill = 1 Workflow」アーキテクチャへ移行**
- skills-system 3スキルを8つの単一ワークフロースキルに分割
- 5つの既存スキルを統合ワークフロー形式に移行
- validate_skill.py v4.1.0（ルーター/ワークフロー/レガシー3モード対応）
- DDD命名規則 `<context>-<workflow>` を導入
- Skills総数: 18 + production 1

### v1.1.0 (2026-02-13)
- Productionカテゴリを追加
- tdd-standard-practice を追加

### v1.0.0 (2026-02-12)
- 初回リリース（Meta-Skills 10種）

---

**Author**: RyoMurakami1983
