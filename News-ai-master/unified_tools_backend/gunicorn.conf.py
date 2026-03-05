# Gunicorn configuration for News AI Backend

import multiprocessing
import os

# Server socket
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout
timeout = 30
keepalive = 10

# Logging
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'news_ai_backend'

# Server mechanics
preload_app = True
pidfile = '/tmp/gunicorn.pid'
user = os.getenv('USER', None)
group = os.getenv('GROUP', None)
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Development vs Production
if os.getenv('ENVIRONMENT') == 'development':
    reload = True
    workers = 1
    loglevel = 'debug'