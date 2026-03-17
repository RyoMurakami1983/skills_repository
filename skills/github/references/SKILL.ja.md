---
name: github
description: >
  GitHub 系の広い依頼を既存の具体 workflow skill へ案内する薄い入口 skill。
  Use when ユーザーが「GitHub」「プルリクして」「PRレビュー待機して」
  「レビュー対応して」「Issue登録して」のように言うが、まだ具体 skill 名を指定していないとき。
---

# GitHub 入口 skill

GitHub 上の delivery や issue 運用が必要なのは明らかだが、まだどの具体 skill に入るべきか曖昧なときに最初に使う薄い入口です。

この skill は `github-pr-workflow` や `github-pr-review-response` を置き換えません。役割は最初の振り分けだけで、意図が見えたらすぐに canonical workflow へ委譲します。

## When to Use This Skill

Use this skill when:
- 広い GitHub 依頼を最初に分類したいとき
- 「プルリクして」を canonical な PR 作成 + レビュー待機フローへつなぎたいとき
- 「PRレビュー待機して」「レビュー対応して」を review phase の適切な skill へ振り分けたいとき
- 「Issue登録して」や backlog 化したい依頼を issue intake へ案内したいとき
- greeting 起点で issue を end-to-end に進める session workflow へつなぎたいとき
- 「コミットして」を PR 前の atomic commit 要求として `git-commit-practices` に流したいとき

## Decision Table

| 意図 | ルート | 何をするか |
| --- | --- | --- |
| PR を作る、Issue を紐づける、レビュー待機へ入る | `github-pr-workflow` | branch/state 判定から PR 作成、review waiting まで canonical workflow を使う。 |
| 新しい PR review comment に対応する、再レビュー依頼する | `github-pr-review-response` | 実際の review signal があるときだけ入る。 |
| スコープ外作業や後続対応を Issue 化する | `github-issue-intake` | scope expansion や vague work を構造化された GitHub Issue にする。 |
| 1つの Issue を今の session で end-to-end に進める | `session-issue-autopilot` | Issue 実行から PR flow まで guided に進める。 |
| labels や quality gate を repo レベルで整える | `github-repo-label-setup`、`github-quality-gate-setup` | PR concern ではなく repo bootstrap / hardening concern として扱う。 |
| PR 前に commit を整える | `git-commit-practices` | 「コミットして」は原則として atomic commit 要求として解釈する。 |

## Related Skills

- **`github-pr-workflow`** — PR 作成、Issue 連携、レビュー待機の第一候補
- **`github-pr-review-response`** — review feedback 対応の第一候補
- **`github-issue-intake`** — Issue 起票・defer/triage の第一候補
- **`session-issue-autopilot`** — Issue 実行の session wrapper
- **`git-commit-practices`** — PR 前に履歴を reviewable に整えるための上流 route

## Routing Notes

- 意図が明確になったら直接 concrete skill を呼ぶ。入口 skill に留まり続けない。
- 「コミットして」は generic な GitHub 作業ではなく、atomic commit を前提とした `git-commit-practices` ルートとして扱う。
- merge 判断は人間が持つ。routing skill が merge ownership を曖昧にしない。

## Pitfalls

- **router に留まりすぎる**: 具体意図が見えたら category 説明を続けず、すぐ concrete skill に渡す。
- **`github` を巨大 workflow にしてしまう**: これは入口であり、`github-pr-workflow` や `github-pr-review-response` の代替ではない。
- **commit hygiene を飛ばす**: review に耐える履歴でなければ、まず `git-commit-practices` で atomic commit に分割してから PR に進む。
