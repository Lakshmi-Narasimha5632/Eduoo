from django.urls import path

from .views import (
    create_insight,
    dismiss_insight_view,
    generate_insights_view,
    insights_list,
)

urlpatterns = [
    path("", insights_list, name="insights-list"),
    path("create/", create_insight, name="insights-create"),
    path("generate/", generate_insights_view, name="insights-generate"),
    path("<int:insight_id>/dismiss/", dismiss_insight_view, name="insights-dismiss"),
]
