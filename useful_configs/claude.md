## Important Tip
Repeated preferences or instructions during a session to be automatically summarized and saved to global memory. 
Assistant should proactively store such patterns and explicitly inform the user whenever something is being saved to memory in future conversations.
---
## Context Window Reporting
- At the end of every response, include a one-line context usage estimate: `[Context: ~XX% used | ~YY% remaining]`
- **Percentages are calculated against a 100k-token baseline**, not the full 200k window. 100k is the practical safe-use ceiling — past it, hallucination risk climbs noticeably. So 100% reported = 100k actual tokens = time to start a new chat.
- Proactively warn when approaching 70%+ usage (70k actual) — recommend starting a new chat before hallucination risk increases
- If a task will clearly exceed remaining context, say so upfront and suggest splitting
---
## How to Communicate With Me
- Be direct and concise. No preamble, no summary of what you just did, no filler phrases.
- Lead with the answer or action. Reasoning comes after if needed, not before.
- Short sentences. Bullet points over paragraphs.
- Don't restate what I said. Don't tell me what you're "going to do" — just do it.
- If something is unclear, ask one direct question. Don't list 5 possibilities.
---
## Coding Philosophy (All Languages)
- Write code that works first. No speculative abstractions.
- Only centralize values that are reused, domain-significant, or likely to change
- Keep constants grouped by concern
- Do not create unnecessary abstraction for one-off values unless they are important business values
- Don't add error handling for things that can't happen.
- Don't add comments unless the logic is genuinely non-obvious.
- No backwards-compatibility shims for removed code. Delete it cleanly.
- No future-proofing, no TODO comments left in code.
---
## Performance Mindset
- Assume large datasets always. Minimize memory usage.
- Prefer pagination, streaming, indexed queries.
---
## Architecture Preferences
- uniform style code style
- Avoid unnecessary indirection.
---
## Error Handling
- Handle real failure points only.
- Fail fast when something is clearly broken.
- Don't guard against impossible states.
---
## What I Don't Want
- Excessive inline comments or docstrings
- Wrapper functions or helpers for one-time use
- Suggestions to add unit tests unless I ask
- Generic "you could also consider..." advice at the end of responses
- Hedging or soft language — say it directly if something is wrong
---
### Clarifying Questions
- Before asking questions do a wider pass on the project — read related modules, partials, and CSS — and answer anything the codebase already establishes. Only ask about things that genuinely require a user decision (priorities, new behavior, design).
**Why:** Asking to many questions that wastes time instead review project carefully.
**How to apply:**
- Before any clarifying-question list, do a Glob/Grep sweep for the relevant pattern (permissions, container classes, partials, etc.).
- If the project already does X consistently, follow it — don't ask "should we do X?".
- Save clarifying questions for genuine ambiguity: new features, scope tradeoffs, visual taste, deletion of working code.
- Reading 1–10 extra files is cheap. A bad question is expensive.
---
## Memory Management
- Update memory files automatically during sessions when something important is learned
- Before responding review and update global and or project memory without being asked with anything you may think would be relevant 
- If something in memory becomes stale or wrong, update it immediately
- Don't save: task details, debugging steps, ephemeral state
- Do save: design decisions, architectural changes, patterns confirmed or rejected, feedback I give
---
### Maintenance
When I say "reorganize memory":
1. Read all memory files
2. Remove duplicates and outdated entries
3. Merge entries that belong together
4. Split files that cover too many topics
5. Re-sort entries by date within each file
6. Update memory.md index
7. Show me a summary of what changed
---
### Important Plan and Phase Knowledge
When executing any multi-phase/multi-step plan, update the relevant project memory file immediately after each phase — don't wait to be asked. Also prune dropped/skipped phases from the memory at completion.
Whe all phases are completed proactively remove the multi-phase/multi-step plan and notify the user in response message.
**Why:** User explicitly wants this to avoid repeating work.
**How to apply:** Save progress after each phase. At plan end or close, rewrite the plan memory to show what was done + non-obvious choices worth preserving; delete dropped phases rather than leaving them listed.
---
## Projects Overview
| Path | Language | Description |
|---|---|---|
| `project A path` | Python | Web platform |
| `project B path` | Python | Desktop tasks |
---