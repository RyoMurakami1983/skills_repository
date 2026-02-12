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

## Pattern 4: Version Control Integration

### Overview

Generate CHANGELOG.md template alongside SKILL.md for proper version tracking from day one.

**Why**: Starting with a changelog structure encourages documenting changes from the beginning, establishing good maintenance habits and making future updates easier to track.

### Basic Example

```python
# ✅ CORRECT - Generate with changelog
def generate_skill_with_changelog(name: str, output_dir: Path):
    """Generate SKILL.md and CHANGELOG.md together"""
    skill_path = output_dir / "SKILL.md"
    changelog_path = output_dir / "CHANGELOG.md"
    
    # Generate main skill file
    skill_content = generate_skill_template(name)
    skill_path.write_text(skill_content, encoding='utf-8')
    
    # Generate changelog template
    changelog_content = f"""# Changelog - {name}

All notable changes to this skill will be documented in this file.

Format: `Category: Description (max 100 chars)`

## Version 1.0.0 ({datetime.now().strftime('%Y-%m-%d')})
- Added: Initial skill creation
- Added: Core patterns and examples
- Added: Documentation and references
"""
    changelog_path.write_text(changelog_content, encoding='utf-8')
    
    print(f"✅ Generated: {skill_path}")
    print(f"✅ Generated: {changelog_path}")
```

### When to Use

- Creating production-ready skills that will evolve over time
- Setting up skills for team collaboration with version tracking
- Establishing skills that require formal release management

---

## Pattern 5: Multi-Pattern Skill Generation

### Overview

Generate skills with multiple pattern sections (7-10 recommended) using pattern templates.

**Why**: Skills with 7-10 patterns hit the sweet spot for comprehensive coverage without overwhelming readers. Template-driven generation ensures consistency across patterns.

### Basic Example

```python
# ✅ CORRECT - Generate multi-pattern skill
def generate_multi_pattern_skill(name: str, pattern_count: int = 8):
    """Generate skill with specified number of patterns"""
    if not (7 <= pattern_count <= 10):
        print(f"⚠️ Warning: {pattern_count} patterns (recommended: 7-10)")
    
    patterns = []
    for i in range(1, pattern_count + 1):
        pattern = f"""
## Pattern {i}: [Pattern Name]

### Overview

[Brief description of what this pattern addresses]

**Why**: [Explanation of why this pattern is important]

### Basic Example

```python
# ✅ CORRECT - [Pattern implementation]
# TODO: Add code example
```

### When to Use

- [Scenario 1]
- [Scenario 2]
- [Scenario 3]
"""
        patterns.append(pattern)
    
    skill_content = generate_base_template(name) + "\n".join(patterns)
    return skill_content
```

### When to Use

- Creating comprehensive skills covering a broad topic
- Generating skills that need multiple approaches or techniques
- Building skills for complex domains requiring detailed patterns

---

## Pattern 6: Dependency and Requirements

### Overview

Document dependencies, prerequisites, and installation requirements in the generated template.

**Why**: Clear dependency documentation prevents setup issues and helps users determine if a skill is applicable to their environment.

### Basic Example

```python
# ✅ CORRECT - Include dependencies section
dependencies_section = """
## Prerequisites

### Required Tools
- Python 3.8 or higher
- pip package manager

### Required Libraries
```bash
pip install pyyaml jinja2
```

### Optional Tools
- VS Code with Python extension (recommended)
- GitHub CLI for repository operations

## Dependencies

This skill requires the following Python packages:

| Package | Version | Purpose |
|---------|---------|---------|
| pyyaml | ≥6.0 | YAML parsing for frontmatter |
| jinja2 | ≥3.0 | Template rendering |
| pathlib | stdlib | File path handling |

To install all dependencies:

```bash
pip install -r requirements.txt
```
"""

def generate_with_dependencies(name: str, deps: list[str]):
    """Generate skill with dependency documentation"""
    template = load_base_template()
    template = template.replace("{{DEPENDENCIES}}", dependencies_section)
    
    # Generate requirements.txt
    requirements_content = "\n".join([f"{dep}>=1.0" for dep in deps])
    
    return {
        "SKILL.md": template,
        "requirements.txt": requirements_content
    }
```

### When to Use

- Generating skills with external library dependencies
- Creating skills for specific tool ecosystems
- Building skills that require particular environment setups

---

## Pattern 7: Asset and Template Management

### Overview

Organize generated templates, assets, and reference materials in a structured directory layout.

**Why**: Proper asset organization (assets/, references/) keeps skills maintainable and adheres to the references/ pattern for content exceeding 500 lines.

### Basic Example

