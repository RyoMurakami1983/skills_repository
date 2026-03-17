---
name: dotnet
description: >
  Route .NET requests to the right existing dotnet skill or deployment workflow.
  Use when the user says "dotnet", ".NET", "C#", "WPF", "EF Core", or
  related platform terms but has not named the exact skill yet.
---

# .NET Entry Skill

Use this skill as a thin entry point when the user clearly needs `.NET` guidance but the best existing skill is still ambiguous. Why: broad platform requests often arrive before the user knows whether they need WPF, data, bootstrap, testing, or deployment guidance.

This skill does not replace the direct use of concrete skills such as `dotnet-project-structure` or `dotnet-wpf-mvvm-patterns`. Its job is to route quickly, then get out of the way.

## When to Use This Skill

Use this skill when:
- Interpreting a broad `.NET` or `C#` request before the right skill is obvious
- Routing a new WPF application request into the most relevant WPF-focused skills
- Mapping solution bootstrap questions to project-structure, DI, configuration, or package-management skills
- Directing EF Core, serialization, and database topics to the right data-oriented skills
- Guiding a team on whether to deploy a curated category set into `.github/skills/`

## Decision Table

| Your intent | Route | What to do |
| --- | --- | --- |
| Start a new `.NET` solution or modernize repo structure | `dotnet-project-structure` | Use the project-structure workflow first, then add adjacent infra skills only when needed. |
| Deploy a recommended set of `.NET` skills into a project | `dotnet-skill-deploy` | Choose a category such as `foundation`, `wpf`, or `wpf-app` and deploy only the needed skills. |
| Build or refactor a WPF application | `dotnet-wpf-mvvm-patterns` | Start with MVVM as the WPF foundation, then branch into secure config, dialogs, OCR, PDF, or integrations. |
| Work on EF Core, serialization, or database performance | `dotnet-efcore-patterns`, `dotnet-serialization`, `dotnet-database-performance` | Stay in the data track rather than routing through UI or bootstrap skills. |
| Improve testing, snapshotting, Playwright, or containers | `dotnet-testcontainers`, `dotnet-snapshot-testing`, `dotnet-playwright-blazor`, `dotnet-playwright-ci-caching` | Route by testing concern and keep platform-specific advice narrow. |
| Work on DI, configuration, tools, or package management | `dotnet-extensions-dependency-injection`, `dotnet-extensions-configuration`, `dotnet-local-tools`, `dotnet-package-management` | Treat these as infrastructure or bootstrap concerns, not application-feature concerns. |

## Related Skills

- **`dotnet-skill-deploy`** — Deploy curated `.NET` skill sets into a target project's `.github/skills/`
- **`dotnet-project-structure`** — Strong first route for new or modernized solutions
- **`dotnet-wpf-mvvm-patterns`** — Strong first route for WPF requests
- **`dotnet-efcore-patterns`** — Primary data/persistence route
- **`dotnet-testcontainers`** — Representative testing/integration route

## Routing Notes

- Prefer direct skill invocation once the user's intent is clear; this entry skill is only for early ambiguity.
- Treat `WPF` as the strongest sub-domain inside `.NET`, but do not create a separate top-level `wpf` entry unless evidence shows the `dotnet` route is too broad.
- Keep deployment concerns in `dotnet-skill-deploy`; this skill should recommend deployment, not perform it.

## Pitfalls

- **Staying in the router too long**: once the user's real concern is clear, switch to the concrete skill instead of repeating high-level category guidance.
- **Using `dotnet` as a replacement for direct skills**: this entry skill exists to resolve ambiguity, not to hide concrete skills such as `dotnet-project-structure` or `dotnet-wpf-mvvm-patterns`.
