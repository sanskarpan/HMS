"""
Celery application configuration for Hospital Management System.
"""
from celery import Celery
from celery.schedules import crontab
from backend.config import get_config

config = get_config()


def make_celery(app=None):
    """
    Create and configure Celery instance.

    Args:
        app: Optional Flask application instance

    Returns:
        Configured Celery instance
    """
    celery = Celery(
        'hospital_tasks',
        broker=config.CELERY_BROKER_URL,
        backend=config.CELERY_RESULT_BACKEND,
        include=[
            'backend.app.tasks.reminders',
            'backend.app.tasks.reports',
            'backend.app.tasks.exports'
        ]
    )

    # Celery configuration
    celery.conf.update(
        # Task settings
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,

        # Task execution settings
        task_acks_late=True,
        task_reject_on_worker_lost=True,

        # Result backend settings
        result_expires=3600,  # Results expire after 1 hour

        # Worker settings
        worker_prefetch_multiplier=1,
        worker_concurrency=4,

        # Beat schedule for periodic tasks
        beat_schedule={
            'send-daily-reminders': {
                'task': 'backend.app.tasks.reminders.send_daily_reminders',
                'schedule': crontab(hour=8, minute=0),  # Run at 8 AM daily
            },
            'send-monthly-reports': {
                'task': 'backend.app.tasks.reports.send_monthly_reports',
                'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month at 9 AM
            },
            'cleanup-exports': {
                'task': 'backend.app.tasks.exports.cleanup_exports_task',
                'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
            },
        },

        # Task annotations for retry logic
        task_annotations={
            'backend.app.tasks.reminders.*': {
                'rate_limit': '10/m',
                'max_retries': 3,
                'default_retry_delay': 60
            },
            'backend.app.tasks.reports.*': {
                'rate_limit': '5/m',
                'max_retries': 3,
                'default_retry_delay': 120
            },
            'backend.app.tasks.exports.*': {
                'rate_limit': '20/m',
                'max_retries': 3,
                'default_retry_delay': 30
            }
        },
    )

    # If Flask app is provided, integrate with it
    if app is not None:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            """Task that runs within Flask application context."""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


# Create default celery instance
celery = make_celery()


def init_celery(app):
    """
    Initialize Celery with Flask application context.

    Args:
        app: Flask application instance

    Returns:
        Configured Celery instance with Flask context
    """
    global celery
    celery = make_celery(app)
    return celery
