---
name: skill-git-commit-practices
description: Conventional Commitsと原子的コミットの実践ガイド。履歴標準化に使う。
author: RyoMurakami1983
tags: [git, commits, conventional-commits, workflow, quality]
invocable: false
version: 1.0.0
---

# Gitコミット実践

一貫したコミットメッセージ、原子的コミット、学習可能な履歴を作るための実践パターンです。

**Conventional Commits**: feat/fix等の標準化されたコミット形式。
**Atomic Commit**: 1つの目的に絞ったコミット。
**Pull Request (PR)**: GitHub上のレビュー前提の変更提案。

Progression: Simple → Intermediate → Advanced の例で段階的に深めます。
Reason: 文脈が増えるほど履歴の再利用性が上がります。

## このスキルを使うとき

以下の状況で活用してください：
- 複数人のリポジトリでコミット形式を統一したい
- 日本語コミットを履歴で読みやすく保ちたい
- 原子的コミットでレビューとリバートを安全にしたい
- コミット本文にWhyを残して判断理由を共有したい
- Pull Request (PR)前に履歴を整えたい
- 新メンバーに再現可能なコミット運用を教えたい

## 関連スキル

- **`skill-github-pr-workflow`** - PR作成とマージ運用
- **`skill-git-review-standards`** - レビュー品質とPRサイズ基準
- **`skill-git-history-learning`** - 履歴を学習資産化
- **`skill-issue-intake`** - Issue作成とトリアージ

---

## 依存関係

- Git 2.30+
- Conventional Commitsの合意
- Pull Request (PR)運用

---

## コア原則

1. **単一責務** - 1コミット=1論理変更
2. **Whyを残す** - 理由は実装より長持ちする
3. **形式の一貫性** - 自動化と検索性を高める
4. **レビュー容易性** - 小さなコミットでリスク低減
5. **学習資産化** - 履歴をチームの教材にする

---

## パターン1: Conventional Commits構造

### 概要

Conventional Commitsでメッセージを統一します。

### 基本例

```bash
# ✅ CORRECT
git commit -m "feat: 通知設定を追加"

# ❌ WRONG
git commit -m "update stuff"
```

### 中級例

```bash
git commit -m "fix: CSVインポートの文字化けを修正

Why: UTF-8 BOM付きCSVで失敗していたため"
```

### 上級例

```bash
git commit -m "feat(auth)!: OAuth2を導入

BREAKING CHANGE: /auth/login を /oauth/authorize に変更"
```

### 使うとき

- 履歴からCHANGELOGを自動生成したい
- 複数人で同じ形式を使いたい

---

## パターン2: タイプとスコープ選定

### 概要

typeとscopeで変更意図を明確化します。

### 基本例

| Type | 用途 | 例 |
|------|-----|----|
| `feat` | 新機能 | `feat: 通知を追加` |
| `fix` | バグ修正 | `fix: 文字化け修正` |
| `docs` | 文書更新 | `docs: 手順追加` |
| `test` | テスト | `test: E2E追加` |
| `refactor` | 内部整理 | `refactor: 命名整理` |

E2Eはend-to-end (E2E) テストです。

### 中級例

```bash
# ✅ CORRECT - scope指定
git commit -m "feat(api): 決済APIを追加"
```

### 上級例

```bash
# モノレポscope
git commit -m "fix(web): 404画面の導線修正"
```

### 使うとき

- モジュール単位で責務が分かれている
- 複数ドメインが共存する

---

## パターン3: 日本語メッセージの明確化

### 概要

日本語コミットを検索可能にします。

### 基本例

```bash
# ✅ CORRECT
git commit -m "fix: ログイン失敗時のエラーメッセージを明確化"

# ❌ WRONG
git commit -m "fix: バグ修正"
```

### 中級例

```bash
git commit -m "feat: 注文履歴画面に検索フィルタを追加

Why: サポート対応で検索要求が多かったため"
```

### 上級例

```bash
git commit -m "refactor: 配送計算ロジックを整理

Why: 例外処理の分岐が増えたため"
```

### 使うとき

- チームの母国語が日本語
- 履歴を監査・レビューで使う

---

## パターン4: 原子的コミット

### 概要

原子的コミットで変更を分割します。

