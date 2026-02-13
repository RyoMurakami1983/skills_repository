# Anti-Patterns in Skill Writing (Detailed Guide)

This document provides comprehensive details on anti-patterns to avoid when writing GitHub Copilot agent skills. For a quick summary, see the main SKILL.md file.

---

## Anti-Pattern 1: Overloading a Single Skill with Too Many Patterns

### What

Including 20+ pattern sections in one skill, making it overwhelming for both AI agents and human readers.

### Why It's Wrong

1. **Exceeds Cognitive Load**: Readers cannot effectively scan or absorb content
2. **Violates 500-Line Limit**: Makes the file too large for optimal AI agent processing
3. **Breaks Progressive Disclosure**: Dumps all information at once instead of layering complexity
4. **Poor Discoverability**: Readers can't quickly find relevant patterns

### Symptoms

- SKILL.md exceeds 1000+ lines
- Table of contents has 20+ pattern sections
- Readers report feeling overwhelmed
- GitHub Copilot struggles to activate the skill appropriately

### Concrete Examples

❌ **WRONG - Monolithic Skill**:
```markdown
# wpf-everything-guide

## Pattern 1: Basic XAML Binding
## Pattern 2: INotifyPropertyChanged
## Pattern 3: Commands
## Pattern 4: Data Templates
## Pattern 5: Control Templates
## Pattern 6: Styles
## Pattern 7: Resources
## Pattern 8: Animations
## Pattern 9: Behaviors
## Pattern 10: Attached Properties
... (20 more patterns)
```

✅ **CORRECT - Focused Skills**:
```markdown
# wpf-mvvm-fundamentals (8 patterns)
- Pattern 1: INotifyPropertyChanged
- Pattern 2: Commands  
- Pattern 3: ViewModels
- Pattern 4: Data Binding Basics
- Pattern 5: Dependency Injection
- Pattern 6: Unit Testing ViewModels
- Pattern 7: MVVM Messaging
- Pattern 8: Common Pitfalls

# wpf-data-binding-patterns (7 patterns)
- Pattern 1: OneWay vs TwoWay
- Pattern 2: Data Templates
- Pattern 3: Item Templates
- Pattern 4: Value Converters
- Pattern 5: MultiBinding
- Pattern 6: RelativeSource
- Pattern 7: Validation Rules

# wpf-performance-optimization (7 patterns)
- Pattern 1: Virtualization
- Pattern 2: Async Data Loading
- Pattern 3: UI Thread Management
- Pattern 4: Memory Profiling
- Pattern 5: Render Optimization
- Pattern 6: XAML Compilation
- Pattern 7: Benchmarking
```

### Better Approach

1. **Identify Coherent Topics**: Group related patterns into themes
2. **Split into Multiple Skills**: Create 2-4 focused skills instead of one mega-skill
3. **Cross-Reference**: Use "Related Skills" section to link related skills
4. **Target 7-10 Patterns**: Keep each skill focused and manageable

### Impact on Values

- **Violates "基礎と型"**: No clear foundational structure when overloaded
- **Violates "ニュートラル"**: Too complex for universal understanding

---

## Anti-Pattern 2: Creating Skills Without Clear Activation Criteria

### What

Writing generic descriptions in YAML frontmatter that don't specify when GitHub Copilot should activate the skill.

### Why It's Wrong

1. **Poor AI Discovery**: GitHub Copilot cannot determine when the skill is relevant
2. **Wasted Activation**: Skill may be loaded when not applicable
3. **User Frustration**: Developers can't find the skill when they need it
4. **Ambiguous Purpose**: Unclear value proposition

### Symptoms

- Description lacks "Use when..." clause
- Description is generic ("helpful guide", "useful tool")
- No technology-specific tags
- Skill rarely gets activated despite being relevant

### Concrete Examples

❌ **WRONG - Vague Descriptions**:
```yaml
---
name: wpf-guide
description: A helpful guide for WPF development
tags: [wpf]
---
```

```yaml
---
name: api-patterns
description: Best practices for APIs
---
```

```yaml
---
name: testing-guide
description: Information about testing
tags: [testing]
---
```

✅ **CORRECT - Specific Activation Criteria**:
```yaml
---
name: wpf-mvvm-patterns
description: Implement MVVM in WPF with domain-driven design, dependency injection, and testability. Use when building enterprise WPF applications with complex business logic.
author: RyoMurakami1983
tags: [wpf, mvvm, ddd, csharp, dotnet]
invocable: false
---
```

```yaml
---
name: rest-api-versioning
description: Design and implement API versioning strategies with backward compatibility. Use when planning breaking changes to public REST APIs or managing multiple API versions.
author: RyoMurakami1983
tags: [api, rest, versioning, dotnet, aspnet]
invocable: false
---
```

```yaml
---
name: tdd-standard-practice
description: Standardize a production TDD workflow with test lists and Red-Green-Refactor. Use when building MVP or production features requiring stable behavior under change.
author: RyoMurakami1983
tags: [tdd, testing, workflow, ci, quality]
invocable: false
---
```

### Better Approach

1. **Include "Use when..."**: Explicitly state activation scenarios in description
2. **Be Specific**: Mention technologies, patterns, and use cases
3. **Add Relevant Tags**: Include 3-5 technology-focused tags
4. **100-Character Limit**: Keep description concise but informative
5. **Action-Oriented**: Focus on what the developer is trying to accomplish

