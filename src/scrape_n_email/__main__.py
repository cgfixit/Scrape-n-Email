"""Allow running as: python -m scrape_n_email."""

from __future__ import annotations

import sys

from scrape_n_email.cli import main

if __name__ == "__main__":
    sys.exit(main())
