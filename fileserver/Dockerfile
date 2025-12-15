FROM debian:13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 \
      tzdata \
 && rm -rf /var/lib/apt/lists/*

ENV TZ=America/New_York

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo $TZ > /etc/timezone

WORKDIR /data
CMD ["python3", "-m", "http.server", "8000"]
