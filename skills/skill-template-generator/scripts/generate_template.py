#!/usr/bin/env python3
"""
GitHub Copilot Skill Template Generator

Interactively generates SKILL.md template files for GitHub Copilot Skills.
Creates complete directory structure with bilingual templates.

Usage:
    python scripts/generate_template.py
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path


class TemplateGenerator:
    """Interactive template generator for GitHub Copilot Skills."""
    
    AUTHOR = "RyoMurakami1983"
    
    def __init__(self):
        self.skill_name = ""
        self.description = ""
        self.tags = []
        self.pattern_count = 8
        self.bilingual = True
        self.output_dir = ""
        
    def run(self):
        """Main entry point for the generator."""
        self.print_header()
        self.collect_input()
        self.confirm_settings()
        self.generate_files()
        self.print_success()
        
    def print_header(self):
        """Print welcome header."""
        print("\n" + "=" * 50)
        print("GitHub Copilot Skill Template Generator")
        print("=" * 50 + "\n")
        
    def collect_input(self):
        """Collect user input interactively."""
        # 1. Skill name
        while True:
            self.skill_name = input("1. Skill name (kebab-case): ").strip()
            if self.validate_skill_name(self.skill_name):
                break
            print("   ❌ Invalid name. Use kebab-case, max 64 characters.")
            
        # 2. Description
        while True:
            self.description = input("2. Description (when to use): ").strip()
            if self.validate_description(self.description):
                break
            print("   ❌ Description too long (max 100 characters).")
            
        # 3. Tags
        while True:
            tags_input = input("3. Tags (comma-separated): ").strip()
            self.tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
            if len(self.tags) >= 1:
                if len(self.tags) < 3 or len(self.tags) > 5:
                    print(f"   ⚠️  Recommended: 3-5 tags (you entered {len(self.tags)})")
                break
            print("   ❌ Enter at least 1 tag.")
            
        # 4. Pattern count
        while True:
            try:
                count_input = input("4. Number of patterns (7-10): ").strip()
                self.pattern_count = int(count_input)
                if 1 <= self.pattern_count <= 20:
                    if self.pattern_count < 7 or self.pattern_count > 10:
                        print(f"   ⚠️  Recommended: 7-10 patterns")
                    break
                print("   ❌ Enter a number between 1 and 20.")
            except ValueError:
                print("   ❌ Enter a valid number.")
                
        # 5. Bilingual option
        bilingual_input = input("5. Generate bilingual? (y/n): ").strip().lower()
        self.bilingual = bilingual_input in ['y', 'yes', '']
        
        # 6. Output directory
        default_dir = f"./{self.skill_name}/"
        dir_input = input(f"6. Output directory [{default_dir}]: ").strip()
        self.output_dir = dir_input if dir_input else default_dir
        
    def validate_skill_name(self, name):
        """Validate skill name format."""
        if not name or len(name) > 64:
            return False
        # Check kebab-case: lowercase letters, numbers, hyphens
        return bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name))
        
    def validate_description(self, desc):
        """Validate description length."""
        return 1 <= len(desc) <= 100
        
    def confirm_settings(self):
        """Display settings and confirm."""
        print("\n" + "-" * 50)
        print("Settings:")
        print(f"  Name: {self.skill_name}")
        print(f"  Description: {self.description}")
        print(f"  Tags: {', '.join(self.tags)}")
        print(f"  Patterns: {self.pattern_count}")
        print(f"  Bilingual: {'Yes' if self.bilingual else 'No'}")
        print(f"  Output: {self.output_dir}")
        print("-" * 50)
        
        confirm = input("\nProceed? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', '']:
            print("Cancelled.")
            sys.exit(0)
            
    def generate_files(self):
        """Generate all template files."""
        print("\nGenerating...")
        
        # Create directory structure
        base_path = Path(self.output_dir)
        base_path.mkdir(parents=True, exist_ok=True)
        (base_path / "assets").mkdir(exist_ok=True)
        
        # Generate SKILL.md (English)
        skill_md_path = base_path / "SKILL.md"
        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_skill_md())
        print(f"✅ Created: {skill_md_path}")
        
        # Generate Japanese version if requested
        if self.bilingual:
            ref_dir = base_path / "references"
            ref_dir.mkdir(exist_ok=True)
            skill_ja_path = ref_dir / "SKILL.ja.md"
            with open(skill_ja_path, 'w', encoding='utf-8') as f:
                f.write(self.generate_skill_ja_md())
            print(f"✅ Created: {skill_ja_path}")
            
        # Generate CHANGELOG.md
        changelog_path = base_path / "CHANGELOG.md"
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_changelog())
        print(f"✅ Created: {changelog_path}")
        
        # Confirm assets directory
        print(f"✅ Created: {base_path / 'assets'}/")
        
    def generate_skill_md(self):
        """Generate English SKILL.md content."""
        tags_str = ", ".join(self.tags)
        
        content = f"""---
