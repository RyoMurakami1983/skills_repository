---
name: dotnet-skill-deploy
description: >
  選択したdotnetスキルをプロジェクトの .github/skills/ にデプロイする。
  新規.NETプロジェクトのセットアップ時、チームへのスキル展開時、
  またはskills_repositoryからのスキル更新時に使用。
allowed-tools:
  - powershell
metadata:
  author: RyoMurakami1983
  tags: [dotnet, deployment, skills, project-setup, automation]
  invocable: false
---

# dotnetスキルをプロジェクトにデプロイする

`skills_repository/dotnet/` から選択したdotnetスキルを、対象プロジェクトの `.github/skills/` にデプロイする対話型ワークフロー。エージェントがプロジェクト分析、カテゴリ選択、実行を `Deploy-DotnetSkills.ps1` 経由でガイドする。

## When to Use This Skill

以下の場面で使用：
- 新規.NETプロジェクトのセットアップ時に関連スキルをデプロイしたい
- チームメンバーのオンボーディングでプロジェクトレベルのコーディング標準が必要
- skills_repositoryの最新版でプロジェクトレベルのスキルを更新したい
- 「dotnet skills をプロジェクトに追加して」と依頼された
- 新規WPF、Blazor、クラスライブラリプロジェクトを開始する

## Related Skills

- **`dotnet-modern-csharp-coding-standards`** — 頻繁にデプロイされる基盤スキル
- **`dotnet-wpf-mvvm-patterns`** — WPF MVVM基盤スキル
- **`dotnet-project-structure`** — プロジェクト構造スキル
- **`git-initial-setup`** — 新規プロジェクトでスキルデプロイと併用

---

## Dependencies

- PowerShell 5.1+（Windows）
- `skills_repository` がローカルにクローン済み（通常 `C:\tools\skills_repository`）

## Core Principles

1. **選択的デプロイ** — 関連するスキルのみコピーし、エージェントのコンテキストノイズを回避（余白の設計）。なぜ？ — 不要なスキルがプロジェクトにあると、Copilotエージェントのコンテキストウィンドウに入り、関連しないパターンを参照してしまう。WPFプロジェクトにBlazorスキルは不要。

2. **カテゴリ駆動選択** — `dotnet-shihan` 管轄に整合したカテゴリで一貫したグルーピング（基礎と型）。なぜ？ — 31スキルを一つずつ選ぶのは非効率。dotnet-shihan.agent.mdの分類と同じカテゴリを使うことで、エージェントとユーザーの間に共通言語が生まれる。

3. **べき等な操作** — 安全に再実行可能。既存スキルは `-Force` 指定時のみ上書き（継続は力）。なぜ？ — 誤って実行しても既存のスキルを壊さない。更新時は明示的に `-Force` を使うことで意図を明確にする。

4. **透明性優先** — 実行前に何がデプロイされるか常に表示。`-WhatIf` でドライラン対応（ニュートラルな視点）。なぜ？ — 「何が起こるか分からない」ツールは使われない。事前プレビューが信頼を生む。

---

## Workflow: dotnetスキルのデプロイ

### Step 1 — プロジェクト情報の確認

デプロイのコンテキストをユーザーから収集：

1. **ターゲットプロジェクトパス**: `.github/skills/` を作成する場所を確認
2. **プロジェクトの種類**: スキル推奨のためのプロジェクトカテゴリを特定

```
質問例:
- 「どのプロジェクトにスキルをデプロイしますか？（プロジェクトのルートパスを教えてください）」
- 「このプロジェクトの種類は？」
  選択肢: WPFアプリケーション、クラスライブラリ、Blazorアプリ、コンソールアプリ、その他
```

**出力**: ターゲットパスとプロジェクト種別が確定。

> **Values**: ニュートラルな視点（先入観なく、プロジェクトの実態に合わせる）

### Step 2 — カテゴリ・スキルの提案

プロジェクト種別に基づき適切なスキルカテゴリを推奨：

| プロジェクト種別 | 推奨カテゴリ | 概算スキル数 |
|---------------|------------|------------|
| WPFアプリケーション | `wpf-app`（複合） | 15 |
| クラスライブラリ | `foundation` + `data` | 8 |
| Blazorアプリ | `foundation` + `testing`（playwright） | 12 |
| コンソールアプリ | `foundation` | 5 |
| フルスタック | `all` | 31 |

**`-List` で全オプションを表示**:

```powershell
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -List
```

**利用可能なカテゴリ**（`dotnet-shihan.agent.md` と整合）:

| カテゴリ | 数 | 説明 |
|---------|---|------|
| `foundation` | 5 | 技術基盤（modern-csharp, type-design, project-structure, slopwatch, api-design） |
| `data` | 3 | データ・永続化（efcore, database-performance, serialization） |
| `testing` | 7 | 並行・テスト・CI（concurrency, testcontainers, snapshot-testing, verify-email, crap-analysis, playwright-blazor, playwright-ci-caching） |
| `wpf` | 11 | WPF・デスクトップ（mvvm, secure-config, oracle, dify, UIコンポーネント, マッチング） |
| `infra` | 6 | インフラ・パッケージ（DI, configuration, local-tools, package-management, marketplace, mjml） |
| `wpf-app` | 15 | **複合**: foundation一部 + wpf + infra一部 |
| `all` | 31 | 全dotnetスキル |

