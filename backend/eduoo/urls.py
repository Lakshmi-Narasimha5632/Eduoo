from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    return JsonResponse(
        {
            "status": "healthy",
            "service": "Eduoo Backend API",
            "version": "1.0.0",
        }
    )


urlpatterns = [
    path("", health_check, name="root-health-check"),
    path("api/health/", health_check, name="api-health-check"),
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/platforms/", include("platforms.urls")),
    path("api/insights/", include("insights.urls")),
    path("api/recommendations/", include("recommendations.urls")),
    path("api/tasks/", include("tasks.urls")),
    path("api/progress/", include("progress.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/resume/", include("resume.urls")),
    path("api/skill-gaps/", include("skill_gaps.urls")),
    path("api/skills/", include("skills.urls")),
    path("api/mock-interviews/", include("mock_interviews.urls")),
    path("api/ai-evaluation/", include("ai_evaluation.urls")),
    path("api/interviews/", include("interviews.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
