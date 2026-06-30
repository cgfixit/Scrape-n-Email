# `.codex/`

This folder contains Codex-specific operating material for Scrape-n-Email. Repo-wide instructions belong in `AGENTS.md`; task-specific playbooks, prompts, and checklists live here. Runnable Codex slash commands live in the repo-root `commands/` directory.

## Purpose

Use `.codex/` to help future Codex agents work safely in this small Python scraper/email automation repo without rediscovering the setup, test commands, and secret-handling rules each time.

## Available Routines

- `routines/first-pass-repo-review.md` - orient in the repo before edits.
- `routines/bugfix.md` - diagnose and fix parser, CSV, mailer, or orchestration bugs.
- `routines/feature.md` - add focused functionality without turning the project into a framework.
- `routines/refactor.md` - improve structure while preserving behavior.
- `routines/test-and-verify.md` - choose the right unittest/import checks.
- `routines/pr-review.md` - review diffs with parser, email, and generated-file risks in mind.
- `routines/security-review.md` - check secrets, CSV injection, SMTP, and untrusted scrape content.

## Prompt Templates

- `prompts/issue-triage.md`
- `prompts/implementation-plan.md`
- `prompts/review-diff.md`
- `prompts/release-notes.md`

Each prompt references `AGENTS.md`; copy one into a Codex prompt and fill in the placeholders.

## Commands

- `commands/ponytail.toml` - switch into minimal-diff, dependency-light repo mode.
- `commands/optimize.toml` - focus a task on tight, measurable cleanup or improvement.

## Checklists

- `checklists/pre-commit.md`
- `checklists/pre-pr.md`
- `checklists/regression-risk.md`

Use these as quick reminders. They do not replace reading the code or running the relevant tests.

## Adding New Routines

1. Put repo-wide agent rules in `AGENTS.md`.
2. Put task-specific playbooks in `.codex/routines/`.
3. Link to `README.md`, `CONTRIBUTING.md`, and `.github/workflows/ci.yml` rather than copying large sections.
4. Keep routines concise and grounded in actual commands.

## Scratch Work

Do not commit generated scrape outputs, logs, local notes, credentials, or temporary artifacts unless the maintainer explicitly requests them.
