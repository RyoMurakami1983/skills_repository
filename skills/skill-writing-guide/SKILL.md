---
name: skill-writing-guide
description: Guide for writing high-quality GitHub Copilot agent skills. Use when creating SKILL.md files.
author: RyoMurakami1983
tags: [copilot, agent-skills, documentation, writing-guide]
invocable: false
---

# Skill Writing Guide

A comprehensive guide for writing high-quality GitHub Copilot agent skills following official specifications and best practices.

## When to Use This Skill

Use this skill when:
- Building a new SKILL.md file from scratch for GitHub Copilot agents
- Learning required structure and sections for agent skills documentation
- Understanding code example best practices and formatting guidelines
- Designing effective section layouts including When to Use and Patterns
- Writing clear, actionable skill documentation for developers
- Ensuring compliance with GitHub Copilot and Claude specifications

---

## Related Skills

- **`skill-template-generator`** - Generate structured SKILL.md templates
- **`skill-quality-validation`** - Validate and score skill quality
- **`skill-revision-guide`** - Revise and maintain existing skills

---

## Core Principles

1. **Single File Principle** - Complete all content in SKILL.md; avoid additional support files
2. **Reader-First Design** - Enable readers to determine relevance within 5 seconds  
3. **Progressive Learning** - Structure examples from Simple → Intermediate → Advanced
4. **Problem-Solution Focus** - Always explain "why" before "how" (成長の複利)
5. **Practical Utility** - Provide copy-paste ready, compilable code examples
6. **Values Integration** - Align with development philosophy (基礎と型、継続は力、ニュートラル)

---

## Pattern 1: YAML Frontmatter Structure

### Overview

The YAML frontmatter defines metadata that determines when and how the skill is activated. Proper configuration is critical for skill discoverability.

### Basic Example

```yaml
---
name: your-skill-name
description: One-line description of what problem this skill solves (100 chars max)
invocable: false
---
```

### When to Use

| Scenario | Field Configuration | Why |
|----------|-------------------|-----|
| Personal skill | `invocable: false` | Standard for most skills |
| Requires specific activation | `invocable: true` | User must explicitly invoke |
| Technology-specific | Add `tags: [tech1, tech2]` | Improves discoverability |

### With Configuration

```yaml
---
name: skill-writing-guide
description: Guide for writing high-quality GitHub Copilot agent skills. Use when creating new SKILL.md files or structuring skill content.
author: RyoMurakami1983
tags: [copilot, agent-skills, documentation]
invocable: false
---
```

### Advanced Pattern (Production-Grade)

```yaml
---
name: wpf-mvvm-patterns
description: Implement MVVM in WPF with domain-driven design, dependency injection, and testability. Use when building enterprise WPF applications with complex business logic.
author: RyoMurakami1983
tags: [wpf, mvvm, ddd, csharp, dotnet]
invocable: false
license: MIT
version: 1.2.0
---
```

**Field Guidelines**:
- **name**: kebab-case, must match directory name, max 64 characters
- **description**: 100 chars max, include "Use when..." for activation context
- **author**: Use `RyoMurakami1983` for skills created by this system
- **tags**: 3-5 technology-focused tags
- **invocable**: Usually `false`

---

## Pattern 2: "When to Use This Skill" Section

### Overview

The first H2 section after the title. Enables readers to quickly determine if the skill is relevant to their current task.

### Basic Example

```markdown
## When to Use This Skill

Use this skill when:
- Designing public APIs for NuGet packages
- Making changes to existing public APIs
- Planning wire format changes
```

### When to Use

- ✅ **DO**: Write 5-8 specific, action-oriented scenarios
- ✅ **DO**: Start each item with a verb (Designing, Implementing, Building)
- ✅ **DO**: Keep each item to 50-100 characters
- ❌ **DON'T**: Use abstract phrases ("When you need quality code")
- ❌ **DON'T**: List more than 10 items (overwhelming)

### With Configuration

