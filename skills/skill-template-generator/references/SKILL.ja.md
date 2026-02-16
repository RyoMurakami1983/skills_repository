<!-- 
このテンプレートはSKILL.md単一ファイルで完結する設計です。
注意: 実際のskillでは7-10個のパターンセクションを含めてください。
-->

---
name: skill-template-generator
description: Generate structured SKILL.md templates for GitHub Copilot agent skills. Use when starting a new skill from scratch or creating skill boilerplate.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, templates, generator, scaffolding]
  invocable: false
---

# Skill Template Generator

GitHub Copilot エージェントスキル用の構造化されたSKILL.mdテンプレートを自動生成します。適切なフォーマット、セクション、ボイラープレートコードを含みます。

## Related Skills

- **`skill-writing-guide`** - スキル執筆のベストプラクティスを学ぶ
- **`skill-quality-validation`** - 生成されたスキルを検証する
- **`skills-revise-skill`** - 生成されたスキルを改訂する

## When to Use This Skill

このスキルを使用する場面：
- 新しいスキルをゼロから開始する
- 必須セクションを含む標準的なSKILL.md構造が必要
- 英語版と日本語版を同時に生成したい
- 適切なYAML frontmatterを含むスキルボイラープレートを設定する
- GitHub Copilot/Claude仕様に準拠したスキルを作成する
- システム作成スキルに`author: RyoMurakami1983`を含める必要がある

---

## Core Principles

1. **標準準拠** - デフォルトで品質検証に合格するテンプレートを生成
2. **バイリンガルサポート** - 英語版（SKILL.md）と日本語版（references/SKILL.ja.md）の両方を作成
3. **カスタマイズ可能** - スキル名、説明、タグ、パターン数をユーザーが指定可能
4. **著者の帰属** - 追跡のため`author: RyoMurakami1983`を自動的に含める
5. **記入準備完了** - コンテンツ作成をガイドするプレースホルダーと例を提供

---

## Pattern 1: 基本的なテンプレート生成

### Overview

必須セクションとYAML frontmatterを含む最小限のSKILL.mdを生成します。

### Basic Example

```bash
# 基本テンプレートの生成
Skill Name: my-new-skill
Description: Brief description of what this skill does
Tags: tag1, tag2, tag3

# 出力:
# ~/.copilot/skills/my-new-skill/SKILL.md が作成されました
```

**生成される構造**:
```yaml
---
name: my-new-skill
description: Brief description of what this skill does
author: RyoMurakami1983
tags: [tag1, tag2, tag3]
invocable: false
---

# My New Skill

## Related Skills
[Placeholders]

## When to Use This Skill
[5-8 scenarios - to be filled]

## Core Principles
[3-5 principles - to be filled]

## Pattern 1-7: [Pattern Names]
[Sections to be filled]

## Common Pitfalls
[3-5 items - to be filled]

## Anti-Patterns
[2-4 items - to be filled]

## Quick Reference
[Decision tree or table - to be filled]

## Best Practices Summary
[5-10 items - to be filled]

## Resources
[Links - to be filled]

## Changelog
### Version 1.0.0 (YYYY-MM-DD)
- Initial version
```

### When to Use

| シナリオ | テンプレートタイプ | 理由 |
|----------|--------------|-----|
| 全く新しいスキル | 基本テンプレート | 構造から始めて内容を埋める |
| 既存のものに類似 | クローン+修正 | 実証済みの構造を再利用 |
| クイックプロトタイプ | 最小限テンプレート | アイデアを素早くテスト |

### With Configuration

