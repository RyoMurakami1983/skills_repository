---
name: python-skill-deploy
description: >
  選択した Python skill をプロジェクトの .github/skills/ へ配備する。Use when: 新しい Python プロジェクトへ skill を導入したいとき、チームへ共通 Python skill を展開したいとき、skills_repository の更新を反映したいとき。
---
# Pythonスキルをプロジェクトへデプロイする

`skills_repository/python/` から選択したPythonスキルを、対象プロジェクトの `.github/skills/` へ配置する対話型ワークフローです。PowerShell と Bash の両方から実行できます。

## こんなときに使う
次のような場面で使います。
- 新しいPythonプロジェクトへ、プロジェクトレベルのPythonワークフロースキルを入れたいとき
- チームメンバーにPython運用ガイドをリポジトリ内で配布したいとき
- 既存プロジェクトへ、このリポジトリの最新Pythonスキルを反映したいとき
- 「python skills をプロジェクトに追加して」や「deploy python skills」と依頼されたとき
- どのPythonスキルがコピーされるかを、実行前にプレビューしたいとき

## Related Skills

- **`python-setup-dev-environment`** — Pythonプロジェクトで最初に配布しやすい基盤スキル
- **`python-debug-tdd`** — `all` で一緒に配布できる追加ワークフロー
- **`git-initial-setup`** — 新規リポジトリの初期整備と併用しやすい
- **`skill`** — このスキル文書を検証するときに使う

---

## Dependencies

- PowerShell 5.1+ または Bash 4.0+
- `skills_repository` がローカルにクローン済みであること
- `$env:SKILLS_REPO`（PowerShell）または `$SKILLS_REPO`（bash/WSL）がリポジトリルートを指していること

---

## Core Principles

1. **選択的にデプロイする** — そのプロジェクトで今必要なスキルだけをコピーする（余白の設計）
2. **カテゴリを先に提案する** — まず小さな既定カテゴリを提示し、必要なら個別スキルで補う（基礎と型）
3. **再実行を安全にする** — 既存スキルは `-Force` を明示したときだけ上書きする（継続は力）
4. **何をするか先に見せる** — list/preview の結果で変更範囲を見える化してから実行する（ニュートラル）

---

## Workflow: Pythonスキルをデプロイする

### Step 1 — 対象プロジェクトとPython文脈を確認する

どこへデプロイするか、そしてそのPythonプロジェクトに何が必要かを先に確認します。

```powershell
# デプロイ前に確認する質問
# - どのプロジェクトルートへ .github/skills/ を作るか
# - 開発環境整備が主目的か、デバッグ系ワークフローも欲しいか
```

判断ルール:
- 新規Pythonプロジェクトなら `dev-env` を既定にする
- 現在あるPythonプロジェクトスキルを全部入れたいときだけ `all` を使う
- カテゴリがほぼ合っていて一つだけ足りないときは `-Skills` を追加する

使うとき: 「Pythonスキルを入れて」のような広い依頼を具体化するとき。

> **Values**: ニュートラル / 基礎と型

### Step 2 — カテゴリまたは個別スキルを提案する

最小で役立つ構成を提案し、その後に選択肢一覧を見せます。

| プロジェクト状況 | 推奨選択 | 理由 |
|---|---|---|
| 新しいPythonリポジトリ | `dev-env` | まず再現可能な開発環境の型を入れるため |
| 今あるPythonプロジェクトスキルを全部使いたい | `all` | `python/` 配下の全スキルを配布できるため |
| 既定カテゴリに1つだけ追加したい | `-Category dev-env -Skills ...` | 既定を保ったまま例外を最小化できるため |

```powershell
& "<skills_repository>\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "<skills_repository>\python" `
    -List
```

```bash
"<skills_repository>/skills/python-skill-deploy/scripts/Deploy-PythonSkills.sh" \
  --source-root "<skills_repository>/python" \
  --list
