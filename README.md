# GitHub Copilot Skills Collection

GitHub Copilot Agent / CLI で使う skills・agents・business workflows を管理するリポジトリです。

普段よく使う操作は `Windows の .copilot へ同期` だと想定し、この README ではそこに最短で到達できる構成にしています。

詳細なセットアップや運用手順は `docs/` に分離しています。

## 概要

- `skills/` はグローバルに使うスキル群
- `agents/` は師範エージェント群
- `business/` は業務向けワークフロー群
- `dotnet/`, `python/`, `typescript/`, `production/` はプロジェクト側 `.github/skills/` に配置して使います

## クイックスタート

```powershell
git clone https://github.com/RyoMurakami1983/skills_repository.git C:\tools\skills_repository
Set-Location C:\tools\skills_repository
uv sync
uv run python skills\skill-quality-validation\scripts\validate_skill.py skills\git-initial-setup\SKILL.md
```

WSL / Linux / macOS を含む詳細手順は `docs/INSTALL.md` を参照してください。

## Windows の `.copilot` へ同期

最もよく使う想定の手順です。`skills` に加えて `agents` と `business` も同期します。

```powershell
Set-Location C:\tools\skills_repository
git pull --ff-only

New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\skills | Out-Null
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\agents | Out-Null
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\business | Out-Null

robocopy skills   $env:USERPROFILE\.copilot\skills   /MIR
robocopy agents   $env:USERPROFILE\.copilot\agents   /MIR
robocopy business $env:USERPROFILE\.copilot\business /MIR
Copy-Item copilot\copilot-instructions.md $env:USERPROFILE\.copilot\copilot-instructions.md
```

`/MIR` は同期先の不要ファイルを削除します。専用同期先として使ってください。

WSL 側の `~/.copilot/` への同期、クロス環境パス設定、Linux/macOS 手順は `docs/INSTALL.md` にまとめています。

## カテゴリ

| カテゴリ | 用途 | 主な配置先 | 詳細 |
| --- | --- | --- | --- |
| `copilot/` | グローバル開発規律 | `~/.copilot/` | [`copilot/copilot-instructions.md`](copilot/copilot-instructions.md) |
| `agents/` | 師範エージェント | `~/.copilot/agents/` | [Agents](#agents) |
| `skills/` | 汎用 skill 群 | `~/.copilot/skills/` | [`skills/SKILLS_README.md`](skills/SKILLS_README.md) |
| `business/` | 業務向け skill 群 | `~/.copilot/business/` | [`business/`](business/) |
| `dotnet/` | .NET / C# / WPF 向け | `.github/skills/` | [`dotnet/`](dotnet/) |
| `python/` | Python 向け | `.github/skills/` | [`python/`](python/) |
| `typescript/` | TypeScript / Node.js 向け | `.github/skills/` | [`typescript/`](typescript/) |
| `production/` | MVP / 本番運用向け | `.github/skills/` | [`production/PRODUCTION_SKILLS_README.md`](production/PRODUCTION_SKILLS_README.md) |

## Agents

グローバル配置すると、どのプロジェクトでも `@agent-name` で呼び出せます。

| Agent | 役割 |
| --- | --- |
| `@dotnet-shihan` | C# / .NET / WPF の設計・実装・レビュー |
| `@python-shihan` | Python の設計・実装・レビュー |
| `@typescript-shihan` | TypeScript / Node.js の設計・実装・レビュー |
| `@skill-shihan` | Skill の作成・レビュー・バリデーション |

## 主なスキル群

- [`skills/`](skills/) — スキル作成支援、Git / GitHub ワークフロー
- [`business/evidence-response/`](business/evidence-response/) — 監査・質問票・調査票への evidence-response ワークフロー
- [`business/pdf/`](business/pdf/) — PDF 抽出、OCR、分割・結合、フォーム処理
- [`dotnet/`](dotnet/) — .NET / C# / WPF ワークフロー
- [`python/`](python/) — Python 開発ワークフロー
- [`typescript/`](typescript/) — TypeScript / Node.js 開発ワークフロー
- [`production/`](production/) — MVP / 本番向け実践集

プロジェクト用 skills の配置方法は `docs/INSTALL.md` を参照してください。

## ドキュメント

- [`docs/INSTALL.md`](docs/INSTALL.md) — セットアップ、各環境への同期、プロジェクト配備
- [`docs/WINDOWS_SETUP.md`](docs/WINDOWS_SETUP.md) — Windows の UTF-8、改行コード、PowerShell 設定
- [`.github/copilot-instructions.md`](.github/copilot-instructions.md) — この repo 専用の README / CHANGELOG 更新ルール
- [`skills/SKILLS_README.md`](skills/SKILLS_README.md) — `skills/` 配下の詳細
- [`PHILOSOPHY.md`](PHILOSOPHY.md) — 開発憲法と設計思想
- [`docs/adr/`](docs/adr/) — 設計判断の背景を残す ADR
- [`CHANGELOG.md`](CHANGELOG.md) — 変更履歴

ADR は「なぜその設計判断を採ったのか」を後から追えるように残すための記録です。

## 最近の主要変更

**2026-03**

- `business/` カテゴリを整理し、`evidence-response` と `pdf` を業務向け workflow として扱いやすくした
- `CHANGELOG.md` を月次サマリ方針に見直し、repo 固有の更新ルールを `.github/copilot-instructions.md` に追加した
- README は Windows の `.copilot` 同期を最優先に保ちつつ、詳細を `docs/INSTALL.md` へ分離した

詳細は [`CHANGELOG.md`](CHANGELOG.md) を参照してください。ユーザーから最新化の指示があったときは、この欄も合わせて更新します。

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。

## 作成者

**RyoMurakami1983**
