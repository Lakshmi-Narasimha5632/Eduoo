"""
Celery asynchronous background tasks for platform telemetry synchronization.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except (ImportError, ModuleNotFoundError):
    def shared_task(func=None, **kwargs):
        if func is not None:
            return func
        def decorator(f):
            return f
        return decorator


@shared_task
def sync_all_active_platforms():
    """
    Background worker cron task to synchronize all connected platform profiles
    and update daily user study statistics.
    """
    from platforms.models import PlatformAccount
    from platforms.services import PlatformService

    accounts = PlatformAccount.objects.filter(is_active=True).select_related('user')
    success_count = 0
    failure_count = 0

    for account in accounts:
        try:
            PlatformService.sync_account(account)
            success_count += 1
        except Exception as e:
            logger.error("Failed to sync account %s for user %s: %s", account.platform, account.user_id, e)
            failure_count += 1

    logger.info("Background platform sync completed: %d succeeded, %d failed", success_count, failure_count)
    return {"synced": success_count, "failed": failure_count}


@shared_task
def sync_single_user_platforms(user_id: int):
    """
    Sync all connected accounts for a specific user.
    """
    from platforms.models import PlatformAccount
    from platforms.services import PlatformService

    accounts = PlatformAccount.objects.filter(user_id=user_id, is_active=True)
    results = {}
    for account in accounts:
        try:
            PlatformService.sync_account(account)
            results[account.platform] = "success"
        except Exception as e:
            results[account.platform] = f"failed: {str(e)}"
    return results
