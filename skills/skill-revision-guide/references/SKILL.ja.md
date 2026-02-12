---
name: skill-revision-guide
description: Guide for revising and maintaining GitHub Copilot agent skills. Use when updating existing SKILL.md files, managing changelogs, keeping English-Japanese versions synchronized, or identifying skills needing updates. Enhanced support for skills with author RyoMurakami1983.
author: RyoMurakami1983
tags: [copilot, agent-skills, revision, maintenance, changelog]
invocable: false
---

# Skill修正ガイド

GitHub Copilot agentスキルの修正、メンテナンス、バージョン管理のための包括的なガイド（変更履歴管理と日英同期対応）。

## Related Skills

- **`skill-writing-guide`** - スキル執筆標準を参照
- **`skill-quality-validation`** - 公開前に修正内容を検証
- **`skill-template-generator`** - 新しいスキルを生成

## When to Use This Skill

このスキルを使用する場面：
- 既存のSKILL.mdファイルを新しいコンテンツや修正で更新する場合
- CHANGELOG.mdに簡潔な1行エントリーで変更を記録する場合
- 英語版SKILL.mdと日本語版references/SKILL.ja.mdを同期する場合
- このシステムが作成したスキル（`author: RyoMurakami1983`）を識別する場合
- 変更が実質的（changelog記録が必要）か些細（タイポ修正）かを判断する場合
- スキルバージョンを管理し、後方互換性を維持する場合

---

## Core Principles

1. **簡潔なChangelog** - 実質的な変更のみを1行形式で記録: "Changed: [変更前] → [変更後]"
2. **英語-日本語同期** - システム作成スキルを修正する際は常に両バージョンを更新
3. **実質的な変更のみ** - コンテンツ/機能の変更をログに記録。タイポや書式設定はスキップ
4. **著者ベースの検出** - `author: RyoMurakami1983`を使用してシステムスキルを識別し、強化サポートを提供
5. **CHANGELOG.mdの分離** - changelogが大きくなったらSKILL.mdからCHANGELOG.mdへ移動

---

## Pattern 1: システム作成スキルの識別

### Overview

YAML frontmatterの`author: RyoMurakami1983`を通じて、このシステムが作成したスキルを検出し、ターゲットを絞った修正サポートを提供します。

### Basic Example

```python
# ✅ CORRECT - システム作成スキルの検出
import yaml

def is_system_skill(skill_path: Path) -> bool:
    """このシステムがスキルを作成したかをチェック"""
    content = skill_path.read_text(encoding='utf-8')
    
    # YAML frontmatterを抽出
    if not content.startswith('---'):
        return False
    
    end_index = content.find('---', 3)
    if end_index == -1:
        return False
    
    frontmatter_text = content[3:end_index]
    frontmatter = yaml.safe_load(frontmatter_text)
    
    return frontmatter.get('author') == 'RyoMurakami1983'

# 使用例
if is_system_skill(Path("~/.copilot/skills/my-skill/SKILL.md")):
    print("✅ システムスキルを検出 - 強化修正サポートを適用")
    print("  - references/SKILL.ja.mdの同期をチェック")
    print("  - CHANGELOG.mdの存在を確認")
else:
    print("ℹ️ 非システムスキル - 標準修正サポートを適用")
```

### When to Use

| スキルタイプ | 検出 | 修正サポート |
|------------|-----------|------------------|
| システム作成 | `author: RyoMurakami1983` | 強化: EN/JA同期 + CHANGELOG |
| サードパーティ | 著者なしまたは異なる | 標準: 英語版のみ |
| 不明 | frontmatterなし | 最小限: frontmatterの追加を提案 |

### With Configuration

