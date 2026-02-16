---
name: skills-review-skill-enterprise-readiness
description: Review a skill for enterprise deployment readiness — governance, security, testing, and operational concerns.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, enterprise, governance, security, review]
  invocable: false
---

# Review Skill Enterprise Readiness

Evaluate whether a skill meets enterprise-grade requirements before deploying it to a team or organization. This workflow covers governance, security, testing, operational stability, and compliance concerns that go beyond individual quality validation.

## When to Use This Skill

Use this skill when:
- Deploying a skill to a team, department, or organization (not just personal use)
- A skill will be used in production codebases with compliance requirements
- Reviewing third-party or community-contributed skills before adoption
- Preparing skills for cross-team standardization
- Auditing existing deployed skills for enterprise policy compliance

Do **not** use this skill when:
- Writing or authoring a new skill → use `skills-author-skill`
- Validating individual skill quality (structure, content) → use `skills-validate-skill`
- The skill is for personal/experimental use only

---

## Related Skills

| Skill | Relationship |
|-------|-------------|
| [`skills-validate-skill`](../skills-validate-skill/SKILL.md) | Run quality validation first, then enterprise review |
| [`skills-author-skill`](../skills-author-skill/SKILL.md) | Author skills that pass enterprise review from the start |
| [`skills-validate-skill`](../skills-validate-skill/SKILL.md) | Validate and remediate issues found during review |

---

## Core Principles

1. **Defense in Depth** — Review security at every layer: input handling, output generation, credential management, and dependency trust (基礎と型)
2. **Governance as Enablement** — Governance processes should accelerate safe adoption, not block it. Clear criteria reduce ambiguity and speed up approvals (成長の複利)
3. **Operational Transparency** — Every skill must be observable, auditable, and rollback-ready in a team environment (継続は力)
4. **Zero Trust for AI Output** — Never assume AI-generated code or instructions are safe. Validate, sandbox, and review before execution (基礎と型 / ニュートラル)
5. **Compliance by Design** — Build compliance into skill structure from the start, not as an afterthought (温故知新)

---

## Workflow: Review a Skill for Enterprise Readiness

### Step 1 — Prerequisites Check

Confirm the skill has passed basic quality validation before enterprise review:

```
Pre-flight checklist:
├─ [ ] skills-validate-skill report exists and passes (no Critical findings)
├─ [ ] SKILL.md follows 1-skill-1-workflow structure
├─ [ ] author field is set in YAML frontmatter
├─ [ ] Bilingual versions exist (SKILL.md + references/SKILL.ja.md)
└─ [ ] Version and Changelog are present
```

If prerequisites fail, route to `skills-validate-skill` first.

### Step 2 — Security Review

Evaluate the skill for security risks:

**2a. Code Generation Safety**

```
Security checklist — Code output:
├─ [ ] No hardcoded credentials, tokens, or secrets in examples
├─ [ ] No instruction to disable security features (SSL verification, CORS, auth)
├─ [ ] Generated code includes input validation guidance
├─ [ ] SQL/command injection risks are addressed in examples
├─ [ ] File system operations use safe path handling
└─ [ ] Network operations use HTTPS by default
```

**2b. Dependency Trust**

```
Security checklist — Dependencies:
├─ [ ] All referenced packages/libraries are from trusted sources
├─ [ ] Version pinning is recommended (not "latest")
├─ [ ] No unnecessary elevated permissions required
└─ [ ] Script files (if any) are reviewed for safe execution
```

**2c. Data Handling**

```
Security checklist — Data:
├─ [ ] No PII/sensitive data in examples or templates
├─ [ ] Logging guidance excludes sensitive fields
├─ [ ] Error messages do not leak internal details
└─ [ ] Temporary files are cleaned up in workflows
```

### Step 3 — Governance Review

Evaluate organizational readiness:

**3a. Ownership and Accountability**

```
Governance checklist:
├─ [ ] Author/owner is clearly identified
├─ [ ] Maintenance responsibility is assigned
├─ [ ] Change approval process is defined (who reviews updates?)
├─ [ ] Deprecation/retirement plan exists
└─ [ ] License compatibility confirmed (MIT, Apache 2.0, etc.)
```

**3b. Scope and Boundaries**

```
Scope checklist:
├─ [ ] Skill scope is clearly bounded (no "do everything" skills)
├─ [ ] Cross-skill dependencies are documented in Related Skills
├─ [ ] The skill does not duplicate functionality of existing team skills
└─ [ ] Target audience is defined (all devs? specific team? specific role?)
```

### Step 4 — Testing and Reliability Review

Evaluate operational stability:

```
Testing checklist:
├─ [ ] Workflow steps are reproducible (same input → same output)
├─ [ ] Edge cases are documented (what happens when X fails?)
├─ [ ] Error handling guidance is present (not just happy path)
├─ [ ] Rollback procedure exists if skill produces bad output
├─ [ ] Script files (if any) have been tested on target platforms
└─ [ ] Examples compile/run without modification (copy-paste ready)
```

