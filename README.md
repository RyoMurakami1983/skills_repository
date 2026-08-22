> [!IMPORTANT]
> このリポジトリは2026-08-22に開発を終了し、[happy-ai-work](https://github.com/RyoMurakami1983/happy-ai-work)へ統合しました。現在の開発・導入手順は移行先を参照してください。このrepoのCopilot向けskills／agentsは履歴としてのみ保持します。判断の詳細は[ARCHIVE_NOTICE.md](ARCHIVE_NOTICE.md)に記録しています。

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
$env:SKILLS_REPO = "C:\tools\skills_repository"
git clone https://github.com/RyoMurakami1983/skills_repository.git $env:SKILLS_REPO
Set-Location $env:SKILLS_REPO
uv sync
uv run python skills\skill\_eval\scripts\validate_skill.py skills\git-initial-setup\SKILL.md
```

WSL / Linux / macOS を含む詳細手順は `docs/INSTALL.md` を参照してください。

## Windows の `.copilot` へ同期

最もよく使う想定の手順です。`skills` と `agents` を同期し、`business/` 配下の skill は `~/.copilot/skills/` に統合して同期します。

```powershell
$env:SKILLS_REPO = "C:\tools\skills_repository"  # 未設定なら先に設定
Set-Location $env:SKILLS_REPO
git pull --ff-only

New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\skills | Out-Null
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.copilot\agents | Out-Null

robocopy skills   $env:USERPROFILE\.copilot\skills   /MIR
robocopy agents   $env:USERPROFILE\.copilot\agents   /MIR
Get-ChildItem -Path business -Directory | ForEach-Object {
  robocopy $_.FullName (Join-Path $env:USERPROFILE ".copilot\skills\$($_.Name)") /MIR
}
Copy-Item copilot\copilot-instructions.md $env:USERPROFILE\.copilot\copilot-instructions.md
```

`/MIR` は同期先の不要ファイルを削除します。`business/` は skill ごとに `.copilot\skills\{skill-name}` へ個別同期しています。

WSL 側の `~/.copilot/` への同期、クロス環境パス設定、Linux/macOS 手順は `docs/INSTALL.md` にまとめています。

## カテゴリ

| カテゴリ | 用途 | 主な配置先 | 詳細 |
| --- | --- | --- | --- |
| `copilot/` | グローバル開発規律 | `~/.copilot/` | [`copilot/copilot-instructions.md`](copilot/copilot-instructions.md) |
| `agents/` | 師範エージェント | `~/.copilot/agents/` | [Agents](#agents) |
| `skills/` | 汎用 skill 群 | `~/.copilot/skills/` | [`skills/SKILLS_README.md`](skills/SKILLS_README.md) |
| `business/` | 業務向け skill 群 | `~/.copilot/skills/{skill-name}/` | [`business/`](business/) |
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

## SKILL の言語方針

この repo では、`skills/` 配下の skill の正本を **`SKILL.md` 1つ** に統一します。

`skills/skill/` で確立した型を基に、従来の「英語 `SKILL.md` + `references/SKILL.ja.md`」運用から、**日本語 `SKILL.md` を正本とする運用**へ横展開します。目的は英語を排除することではなく、二重管理コストを減らし、validator / template / generator を含む skill の型を repo 実態に合わせて簡素化することです。

不変条件として、**JSON key / schema key / file name / enum は英語のまま維持**します。`references/` は overflow docs や補助資料の置き場として残し、`references/SKILL.ja.md` は常設前提にしません。

判断理由と移行原則は [`docs/adr/ADR-003-skill-japanese-primary-language-policy.md`](docs/adr/ADR-003-skill-japanese-primary-language-policy.md) を参照してください。

## 最近の主要変更

**2026-03**

- `skills/skill/` を追加してメタスキル群を単一入口 + sub_skills / _foundation / _eval / scripts 構成へ整備し、そこで固めた日本語正本化ルールを `skills/` の残り skill へ横展開して `references/SKILL.ja.md` の常設をやめた
- `business/` と `dotnet/` の skill を日本語 `SKILL.md` 正本へ揃え、`references/SKILL.ja.md` を段階的に廃止した
- `skill/_eval/scripts/validate_skill.py`、`skill/scripts/create_skill.py` などを新構造へ移し、スキル用ツールチェインを同梱した
- README は Windows の `.copilot` 同期を最優先に保ちつつ、詳細を `docs/INSTALL.md` へ分離した

詳細は [`CHANGELOG.md`](CHANGELOG.md) を参照してください。ユーザーから最新化の指示があったときは、この欄も合わせて更新します。

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。

## 作成者

**RyoMurakami1983**

