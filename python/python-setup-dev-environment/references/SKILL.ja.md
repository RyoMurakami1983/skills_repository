---
name: python-setup-dev-environment
description: Set up and run a reproducible Python dev environment with uv, ruff, mypy, and VSCode.
author: RyoMurakami1983
tags: [python, uv, ruff, mypy, vscode]
invocable: false
version: 1.0.0
---

# Python開発環境をセットアップする

`uv`・`ruff`・`mypy`・VSCode保存時ガードを使って、再現可能なPython開発環境を構築・運用するための単一ワークフローです。

## このスキルを使うとき

このスキルは次のときに使います:
- 新しいPythonプロジェクトを立ち上げ、実行方法を `uv run` に統一したいとき
- lint/format/type-check の順序を固定して品質を安定させたいとき
- VSCode保存時の自動整形で差分が崩れる問題を回避したいとき
- チームメンバー間で同じPython実行環境を再現したいとき
- `python ...` の運用から `uv` ベース運用へ移行したいとき

---

## Related Skills

- **`skills-validate-skill`** — このSkill文書を検証するときに使用
- **`git-commit-practices`** — 環境変更を原子的にコミットするときに使用
- **`github-pr-workflow`** — 環境変更をPR経由で反映するときに使用

---

## Dependencies

- `uv`（必須）
- `ruff` / `mypy`（開発依存）
- VSCode + Ruff拡張（推奨）

---

## Core Principles

1. **実行入口を一本化する** — Python関連コマンドを `uv run` で統一し、環境差異を減らす（基礎と型）
2. **コミット前の高速フィードバック** — `ruff` と `mypy` を固定順で回し、品質劣化を早期検知する（成長の複利）
3. **依存状態を再現可能に保つ** — `pyproject.toml` と `uv.lock` を常にセットで扱う（温故知新）
4. **エディタ自動化を安全側で制御する** — 保存時アクションを `explicit` にして想定外の書き換えを防ぐ（ニュートラル）
5. **最小構成から段階導入する** — まず `uv + ruff + mypy` に絞って安定化し、必要になったら拡張する（継続は力）

---

## Workflow: Set Up and Operate Python Dev Environment

### Step 1: 初期化と依存関係の固定

まずはプロジェクト情報と依存関係の基盤を作ります。

```powershell
# プロジェクト初期化
uv init .

# 管理下Pythonを確認
uv run python --version

# 開発依存を追加
uv add --dev ruff mypy
```

使うとき: 新規立ち上げ時、または既存環境を標準化するとき。

**Values**: 基礎と型 / 継続は力

### Step 2: 日次実行コマンドを `uv run` に統一

`uv run` を共通プレフィックスにすることで、実行環境のズレを防ぎます。

```powershell
uv run python path\to\script.py
uv run ruff check .
uv run ruff format .
uv run mypy .
```

使うとき: ローカルPythonやPATH差分で実行結果がぶれるとき。

**Values**: ニュートラル / 基礎と型

### Step 3: 品質チェック順序を固定

順序を固定して、不要な差分とレビューコストを減らします。

| フェーズ | コマンド | 理由 |
|---------|---------|------|
| 1 | `uv run ruff format .` | 先に整形して差分を安定化 |
| 2 | `uv run ruff check .` | 整形後のlint違反を確認 |
| 3 | `uv run mypy .` | 型整合性を最後に確認 |

使うとき: コミット前、PR作成前の最終確認をするとき。

**Values**: 継続は力 / 成長の複利

### Step 4: VSCode保存時ガードを設定

Ruff formatterを使いつつ、保存時の自動修正を明示実行に限定します。

```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

使うとき: 「保存しただけでコードが崩れた」問題を防ぎたいとき。

**Values**: ニュートラル / 継続は力

### Step 5: 再現性を検証

他環境でも同じ状態を再現できるか確認します。

```powershell
uv sync
uv run ruff check .
uv run mypy .
```

使うとき: 新規メンバー参加時、CI前提の再現性確認時。

**Values**: 温故知新 / 基礎と型

### Step 6: チーム展開前に用語を定義

用語定義を先に揃え、レビューやオンボーディング時の認識ズレを減らします。

- **UV**: Python向けのパッケージ・プロジェクト管理ツール。`uv run` による実行と依存解決を一元化する。
- **LSP (Language Server Protocol)**: エディタと診断・補完機能の連携仕様。開発体験の一貫性に直結する。
- **CI**: Continuous Integration。ローカルで使うチェック手順を自動検証へ再利用する基盤。

使うとき: チームへ運用ルールを共有する前、またはオンボーディング資料を作成するとき。

**Values**: ニュートラル / 成長の複利

---

## Best Practices

- Python実行系コマンドは常に `uv run` を使う
- `pyproject.toml` と `uv.lock` はセットでコミットする
- Ruff/mypy設定は最初は最小構成で開始する
- PR前にローカルで `ruff` と `mypy` を実行する
- 例外運用はREADMEまたはreferencesに明記する

---

## Common Pitfalls

1. **`python ...` を直接実行してしまう**  
Fix: 手順・スクリプト・ドキュメントを `uv run ...` へ統一する。

2. **保存時に自動fixを全適用してしまう**  
Fix: `source.fixAll` / `source.organizeImports` を `explicit` にする。

3. **依存追加後にlockfileを更新しない**  
Fix: `uv add`/`uv remove` を使い、`uv.lock` 差分を必ずコミットする。

---

## Anti-Patterns

- ベース運用が固まる前に便利ツールを過剰追加する
- Pythonフォーマッタを複数混在させる
- lintが通ったことを理由に型チェックを省略する
- `uv pip install` を通常運用コマンドとして使い、理由や手順を文書化しない

---

## Quick Reference

### 初期セットアップ

```powershell
uv init .
uv add --dev ruff mypy
uv run python --version
```

### 日次チェック

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy .
```

### 再現

```powershell
uv sync
```

### Decision Table（状況別の使い分け）

| 状況 | 推奨アクション | なぜ |
|------|----------------|------|
| まずローカルで素早く確認したい | `uv run ruff check .` | lint違反を早期に検出できる |
| コミット前に差分を安定化したい | `uv run ruff format .` → `uv run ruff check .` | 整形を先に確定し、レビュー差分を最小化できる |
| PR前に品質ゲートを通したい | `uv run mypy .` | 型レベルの回帰を事前に検知できる |

---

## FAQ

**Q: このSkillにpoethepoetを含めるべき？**  
A: いいえ。今回は最小構成に限定し、必要なら別Issueで段階導入します。

**Q: なぜ `codeActionsOnSave` を `explicit` にするの？**  
A: 保存時の想定外一括修正を防ぎ、差分を制御しやすくするためです。

**Q: `uv pip install` は使ってよい？**  
A: 原則禁止です。通常運用は `uv add` / `uv remove` を使って再現性を維持します。やむを得ず実行する場合は、理由と実行内容を `README.md` などに必ず記載してください。

---

## Resources

- [uv documentation](https://docs.astral.sh/uv/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [mypy documentation](https://mypy.readthedocs.io/)

---

## Changelog

### Version 1.0.0 (2026-02-14)
- Issue #29 対応として初版を追加

