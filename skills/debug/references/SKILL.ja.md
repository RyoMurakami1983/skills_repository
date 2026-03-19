<!--
このドキュメントは debug skill の日本語リファレンスです。
英語版: ../SKILL.md
-->

# 再現可能な証拠でデバッグする

この skill は、勘ではなく証拠でデバッグを進めるための共通コアです。

コア workflow はできるだけ不変に保ち、`modules/` 配下のドメイン別モジュールは薄く始めて、実際のデバッグセッションから学んだことだけを追記して育てます。

## When to Use This Skill

次のような場面で使います。

- コードを触る前に、まず不具合を再現して固定したいとき
- 正常系と異常系を同じ刺激で比較したいとき
- どの層が不具合の所有境界なのか切り分けたいとき
- 修正後に同じシナリオで再検証したいとき
- PR、レビュー、インシデント共有へ証拠付きで引き継ぎたいとき

## Related Skills

- **`github-pr-workflow`** - 修正と検証が終わった後に、証拠付きで PR へつなぐ
- **`github-pr-review-response`** - レビューで追加説明が必要になったときに、before/after の根拠で返す
- **`knowledge-capture`** - デバッグで学んだ再利用可能な知見を整理する

## Core Principles

1. **失敗ケースを先に固定する** - 的が定まるほど、デバッグは速くなる
2. **説明より先に証拠を集める** - スクリーンショット、ログ、トレース、差分が推測より強い
3. **同じ刺激で比較する** - 入力や条件を変えると比較が弱くなる
4. **所有境界を特定する** - 症状ではなく、本当に壊れた層を直す
5. **根本原因に対する最小修正を選ぶ** - 小さい修正ほど検証しやすく安全
6. **再利用できる痕跡を残す** - 一回のデバッグを次回の資産にする

## Preflight

- 観測された挙動、期待挙動、最小再現刺激を書き出す
- どのドメインモジュールを読むべきか `modules/` から決める
- `debug/<session>/` のような保存先を先に決める
- 固定すべき環境、モード、入力、時刻条件を洗い出す
- 修正後に再実行すべき既存 gate を確認する

## Module Decision Table

最初に読む module を決めるための短い決定表です。どれから証拠を取るべきか曖昧なときは、最も近いものから始め、必要なら `evidence-manifest.md` を併用します。

| 現象の形 | 最初に読む module | 理由 |
|---|---|---|
| UI、描画、editor、入力、focus、layout のずれ | `gui.md` | まず見た目と操作の証拠が主役になるため |
| HTTP、認証、service、transaction、cache のずれ | `api-backend.md` | request と状態境界の切り分けが主になるため |
| data drift、schema 破壊、join、null、aggregate の不具合 | `data-etl.md` | snapshot と分布比較が重要になるため |
| 機能は正しいが latency、throughput、memory が悪い | `performance.md` | 機能差分より計測結果が主役になるため |
| race、retry、ordering、AI 出力の揺らぎ、時刻依存だが強い物理要因が見えない | `nondeterminism.md` | time と制御変数を握るのが最短だから |
| 個体差、fixture、電源、環境、発生時間、場所、周辺設備、仕様外使用で出たり出なかったりする | `embedded-hardware.md` | 物理条件や測定品質が owner かもしれないため |
| 何を記録し、どう比較するか自体が曖昧 | `evidence-manifest.md` | まず証拠パッケージの型を固定するため |

## Workflow: Debug with Evidence

### Step 1 — 不具合の定義を固める

何が起きたか、何が起きるべきか、どこで起きるか、最小の再現刺激は何かを一文にまとめます。

報告が曖昧だったり、推測と事実が混ざっているときに使います。Why: 的が安定すると、寄り道の修正が減り、比較も崩れません。

> **Values**: 基礎と型 / ニュートラル

### Step 2 — 修正前の証拠パッケージを取る

コード変更前に、現在の挙動を否定できない形で残します。必要な中身はモジュールごとに変わりますが、基本は刺激、観測結果、環境またはモードです。

保存先は一箇所に寄せます。

```text
debug/<session>/
  manifest.(md|json)
  before/
  after/
```

少なくとも一度は再現できるときに使います。Why: baseline がないデバッグは、何が変わったかを証明しにくくなります。

> **Values**: 継続は力 / 成長の複利

### Step 3 — 同じ刺激で比較する

