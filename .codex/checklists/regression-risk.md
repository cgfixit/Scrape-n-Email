# Regression Risk Checklist

- Could this break the daily Windows scheduled run?
- Could parser changes require live network in tests?
- Could generated files be accidentally committed?
- Could Gmail credentials, app passwords, or `.env` content leak?
- Could CSV output reintroduce formula-injection risk?
- Could RCP/Craigslist/Drudge selector changes drop valid headlines/jobs?
- Could mailer changes send real email during tests?
- Could a new dependency be avoided?