```python
# ✅ CORRECT - システムスキル向けの強化修正
class SkillRevisionAssistant:
    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.is_system_skill = self._detect_system_skill()
    
    def _detect_system_skill(self) -> bool:
        """システム作成スキルかどうかを検出"""
        # ... (上記の検出ロジック)
        pass
    
    def revise(self, changes: dict):
        """適切なサポートレベルで修正を適用"""
        if self.is_system_skill:
            self._revise_with_enhanced_support(changes)
        else:
            self._revise_standard(changes)
    
    def _revise_with_enhanced_support(self, changes: dict):
        """システムスキル向けの強化修正"""
        # 1. 英語版に変更を適用
        self._apply_changes_to_english(changes)
        
        # 2. 日本語版をチェック
        ja_path = self.skill_path.parent / "references" / "SKILL.ja.md"
        if ja_path.exists():
            print("⚠️ 日本語版を検出")
            print(f"   references/SKILL.ja.mdを英語版の変更に合わせて更新してください")
            self._suggest_japanese_updates(changes)
        else:
            print("ℹ️ 日本語版が見つかりません - 英語版のみ修正")
        
        # 3. CHANGELOG.mdを更新
        if self._is_substantial_change(changes):
            self._update_changelog(changes)
        
        # 4. 品質検証を実行
        print("✅ 品質検証を実行中...")
        # skill-quality-validationを呼び出し
```

---

## Pattern 2: 実質的な変更の記録

### Overview

変更が実質的（ログ記録が必要）か些細（ログスキップ）かを判断します。

### Basic Example

**実質的な変更**（これらをログ記録）：
- 新しいパターンセクションを追加
- コード例の重大なバグを修正
- APIシグネチャを変更
- 新しいフレームワークバージョンへ更新
- 曖昧なセクションを明確化

**些細な変更**（ログ記録しない）：
- タイポを修正（"performace" → "performance"）
- 空白文字/書式設定を調整
- 文法を修正
- 欠けているカンマを追加
- 句読点を更新

### When to Use

このパターンを使用して、CHANGELOG.mdエントリーが必要かどうかを判断します。

| 変更タイプ | ログ? | 例 |
|-------------|------|---------|
| コンテンツの追加/削除 | ✅ Yes | "Added Pattern 8: Circuit Breaker" |
| 機能変更 | ✅ Yes | "Changed: Sync method → Async/await pattern" |
| バグ修正 | ✅ Yes | "Fixed: Memory leak in ViewModelBase" |
| タイポ/文法 | ❌ No | "performace" → "performance" |
| 書式設定 | ❌ No | インデント、改行 |

### With Configuration

```python
# ✅ CORRECT - 実質的な変更の検出器
import difflib

class ChangeAnalyzer:
    TRIVIAL_PATTERNS = [
        r'^\s+',  # 空白文字のみ
        r'^[.,;:!?]',  # 句読点のみ
        r'typo|spelling|grammar',  # 明示的なマーカー
    ]
    
    SUBSTANTIAL_KEYWORDS = [
        'added', 'removed', 'changed', 'fixed', 'updated',
        'improved', 'refactored', 'deprecated', 'breaking'
    ]
    
    def is_substantial(self, before: str, after: str, description: str = "") -> bool:
        """変更が実質的かどうかを判断"""
        # 明示的な説明をチェック
        desc_lower = description.lower()
        if any(keyword in desc_lower for keyword in self.SUBSTANTIAL_KEYWORDS):
            return True
        
        if any(re.search(pattern, desc_lower) for pattern in self.TRIVIAL_PATTERNS):
            return False
        
        # コンテンツを比較
        diff = difflib.unified_diff(
            before.split('\n'),
            after.split('\n'),
            lineterm=''
        )
        changes = list(diff)
        
        # 10行以上の変更があれば、おそらく実質的
        if len([l for l in changes if l.startswith('+') or l.startswith('-')]) > 10:
            return True
        
        # 構造的変更をチェック（見出し、コードブロック）
        before_structure = self._extract_structure(before)
        after_structure = self._extract_structure(after)
        
        return before_structure != after_structure
    
    def _extract_structure(self, content: str) -> list:
        """見出しとコードブロックマーカーを抽出"""
        return [
            line.strip() for line in content.split('\n')
            if line.startswith('#') or line.startswith('```')
        ]

# 使用例
analyzer = ChangeAnalyzer()

# 実質的な変更
if analyzer.is_substantial(
    before="public void DoSync()",
    after="public async Task DoAsync()",
    description="Changed to async method"
):
    print("✅ この変更をCHANGELOG.mdに記録")

