---
name: skill-template-generator
description: Generate structured SKILL.md templates for GitHub Copilot agent skills.
author: RyoMurakami1983
tags: [copilot, agent-skills, templates, generator, scaffolding]
invocable: false
---

# Skill Template Generator

Automated generation of structured SKILL.md templates with proper formatting, sections, and boilerplate code.

## When to Use This Skill

Use this skill when:
- Generating standard SKILL.md structure with all required sections
- Creating skills that comply with GitHub Copilot specifications
- Setting up bilingual skill boilerplate (English and Japanese)
- Establishing skill scaffolding with proper YAML frontmatter
- Building skill templates with author attribution included
- Automating skill structure validation from the start

---

## Related Skills

- **`skill-writing-guide`** - Learn skill writing best practices
- **`skill-quality-validation`** - Validate generated skills
- **`skill-revision-guide`** - Revise generated skills

---

## Core Principles

1. **基礎と型（Foundation & Form）** - Generate templates that embed standard structure and pass quality validation by default
2. **成長の複利（Compound Growth）** - Provide scaffolding that makes it easy to add patterns incrementally over time
3. **継続は力（Consistency is Strength）** - Support bilingual versions (English + Japanese) to maintain accessibility and reach
4. **ニュートラル（Neutrality）** - Create templates with clear placeholders and guidance for diverse skill domains

---

## Pattern 1: Basic Template Generation

### Overview

Generate a minimal SKILL.md with required sections and YAML frontmatter.

### Basic Example

```bash
# Generate basic template
Skill Name: my-new-skill
Description: Brief description of what this skill does
Tags: tag1, tag2, tag3

# Output:
# ~/.copilot/skills/my-new-skill/SKILL.md created
```

**Generated Structure**:
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

| Scenario | Template Type | Why |
|----------|--------------|-----|
| Brand new skill | Basic template | Start with structure, fill content |
| Similar to existing | Clone + modify | Reuse proven structure |
| Quick prototype | Minimal template | Test idea quickly |

### With Configuration

```python
# ✅ CORRECT - Template generator with options
from pathlib import Path
from datetime import date

class SkillTemplateGenerator:
    def __init__(self, skill_name: str, description: str, tags: list):
        self.skill_name = skill_name
        self.description = description
        self.tags = tags
        self.output_dir = Path.home() / ".copilot" / "skills" / skill_name
    
    def generate(self, pattern_count: int = 7, include_japanese: bool = True):
        """Generate SKILL.md template"""
        # Create directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "references").mkdir(exist_ok=True)
        
        # Generate English version
        skill_md = self._generate_skill_md(pattern_count)
        (self.output_dir / "SKILL.md").write_text(skill_md, encoding='utf-8')
        
        # Generate Japanese version
        if include_japanese:
            skill_ja = self._generate_skill_ja_md(pattern_count)
            (self.output_dir / "references" / "SKILL.ja.md").write_text(
                skill_ja, encoding='utf-8'
            )
        
        print(f"✅ Template generated at {self.output_dir}")
    
    def _generate_skill_md(self, pattern_count: int) -> str:
        """Generate English SKILL.md content"""
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
        # Add pattern sections
        for i in range(1, pattern_count + 1):
            content += self._generate_pattern_section(i)
        
        # Add remaining sections
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
        """Generate a pattern section template"""
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
        """Convert kebab-case to Title Case"""
        return " ".join(word.capitalize() for word in kebab_name.split('-'))

# Usage
generator = SkillTemplateGenerator(
    skill_name="wpf-data-binding",
    description="Advanced WPF data binding patterns with MVVM and validation",
    tags=["wpf", "mvvm", "databinding", "csharp"]
)
generator.generate(pattern_count=8, include_japanese=True)
```

---

## Pattern 2: Bilingual Template Generation

### Overview

Generate both English and Japanese versions simultaneously with proper directory structure.

### Basic Example

**Directory Structure**:
```
my-skill/
├── SKILL.md                   # English (required)
└── references/
    └── SKILL.ja.md            # Japanese (optional)
```

### When to Use

Always generate Japanese version when:
- Author is Japanese speaker
- Target audience includes Japanese developers
- Need to reduce cognitive load during skill writing

### With Configuration

