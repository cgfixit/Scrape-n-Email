# Security Review Routine

## When To Use

Use this for changes involving email credentials, SMTP, CSV generation, scraped untrusted content, dependency updates, or generated files.

## Inputs To Ask For

- Changed files or PR.
- Whether runtime credentials or live email behavior are involved.

## Workflow

1. Read `AGENTS.md` security rules.
2. Check for committed secrets or `.env` changes.
3. Verify `EMAIL_USER`, `EMAIL_PASS`, and `EMAIL_RECIPIENT` remain environment-only.
4. Preserve or improve `csv_helper._csv_safe()` for spreadsheet formula injection.
5. Treat scraped HTML/text as untrusted input.
6. Ensure tests mock SMTP and avoid live network where possible.

## Verification Checklist

- No secrets committed.
- No real email sent during tests.
- CSV injection defenses intact.
- Generated scrape files not committed.

## Expected Final Response

- Security findings by severity.
- Affected files.
- Suggested fixes.
- Residual risk.
