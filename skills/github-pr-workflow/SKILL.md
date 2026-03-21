---
name: github-pr-workflow
description: >
  実装の検証後に、ブランチ確認から PR 作成、レビュー待機、人間へのマージ引き継ぎまでを標準フローで進める。Use when: feature branch の変更がレビュー準備完了になり、PR lifecycle に入りたいとき。
---
# GitHub PR Workflow

状態検知からPR作成・Issue連携・レビュー待機・人間へのマージ引き継ぎまでを扱うワークフロー。

標準ルート: implementation -> `github-pr-workflow` -> 実際のレビューシグナル待ち -> `github-pr-review-response` -> 人間のマージ判断/引き継ぎ。

**Pull Request (PR)**: GitHub上でレビューする変更提案。

先に状態を検知してください。PRは必ず feature branch から作成してください。複数行本文は `--body-file` を使ってください。

## こんなときに使う
以下の状況で活用してください：
- feature branch の作業がレビュー準備完了になり、PRを作成するとき
- 未コミット・未push の変更をPR作成前にルーティングするとき
- `Closes #N` や `Refs #N` で Issue 連携しながらPRを作成するとき
- `gh pr create` 前にブランチ状態と認証状態を確認するとき
- マージ判断を自動化せず、レビュー待ちへ安全に引き渡すとき

> **スコープ**: このスキルは状態検知からPR作成・Issue連携・低消費なレビュー待機への受け渡し、および残PRブランチ向けの確認済みマージ後同期までを扱います。詳細なレビュー対応とマージ判断そのものはスコープ外です。

## 関連スキル

- **`github-pr-review-response`** - 実際のレビューシグナル到着後のコメント分類・修正・返信・再レビュー依頼
- **`git-commit-practices`** - コミット形式と原子的コミット（Step 1から委譲）
- **`git-initial-setup`** - ブランチ保護の初期設定
- **`github-issue-intake`** - Issue作成とトリアージ

---

## 依存関係

- Git 2.30+
- GitHub CLI (`gh`) — `gh auth status` で事前確認
- GitHubリポジトリへのpush権限

---

## コア原則

1. **ブランチ優先で main を清潔に保つ** (基礎と型) - 作業はレビュー完了まで main に載せず、検証済み変更だけを main に到達させる
2. **追跡性** (成長の複利) - PRとIssueを紐付け、将来の開発者が変更理由を学べるように
3. **日本語PR本文** (ニュートラル) - チーム標準としてPR本文を日本語で記述
4. **状態駆動** (温故知新) - 現在の状態を検知し、適切なアクションにルーティング
5. **イベント駆動で待つ** (余白の設計) - 同じPRを何度も見に行かず、レビューのシグナルを待つ

---

## 判断テーブル

次の一手をひと目で決めるためのテーブルです。

| 現在の状態 | 次のアクション | 理由 |
|---|---|---|
| `main` にいる | 先に feature branch を作る | default branch にレビュー前の作業を置かないため |
| 未コミット変更あり | PR前にコミットする | 追跡可能な状態を保つため |
| ローカルコミットのみ | 先に push する | `gh pr create` にはリモートブランチが必要なため |
| PR未作成 | PRを作成する | レビューフローとIssue連携を開くため |
| PR既存 | 状態を報告して止まる | 重複PRを防ぐため |

---

## 責務境界

自動化がやり過ぎないよう、マージ境界を明示します。

| フェーズ | エージェントの責務 | 人間の責務 |
|---|---|---|
| PR前 | 状態検知、ブランチ作成、検証済み変更の準備 | 提案可能な状態か判断する |
| PR作成 | PR作成、Issue連携、検証根拠の要約 | 誰にレビューを依頼するか、いつ出すか決める |
| レビュー待機 | PR URL を1回記録し、ポーリングを止めて実際のレビューシグナルを待つ | シグナル前に優先順位を変えるか判断する |
| レビュー対応 | レビューシグナル到着時に `github-pr-review-response` へ委譲する | 返信内容を確認し、承認で十分か判断する |
| マージ判断 | 準備完了状況を要約するだけ | GitHub上でマージするか、いつするか決める |
| マージ後 | マージ確認後にローカル同期を補助する | 実際にマージされたことを確認する |
| 並行PRの後処理 | `origin/main` を残PRブランチへ取り込み、再検証・再レビュー要否を要約する | マージ順序の判断やプロダクト優先度の見直しを行う |

このスキルが自動化する範囲・しない範囲を説明するときに使います。

> **Values**: ニュートラル / 余白の設計
## ワークフロー: プルリクエストで出荷する

### Step 1: 状態を検知してルーティングする

現在のgit状態を確認し、適切なアクションを取ります。

