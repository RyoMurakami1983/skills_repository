---
name: session-issue-autopilot
description: 挨拶とIssue対応開始の意図を起点に、実装・PR・レビュー対応・協働ふりかえりまでを一気通貫で進める単一ワークフロー。Use when セッション冒頭でIssue集中モードに入りたいとき。
metadata:
  author: RyoMurakami1983
  tags: [session, issue, workflow, github, pr, retrospective, kpt, ywt, autopilot]
  invocable: false
---

# Session Issue Autopilot

挨拶トリガーから始まる Issue 対応セッションを、実装・標準PR委譲・シグナル駆動のレビュー応答・協働ふりかえりまで接続する単一ワークフロー。

Option A では、このスキルは挨拶起点のセッションラッパーです。PR作成とレビュー待機は `github-pr-workflow`、レビュー対応は `github-pr-review-response` へ委譲し、競合する別系統のPR標準を定義しません。

## このスキルを使うとき

以下のような場面で使います：
- 挨拶トリガー付きで、すぐに Issue 集中実行モードへ入りたいとき。
- Issue選定から実装、PR委譲、レビュー待機、レビュー対応、ふりかえりまでを1本の流れで進めたいとき。
- 複利効果が高く、かつ1日で完了可能なIssueを1つだけ選んで進めたいとき。
- エージェント選択、マージ引き継ぎ、協働ふりかえり参加など、人の確認ポイントを必ず残したいとき。
- Option A の標準PRスキルへ委譲し、別系統のPR運用を増やしたくないとき。

> **スコープ**: このスキルはセッション全体を束ねるオーケストレーターです。Issue選定と実装を進めた後、PR作成/待機は `github-pr-workflow`、レビュー対応は `github-pr-review-response` に委譲し、人間のマージゲートを守ったうえで協働ふりかえりへ接続します。

## Related Skills

- **`github-pr-workflow`** — 標準のPR作成・Issue連携・シグナル駆動レビュー待機
- **`github-pr-review-response`** — 標準のレビューコメント分類・修正・返信・再レビュー依頼
- **`furikaeri-practice`** — さらに深いふりかえりが必要なときの補助

## コア原則

1. **意図確認を先に行う** — 挨拶トリガーを正しく検知してから実装に入る (基礎と型)
2. **1日で終える高複利課題** — 将来の速度・品質・学習に効くIssueを1つ選ぶ (成長の複利)
3. **標準配送スキルへ委譲する** — PRの機械的処理は `github-pr-workflow` と `github-pr-review-response` に集約し、別標準を増やさない (温故知新)
4. **人間参加のチェックポイント** — エージェント選択、マージ引き継ぎ、ふりかえり参加は必ず明示確認する (ニュートラル)
5. **会話を成果物へ接続する** — 判断をIssue/PR/記録に残し、次回へ継承する (継続は力)

## Workflow: Session Issue Autopilot を実行する

### Step 1: トリガー検知とIssue集中モード確認

挨拶 + Issue対応開始の複合意図を検知する。

トリガー例:
- "Good morning, let's solve Issues"
- 「おはよう。Issueを解決しましょう」
- 「挨拶してIssue対応開始」

作業開始前に、モード移行を明示確認する。

```markdown
トリガー検知: 挨拶 + Issue対応開始意図。
**Issue-Focused Session Mode** に切り替えます。
進めますか？ (yes/no)
```

セッション開始時に使う。Why: モード誤認のまま進むと分岐が増え、手戻りが増える。

> **Values**: 基礎と型 / ニュートラル

### Step 2: Issue棚卸しと解決済み候補の検出

Open Issueを一覧化し、マージ済みPR・コミット・実装済み挙動から「実質解決済み候補」を判定する。

```bash
git --no-pager log --oneline -20
# 任意: gh issue list --state open --limit 30
```

棚卸しテーブルを作る:

| Issue | 状態 | 根拠 | アクション |
|---|---|---|---|
| #101 | Open | PR #220 merge済み、受け入れ条件をテストで確認 | 解決済み候補 |
| #108 | Open | 関連PRなし | 継続対応 |

Open Issueが複数あるときに使う。Why: 先に棚卸しすると重複作業と古い課題の放置を防げる。

> **Values**: 温故知新 / ニュートラル

### Step 3: 1日スコープで高複利Issueを1つ選ぶ

継続対応Issueから、複利効果が高く1日で終えられるものを1つだけ選ぶ。

```markdown
選定ルーブリック（各1-5点）:
- 複利レバレッジ（将来の速度/品質への効き）
- ユーザー価値
- 1日完了の実現可能性
- 依存リスク（逆スコア）
```

判断ルール: 最高得点かつ当日完了可能な1件を採用。残りはバックログコメントへ送る。

優先順位を確定するときに使う。Why: 高レバレッジ課題を1件完了する方が中途半端な並行作業より効果が高い。

> **Values**: 成長の複利 / 継続は力

### Step 4: 着手前の現行規約差分チェック（必須）

実装に入る前に、Issue本文の前提が古くないかを **現行** の frontmatter/validator 規約で短時間チェックします。

