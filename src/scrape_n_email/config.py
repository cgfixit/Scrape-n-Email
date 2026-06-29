"""Configuration management via environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


@dataclass(frozen=True, slots=True)
class Config:
    """Application configuration loaded from environment variables."""

    email_user: str = ""
    email_pass: str = ""
    email_recipient: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    max_rcp_items: int = 25
    max_clist_items: int = 25
    max_drudge_items: int = 60
    rcp_url: str = "https://www.realclearpolitics.com/"
    clist_url: str = "https://atlanta.craigslist.org/search/sad"
    drudge_url: str = "https://www.drudgereport.com/"

    @classmethod
    def from_env(cls) -> Config:
        recipient = _env("EMAIL_RECIPIENT")
        return cls(
            email_user=_env("EMAIL_USER"),
            email_pass=_env("EMAIL_PASS"),
            email_recipient=recipient if recipient else _env("EMAIL_USER"),
            smtp_host=_env("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(_env("SMTP_PORT", "587")),
            max_rcp_items=int(_env("MAX_RCP_ITEMS", "25")),
            max_clist_items=int(_env("MAX_CLIST_ITEMS", "25")),
            max_drudge_items=int(_env("MAX_DRUDGE_ITEMS", "60")),
            rcp_url=_env("RCP_URL", "https://www.realclearpolitics.com/"),
            clist_url=_env("CLIST_URL", "https://atlanta.craigslist.org/search/sad"),
            drudge_url=_env("DRUDGE_URL", "https://www.drudgereport.com/"),
        )

    def validate(self) -> None:
        if not self.email_user or not self.email_pass:
            raise ValueError("EMAIL_USER and EMAIL_PASS environment variables are required")
