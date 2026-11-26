import secrets
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.db import models
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from notifications.models import NotificationPreference
from notifications.services import NotificationService
from .models import EmailVerificationOTP, UserProfile
from .serializers import LoginSerializer, ProfileUpdateSerializer, RegisterSerializer, UserSerializer

User = get_user_model()


def _generate_and_send_otp(user, sync: bool = False) -> dict:
    """Generates a secure 6-digit OTP, records it, and safely dispatches an email."""
    # Invalidate existing active OTPs
    EmailVerificationOTP.objects.filter(email__iexact=user.email, is_used=False).update(is_used=True)

    otp_code = f"{secrets.randbelow(900000) + 100000:06d}"
    EmailVerificationOTP.objects.create(
        user=user,
        email=user.email,
        otp_code=otp_code,
        expires_at=timezone.now() + timedelta(minutes=10),
    )

    try:
        print(f"\n[EDUOO REGISTRATION OTP FOR {user.email}]: {otp_code}\n", flush=True)
    except Exception:
        pass

    email_sent = False
    email_error = None
    try:
        res = NotificationService.send_registration_otp(
            recipient=user.email,
            otp_code=otp_code,
            full_name=user.full_name or user.username,
            sync=sync,
        )
        if isinstance(res, dict):
            email_sent = res.get("success", False)
            email_error = res.get("error")
    except Exception as exc:
        email_sent = False
        email_error = str(exc)

    return {
        "otp_code": otp_code,
        "email_sent": email_sent,
        "email_error": email_error,
    }



