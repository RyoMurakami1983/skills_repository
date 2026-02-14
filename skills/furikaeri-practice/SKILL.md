---
name: furikaeri-practice
description: Guided retrospective after sessions or PR reviews. Use when reflecting on work and planning improvements.
author: RyoMurakami1983
tags: [retrospective, kaizen, kpt, ywt, continuous-improvement, team-growth]
invocable: false
version: 1.0.0
---

# Furikaeri Practice

A structured retrospective workflow for AI-assisted sessions. Apply proven team retrospective techniques — KPT, YWT, 5 Whys, SMART goals — to individual or pair sessions with an AI assistant, turning implicit lessons into explicit improvements.

> **Note**: "ふりかえり" (furikaeri) is intentionally written in hiragana, not kanji (振り返り). It denotes a deliberate, structured improvement practice — not casual "looking back."

## When to Use This Skill

Use this skill when:
- Wrapping up a coding session or multi-turn conversation
- Completing PR review feedback and fixes
- Finishing a sprint or milestone
- Encountering repeated problems across sessions
- Wanting to turn tacit knowledge into documented improvements
- Onboarding a new practice and tracking what works

## Related Skills

- **`git-commit-practices`** — Commit history as learning asset
- **`github-pr-workflow`** — PR creation and issue close
- **`github-issue-intake`** — Capture improvement items as issues

---

## Dependencies

- None required (conversation-only workflow)
- Optional: GitHub CLI (`gh`) for creating improvement issues

## Core Principles

1. **Stop and Reflect** — Pause to observe before rushing to the next task (温故知新)
2. **Small Kaizen** — Change little by little; small steps compound (継続は力)
3. **Externalize Knowledge** — Turn tacit lessons into team assets (成長の複利)
4. **Fact-Based** — Start from facts, not assumptions or blame (ニュートラル)
5. **Form Yields Insight** — KPT, YWT, 5 Whys, SMART are forms that unlock depth (基礎と型)

---

## Three Purposes of Furikaeri

1. **Stop** — Create a moment of change. Look around you.
2. **Accelerate Growth** — Frequent communication surfaces problems early and solves them fast.
3. **Kaizen the Process** — Focus on *how* value is created. Change small, change often.

---

## Workflow: Run a Furikaeri

### Step 1: Organize the Session Story

Lay out what happened in chronological order. Focus on facts — emotions and judgments come later.

```markdown
## Session Story

1. Started with Issue #42 — add search filter
2. Created feature branch, wrote tests first (TDD)
3. Hit unexpected API timeout during integration
4. Switched to mocking, tests passed
5. PR review requested 2 changes
6. Fixed and merged
```

Prompt the user:
- "What did we work on today?"
- "Walk me through the timeline of this session."

> **Use when**: Starting any furikaeri. Always do this step first.
>
> **Values**: 温故知新 / ニュートラル

### Step 2: Analyze with KPT or YWT

Choose one framework and categorize the session story.

**KPT (Keep / Problem / Try)**

| Category | Description | Example |
|----------|------------|---------|
| **Keep** | What went well — continue doing | TDD caught the timeout early |
| **Problem** | What went wrong — needs fixing | API docs were outdated |
| **Try** | What to experiment with next | Add integration test timeout config |

Try items have two purposes:
- **Keep strengthening** — Amplify what already works (marked ← K)
- **Problem kaizen** — Fix or prevent what went wrong (marked ← P)

**YWT (Y: did / W: learned / T: next)**

| Category | Description | Example |
|----------|------------|---------|
| **Y** (やったこと) | What you did | Wrote 5 unit tests, 1 integration test |
| **W** (わかったこと) | What you learned | Mock-first is faster for unstable APIs |
| **T** (つぎにやること) | What to do next | Create a mock library for the team |

```markdown
## KPT

### Keep
- TDD workflow caught issues early
- Atomic commits made review easy

### Problem
- API documentation was stale
- Spent 30 min debugging timeout

### Try
- (← K) Add timeout configuration to test setup
- (← P) Update API docs as part of definition of done
```

Prompt the user:
- "Shall we use KPT or YWT?" (default: KPT)
- "What should we Keep doing?"
- "What Problems did we hit?"
- "What should we Try next time?"

> **Use when**: Always. This is the core analysis step.
>
> **Values**: 基礎と型 / 成長の複利

### Step 3: Pick the Most Important Items

Not everything matters equally. Select the items with the highest impact.

Present the combined list from Step 2 and ask the user to pick 1–3 items:

```markdown
## Priority Items (dot-vote style)

From the KPT above, which items matter most?

1. 🔴 API documentation was stale (Problem)
2. 🟡 Add timeout configuration (Try)
3. 🟢 TDD workflow caught issues early (Keep)

→ User picks: #1 (stale docs) and #2 (timeout config)
```

Rules:
- Maximum 3 items to focus on
- At least 1 item must be actionable (Problem or Try)
- Keep items are acknowledged but don't need action plans