```python
# ✅ CORRECT - Bilingual generator
class BilingualTemplateGenerator(SkillTemplateGenerator):
    def _generate_skill_ja_md(self, pattern_count: int) -> str:
        """Generate Japanese SKILL.ja.md content"""
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
        # Add Japanese pattern sections
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

### 1. 落とし穴の名前

**Problem**: ユーザーが通常間違えること。

```csharp
// ❌ WRONG
```

**Solution**: 修正方法。

```csharp
// ✅ CORRECT
```

---

## Changelog

### Version 1.0.0 ({today})
- 初版
"""
        return content
```

---

## Pattern 3: Customizing Generated Templates

### Overview

Modify generated templates to include domain-specific sections or custom patterns.

### Basic Example

```python
# ✅ CORRECT - Custom section injection
class CustomTemplateGenerator(SkillTemplateGenerator):
    def __init__(self, *args, custom_sections: list = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_sections = custom_sections or []
    
    def generate(self, **kwargs):
        """Generate with custom sections"""
        super().generate(**kwargs)
        
        # Inject custom sections before "Common Pitfalls"
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
        """Format custom section"""
        return f"""## {section['title']}

{section['content']}

---
"""

# Usage
generator = CustomTemplateGenerator(
    skill_name="wpf-custom-controls",
    description="Building custom WPF controls",
    tags=["wpf", "controls", "custom"],
    custom_sections=[
        {
            "title": "Performance Considerations",
            "content": "Custom sections about performance..."
        },
        {
            "title": "Accessibility Guidelines",
            "content": "Custom sections about accessibility..."
        }
    ]
)
generator.generate()
```

---

## Common Pitfalls

### 1. Forgetting to Set `author: RyoMurakami1983`

**Problem**: Generated skills don't include author field, making them untrackable.

```yaml
# ❌ WRONG - No author field
---
name: my-skill
description: My skill description
invocable: false
---
```

**Solution**: Always include author in generated templates.

```yaml
# ✅ CORRECT - Author field included
---
name: my-skill
description: My skill description
author: RyoMurakami1983  # System-created skill
invocable: false
---
```

### 2. Generating < 7 Pattern Sections

**Problem**: Default template has only 3 patterns, doesn't pass quality validation.

**Solution**: Configure pattern_count to 7-10.

```python
# ❌ WRONG
generator.generate()  # Defaults to 3 patterns

# ✅ CORRECT
generator.generate(pattern_count=7)  # Meets quality standards
```

---

## Quick Reference

### Template Generation Workflow

```
1. Define skill metadata
   ├─ Name (kebab-case)
   ├─ Description (≤ 100 chars)
   └─ Tags (3-5 items)

2. Run generator
   ├─ pattern_count: 7-10
   ├─ include_japanese: true
   └─ custom_sections: optional

3. Output created
   ├─ SKILL.md (English)
   └─ references/SKILL.ja.md (Japanese)

4. Fill placeholders
   ├─ Replace [Placeholders]
   ├─ Add code examples
   └─ Write content

5. Validate
   └─ Run skill-quality-validation
```

### Generator Options

| Option | Default | Purpose |
|--------|---------|---------|
| skill_name | (required) | Directory and frontmatter name |
| description | (required) | YAML description field |
| tags | (required) | Technology tags |
| pattern_count | 7 | Number of pattern sections |
| include_japanese | true | Generate Japanese version |
| custom_sections | [] | Additional sections to inject |

---

## Best Practices Summary

1. **Always Include Author** - Set `author: RyoMurakami1983` for tracking
2. **Generate 7-10 Patterns** - Meet quality validation requirements
3. **Create Bilingual** - Generate both English and Japanese versions
4. **Use Templates from assets/** - Reference official templates
5. **Validate After Generation** - Run quality check on generated skeleton
6. **Fill Immediately** - Don't leave placeholders for too long
7. **Version Control** - Commit generated skeleton before filling content
8. **Customize Carefully** - Only add custom sections when necessary

---

## Resources

- [SKILL_TEMPLATE.md](assets/SKILL_TEMPLATE.md) - English template
- [SKILL_TEMPLATE.ja.md](assets/SKILL_TEMPLATE.ja.md) - Japanese template
- [skill-writing-guide](../skill-writing-guide/SKILL.md) - How to fill templates
- [skill-quality-validation](../skill-quality-validation/SKILL.md) - Validate generated skills

---

## Changelog

### Version 1.0.0 (2026-02-12)
- Initial release
- Basic and bilingual template generation
- Customization support
- Auto-includes `author: RyoMurakami1983`

<!-- 
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
