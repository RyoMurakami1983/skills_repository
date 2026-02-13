---
name: skill-revision-guide
description: Guide for revising GitHub Copilot agent skills and managing changelogs.
author: RyoMurakami1983
tags: [copilot, agent-skills, revision, maintenance, changelog]
invocable: false
---

# Skill修正ガイド

GitHub Copilot agentスキルの修正、バージョン管理、メンテナンスのためのガイド（変更履歴管理と日英同期対応）。

## When to Use This Skill

このスキルを使用する場面：
- 既存のSKILL.mdファイルを新しいコンテンツや修正で更新する場合
- CHANGELOG.mdに簡潔なエントリーで変更を記録する場合
- 英語版SKILL.mdと日本語版を同期する場合
- スキルバージョンと後方互換性を管理する場合
- authorメタデータでシステム作成スキルを識別する場合

---

## Related Skills

- **`skills-author-skill`** - スキル執筆標準を参照
- **`skills-validate-skill`** - 公開前に修正内容を検証
- **`skills-generate-skill-template`** - 新しいスキルを生成

---

## Core Principles

1. **Changelog規律** - 実質的な変更を1行形式で記録（基礎と型）
2. **日英同期** - 常に英語版と日本語版の両方を更新（温故知新）
3. **著者追跡** - authorフィールドでシステムスキルを検出（ニュートラル）
4. **知識基盤** - 改訂履歴を蓄積し複利的成長へ（成長の複利）

---

## ワークフロー: スキルの改訂とバージョン管理

### Step 1: システム作成スキルの検出

YAML frontmatterの`author: RyoMurakami1983`を確認し、スキルの出自を判定する。システム作成スキルは強化メンテナンス（日英同期 + changelog）が必要。サードパーティスキルは標準的な改訂を適用。

```python
import yaml

def is_system_skill(skill_path: Path) -> bool:
    content = skill_path.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return False
    end = content.find('---', 3)
    frontmatter = yaml.safe_load(content[3:end])
    return frontmatter.get('author') == 'RyoMurakami1983'
```

**実行タイミング**: 常に最初に実行 — EN/JA同期とCHANGELOGチェックの適用可否を決定。

| スキルタイプ | 検出方法 | 改訂サポート |
|------------|-----------|------------------|
| システム作成 | `author: RyoMurakami1983` | 強化: EN/JA同期 + CHANGELOG |
| サードパーティ | 著者なしまたは異なる | 標準: 英語版のみ |
| 不明 | frontmatterなし | 最小限: frontmatter追加を提案 |

---

### Step 2: 変更の重要度を分類

変更が実質的（記録対象）か些細（記録不要）かを判断する。焦点を絞ったchangelogはノイズを防ぎ、意味のある更新を見つけやすくする。

**実質的**（記録）: 新セクション、バグ修正、API変更、フレームワーク更新、明確化。
**些細**（スキップ）: タイポ、空白、文法、句読点。

```python
SUBSTANTIAL_KEYWORDS = ['added', 'removed', 'changed', 'fixed', 'deprecated', 'breaking']
TRIVIAL_MARKERS = ['typo', 'spelling', 'grammar', 'whitespace']

def is_substantial(description: str) -> bool:
    desc = description.lower()
    if any(k in desc for k in TRIVIAL_MARKERS):
        return False
    return any(k in desc for k in SUBSTANTIAL_KEYWORDS)
```

**実行タイミング**: CHANGELOGエントリーを書く前に — すべてのログ記録をこのチェックで制御。

| 変更タイプ | 記録? | 例 |
|-------------|------|---------|
| コンテンツ追加/削除 | ✅ Yes | "Added: Circuit Breakerステップ" |
| 機能変更 | ✅ Yes | "Changed: Sync → Asyncパターン" |
| バグ修正 | ✅ Yes | "Fixed: メモリリーク" |
| タイポ/文法 | ❌ No | "performace" → "performance" |
| 書式設定 | ❌ No | インデント、改行 |

---

### Step 3: CHANGELOG.mdの更新

実質的な変更ごとに1行エントリーで、簡潔でスキャン可能なchangelogを維持する。カテゴリ接頭辞を使用し、ISO日付のバージョンごとにグループ化。

