#!/bin/sh
set -e

# Export runtime env so cron can see it
printenv > /etc/environment

# Start cron in foreground
exec cron -f
