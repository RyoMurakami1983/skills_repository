# インストール・同期ガイド

このドキュメントは、skills\_repository のセットアップから各環境への同期までの詳細手順をまとめています。

---

## 📋 前提ツール

- **Git** — バージョン管理
- **[uv](https://docs.astral.sh/uv/)** — Python ランタイム管理
  - Windows: `winget install astral-sh.uv`
  - WSL/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh && exec "$SHELL" -l`
- **[gh](https://cli.github.com/)** — GitHub CLI
  - Windows: `winget install GitHub.cli`
  - WSL/Linux: [Linux 向けインストール手順](https://github.com/cli/cli#linux)

> Windows 固有の設定（UTF-8、改行コード等）は [WINDOWS\_SETUP.md](WINDOWS_SETUP.md) を参照してください。

---

## 🌐 クロス環境パス設定

このリポジトリのパスは環境によって異なります。環境変数を設定しておくと、後述のコマンドをそのまま使用できます。

| 環境 | 推奨クローン先 | 環境変数設定 |
|------|--------------|-------------|
| Windows (PowerShell) | `C:\tools\skills_repository` | `$env:SKILLS_REPO = "C:\tools\skills_repository"` |
| WSL (bash) | `/mnt/c/tools/skills_repository` | `export SKILLS_REPO="/mnt/c/tools/skills_repository"` |
| Linux/macOS (bash) | `/tmp/skills-repository` | `export SKILLS_REPO="/tmp/skills-repository"` |

### PowerShell で永続化

```powershell
$env:SKILLS_REPO = "C:\tools\skills_repository"

# $PROFILE に追記（未作成なら作成）
if (!(Test-Path -Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force | Out-Null }
if (-not (Select-String -Path $PROFILE -Pattern 'SKILLS_REPO' -SimpleMatch -Quiet)) {
    Add-Content -Path $PROFILE -Value "`n`$env:SKILLS_REPO = `"C:\tools\skills_repository`""
}
```

### bash/WSL で永続化

```bash
export SKILLS_REPO="/mnt/c/tools/skills_repository"

grep -qxF 'export SKILLS_REPO="/mnt/c/tools/skills_repository"' ~/.bashrc 2>/dev/null || \
  echo 'export SKILLS_REPO="/mnt/c/tools/skills_repository"' >> ~/.bashrc
```

### 反映確認

```powershell
$env:SKILLS_REPO
Test-Path "$env:SKILLS_REPO\.git"
```

```bash
echo "$SKILLS_REPO"
test -d "$SKILLS_REPO/.git" && echo "SKILLS_REPO is ready"
```

> PowerShell の `$PROFILE` 作成方法や UTF-8 設定は [WINDOWS\_SETUP.md](WINDOWS_SETUP.md) を参照してください。

---

## 🏁 初回セットアップ

### Windows（推奨）

```powershell
$env:SKILLS_REPO = "C:\tools\skills_repository"
git clone https://github.com/RyoMurakami1983/skills_repository.git $env:SKILLS_REPO
Set-Location $env:SKILLS_REPO
uv sync
uv run python skills\skill\_eval\scripts\validate_skill.py skills\git-initial-setup\SKILL.md --level L2
```

### WSL からの作業

```bash
export SKILLS_REPO="/mnt/c/tools/skills_repository"
cd "$SKILLS_REPO"
uv sync
uv run python skills/skill/_eval/scripts/validate_skill.py skills/git-initial-setup/SKILL.md --level L2
```

> WSL で作業する場合は、`uv sync` も **WSL 側** で実行します。WSL 環境にも `uv` をインストールしてください。

---

## 🔄 グローバル同期（全プロジェクト共通）

### Windows .copilot への同期

```powershell
Set-Location $env:SKILLS_REPO
git pull --ff-only

New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\skills | Out-Null
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\agents | Out-Null
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\business | Out-Null

robocopy skills   $env:USERPROFILE\.copilot\skills   /MIR
robocopy agents   $env:USERPROFILE\.copilot\agents   /MIR
robocopy business $env:USERPROFILE\.copilot\business  /MIR
Copy-Item copilot\copilot-instructions.md $env:USERPROFILE\.copilot\copilot-instructions.md
```

> `/MIR` は同期先の不要ファイルを削除します。`$env:USERPROFILE\.copilot\skills`、`agents`、`business` を専用同期先として使用してください。

### WSL .copilot への同期（WSL から実行）

```bash
cd "$SKILLS_REPO"
git pull --ff-only
mkdir -p ~/.copilot/skills ~/.copilot/agents ~/.copilot/business
rsync -a --delete "$SKILLS_REPO/skills/" ~/.copilot/skills/
rsync -a --delete "$SKILLS_REPO/agents/" ~/.copilot/agents/
rsync -a --delete "$SKILLS_REPO/business/" ~/.copilot/business/
cp "$SKILLS_REPO/copilot/copilot-instructions.md" ~/.copilot/copilot-instructions.md
```

### Windows PowerShell から WSL 側もまとめて同期

```powershell
Set-Location $env:SKILLS_REPO
git pull --ff-only

$skillsRepoWsl = wsl wslpath -a "$env:SKILLS_REPO"
wsl env "SKILLS_REPO_WSL=$skillsRepoWsl" bash -lc 'set -euo pipefail; mkdir -p ~/.copilot/skills ~/.copilot/agents ~/.copilot/business; rsync -a --delete "$SKILLS_REPO_WSL/skills/" ~/.copilot/skills/; rsync -a --delete "$SKILLS_REPO_WSL/agents/" ~/.copilot/agents/; rsync -a --delete "$SKILLS_REPO_WSL/business/" ~/.copilot/business/; cp "$SKILLS_REPO_WSL/copilot/copilot-instructions.md" ~/.copilot/copilot-instructions.md'
```

> `wsl ...` は既定ディストリビューション / 既定ユーザーを対象にします。複数の WSL ディストリビューションを使う場合は `wsl -d <DistroName>` を指定してください。`rsync` が未導入なら WSL 側で `sudo apt install rsync` を実行します。

### 同期確認

```powershell
Test-Path "$env:USERPROFILE\.copilot\skills\git-commit-practices\SKILL.md"
Test-Path "$env:USERPROFILE\.copilot\business\evidence-response\SKILL.md"
wsl bash -lc 'test -f ~/.copilot/skills/git-commit-practices/SKILL.md && echo OK'
```

### Linux/macOS（初回）

```bash
export SKILLS_REPO="/tmp/skills-repository"
git clone https://github.com/RyoMurakami1983/skills_repository.git "$SKILLS_REPO"
mkdir -p ~/.copilot/skills ~/.copilot/agents ~/.copilot/business
cp -r "$SKILLS_REPO/skills/"* ~/.copilot/skills/
cp -r "$SKILLS_REPO/agents/"* ~/.copilot/agents/
cp -r "$SKILLS_REPO/business/"* ~/.copilot/business/
cp "$SKILLS_REPO/copilot/copilot-instructions.md" ~/.copilot/copilot-instructions.md
```

### Linux/macOS（更新時）

```bash
cd "$SKILLS_REPO"
git pull --ff-only
rsync -a --delete "$SKILLS_REPO/skills/" ~/.copilot/skills/
rsync -a --delete "$SKILLS_REPO/agents/" ~/.copilot/agents/
rsync -a --delete "$SKILLS_REPO/business/" ~/.copilot/business/
cp "$SKILLS_REPO/copilot/copilot-instructions.md" ~/.copilot/copilot-instructions.md
```

> `cp -r` の再実行だけでは削除済みファイルが同期先に残る場合があります。更新時は `rsync --delete` を使用してください。

### Codex（WSL利用）

```bash
export SKILLS_REPO="/mnt/c/tools/skills_repository"
mkdir -p ~/.codex/skills
rsync -a --delete "$SKILLS_REPO/skills/" ~/.codex/skills/
```

---

## 📦 プロジェクト固有インストール

production/ や言語別スキルは、プロジェクトの `.github/skills/` にコピーして使用します。

### dotnet スキルのデプロイ（推奨: `dotnet-skill-deploy` スキル使用）

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

### python スキルのデプロイ（推奨: `python-skill-deploy` スキル使用）

`@python-shihan` に「pythonスキルをプロジェクトにデプロイして」と依頼すると、対話型でカテゴリまたは個別スキルを選択してコピーできます。

```powershell
& "$env:SKILLS_REPO\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "$env:SKILLS_REPO\python" -List

& "$env:SKILLS_REPO\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "$env:SKILLS_REPO\python" `
    -Target C:\path\to\my-project `
    -Category dev-env
```

```bash
# WSL/bash
"$SKILLS_REPO/skills/python-skill-deploy/scripts/Deploy-PythonSkills.sh" \
  --source-root "$SKILLS_REPO/python" --list

"$SKILLS_REPO/skills/python-skill-deploy/scripts/Deploy-PythonSkills.sh" \
  --source-root "$SKILLS_REPO/python" \
  --target /path/to/my-project \
  --category dev-env
```

### typescript / production スキルの手動コピー

```bash
mkdir -p .github/skills
cp -r "$SKILLS_REPO/typescript/"* .github/skills/
cp -r "$SKILLS_REPO/production/"* .github/skills/
```

---

## 🪝 Windows + WSL 運用メモ

### 基本フロー

1. **clone の正本は Windows 側** (`C:\tools\skills_repository`)
2. **日常開発は WSL 側** (`/mnt/c/tools/skills_repository`)
3. **Copilot の同期先は別管理** — Windows: `%USERPROFILE%\.copilot\`、WSL: `~/.copilot/`
4. **両方使うなら両方同期** — 片方にコピーしただけでは、もう片方には反映されません

> `/mnt/c/...` 上の開発は便利ですが、重い watcher や大量ファイル監視では Linux ネイティブ側のファイルシステムのほうが安定する場合があります。この `skills_repository` は watcher 依存の重い開発ではないため、Windows 側配置で問題ありません。

### エージェント優先順位

ユーザーレベル（`~/.copilot/agents/`）> リポレベル（`.github/agents/`）> Organization

グローバル配置した師範エージェントは、どのプロジェクトでも `@dotnet-shihan`, `@python-shihan`, `@typescript-shihan`, `@skill-shihan` として呼び出し可能です。

---

## 🗃️ ローカル参照ディレクトリ運用

- `local_reference_skills/`: 外部 skill の一時参照置き場（開発時のみ使用）
- `local_docs/`: 外部ドキュメントの一時参照置き場（開発時のみ使用）
- どちらも **ディレクトリのみ Git 管理**し、配下ファイルは `.gitignore` で追跡しません

---

## よく使うコマンド

```powershell
# スキル検証（単体）
uv run python skills\skill\_eval\scripts\validate_skill.py path\to\SKILL.md --level L2

# スキル検証（一括）
Get-ChildItem skills -Recurse -Filter SKILL.md | ForEach-Object { uv run python skills\skill\_eval\scripts\validate_skill.py $_.FullName --level L1 }

# テスト実行
uv run pytest

# JSON形式で出力
uv run python skills\skill\_eval\scripts\validate_skill.py path\to\SKILL.md --level L2 --json
```

### README / ドキュメント更新前の軽量チェック

README や手順書を更新したら、PR 前に次を確認します。

- 内部アンカー: 変更した README 内リンクが GitHub の自動アンカーと一致
- 前提ツール: 追加したコマンドに必要な CLI / 実行環境を明記
- 可変パス: 固定パスの直書きではなく `SKILLS_REPO` 変数を優先
- コピペ実行性: 変更したコマンドを想定シェルで1回は実行確認
- 差分健全性: 空白・改行崩れがない

```bash
npm run lint:text
git diff --check -- README.md
```

```powershell
Get-Command git, node, npm, uv, gh -ErrorAction Stop | Select-Object Name, Source
```
