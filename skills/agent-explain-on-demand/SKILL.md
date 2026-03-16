---
name: agent-explain-on-demand
description: >
  On-demand explanation of agent behavior, modes, recent changes, and capabilities.
  Use when a user asks what the agent is doing, wants a mode explained, wants to know
  what changed in an update, or wants to understand what the agent can do.
---

# Agent Explain On-Demand

Progressive, on-demand explanation of agent behavior that starts with the shortest useful
answer and deepens only when the user asks for more.

## When to Use This Skill

Use this skill when:
- Explaining what the agent is currently doing after a user says the behavior is unclear
- Describing available interaction modes only after a user explicitly asks for them
- Summarizing what changed in a recent update, revision, or session
- Introducing what the GitHub Copilot CLI (command-line interface) agent is and can do
- Preserving user attention by giving the shortest useful answer first

Do **not** use this skill to proactively insert explanations into task-focused conversations.
Trigger only on an explicit signal of confusion or curiosity.

## Related Skills

- **`session-issue-autopilot`** — Autopilot session workflow (often a source of "what's happening?" questions)
- **`furikaeri-practice`** — Retrospective; may surface "what changed?" questions
- **`github-issue-intake`** — Issue intake workflow users may ask about
- **`skill`** — If a user asks "what does validation do?"

---

## Dependencies

- None required (conversation-only workflow)
- Optional: `fetch_copilot_cli_documentation` for CLI capability questions (Lane D)

---

## Core Principles

1. **Shortest Answer First** — Lead with one or two sentences. Offer depth only on follow-up (余白の設計)
2. **Lane Before Answer** — Identify which of the four lanes the question belongs to before composing the reply (基礎と型)
3. **No Unsolicited Preamble** — Never inject mode declarations or status announcements into task work (ニュートラルな視点)
4. **Depth is Pulled, Not Pushed** — Always end first-layer answers with an offer to go deeper, never force it (余白の設計)
5. **CLI Facts from the Source** — For questions about Copilot CLI capabilities, call `fetch_copilot_cli_documentation` rather than guessing (温故知新)

---

## Workflow: Explain on Demand

### Step 1: Identify the Explanation Lane

Classify the user's message into exactly one lane.
If the message is ambiguous, ask which lane the user wants before going deeper.

| Lane | Signal words / phrases | Question type |
|------|----------------------|---------------|
| **A — Behavior** | "what are you doing?", "why did you do that?", "what is happening now?" | Current action or reasoning |
| **B — Modes** | "what modes exist?", "explain plan mode", "how does autopilot work?", "is the model fixed?" | Mode/behavior options |
| **C — Changes** | "what changed?", "what's new?", "what did the update change?" | Update or release delta |
| **D — Identity** | "who are you?", "what can you do?", "tell me about yourself" | Agent identity or capabilities |

> **Values**: 基礎と型（型を見極めてから動く）

---

### Step 2 — Lane A: Explain Current Behavior

**Trigger**: User is confused about what the agent is doing right now, or why it took an action.

**First-layer response pattern** (≤3 sentences):

```markdown
I am currently working on 〈task name〉 using 〈method〉.
I took 〈last action〉 because 〈reason〉.
Would you like me to continue, or should I try a different approach?
```

Offer depth with: `"Would you like a more detailed step-by-step explanation?"`
Why: naming the task, action, and reason keeps the first answer concrete.

If the user confirms, add:
- The specific step in the active skill workflow you are executing
- The decision rule that triggered the action
- What comes next in the workflow

> **Values**: ニュートラルな視点（事実を淡々と伝え、判断は相手に委ねる）

---

### Step 3 — Lane B: Explain Modes

**Trigger**: User asks about modes, behavior options, or interaction styles.

**First-layer response pattern**:

```markdown
This agent has four broad interaction styles.

| Mode | Trait | Best for |
|------|-------|----------|
| Interactive | Confirms key steps as it goes | Careful, collaborative work |
| Plan | Produces a plan without implementing | Scoping before action |
| Autopilot | Pushes toward task completion | Focused execution loops |
| Shell | Runs or explains local commands | Terminal-centric tasks |

Which mode should I explain next?
```

Offer depth with: `"Tell me which mode you want next."`
Why: a small comparison table is enough for orientation; deeper detail should be user-selected.

If the user names a mode, describe:
1. What triggers it
2. Concrete example exchange (user says → agent does)
3. How the user can ask for that interaction style again

If the user asks about **model behavior**, explain the two layers separately:
1. Session model selection: Copilot CLI can switch the interactive session model with `/model`
2. Sub-agent override: a task/sub-agent call can specify `model` for that call only