```markdown
# Changelog

## Version 1.2.0 (2026-02-15)

- Changed: Sync method → Async/await pattern for API calls
- Added: Step 8 - Circuit Breaker implementation
- Fixed: Memory leak in ViewModelBase.Dispose()

## Version 1.1.0 (2026-01-20)

- Added: Step 7 - Retry policies with Polly
- Deprecated: Old ConfigureServices method

## Version 1.0.0 (2026-01-01)

- Initial release
```

**形式ルール**: カテゴリ接頭辞（Added/Changed/Fixed/Removed/Deprecated/Updated）+ 1行説明（最大100文字）+ バージョンごとにグループ化（YYYY-MM-DD）。

**実行タイミング**: 実質的な変更の後。スキルのバージョンが5以上、またはchangelogが50行を超えたらCHANGELOG.mdを分離。

---

### Step 4: 英語版と日本語版の同期

システムスキルでは、SKILL.mdとreferences/SKILL.ja.mdを同期させる。意味に影響する変更、セクションの追加/削除、コード例の変更時に両方を更新。

| 変更タイプ | 同期必要? | 理由 |
|-------------|---------------|-----|
| セクション追加 | ✅ Yes | 構造が一致する必要がある |
| コード例変更 | ✅ Yes | 技術コンテンツが変更された |
| 言い回し改善 | ⚠️ Maybe | 意味が変わった場合のみ |
| タイポ修正 | ❌ No | 両バージョンにある場合を除く |

**英語版SKILL.md編集後の同期チェックリスト**:
- [ ] セクション数が一致（EN = JA）
- [ ] ステップタイトルが同一
- [ ] コードブロック数が類似（±2許容）
- [ ] 表の列が一致

**実行タイミング**: システムスキル（`author: RyoMurakami1983`）に実質的な英語の変更があるたび。

---

### Step 5: バージョン番号の更新

変更の重要度に基づいてセマンティックバージョニング（MAJOR.MINOR.PATCH）を適用。frontmatterとCHANGELOGのバージョンを更新。

| 変更タイプ | バージョンアップ | 例 |
|-------------|--------------|---------|
| 破壊的変更 | MAJOR (2.0.0) | 非同期シグネチャへ変更 |
| 新機能/ステップ | MINOR (1.3.0) | Step 8を追加 |
| バグ修正 | PATCH (1.2.1) | メモリリークを修正 |
| タイポ修正 | (なし) | 些細な変更ではアップしない |

**実行タイミング**: すべての変更適用とchangelog更新の後。各バージョンアップ = 1つのアトミックコミット。

---

### Step 6: 古いスキルの検出

経過時間に基づいて更新が必要なスキルを積極的に特定。changelogから最新バージョンの日付を解析し、古いスキルをレビュー対象としてフラグ。

```python
import re
from datetime import datetime

def check_freshness(skill_path: Path) -> str:
    content = skill_path.read_text(encoding='utf-8')
    match = re.search(r'## Version.*?\((\d{4}-\d{2}-\d{2})\)', content)
    if not match:
        return "unknown - add changelog"
    age = (datetime.now() - datetime.strptime(match.group(1), '%Y-%m-%d')).days
    if age > 180: return f"stale ({age}d) - review needed"
    if age > 90:  return f"aging ({age}d) - consider review"
    return f"fresh ({age}d)"
```

**実行タイミング**: 四半期メンテナンス時、または一括改訂の前。

| 経過日数 | ステータス | アクション |
|-----|--------|--------|
| < 90日 | Fresh | 対応不要 |
| 90-180日 | Aging | レビュー検討 |
| > 180日 | Stale | 更新をレビュー |

---

### Step 7: スキルの一括改訂

1回のセッションで複数のスキルを改訂し、一貫性を確保。すべてのスキルに同じ基準を適用：システムスキル検出、変更適用、JA版同期、changelog更新、検証。