```python
# ✅ CORRECT - オプション付きテンプレートジェネレーター
from pathlib import Path
from datetime import date

class SkillTemplateGenerator:
    def __init__(self, skill_name: str, description: str, tags: list):
        self.skill_name = skill_name
        self.description = description
        self.tags = tags
        self.output_dir = Path.home() / ".copilot" / "skills" / skill_name
    
    def generate(self, pattern_count: int = 7, include_japanese: bool = True):
        """SKILL.mdテンプレートを生成"""
        # ディレクトリを作成
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "references").mkdir(exist_ok=True)
        
        # 英語版を生成
        skill_md = self._generate_skill_md(pattern_count)
        (self.output_dir / "SKILL.md").write_text(skill_md, encoding='utf-8')
        
        # 日本語版を生成
        if include_japanese:
            skill_ja = self._generate_skill_ja_md(pattern_count)
            (self.output_dir / "references" / "SKILL.ja.md").write_text(
                skill_ja, encoding='utf-8'
            )
        
        print(f"✅ テンプレートが生成されました: {self.output_dir}")
    
    def _generate_skill_md(self, pattern_count: int) -> str:
        """英語版SKILL.mdの内容を生成"""
        tags_str = ", ".join(self.tags)
        today = date.today().strftime("%Y-%m-%d")
        
        content = f"""---
name: {self.skill_name}
description: {self.description}
author: RyoMurakami1983
tags: [{tags_str}]
invocable: false
---

# {self._title_case(self.skill_name)}

[Brief introduction to this skill]

## Related Skills

- **`skill-name-1`** - How it relates
- **`skill-name-2`** - How it relates

## When to Use This Skill

Use this skill when:
- Scenario 1 - Action-oriented description (50-100 chars)
- Scenario 2 - Problem domain description
- Scenario 3 - Team/workflow scenario
- Scenario 4 - Technical decision point
- Scenario 5 - Implementation use case

---

## Core Principles

1. **Principle 1** - One-line summary of key concept
2. **Principle 2** - One-line summary of key concept
3. **Principle 3** - One-line summary of key concept

---

"""
        # パターンセクションを追加
        for i in range(1, pattern_count + 1):
            content += self._generate_pattern_section(i)
        
        # 残りのセクションを追加
        content += """
## Common Pitfalls

### 1. Pitfall Name - Brief Description

**Problem**: What users typically do wrong.

```csharp
// ❌ WRONG
```

**Solution**: How to fix it.

```csharp
// ✅ CORRECT
```

---

## Anti-Patterns

### Architectural Anti-Pattern Name

**What**: Description of the anti-pattern.

**Why It's Wrong**:
- Reason 1
- Reason 2

**Better Approach**:

```csharp
// ✅ CORRECT
```

---

## Quick Reference

### Decision Tree

```
Start: What do you need?
├─► Need A? → Use Pattern 1
├─► Need B? → Use Pattern 2
└─► Need C? → Use Pattern 3
```

---

## Best Practices Summary

1. **Practice 1** - Brief description
2. **Practice 2** - Brief description
3. **Practice 3** - Brief description

---

## Resources

- [Official Documentation](https://example.com/docs)
- [Related Article](https://example.com/article)

---

## Changelog

### Version 1.0.0 ({today})
- Initial version

<!-- 
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
"""
        return content
    
    def _generate_pattern_section(self, num: int) -> str:
        """パターンセクションテンプレートを生成"""
        return f"""## Pattern {num}: [Pattern Name]

### Overview

Brief explanation of what this pattern solves and why it matters.

### Basic Example

```csharp
// ✅ CORRECT - Simple, most common case
public class Example{num}
{{
    public void DoSomething()
    {{
        // Implementation
    }}
}}
```

### When to Use

- Condition A
- Condition B

### With Configuration

```csharp
// ✅ CORRECT - With options/configuration
```

### Advanced Pattern (Production-Grade)

```csharp
// ✅ CORRECT - Production-ready
```

---

"""
    
    def _title_case(self, kebab_name: str) -> str:
        """kebab-caseをTitle Caseに変換"""
        return " ".join(word.capitalize() for word in kebab_name.split('-'))

# 使用例
generator = SkillTemplateGenerator(
    skill_name="wpf-data-binding",
    description="Advanced WPF data binding patterns with MVVM and validation",
    tags=["wpf", "mvvm", "databinding", "csharp"]
)
generator.generate(pattern_count=8, include_japanese=True)
```

---

## Pattern 2: バイリンガルテンプレート生成

### Overview

適切なディレクトリ構造で英語版と日本語版の両方を同時に生成します。

### Basic Example

**ディレクトリ構造**:
```
my-skill/
├── SKILL.md                   # 英語版（必須）
└── references/
    └── SKILL.ja.md            # 日本語版（オプション）
```

### When to Use

以下の場合は常に日本語版を生成：
- 著者が日本語話者である
- 対象読者に日本人開発者が含まれる
- スキル執筆中の認知負荷を軽減する必要がある

### With Configuration

