---
name: validate
description: >
  スキルの構造品質と出荷可否を段階的に検証する。Use when: draft の最低基準確認、
  公開前レビュー、rollout 可否の判断をしたいとき。
compatibility: "_foundation/QUALITY.md, _eval/scripts/validate_skill.py"
---

# スキルを検証する

最小の構造検証から始めて、必要に応じて enterprise review や behavioral eval まで段階的に進める sub-skill です。段階を分ける理由は、個人実験の軽さを保ちつつ、共有利用では必要な厳しさを上げられるようにするためです。

## こんなときに使う

- 新規 skill が最低限の構造を満たすか確認したいとき
- 編集後の skill を公開や merge の前に見直したいとき
- team / organization rollout に進めるべきか判断したいとき
- behavior を eval で測るべきか決めたいとき

## ワークフロー: スキルを検証する

### ステップ 1 — L1 Critical を通す

まず `_foundation/QUALITY.md` の Critical を通します。この repo では `uv run python skills/skill/_eval/scripts/validate_skill.py <path-to-skill>/SKILL.md --level L1` を実行します。発見できない skill、実行指針が欠けた skill は先へ進めません。

### ステップ 2 — Recommended シグナルを見る

Recommended は readability、reuse、maintainability の弱点を見つけるためのシグナルです。L1 を通っても使いにくい skill が残る理由は、ここに出ることが多いです。

### ステップ 3 — 共有利用なら L3 を検討する

team-wide に使う skill なら、governance、security、ownership、operational readiness を追加で確認します。個人用 draft と共有用 skill では、求める厳しさが変わります。

### ステップ 4 — behavior が焦点のときだけ L4 へ回す

問いが「形として正しいか」ではなく「本当に結果を改善するか」なら `../evaluate/` へ回します。static check と behavioral check は別の問いに答えるものです。

## 早見表

| Level | 目的 |
| --- | --- |
| L1 | 最低限の構造を確認する |
| L2 | readability / reuse を含めて見直す |
| L3 | 共有利用に向けた governance を確認する |
| L4 | behavior 変化を比較評価する |

## 共通リソース

- `_foundation/QUALITY.md` — Critical / Recommended の基準
- `../../_eval/scripts/validate_skill.py` — validator 本体
- `../evaluate/` — behavior を測る次ルート
- `../improve/` — 指摘を反映して戻る改善ルート

## 注意点

- **Recommended をノイズ扱いしない**: 弱いシグナルの積み重なりが、実際の adoption friction を説明することが多いです。
- **共有 skill の enterprise review を飛ばさない**: rollout risk が変われば、必要な scrutiny も変わります。
- **eval で構造不備をごまかさない**: metadata や workflow が壊れたままでは、behavior test が良くても出荷の根拠になりません。
