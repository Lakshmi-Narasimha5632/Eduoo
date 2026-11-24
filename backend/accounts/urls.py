from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    change_password_view,
    login_view,
    logout_view,
    profile_view,
    register_view,
    resend_otp_view,
    target_roles_view,
    verify_email_otp_view,
)

urlpatterns = [
    path("auth/register/", register_view, name="register"),
    path("auth/verify-email/", verify_email_otp_view, name="verify_email_otp"),
    path("auth/resend-otp/", resend_otp_view, name="resend_otp"),
    path("auth/login/", login_view, name="login"),
    path("auth/logout/", logout_view, name="logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/profile/", profile_view, name="profile"),
    path("auth/password/change/", change_password_view, name="change_password"),
    path("auth/target-roles/", target_roles_view, name="target_roles"),
]
