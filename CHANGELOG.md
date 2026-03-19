# Changelog

このファイルは、release ノートではなく **月次サマリ形式の主要変更ログ** です。

完全な履歴は Git / PR を参照し、ここには利用者や将来の自分が見返して価値のある変更だけを残します。

## 2026-03

### Added

- `session-issue-autopilot`、`agent-explain-on-demand`、`git-ops-folder-init` など、運用系 skills を拡充
- `typescript-shihan` を追加し、師範エージェント群を拡張
- `python-skill-deploy` の workflow と Bash entrypoint を追加
- `github-quality-gate-setup`、`skills-eval-pipeline`、関連 viewer / optimizer を追加
- `skills/skill/` を追加し、sub_skills / `_foundation` / `_eval` / `scripts` を含む統合メタスキル構造を導入
- 汎用 `skills/debug/` を追加し、コンパクトなコア workflow と実戦で育てる薄いドメイン modules 構成を導入
- `skills/dotnet/` を追加し、広い `.NET` / `C#` / `WPF` 相談を既存 dotnet skill へ振り分ける薄い入口 skill を導入
- `skills/github/` を追加し、PR / review / issue 系の広い GitHub 依頼を既存 workflow skill へ案内する薄い入口 skill を導入

### Changed

- skill `evidence-response` を `business/evidence-response` へ移動し、業務向けワークフローとして整理
- `business/pdf` を復旧し、`business/` カテゴリを `.copilot` 同期対象へ追加
- frontmatter 最小構成方針に合わせて、validation / instructions / skills 周辺の規約を整理
- `README.md` を入口中心に簡素化し、詳細手順を `docs/INSTALL.md` へ分離
- repo 固有の documentation maintenance ルールを `.github/copilot-instructions.md` に追加
- `skills-author-skill` などの旧メタスキル群を `skill` へ集約し、validator / generator / eval assets も新配置へ移行
- `skills/debug/` に module 選択用の短い decision table を追加し、hardware / nondeterminism の境界と intermittent 現象の扱いを強化
- `skills/skill/` の generator と foundation templates を拡張し、Router スキルと `sub_skills/` の scaffolding を作成可能にした
- `git-commit-practices` と `skills/SKILLS_README.md` を更新し、「コミットして」は atomic commit を前提に `git-commit-practices` へ流す標準導線を明文化
- `skills/skill/_eval/scripts/` に real corpus 抽出用 `extract_prompt_corpus.py` と semi-automated run materialization 用 `materialize_manual_run.py` を追加し、`github` cluster の benchmark/viewer 生成まで通せるようにした
- `git-commit-practices` を更新し、atomic commit は「変更意図単位」で分割し、session / wave 単位では束ねない方針を明文化した

### Docs

- README の同期手順、WSL 運用、ランタイム選定、レビュー待機ルールなどの説明を継続改善
- ADR-002 と品質ゲート運用の背景を整理
- `skills/SKILLS_README.md` と git / github 系 skill の Related Skills を更新し、router 化せずに topology と入口導線が追えるよう整理
- `evals/github/evals.json` を追加し、`github` 薄い入口 skill の flat vs thin-entry 比較に使う日常運用フレーズ評価ケースを整備
- `evals/github/corpus_summary.json`、`inventory_matrix.json`、`benchmark_summary.json`、`feedback.json` を追加し、`events.jsonl` の実 prompt corpus に基づく比較評価を残した
- `evals/skill/evals.json`、`inventory_matrix.json`、`manual_run_20260317_002.json`、`benchmark_summary.json`、`feedback.json` を real-corpus-first に更新し、`skill` meta router が naming/taxonomy 相談で over-trigger して baseline 比で degraded することを可視化した
- `evals/dotnet/evals.json`、`inventory_matrix.json`、`manual_run_20260317_003.json`、`benchmark_summary.json`、`feedback.json` を追加し、`dotnet` 薄い入口 skill が local corpus では neutral だが Oracle integration routing で revise 余地があることを可視化した

### Fixed

- リンクチェック、PR review 対応、allowlist / config 周辺の継続修正を実施
- `skills/skill/sub_skills/` の frontmatter を YAML として有効化し、sub-skill ごとの `references/SKILL.ja.md` を追加

## 2026-02

### Added

- 初回の Copilot 指示ファイルと [`PHILOSOPHY.md`](PHILOSOPHY.md) を追加
- `git-initial-setup`、git practices 系 skills、`production` カテゴリを追加
- .NET / WPF / Oracle / OCR 関連の skill 群を拡充
- `dotnet-skill-deploy`、`knowledge-capture` などの実務支援 skills を追加

### Changed

- 配布ハブ構造を見直し、`.github/` から `agents/` と `copilot/` を分離
- skills アーキテクチャを整理し、「1 Skill = 1 Workflow」への移行を進めた

### Docs

- README に Quickstart、Windows / WSL / Codex 手順、ローカル参照ディレクトリ運用を追加
- Windows セットアップやレビュー指摘反映を進め、運用ドキュメントを整備
