Claude Code Session Startup — Detailed Source & Average Sizes
Going through each row with source (where the content comes from) and typical average (across moderate users, not yours specifically).

1. Binary boot — Harness system prompt
Source: Hardcoded into the Claude Code binary itself. Not a file. Updates with each Claude Code release.
Contains: Built-in tool schemas (Read, Edit, Write, Bash, Glob, Grep, Agent, etc.), default behavior rules, env detection (OS, shell, cwd, git status flag), deferred-tool registry.
Average: ~12–18K tokens. Fairly constant per Claude Code version.

2. Organization instructions
Source: Set by the Anthropic Enterprise admin via the Anthropic admin console. Pushed server-side, not a local file you can edit or see directly. Embedded into the system prompt by the auth layer.
Average: ~100–500 tokens. Most non-enterprise users have 0. Enterprise users vary by org policy.

3. Config read — settings.json files
Source: Three literal JSON files, merged in order:
~/.claude/settings.json (user level, applies to all projects)
./.claude/settings.json (project level, committed to repo)
./.claude/settings.local.json (project local, gitignored — personal overrides)
Loads: Permission rules, hook definitions, MCP server registrations, model preferences, env vars.
Context impact: 0. These configure behavior, they don't go into the prompt.

4. Managed policy CLAUDE.md
Source: Admin-deployed file at a system-managed path (varies by OS — e.g. /Library/Application Support/ClaudeCode/CLAUDE.md on macOS, C:\ProgramData\ClaudeCode\CLAUDE.md on Windows). Only Anthropic Enterprise customers typically have this.
Average: Most users 0. When present, ~1–3K tokens of org-mandated rules.
Typical: 0 tokens

5. Global ~/.claude/CLAUDE.md + @-imports
Source: Literal markdown file at ~/.claude/CLAUDE.md. User-editable. @path/to/file.md lines pull in additional .md files (transitive, 5-hop max), each resolved relative to the file that contains the @ reference.
Average: Most active users have a customized one — ~100–300 lines ≈ ~2–4K tokens. Many users use only the default empty version.
Average: ~2K tokens

6. Project ./CLAUDE.md or ./.claude/CLAUDE.md + @-imports
Source: Literal markdown file in the project root (or .claude/CLAUDE.md inside project). Same @-import mechanic. Often committed to the repo so the whole team shares conventions.
Average: Small projects: 50–150 lines. Mature projects with documented conventions: 200–600 lines.
Average: ~3K tokens

7. Local ./CLAUDE.local.md
Source: Literal markdown file in project root, gitignored. Personal rules that override project ones for just this developer's machine.
Average: Most users don't create one.
Average: ~0 tokens

8. MEMORY.md auto-memory index
Source: Literal file at ~/.claude/projects/{project-slug}/memory/MEMORY.md. Maintained by Claude itself via the auto-memory system. Path-keyed to the launch directory.
Cap: Truncated after 200 lines / 25KB at load time.
Average: New users: 0. Users with active auto-memory: 50–150 lines ≈ ~500–2K tokens.
Average: ~500 tokens

9. Git status snippet
Source: Generated at runtime by the harness running git status, git rev-parse, git log against the cwd if it's a git repo. Not a file — produced on the fly.
Contains: Current branch, dirty/clean state, ahead/behind base, untracked file count.
Average: ~100 tokens (more for repos with lots of uncommitted changes)

10. Skill index
Source: Three places, only the description: line of each skill's frontmatter is loaded:
User skills: ~/.claude/skills/{skill-name}/SKILL.md
Project skills: ./.claude/skills/{skill-name}/SKILL.md
Built-in Claude Code skills: hardcoded in the binary (e.g. init, review, security-review)
Lazy bodies: Full skill body only loads when the skill is invoked.
Average: ~5–10 user skills × ~80 tokens descriptions + ~6–10 built-ins ≈ ~1.5K tokens.
Average: ~1.5K tokens

11. Subagent definitions
Source: Markdown files with YAML frontmatter:
User agents: ~/.claude/agents/{agent-name}.md
Project agents: ./.claude/agents/{agent-name}.md
Built-in agents: hardcoded (e.g. general-purpose, Plan, Explore, claude-code-guide, statusline-setup)
Registered: name, description, allowed tools, model — bodies load on invoke.
Average: ~1.5K tokens (mostly built-ins, ~2–4 user-defined agents typical)

12. Slash command registry
Source: Markdown files (with optional frontmatter):
User commands: ~/.claude/commands/{name}.md
Project commands: ./.claude/commands/{name}.md
Built-in commands: hardcoded (/help, /clear, /init, /model, /agents, /memory, /config, etc.)
Loads: Command names + one-line descriptions parsed into a command table.
Average: ~300–500 tokens

