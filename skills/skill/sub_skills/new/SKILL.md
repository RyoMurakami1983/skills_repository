---
name: new
description: >
  新しいスキルやスキル群を要件から作る。Use when: 新規スキルを草案化したいとき、
  手作業を skill 化したいとき、router と sub-skill をまとめて作りたいとき。
compatibility: "_foundation/TEMPLATE.md, _eval/scripts/validate_skill.py"
---

# 新しいスキルを作る

アイデアを structured な skill へ変換し、必要なら router / sub-skill 構成までまとめて立ち上げるための sub-skill です。先に意図と制約を固める理由は、topic の羅列ではなく再利用可能な workflow として設計するためです。

## こんなときに使う

- 新しいワークフローを skill として草案化したいとき
- `SKILL.md` を書く前に制約や edge case を調べたいとき
- router と sibling skill を 1 つの suite として立ち上げたいとき
- 単発 prompt を再利用可能な skill package へ置き換えたいとき

## ワークフロー: 新しいスキルを作る

### ステップ 1 — 意図を定義する

skill が何をするか、いつ trigger するか、どんな出力を返すか、再利用 script / asset が必要かを先に定義します。ここを曖昧にすると、draft が workflow ではなく topic dump になりやすくなります。

### ステップ 2 — 質問と調査を先に行う

草案化の前に、edge case、依存関係、失敗パターン、成功条件を確認します。類似 skill がすでにあるなら比較し、重複ではなく不足パターンを補う形に寄せます。

### ステップ 3 — template から草案を作る

まず `_foundation/TEMPLATE.md` を基準に書き始めます。`description` は trigger-oriented に保ち、hot path は短くし、`compatibility` は本当に runtime / tool 制約がある場合だけ加えます。

### ステップ 4 — L1 validation を早めに通す

`uv run python skills/skill/_eval/scripts/validate_skill.py <path-to-skill>/SKILL.md --level L1` を早い段階で実行し、Critical が崩れていないか確認します。命名、trigger 文、workflow 構造の不足は、細部を磨く前に直します。

### ステップ 5 — suite が必要なら先に全体像を切る

1 つの domain を複数 workflow に分けるなら、先に suite を設計し、skeleton をまとめて生成してから個別に肉付けします。こうすると naming と routing の一貫性が保ちやすくなります。

### ステップ 6 — 構造パターンを選ぶ

domain を flat workflow、peer-skill orchestrator、nested `sub_skills/` を持つ router のどれで表現するか決めます。一本道で足りるなら flat workflow、主に top-level skill へ委譲するなら orchestrator、1 つの入口から内部モード分岐が必要なら router を選びます。

### ステップ 7 — 必要なら router 構造を scaffold する

internal routing が必要なら、`uv run python skills/skill/scripts/create_skill.py --name <router-name> --description "<description>" --type router --sub-skills <route-a>,<route-b>` で skeleton を作ります。親 `SKILL.md` は判断表に集中させ、実行ロジックは生成された sub-skill 側へ移します。

## 早見表

| 段階 | 何を見るか |
| --- | --- |
| 意図定義 | trigger、出力、成功条件、必要 asset |
| 調査 | edge case、依存関係、既存 skill との重複 |
| 草案化 | template 適用、description、workflow 構造 |
| 初期検証 | L1 validation |
| 構造選択 | flat / orchestrator / router |

## 共通リソース

- `_foundation/TEMPLATE.md` — workflow skill の最小 template
- `_foundation/ROUTER_TEMPLATE.md` — router 親 skill の template
- `_foundation/SUB_SKILL_TEMPLATE.md` — nested sub-skill の template
- `../../scripts/create_skill.py` — skill / router / sub-skill scaffold 生成
- `../../_eval/scripts/validate_skill.py` — L1/L2 validation

## 注意点

- **調査より先に書き始めない**: 制約を落としたまま草案化すると、後から構造を崩して直すことになりやすいです。
- **template を説明書化しない**: essentials は `SKILL.md` に残し、詳細は必要になったときだけ `references/` へ逃がします。
- **一本道の workflow に router を使わない**: nested 構造は強力ですが、route が 1 本ならコストだけが増えます。