```markdown
## When to Use This Skill

Use this skill when:
- Building enterprise WPF applications with complex business logic
- Implementing MVVM pattern with domain-driven design
- Integrating APIs with retry/circuit breaker policies
- Setting up dependency injection in WPF projects
- Designing testable ViewModels and Services
- Managing application state across multiple views
```

### Advanced Pattern (Production-Grade)

Include context-specific scenarios with role-based filtering:

```markdown
## When to Use This Skill

Use this skill when:
- **Architects**: Designing multi-tenant WPF application architecture
- **Senior Developers**: Implementing advanced MVVM patterns with CQRS
- **Team Leads**: Reviewing pull requests for MVVM compliance
- **Junior Developers**: Learning MVVM fundamentals in WPF
- **DevOps**: Setting up CI/CD pipelines for WPF applications
```

---

## Pattern 3: "Core Principles" Section

### Overview

Defines the philosophical foundation and guiding principles of the skill. Keep it concise (3-5 principles).

### Basic Example

```markdown
## Core Principles

1. **Separation of Concerns** - Views, ViewModels, and Models have distinct responsibilities
2. **Dependency Inversion** - Depend on abstractions, not concrete implementations
3. **Testability First** - Design for unit testing from day one
```

### When to Use

- ✅ **DO**: Limit to 3-5 principles
- ✅ **DO**: Format as **Bold Name** - Short explanation (30-50 chars)
- ❌ **DON'T**: Write lengthy explanations (save for dedicated sections)

> 📚 **Advanced examples**: See `references/core-principles-examples.md`

---

## Pattern 4: Pattern Sections (7-10 Required)

### Overview

Each pattern section documents a specific approach, technique, or implementation strategy. A complete skill should contain 7-10 pattern sections.

### Basic Example

```markdown
## Pattern 1: [Pattern Name]

### Overview
Brief explanation (2-3 sentences)

### Basic Example
```csharp
// ✅ CORRECT - Simple case
```

### When to Use
- Condition A
- Condition B

### Advanced Pattern
```csharp
// ✅ CORRECT - Production-ready
```
```

### When to Use

Structure patterns to enable progressive learning:
1. **Overview**: What problem does this solve?
2. **Basic Example**: Simplest possible implementation
3. **When to Use**: Decision criteria
4. **Advanced**: Production-grade with error handling

> 📚 **Full pattern examples**: See `references/pattern-examples.md`

---

## Pattern 5: Code Example Best Practices

### Overview

Code examples must be practical, compilable, and progressively complex. Follow the ✅/❌ marker convention consistently.

### Basic Example

```csharp
// ✅ CORRECT - Async all the way
public async Task<Data> GetDataAsync()
{
    return await _client.GetAsync("/api/data");
}

// ❌ WRONG - Blocking async code
public Data GetData()
{
    return _client.GetAsync("/api/data").Result; // Deadlock risk
}
```

### When to Use

**Use ✅/❌ markers**:
- ✅ `// ✅ CORRECT - Reason` for good examples
- ❌ `// ❌ WRONG - Reason` for anti-patterns
- Always pair wrong examples with correct alternatives

**Include context**:
- ✅ Add using statements
- ✅ Show DI configuration
- ✅ Include error handling in advanced examples
- ❌ Don't use pseudocode or placeholders like "..."

> 📚 **Production-grade examples**: See `references/advanced-examples.md`

---

## Pattern 6: Comparison Tables

### Overview

Tables enable at-a-glance decision making. Use them to compare patterns, tools, or scenarios.

### Basic Example

```markdown
| Scenario | Recommendation | Why |
|----------|----------------|-----|
| Read-only data | AsNoTracking() | No change tracking overhead |
| Update entity | Tracking | Automatic change detection |
```

### When to Use

**Decision Support Tables**:
- 3 columns: Scenario, Recommendation, Why
- 5-10 rows maximum
- Bold the recommended option

**Technology Comparison Tables**:
- Include: Tool, Type, Performance, Use When
- Highlight recommended tools in bold

