web: sh /entrypoint.sh
worker: celery --workdir=. -A proj worker --concurrency=1 -l debug --max-tasks-per-child=5
celery_beat: celery --workdir=. -A proj beat -l warning --scheduler django_celery_beat.schedulers:DatabaseScheduler