from django.urls import path

from .views import dashboard_summary, dashboard_update

urlpatterns = [
    path("", dashboard_summary, name="dashboard-summary"),
    path("update/", dashboard_update, name="dashboard-update"),
]
