from datetime import date
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DailyTask, DailyTaskPlan
from .serializers import DailyTaskPlanSerializer, DailyTaskSerializer
from .services import DailyTaskPlanner, DailyTaskReportService


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def task_list_or_create(request):
    if request.method == "GET":
        plan = DailyTaskPlanner.get_or_create_plan(request.user, timezone.now().date())
        tasks = plan.tasks.all()
        return Response({"success": True, "tasks": DailyTaskSerializer(tasks, many=True).data})

    # POST: create custom task
    plan = DailyTaskPlanner.get_or_create_plan(request.user, timezone.now().date())
    title = request.data.get("title", "").strip()
    if not title:
        return Response({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Title is required."}}, status=status.HTTP_400_BAD_REQUEST)

    task = DailyTask.objects.create(
        plan=plan,
        title=title,
        description=request.data.get("description", "").strip(),
        task_type=request.data.get("task_type", "general"),
        topic=request.data.get("topic", "Self-Directed"),
        difficulty=request.data.get("difficulty", "medium").lower(),
        estimated_minutes=int(request.data.get("estimated_minutes") or 30),
        problem_url=request.data.get("external_url") or request.data.get("problem_url") or "",
        status="pending",
    )
    plan.total_minutes = sum(t.estimated_minutes for t in plan.tasks.all())
    plan.completion_report_sent = False
    plan.save(update_fields=["total_minutes", "completion_report_sent", "updated_at"])

    return Response({"success": True, "task": DailyTaskSerializer(task).data}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def today_tasks(request):
    plan = DailyTaskPlanner.generate_for_user(request.user, timezone.now().date())
    serializer = DailyTaskPlanSerializer(plan)
    return Response({"success": True, "plan": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_tasks_view(request):
    plan = DailyTaskPlanner.get_or_create_plan(request.user, timezone.now().date())
    # Clear existing tasks to regenerate fresh adaptive plan
    plan.tasks.all().delete()
    variation = int(request.data.get("variation") or int(timezone.now().timestamp() % 100))
    plan = DailyTaskPlanner.generate_for_user(request.user, timezone.now().date(), variation=variation)
    serializer = DailyTaskPlanSerializer(plan)
    return Response({"success": True, "plan": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_task(request, task_id):
    try:
        task = DailyTask.objects.get(id=task_id, plan__user=request.user)
    except DailyTask.DoesNotExist:
        return Response(
            {"success": False, "error": {"code": "TASK_NOT_FOUND", "message": "Task not found."}},
            status=status.HTTP_404_NOT_FOUND,
        )

    completed_task = DailyTaskPlanner.complete_task(task)
    plan = completed_task.plan
    if plan.status == "completed":
        try:
            DailyTaskReportService.send_completion_report(plan)
        except Exception:
            pass

    return Response({
        "success": True,
        "task": DailyTaskSerializer(completed_task).data,
        "plan": DailyTaskPlanSerializer(plan).data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_task(request, task_id):
    try:
        task = DailyTask.objects.get(id=task_id, plan__user=request.user)
    except DailyTask.DoesNotExist:
        return Response(
            {"success": False, "error": {"code": "TASK_NOT_FOUND", "message": "Task not found."}},
            status=status.HTTP_404_NOT_FOUND,
        )

    plan = task.plan
    if task.status == "completed":
        task.status = "pending"
        task.completed_at = None
        task.save(update_fields=["status", "completed_at"])
    else:
        task.status = "completed"
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at"])

    # Recalculate plan completed minutes
    plan.completed_minutes = sum(item.estimated_minutes for item in plan.tasks.filter(status="completed"))
    was_already_completed = plan.status == "completed"
    if plan.total_minutes > 0 and plan.completed_minutes >= plan.total_minutes:
        plan.status = "completed"
    elif plan.completed_minutes > 0:
        plan.status = "in_progress"
        plan.completion_report_sent = False
    else:
        plan.status = "planned"
        plan.completion_report_sent = False
    plan.save(update_fields=["completed_minutes", "status", "completion_report_sent", "updated_at"])

    # Update StudyProgress
    try:
        from progress.models import StudyProgress
        study_progress, _ = StudyProgress.objects.get_or_create(user=plan.user, date=plan.date)
        study_progress.tasks_completed = plan.tasks.filter(status="completed").count()
        study_progress.study_minutes = plan.completed_minutes
        study_progress.save(update_fields=["tasks_completed", "study_minutes", "updated_at"])
    except Exception:
        pass

    # Trigger real-time milestone notification & automated email report
    if plan.status == "completed" and not was_already_completed:
        try:
            DailyTaskReportService.send_completion_report(plan)
        except Exception:
            pass

    return Response({
        "success": True,
        "task": DailyTaskSerializer(task).data,
        "plan": DailyTaskPlanSerializer(plan).data,
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    try:
        task = DailyTask.objects.get(id=task_id, plan__user=request.user)
    except DailyTask.DoesNotExist:
        return Response(
            {"success": False, "error": {"code": "TASK_NOT_FOUND", "message": "Task not found."}},
            status=status.HTTP_404_NOT_FOUND,
        )

    plan = task.plan
    task.delete()
    plan.total_minutes = sum(t.estimated_minutes for t in plan.tasks.all())
    plan.completed_minutes = sum(t.estimated_minutes for t in plan.tasks.filter(status="completed"))
    plan.save(update_fields=["total_minutes", "completed_minutes", "updated_at"])
    return Response({
        "success": True,
        "message": "Task deleted successfully.",
        "plan": DailyTaskPlanSerializer(plan).data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_daily_task_report_view(request):
    """Dispatches either completion report or incomplete tasks alert email to the user's verified email."""
    force = bool(request.data.get("force", True))
    report_type = request.data.get("type")
    plan = DailyTaskPlanner.get_or_create_plan(request.user, timezone.now().date())
    if report_type == "incomplete":
        res = DailyTaskReportService.send_incomplete_alert(plan, force=force)
    elif report_type == "completion":
        res = DailyTaskReportService.send_completion_report(plan, force=force)
    else:
        res = DailyTaskReportService.send_daily_status(request.user, force=force)
    return Response(res, status=status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST)

