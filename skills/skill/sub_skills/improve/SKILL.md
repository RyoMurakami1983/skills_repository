---
name: improve
description: >
  既存スキルを evidence ベースで改善する。Use when: trigger 精度、
  説明の冗長さ、関連資料の同期ずれを直したいとき。
compatibility: "_foundation/CONVENTIONS.md, _eval/scripts/validate_skill.py"
---

# スキルを改善する

既存 skill の弱い説明や過剰な文言を整理し、一般化された guidance に磨き直すための sub-skill です。改善で重視する理由は、ルールを足すことではなく、なぜ効く guidance かを残して再利用性を上げるためです。

## こんなときに使う

- レビューや eval 結果を受けて公開済み skill を見直したいとき
- 挙動は変えずに context を浪費する wording を削りたいとき
- metadata や trigger 文を見直して起動精度を上げたいとき
- 関連資料や bundled asset の意味を本体と同期したいとき

## ワークフロー: スキルを改善する

### ステップ 1 — 変更の種類を分類する

実質的な挙動変更と、軽い wording 修正を分けて考えます。ここを分けると、関連資料まで同期すべきか、validation をどこまで再実行すべきかを判断しやすくなります。

### ステップ 2 — 根拠を読む

review comment、transcript、validation 出力、eval summary を読みます。同じ helper や説明が何度も再生成されているなら、bundled resource として切り出す強いシグナルです。

### ステップ 3 — 一般化の方向で書き換える

「何を書くか」だけでなく「なぜ効くか」が伝わるように書き換えます。直近の 1 ケースだけに最適化するより、複数の実 prompt に広がる pattern を優先します。

### ステップ 4 — 関連リソースを同期する

意味が変わる変更なら `references/` や bundled asset も同期します。逆に、挙動を変えない軽微修正なら、重い同期を避けて差分を小さく保ちます。

### ステップ 5 — 再検証する

変更後は `uv run python skills/skill/_eval/scripts/validate_skill.py <path-to-skill>/SKILL.md --level L2` を再実行します。構造が崩れていないことを確認して初めて、改善が完了したと言えます。

## 早見表

| 段階 | 見るもの |
| --- | --- |
| 分類 | 構造変更か wording 修正か |
| 根拠確認 | review、transcript、validation、eval |
| 本文修正 | why の明確化、一般化、冗長削減 |
| 同期 | references、assets、周辺説明 |
| 再検証 | L1-L2 |

## 共通リソース

- `_foundation/CONVENTIONS.md` — naming / frontmatter / writing style
- `../../_eval/scripts/validate_skill.py` — L1/L2 validation
- `../validate/` — 改善後の構造チェックへ戻る導線
- `../evaluate/` — behavior change を測りたい場合の次ルート

## 注意点

- **ルールを足すだけで改善した気にならない**: 説明が増えても reasoning が良くならなければ、skill は賢くならず硬くなるだけです。
- **1 つの失敗ケースに過剰適合しない**: overfitting すると、実 prompt 全体での usefulness が下がります。
- **関連リソースの同期を忘れない**: stale な補助資料は、本体を直しても静かに価値を毀損します。
