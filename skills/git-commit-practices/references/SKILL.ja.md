---
name: git-commit-practices
description: Conventional Commitsと原子的コミットの実践ガイド。履歴標準化に使う。
author: RyoMurakami1983
tags: [git, commits, conventional-commits, workflow, quality]
invocable: false
version: 1.0.0
---

# Gitコミット実践

一貫したコミットメッセージ、原子的コミット、学習可能な履歴を作るための実践パターンです。

## このスキルを使うとき

以下の状況で活用してください：
- 複数人のリポジトリでコミット形式を統一したい
- 日本語コミットを履歴で読みやすく保ちたい
- 原子的コミットでレビューとリバートを安全にしたい
- コミット本文にWhyを残して判断理由を共有したい
- Pull Request (PR)前に履歴を整えたい
- 新メンバーに再現可能なコミット運用を教えたい

## 関連スキル

- **`github-pr-workflow`** - PR作成とマージ運用
- **`github-issue-intake`** - Issue作成とトリアージ

---

## 依存関係

- Git 2.30+
- Conventional Commitsの合意
- Pull Request (PR)運用

## コア原則

1. **単一責務** - 1コミット=1論理変更 (基礎と型)
2. **Whyを残す** - 理由は実装より長持ちする (成長の複利)
3. **形式の一貫性** - 自動化と検索性を高める (ニュートラル)
4. **レビュー容易性** - 小さなコミットでリスク低減 (継続は力)
5. **学習資産化** - 履歴をチームの教材にする (温故知新)

---

## ワークフロー: 品質の高いコミットを書く

### Step 1: Conventional Commits形式を使う

`type(scope): subject` 形式に従い、人と自動化ツールの両方が解析できるメッセージを書きます。

```bash
git commit -m "feat(auth)!: OAuth2を導入

BREAKING CHANGE: /auth/login を /oauth/authorize に変更"
```

複数人で統一した形式が必要な場合や、CHANGELOGの自動生成をしたいときに使います。

### Step 2: タイプとスコープを選定する

変更意図に合ったtypeを選び、モジュール分割が明確なときはscopeを付けます。

| Type | 用途 | 例 |
|------|-----|----|
| `feat` | 新機能 | `feat: 通知を追加` |
| `fix` | バグ修正 | `fix: 文字化け修正` |
| `docs` | 文書更新 | `docs: 手順追加` |
| `test` | テスト | `test: E2E追加` |
| `refactor` | 内部整理 | `refactor: 命名整理` |

```bash
# scope指定でドメインを明示
git commit -m "feat(api): 決済APIを追加"
```

モジュールやドメインが明確に分離されているリポジトリで使います。

### Step 3: 明確な日本語メッセージを書く

`git log` で検索可能で自己説明的なメッセージにします。

```bash
# ✅ CORRECT - 具体的な対象と操作
git commit -m "feat: 注文履歴画面に検索フィルタを追加

Why: サポート対応で検索要求が多かったため"

# ❌ WRONG - 曖昧
git commit -m "fix: バグ修正"
```

日本語がチームの主要言語である場合や、履歴を監査で使うときに使います。

### Step 4: 原子的コミットに分割する

1つのコミットに1つの関心事だけを含め、個別にレビュー・リバートできるようにします。

```bash
# ❌ WRONG - 複数責務
git commit -m "feat: 認証追加とUI改善とテスト追加"

# ✅ CORRECT - 分割
git commit -m "feat: 認証機能を追加"
git commit -m "refactor: UIレイアウトを改善"
git commit -m "test: 認証フローのテストを追加"
```

レビューで段階的に確認したい場合や、安全にリバートしたいときに使います。

### Step 5: 本文にWhyを記述する

コミット本文に「なぜ」を残し、将来の読者がdiffではなく判断理由を理解できるようにします。

```bash
git commit -m "fix: APIタイムアウトを10s→30sに変更

- 大量データ処理で10sでは不足していたため
- 監視で504エラーが増加していたため
Why: SLA達成率が低下していたため"
```

後から理由が問われそうな変更や、判断根拠を残したい場合に使います。

### Step 6: コミット前チェックを実行する

diffを確認し、テストを実行してからコミットし、履歴をクリーンに保ちます。

```bash
git diff
git status
npm test
git commit -m "feat: ..."
```

```yaml
# .commitlintrc.yml
rules:
  type-enum: [2, "always", ["feat","fix","docs","test","refactor","chore"]]
```

PRを開く前のプッシュ時や、新規メンバーのオンボーディングで使います。

### Step 7: AmendとRebaseの安全運用

履歴の書き換えは共有前のみ行います。push後は新しいコミットで対応します。

```bash
# push前: amendまたはinteractive rebase
git commit --amend -m "fix: 正しいメッセージ"
git rebase -i HEAD~3

# push後: 新コミットで修正
git commit -m "fix: 補足修正"
```

PR前に履歴を整理したい場合や、共有ブランチの安定を守りたいときに使います。

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