name: {self.skill_name}
description: {self.description}
invocable: false
tags: [{tags_str}]
author: {self.AUTHOR}
---

# {self.skill_name.replace('-', ' ').title()}

## Related Skills

<!-- Add related skills here -->
<!-- Example:
- **`related-skill-name`** - Brief description of relationship
-->

## When to Use This Skill

Use this skill when:
- [Add specific scenario 1]
- [Add specific scenario 2]
- [Add specific scenario 3]
- [Add specific scenario 4]
- [Add specific scenario 5]

---

## Core Principles

1. **[Principle 1]** - One-line summary of key concept
2. **[Principle 2]** - One-line summary of key concept
3. **[Principle 3]** - One-line summary of key concept
4. **[Principle 4]** - One-line summary of key concept (optional)
5. **[Principle 5]** - One-line summary of key concept (optional)

---

"""
        
        # Generate pattern sections
        for i in range(1, self.pattern_count + 1):
            content += self.generate_pattern_section(i)
            
        # Add Common Pitfalls section
        content += """## Common Pitfalls

### 1. [Pitfall Name] - Brief Description

**Problem**: What users typically do wrong and why it fails.

```
// ❌ WRONG - What not to do
// Add anti-pattern example
```

**Solution**: How to fix it and why this approach works.

```
// ✅ CORRECT - The right approach
// Add correct pattern example
```

### 2. [Another Pitfall Name]

[Add more pitfalls as needed...]

---

## Anti-Patterns

### [Anti-Pattern Name]

**What**: Description of the anti-pattern at an architectural level.

```
// ❌ WRONG - Architectural mistake
// Add anti-pattern example
```

**Why It's Wrong**:
- Reason 1: [Explain violation]
- Reason 2: [Explain problem]
- Reason 3: [Explain scalability issue]

**Better Approach**:

```
// ✅ CORRECT - Recommended architecture
// Add correct pattern example
```

---

## Related Patterns & Further Reading

### Related Design Patterns
- [Pattern 1]: Brief description and when to use
- [Pattern 2]: Brief description and when to use

### Official Documentation
- [Link to official docs]
- [Link to relevant API reference]

### Community Resources
- [Relevant blog post or tutorial]
- [GitHub repository or example]

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

---

## License

This skill documentation is provided as-is for use with GitHub Copilot.

---

**Generated by**: GitHub Copilot Skill Template Generator
**Author**: {self.AUTHOR}
**Last Updated**: {datetime.now().strftime("%Y-%m-%d")}
"""
        
        return content
        
    def generate_pattern_section(self, pattern_num):
        """Generate a single pattern section."""
        return f"""## Pattern {pattern_num}: [Pattern Name Here]

### Overview

[Brief explanation of what this pattern solves and why it matters - 2-3 sentences]

### Basic Example

```
// ✅ CORRECT - Simple, most common case
// Add basic implementation example
```

### When to Use

Use this pattern when:
- [Specific condition A]
- [Specific condition B]
- [Specific condition C]

| Scenario | Recommendation | Why |
|----------|----------------|-----|
| [Scenario A] | Use Pattern {pattern_num} | [Brief explanation] |
| [Scenario B] | Consider alternatives | [Brief explanation] |
| [Scenario C] | See Pattern {pattern_num + 1 if pattern_num < self.pattern_count else 1} | [Brief explanation] |

### With Configuration

```
// ✅ CORRECT - With options/configuration
// Add configuration example
```

### Advanced Pattern

```
// ✅ CORRECT - Production-grade with error handling
// Add advanced implementation with:
// - Error handling
// - Cancellation support
// - Resource management
// - Logging/monitoring
```

---

"""

    def generate_skill_ja_md(self):
        """Generate Japanese SKILL.ja.md content."""
        tags_str = ", ".join(self.tags)
        
        content = f"""---
name: {self.skill_name}
description: {self.description}
invocable: false
tags: [{tags_str}]
author: {self.AUTHOR}
---

# {self.skill_name.replace('-', ' ').title()}

## Related Skills

<!-- 関連するスキルをここに追加 -->
<!-- 例:
- **`related-skill-name`** - 関係の簡単な説明
-->

## When to Use This Skill

このスキルを使用する場面：
- [具体的なシナリオ1を追加]
- [具体的なシナリオ2を追加]
- [具体的なシナリオ3を追加]
- [具体的なシナリオ4を追加]
- [具体的なシナリオ5を追加]

---

## Core Principles

このスキルの基盤となる原則：

1. **[原則1]** - 重要な概念の1行サマリー
2. **[原則2]** - 重要な概念の1行サマリー
3. **[原則3]** - 重要な概念の1行サマリー
4. **[原則4]** - 重要な概念の1行サマリー（オプション）
5. **[原則5]** - 重要な概念の1行サマリー（オプション）

