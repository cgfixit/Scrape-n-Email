# PR Review Routine

## When To Use

Use this to review a PR or local diff for Scrape-n-Email.

## Inputs To Ask For

- PR number, URL, branch, or diff.
- Review focus: parser, mailer, tests, docs, or security.

## Workflow

1. Read `AGENTS.md`.
2. Inspect changed files and tests.
3. Check whether generated files were accidentally committed.
4. Look for network/Gmail dependence in tests.
5. Check parser changes against offline fixtures.
6. Report actionable findings first.

## Verification Checklist

- Findings include file/line references where possible.
- Secret handling checked for mailer changes.
- CSV formula-injection behavior considered for CSV changes.
- CI command impact considered.

## Expected Final Response

- Findings by severity.
- Open questions.
- Tests reviewed or run.
- Brief scope summary.
