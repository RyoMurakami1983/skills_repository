---
name: skill-quality-validation
description: Validate and score the quality of GitHub Copilot agent skills. Use when reviewing SKILL.md files for completeness, adherence to best practices, or generating quality reports.
author: RyoMurakami1983
tags: [copilot, agent-skills, quality, validation, testing]
invocable: false
---

# Skill Quality Validation

Comprehensive quality assessment system for GitHub Copilot agent skills with 64-point checklist, automated scoring, and development philosophy integration.

## Related Skills

- **`skill-writing-guide`** - Learn skill writing best practices
- **`skill-template-generator`** - Generate skill templates
- **`skill-revision-guide`** - Revise skills based on validation results

## When to Use This Skill

Use this skill when:
- Reviewing a completed SKILL.md file before publishing
- Assessing skill quality against official standards
- Generating quality reports with scores and improvement recommendations
- Identifying structural or content issues in skills
- Validating compliance with GitHub Copilot/Claude specifications
- Performing peer reviews of skill documentation

---

## Core Principles

1. **Quantitative Assessment** - Use 64-item checklist with objective pass/fail criteria
2. **Category-Based Scoring** - Evaluate Structure (14), Content (23), Code Quality (16), Language (11)
3. **Clear Pass Criteria** - Require 80% per category, 80% overall (51/64 points)
4. **Actionable Feedback** - Identify specific failures with improvement recommendations
5. **Continuous Improvement** - Target 90%+ scores after iterative refinement
6. **Philosophy Integration** - Align with development Values (基礎と型、成長の複利、温故知新、継続は力、ニュートラル)

---

## Pattern 1: Running a Quality Check

### Overview

Execute the 64-point checklist to assess skill quality across four categories, with expanded validation for file length optimization, references/ structure, bilingual support, and development philosophy integration.

### Basic Example

**Quick Check** (Manual):
1. Open the SKILL.md file
2. Verify YAML frontmatter exists with required fields
3. Check "When to Use This Skill" is the first H2 section
4. Count pattern sections (should be 7-10)
5. Verify Common Pitfalls and Anti-Patterns sections exist

### When to Use

| Scenario | Approach | Why |
|----------|----------|-----|
| Pre-publish review | Full 55-item check | Ensure quality standards |
| Quick sanity check | 10-item structure check | Fast feedback during writing |
| Peer review | Content + Code checks | Focus on substance |
| Post-revision | Recheck previously failed items | Verify fixes |

### With Configuration

**Structured Checklist Execution**:

```markdown
## 1. Structure Check (11 items)

- [x] 1.1 SKILL.md only, no additional files
- [x] 1.2 YAML frontmatter with name/description/invocable
- [x] 1.3 Name matches directory (kebab-case)
- [x] 1.4 Description ≤ 100 chars, problem-focused
- [x] 1.5 "When to Use This Skill" is first H2 section
- [x] 1.6 "Core Principles" section exists
- [ ] 1.7 7-10 pattern sections (H2)          ← FAIL: Only 3 patterns
- [x] 1.8 "Common Pitfalls" section exists
- [x] 1.9 "Anti-Patterns" section exists
- [x] 1.10 "Quick Reference" or "Decision Tree" exists
- [x] 1.11 SKILL.md file ≤500 lines (Claude/GitHub Copilot recommendation)

**Score**: 9/11 = 82% ✅ PASS
```



---

## Pattern 2: Structure Validation (14 Items)

### Overview

Validates physical file structure, section ordering, YAML frontmatter compliance, file length optimization, references/ directory structure, and bilingual support.

### Basic Example

**14-Item Structure Checklist**:

1. **Single File**: SKILL.md only (no README.md, examples.md, etc.)
2. **YAML Frontmatter**: Contains name, description, invocable
3. **Name Consistency**: Frontmatter name matches directory name (kebab-case)
4. **Description Length**: ≤ 100 characters, problem-focused
5. **When to Use Position**: First H2 section after title
6. **Core Principles**: Section exists
7. **Pattern Count**: 7-10 H2 pattern sections
8. **Common Pitfalls**: Section exists
9. **Anti-Patterns**: Section exists
10. **Quick Reference**: Section or Decision Tree exists
11. **File Length Optimization**: ≤500 lines (recommended) OR ≤550 lines (+10% tolerance) with valid reasoning
12. **References Directory** (if >500 lines): `references/` exists with at least one valid file
13. **Japanese Version** (bonus): `references/SKILL.ja.md` exists (+1 bonus point)
14. **References Structure Validity**: If `references/` exists, all files follow naming conventions

