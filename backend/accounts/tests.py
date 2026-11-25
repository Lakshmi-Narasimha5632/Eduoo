import pytest
from rest_framework.test import APIClient
from accounts.models import EmailVerificationOTP, User


@pytest.mark.django_db
class TestAuthAPI:
    def test_register_creates_unverified_user_and_sends_otp(self):
        client = APIClient()
        payload = {
            "email": "narasimha@example.com",
            "username": "narasimha",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "full_name": "Narasimha Reddy",
            "college": "IIT Hyderabad",
            "branch": "Computer Science",
            "graduation_year": 2027,
            "target_role": "Full Stack Developer",
            "daily_study_hours": 3.5,
            "preferred_learning_style": "project-based",
            "experience_level": "student",
            "bio": "Aspiring full stack developer.",
            "career_goal": "Become a senior full stack engineer.",
        }

        response = client.post("/api/auth/register/", payload, format="json")

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["requires_verification"] is True
        assert data["email"] == payload["email"]

        # Verify User and OTP were created
        user = User.objects.get(email=payload["email"])
        assert user.is_email_verified is False
        assert user.is_active is False

        otp_record = EmailVerificationOTP.objects.filter(email=payload["email"], is_used=False).first()
        assert otp_record is not None
        assert len(otp_record.otp_code) == 6

    def test_verify_email_otp_success(self):
        client = APIClient()
        signup = {
            "email": "verify_test@example.com",
            "username": "verify_test",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "full_name": "Verify Test User",
        }
        client.post("/api/auth/register/", signup, format="json")

        otp_record = EmailVerificationOTP.objects.filter(email=signup["email"], is_used=False).first()
        assert otp_record is not None

        # Verify with wrong OTP
        bad_res = client.post(
            "/api/auth/verify-email/",
            {"email": signup["email"], "otp": "000000"},
            format="json",
        )
        assert bad_res.status_code == 400
        assert bad_res.json()["error"]["code"] == "INVALID_OTP"

        # Verify with correct OTP
        good_res = client.post(
            "/api/auth/verify-email/",
            {"email": signup["email"], "otp": otp_record.otp_code},
            format="json",
        )
        assert good_res.status_code == 200
        body = good_res.json()
        assert body["success"] is True
        assert "access" in body and "refresh" in body
        assert body["user"]["email"] == signup["email"]

        # Check user is now verified & active
        user = User.objects.get(email=signup["email"])
        assert user.is_email_verified is True
        assert user.is_active is True

    def test_unverified_user_cannot_login_until_verified(self):
        client = APIClient()
        signup = {
            "email": "student@example.com",
            "username": "student",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "full_name": "Student User",
        }
        client.post("/api/auth/register/", signup, format="json")

        # Login attempt before verification
        login_res = client.post(
            "/api/auth/login/",
            {"email": "student@example.com", "password": "StrongPass123!"},
            format="json",
        )
        assert login_res.status_code == 403
        assert login_res.json()["error"]["code"] == "EMAIL_NOT_VERIFIED"

        # Verify OTP
        otp_record = EmailVerificationOTP.objects.filter(email=signup["email"], is_used=False).first()
        client.post(
            "/api/auth/verify-email/",
            {"email": signup["email"], "otp": otp_record.otp_code},
            format="json",
        )

        # Login attempt after verification
        login_res2 = client.post(
            "/api/auth/login/",
            {"email": "student@example.com", "password": "StrongPass123!"},
            format="json",
        )
        assert login_res2.status_code == 200
        assert "access" in login_res2.json()

    def test_resend_otp_rate_limiting(self):
        client = APIClient()
        signup = {
            "email": "resend_test@example.com",
            "username": "resend_test",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        client.post("/api/auth/register/", signup, format="json")

        # Immediate resend should be rate-limited
        resend_res = client.post(
            "/api/auth/resend-otp/",
            {"email": signup["email"]},
            format="json",
        )
        assert resend_res.status_code == 429
        assert resend_res.json()["error"]["code"] == "RATE_LIMITED"

    def test_profile_update(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="update_profile@example.com",
            username="update_profile",
            password="StrongPass123!",
            target_role="Software Developer",
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.put(
            "/api/auth/profile/",
            {"target_role": "AI Engineer", "daily_study_hours": 4.0},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["user"]["target_role"] == "AI Engineer"
        assert float(response.json()["user"]["daily_study_hours"]) == 4.0

    def test_change_password(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="pwd_change@example.com",
            username="pwd_change",
            password="OldPassword123!",
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/auth/password/change/",
            {"old_password": "OldPassword123!", "new_password": "NewStrongPassword123!"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        user.refresh_from_db()
        assert user.check_password("NewStrongPassword123!")

    def test_target_roles_list(self):
        client = APIClient()
        response = client.get("/api/auth/target-roles/")
        assert response.status_code == 200
        assert "target_roles" in response.json()
        assert "Full Stack Developer" in response.json()["target_roles"]

    def test_register_when_verification_disabled(self, settings):
        settings.REQUIRE_EMAIL_VERIFICATION = False
        client = APIClient()
        payload = {
            "email": "instant_user@example.com",
            "username": "instant_user",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "full_name": "Instant User",
        }
        response = client.post("/api/auth/register/", payload, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["requires_verification"] is False
        assert "access" in data and "refresh" in data

        user = User.objects.get(email="instant_user@example.com")
        assert user.is_email_verified is True
        assert user.is_active is True

    def test_login_with_invalid_or_expired_bearer_token(self, django_user_model):
        """Verify that stale Authorization headers in localStorage do not block login."""
        django_user_model.objects.create_user(
            email="stale_token_user@example.com",
            username="stale_token_user",
            password="StrongPass123!",
            is_email_verified=True,
            is_active=True,
        )
        client = APIClient()
        # Simulate browser sending an invalid/expired token from an old session
        client.credentials(HTTP_AUTHORIZATION="Bearer totally_invalid_corrupted_jwt_token_12345")
        response = client.post(
            "/api/auth/login/",
            {"email": "stale_token_user@example.com", "password": "StrongPass123!"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "access" in response.json()
