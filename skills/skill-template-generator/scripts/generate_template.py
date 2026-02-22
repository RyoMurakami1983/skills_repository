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
        self.step_count = 5
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
            
        # 4. Step count
        while True:
            try:
                count_input = input("4. Number of steps (3-8): ").strip()
                self.step_count = int(count_input)
                if 1 <= self.step_count <= 15:
                    if self.step_count < 3 or self.step_count > 8:
                        print(f"   ⚠️  Recommended: 3-8 steps")
                    break
                print("   ❌ Enter a number between 1 and 15.")
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
        print(f"  Steps: {self.step_count}")
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
        today = datetime.now().strftime("%Y-%m-%d")
        
        content = f"""---
name: {self.skill_name}
description: {self.description}
metadata:
  author: {self.AUTHOR}
  tags: [{tags_str}]
  invocable: false
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

---

## Core Principles

<!-- Values alignment: 基礎と型の追求, 成長の複利, ニュートラルな視点 -->

1. **[Principle 1]** - One-line summary of key concept
2. **[Principle 2]** - One-line summary of key concept
3. **[Principle 3]** - One-line summary of key concept

---

## Workflow: [Workflow Name]

"""
        
        # Generate step sections
        for i in range(1, self.step_count + 1):
            content += self.generate_step_section(i)
            
        content += f"""## Best Practices

- [Best practice 1]
- [Best practice 2]
- [Best practice 3]
- [Best practice 4]
- [Best practice 5]

---

## Common Pitfalls

- **[Pitfall 1]** - Why it happens and how to avoid it
- **[Pitfall 2]** - Why it happens and how to avoid it
- **[Pitfall 3]** - Why it happens and how to avoid it

---

## Anti-Patterns

- **[Anti-pattern 1]** - What it looks like and why it fails
- **[Anti-pattern 2]** - What it looks like and why it fails
- **[Anti-pattern 3]** - What it looks like and why it fails

---

## Quick Reference

### Checklist

- [ ] [Step/check 1]
- [ ] [Step/check 2]
- [ ] [Step/check 3]
- [ ] [Step/check 4]
- [ ] [Step/check 5]

### Summary Table

| Step | Action | Key Point |
|------|--------|-----------|
| 1 | [Action] | [Key point] |
| 2 | [Action] | [Key point] |
| 3 | [Action] | [Key point] |

---

## FAQ

**Q: [Common question 1]?**
A: [Answer]

**Q: [Common question 2]?**
A: [Answer]

**Q: [Common question 3]?**
A: [Answer]

---

## Resources

- [Link to official docs]
- [Link to relevant tutorial]
- [Link to example repository]

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

---

## License

This skill documentation is provided as-is for use with GitHub Copilot.

---

**Generated by**: GitHub Copilot Skill Template Generator
**Author**: {self.AUTHOR}
**Last Updated**: {today}
"""
        
        return content
        
    def generate_step_section(self, step_num):
        """Generate a single step section."""
        return f"""### Step {step_num}: [Step Name Here]

[Brief explanation of what this step does and why - 1-2 sentences]

```
// Add code example for this step
```

**Use when**: [Describe when this step applies or is needed]

"""

    def generate_skill_ja_md(self):
        """Generate Japanese SKILL.ja.md content."""
        tags_str = ", ".join(self.tags)
        today = datetime.now().strftime("%Y-%m-%d")
        
        content = f"""---
name: {self.skill_name}
description: {self.description}
metadata:
  author: {self.AUTHOR}
  tags: [{tags_str}]
  invocable: false
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

---

## Core Principles

<!-- Values整合: 基礎と型の追求, 成長の複利, ニュートラルな視点 -->

このスキルの基盤となる原則：

1. **[原則1]** - 重要な概念の1行サマリー
2. **[原則2]** - 重要な概念の1行サマリー
3. **[原則3]** - 重要な概念の1行サマリー

---

## ワークフロー: [ワークフロー名]

"""
        
        # Generate step sections in Japanese
        for i in range(1, self.step_count + 1):
            content += self.generate_step_section_ja(i)
            
        content += f"""## Best Practices

- [ベストプラクティス1]
- [ベストプラクティス2]
- [ベストプラクティス3]
- [ベストプラクティス4]
- [ベストプラクティス5]

---

## Common Pitfalls

- **[よくある問題1]** - 発生理由と回避方法
- **[よくある問題2]** - 発生理由と回避方法
- **[よくある問題3]** - 発生理由と回避方法

---

## Anti-Patterns

- **[アンチパターン1]** - どう見えるか、なぜ失敗するか
- **[アンチパターン2]** - どう見えるか、なぜ失敗するか
- **[アンチパターン3]** - どう見えるか、なぜ失敗するか

---

## Quick Reference

### チェックリスト

- [ ] [ステップ/確認1]
- [ ] [ステップ/確認2]
- [ ] [ステップ/確認3]
- [ ] [ステップ/確認4]
- [ ] [ステップ/確認5]

### サマリーテーブル

| ステップ | アクション | ポイント |
|----------|-----------|---------|
| 1 | [アクション] | [ポイント] |
| 2 | [アクション] | [ポイント] |
| 3 | [アクション] | [ポイント] |

---

## FAQ

**Q: [よくある質問1]？**
A: [回答]

**Q: [よくある質問2]？**
A: [回答]

**Q: [よくある質問3]？**
A: [回答]

---

## Resources

- [公式ドキュメントへのリンク]
- [関連するチュートリアルへのリンク]
- [サンプルリポジトリへのリンク]

---

## Changelog

バージョン履歴は [CHANGELOG.md](../CHANGELOG.md) を参照してください。

---

## License

このスキルドキュメントは、GitHub Copilotでの使用のために提供されています。

---

**生成者**: GitHub Copilot Skill Template Generator
**Author**: {self.AUTHOR}
**最終更新**: {today}
"""
        
        return content
        
    def generate_step_section_ja(self, step_num):
        """Generate a single step section in Japanese."""
        return f"""### Step {step_num}: [ステップ名]

[このステップの内容と理由の簡単な説明 - 1-2文]

```
// このステップのコード例を追加
```

**使用場面**: [このステップが適用される場面・条件]

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
- Initial skill structure with {self.step_count} steps

## [1.0.0] - {today}

### Added
- Initial release of {self.skill_name} skill
- Single workflow with {self.step_count} steps
- Best practices, common pitfalls, and anti-patterns
- Quick reference checklist and FAQ

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
        print(f"1. Fill in Step 1-{self.step_count} sections with examples")
        print("2. Add code examples in your target language")
        print("3. Review and customize Core Principles")
        print("4. Complete Best Practices, Pitfalls, and Anti-Patterns")
        
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
