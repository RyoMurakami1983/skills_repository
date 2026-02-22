---
name: skill-git-history-learning
description: Git履歴を学習資産として使い、意思決定を共有する。
metadata:
  author: RyoMurakami1983
  tags: [git, history, learning, documentation, workflow]
  invocable: false
---

# Git履歴学習

コミット履歴、タグ、ノートを使って「なぜ」を学び、オンボーディングを高速化します。

**Architecture Decision Record (ADR)**: 重要な設計判断を記録する文書。
**Changelog**: リリース内容をまとめた履歴サマリ。
**Git Notes**: 履歴を変えずに追加メタデータを残す仕組み。

Progression: Simple → Intermediate → Advanced で段階的に深めます。
Reason: 文脈が増えるほど学習と監査が速くなります。

## このスキルを使うとき

以下の状況で活用してください：
- 新メンバーを履歴でオンボーディングしたい
- 過去の意思決定を再確認したい
- Changelogやリリースノートを整備したい
- レビュートレーニングに事例を使いたい
- インシデントの学びを再利用したい
- 暗黙知を形式知として共有したい

## 関連スキル

- **`skill-git-commit-practices`** - 文脈付きコミット
- **`skill-git-review-standards`** - レビュー標準
- **`skill-github-pr-workflow`** - PRフロー

---

## 依存関係

- Git 2.30+
- リポジトリ履歴へのアクセス

---

## コア原則

1. **履歴は図書館** - 責任追及でなく学び
2. **Why重視** - 意思決定の背景を残す
3. **追跡性** - Issue/PRに紐付ける
4. **再利用可能な学習** - 事例を型にする
5. **成長の複利** - 共有して学ぶ

---

## パターン1: 文脈付きで履歴を読む

### 概要

グラフ表示で流れを理解します。

### 基本例

```bash
# ✅ CORRECT
git log --oneline --graph --decorate -20

# ❌ WRONG
git log
```

| 目的 | コマンド | 使うとき |
|------|----------|----------|
| ざっと確認 | `git log --oneline` | 毎日の確認 |
| 流れ把握 | `git log --graph` | ブランチ調査 |

### 中級例

```bash
# 著者とマージも確認
git log --graph --decorate --pretty="%h %an %s" -20
```

### 上級例

- `git log --since="30 days"` で期間指定

### 使うとき

- 機能の起点を知りたい
- リリース範囲を把握したい

---

## パターン2: git blameで学ぶ

### 概要

行の理由を辿ります。

### 基本例

```bash
# ✅ CORRECT
git blame path/to/file.cs

# ❌ WRONG
git blame -w
```

### 中級例

- PRリンクと合わせて読む

### 上級例

- リファクタ前にリスク把握

### 使うとき

- バグの起点調査
- サブシステムの理解

---

## パターン3: 学習できるコミットメッセージ

### 概要

「なぜ」を説明するメッセージにします。

### 基本例

```text
feat: API負荷低減のためプロファイルを30秒キャッシュ

# ❌ WRONG
update
```

### 中級例

- 影響と理由を短く書く

### 上級例

- Issue番号や意思決定ログを添える

### 使うとき

- 差分だけでは判断が難しい
- 将来の調査を見越す

---

## パターン4: 履歴からリリースノート作成

### 概要

履歴をまとめてリリースノートにします。

### 基本例

リリース設定ファイル（config）の例:

```yaml
# .github/release.yml
categories:
  - title: "Features"
    labels: ["feature"]
```

### 中級例

```python
# ✅ CORRECT - 失敗時に中断
import subprocess

try:
    output = subprocess.check_output(["git", "log", "--oneline", "-5"], text=True)
    print(output)
except subprocess.CalledProcessError as exc:
    raise SystemExit(exc.returncode)
```

### 上級例

- CIで自動生成する

### 使うとき

- リリースノートが必要
- 共有用サマリが必要

---

## パターン5: オンボーディングの履歴活用

### 概要

履歴を教材化します。

### 基本例

```text
学習ルート:
1) 初期API
2) 認証フロー
3) 決済統合
```

### 中級例

- PRリンクと議論も共有

### 上級例

- 短い解説セッションを録画

### 使うとき

- 新人受け入れ
- 引き継ぎ時

---

## パターン6: 振り返り指標

### 概要

履歴から傾向を学びます。

### 基本例

```bash
# ✅ CORRECT
git shortlog -s -n --since="90 days"
```

### 中級例

- サブシステム別に集計

### 上級例

```csharp
// ✅ CORRECT - 履歴分析登録
using Microsoft.Extensions.DependencyInjection;

services.AddSingleton<HistoryAnalyzer>();
```

### 使うとき

- ベロシティ分析
- ボトルネック把握

---

## パターン7: タグとノートで記憶

### 概要

タグとノートで意思決定を残します。

### 基本例

```bash
# ✅ CORRECT
git tag v1.2.0
```

### 中級例

```bash
# 意思決定ノート
git notes add -m "Issue #123 hotfix"
```

### 上級例

- 共有ノート運用を定義

### 使うとき

- リリース監査
- 障害対応の記録

---

## ベストプラクティス

- 履歴は学習目的で使う
- Changelog形式を統一する
- オンボード用の履歴ルートを作る
- タグとノートで意思決定を残す
- 一語コミットを避ける

---

## よくある落とし穴

1. **直近履歴だけ見る**  
Fix: 期間指定で幅を広げる。

2. **Whyが書かれていない**  
Fix: 理由を短文で追加する。

3. **履歴学習を省略**  
Fix: オンボーディングで活用する。

---

## アンチパターン

- git blameで個人を責める
- 理由なくタグを削除する
- 一語コミットを書く

---

## クイックリファレンス

### 履歴学習チェック

- [ ] logをグラフで読む
- [ ] blameで意図を確認
- [ ] whyをコミットに残す
- [ ] リリースノート作成
- [ ] 履歴でオンボーディング

### 判断テーブル

| 状況 | 対応 | Decision |
|------|------|----------|
| 新メンバー | 履歴ルート共有 | Decision: 学習短縮 |
| インシデント | ノート+タグ | Decision: 証跡確保 |
| 大きなリリース | Changelog | Decision: 影響整理 |

---

## FAQ

**Q: git blameは責任追及？**  
A: いいえ。意図を知るために使います。

**Q: 古いタグは削除して良い？**  
A: 理由記録と代替タグが必要です。

**Q: 履歴でどう教える？**  
A: 厳選コミットとPRリンクで学習します。

---

## リソース

- https://git-scm.com/docs/git-log
- https://git-scm.com/docs/git-blame
- https://github.com/release-drafter/release-drafter
