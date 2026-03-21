# ADR-003: SKILL.md の日本語正本化と bilingual 運用の段階的廃止

## ステータス

Accepted

## 日付

2026-03-20

## コンテキスト

このリポジトリの skill 群は、長らく **英語の `SKILL.md` を本体** とし、必要に応じて `references/SKILL.ja.md` を追加する bilingual 運用を採ってきた。

しかし実運用では、以下の問題が顕在化していた。

- **更新コストの二重化**: 本体と日本語参照の両方を追従更新する必要がある
- **意味のズレ**: 本体更新後に `SKILL.ja.md` が遅れて古くなる
- **型の複雑化**: validator、template、generator、tests まで bilingual 前提が埋め込まれ、変更しにくい
- **repo 実態との不整合**: README、ADR、運用文書の多くはすでに日本語中心であり、skill だけ英語正本を維持する理由が弱くなっていた

今回の目的は「英語を禁止する」ことではない。  
**どのファイルを single source of truth にするかを見直し、運用コストを下げる**ことが目的である。

## 決定

**`SKILL.md` を既定で日本語の正本とし、`references/SKILL.ja.md` を前提とする bilingual 運用を段階的に廃止する。**

- 既定言語は日本語とする
- `SKILL.md` を唯一の正本とする
- `references/` は今後も overflow docs や補助資料の置き場として使う
- ただし `references/SKILL.ja.md` を常設前提にはしない
- 移行は big-bang ではなく **段階移行** とし、まず `skills/skill/` を pilot にする
- pilot 期間中は validator / generator / template が旧形式も一時的に受理できるようにし、既存資産との互換を保つ

## 検討した選択肢

### Design A（採用）: `SKILL.md` を日本語正本にし、段階移行する

- **概要**: 日本語 `SKILL.md` を正本とし、旧来の `references/SKILL.ja.md` は段階的に廃止する
- **メリット**:
  - 単一正本化により更新コストを削減できる
  - validator / template / generator の型を簡素化できる
  - repo 全体の日本語中心運用と整合する
  - pilot で学びながら安全に横展開できる
- **デメリット**:
  - 英語圏の利用者には読みやすさが下がる
  - 外部公開を強く意識する skill では別途翻訳方針が必要になる
  - 移行期間中は新旧フォーマットの両対応が必要になる

### Design B（不採用）: 現行の EN 本体 + JP reference を維持する

- **概要**: `SKILL.md` は英語のまま維持し、日本語は `references/SKILL.ja.md` で補う
- **メリット**:
  - 海外利用や公開共有の見通しは立てやすい
  - 既存 validator / template / generator をすぐには大きく変えなくてよい
- **デメリット**:
  - 二重管理コストが継続する
  - 実態に合わない運用を守るための手間が増える
  - 変更時に意味のズレが起きやすい

### Design C（不採用）: 全 skill を一括で即時日本語化する

- **概要**: repo 全体を一気に日本語 `SKILL.md` へ切り替える
- **メリット**:
  - 方針の見通しは最も明快
  - 新旧混在の期間を短くできる
- **デメリット**:
  - validator / generator / tests / docs を同時に壊すリスクが高い
  - 既存 skill 群への影響範囲が広すぎる
  - 学習なしで横展開するため、設計ミスが全体へ波及しやすい

## 結果

### Positive

- **単一正本化**: `SKILL.md` を読むだけで最新意図を追える
- **運用負荷の削減**: bilingual 追従更新が不要になる
- **型の整理**: validator / template / generator を repo 実態に合わせて簡潔にできる
- **段階導入**: `skills/skill/` pilot で学んでから他 skill へ広げられる

### Negative

- **英語アクセシビリティ低下**: 日本語に不慣れな利用者には入りにくくなる
- **互換維持コスト**: pilot 期間中は新旧形式の受理ルールが必要
- **移行判断の継続必要**: どこで旧形式の受理を打ち切るかを後続で判断する必要がある

## 決定基準

- **単一の信頼できる情報源**: 更新時に意味が分岐しないこと
- **余白の設計**: 翻訳維持コストに時間を奪われず、本質的な skill 改善へ余白を戻すこと
- **基礎と型**: 人間と AI が同じ型で生成・検証できること
- **成長の複利**: pilot の学びを validator / template / generator に織り込み、後続 skill へ横展開できること

## 適用範囲

第1段階の適用対象は **`skills/skill/`** とする。

- `SKILL.md`
- `sub_skills/*/SKILL.md`
- `_foundation/*`
- `_eval/scripts/validate_skill.py`
- `scripts/create_skill.py`
- 関連 tests

README と ADR に理由を明文化したうえで、上記 pilot を実施する。

**補足（2026-03 rollout）**: pilot で validator / generator / template の型を確認した後、同じ原則を `skills/skill/` を除く `skills/` 配下の skill へ横展開する。

## 移行原則

1. 文書だけ先に変えず、validator / generator / template を先に追従させる
2. `references/` 自体は残してよいが、`references/SKILL.ja.md` を常設前提にしない
3. 移行期間中は旧形式を一時受理し、pilot 完了後に受理範囲を再評価する
4. 外部共有や明確な要件がある場合のみ、翻訳や別言語版を追加する

## 今後の類似判断チェックリスト

- [ ] bilingual 維持は本当に利用価値よりコストのほうが小さいか？
- [ ] single source of truth はどのファイルか明確か？
- [ ] validator / template / generator / tests が同じ方針を共有しているか？
- [ ] 全体一括切替ではなく pilot から始めたほうが安全ではないか？

## 関連

- [ADR-001](./ADR-001-dotnet-security-foundation-extraction.md): .NET WPF セキュリティ基盤の独立スキル抽出
- [ADR-002](./ADR-002-quality-gate-ci-strategy.md): 品質ゲートCI導入判断と横展開戦略
- [`README.md`](../../README.md): repo 入口と言語方針の要約
- [`copilot/copilot-instructions.md`](../../copilot/copilot-instructions.md): repo の skill 作成規律