```bash
# 1. 現在のブランチを確認
BRANCH=$(git branch --show-current)

# 2. 未コミットの変更を確認
git status --short

# 3. 未pushのコミットを確認
git log "origin/${BRANCH}..HEAD" --oneline 2>/dev/null

# 4. 既存PRの確認
gh pr list --head "$BRANCH" --state open
```

```powershell
# PowerShell版
$Branch = git branch --show-current

git status --short

git log "origin/$Branch..HEAD" --oneline 2>$null

gh pr list --head $Branch --state open
```

| 状態 | アクション |
|------|-----------|
| mainブランチにいる | feature branch を作成（Step 2） |
| 未コミットの変更あり | `git-commit-practices` に委譲してコミット後、戻る |
| コミット済・未push | `git push -u origin BRANCH` してから Step 3 へ |
| push済・PR未作成 | Step 3（PR作成）へ進む |
| PR既存 | PRステータスとURLを報告 |

> **重要**: 未コミットの変更がある場合は `git-commit-practices` ワークフローに委譲してください（先にコミット、その後戻る）。mainにいる場合は、コミット前に必ず feature branch を作成してください。

「プルリクして」「PR作成して」等のPR関連リクエスト時に使用します。Why: 状態検知を先に行うと、誤った分岐や重複PR作成を防げます。

> **Values**: 基礎と型 / 継続は力

### Step 2: フィーチャーブランチの作成

最新のmainからブランチを作成します。追跡性のためにIssue番号付きの説明的プレフィックス（`feature/`、`fix/`、`docs/`）を使用します。

```bash
# ブランチ作成前に認証確認（push失敗を防ぐ）
gh auth status
git switch main
git pull --ff-only
git switch -c feature/issue-123
git push -u origin feature/issue-123
```

新しい作業を開始するとき、または Step 1 で main にいることが検知された場合に使用します。Why: 先にブランチを切ると、その後のコミット履歴がきれいに保てます。

> **Values**: 基礎と型

### Step 3: PR作成とIssue連携

日本語の本文でPRを作成します。`Closes` でマージ時にIssueを自動クローズします。

**インライン本文**（1行本文のみ）:

```bash
gh pr create \
  --title "feat: 支払い画面にフィルタを追加" \
  --body "注文履歴画面に検索フィルタを追加。Closes #123. Refs #130."
```

**ファイル経由の本文**（複数行Markdown・コードフェンス・バッククォートを含む本文の標準既定）:

```bash
# 一意な一時ファイルを作り、クォート付きHEREDOCで書き出す
# なぜ: mktemp で衝突を避け、trap で失敗時も確実に削除できる
BODY_FILE="$(mktemp "${TMPDIR:-/tmp}/pr_body.XXXXXX")" || {
  echo "PR本文用の一時ファイル作成に失敗しました" >&2
  exit 1
}
cleanup() {
  [ -n "$BODY_FILE" ] && rm -f "$BODY_FILE"
}
trap cleanup EXIT
cat > "$BODY_FILE" <<'EOF'
## 概要
注文履歴画面に検索フィルタを追加し、本文内の `int(order_id)` 例もそのまま残す。

## 理由
サポートから検索要求が多く、対応工数を削減するため。

## テスト
ローカルで動作確認済み。

## 関連
Closes #123
Refs #130
EOF

gh pr create --title "feat: 支払い画面にフィルタを追加" --body-file "$BODY_FILE"
```

複数段落の本文、シェル例、バッククォートを含むMarkdownでは、このパターンを既定にしてください。PowerShell/Bash両対応の再利用テンプレは `docs/patterns/environment-portability.md`（テンプレート2）を参照します。

✅ **良い例**: 本文ファイルを生成して確認してから `gh pr create --body-file` を実行する。
❌ **悪い例**: バッククォート入りの複数行Markdownを `--body` に直接貼り付けてクォート崩れに賭ける。
Why: ファイル経由の方が再現性・レビュー性・シェル安全性が高いからです。

| キーワード | 効果 |
|-----------|------|
| `Closes #N` | マージ時にIssue #N を自動クローズ |
| `Refs #N` | Issue #N へのリンク（クローズしない） |

ブランチがpush済みでPRが未作成の場合に使用します。

> **Values**: 成長の複利 / ニュートラル

✅ **良い例**: PRを1回作成し、URLを記録して待機モードへ受け渡す。
❌ **悪い例**: 状態変化がないのにPR作成や確認コマンドを何度も繰り返す。
Why: きれいな受け渡しの方が追跡性を保ち、重複作業を防げるからです。

### Step 4: 低コストでレビュー待機モードに入る

