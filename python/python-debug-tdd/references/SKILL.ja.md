---
name: python-debug-tdd
description: Pythonの不具合をTDD型（Red→原因調査→Green→副作用確認）で最小修正し、回帰テストを恒久化する。バグ報告を安全に再現・修正・再発防止したいときに使用。
metadata:
  author: RyoMurakami1983
  tags: [python, tdd, debug, pytest, regression]
  invocable: false
  tool_versions:
    python: ">=3.11"
    pytest: ">=8.0"
    uv: ">=0.5"
  last_reviewed: "2026-03-05"
---

# PythonバグをTDDで修正する

不具合を安全に直すための単一ワークフローです。まず再現（Red）し、根本原因を特定し、最小修正でGreenに戻し、回帰防止を残します。

## このスキルを使うタイミング

Use when:
- バグ報告はあるが、テストで失敗がまだ再現できていない
- 大規模改修を避け、最小変更で確実に修正したい
- 同種の障害が再発しており、回帰テストの保持が弱い
- レビューで `red -> green` の客観証跡が求められている
- Python的な原因切り分けを `@python-shihan` と連携したい

トリガーパターン:
- 「ローカル再現が困難で本番データで壊れる」
- 「重み・penalty coefficient 周りで計算がずれる」
- 「呼び出し側と実装側で制約の前提が噛み合っていない」
- 「型変換（str/int/float/bool）で意図せず挙動が変わる」
- 「タイムゾーン・丸め・デフォルト値の層間ドリフト」

---

## Core Principles

1. **推測より再現を先に** — 直感ではなく失敗テストから始める（基礎と型の追求）
2. **影響範囲を限定** — RedをGreenに戻す最小変更を優先する（余白の設計）
3. **仮説駆動で調査** — 前提を書き出し、反証可能な形で潰す（ニュートラルな視点）
4. **未来の失敗を防ぐ** — 回帰テストを恒久保持する（成長の複利）
5. **小さく改善を積む** — Green後に薄くリファクタする（継続は力）

---

## Workflow: TDD型バグ修正（Red → 原因調査 → Green → 防御）

### Step 1: 失敗テストで再現する（Red）

報告された不具合を最小再現テストとして固定します。

```python
import pytest

def test_calculate_score_handles_penalty_coefficient_regression():
    base = 100
    penalty = "0.2"

    result = calculate_score(base=base, penalty=penalty)

    assert result == 80
```

最小再現テストの型:
- 1テスト1期待値に絞る
- 失敗に必要な最小データだけを置く
- assertion にドメイン契約を明示する
- テスト名に欠陥文脈（`_regression`, `_edge_case`）を入れる

Use when 仕様解釈が揺れており、まず共通の失敗事実を作りたいとき。

> **Values**: 基礎と型の追求 / ニュートラルな視点

### Step 2: チェックリストで根本原因を調査する

失敗経路を追い、最初に状態が壊れる地点を特定します。

調査チェックリスト:
- 入力正規化: `str/int/float/Decimal/None` を明示的に扱っているか
- penalty coefficient: 範囲・デフォルト・符号を検証しているか
- 制約不一致: caller の前提境界を callee が強制しているか
- 単位不一致: パーセント（`20`）/ 比率（`0.2`）/ basis points（`2000`）
- 順序依存: sort/filter/group が決定性を崩していないか
- 境界条件: `>=` と `>`、off-by-one
- 日時変換: naive/aware datetime 混在、timezone取り扱い
- シリアライズ境界: JSON/YAML/env パース時の型ドリフト

連携メモ:
- 実装修正前に `@python-shihan` に仮説ログを見せ、分岐の絞り込みを相談する。

Use when 原因候補が複数あり、勘で修正するとノイズが増えるとき。

> **Values**: 温故知新 / ニュートラルな視点

### Step 3: 最小修正でGreenに戻す

焦点を1つに絞った修正を入れ、まず関連テストを再実行します。

```python
def calculate_score(base: int, penalty: float | str) -> int:
    penalty_value = float(penalty)
    if not 0 <= penalty_value <= 1:
        raise ValueError("penalty must be in [0, 1]")
    raw_score = base * (1 - penalty_value)
    # スコアは四捨五入で整数化し、境界挙動を明示する
    return round(raw_score)
```

Use when 根本原因が1文で説明でき、必要な不変条件を明確化できたとき。

> **Values**: 余白の設計 / 基礎と型の追求

### Step 4: 副作用テスト追加と安全なリファクタ

Green後に近傍ケースを追加し、可読性改善は挙動を変えない範囲で行います。

修正後チェックリスト:
- 近傍エッジケース（境界値/不正入力）を最低1件追加
- 無関係な snapshot/golden の差分が出ていないか確認
- 対象ゲートを実行（`pytest -k`, lint, type check）
- Issueスコープ外のAPI変更を入れない
- リファクタはコミット分離、またはPRで明確に区分

Use when 単発修正は通ったが、近傍ロジックで再発リスクが高いとき。

> **Values**: 成長の複利 / 継続は力

### Step 5: 回帰防止を保持してクローズする

最初の失敗テストは恒久的な回帰テストとして保持し、PRに原因要約を残します。

```bash
uv run pytest -k "regression or penalty_coefficient"
uv run pytest
```

Use when マージ前の最終確認とレビュー引き継ぎを行うとき。

> **Values**: 温故知新 / 成長の複利

---

## Best Practices

- 実装修正前に必ず失敗テスト（Red）を作る
- コミットを小さく分離する: `test(red) -> fix(green) -> side-effect tests`
- 境界での型変換と範囲検証を明示する
- 仮説と検証結果をIssue/PRに残して再現可能性を高める
- typing・データモデル・Python idiomが絡む場合は `@python-shihan` レビューを依頼する

---

## Common Pitfalls

1. **失敗テストなしで実装をいじる**  
   対処: まず最小再現テストを作る。

2. **1つのfixtureに過剰適合する**  
   対処: 近傍エッジケースを1件追加して一般化を確認する。

3. **暗黙変換での事故（`bool("0")` など）**  
   対処: 変換を明示し、ドメイン制約を検証する。

4. **バグ修正と大規模リファクタを混在**  
   対処: 挙動修正と整理を分離する。

---

## Anti-Patterns

- red/green証跡のない「たぶん直った」コミット
- 不安定テストを安定化せず skip で回避する
- `except Exception` で根本原因を隠す
- 障害対応中にIssueスコープを拡張して全面改修する

---

## Quick Reference

### 最小コマンドループ

```bash
# 1) 再現 (red)
uv run pytest -k "<bug_keyword>" -q

# 2) 最小修正
# edit code

# 3) green確認 + 近傍確認
uv run pytest -k "<bug_keyword> or <adjacent_case>" -q
uv run pytest -q
```

### 不具合切り分け表

| 症状 | 最初の確認 | 典型的な対処 |
|---|---|---|
| 重み付き結果がずれる | penalty coefficient の単位/範囲 | 正規化 + 境界検証 |
| 分岐が不安定 | 型変換とtruthiness | 明示変換 + guard clause |
| caller/calleeで前提が不一致 | 制約契約の明文化 | 境界で不変条件を強制 |
| 日時がずれる | timezone正規化 | aware datetime に統一 |

### マージ前ゲート

- [ ] 元バグをテストで再現できる（red証跡あり）
- [ ] 最小修正で関連テストがgreen
- [ ] 近傍の副作用テストを追加済み
- [ ] 回帰テストを恒久保持し、skip回避運用に流れていない
- [ ] PRにIssueリンクと原因要約がある
