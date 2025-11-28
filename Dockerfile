FROM python:3.12-slim

# Keep Python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install small utilities for healthcheck
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source
COPY . .

# Make entrypoint executable
RUN chmod +x /app/scripts/entrypoint.sh || true

# Flask runtime configuration
ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=8000 \
    FLASK_ENV=production

EXPOSE 8000

# Ensure required runtime directories exist, then start Flask
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["flask", "run"]
