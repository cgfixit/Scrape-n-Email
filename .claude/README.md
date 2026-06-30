# .claude — Claude Code Configuration

Claude Code tooling for Scrape-n-Email. See root `CLAUDE.md` for full project guidance.

## Skills (`skills/`)

Skills are reusable, richly-documented templates invoked with `/skill-name`. They provide detailed
context, biases, and fill-in sections for structured AI-assisted work.

| Skill | Invoke | Purpose |
|---|---|---|
| `skills/ponytail/SKILL.md` | `/ponytail` | Smallest-diff fix: reuse stdlib + existing helpers, no scope creep |
| `skills/optimize/SKILL.md` | `/optimize` | Hotspot tightening: one measurable improvement, prefer deletion |

## Commands (`commands/`)

Commands are lightweight slash commands invoked with `/command-name [args]`. They send a focused
prompt to Claude with `$ARGUMENTS` replaced by whatever you type after the command name.

| Command | File | Codex equivalent |
|---|---|---|
| `/ponytail [task]` | `commands/ponytail.md` | `commands/ponytail.toml` |
| `/optimize [task]` | `commands/optimize.md` | `commands/optimize.toml` |

The `.toml` files in `commands/` are the Codex-format equivalents for use with Codex agents.

## Skills vs Commands

- **Skills** (`/ponytail`, `/optimize`): use when you want the full structured template with fill-in
  sections, bias notes, and explicit verify steps. Good for starting a focused work session.
- **Commands** (`/ponytail [task]`, `/optimize [task]`): use when you want a quick invoke with a
  task description inline. Good for one-liners.

Both enforce the same house rules: minimal diffs, stdlib-first, offline tests, no `print()`,
formula-injection-safe CSV writes.