@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register_view(request):
    try:
        raw_email = (request.data.get("email") or "").strip().lower()
        require_verification = getattr(settings, "REQUIRE_EMAIL_VERIFICATION", True)

        # Check if an unverified user with this email already exists
        existing_unverified = User.objects.filter(email__iexact=raw_email, is_email_verified=False).first()
        if existing_unverified and request.data.get("password"):
            serializer = RegisterSerializer(existing_unverified, data=request.data, partial=True)
            if not serializer.is_valid():
                first_err = next(iter(serializer.errors.values())) if serializer.errors else "Registration failed."
                first_err = first_err[0] if isinstance(first_err, (list, tuple)) else str(first_err)
                return Response(
                    {"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(first_err), "details": serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = serializer.save()

            if not require_verification:
                user.is_active = True
                user.is_email_verified = True
                user.save(update_fields=["is_active", "is_email_verified"])
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "success": True,
                        "requires_verification": False,
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": UserSerializer(user).data,
                        "message": "Account created and activated successfully! Welcome to Eduoo.",
                    },
                    status=status.HTTP_201_CREATED,
                )

            user.is_active = False
            user.is_email_verified = False
            user.save(update_fields=["is_active", "is_email_verified"])
            otp_info = _generate_and_send_otp(user)
            otp_code = otp_info["otp_code"]

            msg = f"Verification code sent to {user.email}. Please enter the OTP to activate your account."
            expose_fallback = getattr(settings, "EXPOSE_OTP_FALLBACK", True)
            resp_payload = {
                "success": True,
                "requires_verification": True,
                "email": user.email,
                "message": msg,
            }
            if expose_fallback:
                resp_payload["otp_hint"] = otp_code
                resp_payload["message"] = (
                    f"Verification code sent to {user.email}. Direct code: {otp_code}"
                )
            return Response(resp_payload, status=status.HTTP_201_CREATED)

        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            first_err = "Registration failed."
            if serializer.errors:
                val = next(iter(serializer.errors.values()))
                first_err = val[0] if isinstance(val, (list, tuple)) else str(val)
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(first_err),
                        "details": serializer.errors,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()

        if not require_verification:
            user.is_active = True
            user.is_email_verified = True
            user.save(update_fields=["is_active", "is_email_verified"])
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "success": True,
                    "requires_verification": False,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data,
                    "message": "Registration successful! Welcome to Eduoo.",
                },
                status=status.HTTP_201_CREATED,
            )

        user.is_active = False
        user.is_email_verified = False
        user.save(update_fields=["is_active", "is_email_verified"])

        # Generate and dispatch 6-digit OTP verification email
        otp_info = _generate_and_send_otp(user)
        otp_code = otp_info["otp_code"]

        msg = f"Verification code sent to {user.email}. Please enter the 6-digit OTP to activate your account."
        expose_fallback = getattr(settings, "EXPOSE_OTP_FALLBACK", True)
        resp_payload = {
            "success": True,
            "requires_verification": True,
            "email": user.email,
            "message": msg,
            "user": UserSerializer(user).data,
        }
        if expose_fallback:
            resp_payload["otp_hint"] = otp_code
            resp_payload["message"] = (
                f"Verification code sent to {user.email}. Direct code: {otp_code}"
            )

        return Response(resp_payload, status=status.HTTP_201_CREATED)
    except Exception as exc:
        import logging
        import traceback
        logging.getLogger(__name__).error("Registration error: %s\n%s", exc, traceback.format_exc())
        return Response(
            {
                "success": False,
                "error": {
                    "code": "REGISTRATION_FAILED",
                    "message": f"Registration failed: {str(exc)}",
                    "details": str(exc),
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        first_err = "Registration failed."
        if serializer.errors:
            val = next(iter(serializer.errors.values()))
            first_err = val[0] if isinstance(val, (list, tuple)) else str(val)
        return Response(
            {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(first_err),
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()

    if not require_verification:
        user.is_active = True
        user.is_email_verified = True
        user.save(update_fields=["is_active", "is_email_verified"])
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "success": True,
                "requires_verification": False,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
                "message": "Registration successful! Welcome to Eduoo.",
            },
            status=status.HTTP_201_CREATED,
        )

    user.is_active = False
    user.is_email_verified = False
    user.save(update_fields=["is_active", "is_email_verified"])

    # Generate and dispatch 6-digit OTP verification email
    otp_info = _generate_and_send_otp(user)
    otp_code = otp_info["otp_code"]

    msg = f"Verification code sent to {user.email}. Please enter the 6-digit OTP to activate your account."
    expose_fallback = getattr(settings, "EXPOSE_OTP_FALLBACK", True)
    resp_payload = {
        "success": True,
        "requires_verification": True,
        "email": user.email,
        "message": msg,
        "user": UserSerializer(user).data,
    }
    if expose_fallback and (not otp_info.get("email_sent") or not getattr(settings, "EMAIL_HOST_USER", None) or settings.DEBUG):
        resp_payload["otp_hint"] = otp_code
        resp_payload["message"] = (
            f"Account created. If email delivery is delayed or blocked by your provider, your OTP is: {otp_code}"
        )

    return Response(resp_payload, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_email_otp_view(request):
    email = str(request.data.get("email") or "").strip().lower()
    otp = str(request.data.get("otp") or "").strip()

    if not email or not otp:
        return Response(
            {
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": "Email and 6-digit OTP are required."},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response(
            {
                "success": False,
                "error": {"code": "USER_NOT_FOUND", "message": "No account found with this email address."},
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # Find the latest unused OTP record
    otp_record = EmailVerificationOTP.objects.filter(email__iexact=email, is_used=False).first()
    if not otp_record:
        return Response(
            {
                "success": False,
                "error": {"code": "OTP_NOT_FOUND", "message": "No active verification code found. Please request a new one."},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if timezone.now() > otp_record.expires_at:
        otp_record.is_used = True
        otp_record.save(update_fields=["is_used"])
        return Response(
            {
                "success": False,
                "error": {"code": "OTP_EXPIRED", "message": "Verification code has expired. Please request a new code."},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if otp_record.attempts >= 5:
        otp_record.is_used = True
        otp_record.save(update_fields=["is_used"])
        return Response(
            {
                "success": False,
                "error": {"code": "OTP_LOCKED", "message": "Too many failed attempts. Please request a new verification code."},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if otp_record.otp_code != otp:
        otp_record.attempts += 1
        otp_record.save(update_fields=["attempts"])
        remaining = 5 - otp_record.attempts
        return Response(
            {
                "success": False,
                "error": {
                    "code": "INVALID_OTP",
                    "message": f"Incorrect verification code. {remaining} attempt(s) remaining.",
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Mark OTP as used
    otp_record.is_used = True
    otp_record.save(update_fields=["is_used"])

    # Activate user and mark email verified
    user.is_email_verified = True
    user.is_active = True
    user.save(update_fields=["is_email_verified", "is_active"])

    # Ensure notification preference has verified email configured
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)
    prefs.notification_email = user.email
    prefs.email_notifications = True
    prefs.realtime_task_email = True
    prefs.daily_task_reminders = True
    prefs.save()

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "success": True,
            "message": "Email verified successfully! Welcome to Eduoo.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def resend_otp_view(request):
    email = str(request.data.get("email") or "").strip().lower()
    if not email:
        return Response(
            {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Email is required."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response(
            {"success": False, "error": {"code": "USER_NOT_FOUND", "message": "No account found with this email."}},
            status=status.HTTP_404_NOT_FOUND,
        )

    if user.is_email_verified:
        return Response(
            {"success": False, "error": {"code": "ALREADY_VERIFIED", "message": "Your email is already verified. Please sign in."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Rate limiting: 60 seconds cooldown
    recent_otp = EmailVerificationOTP.objects.filter(
        email__iexact=email,
        created_at__gte=timezone.now() - timedelta(seconds=60),
    ).first()
    if recent_otp:
        return Response(
            {
                "success": False,
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "Please wait a minute before requesting another verification code.",
                },
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    otp_info = _generate_and_send_otp(user)
    otp_code = otp_info["otp_code"]
    msg = f"A fresh 6-digit verification code has been sent to {user.email}."
    expose_fallback = getattr(settings, "EXPOSE_OTP_FALLBACK", True)
    resp_payload = {
        "success": True,
        "message": msg,
    }
    if expose_fallback:
        resp_payload["otp_hint"] = otp_code
        resp_payload["message"] = (
            f"Fresh code generated for {user.email}. Direct code: {otp_code}"
        )
    return Response(resp_payload, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        first_err = "Validation error."
        if serializer.errors:
            val = next(iter(serializer.errors.values()))
            first_err = val[0] if isinstance(val, (list, tuple)) else str(val)
        return Response(
            {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(first_err),
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    identifier = serializer.validated_data.get("identifier") or serializer.validated_data.get("email") or serializer.validated_data.get("username", "")
    identifier = str(identifier).strip()
    password = serializer.validated_data["password"]

    # Support login via email or username (case-insensitive)
    user = None
    user_candidates = User.objects.filter(models.Q(email__iexact=identifier) | models.Q(username__iexact=identifier))
    for candidate in user_candidates:
        if candidate.check_password(password):
            user = candidate
            break

    if not user:
        # Fallback to standard Django authenticate
        user = authenticate(request, username=identifier, password=password)

    if not user:
        return Response(
            {
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email/username or password.",
                },
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    require_verification = getattr(settings, "REQUIRE_EMAIL_VERIFICATION", True)
    if require_verification and not user.is_email_verified:
        return Response(
            {
                "success": False,
                "error": {
                    "code": "EMAIL_NOT_VERIFIED",
                    "message": "Please verify your email address to log in. We have sent a verification code to your email.",
                    "email": user.email,
                },
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "success": True,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_200_OK,
    )




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"success": True, "message": "Logged out successfully."})
    except Exception:
        return Response(
            {"success": False, "error": {"code": "INVALID_REFRESH_TOKEN", "message": "Invalid refresh token."}},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    if request.method == "GET":
        return Response({"success": True, "user": UserSerializer(user).data})

    serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.full_name = user.full_name
    profile.college = user.college
    profile.branch = user.branch
    profile.graduation_year = user.graduation_year
    profile.target_role = user.target_role
    profile.daily_study_hours = user.daily_study_hours
    profile.bio = user.bio
    profile.preferred_learning_style = user.preferred_learning_style
    profile.experience_level = user.experience_level
    profile.career_goal = user.career_goal
    profile.save()

    return Response({"success": True, "user": UserSerializer(user).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    if not old_password or not new_password:
        return Response(
            {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Both old_password and new_password are required."}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(new_password) < 8:
        return Response(
            {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "New password must be at least 8 characters long."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from .services import UserService
    success, message = UserService.change_password(request.user, old_password, new_password)
    if not success:
        return Response(
            {"success": False, "error": {"code": "INVALID_PASSWORD", "message": message}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response({"success": True, "message": message})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def target_roles_view(request):
    from .services import UserService
    return Response({"success": True, "target_roles": UserService.get_supported_target_roles()})
