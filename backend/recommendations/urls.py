from django.urls import path

from .views import (
    create_recommendation,
    generate_recommendations_view,
    recommendations_list,
    update_recommendation_status,
)

urlpatterns = [
    path("", recommendations_list, name="recommendations-list"),
    path("create/", create_recommendation, name="recommendations-create"),
    path("generate/", generate_recommendations_view, name="recommendations-generate"),
    path("<int:recommendation_id>/status/", update_recommendation_status, name="recommendations-status"),
]