PRを開いたら、能動的なポーリングを止めます。具体的なシグナルが来たときだけ `github-pr-review-response` へ、シグナルごとに1回だけ受け渡します。

```bash
# PR URL を1回だけ記録し、その後はループ確認を止める
gh pr view --json url,updatedAt --jq '{url: .url, updatedAt: .updatedAt}'

# 自然な作業区切りでのみ、まとめて1回確認
gh pr status
```

| シグナル | 待機継続？ | 次のアクション | 避けること |
|---|---|---|---|
| 新しいレビューが送信された | いいえ | `github-pr-review-response` を開き、コメントを1回確認 | シグナル前の再確認 |
| 自分に review request が来た | いいえ | `github-pr-review-response` を開き、コメントを1回確認 | シグナル前の再確認 |
| ユーザーが新規レビュー活動を共有した | いいえ | 1回だけ確認してから `github-pr-review-response` へ委譲 | シグナル前の再確認 |
| PRは開いているが変化なし | はい | 待機を継続 | 「念のためもう1回」の確認 |
| CI ステータスだけ変わった | 通常ははい | レビュー作業が止まる可能性がある場合だけ1回確認 | CIノイズをレビュー入力扱いすること |
| PRがクローズ/マージ済み | 終了 | 待機を終えて次の確定状態へ進む | レビュー確認を続ける |

待機ルール:
- PRが開いたままという理由だけで再確認しない
- 手動確認が必要でも、自然な区切りで全PRをまとめて1回確認する
- `github-pr-review-response` で再レビュー依頼を出した後は、新しいレビューシグナルまたは人間の明示的なマージ判断が来るまで、この待機モードへ戻る

PR作成後、作業が「作成」から「待機」へ移るときに使います。

> **Values**: 余白の設計 / 継続は力

### Step 5: 1本マージ後に残PRブランチへ main を同期する

複数のPRを並行で進めていて、そのうち1本がマージされたら、残っているPRブランチすべてへ最新の `origin/main` を取り込み、レビュー継続前に差分を揃えます。

```bash
# 作業ツリーがクリーンであることを確認し、残PRブランチへ移動
git status --short
git fetch origin
git switch feature/issue-124-followup

# マージ済み main の履歴を取り込む
git merge origin/main

# conflict があれば解消してから再検証
npm test          # またはこのリポジトリ相当の検証
npm run lint      # またはこのリポジトリ相当の検証

# 同期または conflict 解消コミットを push
git push origin HEAD
```

並行PRの post-merge チェックリスト:

1. 先行PRが GitHub 上で本当にマージ済みか確認する。
2. 残PRブランチごとに切り替え、`origin/main` を取り込む。
3. conflict が出たらその場で解消する。
4. 取り込み後に validator / lint / 関連テストを再実行する。
5. ブランチが更新されたら push し、必要に応じて再レビューを依頼する。

✅ **良い例**: 同じworkflowや近いファイルを触る sibling PR があるなら、1本マージごとに同期を必須フォローアップとして扱う。
❌ **悪い例**: 残PRを古いまま放置し、次のマージ直前になってから conflict に気づく。
Why: 早期同期の方がレビュー状態を正確に保てて、並行PR間の隠れたドリフトを防げるからです。

並行しているPRのうち1本がマージされ、まだレビュー継続中のブランチが残っているときに使います。

> **Values**: 基礎と型 / 継続は力

---

## ベストプラクティス

- PR本文は日本語で記述する（チーム標準）
- タイトルは Conventional Commits 形式（`feat:`, `fix:` 等）
- `Closes #N` で Issue を自動クローズする
- 複数行やシェルに敏感な本文では `--body-file` を既定にする（Windows では必須寄り）
- Bashで本文ファイルを作るときは `mktemp` + `trap` とクォート付きHEREDOC（`<<'EOF'`）を使う
- `gh auth status` で認証を事前確認する
- レビュー待機はイベント駆動を優先し、シグナルなしの再確認を繰り返さない
- PRごとのポーリングではなく、自然な区切りでまとめ確認する
- 並行PRの1本が先にマージされたら、残ブランチを `origin/main` と同期してからレビュー継続へ戻す
- feature branch から次のPR用ブランチを派生させる積み上げ運用をしない
- ベースPRがマージされた後、`git fetch origin` で最新状態を取得し、次の作業ブランチは必ず最新 `origin/main` から新規作成する

### 事前チェックリスト（`gh pr create` 前）