```bash
# 着手前プリフライト: 今日の規約を一次ソースで確認
CHECK_LOG="preflight-issue-<id>.log"
{
  echo "[preflight] validator/frontmatter convention check"
  rg -n "required|name|description|Use when|metadata" skills/skill-quality-validation/scripts/validate_skill.py
  rg -n "frontmatter|name, description" copilot/copilot-instructions.md
} | tee "$CHECK_LOG"
```

実行後は、作業ログまたはIssueコメントに痕跡を1行残します（例: `preflight done: preflight-issue-162.log`）。

Issue選定から実装へ移る直前に使う。Why: 旧前提のまま着手して後からリスコープする手戻りを防ぐ。

> **Values**: 基礎と型 / 温故知新

### Step 5: 必須エージェント選択チェックポイント

実装前に、どの専門エージェントを使うかをユーザーへ確認する。`skill-shihan` を明示選択肢に含める。

```markdown
必須チェックポイント — 実行エージェントを選択してください:
1) skill-shihan（スキル/ワークフロー品質）
2) dotnet-shihan
3) python-shihan
4) typescript-shihan
5) 専門エージェントなしで進行

どれにしますか？選択を待機します。
```

ユーザー回答があるまで先に進まない。

計画から実装へ移る直前に使う。Why: 役割を明示すると責務と品質期待が揃う。

> **Values**: ニュートラル / 基礎と型

### Step 6: 実装と検証

選定Issueを専用ブランチで実装し、対象範囲のテスト/リンター/検証を実施する。

```bash
git checkout -b feature/issue-<id>-short-title
# 実装
# 変更範囲に応じたテスト・lint・検証を実行
```

検証結果は「何が通ったか / 失敗したか / 次の修正」をテキストで要約する。

実装が承認されたら使う。Why: 検証なし実装はレビュー往復を増やす。

> **Values**: 基礎と型 / 継続は力

### Step 7: `github-pr-workflow` へ PR作成とレビュー待機を委譲する

実装と検証が終わったら、ここで別のPR手順を再定義せず `github-pr-workflow` へ渡します。

```markdown
標準ハンドオフ:
implementation complete
-> github-pr-workflow
-> PR作成 + Issue連携
-> PR URL を1回記録
-> シグナル駆動のレビュー待機へ入る
```

検証が通った後に使う。Why: Option A では PR作成 + 待機の標準を1本に集約し、このセッションラッパーと競合させないため。

> **Values**: 基礎と型 / 温故知新

### Step 8: 明示的なレビュー待機タスクを維持し、短時間観測後にシグナルで委譲する

PR作成直後は、レビュー待機が暗黙状態に埋もれないよう、`pr-<number>-review-wait` のような明示的な待機アーティファクトを active のまま維持します。

PR作成直後に限り、1回だけ境界付きの短時間観測ウィンドウを自動実行します:
- 実レビューシグナルの確認は最大でも1分ごとに1回
- シグナルが来なくても最大7分で終了
- これは作成直後の短時間観測であり、無期限ポーリングではない
- 追加チェックはユーザーからの明示指示がある場合に限る

その観測中に新しいレビュー、review request、またはユーザーからの明示シグナルが来たら `github-pr-review-response` へ委譲します。

7分経ってもシグナルが来なければ:
- 自動ポーリングを停止する
- `review-wait continues` と報告する
- `pr-<number>-review-wait`（または同等の明示待機アーティファクト）を active のまま残す
- ユーザーからの次の明示指示が来るまで待機する
- ワークフロー全体を完了扱いにしない

```markdown
レビュー待機ハンドオフ:
PR作成
-> `pr-<number>-review-wait` を作成/維持
-> 最大7分観測（最大1回/分）
-> シグナル到着時: github-pr-review-response
-> シグナルなし: "review-wait continues" と報告
-> ポーリング停止 + ユーザー指示待ち
```

PR作成直後で、レビューがすぐ始まる可能性があるときに使います。Why: 標準PRレビュー系スキルの低消費待機ルールを守りつつ、作成直後の近接レビューだけを短時間で取りこぼさないため。

> **Values**: 継続は力 / ニュートラル

### Step 9: 人間のマージ判断ゲートと安全なマージ後同期

`github-pr-review-response` が完了したら、マージ判断ゲートで止まります。GitHub上でマージするかどうかは人間が決めます。

マージ確認後に限り、かつ worktree が clean な場合だけローカル同期を補助します。

```bash
# PRがマージ済みか確認し、その後ローカル同期の安全性を確認
gh pr view <pr-number> --json state,mergedAt --jq '{state: .state, mergedAt: .mergedAt}'
git status --short
git switch main
git pull --ff-only
```

安全ルール:
- GitHub上のマージを自分で実行しない
- `git status --short` が clean でなければ止まってユーザーへ確認する
- `git pull --ff-only` が失敗したら止まり、差分分岐を明示する

レビュー対応後、次のアクションが人間へのマージ引き継ぎまたはマージ後後処理になるときに使います。

> **Values**: 基礎と型 / 余白の設計