### When to Use

Execute structure validation:
- **Before content writing**: Ensure skeleton is correct
- **After major refactoring**: Verify structure integrity
- **During peer review**: Quick structural compliance check

**Pass Criteria**: 11/14 (79%) minimum

### With Configuration

**Detailed Validation Rules**:

```yaml
# Structure Check Configuration
checks:
  1.1_single_file:
    rule: "Count of *.md files in skill directory == 1"
    allow_exceptions: ["references/SKILL.ja.md", "references/*.md", "CHANGELOG.md"]
  
  1.4_description_length:
    rule: "len(frontmatter['description']) <= 100"
    severity: "warning"  # Over 100 is warning, over 150 is failure
  
  1.7_pattern_count:
    rule: "7 <= pattern_count <= 10"
    count_method: "regex: ^## Pattern \\d+:"
  
  1.11_file_length_optimization:
    rule: |
      if line_count <= 500: PASS
      elif line_count <= 550: PASS with WARNING (+10% tolerance)
      else: FAIL (require references/ structure)
    recommended: 500
    tolerance: 550
  
  1.12_references_directory:
    rule: "If line_count > 500, check references/ directory exists"
    valid_files: ["anti-patterns.md", "advanced-examples.md", "configuration.md", "SKILL.ja.md"]
    required_count: ">= 1"
  
  1.13_japanese_version:
    rule: "Check for references/SKILL.ja.md"
    bonus: true  # +1 bonus point if exists
    required: false
  
  1.14_references_validity:
    rule: "If references/ exists, validate all files are *.md"
    severity: "error"
```



---

## Pattern 3: Content Validation (23 Items)

### Overview

Validates completeness, clarity, and practical utility of skill content across "When to Use", Core Principles, Patterns, Problem-Solution structures, Values integration, and Why explanations.

### Basic Example

**Key Content Checks**:

- **When to Use** (4 items):
  - 5-8 specific scenarios listed
  - Each starts with verb (Designing, Implementing, etc.)
  - Each scenario 50-100 chars
  - No abstract phrases ("good code", "quality software")

- **Patterns** (6 items):
  - Each has Overview subsection
  - Minimum 3 levels (Basic/Intermediate/Advanced)
  - Each has "When to Use" guidance
  - No duplication between patterns

- **Core Principles** (2 items):
  - Values integration: References at least one development Value (基礎と型、成長の複利、etc.)
  - Alignment: Principles align with skill purpose

- **Pattern Quality** (2 items):
  - Why explanations: Complex patterns include "Why" or rationale
  - Progressive Disclosure: If file >500 lines, advanced content moved to references/

### When to Use

Content validation is critical for:
- **Assessing practical utility**: Ensure skill provides actionable guidance
- **Verifying completeness**: Check all required subsections exist
- **Ensuring clarity**: Validate scenarios are specific, not vague

**Pass Criteria**: 18/23 (78%) minimum

### With Configuration

**Validation Rules**:

```python
# ✅ CORRECT - Validate "When to Use" scenarios
scenarios = skill.get_when_to_use_scenarios()

# Check 2.1.1: Count (5-8 scenarios)
if 5 <= len(scenarios) <= 8:
    pass  # ✅ Valid

# Check 2.1.2: Start with verb
if all(scenario.split()[0].lower() in ACTION_VERBS for scenario in scenarios):
    pass  # ✅ Valid

# Check 2.1.3: Length (50-100 chars)
if all(50 <= len(s) <= 100 for s in scenarios):
    pass  # ✅ Valid

# Check 2.1.4: No abstract phrases
if not any(phrase in s.lower() for s in scenarios for phrase in ABSTRACT_PHRASES):
    pass  # ✅ Valid

# ✅ NEW - Validate Core Principles - Values integration
core_principles = skill.get_core_principles()
DEVELOPMENT_VALUES = ['基礎と型', '成長の複利', '温故知新', '継続は力', 'ニュートラル']

# Check 2.2.1: Values integration (bonus)
values_found = any(value in core_principles for value in DEVELOPMENT_VALUES)
if values_found:
    bonus_points += 1  # +1 bonus point

# ✅ NEW - Validate Pattern Quality - Why explanations
advanced_patterns = skill.get_patterns(level='Advanced')

# Check 2.2.2: Why explanations in complex patterns
why_count = sum(1 for p in advanced_patterns if 'why' in p.lower() or '理由' in p)
if why_count >= len(advanced_patterns) * 0.5:  # At least 50%
    pass  # ✅ Valid

# ✅ NEW - Validate Progressive Disclosure
if skill.line_count > 500:
    # Check 2.2.3: Progressive Disclosure strategy
    has_references_dir = Path('references/').exists()
    advanced_in_references = any(f.name.startswith('advanced') for f in Path('references/').glob('*.md'))
    if has_references_dir and advanced_in_references:
        pass  # ✅ Valid
```

> 📚 **Complete validator implementation**: See `references/validation-examples.md`  
> 📚 **Anti-patterns and failures**: See `references/anti-patterns.md`

---

## Pattern 4: Code Quality Validation (16 Items)

### Overview

Validates code examples for compilability, progressive complexity, consistent markers, production-readiness, and code example length limits.

### Basic Example

**Key Code Quality Checks**:

- **Compilability** (3 items): Code compiles, using statements included, dependencies noted
- **Progression** (3 items): Simple → Advanced ordering, each stage explained
- **Markers** (4 items): ✅/❌ used consistently, comments explain WHY not WHAT
- **Completeness** (5 items): DI config, error handling, async/await, resource disposal
- **Code Length** (1 item): Inline examples ≤15 lines (advanced examples moved to references/)

### When to Use

Code validation ensures:
- Examples are copy-paste ready
- Readers can learn through progressive complexity
- Production-grade patterns are demonstrated

**Pass Criteria**: 13/16 (81%) minimum

### With Configuration

**Code Quality Checks**:

```python
# ✅ CORRECT - Validate code markers and comment quality
import re

# Check 3.3.1: Validate ✅/❌ markers are used consistently
code_blocks = re.findall(r'```\w+\n(.*?)```', content, re.DOTALL)
for block in code_blocks:
    if re.search(r'\bclass\b|\bpublic\b', block):
        assert re.search(r'//\s*[✅❌]', block), "Missing ✅/❌ marker"

# Check 3.3.3: Comments explain WHY not WHAT
WHAT_PATTERNS = [r'//\s*Get\s+\w+', r'//\s*Set\s+\w+', r'//\s*Call\s+\w+']
for block in code_blocks:
    for pattern in WHAT_PATTERNS:
        assert not re.search(pattern, block), "Comment explains WHAT, should explain WHY"

# ✅ NEW - Check 3.16: Code example length limit
for block in code_blocks:
    lines = [l for l in block.split('\n') if l.strip() and not l.strip().startswith('using')]
    line_count = len(lines)
    
    if line_count <= 15:
        pass  # ✅ Valid - Inline examples are concise
    elif line_count <= 20:
        warnings.append("Code example is 16-20 lines, consider moving to references/")
    else:
        # >20 lines should be in references/advanced-examples.md
        has_advanced_ref = Path('references/advanced-examples.md').exists()
        assert has_advanced_ref, "Code example >20 lines requires references/advanced-examples.md"
```

> 📚 **Complete validator implementation**: See `references/validation-examples.md`  
> 📚 **Anti-patterns and failures**: See `references/anti-patterns.md`



---

## Pattern 5: Language & Expression Validation (11 Items)

### Overview

Validates writing style, terminology consistency, scannability for optimal readability, and bilingual support.

### Basic Example

**Key Language Checks**:

- **Style** (4 items): Active voice, short sentences, imperative form, minimal ambiguity
- **Terminology** (3 items): Consistent terms, definitions on first use, acronyms expanded
- **Scannability** (3 items): Clear headers, table clarity, important info highlighted
- **Bilingual Support** (1 item): English SKILL.md + Japanese references/SKILL.ja.md (bonus)
- **Scannability** (3 items): Headings reveal structure, tables are clear, key info highlighted