---

"""
        
        # Generate pattern sections in Japanese
        for i in range(1, self.pattern_count + 1):
            content += self.generate_pattern_section_ja(i)
            
        # Add Common Pitfalls section in Japanese
        content += """## Common Pitfalls

### 1. [よくある問題名] - 簡単な説明

**問題**: ユーザーが通常行う誤りとその理由。

```
// ❌ WRONG - やってはいけないこと
// アンチパターンの例を追加
```

**解決策**: 修正方法とこのアプローチが機能する理由。

```
// ✅ CORRECT - 正しいアプローチ
// 正しいパターンの例を追加
```

### 2. [別のよくある問題名]

[必要に応じて問題を追加...]

---

## Anti-Patterns

### [アンチパターン名]

**内容**: アーキテクチャレベルでのアンチパターンの説明。

```
// ❌ WRONG - アーキテクチャ上の誤り
// アンチパターンの例を追加
```

**なぜ間違っているか**:
- 理由1: [違反の説明]
- 理由2: [問題の説明]
- 理由3: [スケーラビリティの問題]

**より良いアプローチ**:

```
// ✅ CORRECT - 推奨されるアーキテクチャ
// 正しいパターンの例を追加
```

---

## Related Patterns & Further Reading

### 関連する設計パターン
- [パターン1]: 簡単な説明と使用時期
- [パターン2]: 簡単な説明と使用時期

### 公式ドキュメント
- [公式ドキュメントへのリンク]
- [関連するAPIリファレンスへのリンク]

### コミュニティリソース
- [関連するブログ投稿やチュートリアル]
- [GitHubリポジトリや例]

---

## Changelog

バージョン履歴は [CHANGELOG.md](../CHANGELOG.md) を参照してください。

---

## License

このスキルドキュメントは、GitHub Copilotでの使用のために提供されています。

---

**生成者**: GitHub Copilot Skill Template Generator
**Author**: {self.AUTHOR}
**最終更新**: {datetime.now().strftime("%Y-%m-%d")}
"""
        
        return content
        
    def generate_pattern_section_ja(self, pattern_num):
        """Generate a single pattern section in Japanese."""
        return f"""## Pattern {pattern_num}: [パターン名]

### Overview

[このパターンが何を解決するか、なぜ重要かの簡単な説明 - 2-3文]

### Basic Example

```
// ✅ CORRECT - Simple, most common case
// 基本的な実装例を追加
```

### When to Use

このパターンを使用する場面：
- [特定の条件A]
- [特定の条件B]
- [特定の条件C]

| シナリオ | 推奨 | 理由 |
|----------|------|------|
| [シナリオA] | パターン{pattern_num}を使用 | [簡単な説明] |
| [シナリオB] | 代替案を検討 | [簡単な説明] |
| [シナリオC] | パターン{pattern_num + 1 if pattern_num < self.pattern_count else 1}を参照 | [簡単な説明] |

### With Configuration

```
// ✅ CORRECT - With options/configuration
// 設定例を追加
```

### Advanced Pattern

```
// ✅ CORRECT - Production-grade with error handling
// 以下を含む高度な実装を追加：
// - エラーハンドリング
// - キャンセルサポート
// - リソース管理
// - ロギング/モニタリング
```

---

"""

    def generate_changelog(self):
        """Generate CHANGELOG.md content."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        return f"""# Changelog

All notable changes to the `{self.skill_name}` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial skill structure with {self.pattern_count} patterns

## [1.0.0] - {today}

### Added
- Initial release of {self.skill_name} skill
- {self.pattern_count} core patterns
- Basic examples and advanced patterns
- Common pitfalls and anti-patterns
- Related patterns and further reading

### Notes
- Generated using GitHub Copilot Skill Template Generator
- Author: {self.AUTHOR}

---

[Unreleased]: https://github.com/yourusername/{self.skill_name}/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/{self.skill_name}/releases/tag/v1.0.0
"""

    def print_success(self):
        """Print success message with next steps."""
        print("\n" + "=" * 50)
        print("✅ Template generation complete!")
        print("=" * 50)
        print("\nNext steps:")
        print(f"1. Fill in Pattern 1-{self.pattern_count} sections with examples")
        print("2. Add code examples in your target language")
        print("3. Review and customize Core Principles")
        print("4. Add Common Pitfalls from real-world experience")
        
        # Check if validation script exists
        validation_script = Path("../skill-quality-validation/scripts/validate_skill.py")
        if validation_script.exists():
            print(f"\n5. Validate: python {validation_script} {self.output_dir}SKILL.md")
        else:
            print("\n5. Consider creating a validation script for quality checks")
            
        print(f"\nOutput directory: {Path(self.output_dir).absolute()}")
        print("")


def main():
    """Main entry point."""
    try:
        generator = TemplateGenerator()
        generator.run()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
