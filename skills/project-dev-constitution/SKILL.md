---
name: project-dev-constitution
description: Create and maintain a .github/copilot-instructions.md development constitution that captures product essence, architecture principles, UI policy, and test strategy. Use when starting a new project, when implementation decisions feel inconsistent, or when onboarding new team members.
---

# Project Development Constitution

A workflow for creating and maintaining `.github/copilot-instructions.md` as a living document. Captures the product's core purpose, architecture principles, domain design rules, UI policy, test strategy, and Git conventions — keeping every implementation decision grounded in an explicit foundation.

**Origin**: This skill was distilled from the experience of building `copilot-instructions.md` for the `rakugaki_writer` project. The core insight: "without an explicit architecture foundation, domain boundaries blur as implementation accelerates."

## When to Use This Skill

Use this skill when:
- Starting a new project and making the first architectural decisions
- Diagnosing an existing project whose architecture has become ambiguous or inconsistently applied
- Onboarding a new team member who needs to understand design intent
- Identifying drift after a retrospective reveals "implementation decisions were inconsistent"
- Grounding an AI coding agent before it starts a new session

**Not this skill**: `git-initial-setup` handles Git operation defaults (hooks, branch protection). This skill handles *design philosophy* documentation.

## Related Skills

- **`furikaeri-practice`** — Triggers constitution updates when new insights surface
- **`git-initial-setup`** — Git operational setup (branch protection, hooks)
- **`git-commit-practices`** — Commit conventions referenced in Step 6
- **`github-issue-intake`** — Capture architecture decisions as issues

---

## Dependencies

- A `.github/` directory in the project root (create if absent)
- No tooling required — this is a documentation workflow

## Core Principles

1. **Domain-First** — Core domain is defined before implementation begins (基礎と型)
2. **Living Document** — Append and revise; don't rewrite from scratch (継続は力)
3. **Explicit Over Implicit** — Record decisions and their rationale, not just outcomes (温故知新)
4. **AI-Readable** — Written so a coding agent can use it as grounding context (余白の設計)
5. **Minimal Ceremony** — One file, plain markdown; avoid tooling overhead (ニュートラル)

---

## Workflow: Build the Development Constitution

### Step 1: Define the Product Essence

Write 1–3 sentences answering: "Who does this project serve, and what problem does it solve?"

Three required elements:

| Element | Question | Example |
|---------|----------|---------|
| **Who** | Target user | Solo writers who want distraction-free writing |
| **What problem** | Pain being solved | Context-switching breaks creative flow |
| **Core value** | The irreducible benefit | The app gets out of the way |

```markdown
## 製品本質 / Product Essence

- **Who**: Solo writers who want distraction-free, offline-first writing
- **What problem**: Context-switching between editing modes and toolbars breaks creative flow
- **Core value**: The editor disappears — only the writing remains
```

This becomes the north star for every feature decision. If a proposed feature contradicts the core value, it belongs in a different product.

Use when starting any project, or when stakeholders debate feature priorities.

> **Values**: 基礎と型 / ニュートラル

### Step 2: Record Architecture Principles

Document the adopted architectural pattern, layer structure, and dependency rules.

Required elements:
- **Layer structure** (e.g., DDD: domain / application / infrastructure / presentation)
- **Dependency direction** (e.g., "UI depends on domain. Domain must not depend on UI.")
- **Tech stack with selection rationale** (why this stack, not just what)

```markdown
## アーキテクチャ方針 / Architecture Principles

### Layer Structure
- `domain/` — Entities, ValueObjects, UseCases, Repository interfaces (ports)
- `application/` — Orchestration, command/query handlers
- `infrastructure/` — File system, OS APIs, external storage (adapters)
- `presentation/` — UI components, state binding

### Dependency Rules
- Dependency direction: presentation → application → domain ← infrastructure (never reversed)
- Domain layer has zero knowledge of UI frameworks, file system, or network
- Infrastructure implements domain interfaces (ports); it never defines them

### Tech Stack
- **Tauri + Rust** — Cross-platform native runtime; offline-first without Electron overhead
- **React + TypeScript** — Component model with strong type safety
- **Vite** — Fast dev iteration, minimal config overhead
```

Use when setting up a new project or when a team member asks "where does this code belong?"

> **Values**: 基礎と型 / 温故知新

### Step 3: Domain-First Checklist