# 些細な変更
if not analyzer.is_substantial(
    before="performace improvements",
    after="performance improvements",
    description="typo fix"
):
    print("ℹ️ 些細な修正のためCHANGELOG.mdをスキップ")
```

---

## Pattern 3: CHANGELOG.md形式

### Overview

各実質的な変更に対して1行エントリーで、簡潔でスキャン可能なchangelogを維持します。

### Basic Example

**CHANGELOG.md**:
```markdown
# Changelog

## Version 1.2.0 (2026-02-15)

- Changed: Sync method → Async/await pattern for API calls（API呼び出しに同期メソッド → Async/awaitパターンへ変更）
- Added: Pattern 8 - Circuit Breaker implementation（Pattern 8 - サーキットブレーカー実装を追加）
- Fixed: Memory leak in ViewModelBase.Dispose()（ViewModelBase.Dispose()のメモリリークを修正）
- Updated: Examples to .NET 8（例を.NET 8へ更新）

## Version 1.1.0 (2026-01-20)

- Added: Pattern 7 - Retry policies with Polly（Pattern 7 - Pollyを使用したリトライポリシーを追加）
- Changed: DI configuration → Minimal API style（DI構成 → Minimal APIスタイルへ変更）
- Deprecated: Old ConfigureServices method（古いConfigureServicesメソッドを非推奨化）

## Version 1.0.0 (2026-01-01)

- Initial release（初回リリース）
```

**形式ルール**：
- **カテゴリ接頭辞**: "Added", "Changed", "Fixed", "Removed", "Deprecated", "Updated"
- **1行説明**: 簡潔な変更前 → 変更後、または行った内容
- **1行あたり最大100文字**
- **バージョンごとにグループ化** - 日付はYYYY-MM-DD形式

### When to Use

CHANGELOG.mdを使用する場合：
- スキルに5つ以上のバージョンがある
- SKILL.md内のchangelogが50行を超える
- 複数の貢献者が変更追跡を必要としている

### With Configuration

```python
# ✅ CORRECT - Changelogマネージャー
from datetime import date
from enum import Enum

class ChangeType(Enum):
    ADDED = "Added"
    CHANGED = "Changed"
    FIXED = "Fixed"
    REMOVED = "Removed"
    DEPRECATED = "Deprecated"
    UPDATED = "Updated"

class ChangelogManager:
    def __init__(self, skill_path: Path):
        self.changelog_path = skill_path.parent / "CHANGELOG.md"
        self.current_version = self._get_current_version()
    
    def add_entry(self, change_type: ChangeType, description: str):
        """新しいchangelogエントリーを追加"""
        if not self.changelog_path.exists():
            self._create_changelog()
        
        entry = f"- {change_type.value}: {description}"
        
        # 現在のバージョンセクションに挿入
        content = self.changelog_path.read_text(encoding='utf-8')
        version_header = f"## Version {self.current_version}"
        
        if version_header in content:
            # 既存のバージョンに追加
            lines = content.split('\n')
            insert_index = None
            for i, line in enumerate(lines):
                if line.strip() == version_header:
                    # バージョンヘッダー後の次の空行を見つける
                    insert_index = i + 2  # バージョン行と日付行をスキップ
                    break
            
            if insert_index:
                lines.insert(insert_index, entry)
                content = '\n'.join(lines)
        else:
            # 新しいバージョンセクションを作成
            new_section = f"\n## Version {self.current_version} ({date.today()})\n\n{entry}\n"
            content = content.replace("# Changelog\n", f"# Changelog\n{new_section}")
        
        self.changelog_path.write_text(content, encoding='utf-8')
        print(f"✅ CHANGELOG.mdに追加: {entry}")
    
    def _create_changelog(self):
        """新しいCHANGELOG.mdを作成"""
        template = f"""# Changelog

このスキルのすべての重要な変更はこのファイルに記録されます。

## Version {self.current_version} ({date.today()})

- Initial version

"""
        self.changelog_path.write_text(template, encoding='utf-8')