推奨を提示し、ユーザーに調整を依頼：

```
「WPFアプリケーションには 'wpf-app' カテゴリ（15スキル）を推奨します。
コーディング標準、MVVMパターン、セキュア設定、全WPF UIコンポーネントが含まれます。
このまま進めますか？カスタマイズしますか？」
```

**出力**: 選択されたカテゴリ・個別スキルが確定。

> **Values**: 基礎と型（カテゴリが選択の型を提供）/ 成長の複利（必要なスキルだけで精度向上）

### Step 3 — デプロイ実行

確定したパラメータでデプロイスクリプトを実行：

**カテゴリデプロイ**:

```powershell
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -Target "<project_path>" `
    -Category <selected_category>
```

**個別スキルデプロイ**:

```powershell
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -Target "<project_path>" `
    -Skills <skill1>,<skill2>,<skill3>
```

**更新（既存を上書き）**:

```powershell
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -Target "<project_path>" `
    -Category <selected_category> `
    -Force
```

**重要**: プレビュー希望時は先に `-WhatIf` を実行：

```powershell
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -Target "<project_path>" `
    -Category <selected_category> `
    -WhatIf
```

**出力**: スキルが `<project_path>\.github\skills\` にコピー完了。

> **Values**: 継続は力（繰り返し実行可能な自動化）

### Step 4 — 確認と次のステップ案内

デプロイ後の確認とガイダンス：

1. **デプロイ確認**: デプロイされたスキルディレクトリを一覧表示

```powershell
Get-ChildItem "<project_path>\.github\skills" -Directory | Select-Object Name
```

2. **Git管理のアドバイス**: デプロイされたスキルのGit追跡はユーザーが決定

```
「スキルが .github/skills/ にデプロイされました。
デフォルトではGit追跡されていません。
プロジェクトリポジトリで管理する場合は以下を実行:
  git add .github/skills/
  git commit -m 'feat: add dotnet skills for project-level guidance'」
```

3. **次のステップ提案**:
   - プロジェクト内のデプロイ済みスキルを確認
   - 新規リポジトリなら `git-initial-setup` を実行
   - `@dotnet-shihan` でデプロイ済みスキルを参照しながらコーディング開始

**出力**: デプロイ確認と具体的な次のアクション。

> **Values**: 成長の複利（デプロイ後のアクション案内で学習を加速）

---

## Best Practices

- ✅ **カテゴリで始め、個別スキルで微調整** — `-Category` で一括、`-Skills` で追加
- ✅ **まずプレビュー** — 実デプロイ前に必ず `-WhatIf` を提案
- ✅ **少なく、多くなく** — 余分なスキルはエージェントのコンテキストノイズ
- ✅ **定期的に更新** — skills_repository更新時に `-Force` で再実行
- ✅ **プロジェクト種別に合わせる** — WPFアプリにBlazor/Playwrightスキルは不要

## Anti-Patterns

- ❌ **デフォルトで `all` をデプロイ** — 不要なコンテキストノイズを追加。関連カテゴリを選択
- ❌ **確認をスキップ** — Step 4で必ずデプロイ結果を確認
- ❌ **パスをハードコード** — `-SourceRoot` と `-Target` パラメータを使い、仮定しない
- ❌ **更新時の `-Force` 忘れ** — なしでは既存スキルがサイレントにスキップされる

---

## スクリプトリファレンス

デプロイスクリプトは `scripts/Deploy-DotnetSkills.ps1` に配置。

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `-SourceRoot` | string | Yes | dotnetスキルのソースディレクトリパス |
| `-Target` | string | デプロイ時 | ターゲットプロジェクトのルートパス |
| `-Category` | string | デプロイ時* | カテゴリ名: foundation, data, testing, wpf, infra, wpf-app, all |
| `-Skills` | string[] | デプロイ時* | カンマ区切りのスキル名 |
| `-List` | switch | No | 利用可能なカテゴリとスキルを表示 |
| `-Force` | switch | No | 既存スキルを上書き |
| `-WhatIf` | switch | No | コピーせずプレビュー |

\* デプロイには `-Category` または `-Skills` のいずれかが必要。

---

## FAQ

**Q: skills_repositoryはどこにクローンすべき？**
A: 推奨場所は `C:\tools\skills_repository`。`-SourceRoot` パラメータでその `dotnet/` サブディレクトリを指定。

**Q: `-Category` と `-Skills` を組み合わせられる？**
A: はい。スクリプトは両方の選択をマージ（重複自動排除）。

**Q: 既存スキルがターゲットにある場合は？**
A: `-Force` なしではスキップ。`-Force` ありでは上書き（削除して再コピー）。

**Q: コピーされたスキルはGit管理される？**
A: 自動的には管理されない。ユーザーが `git add` するかどうかを決定。

**Q: production/ スキルもデプロイできる？**
A: このスキルはdotnet専用。productionスキルは手動コピー: `Copy-Item -Recurse production\* .github\skills\`。
