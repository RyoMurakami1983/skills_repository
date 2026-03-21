---
name: notion-safe-operations
description: >
  Notion MCP 操作を安全かつ再現可能に進めるために、preflight、DS ID 運用、失敗時フォールバックを標準化する。Use when: Notion ページやデータソースを作成・更新・検索するとき、認証や data source ID 周りで詰まりやすいとき。
---
# Notion Safe Operations

Notion操作をスキル横断で共通化し、セッション差分による失敗を減らすための標準手順です。

## こんなときに使う
以下の状況で使います：
- ふりかえり結果を Notion に保存するとき
- Notion ページのプロパティ更新を実行するとき
- agent/model 切替後にツール可用性を確認するとき
- Data Source（DS）ID を安全に解決するとき
- create/update 失敗時に作業停止を避けたいとき
- Notion運用をスキル間で統一したいとき

## 関連スキル

- **`furikaeri-practice`** - ふりかえりログの保存
- **`knowledge-capture`** - 公開前の匿名化
- **`skill`** - 既存スキルへの適用

---

## 依存関係

- Notion MCP ツール（`notion-notion-fetch`, `notion-notion-create-pages`）
- DS ID 用のローカル環境変数（例: `NOTION_FURIKAERI_DS_ID`）
- 対象 Notion DB へのアクセス権

---

## コア原則

1. **Run Preflight First** - 書き込み前に実呼び出しで確認する（基礎と型）
2. **Store IDs Locally** - DS ID は repo外で管理する（ニュートラル）
3. **Fail with Context** - 失敗時は再実行可能な情報を返す（継続は力）
4. **Reuse One Workflow** - Notion手順を重複記述しない（温故知新）
5. **Explain Rationale** - 手順と理由をセットで残す（成長の複利）

---

## ワークフロー: Notionを安全に実行する

### Step 1: ツール Preflight 実行

書き込み前に、実際の fetch を1回実行する。

```text
# ✅ CORRECT - 実呼び出し確認
notion-notion-fetch(id="collection://<your-data-source-id>")

# ❌ WRONG - 一覧表示だけで可用性判定
/mcp show
```

| シグナル | 判断 |
|---|---|
| fetch成功 | Step 2へ進む |
| "unauthorized" / "401" / "authentication" を含むエラー | 認証切れ → ユーザーに `/mcp r` を実行するよう案内 → 再認証後に Step 1 を再実行 |
| ツール未検出/その他失敗 | Step 5フォールバックへ |

**なぜ？** `/mcp show` で見えても、実行コンテキストで呼べない場合があるため。

> **Values**: 基礎と型 / 継続は力

### Step 2: DS ID を安全に解決

まずローカル環境変数を使う。

```bash
export NOTION_FURIKAERI_DS_ID="collection://..."
```

未設定なら DB URL を fetch し、`<data-source>` の `collection://...` を取得する。

```text
notion-notion-fetch(id="https://www.notion.so/...database-url...")
```

**なぜ？** ローカル設定は再現性が高く、識別子漏洩も防げるため。

> **Values**: ニュートラル / 基礎と型

### Step 3: スキーマ確認

対象 data source を fetch し、必須プロパティ名を完全一致で確認する。

```text
notion-notion-fetch(id="collection://...")
# 必須: タイトル, ステータス, 実施内容, 学び・気づき, 課題・問題点, 次回アクション
```

**なぜ？** create/update 失敗の多くはプロパティ名の不一致が原因。

> **Values**: 成長の複利 / 基礎と型

### Step 4: Create/Update 実行

明示的なプロパティ名と日付expanded keysを使う。

```json
{
  "parent": { "data_source_id": "<resolved-id>" },
  "pages": [
    {
      "properties": {
        "タイトル": "Session title",
        "ステータス": "完了",
        "実施内容": "...",
        "学び・気づき": "...",
        "課題・問題点": "...",
        "次回アクション": "...",
        "関連タグ": "[\"開発\", \"レビュー\"]",
        "date:セッション日時:start": "2026-03-05",
        "date:セッション日時:is_datetime": 0
      }
    }
  ]
}
```

**なぜ？** 曖昧さを減らし、セッション間で同じ結果を再現しやすくするため。

> **Values**: 基礎と型 / 温故知新

### Step 5: 失敗時フォールバック

失敗時は必ず、貼り付け可能 payload と再試行手順を返す。

```markdown
## Notion write failed
- Error: <exact error>
- Retry:

  **"unauthorized" / "401" / "authentication" を含む場合（認証切れ）:**
  1. ターミナルで `/mcp r` を実行して Notion を再認証する
  2. Step 1 preflight を再実行
  3. 同じ payload を再送

  **その他の失敗:**
  1. agent/model を再初期化
  2. Step 1 preflight を再実行
  3. 同じ payload を再送

Payload:
{ ...ready-to-paste JSON... }
```

**なぜ？** ツール不安定時でも、ユーザーの作業を止めないため。

> **Values**: 継続は力 / 成長の複利

---

## Common Pitfalls

1. **`/mcp show` だけで健全性判定する**
   修正: 書き込み前に `notion-notion-fetch` を必ず実行。

2. **DS ID をコミット済みファイルに直書きする**
   修正: ローカル環境変数で管理する。

3. **プロパティ名を推測して書く**
   修正: スキーマを fetch して正確な名前を使用。

---

## ベストプラクティス

- すべての write フローで preflight を実行
- Notion手順は基盤スキルに集約
- 失敗時payloadは即貼り付け可能形式にする
- 機密識別子はローカル設定に限定する

## アンチパターン

- preflight 失敗後にそのまま書き込み継続
- 再試行情報なしで「失敗しました」だけ返す
- 各スキルにNotion手順を重複記載する

---

## Quick Reference

### Decision Table

| 状況 | アクション |
|---|---|
| Notionへ書き込みたい | Step 1 preflight を先に実行 |
| DS ID が不明 | Step 2 解決フローを実行 |
| Property error が出た | Step 3 スキーマ確認を再実行 |
| 認証切れ（401 / unauthorized） | `/mcp r` を実行して再認証し、Step 1 からやり直す |
| 実行時にツール失敗（その他） | Step 5 フォールバックを返す |

### 最小チェックリスト

- [ ] preflight fetch 成功
- [ ] DS ID をローカル設定から解決
- [ ] スキーマ確認済み
- [ ] payload が正確なプロパティ名を使用
- [ ] フォールバックpayloadを準備

---

## FAQ

**Q: セッション中に Notion の認証が切れたらどうする？**
A: preflight fetch が "unauthorized" や 401 エラーを返します。ターミナルで `/mcp r` を実行して再認証し、Step 1 からやり直してください。

**Q: なぜ DS ID をリポジトリに書かない？**
A: ワークスペース固有識別子の漏洩を防ぎ、環境依存を減らすため。

**Q: なぜ毎回 preflight が必要？**
A: セッション/agent/model でツール可用性が変動するため。

**Q: MCP とは？**
A: Model Context Protocol の略で、Notion など外部ツール呼び出しの橋渡し。

---

## Resources

- https://developers.notion.com/reference/intro
