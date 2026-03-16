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

### Changed

- skill `evidence-response` を `business/evidence-response` へ移動し、業務向けワークフローとして整理
- `business/pdf` を復旧し、`business/` カテゴリを `.copilot` 同期対象へ追加
- frontmatter 最小構成方針に合わせて、validation / instructions / skills 周辺の規約を整理
- `README.md` を入口中心に簡素化し、詳細手順を `docs/INSTALL.md` へ分離
- repo 固有の documentation maintenance ルールを `.github/copilot-instructions.md` に追加
- `skills-author-skill` などの旧メタスキル群を `skill` へ集約し、validator / generator / eval assets も新配置へ移行

### Docs

- README の同期手順、WSL 運用、ランタイム選定、レビュー待機ルールなどの説明を継続改善
- ADR-002 と品質ゲート運用の背景を整理

### Fixed

- リンクチェック、PR review 対応、allowlist / config 周辺の継続修正を実施

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