同じリクエスト、同じ入力列、同じデータセット、同じ負荷、同じハード条件を、異常系と比較対象の両方へ流します。変えるのは比較軸を一つずつだけにします。

正常系、別モード、別環境、過去の既知良好サンプルがあるときに使います。Why: 同一刺激比較は、ノイズではなく本当の差を見つける最短ルートです。

> **Values**: ニュートラル / 基礎と型

### Step 4 — 所有境界を切り分ける

選んだモジュールを使い、入力処理、validation、transaction、layout、cache、timing、concurrency、sensor chain などの境界で問題を切ります。期待と現実が最初にずれる境界を探します。

症状は見えているが、どの層が owner か分からないときに使います。Why: 境界起点で切ると、大きすぎる変更を避けて根本原因へ近づけます。

> **Values**: 温故知新 / 基礎と型

### Step 5 — 根本原因に対する最小修正を入れる

ずれを消す最小の場所を変えます。証拠が示していない refactor や予防線を、ついでに積み上げないようにします。

所有境界が十分に見えたときに使います。Why: 小さな修正の方が検証範囲を締めやすく、新しい不具合も生みにくいです。

> **Values**: 基礎と型 / 余白の設計

### Step 6 — 同じシナリオと gate を再実行する

同じ刺激を流し、証拠パッケージを再構築し、影響面の既存 check を回します。最後に root cause、変更ファイル、実行コマンド、artifact path を引き継ぎます。

修正を入れ終えたときに使います。Why: 同じシナリオを再実行して初めて、単なる変更が検証済み修正になります。

> **Values**: 継続は力 / 成長の複利

## Modules

`modules/` 配下は、コア workflow を置き換えるものではなく付録です。最初は薄く置き、実際のデバッグセッションで役立った内容だけを追記します。

| Module | 使う場面 | 現在の状態 |
|---|---|---|
| `gui.md` | UI、描画、editor、入力、focus、layout の不具合 | 現時点の主力 |
| `api-backend.md` | HTTP、認証、service、transaction、cache の不具合 | 薄い starter |
| `data-etl.md` | pipeline、schema、join、分布、null 処理の不具合 | 薄い starter |
| `performance.md` | latency、memory、throughput、hot path の不具合 | 薄い starter |
| `distributed-concurrency.md` | ordering、retry、race、sync、eventual consistency の不具合 | 薄い starter |
| `embedded-hardware.md` | sensor、waveform、calibration、fixture、環境条件の不具合 | 薄い starter |
| `nondeterminism.md` | time、seed、retry、parallelism の横断課題 | 薄い starter |
| `evidence-manifest.md` | 何をどう記録し比較するかの標準化 | 薄い starter |

現象が intermittent だからといって、最初から hardware と決めつけないでください。最初の手掛かりに最も合う evidence shape の module から入り、最初の比較結果を見てから広げます。

## Pitfalls

- **baseline を取る前にコードを変える**: before/after の一番強い証拠を失います
- **比較のたびに刺激を変える**: 見かけほど強い比較になりません
- **境界ではなく症状を直す**: 次のシナリオで再発しがちです
- **コア skill にドメイン詳細を詰め込む**: hot path がノイジーになり再利用しにくくなります

## Anti-Patterns

- **証拠パッケージなしの exploratory fix**: 先に編集して、あとで説明が付くことを期待する
- **1 モードだけ成功したら完了扱い**: 影響したモードや環境を十分に見ない
- **実戦前に module を肥大化させる**: 実際に役立つと分かる前に長文化する

## Troubleshooting

- **ローカルで再現しない**: 環境差、feature flag、時刻条件を先に洗い出します
- **証拠がノイジー**: 刺激を狭め、可能なら clock や seed を固定し、高信号の artifact に絞ります
- **怪しい境界が多すぎる**: 一度に一境界ずつ比較し、最初のずれを記録します

## Self-Review

- 安定した failing scenario を一つ示せるか
- before/after で同じ刺激を維持できたか
- 後から他人が見返せる artifact を残したか
- 症状だけでなく所有境界を言語化したか
- 影響する gate を再実行し、証拠 path を引き継いだか

## Quick Reference

1. 不具合を定義する
2. baseline 証拠を取る
3. 同じ刺激で比較する
4. 所有境界を切り分ける
5. 最小修正を入れる
6. 同じシナリオと gate を再実行する
7. root cause、変更、コマンド、artifact path を引き継ぐ
