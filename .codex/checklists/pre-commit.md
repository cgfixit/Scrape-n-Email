# Pre-Commit Checklist

- Read `AGENTS.md`.
- Confirm the diff is scoped to the task.
- Do not commit `.env`, credentials, local scheduler paths, generated `jobs.txt`, `RCPheadlines.txt`, or `RCPlinks.csv`.
- For parser changes, run `python -m unittest test_scrapers -v`.
- For CSV/mailer changes, run `python -m unittest test_mailer_csv -v`.
- For broad changes, run `python -m unittest discover -v -p "test_*.py"`.
- For import changes, run `python -c "import main; print('main.py imports successfully')"`.
- For docs-only changes, run `git diff --check`.
