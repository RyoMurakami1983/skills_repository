---
name: skill-writing-guide
description: Guide for writing high-quality GitHub Copilot agent skills. Use when creating new SKILL.md files, structuring skill content, or learning skill writing best practices.
author: RyoMurakami1983
tags: [copilot, agent-skills, documentation, writing-guide]
invocable: false
---

# Skill Writing Guide

A comprehensive guide for writing high-quality GitHub Copilot agent skills following official specifications and best practices.

## Related Skills

- **`skill-template-generator`** - Generate structured SKILL.md templates
- **`skill-quality-validation`** - Validate and score skill quality
- **`skill-revision-guide`** - Revise and maintain existing skills

## When to Use This Skill

Use this skill when:
- Creating a new SKILL.md file from scratch
- Learning the structure and sections required for skills
- Understanding code example best practices
- Designing section layouts (When to Use, Core Principles, Patterns)
- Writing clear and actionable skill documentation
- Ensuring compliance with GitHub Copilot/Claude skill specifications

---

## Core Principles

1. **Single File Principle** - Complete all content in SKILL.md; avoid additional support files unless following official guidelines
2. **Reader-First Design** - Enable readers to determine relevance within 5 seconds
3. **Progressive Learning** - Structure examples from Simple → Intermediate → Advanced (継続は力 - continuous improvement)
4. **Problem-Solution Focus** - Always explain "why" before "how" (成長の複利 - compound growth through learning)
5. **Practical Utility** - Provide copy-paste ready, compilable code examples
6. **Values Integration** - Align content with development philosophy (基礎と型、成長の複利、温故知新、継続は力、ニュートラル)

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

## Common Pitfalls

### 1. Violating the Single File Principle

**Problem**: Creating multiple support files (README.md, examples.md, etc.) fragments the content.

```
❌ WRONG Structure:
skill-name/
├── SKILL.md
├── README.md          # Redundant
├── examples.md        # Should be in SKILL.md
└── guidelines.md      # Should be in SKILL.md
```

**Solution**: Consolidate all content into SKILL.md. Use `references/` only for supplementary material that would exceed 500 lines.

```
✅ CORRECT Structure:
skill-name/
└── SKILL.md           # Single source of truth
```

### 2. Vague "When to Use" Scenarios

**Problem**: Abstract scenarios don't help readers determine relevance.

```markdown
❌ WRONG:
- When you want to write good code
- Use this for WPF applications
- Helpful for developers
```

**Solution**: Write specific, action-oriented scenarios.

```markdown
✅ CORRECT:
- Building enterprise WPF applications with complex business logic
- Implementing MVVM pattern with dependency injection
- Designing testable ViewModels with INotifyPropertyChanged
```

### 3. Missing ✅/❌ Markers in Code

**Problem**: Readers can't distinguish good practices from anti-patterns.

```csharp
// UNCLEAR - Is this good or bad?
var result = SomeAsyncMethod().Result;
```

**Solution**: Always use explicit markers.

```csharp
// ❌ WRONG - Deadlock risk with .Result
var result = SomeAsyncMethod().Result;

// ✅ CORRECT - Async all the way
var result = await SomeAsyncMethod();
```

---

## Anti-Patterns

### Overloading a Single Skill with Too Many Patterns

**What**: Including 20+ pattern sections in one skill, making it overwhelming.

**Why It's Wrong**:
- Exceeds recommended 500-line limit
- Readers can't scan the content effectively
- Violates progressive disclosure principle

**Better Approach**: Split into multiple focused skills.

```markdown
❌ WRONG: wpf-everything-guide (30 patterns)

✅ CORRECT:
- wpf-mvvm-fundamentals (8 patterns)
- wpf-data-binding-patterns (7 patterns)
- wpf-performance-optimization (7 patterns)
```

### Creating Skills Without Clear Activation Criteria

**What**: Writing generic descriptions that don't specify when to use the skill.

```yaml
❌ WRONG:
description: A helpful guide for WPF development
```

**Why It's Wrong**:
- GitHub Copilot can't determine when to activate the skill
- Users won't discover the skill when relevant

**Better Approach**: Include "Use when..." in the description.

```yaml
✅ CORRECT:
description: Implement MVVM in WPF with dependency injection and testability. Use when building enterprise WPF applications with complex business logic.
```

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

1. **Single File Principle** - Keep all content in SKILL.md; avoid fragmenting across multiple files
2. **Clear Activation Criteria** - Write specific "Use when..." scenarios in the description
3. **Progressive Complexity** - Structure examples from Basic → Configuration → Advanced
4. **Consistent Markers** - Use ✅/❌ prefixes for all code examples
5. **Action-Oriented Scenarios** - Start "When to Use" items with verbs (Building, Implementing, Designing)
6. **Explain WHY** - Code comments should explain decisions, not syntax
7. **7-10 Patterns** - Include enough patterns for completeness without overwhelming
8. **Comparison Tables** - Use tables for at-a-glance decision making
9. **Distinguish Anti-Patterns from Pitfalls** - Separate architectural issues from implementation mistakes
10. **500-Line Limit** - Keep SKILL.md concise; move supplementary content to references/

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
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
