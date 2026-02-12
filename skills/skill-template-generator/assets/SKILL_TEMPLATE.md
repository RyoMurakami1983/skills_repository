<!-- 
This template is designed to be a single SKILL.md file.
Additional support files (references/, assets/, etc.) should only be created
when following GitHub Copilot's official guidelines. Prefer single-file completion.

Note: This template shows structural examples only. Actual skills should contain 7-10 pattern sections.
-->

---
name: your-skill-name-here
description: One-line description of what problem this skill solves (100 chars max)
invocable: false
tags: [tag1, tag2, tag3]  # Add 3-5 technology stack-focused tags
author: RyoMurakami1983  # For identifying skills created by this system (optional)
---

# Your Skill Title Here

## Related Skills

- **`related-skill-1`** - Brief description of how it relates
- **`related-skill-2`** - Brief description of how it relates

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
4. **Principle 4** - One-line summary of key concept (optional)
5. **Principle 5** - One-line summary of key concept (optional)

---

## Pattern 1: [Pattern Name]

### Overview

Brief explanation of what this pattern solves and why it matters.

### Basic Example

```csharp
// ✅ CORRECT - Simple, most common case
public class Example
{
    // Implementation with inline comments explaining WHY
    public void DoSomething()
    {
        // Key decision explained
    }
}
```

### When to Use

Use this pattern when:
- Specific condition A
- Specific condition B
- Specific condition C

| Scenario | Recommendation | Why |
|----------|----------------|-----|
| Scenario A | Use Pattern X | Brief explanation |
| Scenario B | Use Pattern Y | Brief explanation |
| Scenario C | See Pattern 2 | Brief explanation |

### With Configuration

```csharp
// ✅ CORRECT - With options/configuration
public class ConfiguredExample
{
    private readonly IOptions<Settings> _options;
    
    public ConfiguredExample(IOptions<Settings> options)
    {
        _options = options;
    }
    
    public void DoSomething()
    {
        var setting = _options.Value.SomeSetting;
        // Use setting with explanation
    }
}

// In Program.cs or Startup
builder.Services.Configure<Settings>(
    builder.Configuration.GetSection("Settings"));
```

### Advanced Pattern

```csharp
// ✅ CORRECT - Production-grade with error handling
public class AdvancedExample
{
    public async Task DoSomethingAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            // Complex implementation with:
            // - Error handling
            // - Cancellation support
            // - Resource management
        }
        catch (SpecificException ex)
        {
            // Specific error handling
            throw;
        }
    }
}
```

---

## Pattern 2: [Another Pattern Name]

### Overview

Brief explanation of this pattern and when it differs from Pattern 1.

### Simple Example

```csharp
// ✅ CORRECT - Basic usage
```

### Common Variation

```csharp
// ✅ CORRECT - Alternative approach for different scenario
```

### Comparison with Pattern 1

| Aspect | Pattern 1 | Pattern 2 |
|--------|-----------|-----------|
| Use Case | Description | Description |
| Performance | Metric/description | Metric/description |
| Complexity | Low/Medium/High | Low/Medium/High |
| When to Use | Scenario | Scenario |

---

## Pattern 3: [Third Pattern Name]

[Similar structure to Pattern 1 and 2...]

---

<!-- 
Note: This template includes only Patterns 1-3 for brevity.
Actual skills should contain 7-10 pattern sections following the same structure:
- Overview
- Basic Example
- When to Use
- With Configuration
- Advanced Pattern (Production-Grade)
-->

## Common Pitfalls

### 1. Pitfall Name - Brief Description

**Problem**: What users typically do wrong and why it fails.

```csharp
// ❌ WRONG - What not to do
public class BadExample
{
    public void DoSomethingWrong()
    {
        // Anti-pattern with explanation of why it's bad
    }
}
```

**Solution**: How to fix it and why this approach works.

```csharp
// ✅ CORRECT - The right approach
public class GoodExample
{
    public void DoSomethingRight()
    {
        // Correct pattern with explanation
    }
}
```

### 2. Another Common Pitfall

```csharp
// ❌ WRONG - Silent failure example
var result = SomeOperation(); // Missing error handling

// ✅ CORRECT - Explicit error handling
try
{
    var result = SomeOperation();
    // Success path
}
catch (SpecificException ex)
{
    // Handle specific error
}
```

### 3. Third Common Pitfall

[Similar format...]

---

## Anti-Patterns

### Architectural Anti-Pattern Name

**What**: Description of the anti-pattern at an architectural level.

```csharp
// ❌ WRONG - Architectural mistake
public class AntiPatternExample
{
    // Design flaw that causes problems at scale
    // or violates core principles
}
```

**Why It's Wrong**:
- Reason 1: Violates principle X
- Reason 2: Causes problem Y
- Reason 3: Doesn't scale

**Better Approach**:

```csharp
// ✅ CORRECT - Architectural solution
public class BetterDesign
{
    // Proper design that follows core principles
}
```

### Breaking Changes Pattern

```csharp
// ❌ WRONG - "Bug fix" that breaks users
public async Task<Result> GetResultAsync(int id)  // Was sync!
{
    // "Fixed" to be async - but breaks all existing callers
}

// ✅ CORRECT - Add new method, deprecate old
[Obsolete("Use GetResultAsync instead")]
public Result GetResult(int id) => GetResultAsync(id).GetAwaiter().GetResult();

public async Task<Result> GetResultAsync(int id)
{
    // New async implementation
}
```

---

## Quick Reference

### Decision Tree

```
Start: What do you need?
├─► Need A? → Use Pattern 1
├─► Need B? → Use Pattern 2
├─► Need C? → Use Pattern 3
└─► Complex scenario? → Combine patterns (see Advanced section)
```

### Common Scenarios Cheat Sheet

| Scenario | Pattern | Code Snippet |
|----------|---------|--------------|
| Simple case | Pattern 1 | `new Example()` |
| With config | Pattern 1 + Config | `services.Configure<Settings>()` |
| Async operation | Pattern 2 | `await DoAsync()` |
| Error handling | Pattern 3 | `try/catch` with specific exceptions |

---

## Best Practices Summary

1. **Practice 1** - Brief description of recommendation
2. **Practice 2** - Brief description of recommendation
3. **Practice 3** - Brief description of recommendation
4. **Practice 4** - Brief description of recommendation
5. **Practice 5** - Brief description of recommendation

---

## Resources

- [Official Documentation Name](https://example.com/docs)
- [Related Article/Blog Post](https://example.com/article)
- [Reference Implementation](https://github.com/example/repo)
- [Community Discussion](https://example.com/discussion)

---

## Changelog

Change history (only substantial changes recorded. See CHANGELOG.md for details):

### Version 1.0.0 (YYYY-MM-DD)
- Initial version
- Patterns 1-3 documented
- Common pitfalls identified

### Version 1.1.0 (YYYY-MM-DD) (Optional)
- Added Pattern 4
- Updated examples for .NET X
- Clarified anti-pattern Y

<!-- 
When changelog grows large, move to CHANGELOG.md.
Keep only the latest 3-5 versions in SKILL.md and note "See CHANGELOG.md for full history."
-->
