# Environment Portability Guidelines（環境ポータビリティ・ガイドライン）

> **Values**: ニュートラルな視点 / 基礎と型の追求

このドキュメントは、SKILL.md のコードブロックで複数OS・シェルに対応する
標準テンプレートとフォールバック指示を定義する。

---

## 判断フロー

```
コマンドを書く
│
├─ OS/シェル非依存（git, gh, npm, python 等）
│  → 単一コードブロックでOK
│
├─ PowerShell と Bash で構文が違う
│  → 両方を提供（優先度順に並べる）
│
└─ OS固有の動作が必要（レジストリ, .plist 等）
   → OS別セクションで分離
```

---

## 標準テンプレート

### テンプレート1: 共通コマンド（推奨）

コマンドがどのシェルでも動作する場合。

```bash
# Works in both PowerShell and Bash
git add .
git commit -m "feat: add feature"
git push origin HEAD
```

使い所: `git`, `gh`, `npm`, `pip`, `uv`, `docker` などの CLI ツール。

---

### テンプレート2: PowerShell + Bash 両対応

同じ操作でもシェル構文が異なる場合。**PowerShell を先に記述**（このリポジトリは
Windows 開発環境が主）。

```powershell
# PowerShell
$Branch = git branch --show-current
$Body = @"
## 概要
変更の説明
"@
$Body | Out-File -FilePath "$env:TEMP\pr_body.md" -Encoding utf8
gh pr create --title "feat: 変更" --body-file "$env:TEMP\pr_body.md"
```

```bash
# Bash
BRANCH=$(git branch --show-current)
BODY_FILE="$(mktemp "${TMPDIR:-/tmp}/pr_body.XXXXXX")"
trap 'rm -f "$BODY_FILE"' EXIT
cat > "$BODY_FILE" <<'EOF'
## 概要
変更の説明
EOF
gh pr create --title "feat: 変更" --body-file "$BODY_FILE"
```

**PowerShell 優先の理由**: このリポジトリの開発環境が Windows/PowerShell 主体
（`docs/WINDOWS_SETUP.md` 参照）。

---

### テンプレート3: パス変数

パスの区切り文字はシェル非依存な書き方を優先する。

```powershell
# PowerShell — $env: 変数でポータブルなパスを構築
$TempFile = Join-Path $env:TEMP "output.txt"
$RepoRoot = git rev-parse --show-toplevel
```

```bash
# Bash
TEMP_FILE="${TMPDIR:-/tmp}/output.txt"
REPO_ROOT=$(git rev-parse --show-toplevel)
```

**避けるべきパターン**:
```bash
# ❌ ハードコードされた絶対パス（環境固有）
/Users/johndoe/projects/repo/scripts/run.sh
C:\Users\johndoe\projects\repo\scripts\run.ps1
```

---

### テンプレート4: 条件分岐フォールバック

PowerShell 専用の機能で Bash フォールバックが困難な場合。

```powershell
# PowerShell（推奨）
$result = Get-Content output.json | ConvertFrom-Json
$result.items | ForEach-Object { Write-Host $_.name }
```

```bash
# Bash（jq が必要）
# Install: sudo apt install jq  または  brew install jq
jq -r '.items[].name' output.json
```

> **Note**: Bash 版は追加ツール（`jq`）が必要。環境に応じてインストールすること。

---

### テンプレート5: OS判定フォールバック

スクリプト内で動的に OS を判定する場合（主にシェルスクリプト）。

```bash
#!/usr/bin/env bash
# Detect OS and set appropriate temp directory
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Git Bash on Windows
    TEMP_DIR="${TEMP:-/tmp}"
else
    # macOS / Linux
    TEMP_DIR="${TMPDIR:-/tmp}"
fi
```

---

## PowerShell vs Bash 対応表

| 操作 | PowerShell | Bash |
|------|-----------|------|
| 変数設定 | `$VAR = "value"` | `VAR="value"` |
| 変数参照 | `$VAR` | `$VAR` |
| 環境変数 | `$env:HOME` | `$HOME` |
| 一時ファイル | `$env:TEMP\file.txt` | `${TMPDIR:-/tmp}/file.txt` |
| コマンド出力取得 | `` $x = cmd `` | `` x=$(cmd) `` |
| 条件分岐 | `if ($x -eq "y") {...}` | `if [ "$x" = "y" ]; then...fi` |
| NULL条件 | `$x ?? "default"` | `${x:-default}` |
| JSON解析 | `ConvertFrom-Json` | `jq` (要インストール) |
| マルチライン文字列 | `@"..."@` | `<<'EOF'...EOF` |
| エラーハンドリング | `$ErrorActionPreference = "Stop"` | `set -euo pipefail` |
| ファイル書き込み | `Out-File -Encoding utf8` | `> file` |
| パイプ | `\|` | `\|` |

---

## フォールバック指示パターン

### パターン1: スキル内のフォールバックノート

```markdown
> **Windows (PowerShell)**: 上記の PowerShell コードを使用してください。
> **macOS/Linux (Bash)**: 以下の Bash 版を使用してください。
```

### パターン2: 前提条件の明示

```markdown
## Dependencies

- Git 2.30+
- GitHub CLI (`gh`) 2.0+ — `gh auth status` で確認
- **Windows**: PowerShell 5.1+ または PowerShell 7+
- **macOS/Linux**: Bash 4.0+ または Zsh 5.0+
- (オプション) `jq` 1.6+ — JSON 解析が必要な場合のみ
```

### パターン3: 既知の環境差異のドキュメント化

スキルの `references/environment-notes.md` に記載する（推奨）:

```markdown
# Environment Notes

## Windows 固有の注意点

- `mktemp` は Git Bash 経由で使用可能、ネイティブ PowerShell では不可
- パスの区切りは `\` だが `git` コマンドでは `/` も動作する
- ファイル権限の概念が異なる（`chmod` は無効）

## macOS 固有の注意点

- `sed -i` は macOS BSD 版と GNU 版で動作が異なる
  - macOS: `sed -i '' 's/old/new/g'`
  - Linux: `sed -i 's/old/new/g'`

## CI (GitHub Actions) での動作

- `ubuntu-latest` ランナーを想定
- Windows ランナーでの動作は未検証の場合がある
```

---

## スキル別環境対応状況

| スキル | PowerShell | Bash | 備考 |
|--------|-----------|------|------|
| `git-commit-practices` | ✅ | ✅ | 共通コマンドのみ |
| `github-pr-workflow` | ✅ | ✅ | 両対応テンプレート |
| `git-ops-folder-init` | ✅ | ✅ | safe.directory 注意 |
| `python-skill-deploy` | ✅ | ✅ | PS + Bash スクリプト |
| `dotnet-skill-deploy` | ✅ | ✅ | PS + Bash スクリプト |

---

## アンチパターン

```markdown
<!-- ❌ 環境非依存コマンドに不要な2段構成 -->
\`\`\`powershell
git status
\`\`\`
\`\`\`bash
git status
\`\`\`

<!-- ✅ 共通コマンドは1ブロックで十分 -->
\`\`\`bash
git status
\`\`\`
```

```markdown
<!-- ❌ 片方だけの環境依存コマンドを無断で使用 -->
New-Item -ItemType Directory -Path "output"   # PowerShell のみ

<!-- ✅ 環境を明示するか、ポータブルな代替を提供 -->
mkdir output   # bash/PowerShell 共通
```
