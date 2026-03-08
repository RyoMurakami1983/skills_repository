# GitHub Copilot Skills Collection

GitHub Copilot Agent Skillsのコレクション

## 📋 概要

このリポジトリは、GitHub Copilot Agentで使用できるSkillsを集約・管理するためのものです。
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
| `agents/` | 師範エージェント（dotnet/python/typescript/skill） | グローバル（~/.copilot/agents/） | [下記参照](#agents) |
| `skills/` | Skill作成支援 + Git/GitHub ワークフロー | グローバル（~/.copilot/skills/） | [SKILLS_README.md](skills/SKILLS_README.md) |
| `dotnet/` | .NET/C# WPF開発ワークフロー | プロジェクト（.github/skills/） | [下記参照](#dotnet-skills) |
| `python/` | Python開発ワークフロー | プロジェクト（.github/skills/） | [下記参照](#python-skills) |
| `typescript/` | TypeScript/Node.js開発ワークフロー | プロジェクト（.github/skills/） | [下記参照](#typescript-skills) |
| `production/` | MVP/本番向け開発プラクティス | プロジェクト（.github/skills/） | [PRODUCTION_SKILLS_README.md](production/PRODUCTION_SKILLS_README.md) |

## 🏁 Developer Quickstart

### 前提ツール

- **Git** — バージョン管理
- **[uv](https://docs.astral.sh/uv/)** — Python ランタイム管理
  - Windows（ホスト）: `winget install astral-sh.uv`
  - WSL（`uv sync` を実行する環境）:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    exec "$SHELL" -l
    ```
- **[gh](https://cli.github.com/)** — GitHub CLI
  - Windows（ホスト）: `winget install GitHub.cli`
  - WSL: [Linux 向けインストール手順](https://github.com/cli/cli#linux) を参照

> 下記の `uv sync` は **WSL 側** で実行する前提です。WSL 側にも `uv` をインストールしてください。

### セットアップ（このRepoの推奨: Windows側にclone + WSLで利用）

```bash
# 1. 前提: Windows側に clone 済み（例: C:\tools\skills_repository）
#    git clone https://github.com/RyoMurakami1983/skills_repository.git C:\tools\skills_repository

# 2. WSL から作業ディレクトリへ移動
cd /mnt/c/tools/skills_repository

# 3. 依存関係の同期
uv sync

# 4. 動作確認：スキル検証を実行
uv run python skills/skill-quality-validation/scripts/validate_skill.py skills/git-initial-setup/SKILL.md
```

**Windows PowerShell で直接作業する場合**:

```powershell
git clone https://github.com/RyoMurakami1983/skills_repository.git C:\tools\skills_repository
Set-Location C:\tools\skills_repository
uv sync
uv run python skills\skill-quality-validation\scripts\validate_skill.py skills\git-initial-setup\SKILL.md
```

> この `skills_repository` は `SKILL.md` 作成・文書更新・軽い検証が中心のため、Windows 側に置いて Windows/WSL の両方から触りやすくする運用を標準とします。

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

### 🌐 クロス環境パス設定（Windows / WSL 共通）

このリポジトリのパスは環境によって異なります。以下の環境変数を設定しておくと、後述のコマンドをそのまま使用できます。

> **推奨運用（このRepo向け）**: リポジトリは Windows 側 (`C:\tools\skills_repository`) に置き、普段の編集・検証は WSL から `/mnt/c/tools/skills_repository` を使って進めます。

> 将来の実アプリ用リポジトリは同じ基準で固定せず、**Windows デスクトップ系は Windows 側、Python/TypeScript/Linux 系は WSL 側**を基本に使い分ける運用を推奨します。

| 環境 | 推奨クローン先 | 環境変数設定 |
|------|--------------|-------------|
| Windows (PowerShell) | `C:\tools\skills_repository` | `$env:SKILLS_REPO = "C:\tools\skills_repository"` |
| WSL (bash) | `/mnt/c/tools/skills_repository` | `export SKILLS_REPO="/mnt/c/tools/skills_repository"` |
| Linux/macOS (bash) | `/tmp/skills-repository` | `export SKILLS_REPO="/tmp/skills-repository"` |

```powershell
# PowerShell: まずセッションに設定
$env:SKILLS_REPO = "C:\tools\skills_repository"

# PowerShell: 永続化（$PROFILE が無ければ作成してから追記）
if (!(Test-Path -Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force | Out-Null }
if (-not (Select-String -Path $PROFILE -Pattern 'SKILLS_REPO' -SimpleMatch -Quiet)) {
    Add-Content -Path $PROFILE -Value "`n`$env:SKILLS_REPO = `"C:\tools\skills_repository`""
}
```

```bash
# bash/WSL: まずセッションに設定
export SKILLS_REPO="/mnt/c/tools/skills_repository"

# bash/WSL: 永続化（bash は ~/.bashrc、zsh は ~/.zshrc）
grep -qxF 'export SKILLS_REPO="/mnt/c/tools/skills_repository"' ~/.bashrc 2>/dev/null || \
  echo 'export SKILLS_REPO="/mnt/c/tools/skills_repository"' >> ~/.bashrc

# zsh を使う場合はこちら
# grep -qxF 'export SKILLS_REPO="/mnt/c/tools/skills_repository"' ~/.zshrc 2>/dev/null || \
#   echo 'export SKILLS_REPO="/mnt/c/tools/skills_repository"' >> ~/.zshrc
```

```bash
# 反映確認
echo "$SKILLS_REPO"
test -d "$SKILLS_REPO/.git" && echo "SKILLS_REPO is ready"
```

```powershell
# 反映確認
$env:SKILLS_REPO
Test-Path "$env:SKILLS_REPO\.git"
```

> PowerShell の `$PROFILE` 自体の作成方法や UTF-8 設定は [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) も参照してください。

### 🪟+🐧 Windows に clone / WSL で開発する場合の基本フロー

1. **clone の正本は Windows 側** (`C:\tools\skills_repository`)
2. **日常開発は WSL 側** (`/mnt/c/tools/skills_repository`)
3. **Copilot の同期先は別管理**
   - Windows Copilot: `%USERPROFILE%\.copilot\`
   - WSL Copilot: `~/.copilot/`
4. **両方使うなら両方同期** — 片方にコピーしただけでは、もう片方には反映されません

> 補足: `/mnt/c/...` 上の開発は便利ですが、重い watcher や大量ファイル監視では Linux ネイティブ側のファイルシステムのほうが安定する場合があります。

> この注意は主に実アプリ開発向けです。この `skills_repository` は watcher 依存の重い開発が中心ではないため、Windows 側配置を標準にして問題ありません。

### グローバルインストール（全プロジェクト共通）

**まず Windows 側に clone を用意**:

```powershell
# 0) 環境変数を設定（未設定の場合）
$env:SKILLS_REPO = "C:\tools\skills_repository"

# 1) 専用のローカルcloneを作成（初回のみ）
git clone https://github.com/RyoMurakami1983/skills_repository.git $env:SKILLS_REPO

# 2) Windows 側の同期先フォルダを作成（初回のみ）
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\skills | Out-Null
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\agents | Out-Null

# 3) Windows 側へ同期
Set-Location $env:SKILLS_REPO
git pull --ff-only
robocopy skills $env:USERPROFILE\.copilot\skills /MIR
robocopy agents $env:USERPROFILE\.copilot\agents /MIR
Copy-Item copilot\copilot-instructions.md $env:USERPROFILE\.copilot\copilot-instructions.md
```

> 注意: `/MIR` は同期先の不要ファイルを削除します。`$env:USERPROFILE\.copilot\skills` と `$env:USERPROFILE\.copilot\agents` を専用同期先として使用してください。

**WSL 側の `.copilot` に同期（WSL から実行）**:

```bash
cd "$SKILLS_REPO"
git pull --ff-only
mkdir -p ~/.copilot/skills ~/.copilot/agents
rsync -a --delete "$SKILLS_REPO/skills/" ~/.copilot/skills/
rsync -a --delete "$SKILLS_REPO/agents/" ~/.copilot/agents/
cp "$SKILLS_REPO/copilot/copilot-instructions.md" ~/.copilot/copilot-instructions.md
```

> 注意: `rsync --delete` は同期先の不要ファイルを削除します。`~/.copilot/skills` と `~/.copilot/agents` を専用同期先として使用してください。

**Windows PowerShell から WSL 側の `.copilot` もまとめて同期**:

```powershell
Set-Location $env:SKILLS_REPO
git pull --ff-only

$skillsRepoWsl = wsl wslpath -a "$env:SKILLS_REPO"

wsl bash -lc 'mkdir -p ~/.copilot/skills ~/.copilot/agents'
wsl bash -lc "rsync -a --delete '$skillsRepoWsl/skills/' ~/.copilot/skills/"
wsl bash -lc "rsync -a --delete '$skillsRepoWsl/agents/' ~/.copilot/agents/"
wsl bash -lc "cp '$skillsRepoWsl/copilot/copilot-instructions.md' ~/.copilot/copilot-instructions.md"
```

> `wsl ...` は既定ディストリビューション / 既定ユーザーを対象にします。複数の WSL ディストリビューションを使う場合は `wsl -d <DistroName> bash -lc '...'` を使用してください。`rsync` が未導入なら WSL 側で `sudo apt install rsync` などを先に実行します。

**Windows と WSL の両方を確認**:

```powershell
Test-Path "$env:USERPROFILE\.copilot\skills\git-commit-practices\SKILL.md"
wsl bash -lc 'test -f ~/.copilot/skills/git-commit-practices/SKILL.md && echo OK'
```

> **エージェント優先順位**: ユーザーレベル（`~/.copilot/agents/`）> リポレベル（`.github/agents/`）> Organization。グローバルに配置した師範エージェントは、どのプロジェクトでも `@dotnet-shihan`, `@python-shihan`, `@typescript-shihan`, `@skill-shihan` として呼び出し可能です。

**Linux/macOS（初回）**:

```bash
export SKILLS_REPO="/tmp/skills-repository"  # 任意のパスに変更可
git clone https://github.com/RyoMurakami1983/skills_repository.git "$SKILLS_REPO"
mkdir -p ~/.copilot/skills ~/.copilot/agents
cp -r "$SKILLS_REPO/skills/"* ~/.copilot/skills/
cp -r "$SKILLS_REPO/agents/"* ~/.copilot/agents/
cp "$SKILLS_REPO/copilot/copilot-instructions.md" ~/.copilot/copilot-instructions.md
```

**Linux/macOS（更新時）**:

```bash
cd "$SKILLS_REPO"
git pull --ff-only
rsync -a --delete "$SKILLS_REPO/skills/" ~/.copilot/skills/
rsync -a --delete "$SKILLS_REPO/agents/" ~/.copilot/agents/
cp "$SKILLS_REPO/copilot/copilot-instructions.md" ~/.copilot/copilot-instructions.md
```

> 注意: `cp -r` の再実行だけでは削除済みSkill/Agentが同期先に残る場合があります。更新時は `rsync --delete` を使用してください。

**Codex（WSL利用）**:

```bash
# WSL上でCodex用skills配置（例: ~/.codex/skills）
export SKILLS_REPO="/mnt/c/tools/skills_repository"  # 環境変数を設定
mkdir -p ~/.codex/skills
rsync -a --delete "$SKILLS_REPO/skills/" ~/.codex/skills/
```

> Windows側のcloneが `C:\tools\skills_repository` の場合、WSLパスは `/mnt/c/tools/skills_repository` になります。`$SKILLS_REPO` 環境変数を使えばパスを1箇所で管理できます。

### プロジェクトインストール（プロジェクト固有）

production/ や言語別Skillsは、プロジェクトの`.github/skills/`にコピーして使用します。

**dotnetスキルのデプロイ（推奨: `dotnet-skill-deploy` スキル使用）**:

`@dotnet-shihan` に「dotnetスキルをプロジェクトにデプロイして」と依頼すると、対話型でプロジェクト種別に応じたスキルを選択・コピーできます。

手動実行する場合:

```powershell
# カテゴリ一覧を表示
& "$env:SKILLS_REPO\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "$env:SKILLS_REPO\dotnet" -List

# WPFアプリ開発一式をデプロイ
& "$env:SKILLS_REPO\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "$env:SKILLS_REPO\dotnet" `
    -Target C:\path\to\my-project `
    -Category wpf-app
```

**pythonスキルのデプロイ（推奨: `python-skill-deploy` スキル使用）**:

`@python-shihan` に「pythonスキルをプロジェクトにデプロイして」と依頼すると、対話型でカテゴリまたは個別スキルを選択してコピーできます。

```powershell
# カテゴリ一覧を表示
& "$env:SKILLS_REPO\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "$env:SKILLS_REPO\python" -List

# Python開発環境スキルをデプロイ
& "$env:SKILLS_REPO\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "$env:SKILLS_REPO\python" `
    -Target C:\path\to\my-project `
    -Category dev-env
```

```bash
# WSL/bash からカテゴリ一覧を表示
"$SKILLS_REPO/skills/python-skill-deploy/scripts/Deploy-PythonSkills.sh" \
  --source-root "$SKILLS_REPO/python" \
  --list

# WSL/bash から Python 開発環境スキルをデプロイ
"$SKILLS_REPO/skills/python-skill-deploy/scripts/Deploy-PythonSkills.sh" \
  --source-root "$SKILLS_REPO/python" \
  --target /path/to/my-project \
  --category dev-env
```

**typescriptスキルの手動コピー**:

```bash
mkdir -p .github/skills
cp -r "$SKILLS_REPO/typescript/"* .github/skills/
```

**productionスキルの手動コピー**:

```bash
mkdir -p .github/skills
cp -r "$SKILLS_REPO/production/"* .github/skills/
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
| `@typescript-shihan` | TypeScript/Node.jsの設計・実装・レビュー | 先生（既定）/ 求道者 |
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

## 🐍 Python Skills

Python 開発ワークフローのためのスキル群（2スキル）。

| スキル | 説明 |
|--------|------|
| `python-setup-dev-environment` | `uv` / `ruff` / `mypy` / VSCode を使った再現可能な Python 開発環境の標準化 |
| `python-debug-tdd` | Red → investigation → Green の流れで Python バグを最小修正する TDD 型デバッグ |

## 🟦 TypeScript Skills

TypeScript / Node.js / デスクトップ拡張のためのスキル群（2スキル）。

| スキル | 説明 |
|--------|------|
| `typescript-setup-dev-environment` | Node.js / npm / ESLint / Prettier / Jest / VSCode による再現可能な TypeScript 開発環境 |
| `typescript-tauri-setup` | 既存 TypeScript プロジェクトに Tauri v2 デスクトップアプリ環境を追加 |

## 📚 ドキュメント

- **[PHILOSOPHY.md](PHILOSOPHY.md)** - 開発憲法（Values / Mission / Vision）
- **[copilot/copilot-instructions.md](copilot/copilot-instructions.md)** - グローバル開発規律（全プロジェクト適用）
- **[skills/SKILLS_README.md](skills/SKILLS_README.md)** - Skills詳細情報・一覧
- **[python/](python/)** - Python skills 一覧
- **[typescript/](typescript/)** - TypeScript skills 一覧
- **[production/PRODUCTION_SKILLS_README.md](production/PRODUCTION_SKILLS_README.md)** - Production Skills詳細情報

### 💬 エージェントの動作を知りたいとき

モードを宣言しなくても大丈夫です。気になったときに、そのまま聞いてください。

| こんなとき | 話しかけ方の例 |
|-----------|-------------|
| 何をしているか分からない | `今何してる？` / `動作がよく分からない` |
| 使えるモードを知りたい | `モードの説明をして` / `どんな動き方ができる？` |
| モデルの切り替わり方を知りたい | `モデルは固定？` / `さっきSonnet 4.6だったのはなぜ？` |
| アップデートで変わった点を知りたい | `最近何が変わった？` / `updateで何が変わった？` |
| エージェント自体について知りたい | `あなたについて教えて` / `何ができる？` |

エージェントは **短い答えを先に返し、詳しく聞かれたら掘り下げます**。  
たとえばモデルについて聞かれたら、`/model` で切り替える通常の仕組みと、sub-agent 呼び出し時にその回だけ `model` 指定で上書きできるケースを分けて説明します。  
詳細は [`skills/agent-explain-on-demand/`](skills/agent-explain-on-demand/) を参照してください。

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
- Skills総数: skills / dotnet / production の各カテゴリ配下を参照

### v1.1.0 (2026-02-13)
- Productionカテゴリを追加
- tdd-standard-practice を追加

### v1.0.0 (2026-02-12)
- 初回リリース（Meta-Skills 10種）

---

**Author**: RyoMurakami1983
