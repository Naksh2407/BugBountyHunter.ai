import redis
from celery import Celery  # type: ignore

# Attempt to connect to local Redis
redis_running = False
try:
    r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=1, socket_connect_timeout=1)
    r.ping()
    redis_running = True
except Exception:
    pass

if redis_running:
    celery_app = Celery(
        "bugbountyhunter",
        broker="redis://127.0.0.1:6379/0",
        backend="redis://127.0.0.1:6379/0"
    )
else:
    # Use memory broker and SQLite backend for local development without Redis
    print("Redis is not running. Falling back to Celery Eager execution mode (synchronous execution).")
    celery_app = Celery(
        "bugbountyhunter",
        broker="memory://",
        backend="db+sqlite:///./celery_results.db"
    )
    celery_app.conf.task_always_eager = True

celery_app.conf.task_track_started = True