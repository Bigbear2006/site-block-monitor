from django.http import HttpRequest, HttpResponse

from bot.loader import logger
from core.tasks import notify_site_status


def ping_admin_webhook(request: HttpRequest):
    logger.info(f'ping-admin webhook received params: {request.GET}')
    task_id = request.GET.get('id')
    status = request.GET.get('status')
    if status and task_id:
        notify_site_status.apply_async(args=(task_id, status))
    return HttpResponse('2bca3530a9ecdef5712f13b29089cf00')