A five-item checklist to run before starting any new feature. Prevents the most common drift: building UI before the domain model is clear.

```markdown
## コアドメイン先行チェックリスト / Domain-First Checklist

Before implementing any new feature:
- [ ] Identified what domain model changes are needed (Entity / ValueObject / UseCase)
- [ ] Implementation starts from the domain layer — not from the UI
- [ ] Ports (interfaces) are defined before infrastructure is written
- [ ] Domain-layer tests are written before application/UI layers
- [ ] No infrastructure dependency (file system / DB / OS API) leaks into domain
```

**Why this matters**: Starting from the UI is natural — it's visible and concrete. But UI-first development embeds accidental complexity into the domain. The checklist creates a moment of deliberate pause before each feature.

Use before every new feature, story, or significant bug fix.

> **Values**: 基礎と型 / 余白の設計

### Step 4: Codify the UI Policy

Record UI design decisions as policy rather than personal preference. Future contributors (human and AI) need to know what is intentional.

Required elements:
- **Inspiration / design reference** — The aesthetic target
- **Explicit prohibitions** — What must not be built (as important as what should)
- **Accessibility commitment** — Minimum viable accessibility stance

```markdown
## UIポリシー / UI Policy

### Design Direction
- Notion-inspired: minimal header, context-dependent toolbar, focus on content canvas
- Single-surface editor: no modal dialogs for routine operations

### Prohibitions
- Do NOT pack mode buttons into the header toolbar
- Do NOT show formatting controls when no text is selected
- Do NOT add persistent sidebars without explicit user opt-in

### Accessibility
- Keyboard navigation required for all primary actions
- Sufficient color contrast (WCAG AA minimum)
- Screen reader labels on all icon-only buttons
```

Use when implementing any UI component or reviewing a UI-related PR.

> **Values**: 基礎と型 / ニュートラル

### Step 5: Define the Test Strategy

Establish testing principles before writing the first test. Inconsistent testing philosophy compounds over time.

Required elements:
- **Strategy** — TDD / BDD / After (pick one as default)
- **Priority order** — Which layers get tested first
- **Mock policy** — When mocking is allowed vs. forbidden
- **File placement** — Convention for test file location

```markdown
## テスト方針 / Test Strategy

### Strategy
TDD for domain and application layers; integration tests for infrastructure adapters.

### Priority
1. Domain layer (pure business logic — no mocks needed)
2. Application layer (use case orchestration — mock domain ports)
3. Infrastructure layer (adapter contracts — test against real dependencies)
4. UI layer (interaction tests — focus on user workflows, not implementation)

### Mock Policy
- Domain layer: No mocks. If you need a mock, the dependency belongs in infrastructure.
- Application layer: Mock domain ports (interfaces) only.
- Infrastructure layer: Use real implementations for adapter tests.

### File Placement
- Unit tests: colocated with source (`*.test.ts`)
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`
```

Use when setting up a project, or when a PR introduces a test pattern that violates the policy.

> **Values**: 基礎と型 / 継続は力

### Step 6: Git and Coding Conventions

Record the commit format, branch strategy, and language-specific style rules. These should align with `git-commit-practices`.

```markdown
## Git・コーディング規約 / Git and Coding Conventions

### Commit Format (Conventional Commits)
- `feat:` — New feature
- `fix:` — Bug fix
- `refactor:` — No behavior change
- `test:` — Test additions / modifications
- `docs:` — Documentation only
- `chore:` — Tooling, dependencies

### Branch Strategy
- `main` — Production-ready; protected (no direct push)
- `feat/<issue-number>-<short-description>` — Feature branches
- `fix/<issue-number>-<short-description>` — Bug fix branches