### Description Formula

```
[Action Verb] + [Core Technology/Pattern] + [Additional Context] + "Use when" + [Specific Scenarios]
```

Example:
```
Implement MVVM in WPF with dependency injection and testability. Use when building enterprise WPF applications with complex business logic.
```

### Impact on Values

- **Violates "ニュートラル"**: Lack of clarity excludes potential users
- **Violates "成長の複利"**: Poor discoverability prevents learning

---

## Anti-Pattern 3: Mixing Good and Bad Examples Without Clear Labels

### What

Showing code examples without ✅ CORRECT or ❌ WRONG markers, leaving readers and AI agents confused about which approach is recommended.

### Why It's Wrong

1. **Ambiguity**: Readers cannot distinguish good practices from anti-patterns
2. **AI Confusion**: GitHub Copilot may learn and replicate bad patterns
3. **Knowledge Transfer Failure**: Violates 形式知化 (explicit knowledge transfer)
4. **Learning Inefficiency**: Contrast learning requires clear labeling

### Symptoms

- Code examples lack ✅/❌ markers
- Comments don't explain if code is good or bad
- Multiple examples shown without recommendations
- Readers ask "Which approach should I use?"

### Concrete Examples

❌ **WRONG - Unlabeled Examples**:
```csharp
// Approach 1
var result = SomeAsyncMethod().Result;

// Approach 2  
var result = await SomeAsyncMethod();
```

```python
# Example 1
timeout = 10

# Example 2
timeout = 30
```

```typescript
// Pattern A
const data = await fetch(url).then(r => r.json());

// Pattern B
const response = await fetch(url);
const data = await response.json();
```

✅ **CORRECT - Clear Labeling**:
```csharp
// ❌ WRONG - Deadlock risk with .Result
var result = SomeAsyncMethod().Result;

// ✅ CORRECT - Async all the way
var result = await SomeAsyncMethod();
```

```python
# ❌ WRONG - Too short for large datasets
timeout = 10

# ✅ CORRECT - Based on production analysis (2026-02-10)
timeout = 30  # Why: Large dataset processing requires more time
```

```typescript
// ❌ WRONG - No error handling, unclear intent
const data = await fetch(url).then(r => r.json());

// ✅ CORRECT - Explicit error handling, clear steps
const response = await fetch(url);
if (!response.ok) {
  throw new Error(`HTTP ${response.status}: ${response.statusText}`);
}
const data = await response.json();
```

### Better Approach

1. **Always Use Markers**: Prefix every code example with ✅ or ❌
2. **Pair Bad with Good**: Show the wrong way, then the correct way
3. **Explain Why**: Include brief comments explaining the rationale
4. **Consistent Format**: Use same marker style throughout the skill

### Marker Guidelines

| Marker | When to Use | Format |
|--------|-------------|--------|
| ✅ CORRECT | Good practice, recommended approach | `// ✅ CORRECT - [Brief reason]` |
| ❌ WRONG | Anti-pattern, mistake to avoid | `// ❌ WRONG - [What's wrong]` |
| ⚠️ CAUTION | Works but has limitations | `// ⚠️ CAUTION - [Limitation]` |
| 📝 NOTE | Additional context | `// 📝 NOTE - [Context]` |

### Advanced Pattern

For complex scenarios, use tables to compare approaches:

```markdown
| Aspect | ❌ Anti-Pattern | ✅ Good Practice |
|--------|----------------|------------------|
| **Approach** | `result = task.Result` | `result = await task` |
| **Risk** | Deadlock in UI thread | No blocking |
| **Performance** | Blocks thread | Async throughout |
| **Use Case** | Never | Always in async code |
```

### Impact on Values

- **Violates "ニュートラル"**: Ambiguity prevents 形式知化 (formalization)
- **Violates "成長の複利"**: Poor contrast learning reduces effectiveness
- **Violates "基礎と型"**: Unclear patterns prevent proper foundation

---

## Summary

These anti-patterns represent common mistakes that undermine skill quality:

1. **Overloading**: Creates cognitive overload and violates 500-line principle
2. **Vague Activation**: Prevents discovery and proper AI activation
3. **Unlabeled Examples**: Causes ambiguity and learning confusion

### Remediation Checklist

For each skill you write, verify:

- [ ] Total lines < 550 (500 + 10% tolerance)
- [ ] Pattern count: 7-10 (not 20+)
- [ ] Description includes "Use when..." clause
- [ ] All code examples have ✅/❌ markers
- [ ] Tags are specific and technology-focused
- [ ] Related skills are cross-referenced
- [ ] Progressive disclosure is applied (references/ for details)

### Values Alignment

- **基礎と型**: Clear patterns, focused scope, minimal forms
- **成長の複利**: Effective learning through proper labeling and structure
- **ニュートラル**: Universal understanding through explicit formalization
- **継続は力**: Small, focused skills are easier to maintain
- **温故知新**: Learn from common mistakes, apply modern best practices

---

## See Also

- **SKILL.md** - Main skill writing guide (concise version)
- **skill_jp.md** - 日本語版詳細ガイド (comprehensive Japanese guide)
- **SKILL_TEMPLATE.md** - Skill template for starting new skills
- **skill-quality-validation** - Automated quality checks

---

Last Updated: 2026-02-13
