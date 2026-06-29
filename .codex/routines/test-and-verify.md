# Test And Verify Routine

## When To Use

Use this when choosing verification for docs, parser changes, mailer changes, or CI triage.

## Inputs To Ask For

- Files changed.
- Whether dependencies are installed.
- Whether live-site or real-email checks are allowed.

## Workflow

1. For docs-only changes, run `git diff --check`.
2. For parser changes, run `python -m unittest test_scrapers -v`.
3. For CSV/mailer changes, run `python -m unittest test_mailer_csv -v`.
4. For broad changes, run `python -m unittest discover -v -p "test_*.py"`.
5. For import boundary changes, run `python -c "import main; print('main.py imports successfully')"`.

## Verification Checklist

- Commands came from README/CONTRIBUTING/CI.
- No network or Gmail dependency introduced into tests.
- Skipped checks have explicit reasons.

## Expected Final Response

- Commands run.
- Results.
- Skipped checks and why.
- Recommended next check.
