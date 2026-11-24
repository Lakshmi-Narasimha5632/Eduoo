from django.urls import path

from .views import (
    complete_task,
    delete_task,
    generate_tasks_view,
    send_daily_task_report_view,
    task_list_or_create,
    today_tasks,
    toggle_task,
)

urlpatterns = [
    path("", task_list_or_create, name="task-list-create"),
    path("today/", today_tasks, name="tasks-today"),
    path("generate/", generate_tasks_view, name="tasks-generate"),
    path("send-daily-report/", send_daily_task_report_view, name="tasks-send-daily-report"),
    path("<int:task_id>/", delete_task, name="task-delete"),
    path("<int:task_id>/complete/", complete_task, name="task-complete"),
    path("<int:task_id>/toggle/", toggle_task, name="task-toggle"),
]
