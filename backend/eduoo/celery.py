import os

try:
    from celery import Celery

    # Set default Django settings module for 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduoo.settings')

    app = Celery('eduoo')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()

    @app.task(bind=True, ignore_result=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')
except (ImportError, ModuleNotFoundError):
    app = None
