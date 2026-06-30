"""Compatibility shim — preserves the documented `python main.py` entry point.

Existing Windows Task Scheduler jobs and scripts that call `python main.py`
continue to work after the package is installed with `pip install -e .`.
New setups should use `python -m scrape_n_email` or the `scrape-n-email` CLI.
"""

import sys

from scrape_n_email.cli import main

if __name__ == "__main__":
    sys.exit(main())