```

現在のカテゴリ:

| カテゴリ | 数 | 内容 |
|---|---:|---|
| `dev-env` | 1 | `python-setup-dev-environment` |
| `all` | 可変 | `python/` 配下に現在存在する全Pythonソーススキル |

使うとき: コピー前に推奨案と選択肢を示したいとき。

> **Values**: 基礎と型 / 成長の複利

### Step 3 — 安全にデプロイを実行する

確定した選択でスクリプトを実行します。初回や不安があるときは `-WhatIf` を先に提案します。

```powershell
# カテゴリデプロイをプレビュー
& "<skills_repository>\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "<skills_repository>\python" `
    -Target "<project_path>" `
    -Category dev-env `
    -WhatIf

# カテゴリを実デプロイ
& "<skills_repository>\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "<skills_repository>\python" `
    -Target "<project_path>" `
    -Category dev-env

# 追加スキルを個別指定
& "<skills_repository>\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "<skills_repository>\python" `
    -Target "<project_path>" `
    -Category dev-env `
    -Skills python-debug-tdd
```

```bash
# カテゴリデプロイをプレビュー
"<skills_repository>/skills/python-skill-deploy/scripts/Deploy-PythonSkills.sh" \
  --source-root "<skills_repository>/python" \
  --target "<project_path>" \
  --category dev-env \
  --what-if

# カテゴリを実デプロイ
"<skills_repository>/skills/python-skill-deploy/scripts/Deploy-PythonSkills.sh" \
  --source-root "<skills_repository>/python" \
  --target "<project_path>" \
  --category dev-env
