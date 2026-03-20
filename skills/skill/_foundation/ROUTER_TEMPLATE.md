---
name: <context>-<object>
description: >
  <What this router does>
---

# <Router Title>

<Explain what this router unifies and why a single entry point helps.>

## こんなときに使う

このスキルは次のようなときに使います:
- <Verb-led scenario 1>
- <Verb-led scenario 2>
- <Verb-led scenario 3>

## 判断表

| やりたいこと | ルート | 次にやること |
| --- | --- | --- |
<Decision Rows>

## 共通リソース

- `_foundation/` は sub-skill 間で共有する template / convention / quality definition を置く
- `scripts/` は sub-skill から呼ぶ deterministic helper を置く
- `references/` は overflow documentation や必要時の補助資料を置く

## ルーティングメモ

- ユーザーの現在地点に最も合う sub-skill へ直接案内する。
- 実行ロジックは router ではなく sub-skill や script に置く。
- 用語は相手の literacy に合わせ、必要なら専門語を説明する。