### Step 5 — Operational Readiness Review

Evaluate deployment and maintenance:

```
Operations checklist:
├─ [ ] Deployment method is documented (global install? repo-level?)
├─ [ ] Update/upgrade path is clear (how to get new versions)
├─ [ ] Monitoring: how to know if the skill is causing problems
├─ [ ] Feedback channel exists (issues, PR, contact)
└─ [ ] Onboarding: new team members can understand the skill quickly
```

### Step 6 — Generate Enterprise Readiness Report

Produce a structured report:

```markdown
# Enterprise Readiness Report
**Skill**: <skill-name>
**Reviewer**: <name>
**Date**: <YYYY-MM-DD>
**Verdict**: APPROVED / CONDITIONAL / REJECTED

## Summary
<1-2 sentence assessment>

## Security Review
- Status: PASS / FAIL
- Findings: <list>

## Governance Review
- Status: PASS / FAIL
- Findings: <list>

## Testing & Reliability
- Status: PASS / FAIL
- Findings: <list>

## Operational Readiness
- Status: PASS / FAIL
- Findings: <list>

## Required Actions (if CONDITIONAL)
1. <action with deadline>
2. <action with deadline>

## Recommendation
<deploy as-is / deploy with conditions / do not deploy>
```

**Verdict criteria**:
- **APPROVED**: All sections PASS, no critical findings
- **CONDITIONAL**: Minor findings exist, deploy with documented mitigations
- **REJECTED**: Critical security or governance findings, must fix before deployment

---

## Good Practices

1. **Review before deploy, not after** — Enterprise review is a gate, not a post-mortem (基礎と型)
2. **Automate repeatable checks** — Script the security and structure checks; reserve human review for judgment calls (成長の複利)
3. **Version-lock deployed skills** — Pin skill versions in enterprise environments; do not auto-update (継続は力)
4. **Maintain an approved skill registry** — Track which skills are approved, conditional, or rejected (ニュートラル)
5. **Re-review on major updates** — Any breaking change or security-related update triggers a re-review (温故知新)

---

## Common Pitfalls

### 1. Skipping Security Review for "Internal" Skills

**Problem**: Assuming internal skills are safe because they are not public.

**Why it matters**: Internal skills can still contain credential leaks, unsafe code patterns, or compliance violations.

**Fix**: Apply the same security checklist regardless of audience.

### 2. Reviewing Once and Forgetting

**Problem**: Initial review passes, but the skill evolves without re-review.

**Why it matters**: Updates may introduce new security risks or governance violations.

**Fix**: Tie re-review to the Changelog. Any version bump triggers a lightweight review.

### 3. Blocking Adoption with Excessive Process

**Problem**: Review process is so heavy that teams avoid creating skills entirely.

**Why it matters**: Defeats the purpose of skills as a productivity tool.

**Fix**: Use a tiered approach — lightweight review for low-risk skills, full review for production-critical ones.

---

## Anti-Patterns

### Rubber-Stamp Review

**What**: Approving skills without actually checking security or governance criteria.

**Why it's wrong**: Creates a false sense of compliance. Problems surface in production.

**Fix**: Use the checklists in Steps 2-5 as a minimum. At least one finding per section should be documented (even if it's "no issues found").

### One Size Fits All

**What**: Applying the full enterprise review to every skill regardless of risk level.

**Why it's wrong**: Personal utility skills and production-critical skills have different risk profiles.

**Fix**: Classify skills by deployment scope:
- **Personal**: No enterprise review needed
- **Team**: Lightweight review (Steps 1, 2a, 3b)
- **Organization**: Full review (all steps)
- **External/Public**: Full review + legal/license check

---

## Quick Reference

### Review Decision Flow

```
Skill ready for review?
│
├─ Passed skills-validate-skill? ─── No ──→ Run validation first
│
├─ Yes
│   │
│   ├─ Deployment scope?
│   │   ├─ Personal only ──→ No enterprise review needed
│   │   ├─ Team ──→ Lightweight review (Steps 1, 2a, 3b)
│   │   ├─ Organization ──→ Full review (Steps 1-6)
│   │   └─ External/Public ──→ Full review + legal check
│   │
│   └─ Generate report (Step 6)
│       ├─ APPROVED ──→ Add to approved registry, deploy
│       ├─ CONDITIONAL ──→ Deploy with documented mitigations
│       └─ REJECTED ──→ Fix findings, re-review
```

### Checklist Summary

| Category | Items | Focus |
|----------|-------|-------|
| Security — Code | 6 | Credentials, injection, safe defaults |
| Security — Dependencies | 4 | Trust, pinning, permissions |
| Security — Data | 4 | PII, logging, error messages |
| Governance | 9 | Ownership, scope, licensing |
| Testing | 6 | Reproducibility, edge cases, rollback |
| Operations | 5 | Deployment, updates, monitoring |
| **Total** | **34** | |

---

## Resources

- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — Quality validation (run first)
- [skills-author-skill](../skills-author-skill/SKILL.md) — Author enterprise-ready skills from the start

---