```

更新時は `-Force` を付けて、上書き意図を明示します。

✅ **良い例**: 初めて触るターゲットには先に `-WhatIf` を実行し、その後に同じコマンドから `-WhatIf` だけ外して本番実行する。
❌ **悪い例**: 初回からいきなり `-Force` を使ったり、ソースパスを記憶頼みで決め打ちしたりする。
Why: 先にプレビューするとパス誤りや想定外上書きを、実変更前に止められるからです。

使うとき: 対象パスと配布対象が確定したあと。

> **Values**: 継続は力 / 基礎と型

### Step 4 — デプロイ結果を確認し、次の一手を案内する

デプロイ後にディレクトリ一覧を確認し、次にやることまで案内します。

```powershell
Get-ChildItem "<project_path>\.github\skills" -Directory | Select-Object Name
```

次の一手:
1. `.github/skills/` にコピーされたスキルを確認する
2. `git add .github/skills/` するかどうか判断する
3. `@python-shihan` で、そのプロジェクトの作業を始める

使うとき: コピーが終わり、結果確認と引き継ぎをしたいとき。

> **Values**: 成長の複利 / ニュートラル

---

## Best Practices

- まず `dev-env` から始め、本当に必要なときだけ個別スキルを足す
- 初回の本番コピー前には `-WhatIf` を提案する
- `all` は動的に保ち、新しいPythonソーススキルが増えても再利用できるようにする
- Pythonプロジェクトスキルが増減したら `agents/python-shihan.agent.md` とカテゴリ定義を同期する
- 更新時だけ `-Force` を使い、上書き意図をあいまいにしない
- WSL や bash 主体の作業では `Deploy-PythonSkills.sh` を優先し、PowerShell 変換の手間を減らす
- Windows PowerShell / WSL / ログ出力で崩れないよう、スクリプトのコンソール出力は ASCII 安全に保つ

---

## Common Pitfalls

1. **`-SourceRoot` を間違える**
   Fix: `skills/` ではなく、リポジトリの `python/` を指定する。

2. **習慣で全部デプロイしてしまう**
   Fix: 既定は `dev-env` にし、`all` は本当に全部必要なときだけ使う。

3. **更新時の上書き意図を明示しない**
   Fix: 既存コピーを更新したいときだけ `-Force` を付ける。

4. **コピー後の確認を省略する**
   Fix: 直後に `.github/skills/` を一覧表示し、期待したディレクトリがあるか確認する。

5. **Windows/WSL で文字化けした出力をそのまま使う**
   Fix: スクリプト出力は ASCII 安全に保ち、ローカライズ説明は SKILL 文書側へ寄せる。

---

## Anti-Patterns

- Explorer/Finder で手動コピーして再現可能な手順を残さない
- スクリプト内でリポジトリパスをハードコードし、`-SourceRoot` / `-Target` を使わない
- 配布後にGit追跡するかどうかをユーザーへ案内せず終える

## Troubleshooting

- **`SourceRoot not found` が出る**
  - 原因: リポジトリパスの指定先が誤っている。
  - 対処: `$env:SKILLS_REPO` を確認し、`-SourceRoot "$env:SKILLS_REPO\python"` を使う。

- **`Skills not found in source` が出る**
  - 原因: 指定したスキル名が `python/` 配下のディレクトリ名と一致していない。
  - 対処: `-List` で正式名を確認してから再実行する。

- **ターゲットに見た目の変化がない**
  - 原因: `-WhatIf` のままだったか、`-Force` なしで既存スキルがスキップされた。
  - 対処: サマリー出力を確認し、必要なら `-WhatIf` を外すか `-Force` を付けて再実行する。

- **WSL で PowerShell を呼びたくない**
  - 原因: bash 主体の環境で PowerShell スクリプトを経由したくない。
  - 対処: `skills/python-skill-deploy/scripts/Deploy-PythonSkills.sh` を使い、`--source-root` / `--target` / `--category` で同じ操作を行う。

---

## Quick Reference

### Preflight Checklist

- [ ] `skills_repository` の場所が分かっており、その下に `python/` が存在する
- [ ] ターゲットプロジェクトルートが確定している
- [ ] `dev-env` / `all` / 個別 `-Skills` のどれを使うか決まっている
- [ ] 本番コピー前に `-WhatIf` を使うかどうか決めている

### Self-Review Checklist

- [ ] `Deploy-PythonSkills.ps1` または `Deploy-PythonSkills.sh` を使っている
- [ ] ソースルート（`-SourceRoot` / `--source-root`）が `python/` を指している
- [ ] サマリー出力が期待した配布対象と一致している
- [ ] 配布後にターゲット `.github/skills/` を一覧表示して確認した

### Decision Table

| 状況 | 推奨アクション | なぜ |
|---|---|---|
| 新しいPythonプロジェクトで、まだスキルが無い | `dev-env` を配布する | 最小ノイズで基盤ワークフローを入れられる |
| 今あるPythonプロジェクトスキルを全て入れたい | `all` を配布する | 現在のソーススキルをまとめて反映できる |
| 既存コピーを最新版へ更新したい | `-Force` を付ける | 上書き意図を明示できる |
| 影響範囲に不安がある | 先に `-WhatIf` を付ける | ファイル変更前にコピー範囲を確認できる |

### Command Summary

```powershell
# カテゴリとスキル一覧
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -List

# プレビュー
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -Target <project> -Category dev-env -WhatIf

# カテゴリ配布
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -Target <project> -Category dev-env

# カテゴリ + 追加スキル
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -Target <project> -Category dev-env -Skills python-debug-tdd

# 既存コピー更新
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -Target <project> -Category all -Force
```

```bash
# カテゴリとスキル一覧
Deploy-PythonSkills.sh --source-root <python_path> --list

# プレビュー
Deploy-PythonSkills.sh --source-root <python_path> --target <project> --category dev-env --what-if

# カテゴリ配布
Deploy-PythonSkills.sh --source-root <python_path> --target <project> --category dev-env
```

---

## Resources

- [PowerShell documentation](https://learn.microsoft.com/powershell/)
- [Bash manual](https://www.gnu.org/software/bash/manual/bash.html)
- [uv documentation](https://docs.astral.sh/uv/)
- [Python Setup Dev Environment](../../../python/python-setup-dev-environment/SKILL.md)
- [Deploy Dotnet Skills to Project](../../dotnet-skill-deploy/SKILL.md)
