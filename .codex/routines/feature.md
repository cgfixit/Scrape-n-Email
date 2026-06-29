# Feature Routine

## When To Use

Use this for a focused enhancement such as another attachment, parser fallback, scheduler note, or small output-format improvement.

## Inputs To Ask For

- Desired behavior.
- Whether the change affects daily scheduled use.
- Whether new secrets or network behavior are involved.

## Workflow

1. Read `AGENTS.md`.
2. Keep the feature small and dependency-light.
3. Preserve pure parser functions where possible.
4. Add offline unittest coverage.
5. Update README/CONTRIBUTING only if setup or user behavior changes.
6. Run full unittest discovery.

## Verification Checklist

- No new secret committed.
- No tests require live sites or Gmail.
- Existing generated-file ignore rules still apply.
- Dependency changes are justified and documented.

## Expected Final Response

- Feature summary.
- User-visible behavior.
- Tests run.
- Remaining manual/live checks.