### 基本例

```bash
# ❌ WRONG - 複数責務
git commit -m "feat: 認証追加とUI改善とテスト追加"

# ✅ CORRECT - 分割
git commit -m "feat: 認証機能を追加"
git commit -m "refactor: UIレイアウトを改善"
git commit -m "test: 認証フローのテストを追加"
```

### 中級例

- モデル変更とAPI変更は別コミット
- ドキュメント更新は別コミット

### 上級例

```bash
# 部分ステージング
git add -p src/user/service.py
git commit -m "feat: ユーザー検証を追加"
```

### 使うとき

- レビューで段階的に確認したい
- 安全にリバートしたい

---

## パターン5: Commit本文とWhy

### 概要

Whyを残して判断理由を共有します。

### 基本例

```bash
git commit -m "fix: APIタイムアウトを10s→30sに変更

Why: 大量データ処理で10sでは不足していたため"
```

### 中級例

```bash
git commit -m "refactor: キャッシュキー生成を整理

- 旧キーの衝突を回避
- 生成ロジックを共通化
Why: 監視で衝突率が増えたため"
```

### 上級例

```python
# ✅ CORRECT - 根拠を残す
import textwrap

message = textwrap.dedent("""\
fix: 画像圧縮率を調整

Why: 画像サイズが平均30%増加していたため
""")
```

### 使うとき

- 後で理由が問われそうな変更
- 判断根拠を残したい場合

---

## パターン6: コミット前チェック

### 概要

チェックリストで品質を担保します。

### 基本例

```bash
git diff
git status
git commit -m "feat: ..."
```

### 中級例

```bash
# テスト実行
npm test
```

### 上級例

コミットlint設定ファイル（config）の例:

```yaml
# .commitlintrc.yml
rules:
  type-enum: [2, "always", ["feat","fix","docs","test","refactor","chore"]]
```

```csharp
// ✅ CORRECT - コミットポリシー登録
using Microsoft.Extensions.DependencyInjection;

services.AddSingleton<CommitPolicyChecker>();
```

```bash
# ✅ CORRECT - error handling for commit checks
if ! git diff --check --exit-code; then
  echo "Commit check failed"; exit 1
fi
```

### 使うとき

- PR前に品質を安定させたい
- 新規メンバーのオンボーディング

---

## パターン7: AmendとRebaseの安全運用

### 概要

共有前のみ履歴を書き換えます。

### 基本例

```bash
git commit --amend -m "fix: 正しいメッセージ"
```

### 中級例

```bash
git rebase -i HEAD~3
```

### 上級例

```bash
# push後は新コミットで修正
git commit -m "fix: 補足修正"
```

### 使うとき

- PR前の整理をしたい
- 共有ブランチの安定を守りたい

---

## ベストプラクティス

- 動詞で始める
- 50文字以内のルールを決める
- Why行で理由を残す
- ドキュメント更新は分離する
- 大きな変更はコミット分割する

---

## よくある落とし穴

1. **曖昧なメッセージ**  
Fix: 名詞と動詞で具体化する。

2. **複数の変更を混在**  
Fix: 原子的コミットに分割する。

3. **文脈がない**  
Fix: Why行を追加する。

---

## アンチパターン

- TODOコメントで先送り
- 共有ブランチのrebase
- 1コミットに複数責務を入れる

---

## クイックリファレンス

### コミットチェック

- [ ] `git diff` を確認
- [ ] 1コミット=1責務
- [ ] Conventional Commits形式
- [ ] Whyを付ける

### 判断テーブル

| 状況 | 対応 | 理由 |
|------|------|------|
| 30分以内 | そのままコミット | テンポ維持 |
| 複数責務 | 分割コミット | レビュー安全 |
| 共有ブランチ | rebase回避 | 履歴保護 |

---

## FAQ

**Q: スコープは必須ですか？**  
A: モジュールが明確なら付けると便利です。

**Q: WIPコミットは許容？**  
A: ローカルならOKですがPR前に整理します。

**Q: 間違ったメッセージをpushしたら？**  
A: rebaseせず新しい修正コミットを追加します。

---

## リソース

- https://www.conventionalcommits.org
- https://git-scm.com/docs/git-commit
