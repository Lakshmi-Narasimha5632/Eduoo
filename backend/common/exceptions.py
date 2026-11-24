"""Standardized API exceptions and error handler for Eduoo."""

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


class EduooAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "BAD_REQUEST"
    default_detail = "An error occurred."

    def __init__(self, message=None, code=None, status_code=None, details=None):
        self.message = message or self.default_detail
        self.code = code or self.default_code
        if status_code is not None:
            self.status_code = status_code
        self.details = details
        super().__init__(detail=self.message, code=self.code)


class PlatformNotConnectedError(EduooAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "PLATFORM_NOT_CONNECTED"
    default_detail = "Please connect your platform account first."


class ResourceNotFoundError(EduooAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "NOT_FOUND"
    default_detail = "The requested resource was not found."


def standard_error_response(code: str, message: str, status_code: int = 400, details=None):
    """Helper to return standardized error format per Section 38."""
    error_body = {
        "code": code,
        "message": message,
    }
    if details:
        error_body["details"] = details
    return Response(
        {
            "success": False,
            "error": error_body,
        },
        status=status_code,
    )


def standard_success_response(data=None, message=None, status_code: int = 200, **kwargs):
    """Helper to return standardized success format."""
    payload = {"success": True}
    if message:
        payload["message"] = message
    if data is not None:
        if isinstance(data, dict):
            payload.update(data)
        else:
            payload["data"] = data
    if kwargs:
        payload.update(kwargs)
    return Response(payload, status=status_code)


def custom_exception_handler(exc, context):
    """DRF custom exception handler ensuring standardized responses."""
    response = exception_handler(exc, context)

    if response is not None:
        error_code = getattr(exc, "default_code", "API_ERROR")
        if hasattr(exc, "get_codes"):
            codes = exc.get_codes()
            if isinstance(codes, str):
                error_code = codes.upper()
            elif isinstance(codes, list) and codes:
                error_code = str(codes[0]).upper()
            elif isinstance(codes, dict) and codes:
                first_key = next(iter(codes))
                first_val = codes[first_key]
                error_code = str(first_val[0] if isinstance(first_val, list) else first_val).upper()

        if isinstance(response.data, dict):
            detail = response.data.get("detail")
            if detail:
                message = str(detail)
            else:
                first_key = next(iter(response.data))
                val = response.data[first_key]
                message = f"{first_key}: {val[0] if isinstance(val, list) else val}"
        else:
            message = str(response.data)

        response.data = {
            "success": False,
            "error": {
                "code": str(error_code),
                "message": message,
            },
        }

    return response