### With Configuration

```markdown
| Feature | Pattern A | Pattern B | Pattern C |
|---------|-----------|-----------|-----------|
| **Complexity** | Low | Medium | High |
| **Performance** | Good | Better | Best |
| **Maintainability** | High | Medium | Low |
| **Use Case** | Simple CRUD | Complex queries | Bulk operations |
| **Recommendation** | ✅ Start here | Scale to this | **Only if needed** |
```

---

## Pattern 7: Anti-Patterns vs. Common Pitfalls

### Overview

Distinguish between architectural mistakes (Anti-Patterns) and implementation errors (Common Pitfalls).

### Basic Example

**Common Pitfall**:
```csharp
// ❌ WRONG - Resource not disposed
var stream = File.OpenRead("file.txt");

// ✅ CORRECT - Automatically disposed
using var stream = File.OpenRead("file.txt");
```

### When to Use

| Type | Focus | Example |
|------|-------|---------|
| **Anti-Pattern** | Architecture, design principles | God Class, Tight Coupling |
| **Common Pitfall** | Implementation mistakes | Forgetting await, null refs |

> 📚 **Detailed anti-patterns**: See `references/anti-patterns.md`

---

## Pattern 8: Optimizing for 500-Line Limit

### Overview

Apply progressive disclosure to keep SKILL.md under 500 lines while maintaining quality.

### Core Strategy

**Progressive Disclosure**: Essential content in SKILL.md, details in references/

```
┌─────────────────────────────────────┐
│ SKILL.md (≤500 lines)               │
│ • ✅ Good patterns (5-15 lines)     │
│ • Basic examples                    │
│ • Simple comparisons                │
└─────────────────────────────────────┘
           ↓ references
┌─────────────────────────────────────┐
│ references/ (loaded when needed)    │
│ • ❌ Anti-pattern details           │
│ • 📚 Advanced implementations       │
│ • ⚙️ Complex configurations         │
└─────────────────────────────────────┘
```

### What to Keep in SKILL.md

✅ **Keep** (High Priority):
1. Good patterns with ✅ markers (5-15 lines each)
2. Basic YAML/markdown examples
3. Simple comparisons (✅ vs ❌, 2-3 lines each)
4. Core principles and decision trees

### What to Move to references/

📤 **Move** (Lower Priority):
1. ❌ Detailed anti-pattern code → `references/anti-patterns.md`
2. 📚 Production-grade implementations → `references/advanced-examples.md`
3. ⚙️ Complex configurations → `references/configuration.md`
4. 🌏 Japanese translations → `references/SKILL.ja.md`

### Decision Tree

| Question | Answer | Action |
|----------|--------|--------|
| Code example > 15 lines? | Yes | Consider moving to references/ |
| Essential for basic understanding? | No | Move to references/ |
| Is it an anti-pattern? | Yes | Move to references/anti-patterns.md |
| Is it advanced/production-grade? | Yes | Move to references/advanced-examples.md |
| Is it a good basic example? | Yes | **Keep in SKILL.md** |

### Basic Example

✅ **CORRECT - Concise good pattern**:
```yaml
---
name: wpf-databinding
description: Guide for WPF data binding patterns. Use when implementing MVVM.
---
```

> 📚 **Anti-patterns and detailed examples**: See `references/anti-patterns.md`

### When to Use

Use this pattern when:
- Your SKILL.md exceeds 500 lines
- You have many code examples (both ✅ and ❌)
- You have production-grade implementations
- You want to reduce cognitive load

---

## Good Practices

### 1. Start with "When to Use" for Quick Discovery

**What**: Place "When to Use This Skill" as first H2 with 5-8 specific scenarios.

**Why**: Enables 5-second relevance check; improves AI discoverability.

```markdown
## When to Use This Skill
Use this skill when:
- Building enterprise WPF applications with complex business logic
- Implementing MVVM pattern with dependency injection
```

**Values**: ニュートラル（形式知化で誰もが理解可能）

