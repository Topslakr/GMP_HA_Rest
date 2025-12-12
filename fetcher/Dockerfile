FROM debian:13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 \
      python3-pip \
      ca-certificates \
      tzdata \
      cron \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir greenmountainpower --break-system-packages

WORKDIR /app
COPY app.py /app/app.py

# Copy your cron schedule into place
COPY fetch-cron /etc/cron.d/fetch-cron

# Required permissions for cron
RUN chmod 0644 /etc/cron.d/fetch-cron \
 && crontab /etc/cron.d/fetch-cron

# Run cron in foreground
CMD ["cron", "-f"]