### Step 10: 必須 協働ふりかえりチェックポイント

マージ後（またはレビュー一区切り後）、ユーザー参加のふりかえり実施可否を確認する。

```markdown
必須チェックポイント:
いま協働ふりかえりを実施しますか？ (yes/no)
参加確認が取れるまで待機します。
```

**ユーザー参加を確認してから実行する。** yes が出るまで待つ。

実行ループ完了時に使う。Why: 参加者不在の内省は浅くなり、実行へつながりにくい。

> **Values**: 余白の設計 / 成長の複利

### Step 11: KPT/YWT実施とアクション記録（Issue/Notion）

Step 10 で参加同意が得られたら、KPTまたはYWTを実施し、次アクションを記録する。

```markdown
形式選択: KPT or YWT
- KPT: Keep / Problem / Try
- YWT: Yatta / Wakatta / Tsugi

記録先:
- GitHub Issue: 実行可能な開発/プロセス改善
- Notion（利用可能時）: セッション記録と学習履歴
```

最低限、実行可能アクションはIssue化し、ふりかえりノートと相互リンクする。

協働ふりかえり承認後に使う。Why: 記録されたアクションが内省を複利成長へ変える。

> **Values**: 成長の複利 / 継続は力 / 温故知新

## Best Practices

- ✅ 挨拶意図を推測で済ませず、Issue集中モード確認を必ず行う。
- 優先順位決定前にIssue棚卸し表を可視化する。
- 1日完了条件を厳守し、大きいIssueは分割する。
- エージェント選択チェックポイントを必須かつブロッキングにする。
- `gh` の本文は原則 `--body-file` を使い、`docs/patterns/environment-portability.md` のテンプレート2を再利用する。
- PR作成後は `pr-<number>-review-wait`（または同等物）を明示的な active task として維持し、レビュー待機を追跡可能にする。
- GitHub上のマージは人間に残し、マージ確認後にだけローカル同期へ進む。
- ふりかえり結果は追跡可能な成果物（Issue/Notion）へ接続する。

## Common Pitfalls

1. モード確認前に実装へ入る。
   - Fix: 必ず Step 1 の確認を先に実施。
2. 1日で終わらないIssueを選ぶ。
   - Fix: 実現可能性ゲートでスコープ分割。
3. エージェント選択チェックポイントを飛ばす。
   - Fix: Step 6前にユーザー回答を必須化。
4. `gh`本文をインラインで書いてMarkdown/バッククォートを壊す。
   - Fix: 一時Markdownファイル + `--body-file` を使用。
5. PR作成後にレビュー待機が消える、または無期限にポーリングし続ける。
   - Fix: 明示レビュー待機タスクを維持し、7分の境界付き観測だけ行ったら `review-wait continues` を報告して停止する。
6. 人間確認なしでマージや同期を進める。
   - Fix: マージ判断ゲートで止まり、マージ確認と clean tree を確認してから同期する。
7. ユーザー不在でふりかえりを自動実行する。
   - Fix: Step 10 の yes/no 応答待ちでブロック。

## Anti-Patterns

- ❌ 役割選択やふりかえり参加確認を省いた全自動運転。
- GitHub上のマージ判断まで自動化し、人間の最終意思決定を飛ばす運用。
- 明示的な再優先なしにIssue対象を途中で頻繁に切り替える運用。
- 検証根拠が薄いままPR先行で進める進行。
- ふりかえりを装飾扱いし、複利成長ループ設計を欠く運用。

## Quick Reference

| フェーズ | 必須アウトプット | ゲート質問 |
|---|---|---|
| トリガー | Issue集中モード確認 | "Issue-Focused Session Modeで進めますか？" |
| 棚卸し | Open + 解決済み候補テーブル | "古いIssueを更新/クローズしますか？" |
| 優先付け | 1日完了・高複利Issue 1件 | "今日中に完了できますか？" |
| Agent Checkpoint | ユーザー選択エージェント（skill-shihan含む） | "どの専門家を使いますか？" |
| 実装・検証 | ブランチ + 検証結果 | "検証はグリーンですか？" |
| PR | `github-pr-workflow` への委譲 | "`github-pr-workflow` がPR作成とレビュー待機へ入れましたか？" |
| レビューループ | active な `pr-<number>-review-wait` + 境界付き7分観測、その後シグナルで委譲 | "短時間観測内で実レビューシグナルが来たか、来なければ `review-wait continues` を報告してポーリング停止しましたか？" |
| Merge Gate | 人間のマージ判断 + 安全なローカル同期 | "人間がこのPRをマージ済みですか？" |
| Retro Checkpoint | ユーザー yes/no 明示 | "協働ふりかえりを今実施しますか？" |
| KPT/YWT記録 | Issue/Notion へのアクション記録 | "アクションをリンク付きで保存しましたか？" |

### Minimal Command Pattern

```bash
# GH本文の安全投稿
cat > /tmp/body.md <<'MD'
<backticks や箇条書きを含む markdown>
MD

gh issue comment <issue-number> --body-file /tmp/body.md
gh pr comment <pr-number> --body-file /tmp/body.md
```
