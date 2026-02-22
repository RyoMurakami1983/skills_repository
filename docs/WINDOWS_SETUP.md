# Windows 開発環境セットアップガイド

このリポジトリをWindowsで開発する際の推奨設定をまとめています。

## 📋 前提ツール

| ツール | 用途 | インストール |
|--------|------|-------------|
| Git for Windows | バージョン管理 | https://git-scm.com/ |
| uv | Pythonランタイム・パッケージ管理 | `winget install astral-sh.uv` |
| gh | GitHub CLI | `winget install GitHub.cli` |

## 🔧 改行コード（LF/CRLF）ポリシー

### 方針

このリポジトリでは `.gitattributes` で改行コードを制御しています。

| ファイル種別 | 改行コード | 理由 |
|-------------|-----------|------|
| `*.py`, `*.sh`, `*.ts`, `*.js` | LF | クロスプラットフォーム互換性 |
| `*.ps1`, `*.cmd`, `*.bat` | CRLF | Windows PowerShell/CMD互換性 |
| `*.cs`, `*.csproj`, `*.sln` | CRLF | Visual Studio互換性 |
| `*.md`, `*.json`, `*.yaml` | auto（LF推奨） | エディタの設定に依存 |

### 推奨Git設定

```powershell
# autocrlf は無効にし、.gitattributes に任せる
git config --global core.autocrlf false

# Git内部のエンコーディング設定
git config --global i18n.commitEncoding utf-8
git config --global i18n.logOutputEncoding utf-8

# 日本語ファイル名のエスケープを無効化
git config --global core.quotepath false
```

### トラブルシューティング

**「LF will be replaced by CRLF」警告が出る場合**:

```powershell
# 1. autocrlf の現在値を確認
git config --global core.autocrlf
# → "true" なら "false" に変更

# 2. 変更後、インデックスを再正規化
git rm --cached -r .
git reset HEAD
git restore .
```

## 🔤 UTF-8 標準化

### PowerShell推奨設定

PowerShellセッション開始時に以下を実行（または `$PROFILE` に追記）:

```powershell
# 出力エンコーディングをUTF-8に統一
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# PowerShell 5.x の場合は追加で:
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
```

`$PROFILE` に追記する方法:

```powershell
# プロファイルが無ければ作成
if (!(Test-Path -Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }

# エディタで開いて上記を追記
notepad $PROFILE
```

### gh CLI でのUTF-8安全手順

Issue/PRの本文に日本語や絵文字を含む場合、`--body` ではなく `--body-file` を使用:

```powershell
# 1. 本文をUTF-8ファイルに書き出し（BOMなし）
$body = @"
## 背景
日本語テキストや絵文字 🎯 を安全に扱えます。
"@
[System.IO.File]::WriteAllText("body.md", $body, [System.Text.UTF8Encoding]::new($false))

# 2. --body-file で渡す
gh issue create --title "タイトル" --body-file body.md

# 3. 一時ファイルを削除
Remove-Item body.md
```

### トラブルシューティング

**文字化け（mojibake）が起きた場合のチェックリスト**:

1. `$OutputEncoding` → UTF-8 か？
2. `[Console]::OutputEncoding` → UTF-8 か？
3. Windows Terminal を使っているか？（従来の `cmd.exe` ウィンドウは非推奨）
4. ファイルがBOMなしUTF-8で保存されているか？

```powershell
# 確認コマンド
$OutputEncoding
[Console]::OutputEncoding
```

## 🪝 Gitフックのセットアップ

### clone後にフックを有効化する

リポジトリのフック（pre-commit, pre-push）はclone後に自動適用されません。以下のいずれかの方法で有効化してください。

**方法1: `core.hooksPath`（推奨）**

リポジトリに `.githooks/` ディレクトリがある場合、以下で有効化できます：

```powershell
# リポジトリレベルでフックディレクトリを指定
git config core.hooksPath .githooks
```

この方法ではフックがバージョン管理され、セットアップスクリプトの実行が不要です。

**方法2: セットアップスクリプト**

```powershell
.\scripts\setup.ps1
```

### トラブルシューティング

**`setup.ps1` がセキュリティエラーで失敗する場合**:

PowerShellの実行ポリシーが `Restricted`（デフォルト）だとスクリプトが実行できません：

```powershell
# 現在のポリシーを確認
Get-ExecutionPolicy -Scope CurrentUser

# CurrentUserスコープでRemoteSignedに変更
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# 変更後、再実行
.\scripts\setup.ps1
```

---

## 🐍 Python実行の規約

### 基本ルール

このリポジトリでは **`uv run`** を標準のPython実行方法とします。

```powershell
# ✅ 推奨
uv run python skills/skill-quality-validation/scripts/validate_skill.py path/to/SKILL.md

# ❌ 非推奨（直接呼び出し）
python skills/skill-quality-validation/scripts/validate_skill.py path/to/SKILL.md
```

### 理由

- `uv` がPythonバージョンと依存関係を自動管理
- `pyproject.toml` の設定が自動適用される
- 仮想環境の手動管理が不要

### よく使うコマンド

```powershell
# スキル検証
uv run python skills\skill-quality-validation\scripts\validate_skill.py path\to\SKILL.md

# テスト実行
uv run pytest

# 依存関係の同期
uv sync
```