### When to Use

Language validation ensures:
- Skill is readable and accessible
- Technical terms are defined
- Content is scannable

**Pass Criteria**: 9/11 (82%) minimum

### With Configuration

**Language Quality Checks**:

```python
# ✅ CORRECT - Validate sentence length and active voice
import re

# Check 5.1.2: Sentences ≤ 20 words
sentences = re.split(r'[.!?]\s+', text)
for sentence in sentences:
    word_count = len(sentence.split())
    assert word_count <= 20, f"Sentence too long: {word_count} words"

# Check 5.1.1: Detect passive voice
PASSIVE_INDICATORS = [r'\bis\s+\w+ed\b', r'\bwas\s+\w+ed\b', r'\bcan\s+be\s+\w+ed']
passive_count = sum(1 for s in sentences for p in PASSIVE_INDICATORS if re.search(p, s))
passive_ratio = passive_count / len(sentences)
assert passive_ratio < 0.2, f"Too much passive voice: {passive_ratio:.0%}"

# ✅ NEW - Check 5.11: Bilingual Support
has_english = Path('SKILL.md').exists()
has_japanese = Path('references/SKILL.ja.md').exists()

if has_english and has_japanese:
    bonus_points += 1  # +1 bonus point for bilingual support
elif not has_english and has_japanese:
    assert False, "Japanese-only skill - must have English SKILL.md"
# English-only is acceptable (no penalty)
```

> 📚 **Complete validator implementation**: See `references/validation-examples.md`  
> 📚 **Anti-patterns and failures**: See `references/anti-patterns.md`

---

## Pattern 6: Generating Quality Reports

### Overview

Generate comprehensive reports with scores, failures, and actionable improvement recommendations.

### Basic Example

**Simple Report**:

```markdown
# Quality Report: skill-name

**Overall**: 52/64 (81%) ✅ PASS
- Structure: 11/14 (79%) ✅
- Content: 19/23 (83%) ✅
- Code Quality: 13/16 (81%) ✅
- Language: 9/11 (82%) ✅
- Bonus Points: +1 (Japanese version)

**Critical Issues**:
- File length: 520 lines (warning: use references/ for >500)
- Missing Why explanations in Advanced patterns
```



---

## Common Pitfalls

### 1. Passing Skills with < 80% Overall Score

**Problem**: Skills barely meeting 80% per category but falling short of overall threshold get published.

**Solution**: Enforce BOTH criteria: 80% per category AND 80% overall (51/64 points).

```python
# ✅ CORRECT - Strict validation
def is_passing(results: Dict[str, ValidationResult]) -> bool:
    # Check per-category threshold (80%)
    if not all(r.score >= 80 for r in results.values()):
        return False
    
    # Check overall threshold (80%, 51/64 points)
    total_passed = sum(r.passed for r in results.values())
    total_items = sum(r.total for r in results.values())
    overall_score = (total_passed / total_items) * 100
    
    return overall_score >= 80  # 51/64 = 79.7%, round to 80%
```

### 2. Ignoring Context in Code Quality Checks

**Problem**: Flagging tutorial skills for missing error handling when simplicity is intentional.

**Solution**: Allow skill-type annotations to adjust validation rules.

```yaml
# In SKILL.md frontmatter
validation_profile: tutorial  # or: production, reference, quickstart

# Adjust checks based on profile
if profile == "tutorial":
    skip_checks = ["3.4.3"]  # Error handling optional for tutorials
```

### 3. Not Re-validating After Fixes

**Problem**: Fixing one issue breaks another, but没验证.

**Solution**: Always re-run full validation after making changes.

```bash
# ❌ WRONG - Fix and assume it's good
# Edit SKILL.md...
# Done!

# ✅ CORRECT - Fix and validate
# Edit SKILL.md...
python validate_skill.py --skill my-skill --full-check
```

---

## Anti-Patterns

### Automating Quality Without Human Review

**What**: Relying solely on automated checks without manual peer review.

**Why It's Wrong**:
- Automated checks miss subjective quality issues (clarity, usefulness)
- Can't assess if examples are practical or theoretical
- Doesn't catch subtle inconsistencies

