# Gunicorn configuration for high performance production deployment
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Preload app for better performance
preload_app = True

# User and group to run as (non-root for security)
user = "app"
group = "app"

# Logging
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "quizsystem"

# Graceful timeout for worker shutdown
graceful_timeout = 30

# Enable async workers for better I/O performance (uncomment if needed)
# worker_class = "gevent"
# worker_connections = 1000

# Memory management
# max_requests = 1000
# max_requests_jitter = 100

# SSL (uncomment if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Development vs Production settings
if os.getenv('FLASK_ENV') == 'development':
    reload = True
    workers = 1
    loglevel = "debug"