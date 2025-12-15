FROM debian:13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 \
      python3-pip \
      ca-certificates \
      tzdata \
      cron \
 && rm -rf /var/lib/apt/lists/*

ENV TZ=America/New_York

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN python3 -m pip install --no-cache-dir greenmountainpower --break-system-packages

WORKDIR /app
COPY app.py /app/app.py
COPY fetch-cron /etc/cron.d/fetch-cron
COPY entrypoint.sh /entrypoint.sh


# Required permissions for cron
RUN chmod 0644 /etc/cron.d/fetch-cron \
 && crontab /etc/cron.d/fetch-cron \
 && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
