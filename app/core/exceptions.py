"""Typed application errors that can be safely rendered at the API boundary."""


class OSSentinelError(Exception):
    status_code = 400
    public_message = "The request could not be completed."


class AuthenticationError(OSSentinelError):
    status_code = 401
    public_message = "Authentication is required."


class AuthorizationError(OSSentinelError):
    status_code = 403
    public_message = "You do not have permission to perform this action."


class ExternalServiceError(OSSentinelError):
    status_code = 502
    public_message = "An external service is temporarily unavailable."
