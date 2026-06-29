# Bugfix Routine

## When To Use

Use this for broken parser output, CSV issues, mailer behavior, import errors, or failing CI.

## Inputs To Ask For

- Error output or failing test.
- Site/source involved: RCP, Craigslist, Drudge, CSV, or Gmail.
- Whether live scraping was observed or only offline tests fail.

## Workflow

1. Reproduce with the smallest offline test when possible.
2. For parser bugs, add or adjust an HTML fixture in `test_scrapers.py`.
3. For CSV/mailer bugs, use temp files and mocks in `test_mailer_csv.py`.
4. Make the minimal code change.
5. Run the targeted unittest, then full discovery.

## Verification Checklist

- Offline regression test added or updated.
- No real email sent.
- No network required for tests.
- Generated files remain uncommitted.

## Expected Final Response

- Root cause.
- Files changed.
- Tests run and results.
- Live-site verification status, if any.
