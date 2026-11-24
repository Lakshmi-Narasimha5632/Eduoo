from django.urls import path

from .views import analytics_dashboard, platform_analytics

urlpatterns = [
    path("", analytics_dashboard, name="analytics-dashboard"),
    path("<slug:platform>/", platform_analytics, name="platform-analytics"),
]