# 使用例
manager = ChangelogManager(Path("~/.copilot/skills/my-skill/SKILL.md"))
manager.add_entry(
    ChangeType.CHANGED,
    "Sync method → Async/await pattern for API calls"
)
manager.add_entry(
    ChangeType.FIXED,
    "Memory leak in ViewModelBase.Dispose()"
)
```

---

## Pattern 4: 英語-日本語同期

### Overview

システム作成スキルを修正する際、英語版SKILL.mdと日本語版references/SKILL.ja.mdを同期させます。

### Basic Example

**同期ワークフロー**：
1. 英語版SKILL.mdを編集
2. 変更されたセクションを特定
3. references/SKILL.ja.mdの対応するセクションを更新
4. 両方のバージョンが同じ構造を持つことを確認（セクション数、順序）

### When to Use

以下の場合に同期：
- システムスキル（`author: RyoMurakami1983`）を修正している
- コンテンツの変更が意味に影響する（単なる言い回しの変更ではない）
- 新しいセクションが追加または削除された
- 異なるコードで例が更新された

| 変更タイプ | 同期必要? | 理由 |
|-------------|---------------|-----|
| セクション追加 | ✅ Yes | 構造が一致する必要がある |
| コード例変更 | ✅ Yes | 技術的なコンテンツが変更された |
| 言い回し改善 | ⚠️ Maybe | 意味が変わった場合はYes |
| タイポ修正 | ❌ No | 両方のバージョンにある場合を除く |

### Manual Sync Checklist

**英語版SKILL.mdを編集後、確認**：

- [ ] セクション数が一致（EN: 8セクション = JA: 8セクション）
- [ ] パターンタイトルが同一（例: "## Pattern 4:"）
- [ ] コードブロック数が類似（±2ブロックは許容）
- [ ] 例が構造的に整列
- [ ] 表の列が一致

> 📚 **自動同期チェッカー**: 詳細な同期ガイドとPython実装については[references/sync-checker.md](references/sync-checker.md)を参照してください。

---

## Pattern 5: バージョンアップ戦略

### Overview

変更の重要性に基づいて、いつバージョン番号をインクリメントするかを決定します。

### Basic Example

**セマンティックバージョニング**: MAJOR.MINOR.PATCH（例: 1.2.3）

- **MAJOR** (1.x.x): 破壊的変更、互換性のないAPI変更
- **MINOR** (x.1.x): 新機能、後方互換性のある追加
- **PATCH** (x.x.1): バグ修正、タイポ、マイナーな改善

### When to Use

| 変更タイプ | バージョンアップ | 例 |
|-------------|--------------|---------|
| 破壊的変更 | MAJOR | 非同期シグネチャへ変更 |
| 新パターン追加 | MINOR | Pattern 8を追加 |
| バグ修正 | PATCH | メモリリークを修正 |
| タイポ修正 | (なし) | 些細な変更ではアップしない |

### Decision Helper

**クイックガイド**：

```python
# 破壊的変更? → MAJOR
"Changed: sync method → async/await (incompatible)"  # → 2.0.0

# 新機能? → MINOR
"Added: Pattern 8 - Circuit Breaker"  # → 1.3.0

# バグ修正? → PATCH
"Fixed: Memory leak in example"  # → 1.2.1

# タイポ? → アップなし
"Fixed typo: 'performace' → 'performance'"  # → 1.2.0 (変更なし)
```

> 📚 **詳細なバージョニングルール**: 包括的なセマンティックバージョニングガイド、非推奨化戦略、CHANGELOGベストプラクティスについては[references/versioning-guide.md](references/versioning-guide.md)を参照してください。

---

## Common Pitfalls

### 1. 日本語版の更新を忘れる

**問題**: 英語版SKILL.mdを修正したが、references/SKILL.ja.mdの更新を忘れ、同期のずれが発生。

**解決策**: 英語版を編集した後、常に日本語版をチェック。

```python
# ✅ CORRECT - JA版の自動チェック
def revise_skill(skill_path: Path, changes: dict):
    # 英語版に変更を適用
    apply_changes(skill_path, changes)
    
    # 日本語版をチェック
    ja_path = skill_path.parent / "references" / "SKILL.ja.md"
    if ja_path.exists():
        print("⚠️ 警告: 日本語版が存在します")
        print("   references/SKILL.ja.mdを同等の変更で更新することを忘れずに")
        print("\n変更されたセクション:")
        for section in changes.get('sections', []):
            print(f"  - {section}")
