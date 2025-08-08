from rest_framework.response import Response as DRFResponse
from rest_framework import status as drf_status


class Response(DRFResponse):
    """
    A custom Response class that standardizes API responses across the project.

    This class wraps DRF's native Response object and enforces a consistent 
    response format for both successful and error responses.

    === Default Response Structure ===

    For success responses (status code < 400):
    {
        "success": true,
        "message": "Success",
        "data": {...}
    }

    For error responses (status code >= 400):
    {
        "success": false,
        "message": "Error message",
        "errors": {...}
    }

    === Parameters ===

    data (any, optional): 
        The payload to return in the "data" field (used for success responses).

    message (str, optional): 
        A human-readable message summarizing the response. Default is "Success".

    errors (dict, optional): 
        A dictionary of validation or business logic errors. Only shown if success is False.

    success (bool, optional): 
        Indicates whether the response represents a successful operation. Default is True.

    status (int, optional): 
        HTTP status code (e.g., 200, 201, 400, 404, etc.). Default is 200 OK.

    kwargs (dict): 
        Any additional keyword arguments passed to the base DRF Response.

    === Usage Example ===

        # Success example
        return Response(data={"id": 1, "email": "test@example.com"})

        # Error example
        return Response(success=False, message="Invalid credentials", errors={"email": ["Not found."]}, status=400)
    """

    def __init__(self, data=None, message="Success", errors=None, success=True, status=drf_status.HTTP_200_OK, **kwargs):
        payload = {
            "success": success,
            "message": message,
        }

        if success:
            payload["data"] = data
        else:
            payload["errors"] = errors or {}

        super().__init__(data=payload, status=status, **kwargs)