### Coding Style
- TypeScript strict mode enabled
- No `any` without explicit justification in a comment
- Pure functions for domain logic; side effects only in infrastructure/presentation
- Rust: follow `clippy` defaults; no `unwrap()` in production paths
```

> **Values**: 継続は力 / 基礎と型

### Step 7: Update Cadence and Triggers

The development constitution is a living document. Define when it gets updated.

**Update triggers**:

| Trigger | Action |
|---------|--------|
| Retrospective surfaces new insight (`furikaeri-practice` Step 5) | Add a line to the relevant section |
| Architecture decision made | Record it in Step 2 with rationale |
| A decision pattern was applied 3+ times | Promote it to an explicit rule |
| New team member asks "why did we do X?" | Add the answer to the constitution |

**Update discipline**:
- **Append and revise** — Do not rewrite the document; add to it
- **Date-stamp significant changes** in the Update Log section
- **Do not update for every PR** — Update when a decision has proven durable

Use when closing a sprint, completing a `furikaeri-practice` session, or recording an ADR (Architecture Decision Record).

> **Values**: 継続は力 / 温故知新 / 成長の複利

---

## Common Pitfalls

1. **Writing the constitution after implementation**
   Fix: Block implementation until Steps 1–3 are complete. The constitution protects the domain model, not the UI.

2. **Too abstract to be actionable**
   Fix: Every section must contain at least one concrete prohibition or concrete example. Vague principles ("keep it simple") provide no constraint.

3. **Never updated after creation**
   Fix: Add the constitution review to `furikaeri-practice` Step 5 as a default Skill-ization Check. If insights are surfaced, update the document.

4. **Copying a template without customizing**
   Fix: Step 1 (Product Essence) is non-negotiable. A generic "North Star" that fits any project fits none.

5. **Conflating this with a README**
   Fix: The README is for users and contributors; the constitution is for AI agents and design decision tracking. Keep them separate.

---

## Anti-Patterns

- Writing the constitution as a one-time exercise and archiving it
- Using the constitution as a constraints document ("you can't do X") without rationale
- Adding every coding style preference (that belongs in linting config)
- Letting AI agents generate the constitution without human editorial on Step 1

---

## Quick Reference

### Development Constitution Template

```markdown
# 開発憲法 / Development Constitution

## 製品本質 / Product Essence
<!-- Who: -->
<!-- What problem: -->
<!-- Core value: -->

## アーキテクチャ方針 / Architecture Principles
<!-- Layers: -->
<!-- Dependency rules: -->
<!-- Tech stack + rationale: -->

## コアドメイン先行チェックリスト / Domain-First Checklist

Before implementing any new feature:
- [ ] Identified what domain model changes are needed (Entity / ValueObject / UseCase)
- [ ] Implementation starts from the domain layer — not from the UI
- [ ] Ports (interfaces) are defined before infrastructure is written
- [ ] Domain-layer tests are written before application/UI layers
- [ ] No infrastructure dependency leaks into domain

## UIポリシー / UI Policy
<!-- Design direction / inspiration: -->
<!-- Prohibitions: -->
<!-- Accessibility: -->

## テスト方針 / Test Strategy
<!-- Strategy (TDD/BDD/After): -->
<!-- Priority order: -->
<!-- Mock policy: -->
<!-- File placement: -->

## Git・コーディング規約 / Git and Coding Conventions
<!-- Commit format: -->
<!-- Branch strategy: -->
<!-- Language-specific style: -->

## 更新ログ / Update Log
- YYYY-MM-DD: Initial constitution created
```

### Step Summary

| Step | Output | Trigger to Skip |
|------|--------|-----------------|
| 1 Product Essence | 1–3 sentence north star | Never — required for all projects |
| 2 Architecture Principles | Layer diagram + dependency rules | Prototype with no architecture intent |
| 3 Domain-First Checklist | 5-item pre-feature gate | Project has no domain model |
| 4 UI Policy | Design direction + prohibitions | Non-UI project |
| 5 Test Strategy | Strategy + priority + mock policy | Spike / throwaway prototype |
| 6 Git Conventions | Commit format + branch strategy | Solo, no-PR workflow |
| 7 Update Cadence | Triggers + discipline | N/A — always maintain |

### Decision Table

| Situation | Action |
|-----------|--------|
| New project, day one | Complete Steps 1–6 before writing implementation code |
| Existing project, architecture drifting | Complete Steps 1–3; skip or skim Steps 4–6 if policy exists |
| New team member | Share the constitution file; walk through Step 1 together |
| Retrospective insight about design | Update the relevant section via Step 7 |
| AI agent starting a new session | Point the agent to `.github/copilot-instructions.md` as grounding |

---

## Resources

- Eric Evans, *Domain-Driven Design* — foundational reading for Step 2–3
- Michael Feathers, *Working Effectively with Legacy Code* — motivates domain isolation
- [Conventional Commits](https://www.conventionalcommits.org/) — Step 6 commit format
- `furikaeri-practice` — triggers Step 7 update cadence
- `git-commit-practices` — detailed commit workflow aligned with Step 6