### 2. Use ✅/❌ Markers Consistently

**What**: Prefix code with ✅ CORRECT or ❌ WRONG + brief reason.

**Why**: Eliminates ambiguity; enables quick scanning; reinforces contrast learning.

```csharp
// ✅ CORRECT - Async all the way
var result = await SomeAsyncMethod();

// ❌ WRONG - Deadlock risk  
var result = SomeAsyncMethod().Result;
```

**Values**: 基礎と型（明確なパターン）/ 成長の複利（対比学習）

### 3. Progressive Disclosure for Length Management

**What**: Keep essential patterns in SKILL.md (~500 lines); move details to references/.

**Why**: Maintains AI performance; reduces cognitive load; preserves deep-dive content.

```
SKILL.md (≤550)      references/
├─ ✅ Good patterns  ├─ anti-patterns.md
├─ Basic examples    ├─ advanced-examples.md  
└─ Core principles   └─ skill_jp.md (日本語)
```

**Values**: 基礎と型（最小形式で最大可能性）

### 4. Explain WHY in Comments and Text

**What**: Always include "Why" for design decisions, not just "What".

**Why**: Transforms 暗黙知 into 形式知; supports compound learning growth.

```python
timeout = 30  # Why: Production analysis showed 10s insufficient for large datasets
```

**Values**: 成長の複利（学習資産化）/ ニュートラル（形式知化）

---

## Common Pitfalls

### 1. Violating the Single File Principle

**Problem**: Creating multiple support files fragments content.

**Solution**: Consolidate into SKILL.md; use references/ only for 500+ line overflow.

```
❌ WRONG: skill-name/ with README.md, examples.md, guidelines.md
✅ CORRECT: skill-name/SKILL.md (single source of truth)
```

### 2. Vague "When to Use" Scenarios

**Problem**: Abstract scenarios don't help determine relevance.

**Solution**: Write specific, action-oriented scenarios.

```markdown
❌ WRONG: "When you want to write good code"
✅ CORRECT: "Building enterprise WPF apps with complex business logic"
```

### 3. Missing ✅/❌ Markers in Code

**Problem**: Readers can't distinguish good from bad.

**Solution**: Always use explicit markers.

```csharp
❌ WRONG - Deadlock risk: var result = SomeAsyncMethod().Result;
✅ CORRECT - Async all the way: var result = await SomeAsyncMethod();
```

---

## Anti-Patterns

### Overloading a Single Skill with Too Many Patterns

**What**: Including 20+ pattern sections in one skill, making it overwhelming.

**Why It's Wrong**: Exceeds 500-line limit, violates progressive disclosure, reduces scannability.

**Better Approach**: Split into focused skills (7-10 patterns each).

```markdown
❌ WRONG: wpf-everything-guide (30 patterns, 1000+ lines)

✅ CORRECT:
- wpf-mvvm-fundamentals (8 patterns)
- wpf-data-binding-patterns (7 patterns)
- wpf-performance-optimization (7 patterns)
```

### Creating Skills Without Clear Activation Criteria

**What**: Writing generic descriptions without "Use when..." specifications.

**Why It's Wrong**: GitHub Copilot can't determine when to activate; poor discoverability.

**Better Approach**: Include specific activation scenarios in description.

```yaml
❌ WRONG:
description: A helpful guide for WPF development

✅ CORRECT:
description: Implement MVVM in WPF with DI and testability. Use when building enterprise WPF applications.
```

### Mixing Good and Bad Examples Without Clear Labels

**What**: Showing code without ✅/❌ markers; ambiguous recommendations.

**Why It's Wrong**: Readers and AI can't distinguish good from bad; violates 形式知化.

**Better Approach**: Always use explicit markers and pair anti-patterns with solutions.

```csharp
❌ WRONG - No labels:
var result = SomeAsyncMethod().Result;

✅ CORRECT - Clear labels:
// ❌ WRONG - Deadlock risk
var result = SomeAsyncMethod().Result;

// ✅ CORRECT - Async all the way  
var result = await SomeAsyncMethod();
```

