# Pre-PR Checklist

- Summarize what changed and why.
- Mention whether the change affects RCP, Craigslist, Drudge, CSV, mailer, CI, or docs.
- Include commands run and results.
- Confirm no generated scrape outputs or secrets are included.
- For parser changes, explain the fixture or live-site behavior represented.
- For mailer changes, confirm SMTP was mocked in tests.
- Document any live-site or real-email checks not performed.