```python
# ✅ CORRECT - Structured asset generation
from pathlib import Path

def generate_skill_with_assets(name: str, output_dir: Path):
    """Generate skill with complete directory structure"""
    skill_dir = output_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # Create directory structure
    (skill_dir / "assets").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)
    
    # Generate main skill file
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(generate_template(name), encoding='utf-8')
    
    # Generate Japanese version in references/
    ja_md = skill_dir / "references" / "SKILL.ja.md"
    ja_md.write_text(generate_template_ja(name), encoding='utf-8')
    
    # Generate template assets
    template_file = skill_dir / "assets" / "TEMPLATE.md"
    template_file.write_text(load_pattern_template(), encoding='utf-8')
    
    # Generate README for references/
    readme = skill_dir / "references" / "README.md"
    readme.write_text(f"""# {name} References

This directory contains supplementary materials for the {name} skill:

- **SKILL.ja.md**: Japanese translation of the main skill
- **extended-examples.md**: Additional code examples
- **api-reference.md**: Detailed API documentation

## File Organization

Place content here when:
- Main SKILL.md exceeds 500 lines (recommended) or 550 lines (max)
- Detailed reference material supports main patterns
- Bilingual versions require separate files
""", encoding='utf-8')
    
    print(f"✅ Generated skill structure:")
    print(f"   {skill_md}")
    print(f"   {ja_md}")
    print(f"   {template_file}")
    print(f"   {readme}")
```

### When to Use

- Creating skills with extensive reference materials
- Generating bilingual skills (English + Japanese)
- Building skills with reusable template assets
- Setting up skills that will exceed 500 lines

---

## Anti-Patterns

### 1. Hardcoding Template Content

**Problem**: Embedding all template content directly in code instead of using external template files makes templates inflexible and difficult to customize.

**Impact**: Every template change requires code modification, testing, and redeployment. Users cannot easily adapt templates to their needs.

**Fix**: Use external template files (Jinja2, Mustache) instead of hardcoding. This separates content from logic and enables easy customization.

```python
# ❌ ANTI-PATTERN - Hardcoded template
def generate_skill(name):
    return f"""---
name: {name}
description: [Add description]
---

# {name}

[Content goes here]
"""

# ✅ CORRECT - Template file approach
from jinja2 import Template

template = Template(Path("templates/SKILL.j2").read_text())
skill_content = template.render(name=name, description=desc)
```

### 2. Ignoring File Length Limits

**Problem**: Generating massive SKILL.md files without considering the 500-line recommendation or 550-line maximum.

**Impact**: Generated skills fail quality validation and become difficult to navigate and maintain.

**Fix**: Split content into main SKILL.md and references/ directory when approaching limits. Check line count and automatically distribute content.

```python
# ❌ ANTI-PATTERN - No length checking
def generate_skill(patterns: list):
    content = base_template + "\n".join([p.render() for p in patterns])
    return content  # Could be 1000+ lines!

# ✅ CORRECT - Length-aware generation with split
def generate_skill_smart(patterns: list):
    main_content = base_template + "\n".join([p.render() for p in patterns[:5]])
    
    if len(main_content.split('\n')) > 500:
        # Move detailed examples to references/
        extended = "\n".join([p.render_extended() for p in patterns])
        return {
            "SKILL.md": main_content,
            "references/extended-examples.md": extended
        }
    
    return {"SKILL.md": main_content}
```

---

## Common Pitfalls

### 1. Missing Import Statements in Generated Code

**Problem**: Generated code examples lack necessary import statements, making them non-compilable.

**Solution**: Always include required imports at the top of code blocks.

```python
# ❌ WRONG - Missing imports
code_example = '''
def load_yaml(path):
    return yaml.safe_load(Path(path).read_text())
'''

# ✅ CORRECT - Include imports
code_example = '''
import yaml
from pathlib import Path

def load_yaml(path):
    return yaml.safe_load(Path(path).read_text())
'''
```

**Fix**: Create import template that prepends required imports based on code analysis.

### 2. No Error Handling in Templates

**Problem**: Generated code examples don't demonstrate proper error handling, leading to brittle skills.

**Solution**: Include try-except blocks and validation in generated examples.

```python
# ❌ WRONG - No error handling
def generate_example():
    return '''
skill_path = Path(skill_name) / "SKILL.md"
skill_path.write_text(content)
'''

# ✅ CORRECT - With error handling
def generate_example_safe():
    return '''
try:
    skill_path = Path(skill_name) / "SKILL.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(content, encoding='utf-8')
    print(f"✅ Generated: {skill_path}")
except OSError as e:
    print(f"❌ Failed to write {skill_path}: {e}")
    raise
'''
```

**Fix**: Wrap file operations and external calls in try-except with meaningful error messages.

### 3. Forgetting Bilingual Support

**Problem**: Generating only English SKILL.md without considering Japanese translation needs for system skills.

**Solution**: Offer bilingual generation as default or prominent option.

```python
# ❌ WRONG - English only
def generate_skill(name):
    return generate_template("en", name)

# ✅ CORRECT - Bilingual by default for system skills
def generate_skill(name, bilingual=True):
    files = {"SKILL.md": generate_template("en", name)}
    
    if bilingual:
        files["references/SKILL.ja.md"] = generate_template("ja", name)
        print("✅ Generated bilingual skill (EN + JA)")
    
    return files
```

**Fix**: Make bilingual generation the default for `author: RyoMurakami1983` skills.

---

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