**Better Approach**: Use automation for baseline validation, human review for quality assessment.

---

## Quick Reference

### Validation Workflow

```
1. Run structure check (14 items)
   ├─ PASS: Continue
   └─ FAIL: Fix structure issues, restart

2. Run content check (23 items)
   ├─ PASS: Continue
   └─ FAIL: Improve scenarios, patterns, Values integration

3. Run code quality check (16 items)
   ├─ PASS: Continue
   └─ FAIL: Fix code examples, add DI/error handling, shorten long examples

4. Run language check (11 items)
   ├─ PASS: Calculate overall score
   └─ FAIL: Rewrite for clarity, active voice, add Japanese version

5. Overall score ≥ 80% AND all categories ≥ 80%?
   ├─ YES: ✅ PUBLISH
   └─ NO: Review failures, iterate
```

### Pass Criteria Summary

| Category | Items | Pass Threshold | Weight |
|----------|-------|----------------|--------|
| Structure | 14 | ≥ 11 (79%) | Critical |
| Content | 23 | ≥ 18 (78%) | High |
| Code Quality | 16 | ≥ 13 (81%) | High |
| Language | 11 | ≥ 9 (82%) | Medium |
| **Overall** | **64** | **≥ 51 (80%)** | **Required** |
| **Bonus** | **+2** | **Japanese + Values** | **Optional** |

---

## Best Practices Summary

1. **Run Early and Often** - Validate during writing, not just at the end
2. **Fix Structurally First** - Structure failures block everything else
3. **Automate Where Possible** - Use .ps1/.sh scripts for repetitive checks
4. **Prioritize Critical Failures** - Fix structure/content before language
5. **Target 90%+ After Revision** - First draft 80% is acceptable, revise to 90%+
6. **Document Exceptions** - Note when intentionally skipping a check
7. **Peer Review Final Draft** - Automated checks + human review
8. **Re-validate After Changes** - Don't assume fixes don't break other checks
9. **Track Improvement Over Time** - Monitor scores across skill versions
10. **Use Reports for Learning** - Analyze common failures to improve writing
11. **Leverage references/** - Move detailed content to references/ for >500 line skills
12. **Integrate Development Values** - Align Core Principles with 基礎と型、成長の複利、etc.

---

## Resources

- **[references/anti-patterns.md](references/anti-patterns.md)** - Detailed ❌ bad pattern examples and common failures
- **[references/validation-examples.md](references/validation-examples.md)** - Advanced validator implementations
- **[skill-writing-guide](../skill-writing-guide/SKILL.md)** - Learn how to write high-quality skills
- **[skill-revision-guide](../skill-revision-guide/SKILL.md)** - Fix issues found during validation
- **[Development Philosophy](../../.github/copilot-instructions.md)** - Values and coding standards

---

## Changelog

### Version 3.0.0 (2026-02-12)
- **Expanded checklist**: 56 → 64 items (+8 validation checks)
- **Added file length optimization**: 500 line recommendation with 550 line (+10%) tolerance
- **Added references/ validation**: Check for references/ directory structure
- **Added bilingual support**: Japanese version bonus point
- **Added Values integration**: Development philosophy alignment checks
- **Added code length limits**: Inline examples ≤15 lines recommended
- **Added Progressive Disclosure**: Advanced content in references/ for >500 line skills
- **Updated thresholds**: Overall 85% → 80% (51/64 points)
- **New scripts**: PowerShell (.ps1) and Bash (.sh) validation scripts

### Version 2.0.0 (2026-02-12)
- **Optimized file length**: Reduced from 780 lines to 335 lines (57% reduction)
- **Moved anti-patterns**: All ❌ bad pattern examples moved to `references/anti-patterns.md`
- **Simplified validators**: Condensed class definitions to concise pseudocode with references
- **Maintained 56-item checklist**: All validation criteria preserved
- **Added cross-references**: Links to anti-patterns.md and validation-examples.md

### Version 1.0.0 (2026-02-12)
- Initial release
- 56-item validation checklist
- 4-category scoring system
- Automated validation examples
- Report generation patterns

<!-- 
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