```python
# ✅ CORRECT - バイリンガルジェネレーター
class BilingualTemplateGenerator(SkillTemplateGenerator):
    def _generate_skill_ja_md(self, pattern_count: int) -> str:
        """日本語版SKILL.ja.mdの内容を生成"""
        tags_str = ", ".join(self.tags)
        today = date.today().strftime("%Y-%m-%d")
        
        content = f"""<!-- 
このテンプレートはSKILL.md単一ファイルで完結する設計です。
注意: 実際のskillでは7-10個のパターンセクションを含めてください。
-->

---
name: {self.skill_name}
description: {self.description}
author: RyoMurakami1983
tags: [{tags_str}]
invocable: false
---

# {self._title_case(self.skill_name)}

[このスキルの簡単な紹介]

## Related Skills

- **`skill-name-1`** - 関連の説明
- **`skill-name-2`** - 関連の説明

## When to Use This Skill

このスキルを使用する場面：
- シナリオ1 - アクション志向の説明（50-100文字）
- シナリオ2 - 問題ドメインの説明
- シナリオ3 - チーム/ワークフローのシナリオ
- シナリオ4 - 技術的な決定ポイント
- シナリオ5 - 実装のユースケース

---

## Core Principles

1. **原則1** - 重要な概念の1行サマリー
2. **原則2** - 重要な概念の1行サマリー
3. **原則3** - 重要な概念の1行サマリー

---
"""
        # 日本語パターンセクションを追加
        for i in range(1, pattern_count + 1):
            content += f"""
## Pattern {i}: [パターン名]

### Overview

このパターンが何を解決するか、なぜ重要かの説明。

### Basic Example

```csharp
// ✅ CORRECT - シンプルで最も一般的なケース
```

### When to Use

- 条件A
- 条件B

### With Configuration

```csharp
// ✅ CORRECT - オプション/設定を使用
```

### Advanced Pattern (Production-Grade)

```csharp
// ✅ CORRECT - 本番グレード
```

---
"""
        
        content += f"""
## Common Pitfalls

### 1. 落とし穴の名前 - 簡単な説明

**Problem**: ユーザーが通常間違えること。

```csharp
// ❌ WRONG
```

**Solution**: 修正方法。

```csharp
// ✅ CORRECT
```

---

## Anti-Patterns

### アーキテクチャアンチパターン名

**What**: アンチパターンの説明。

**Why It's Wrong**:
- 理由1
- 理由2

**Better Approach**:

```csharp
// ✅ CORRECT
```

---

## Quick Reference

### 意思決定ツリー

```
開始: 何が必要ですか？
├─► Aが必要？ → Pattern 1を使用
├─► Bが必要？ → Pattern 2を使用
└─► Cが必要？ → Pattern 3を使用
```

---

## Best Practices Summary

1. **プラクティス1** - 簡単な説明
2. **プラクティス2** - 簡単な説明
3. **プラクティス3** - 簡単な説明

---

## Resources

- [公式ドキュメント](https://example.com/docs)
- [関連記事](https://example.com/article)

---

## Changelog

### Version 1.0.0 ({today})
- 初版

<!-- 
English version available at ../SKILL.md
英語版は ../SKILL.md を参照してください
-->
"""
        return content
```

---

## Pattern 3: 生成されたテンプレートのカスタマイズ

### Overview

生成されたテンプレートを修正して、ドメイン固有のセクションやカスタムパターンを含めます。

### Basic Example

```python
# ✅ CORRECT - カスタムセクションの注入
class CustomTemplateGenerator(SkillTemplateGenerator):
    def __init__(self, *args, custom_sections: list = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_sections = custom_sections or []
    
    def generate(self, **kwargs):
        """カスタムセクション付きで生成"""
        super().generate(**kwargs)
        
        # "Common Pitfalls"の前にカスタムセクションを注入
        skill_path = self.output_dir / "SKILL.md"
        content = skill_path.read_text(encoding='utf-8')
        
        injection_point = content.find("## Common Pitfalls")
        if injection_point != -1:
            custom_content = "\n".join(
                self._format_custom_section(section)
                for section in self.custom_sections
            )
            content = (
                content[:injection_point] +
                custom_content + "\n\n" +
                content[injection_point:]
            )
            skill_path.write_text(content, encoding='utf-8')
    
    def _format_custom_section(self, section: dict) -> str:
        """カスタムセクションをフォーマット"""
        return f"""## {section['title']}

{section['content']}

---
"""

# 使用例
generator = CustomTemplateGenerator(
    skill_name="wpf-custom-controls",
    description="Building custom WPF controls",
    tags=["wpf", "controls", "custom"],
    custom_sections=[
        {
            "title": "Performance Considerations",
            "content": "パフォーマンスに関するカスタムセクション..."
        },
        {
            "title": "Accessibility Guidelines",
            "content": "アクセシビリティに関するカスタムセクション..."
        }
    ]
)
generator.generate()
```

