# Refactor Routine

## When To Use

Use this to simplify code, improve module boundaries, or remove duplication without changing behavior.

## Inputs To Ask For

- Target module.
- Behavior that must remain unchanged.
- Verification budget.

## Workflow

1. Run or inspect the relevant baseline unittest.
2. Keep changes narrow and behavior-preserving.
3. Preserve `csv_helper.py` as the CSV boundary unless the task is explicitly about CSV architecture.
4. Do not mix refactor with new dependencies or feature behavior.
5. Run the same tests after the edit.

## Verification Checklist

- Behavior unchanged.
- Tests before/after comparable or baseline explicitly unavailable.
- No generated outputs committed.

## Expected Final Response

- Refactor goal.
- Files changed.
- Checks run.
- Any behavior risks.