> **Use when**: Always. Forces focus on what matters most.
>
> **Values**: ニュートラル / 継続は力

### Step 4: Dig Deeper (When Needed)

For items with unclear root causes, apply **5 Whys** to find the real problem. Then set a **SMART goal** for the action item.

**5 Whys Example**

```markdown
## 5 Whys: API documentation was stale

1. Why was the documentation stale?
   → Nobody updated it when the API changed.
2. Why didn't anyone update it?
   → It wasn't part of the PR checklist.
3. Why wasn't it in the checklist?
   → We didn't have a definition of done for API changes.
4. Why no definition of done?
   → We haven't formalized our API change process.
5. Why not formalized?
   → Small team, assumed everyone knew.

Root cause: No formalized API change process.
```

**SMART Goal**

| Element | Value |
|---------|-------|
| **S**pecific | Add "Update API docs" to PR checklist |
| **M**easurable | 100% of API PRs include doc updates |
| **A**chievable | One checklist item addition |
| **R**elevant | Directly prevents stale documentation |
| **T**ime-bound | Add to checklist by next sprint |

> **Use when**: A Problem item has unclear root cause, or a Try item needs a concrete plan.
>
> **Values**: 温故知新 / 基礎と型

### Step 5: Furikaeri the Furikaeri

Improve the retrospective process itself. Ask one question:

> "What would you change about this furikaeri next time?"

Examples:
- "Spend less time on story, more on analysis"
- "Try YWT instead of KPT next session"
- "Include metrics (time spent, commits count)"
- "Skip 5 Whys — problems were straightforward"

Record the answer for the next session.

```markdown
## Meta-Furikaeri

Next time: Try YWT format — KPT felt repetitive for this type of session.
```

> **Use when**: Always. Even 1 sentence improves the next furikaeri.
>
> **Values**: 継続は力 / 成長の複利

---

## Best Practices

- Keep furikaeri under 10 minutes for solo sessions
- Use KPT for problem-focused sessions, YWT for learning-focused ones
- Write down action items immediately — don't rely on memory
- Link action items to GitHub Issues for tracking
- Review previous furikaeri notes before starting a new one

## Common Pitfalls

1. **Skipping the story step**
   Fix: Always start with facts. Analysis without context leads to wrong conclusions.

2. **Too many action items**
   Fix: Pick 1–3 items maximum. Better to finish 1 than abandon 5.

3. **Vague Try items**
   Fix: Convert to SMART goals. "Be more careful" is not actionable.

4. **Blame-oriented Problems**
   Fix: Focus on process and tools, not people. "The process allowed X" not "Person did X."

5. **Never reviewing past furikaeri**
   Fix: Spend 1 minute reading the previous session's notes before starting.

## Anti-Patterns

- Treating furikaeri as a status report (it's about improvement, not reporting)
- Only doing furikaeri when things go wrong (good sessions have lessons too)
- Skipping "furikaeri the furikaeri" (the meta-step drives long-term improvement)
- Writing action items but never following up

---

## Quick Reference

### KPT Template

```markdown
## KPT — [Date/Session]

### Keep
- 

### Problem
- 

### Try
- (← K) Keep strengthening idea
- (← P) Problem kaizen idea

### Priority (top 1-3)
1. 

### Action (SMART)
- 

### Meta
- Next furikaeri change: 
```

### YWT Template

```markdown
## YWT — [Date/Session]

### Y (やったこと / What I Did)
- 

### W (わかったこと / What I Learned)
- 

### T (つぎにやること / What To Do Next)
- 

### Priority (top 1-3)
1. 

### Action (SMART)
- 

### Meta
- Next furikaeri change: 
```

### Decision Table

| Situation | Framework | Why |
|-----------|-----------|-----|
| Problem-heavy session | KPT | Separates Keep from Problem clearly |
| Learning-heavy session | YWT | Focuses on what was discovered |
| Root cause unclear | KPT + 5 Whys | Drills into systemic issues |
| First furikaeri ever | KPT | Simpler, more intuitive |

---

## FAQ

**Q: How long should a furikaeri take?**
A: 5–10 minutes for a solo AI session. 15–30 minutes for a team session.

**Q: KPT or YWT — which is better?**
A: KPT for problem-solving sessions, YWT for learning-focused ones. Try both and see what fits.

**Q: Do I need to do all 5 steps every time?**
A: Steps 1–3 and 5 are always recommended. Step 4 (5 Whys + SMART) is only for complex or recurring problems.

**Q: What if nothing went wrong?**
A: Great sessions still have Keep items and Try items. "What could be even better?" always yields insights.

**Q: Should I store furikaeri notes somewhere?**
A: Yes. Create a GitHub Issue with the `furikaeri` label, or keep a `FURIKAERI.md` in your project.

---

## Resources

- Esther Derby & Diana Larsen, *Agile Retrospectives*
- https://www.funretrospectives.com
- Toyota Production System — 5 Whys
- George T. Doran, "There's a S.M.A.R.T. Way to Write Management Goals and Objectives"
