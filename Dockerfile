FROM python:3.12-slim

WORKDIR /app

# Copy package definition and source first so pip layer is cached separately
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install runtime deps only (no dev extras)
RUN pip install --no-cache-dir .

# Output files (RCPheadlines.txt, jobs.txt, RCPlinks.csv) are written to /data.
# Mount a host directory here to persist them across runs:
#   docker run -v $(pwd)/output:/data ...
VOLUME /data
WORKDIR /data

# Required — must be supplied via docker run -e or an env file:
#   EMAIL_USER   Gmail address used to send
#   EMAIL_PASS   Gmail app password
# Optional:
#   EMAIL_RECIPIENT  defaults to EMAIL_USER
#   SMTP_HOST        defaults to smtp.gmail.com
#   SMTP_PORT        defaults to 587
ENV EMAIL_USER="" \
    EMAIL_PASS="" \
    EMAIL_RECIPIENT="" \
    SMTP_HOST="smtp.gmail.com" \
    SMTP_PORT="587"

ENTRYPOINT ["python", "-m", "scrape_n_email"]