> 📚 **Detailed anti-patterns with examples and remediation**: See `references/anti-patterns.md`

---

## Quick Reference

### Skill Structure Checklist

- [ ] YAML frontmatter with name, description, author, tags
- [ ] H1 title matching skill name
- [ ] Related Skills section
- [ ] "When to Use This Skill" as first H2 section (5-8 scenarios)
- [ ] Core Principles (3-5 principles)
- [ ] 7-10 Pattern sections with progressive examples
- [ ] Common Pitfalls (3-5 items)
- [ ] Anti-Patterns (2-4 items)
- [ ] Quick Reference or Decision Tree
- [ ] Best Practices Summary
- [ ] Resources section
- [ ] Changelog (link to CHANGELOG.md if large)

### Section Writing Checklist

- [ ] Use ✅/❌ markers consistently in code examples
- [ ] Include using statements and DI configuration
- [ ] Write inline comments explaining WHY, not WHAT
- [ ] Keep SKILL.md under 500 lines
- [ ] Use tables for decision support
- [ ] Start each "When to Use" item with a verb
- [ ] Make Core Principles independent and concise
- [ ] Structure patterns: Overview → Basic → Configuration → Advanced

### Code Quality Checklist

- [ ] All code examples are compilable
- [ ] Advanced examples include error handling
- [ ] Async methods use CancellationToken
- [ ] Resources are properly disposed (using statements)
- [ ] DI configuration is shown where relevant

---

## Best Practices Summary

1. **Single File Principle** - Consolidate in SKILL.md; references/ for overflow only
2. **Clear Activation** - Specific "Use when..." in description
3. **Progressive Complexity** - Basic → Configuration → Advanced
4. **Consistent Markers** - ✅/❌ prefixes in all code
5. **Action-Oriented** - Verb-led "When to Use" items
6. **Explain WHY** - Comments show decisions, not syntax
7. **7-10 Patterns** - Complete coverage without overload
8. **Comparison Tables** - Enable quick decision-making
9. **Distinguish Types** - Separate anti-patterns from pitfalls
10. **500-Line Limit** - Concise main file; details to references/

---

## Resources

- [GitHub Copilot Agent Skills Documentation](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Claude Skills Documentation](https://claude.com/docs/skills/overview)
- [Agent Skills Specification](https://agentskills.io/specification)
- [SKILL_TEMPLATE.md](../../.copilot/docs/SKILL_TEMPLATE.md) - English template
- [SKILL_TEMPLATE.ja.md](../../.copilot/docs/SKILL_TEMPLATE.ja.md) - Japanese template

---

## Changelog

See CHANGELOG.md for full history. Recent changes:

### Version 2.1.0 (2026-02-13)
- **Added Good Practices section**: 4 essential good practices with Values integration
- **Enhanced Anti-Patterns section**: Added "Mixing Good and Bad Examples" anti-pattern
- **Japanese consolidation**: Moved from references/SKILL.ja.md to skill_jp.md for better organization
- **Progressive Disclosure**: Added reference to detailed anti-patterns in references/anti-patterns.md

### Version 2.0.0 (2026-02-12)
- **Expanded Core Principles**: Added Values integration (基礎と型、成長の複利、温故知新、継続は力、ニュートラル)
- **Updated Pattern 8**: 500-line recommendation with 550-line (+10%) tolerance
- **Development Philosophy Integration**: Aligned patterns with development Values
- **Enhanced guidance**: Emphasized "Why" explanations for compound learning growth
- **Quality validation alignment**: Synchronized with skill-quality-validation 64-item checklist

### Version 1.0.0 (2026-02-12)
- Initial release
- 8 pattern sections documented
- Code example best practices defined
- Anti-patterns vs. pitfalls clarified
- Progressive Disclosure strategy introduced

<!-- 
Japanese version available at skill_jp.md
日本語版は skill_jp.md を参照してください
-->
