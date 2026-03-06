---
name: session-issue-autopilot
description: 挨拶とIssue対応開始の意図を起点に、実装・PR・レビュー対応・協働ふりかえりまでを一気通貫で進める単一ワークフロー。Use when セッション冒頭でIssue集中モードに入りたいとき。
metadata:
  author: RyoMurakami1983
  tags: [session, issue, workflow, github, pr, retrospective, kpt, ywt, autopilot]
  invocable: false
---

# Session Issue Autopilot

挨拶トリガーから始まる Issue 対応セッションを、実装・PR・レビュー応答・協働ふりかえりまで接続する単一ワークフロー。

## このスキルを使うとき

以下のような場面で使います：
- ユーザーの挨拶に「Issue対応を始める」意図が含まれ、すぐに実行へ入りたいとき。
- Issue選定から実装、PR作成、レビュー対応、ふりかえりまでを1本の流れで進めたいとき。
- 複利効果が高く、かつ1日で完了可能なIssueを1つだけ選んで進めたいとき。
- エージェント選択や協働ふりかえり参加など、人の確認ポイントを必ず残したいとき。

## コア原則

1. **意図確認を先に行う** — 挨拶トリガーを正しく検知してから実装に入る (基礎と型)
2. **1日で終える高複利課題** — 将来の速度・品質・学習に効くIssueを1つ選ぶ (成長の複利)
3. **人間参加のチェックポイント** — エージェント選択とふりかえり参加は必ず明示確認する (ニュートラル)
4. **会話を成果物へ接続する** — 判断をIssue/PR/記録に残し、次回へ継承する (継続は力)
5. **自動化の境界を守る** — 作業は自動化しても、協働内省と同意は参加確認を必須化する (余白の設計)
6. **マージ判断は人間が行う** — GitHub上のマージは人間に残し、確認後の同期だけを自動化候補にする (基礎と型)

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

### Step 4: 必須エージェント選択チェックポイント

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

### Step 5: 実装と検証

選定Issueを専用ブランチで実装し、対象範囲のテスト/リンター/検証を実施する。

```bash
git checkout -b feature/issue-<id>-short-title
# 実装
# 変更範囲に応じたテスト・lint・検証を実行
```

検証結果は「何が通ったか / 失敗したか / 次の修正」をテキストで要約する。

実装が承認されたら使う。Why: 検証なし実装はレビュー往復を増やす。

> **Values**: 基礎と型 / 継続は力

### Step 6: PR作成（body-file安全運用）

文脈・検証結果・Issue連携を含むPRを作成する。

**`gh` の本文は body-file を使う**。シェル引用やバッククォート崩れを回避する。

```bash
cat > /tmp/pr_body.md <<'MD'
## Summary
- #<issue-id> を実装

## Validation
- [x] tests
- [x] lint

## Link
- Closes #<issue-id>
MD

gh pr create --title "feat: resolve #<issue-id> <short-title>" --body-file /tmp/pr_body.md
```

検証が通った後に使う。Why: body-fileなら複雑なMarkdownでも安全に投稿できる。

> **Values**: 基礎と型 / 温故知新

### Step 7: レビューコメント監視と返信

PRレビュー指摘を追跡し、修正コミットまたは根拠付き説明で返信する。

**長文コメントも body-file を使う**。

```bash
cat > /tmp/review_reply.md <<'MD'
レビューありがとうございます。
commit <sha> で対応しました:
- nullハンドリングの修正
- 回帰テスト追加
MD

gh pr comment <pr-number> --body-file /tmp/review_reply.md
```

レビュー開始後に使う。Why: 構造化返信は往復時間を短縮し、文脈欠落を防ぐ。

> **Values**: 継続は力 / ニュートラル

### Step 8: 人間のマージ判断ゲートと安全なマージ後同期

レビュー対応が完了したら、マージ判断ゲートで止まります。GitHub上でマージするかどうかは人間が決めます。

マージ確認後に限り、かつ worktree が clean な場合だけローカル同期を補助します。

```bash
# 先にマージ済みであることとローカル同期の安全性を確認
git status --short
git switch main
git pull --ff-only
```

安全ルール:
- GitHub上のマージを自分で実行しない
- `git status --short` が clean でなければ止まってユーザーへ確認する
- `git pull --ff-only` が失敗したら止まり、差分分岐を明示する

レビュー対応後、次のアクションがマージ判断またはマージ後後処理になるときに使います。

> **Values**: 基礎と型 / 余白の設計

### Step 9: 必須 協働ふりかえりチェックポイント

マージ後（またはレビュー一区切り後）、ユーザー参加のふりかえり実施可否を確認する。

```markdown
必須チェックポイント:
いま協働ふりかえりを実施しますか？ (yes/no)
参加確認が取れるまで待機します。
```

**ユーザー参加を確認してから実行する。** yes が出るまで待つ。

実行ループ完了時に使う。Why: 参加者不在の内省は浅くなり、実行へつながりにくい。

> **Values**: 余白の設計 / 成長の複利

### Step 10: KPT/YWT実施とアクション記録（Issue/Notion）

Step 9 で参加同意が得られたら、KPTまたはYWTを実施し、次アクションを記録する。

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
- `gh` の本文は原則 `--body-file` を使う。
- GitHub上のマージは人間に残し、マージ確認後にだけローカル同期へ進む。
- ふりかえり結果は追跡可能な成果物（Issue/Notion）へ接続する。

## Common Pitfalls

1. モード確認前に実装へ入る。
   - Fix: 必ず Step 1 の確認を先に実施。
2. 1日で終わらないIssueを選ぶ。
   - Fix: 実現可能性ゲートでスコープ分割。
3. エージェント選択チェックポイントを飛ばす。
   - Fix: Step 5前にユーザー回答を必須化。
4. `gh`本文をインラインで書いてMarkdown/バッククォートを壊す。
   - Fix: 一時Markdownファイル + `--body-file` を使用。
5. 人間確認なしでマージや同期を進める。
   - Fix: マージ判断ゲートで止まり、マージ確認と clean tree を確認してから同期する。
6. ユーザー不在でふりかえりを自動実行する。
   - Fix: Step 9 の yes/no 応答待ちでブロック。

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
| PR | `--body-file` でPR作成 | "本文に根拠とIssueリンクがありますか？" |
| レビューループ | 返信コメントと修正コミット | "レビュー指摘は全件対応しましたか？" |
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
