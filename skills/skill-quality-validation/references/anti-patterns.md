# Anti-Patterns and Common Validation Failures

Detailed examples of ❌ INCORRECT patterns across all validation categories. Use this reference to understand WHY certain approaches fail validation and HOW to fix them.

---

## Table of Contents

1. [Structure Anti-Patterns](#structure-anti-patterns)
2. [Content Anti-Patterns](#content-anti-patterns)
3. [Code Quality Anti-Patterns](#code-quality-anti-patterns)
4. [Language & Expression Anti-Patterns](#language-expression-anti-patterns)
5. [Validation Process Anti-Patterns](#validation-process-anti-patterns)

---

## Structure Anti-Patterns

### ❌ INCORRECT: Multiple Markdown Files

**Problem**: Skill contains README.md, examples.md, advanced-usage.md in addition to SKILL.md.

**Why It Fails**: Check 1.1 - Skills must be self-contained in a single SKILL.md file.

```
skill-my-feature/
├── SKILL.md           ← Main file
├── README.md          ❌ Violates single-file rule
├── examples.md        ❌ Violates single-file rule
└── advanced.md        ❌ Violates single-file rule
```

**Fix**: Consolidate all content into SKILL.md, or move supporting content to `references/` subdirectory.

---

### ❌ INCORRECT: Missing Required YAML Fields

**Problem**: YAML frontmatter incomplete or malformed.

**Why It Fails**: Check 1.2 - Must include name, description, and invocable fields.

```yaml
# ❌ WRONG - Missing fields
---
name: my-skill
---

# ❌ WRONG - Invalid invocable value
---
name: my-skill
description: Does something
invocable: yes  # Should be true/false
---
```

**Fix**:

```yaml
# ✅ CORRECT
---
name: my-skill
description: Validate input against schema rules
invocable: true
---
```

---

### ❌ INCORRECT: Name Mismatch

**Problem**: Directory name is `skill-data-validation` but YAML name is `data-validator`.

**Why It Fails**: Check 1.3 - Directory name and YAML name must match exactly.

```yaml
# Directory: skill-data-validation/
---
name: data-validator  # ❌ Doesn't match directory
---
```

**Fix**:

```yaml
# Directory: skill-data-validation/
---
name: skill-data-validation  # ✅ Matches directory
---
```

---

### ❌ INCORRECT: Description Too Long or Vague

**Problem**: Description exceeds 100 characters or uses abstract language.

**Why It Fails**: Check 1.4 - Description must be ≤100 chars and problem-focused.

```yaml
# ❌ WRONG - Too long (132 chars)
---
description: This skill helps you write better code by validating quality, checking adherence to best practices, and generating comprehensive reports.
---

# ❌ WRONG - Too vague
---
description: Improve code quality and follow best practices
---
```

**Fix**:

```yaml
# ✅ CORRECT - Concise and specific (99 chars)
---
description: Validate skill quality with 56-point checklist. Generate reports with scores and fixes.
---
```

---

### ❌ INCORRECT: Wrong Section Order

**Problem**: "Core Principles" appears before "When to Use This Skill".

**Why It Fails**: Check 1.5 - "When to Use This Skill" must be first H2 section.

```markdown
# Skill Name

## Core Principles  ❌ Wrong order

## When to Use This Skill  ❌ Should be first
```

**Fix**:

```markdown
# Skill Name

## When to Use This Skill  ✅ First

## Core Principles  ✅ Second
```

---

### ❌ INCORRECT: Too Few or Too Many Patterns

**Problem**: Skill contains only 3 pattern sections or 15 pattern sections.

**Why It Fails**: Check 1.7 - Skills should have 7-10 pattern sections.

```markdown
## Pattern 1: Basic Usage
## Pattern 2: Advanced Usage
## Pattern 3: Edge Cases
# ❌ Only 3 patterns - too few
```

**Fix**: Break down broad patterns into specific scenarios, or consolidate overly granular patterns.

---

## Content Anti-Patterns

### ❌ INCORRECT: "When to Use" - Too Few Scenarios

**Problem**: Only 3 scenarios listed when 5-8 are required.

**Why It Fails**: Check 2.1.1 - Need 5-8 specific scenarios.

```markdown
## When to Use This Skill

- Validating code
- Checking quality
- Generating reports
# ❌ Only 3 scenarios
```

**Fix**:

```markdown
## When to Use This Skill

- Reviewing a completed SKILL.md file before publishing
- Assessing skill quality against official standards
- Generating quality reports with scores and improvement recommendations
- Identifying structural or content issues in skills
- Validating compliance with GitHub Copilot/Claude specifications
- Performing peer reviews of skill documentation
# ✅ 6 scenarios - specific and actionable
```

---

### ❌ INCORRECT: "When to Use" - Doesn't Start with Verb

**Problem**: Scenarios don't begin with action verbs.

**Why It Fails**: Check 2.1.2 - Each scenario should start with verb (Designing, Implementing, etc.).

```markdown
## When to Use This Skill

- You need to validate skills  ❌ Starts with "You"
- Quality checks are required  ❌ Starts with noun
- For code review purposes     ❌ Starts with preposition
```

**Fix**:

```markdown
## When to Use This Skill

- Validating skills before publication  ✅
- Checking quality against standards    ✅
- Reviewing code during peer review     ✅
```

---

### ❌ INCORRECT: "When to Use" - Too Short or Too Long

**Problem**: Scenarios are < 50 chars or > 100 chars.

**Why It Fails**: Check 2.1.3 - Each scenario should be 50-100 chars.

```markdown
## When to Use This Skill

- Validate skills  ❌ 15 chars - too short
- Performing comprehensive validation of all skill components including structure, content, code quality, language, and generating detailed reports with actionable recommendations  ❌ 175 chars - too long
```

**Fix**:

```markdown
## When to Use This Skill

- Validating skill structure and content before publication  ✅ 60 chars
- Generating quality reports with scores and improvement tips  ✅ 65 chars
```

---

### ❌ INCORRECT: "When to Use" - Abstract Phrases

**Problem**: Uses vague terms like "good code", "best practices", "quality software".

**Why It Fails**: Check 2.1.4 - Avoid abstract phrases; be specific.

```markdown
## When to Use This Skill

- Writing good code that follows best practices  ❌ "good code", "best practices"
- Ensuring quality software development          ❌ "quality software"
- Implementing proper error handling             ❌ "proper"
```

**Fix**:

```markdown
## When to Use This Skill

- Implementing try-catch blocks with specific exception types  ✅
- Configuring dependency injection for testable services       ✅
- Validating input against JSON schema with error messages     ✅
```

---

### ❌ INCORRECT: Patterns Missing "When to Use" Guidance

**Problem**: Pattern section lacks guidance on when to apply it.

**Why It Fails**: Check 2.2.4 - Each pattern must include "When to Use" subsection.

```markdown
## Pattern 3: Advanced Configuration

### Overview
Configure complex scenarios with multiple options.

### Example
[code example...]

# ❌ Missing "When to Use" subsection
```

**Fix**:

```markdown
## Pattern 3: Advanced Configuration

### Overview
Configure complex scenarios with multiple options.

### When to Use
- Multi-tenant applications requiring per-tenant config
- Feature flags that change behavior dynamically
- A/B testing scenarios with different configurations

### Example
[code example...]
```

---

### ❌ INCORRECT: Duplicate Content Across Patterns

**Problem**: Pattern 2 and Pattern 5 both explain the same concept.

**Why It Fails**: Check 2.2.5 - Each pattern must cover unique scenarios.

```markdown
## Pattern 2: Error Handling
Use try-catch blocks to handle exceptions...

## Pattern 5: Exception Management
Use try-catch blocks to handle exceptions...
# ❌ Duplicate of Pattern 2
```

**Fix**: Differentiate patterns (e.g., Pattern 2: Basic error handling, Pattern 5: Distributed error handling with correlation IDs).

---

## Code Quality Anti-Patterns

### ❌ INCORRECT: Non-Compilable Code

**Problem**: Code example has syntax errors or missing imports.

**Why It Fails**: Check 3.1.1 - All code must compile without errors.

```csharp
// ❌ WRONG - Missing using statements
public class UserService {
    public async Task<User> GetUserAsync(int id) {
        var user = await _dbContext.Users.FindAsync(id);  // DbContext not imported
        return user;
    }
}
```

**Fix**:

```csharp
// ✅ CORRECT
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;

public class UserService {
    private readonly AppDbContext _dbContext;
    
    public async Task<User> GetUserAsync(int id) {
        var user = await _dbContext.Users.FindAsync(id);
        return user;
    }
}
```

---

### ❌ INCORRECT: No Progressive Complexity

**Problem**: Examples jump from trivial to advanced without intermediate steps.

**Why It Fails**: Check 3.2.1 - Show progression: Basic → Intermediate → Advanced.

```markdown
## Pattern 1: Usage

### Basic Example
```csharp
var result = DoSomething();
```

### Advanced Example
```csharp
var result = await _mediator.Send(
    new ComplexCommand { /* 50 lines of config */ }
);
// ❌ No intermediate steps between basic and advanced
```
```

**Fix**: Add intermediate example showing gradual complexity increase.

---

### ❌ INCORRECT: Inconsistent Marker Usage

**Problem**: Some examples use ✅/❌, others use "Good/Bad" comments.

**Why It Fails**: Check 3.3.1 - Use ✅/❌ markers consistently.

```csharp
// Good - Dependency injection  ❌ Should use ✅ marker
public class UserService {
    private readonly IUserRepository _repository;
}

// ❌ WRONG - Hardcoded dependency
public class UserService {
    private readonly UserRepository _repository = new UserRepository();
}
```

**Fix**:

```csharp
// ✅ CORRECT - Dependency injection
public class UserService {
    private readonly IUserRepository _repository;
}

// ❌ WRONG - Hardcoded dependency
public class UserService {
    private readonly UserRepository _repository = new UserRepository();
}
```

---

### ❌ INCORRECT: Comments Explain WHAT Not WHY

**Problem**: Comments repeat what code does instead of explaining intent.

**Why It Fails**: Check 3.3.3 - Comments should explain WHY, not WHAT.

```csharp
// ❌ WRONG - Comments explain WHAT (obvious from code)
// Get user from database
var user = await _dbContext.Users.FindAsync(id);

// Set status to active
user.Status = UserStatus.Active;

// Save changes
await _dbContext.SaveChangesAsync();
```

**Fix**:

```csharp
// ✅ CORRECT - Comments explain WHY (intent/business logic)
// Need to activate account before sending welcome email per GDPR compliance
var user = await _dbContext.Users.FindAsync(id);
user.Status = UserStatus.Active;

// Single transaction to prevent race condition with concurrent activations
await _dbContext.SaveChangesAsync();
```

---

### ❌ INCORRECT: Missing DI Configuration

**Problem**: Code uses dependency injection but doesn't show DI setup.

**Why It Fails**: Check 3.4.1 - Show DI container registration.

```csharp
// ❌ WRONG - Shows usage but not configuration
public class UserService {
    private readonly IUserRepository _repository;
    
    public UserService(IUserRepository repository) {
        _repository = repository;
    }
}
// Missing: How to register IUserRepository in DI container
```

**Fix**:

```csharp
// ✅ CORRECT - Shows both usage and configuration
public class UserService {
    private readonly IUserRepository _repository;
    
    public UserService(IUserRepository repository) {
        _repository = repository;
    }
}

// DI Configuration
services.AddScoped<IUserRepository, UserRepository>();
services.AddScoped<UserService>();
```

---

### ❌ INCORRECT: Missing Error Handling

**Problem**: Production-grade example without try-catch or validation.

**Why It Fails**: Check 3.4.2 - Production examples must include error handling.

```csharp
// ❌ WRONG - No error handling
public async Task<User> GetUserAsync(int id) {
    var user = await _dbContext.Users.FindAsync(id);
    return user;  // What if user is null? What if DB is down?
}
```

**Fix**:

```csharp
// ✅ CORRECT - Includes error handling
public async Task<User> GetUserAsync(int id) {
    try {
        var user = await _dbContext.Users.FindAsync(id);
        
        if (user == null) {
            throw new NotFoundException($"User {id} not found");
        }
        
        return user;
    }
    catch (DbUpdateException ex) {
        _logger.LogError(ex, "Database error retrieving user {UserId}", id);
        throw new DataAccessException("Failed to retrieve user", ex);
    }
}
```

---

### ❌ INCORRECT: Missing Resource Disposal

**Problem**: IDisposable resources not properly disposed.

**Why It Fails**: Check 3.4.5 - Use using statements for IDisposable.

```csharp
// ❌ WRONG - HttpClient not disposed
public async Task<string> FetchDataAsync(string url) {
    var client = new HttpClient();
    var response = await client.GetStringAsync(url);
    return response;
}
```

**Fix**:

```csharp
// ✅ CORRECT - Proper disposal with using statement
public async Task<string> FetchDataAsync(string url) {
    using var client = new HttpClient();
    var response = await client.GetStringAsync(url);
    return response;
}

// ✅ BETTER - Inject IHttpClientFactory for reusability
public class DataService {
    private readonly IHttpClientFactory _httpClientFactory;
    
    public async Task<string> FetchDataAsync(string url) {
        using var client = _httpClientFactory.CreateClient();
        return await client.GetStringAsync(url);
    }
}
```

---

## Language & Expression Anti-Patterns

### ❌ INCORRECT: Passive Voice Overuse

**Problem**: Sentences use passive voice excessively.

**Why It Fails**: Check 5.1.1 - Use active voice for clarity.

```markdown
# ❌ WRONG - Passive voice
The validation is performed by the system.
The configuration is loaded from the file.
The error should be handled by the caller.
```

**Fix**:

```markdown
# ✅ CORRECT - Active voice
The system performs validation.
Load configuration from the file.
The caller handles the error.
```

---

### ❌ INCORRECT: Long, Complex Sentences

**Problem**: Sentences exceed 20 words, making them hard to parse.

**Why It Fails**: Check 5.1.2 - Keep sentences under 20 words.

```markdown
# ❌ WRONG - 35 words
When implementing dependency injection in ASP.NET Core applications, it is important to understand the different service lifetimes (transient, scoped, singleton) and when to use each one appropriately based on your application's requirements.
```

**Fix**:

```markdown
# ✅ CORRECT - Broken into clear sentences
ASP.NET Core supports three service lifetimes: transient, scoped, and singleton.
Choose the lifetime based on your application's needs.
Transient creates new instances per request.
Scoped creates one instance per HTTP request.
Singleton creates one instance for the application lifetime.
```

---

### ❌ INCORRECT: Ambiguous Language

**Problem**: Uses "should", "may", "might" without clear guidance.

**Why It Fails**: Check 5.1.4 - Use imperative form: "Use", "Avoid", "Ensure".

```markdown
# ❌ WRONG - Ambiguous
You might want to consider using async/await.
Error handling should probably be added.
It may be better to use dependency injection.
```

**Fix**:

```markdown
# ✅ CORRECT - Imperative
Use async/await for I/O operations.
Add error handling for production code.
Use dependency injection for testability.
```

---

### ❌ INCORRECT: Undefined Acronyms

**Problem**: Uses DI, CQRS, DDD without defining them.

**Why It Fails**: Check 5.2.3 - Define acronyms on first use.

```markdown
# ❌ WRONG
Implement CQRS with DDD for complex domains.
# What do CQRS and DDD mean?
```

**Fix**:

```markdown
# ✅ CORRECT
Implement Command Query Responsibility Segregation (CQRS) with Domain-Driven Design (DDD) for complex domains.
# Subsequent uses can just say CQRS and DDD
```

---

### ❌ INCORRECT: Inconsistent Terminology

**Problem**: Uses "repository", "data access", "DAO" interchangeably.

**Why It Fails**: Check 5.2.1 - Use consistent terminology throughout.

```markdown
# ❌ WRONG - Inconsistent
Pattern 1: Inject IUserRepository
Pattern 2: Configure the data access layer
Pattern 3: Register the UserDAO
```

**Fix**:

```markdown
# ✅ CORRECT - Consistent
Pattern 1: Inject IUserRepository
Pattern 2: Configure the repository layer
Pattern 3: Register the UserRepository
```

---

### ❌ INCORRECT: Poor Scannability

**Problem**: No visual hierarchy, dense text blocks, no highlighting.

**Why It Fails**: Check 5.3.1-5.3.3 - Content must be scannable.

```markdown
# ❌ WRONG - Wall of text
This pattern is used when you need to implement dependency injection in your application and you want to follow SOLID principles. You should register your dependencies in the DI container during application startup. The container will manage the lifetime of your dependencies and inject them where needed. This makes your code more testable and maintainable.
```

**Fix**:

```markdown
# ✅ CORRECT - Scannable

## When to Use
- Implementing dependency injection
- Following SOLID principles
- Improving testability

## Key Steps
1. **Register** dependencies in DI container
2. **Configure** lifetimes (transient/scoped/singleton)
3. **Inject** via constructor parameters

**Benefits**: Better testability and maintainability
```

---

## Validation Process Anti-Patterns

### ❌ INCORRECT: Checking Only Overall Score

**Problem**: Skill scores 85% overall but Structure category is 60%.

**Why It Fails**: Must pass BOTH per-category (≥80%) AND overall (≥85%).

```python
# ❌ WRONG - Only checks overall
def is_passing(total_passed: int, total_items: int) -> bool:
    return (total_passed / total_items) >= 0.85

# Example: 47/55 (85%) passes, but Structure is 6/10 (60%)
```

**Fix**:

```python
# ✅ CORRECT - Checks both criteria
def is_passing(results: Dict[str, ValidationResult]) -> bool:
    # Check per-category threshold
    for category, result in results.items():
        if result.score < 80:
            return False
    
    # Check overall threshold
    total_passed = sum(r.passed for r in results.values())
    total_items = sum(r.total for r in results.values())
    return (total_passed / total_items) >= 0.85
```

---

### ❌ INCORRECT: Not Re-validating After Fixes

**Problem**: Fix one issue, assume entire skill is now valid.

**Why It Fails**: Fixes can introduce new failures.

```bash
# ❌ WRONG
# 1. Run validation → Pattern count is 5 (need 7-10)
# 2. Add 3 more patterns
# 3. Done! ← Didn't re-validate

# ✅ CORRECT
# 1. Run validation → Pattern count is 5
# 2. Add 3 more patterns
# 3. Re-run FULL validation
# 4. New failure: Pattern 7 missing "When to Use" subsection
# 5. Fix Pattern 7
# 6. Re-run validation again
# 7. All checks pass ✅
```

---

### ❌ INCORRECT: Ignoring Context in Validation

**Problem**: Flagging tutorial-level skill for missing error handling.

**Why It Fails**: Validation should adjust for skill purpose.

```python
# ❌ WRONG - One-size-fits-all validation
def validate_code_quality(skill: Skill) -> ValidationResult:
    if not has_error_handling(skill):
        return Failure("Missing error handling")
    # Always requires error handling, even for tutorials
```

**Fix**:

```python
# ✅ CORRECT - Context-aware validation
def validate_code_quality(skill: Skill) -> ValidationResult:
    profile = skill.frontmatter.get('validation_profile', 'production')
    
    if profile == 'tutorial':
        # Error handling optional for educational simplicity
        pass
    elif profile == 'production':
        if not has_error_handling(skill):
            return Failure("Production skills must include error handling")
    
    return Success()
```

---

## Summary

**Most Common Failures by Category**:

1. **Structure**: Wrong section order (1.5), too few patterns (1.7)
2. **Content**: Abstract "When to Use" scenarios (2.1.4), duplicate patterns (2.2.5)
3. **Code Quality**: Missing error handling (3.4.2), missing DI config (3.4.1)
4. **Language**: Passive voice overuse (5.1.1), long sentences (5.1.2)

**Fix Priority**:
1. Structure issues (block everything else)
2. Content completeness (core value)
3. Code quality (production-readiness)
4. Language polish (final refinement)

---

## Related Resources

- **[SKILL.md](../SKILL.md)** - Main validation guide with ✅ correct patterns
- **[validation-examples.md](validation-examples.md)** - Advanced code examples and validators
- **[SKILL_QUALITY_CHECKLIST.md](../../../.copilot/docs/SKILL_QUALITY_CHECKLIST.md)** - Full 56-item checklist
