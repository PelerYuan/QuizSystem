#!/bin/sh
set -e

# Ensure required directories exist (works for both named volumes and bind mounts)
mkdir -p /app/data /app/img /app/quiz /app/result /app/tmp

# Optionally relax permissions if running as non-root (commented out by default)
# chown -R $(id -u):$(id -g) /app/data /app/img /app/quiz /app/result /app/tmp 2>/dev/null || true

exec "$@"
