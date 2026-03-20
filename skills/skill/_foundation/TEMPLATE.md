---
name: <context>-<verb>-<object>
description: >
  <What this skill does>
compatibility: <optional tools, runtime, or platform constraints>
---

# <Skill Title>

<Explain why this skill exists in 1-2 sentences.>

## こんなときに使う

このスキルは次のようなときに使います:
- <Verb-led scenario 1>
- <Verb-led scenario 2>
- <Verb-led scenario 3>

## ワークフロー: <Workflow Name>

### ステップ 1 — <Action>
何をするか、なぜ必要か、短い例と合わせて説明する。

### ステップ 2 — <Action>
次に何をするか、なぜ必要か、どこで失敗しやすいかを書く。

## 注意点

- **<Pitfall>**: <How to avoid it and why the safer choice works better.>

## 同梱リソース

再利用できる asset が必要なら、次のようなディレクトリ構成を使います:

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

- `scripts/`: 再利用価値のある deterministic helper code
- `references/`: 必要時だけ読む overflow documentation
- `assets/`: HTML や template など、出力に埋め込むファイル
