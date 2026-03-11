# skills_repository repo-specific instructions

このファイルは、`skills_repository` 専用の運用ルールを定義します。

基礎となる価値観・判断基準は常に [`PHILOSOPHY.md`](../PHILOSOPHY.md) を優先してください。

## Documentation maintenance

### PHILOSOPHY.md を前提にする

- README や CHANGELOG の構造変更を行う前に、`PHILOSOPHY.md` の方針に反しないことを確認する
- 特に **基礎と型**、**成長の複利**、**余白の設計** を損なう変更は避ける

### README.md の役割

- `README.md` は **入口** として保つ
- 最もよく使う導線を優先し、詳細説明は `docs/` へ逃がす
- 完全な履歴置き場にはしない
- 「最近の主要変更」を載せる場合でも **最大3項目** に抑える

### CHANGELOG.md の役割

- `CHANGELOG.md` は **月次サマリ** で管理する
- 見出しは `## YYYY-MM` 形式を使う
- すべての commit を転記せず、**curated summary** として主要変更のみ残す

### CHANGELOG に残す変更

- 新しい skill / agent / business workflow の追加
- 既存スキルやディレクトリ構造の大きな移動・統合・削除
- validation / quality gate / repository policy の変更
- README や docs 構造の大きな見直し

### CHANGELOG に原則残さない変更

- typo 修正
- wording だけの修正
- artifact / placeholder の追加
- 利用者影響が薄い小さな chore

### README と CHANGELOG の同期ルール

- 実質的な変更を加えたときは、該当月の `CHANGELOG.md` を更新する
- ユーザーが「最新にして」「更新して」「今月分を反映して」と指示した場合は、`CHANGELOG.md` に加えて `README.md` の「最近の主要変更」も見直す
- README には、入口で見せる価値が高い変更だけを抜粋する

### 複雑化した場合の次手

- instruction だけで monthly 更新が安定しない場合は、`.github/skills/` に repo-local skill を追加して workflow 化する
- ただし、まずはこの instruction-first 運用を優先する