---

## Common Pitfalls

### 1. `author: RyoMurakami1983`の設定忘れ

**Problem**: 生成されたスキルにauthorフィールドが含まれず、追跡できません。

```yaml
# ❌ WRONG - authorフィールドがない
---
name: my-skill
description: My skill description
invocable: false
---
```

**Solution**: 生成されたテンプレートに常にauthorを含めます。

```yaml
# ✅ CORRECT - authorフィールドを含む
---
name: my-skill
description: My skill description
author: RyoMurakami1983  # システム作成スキル
invocable: false
---
```

### 2. パターンセクションが7個未満

**Problem**: デフォルトテンプレートが3パターンのみで、品質検証に合格しません。

**Solution**: pattern_countを7-10に設定します。

```python
# ❌ WRONG
generator.generate()  # デフォルトは3パターン

# ✅ CORRECT
generator.generate(pattern_count=7)  # 品質基準を満たす
```

---

## Anti-Patterns

### テンプレートの過度なカスタマイズ

**What**: 標準構造から大きく逸脱したテンプレートを作成してしまう。

**Why It's Wrong**:
- 他のスキルとの一貫性が失われる
- 品質検証に合格しない可能性がある
- メンテナンスが困難になる

**Better Approach**:

```python
# ✅ CORRECT - 標準構造を維持
# カスタムセクションは控えめに追加
generator = CustomTemplateGenerator(
    skill_name="my-skill",
    description="My skill description",
    tags=["tag1", "tag2"],
    custom_sections=[
        # 1-2個のカスタムセクションのみ
        {"title": "Domain-Specific Section", "content": "..."}
    ]
)
```

---

## Quick Reference

### テンプレート生成ワークフロー

```
1. スキルメタデータを定義
   ├─ 名前（kebab-case）
   ├─ 説明（≤ 100文字）
   └─ タグ（3-5個）

2. ジェネレーターを実行
   ├─ pattern_count: 7-10
   ├─ include_japanese: true
   └─ custom_sections: オプション

3. 出力が作成される
   ├─ SKILL.md（英語）
   └─ references/SKILL.ja.md（日本語）

4. プレースホルダーを埋める
   ├─ [Placeholders]を置き換え
   ├─ コード例を追加
   └─ コンテンツを執筆

5. 検証
   └─ skill-quality-validationを実行
```

### ジェネレーターオプション

| オプション | デフォルト | 目的 |
|--------|---------|---------|
| skill_name | （必須） | ディレクトリとfrontmatterの名前 |
| description | （必須） | YAML descriptionフィールド |
| tags | （必須） | 技術タグ |
| pattern_count | 7 | パターンセクションの数 |
| include_japanese | true | 日本語版を生成 |
| custom_sections | [] | 注入する追加セクション |

---

## Best Practices Summary

1. **常にAuthorを含める** - 追跡のため`author: RyoMurakami1983`を設定
2. **7-10パターンを生成** - 品質検証要件を満たす
3. **バイリンガルで作成** - 英語版と日本語版の両方を生成
4. **assets/のテンプレートを使用** - 公式テンプレートを参照
5. **生成後に検証** - 生成されたスケルトンの品質チェックを実行
6. **すぐに埋める** - プレースホルダーを長く放置しない
7. **バージョン管理** - コンテンツを埋める前にスケルトンをコミット
8. **慎重にカスタマイズ** - 必要な場合のみカスタムセクションを追加

---

## Resources

- [SKILL_TEMPLATE.md](assets/SKILL_TEMPLATE.md) - 英語テンプレート
- [SKILL_TEMPLATE.ja.md](assets/SKILL_TEMPLATE.ja.md) - 日本語テンプレート
- [skill-writing-guide](../skill-writing-guide/SKILL.md) - テンプレートの埋め方
- [skill-quality-validation](../skill-quality-validation/SKILL.md) - 生成されたスキルを検証

---