- [ ] feature branch 上で作業している（`main` ではない）
- [ ] `gh auth status` が対象アカウントで成功する
- [ ] ブランチをリモートへ push できる（保護ルールに抵触しない）
- [ ] `.github/workflows/*` を変更する場合、トークンに `workflow` scope がある
- [ ] 対象ブランチに既存のOpen PRがないことを確認済み（`gh pr list --head BRANCH --state open`）
- [ ] `skills/**/SKILL.md` を変更した場合、PR作成前に `uv run python skills/skill/_eval/scripts/validate_skill.py skills/<skill_id>/SKILL.md` を実行している
- [ ] スキル変更時は検証ゲートを確認している（overall ≥85%、各カテゴリ ≥80%、warning は高シグナル項目を優先修正）

---

## よくある落とし穴

1. **PR本文が英語になる**
   修正: テンプレ見出しを日本語で統一（概要/理由/テスト/関連）。

2. **Issueリンクの忘れ**
   修正: `## 関連` セクションに `Closes #N` を必ず含める。

3. **mainブランチから直接PRを作る**
   修正: Step 1 の状態検知で feature branch 作成に誘導。

4. **数分おきにレビューを確認し続ける**
   修正: イベント駆動の待機に切り替え、計画した区切りでのみまとめ確認する。

5. **バッククォートや `$()` を含む本文が壊れる**
   修正: クォート付きHEREDOCで本文ファイルを生成し、`--body-file` で渡す。

6. **兄弟PRがマージされたのに残ブランチを同期しない**
   修正: 各残PRブランチへ `origin/main` を取り込み、再検証後に必要なら再レビューを依頼する。

7. **feature branch から別のPRブランチを切る（依存した積み上げPR）**
   修正: 依存ブランチを増やさず、ベースPRのマージ後に `git fetch origin` で最新状態を取得し、`origin/main` から新規ブランチを作る。

## トラブルシューティング

- **Actions実行時に `workflow ... not found on the default branch` が出る**
  - 原因: `workflow_dispatch` は default branch 上に存在する workflow を対象にする。
  - 対処: 先に workflow ファイルを default branch にマージしてから手動実行する。

- **`.github/workflows/*` を含む push が権限エラーで拒否される**
  - 原因: トークンに `workflow` scope が不足している。
  - 対処: `gh auth refresh -h github.com -s workflow` で再認証する。

- **別PRのマージ後、残PRが conflict 状態になった**
  - 原因: ブランチがマージ前の main 履歴を前提にしたまま残っている。
  - 対処: `git fetch origin` 後に対象ブランチへ切り替え、`origin/main` をマージして conflict を解消し、再検証してから push する。

---

## アンチパターン

- main に直接 push してから PR を作る
- Issue 番号なしで PR を作成する
- PR 本文を空にする

---

## クイックリファレンス

### PRフローチェックリスト

- [ ] `gh auth status` で認証を確認
- [ ] 状態を検知（未コミット / 未push / PR無し）
- [ ] 必要なら `git-commit-practices` でコミット
- [ ] ブランチを origin に push
- [ ] `gh pr create` で PR 作成（日本語本文 + `Closes #N`）
- [ ] PR URL を記録したら、シグナル駆動のレビュー待機へ入る
- [ ] 実際のレビューシグナルが来たら `github-pr-review-response` へ委譲し、修正・返信・再レビュー依頼を行う
- [ ] レビュー作業完了後、マージ判断は人間へ引き継ぐ
- [ ] sibling PR が先にマージされたら、このブランチへ `origin/main` を取り込み、再検証して必要なら再レビュー依頼

### セルフレビューチェックリスト（完了前）

- [ ] PR本文に「意図・理由・テスト・Issueリンク」が揃っている
- [ ] バッククォートやシェル例を含む本文では、クォート付きHEREDOC + `--body-file` を使っている
- [ ] 自動化/workflow変更では必要な出力先ディレクトリ準備がある
- [ ] GitHub API の create 処理が冪等（422競合など）になっている
- [ ] ラベル名・色がリポジトリ規約に一致している

### PR本文テンプレート

```markdown
## 概要
（何を変更したか）

## 理由
（なぜこの変更が必要か）

## テスト
（どう検証したか）

## 関連
Closes #N
```

---

## FAQ

**Q: PR本文は英語でも良い？**
A: チームポリシーとして日本語で統一しています。

**Q: レビューやマージはこのスキルで扱う？**
A: PR作成、シグナル駆動のレビュー待機、残PRブランチ向けの確認済みマージ後同期まで扱います。標準ルートは implementation -> `github-pr-workflow` -> レビューシグナル待ち -> `github-pr-review-response` -> 人間のマージ判断/引き継ぎ です。

**Q: `gh` が未インストールの場合は？**
A: `gh auth status` でエラーになります。[GitHub CLI](https://cli.github.com/) をインストールしてください。

---

## リソース

- https://docs.github.com/en/pull-requests
- https://cli.github.com/manual/gh_pr_create
