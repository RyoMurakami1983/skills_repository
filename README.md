# GitHub Copilot Skills Collection

高品質なGitHub Copilot Agent Skillsのコレクション

## 📋 概要

このリポジトリは、GitHub Copilot Agentで使用できる高品質なSkillsを集約・管理するためのものです。
**「1 Skill = 1 Pattern」** 標準に基づき設計されており、各スキルは1つの実行パターン（workflow/cycle/router等）に特化しています。

### 🎯 設計思想

- **1 Skill = 1 Pattern**: 各スキルは単一の実行パターンに集中し、≤500行で記述
- **DDD命名規則**: `<context>-<workflow>` 形式（例: `skills-author-skill`, `git-protect-main`）
- **バイリンガル**: 英語 `SKILL.md` + 日本語 `references/SKILL.ja.md`
- **憲法連携**: すべてのスキルが [PHILOSOPHY.md](PHILOSOPHY.md) のValuesと接続

## 🗂️ カテゴリ

| カテゴリ | 説明 | 配置先 | 詳細 |
|---------|------|--------|------|
| `copilot/` | グローバル開発憲法（copilot-instructions.md） | グローバル（~/.copilot/） | [copilot-instructions.md](copilot/copilot-instructions.md) |
| `agents/` | 師範エージェント（dotnet/python/skill） | グローバル（~/.copilot/agents/） | [下記参照](#-agents) |
| `skills/` | Skill作成支援 + Git/GitHub ワークフロー（18） | グローバル（~/.copilot/skills/） | [SKILLS_README.md](skills/SKILLS_README.md) |
| `dotnet/` | .NET/C# WPF開発ワークフロー（10） | プロジェクト（.github/skills/） | [下記参照](#-dotnet-skills) |
| `production/` | MVP/本番向け開発プラクティス（1） | プロジェクト（.github/skills/） | [PRODUCTION_SKILLS_README.md](production/PRODUCTION_SKILLS_README.md) |

### 📌 今後追加予定のカテゴリ

- **python/** - Python開発ワークフロー（FastAPI、Pytest等）
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
# スキル検証（単体）
uv run python skills\skill-quality-validation\scripts\validate_skill.py path\to\SKILL.md

# スキル検証（一括 — skills/ 配下すべて）
.\skills\skill-quality-validation\scripts\validate_all_skills.ps1

# テスト実行
uv run pytest

# JSON形式で出力
uv run python skills\skill-quality-validation\scripts\validate_skill.py path\to\SKILL.md --json
```

> 📖 Windows固有の設定（UTF-8、改行コード等）は [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) を参照

### 🗃️ ローカル参照ディレクトリ運用

- `local_reference_skills/`: 外部skillの一時参照置き場（開発時のみ使用）
- `local_docs/`: 外部ドキュメントの一時参照置き場（開発時のみ使用）
- どちらも **ディレクトリのみGit管理**し、配下ファイルは `.gitignore` で追跡しません

## 🚀 インストール

### グローバルインストール（全プロジェクト共通）

**Skills + Agents + 開発憲法 をグローバルに配置（Windows推奨: 安全同期）**:

```powershell
# 1) 専用のローカルcloneを作成（初回のみ）
git clone https://github.com/RyoMurakami1983/skills_repository.git C:\tools\skills_repository

# 2) 同期先フォルダを作成（初回のみ）
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\skills | Out-Null
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\agents | Out-Null

# 3) 初回同期（Skills + Agents + copilot-instructions.md を完全同期）
robocopy C:\tools\skills_repository\skills $env:USERPROFILE\.copilot\skills /MIR
robocopy C:\tools\skills_repository\agents $env:USERPROFILE\.copilot\agents /MIR
Copy-Item C:\tools\skills_repository\copilot\copilot-instructions.md $env:USERPROFILE\.copilot\copilot-instructions.md
```

**更新時（常に最新へ安全同期）**:

```powershell
Set-Location C:\tools\skills_repository
git pull --ff-only
robocopy skills $env:USERPROFILE\.copilot\skills /MIR
robocopy agents $env:USERPROFILE\.copilot\agents /MIR
Copy-Item copilot\copilot-instructions.md $env:USERPROFILE\.copilot\copilot-instructions.md
```

> 注意: `/MIR` は同期先の不要ファイルを削除します。`$env:USERPROFILE\.copilot\skills` と `$env:USERPROFILE\.copilot\agents` を専用同期先として使用してください。

> **エージェント優先順位**: ユーザーレベル（`~/.copilot/agents/`）> リポレベル（`.github/agents/`）> Organization。グローバルに配置した師範エージェントは、どのプロジェクトでも `@dotnet-shihan`, `@python-shihan`, `@skill-shihan` として呼び出し可能です。

**Linux/macOS（初回）**:

```bash
git clone https://github.com/RyoMurakami1983/skills_repository.git /tmp/skills-repository
mkdir -p ~/.copilot/skills ~/.copilot/agents
cp -r /tmp/skills-repository/skills/* ~/.copilot/skills/
cp -r /tmp/skills-repository/agents/* ~/.copilot/agents/
cp /tmp/skills-repository/copilot/copilot-instructions.md ~/.copilot/copilot-instructions.md
```

**Linux/macOS（更新時）**:

```bash
cd /tmp/skills-repository
git pull --ff-only
rsync -a --delete /tmp/skills-repository/skills/ ~/.copilot/skills/
rsync -a --delete /tmp/skills-repository/agents/ ~/.copilot/agents/
cp /tmp/skills-repository/copilot/copilot-instructions.md ~/.copilot/copilot-instructions.md
```

> 注意: `cp -r` の再実行だけでは削除済みSkill/Agentが同期先に残る場合があります。更新時は `rsync --delete` を使用してください。

**Codex（WSL利用）**:

```bash
# WSL上でCodex用skills配置（例: ~/.codex/skills）
mkdir -p ~/.codex/skills
rsync -a --delete /mnt/c/tools/skills_repository/skills/ ~/.codex/skills/
```

> Windows側のcloneが `C:\tools\skills_repository` の場合、WSLパスは `/mnt/c/tools/skills_repository` になります。

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
skills-author-skill を使ってスケルトン作成（Step 2）
```

#### 2. 品質検証
```bash
uv run python ~/.copilot/skills/skill-quality-validation/scripts/validate_skill.py path/to/SKILL.md
```

#### 3. GitHub Copilot Chat内で使用

**スキル作成系 (`skills-*`)**:
- `skills-author-skill` — 新しいスキルを一から執筆
- `skills-validate-skill` — スキルの品質検証
- `skills-generate-skill-suite` — 関連スキル群を一括生成
- `skills-refactor-skill-to-single-workflow` — レガシー形式から移行
- `skills-revise-skill` — スキル改訂 + 発見性最適化
- `skills-review-skill-enterprise-readiness` — エンタープライズ適性レビュー

**Git/GitHub系**:
- `git-commit-practices` — コミット規約と原子性
- `git-initial-setup` — git init/clone時のブランチ保護
- `github-pr-workflow` — PRフローの標準化
- `github-issue-intake` — スコープ外作業のIssue化
- `skills-revise-skill` — スキルの修正・バージョン管理

**後方互換メモ**:
- 旧ルータースキル/統合元スキルの `SKILL.md` は `archive/phase3-deprecated/` に移動済み
- `skill-quality-validation/scripts/validate_skill.py` は現行検証スクリプトとして維持

## 🤖 Agents

師範エージェント（`agents/` → `~/.copilot/agents/` にグローバル配置）。どのプロジェクトでも `@エージェント名` で呼び出し可能。

| エージェント | 説明 | モード |
|-------------|------|--------|
| `@dotnet-shihan` | C#/.NET/WPFの設計・実装・レビュー | 先生（既定）/ 求道者 |
| `@python-shihan` | Pythonの設計・実装・レビュー | 先生（既定）/ 求道者 |
| `@skill-shihan` | スキルの作成・レビュー・バリデーション | 先生（既定）/ 求道者 |

## 🔷 dotnet Skills

.NET/C# WPF アプリケーション開発のためのスキル群（10スキル）。

### 基盤スキル

| スキル | 説明 |
|--------|------|
| `dotnet-wpf-secure-config` | DPAPI暗号化によるWPFアプリの設定・認証情報管理 |
| `dotnet-access-to-oracle-migration` | Access SQLからOracleへの移行と.NET C#コード生成 |
| `dotnet-oracle-wpf-integration` | WPFアプリへのOracle DB接続（Repositoryパターン+CRUD） |
| `dotnet-wpf-dify-api-integration` | WPFアプリへのDify API統合（DPAPI設定+SSEストリーミング） |

### UIコンポーネントスキル

| スキル | 説明 |
|--------|------|
| `dotnet-wpf-employee-input` | 社員番号入力ダイアログ（4桁バリデーション+DPAPI暗号化保存） |
| `dotnet-wpf-ocr-parameter-input` | OCR実行パラメータ入力UIタブ（非同期進捗表示付き） |
| `dotnet-wpf-pdf-preview` | PDFアップロード+WebView2インラインプレビュー（MVVM対応） |
| `dotnet-wpf-comparison-view` | マッチング結果のサイドバイサイド比較ビュー（不一致ハイライト） |

### ドメインロジック・オーケストレーション

| スキル | 説明 |
|--------|------|
| `dotnet-generic-matching` | 汎用フィールドマッチング（重み付きスコアリング+Specificationパターン） |
| `dotnet-ocr-matching-workflow` | OCR→DB照合エンドツーエンドワークフローオーケストレーター（12ステップ） |

## 📚 ドキュメント

- **[PHILOSOPHY.md](PHILOSOPHY.md)** - 開発憲法（Values / Mission / Vision）
- **[copilot/copilot-instructions.md](copilot/copilot-instructions.md)** - グローバル開発規律（全プロジェクト適用）
- **[skills/SKILLS_README.md](skills/SKILLS_README.md)** - Skills詳細情報・一覧
- **[production/PRODUCTION_SKILLS_README.md](production/PRODUCTION_SKILLS_README.md)** - Production Skills詳細情報

## 📋 Architecture Decision Records (ADR)

設計判断の記録は `docs/adr/` に保存しています。

| ID | タイトル | ステータス |
|----|---------|-----------|
| [ADR-001](docs/adr/ADR-001-dotnet-security-foundation-extraction.md) | .NET WPF セキュリティ基盤の独立スキル抽出 | Accepted |

## 🤝 貢献

### 新しいSkillを追加する

1. `skills-author-skill` でスケルトン作成 + 本文執筆
2. `skills-validate-skill` で品質検証（80点以上）
3. Pull Request作成

### 貢献ガイドライン

- **1 Skill = 1 Pattern** を厳守
- 日本語と英語の両方でドキュメント作成
- 品質検証で80点以上のスコアを維持
- Conventional Commits形式でコミット

## 📝 表記規約

- プレースホルダーは **UPPER_CASE** で記述: `PATH`, `FILE`, `WORKFLOW_NAME`
- またはバッククォート内で山括弧を使用: `` `<path>` ``, `` `<file>` ``
- Markdown中に裸の `<...>` を書くとHTMLタグとして解釈され表示が消えるため避けること

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
- **dotnetカテゴリ追加**: WPF/Oracle/.NET C#スキル10種を追加
- Skills総数: 18 + dotnet 10 + production 1

### v1.1.0 (2026-02-13)
- Productionカテゴリを追加
- tdd-standard-practice を追加

### v1.0.0 (2026-02-12)
- 初回リリース（Meta-Skills 10種）

---

**Author**: RyoMurakami1983
