# Agent Explain On-Demand — Explanation Patterns

## Common Explanation Request Patterns

### Mode Explanations
When a user asks about a mode (e.g., "What is plan mode?"):
1. Name the mode clearly
2. Explain what changes behaviorally
3. Show how to enter/exit the mode
4. Give a concrete example of when to use it

Example response structure:
> **Plan mode** (Shift+Tab to activate) changes my behavior so I:
> 1. Analyze the problem and write a plan BEFORE making changes
> 2. Ask clarifying questions instead of assuming
> 3. Don't start implementation until you explicitly say "go"
>
> Use it when you want to review the approach before code changes.

### Capability Explanations
When a user asks "What can you do?":
1. Start with the most common use cases
2. Give concrete action examples (not abstract descriptions)
3. Mention any limitations or prerequisites
4. Point to relevant skills with `skill-name` format

### Recent Change Explanations
When a user asks "What changed?":
1. Check recent commits with `git log --oneline -10`
2. Summarize changes in user-visible terms (not technical diffs)
3. Highlight breaking changes or new behaviors first

## Explanation Quality Checklist

- [ ] Uses concrete examples, not just abstract descriptions
- [ ] Mentions prerequisites if any setup is needed
- [ ] Links to related skills when delegation is better
- [ ] Answers the implicit question, not just the literal one
- [ ] Checks if follow-up is needed (complex explanations often lead to more questions)