```

### 2. 些細な変更をログに記録する

**問題**: CHANGELOG.mdがタイポ修正や書式設定の変更で雑然とする。

**解決策**: 実質的な変更のみをログに記録。

```markdown
❌ 間違ったCHANGELOG:
## Version 1.2.1
- Fixed: typo "performace" → "performance"
- Updated: indentation in code block
- Changed: comma placement
- Fixed: typo "recieve" → "receive"

✅ 正しいCHANGELOG:
## Version 1.2.0
- Changed: Sync method → Async/await pattern
- Added: Pattern 8 - Circuit Breaker
- Fixed: Memory leak in ViewModelBase
```

### 3. authorフィールドを検出に使用しない

**問題**: システム作成とサードパーティのスキルを手動で追跡。

**解決策**: `author: RyoMurakami1983`フィールドをプログラム的に使用。

```python
# ❌ WRONG - 手動追跡
SYSTEM_SKILLS = ["skill-writing-guide", "skill-quality-validation"]  # ハードコード

# ✅ CORRECT - 自動検出
def is_system_skill(path: Path) -> bool:
    frontmatter = extract_frontmatter(path)
    return frontmatter.get('author') == 'RyoMurakami1983'
```

---

## Quick Reference

### 修正ワークフロー

```
1. 修正するSKILL.mdを開く

2. authorフィールドをチェック
   ├─ author: RyoMurakami1983? → システムスキル（強化サポート）
   └─ その他/なし → 標準修正

3. 英語版SKILL.mdに変更を加える

4. 変更は実質的?
   ├─ Yes（コンテンツ/機能） → 続行
   └─ No（タイポ/書式） → ステップ7へスキップ

5. CHANGELOG.mdを更新
   - カテゴリ: Added/Changed/Fixed/等
   - 説明: 1行サマリー（最大100文字）

6. システムスキルの場合: references/SKILL.ja.mdをチェック
   ├─ 存在 → 日本語版を更新
   └─ なし → 英語版のみ

7. skill-quality-validationを実行

8. frontmatterのバージョンをアップ
   - 破壊的? → MAJOR
   - 機能? → MINOR
   - バグ修正? → PATCH

9. 変更をコミット
```

### システムスキルインジケーター

✅ **システムスキル**（`author: RyoMurakami1983`）：
- references/SKILL.ja.mdをチェック
- CHANGELOG.mdが存在することを確認（5バージョン以上の場合）
- 英語版と日本語版を同期
- 強化検証

ℹ️ **非システムスキル**：
- 英語版のみ修正
- 標準changelog（SKILL.md内）
- 基本検証

---

## Best Practices Summary

1. **システムスキルを検出** - `author: RyoMurakami1983`フィールドをプログラム的に使用
2. **実質的なもののみをログ** - タイポ、書式設定はスキップ。コンテンツ/機能の変更を記録
3. **1行Changelog** - "カテゴリ: 簡潔な説明（最大100文字）"
4. **EN/JA同期** - システムスキルでは常に両方のバージョンを更新
5. **CHANGELOG.md** - 50行を超えたらSKILL.mdから移動
6. **セマンティックバージョニング** - 変更タイプに基づくMAJOR.MINOR.PATCH
7. **修正後に検証** - 公開前に品質チェックを実行
8. **アトミックにコミット** - 各バージョンアップ = 1つのコミット
9. **変更を参照** - changelogで関連issue/PRにリンク
10. **後方互換性** - 機能を削除する前に非推奨化

---

## Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [skill-quality-validation](../skill-quality-validation/SKILL.md) - 修正を検証
- [CHANGELOG_TEMPLATE.md](assets/CHANGELOG_TEMPLATE.md) - Changelogテンプレート

---

## Changelog

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