13. MCP server connect
Source: Configured in ~/.mcp.json and/or ~/.claude/settings.json mcpServers block, plus project .mcp.json. Each entry spawns a server process (stdio npx/uvx/local binary) or opens a network connection (HTTP/SSE/WebSocket to a URL).
Schema origin: Tool schemas come from the MCP server itself over the MCP protocol, not from a local file. The server may be local (stdio process on your machine) or remote (URL endpoint). The server in turn may proxy to a public or private backend:
mssql MCP → local Node/Python process → connects to a database URL (private or local)
github MCP → local process → calls api.github.com (public) or GitHub Enterprise URL (private)
ado MCP → local process → calls dev.azure.com (public) or Azure DevOps Server (private)
Average: Heavy variance. 0 MCPs: 0 tokens. 1–3 MCPs: ~3–10K. 5+ MCPs (especially GitHub's ~50-tool server): ~10–25K.
Average: ~7K tokens

14. Plugin registration
Source: Plugins declared in settings.json under plugins or installed via marketplace. Each plugin can ship commands, skills, agents, and hooks.
Average: Most users have 0–2 plugins.
Average: ~200 tokens

15. IDE context (VS Code / JetBrains only)
Source: Generated at runtime by the IDE extension process. Not a file. The extension pushes structured tags into the conversation context every turn:
<ide_opened_file> (path to the currently-focused file)
Text selection if any
Workspace metadata
Code-reference formatting instructions
Per-turn, not just first turn. Recurs on every prompt.
Average in IDE: ~1–3K tokens. Terminal: 0.
Average: ~1.5K tokens (assuming IDE mode)

16. SessionStart hook
Source: Shell command(s) configured in settings.json under hooks.SessionStart. Runs once at session start; stdout (JSON-formatted) provides additionalContext. The script source can be inline or reference any executable on the system.
Cap: ~10KB raw → ~2.5K tokens. >10KB triggers 2KB preview + file path.
Average: Most users have 0 of these configured.
Average: ~0 tokens (~1.5K when present)

17. Resume rehydration
Source: Stored transcripts at ~/.claude/projects/{project-slug}/transcripts/{session-id}.jsonl. Only loads if started with claude --resume or claude --continue.
Contains: Entire prior conversation (messages, tool calls, results).
Average: Fresh sessions: 0. Resumed: 20K–100K+ depending on the prior session's length.

Average: 0 tokens (most sessions are fresh)
18. Prompt shown — 0 tokens, UI only.

19. You type and submit
Source: Your keyboard input. Pure user message text.
Average first prompt: ~50–200 tokens

20. UserPromptSubmit hook
Source: Same mechanic as SessionStart but configured under hooks.UserPromptSubmit. Fires every turn, not just the first.
Cap: Same ~10KB / ~2.5K tokens / 2KB preview.
Average: Most users 0.
Average: ~0 tokens (~1K when present, paid every turn)

21. First model inference — sum of 1–20.



# Claude Code Session Startup — Load Order & Average Context Budget

| # | Stage | Source | Avg tokens (typical user) |
|---|---|---|---|
| 1 | Binary boot — harness system prompt | Hardcoded in Claude Code binary | ~15K |
| 2 | Organization instructions | Anthropic Enterprise admin console (server-pushed) | ~200 (0 for non-enterprise) |
| 3 | Config read — settings.json | `~/.claude/settings.json` + project `.claude/settings.json` + `settings.local.json` (literal JSON) | 0 (config only) |
| 4 | Managed policy CLAUDE.md | Admin-deployed file at OS-managed path (e.g. `/Library/Application Support/ClaudeCode/CLAUDE.md`) | 0 (most users) |
| 5 | Global CLAUDE.md + @-imports | Literal `~/.claude/CLAUDE.md` + transitively imported `.md` files (5-hop max) | ~2K |
| 6 | Project CLAUDE.md + @-imports | Literal `./CLAUDE.md` or `./.claude/CLAUDE.md` + imports | ~3K |
| 7 | Local CLAUDE.local.md | Literal `./CLAUDE.local.md` (gitignored) | ~0 |
| 8 | MEMORY.md auto-memory index | Literal `~/.claude/projects/{slug}/memory/MEMORY.md` (cap 200 lines / 25KB) | ~500 |
| 9 | Git status snippet | Generated at runtime via `git status` / `git rev-parse` | ~100 |
| 10 | Skill index | Frontmatter `description:` from `~/.claude/skills/*/SKILL.md` + project skills + hardcoded built-ins | ~1.5K |
| 11 | Subagent definitions | Frontmatter from `~/.claude/agents/*.md` + project agents + hardcoded built-ins | ~1.5K |
| 12 | Slash command registry | Names + descriptions from `~/.claude/commands/*.md` + project commands + hardcoded built-ins | ~400 |
| 13 | MCP server connect | Tool schemas streamed from each MCP server process (local stdio or remote URL) defined in `~/.mcp.json` / settings; servers may proxy to public APIs (api.github.com, dev.azure.com) or private endpoints (db URLs, internal hosts) | ~7K |
| 14 | Plugin registration | Plugins declared in settings.json (commands, skills, agents, hooks) | ~200 |
| 15 | IDE context (VS Code / JetBrains) | Injected per-turn by IDE extension process — open file, selection, workspace meta | ~1.5K (terminal: 0) |
| 16 | SessionStart hook | Shell command in `settings.json` hooks.SessionStart — stdout JSON `additionalContext` (cap ~10KB / 2KB preview) | 0 (most users) |
| 17 | Resume rehydration | Prior transcript at `~/.claude/projects/{slug}/transcripts/{session-id}.jsonl` if `--resume`/`--continue` | 0 (fresh sessions) |
| 18 | Prompt shown | UI only | 0 |
| 19 | User types and submits | Keyboard input | ~100 |
| 20 | UserPromptSubmit hook | Same source as #16 but per-turn | 0 (most users) |
| 21 | First model inference | Sum of 1–20 | sum |

**Typical terminal cold-start pre-prompt total: ~30–35K tokens** (≈15–18% of 200K window, ≈30–35% of 100K baseline) before the user types a character.