```python
def batch_revise(skill_paths: list[Path], description: str):
    for path in skill_paths:
        is_system = is_system_skill(path)
        apply_revision(path)
        if is_system:
            ja = path.parent / "references" / "SKILL.ja.md"
            if ja.exists():
                apply_revision(ja, language='ja')
        update_changelog(path, description)
        score = run_validation(path)
        status = "PASS" if score >= 80 else "FAIL"
        print(f"{path.name}: {score:.0f}% ({status})")
```

**実行タイミング**: フレームワーク/ライブラリの横断更新、スタイル統一、繰り返し問題の修正、四半期メンテナンス。

---

## Best Practices

1. **システムスキルを検出** - `author: RyoMurakami1983`フィールドをプログラム的に使用
2. **実質的な変更のみ記録** - タイポ、書式設定はスキップ。コンテンツ/機能の変更を記録
3. **1行Changelog** - "カテゴリ: 簡潔な説明（最大100文字）"
4. **EN/JA同期** - システムスキルでは常に両バージョンを更新
5. **CHANGELOG.md分離** - 50行を超えたらSKILL.mdから移動
6. **セマンティックバージョニング** - 変更タイプに基づくMAJOR.MINOR.PATCH
7. **改訂後に検証** - 公開前に品質チェックを実行
8. **アトミックにコミット** - 各バージョンアップ = 1つのコミット
9. **後方互換性** - 機能を削除する前に非推奨化

---

## Common Pitfalls

- **日本語版の更新忘れ**: 英語版SKILL.md編集後、常に`references/SKILL.ja.md`の存在を確認し更新する。対策: 改訂ワークフローにJAチェックを追加。
- **些細な変更のログ記録**: タイポ/書式修正でCHANGELOGを散らかさない。対策: すべてのエントリーを`is_substantial()`チェックで制御。
- **システムスキルリストのハードコード**: システムスキルの手動リストを維持しない。対策: `author`フロントマターフィールドでプログラム的に検出。

---

## Anti-Patterns

### 1. すべての変更をログに記録

**問題**: 些細なエントリー（タイポ、インデント）が意味のある更新を埋没させる。

```python
# ❌ changelog.append("Fixed: typo in line 42")
# ✅ 実質的な変更のみ: changelog.append(f"Changed: {before} → {after}")
```

### 2. 日英同期の怠慢

**問題**: 英語版のみ更新すると、日本語ユーザー向けドキュメントにずれが生じる。

```python
# ❌ update_file("SKILL.md", content)  # JA版を忘れた！
# ✅ update_file("SKILL.md", en); update_file("references/SKILL.ja.md", ja)
```

---

## Quick Reference

```
1. SKILL.mdを開く → authorフィールドを確認
   ├─ author: RyoMurakami1983 → システムスキル（強化）
   └─ その他/なし → 標準改訂

2. 英語版SKILL.mdに変更を加える

3. 実質的な変更？
   ├─ Yes → CHANGELOG.mdを更新 + 続行
   └─ No（タイポ/書式） → ステップ6へスキップ

4. システムスキルの場合 → references/SKILL.ja.mdを更新

5. バージョンアップ（破壊的→MAJOR、機能→MINOR、修正→PATCH）

6. skills-validate-skillを実行 → コミット
```

**システムスキル**（`author: RyoMurakami1983`）: EN/JA同期 + CHANGELOG + 強化検証。
**非システムスキル**: 英語版のみ + 標準changelog + 基本検証。

---

## Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [skills-validate-skill](../skills-validate-skill/SKILL.md) - 改訂を検証
- [CHANGELOG_TEMPLATE.md](assets/CHANGELOG_TEMPLATE.md) - Changelogテンプレート

---

## Changelog

### Version 2.0.0 (2026-02-15)
- Changed: マルチパターン形式 → 7ステップの単一ワークフローへ移行
- Removed: 冗長なコードブロック（本質的なロジックに圧縮）
- Changed: Best Practices SummaryをBest Practicesに統合
- Changed: Common Pitfallsを箇条書き形式に圧縮

### Version 1.0.0 (2026-02-12)
- 初回リリース
- 著者ベースのシステムスキル検出
- CHANGELOG.md形式仕様
- EN/JA同期パターン
- バージョンアップ戦略

<!-- 
English version available at ../SKILL.md
英語版は ../SKILL.md を参照してください
-->
