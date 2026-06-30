# Contributing to Scrape-n-Email

Thanks for checking out this project.

**Scrape-n-Email** is a lightweight, personal automation tool that scrapes RealClearPolitics headlines and Atlanta Craigslist sysadmin job listings, then emails clean daily digests with attachments. It was originally written for personal daily use and received a significant modernization pass in June 2026 (circular import fixes, robust CSV handling, cross-platform logging, and comprehensive offline tests).

This repo is **primarily maintained for personal use**, but thoughtful contributions, bug reports, and improvements are welcome.

## Quick Start for Contributors

### Prerequisites
- Python 3.10+
- `requests` and `beautifulsoup4` (see `requirements.txt`)

### Setup
```bash
git clone https://github.com/CGFixIT/Scrape-n-Email.git
cd Scrape-n-Email
pip install -r requirements.txt
```

### Environment Variables (for running the full script)
Set these in your shell or `.env` (never commit secrets):

| Variable          | Description                                      |
|-------------------|--------------------------------------------------|
| `EMAIL_USER`      | Your Gmail address                               |
| `EMAIL_PASS`      | Gmail App Password (16-character token)          |
| `EMAIL_RECIPIENT` | (Optional) Override recipient; defaults to `EMAIL_USER` |

### Running Tests (Recommended)
All tests are **offline** and use HTML fixtures — no network required.

```bash
python -m unittest test_scrapers -v
```

### Running the Scraper (one-off)
```bash
python main.py
```

Scheduled example (Windows Task Scheduler) is in the README.

## What We're Looking For

- **Bug reports** with reproduction steps and (ideally) a minimal HTML snippet if it's a parsing issue.
- **Improvements to parsing robustness** (sites change; defensive selectors + fallbacks are appreciated).
- **Test coverage** for new edge cases in `parse_*` functions.
- **Documentation** or README clarifications.
- **Cross-platform** or scheduling improvements.

## Code Style & Guidelines

- Keep it simple and dependency-light. This is a personal tool, not a framework.
- Parser functions (`parse_headlines`, `parse_jobs`, etc.) should remain **pure** where possible (no I/O or network) so they can be unit tested easily.
- Prefer explicit, readable code over clever one-liners.
- Add or update tests in `test_scrapers.py` when changing parsing logic.
- Use `logging` (already configured in `main.py`) instead of `print()` for operational messages.
- Respect the existing module boundaries (`csv_helper.py` centralizes CSV logic).

## Pull Request Process

1. Fork the repo and create a feature branch from `main`.
2. Make your changes + add/update tests.
3. Run `python -m unittest test_scrapers -v` and confirm everything passes.
4. Open a PR with a clear description of the change and why it helps.
5. I'll review and merge (or provide feedback) when I have time.

Small fixes and documentation improvements may be merged quickly. Larger changes will be discussed.

## Reporting Issues

Use the GitHub Issues tab. Please include:
- Python version and OS
- Exact error or unexpected behavior
- Steps to reproduce (or a link to a failing test if applicable)
- For scraping bugs: the relevant HTML snippet if you can capture it

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Questions?

Open an issue or reach out on X (@cgfixit). I'm happy to discuss design decisions or how the scrapers are used in practice.

---

*Maintained by Christopher Michael Grady (@cgfixit) — June 2026*