Example clarification:

```markdown
The agent was not permanently fixed to that model.
The main session model and a sub-agent call can be different.
In that case, the sub-agent used a per-call `model` override just for that run.
```

Why: users often interpret a one-time sub-agent model override as a global agent setting.

> **Values**: 余白の設計（全部渡さず、選ばせてから深める）

---

### Step 4 — Lane C: Explain What Changed

**Trigger**: User asks what changed in a recent update, skill revision, or session.

**First-layer response pattern**:

```markdown
The recent change is 〈1–2 line summary〉.
Before, 〈old behavior〉 happened. Now, 〈new behavior〉 happens.
Would you like the detailed change history?
```

Why: compare old and new behavior before offering raw history.

If the user says yes, inspect sources in this order:
1. Current session diff, issue summary, or PR summary
2. Relevant `## Changelog` section
3. Recent commits

Use commands like:

```bash
git --no-pager status --short
git --no-pager diff --stat
git --no-pager log --oneline -10
```

If no Changelog is available, say so honestly and offer to inspect the changed files directly.

> **Values**: 温故知新（過去の型を参照し、変化の意味を伝える）

---

### Step 5 — Lane D: Explain Identity and Capabilities

**Trigger**: User asks who the agent is or what it can do.

**First-layer response pattern**:

```markdown
I am GitHub Copilot CLI, a terminal-based coding agent.
I can help with coding, reviews, issue work, repository guidance, and skill-driven workflows.
Which capability do you want me to explain first?
```

**For CLI capability questions specifically** — call `fetch_copilot_cli_documentation` first:

```
# Before answering "Can you run X?" or "Does Copilot support Y in the CLI?",
# call fetch_copilot_cli_documentation to get accurate, up-to-date capability facts.
# Do not guess or extrapolate from memory.
```

After fetching, summarize in plain language. Cite the source section.
Why: capability answers must separate local repository conventions from CLI platform facts.

Offer depth with: `"Would you like me to list the available skills?"`

If the user says yes, list available skills from `skills/` with one-line descriptions.

> **Values**: 基礎と型（ファクトをファクトの源泉から取る）

---

## Common Pitfalls

| Pitfall | Why it hurts | Fix |
|---------|-------------|-----|
| Answering before lane identification | Mixes mode info with behavior info; confuses the user | Always classify first |
| Pushing all four lanes at once | Cognitive overload; violates the leave-room principle | One lane per turn unless the user requests multiple |
| Guessing CLI capabilities | Stale or wrong info erodes trust | Call `fetch_copilot_cli_documentation` |
| Injecting this skill proactively | Interrupts task flow; unwanted context switching | Trigger only on explicit confusion or curiosity signal |
| Over-explaining first-layer answers | Forces depth the user didn't request | ≤3 sentences, then offer depth |

Fix rule:
- Stay in one lane per reply.
- State the source for change or capability questions.
- End the first layer with a clear invitation to go deeper.

## Anti-Patterns

```markdown
## ❌ Proactive mode announcement (rejected pattern)
"PLANモードで動作を開始します。"
→ User did not ask for this. It adds noise to task output.

## ❌ Forced preamble before every task
"このタスクはインタラクティブモードで実行します。"
→ Violates 余白の設計. Explain only when asked.

## ✅ On-demand reply when asked
User: "今何してる？"
Agent: "PRのdiffを分析して、レビューコメントの草案を作成しています。続けますか？"
```

- Treating explanation as a mandatory pre-task ritual
- Merging mode help, change summaries, and identity into one generic block
- Answering capability questions without source-backed documentation

---

## Quick Reference

```
User question → Lane → First-layer (≤3 sentences) → Offer depth → Deliver if pulled
```

| Phrase heard | Lane | First action |
|-------------|------|-------------|
| what are you doing | A | Describe the current task in 1–2 sentences |
| what modes exist | B | Show the 4-row mode table |
| is the model fixed | B | Explain `/model` vs per-call sub-agent override |
| what changed | C | State the delta in 1–2 sentences |
| what can you do | D | Give a brief identity summary and ask what they want to know |
| can Copilot CLI do X | D | Call `fetch_copilot_cli_documentation` first |

---

## Changelog

### v1.0.0 (2026-03-07)
- Initial release
- 4 explanation lanes: Behavior, Modes, Changes, Identity
- Short-first, depth-on-demand response pattern
- CLI capability questions routed through `fetch_copilot_cli_documentation`

