class WalletServiceError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InsufficientFundsError(WalletServiceError):
    def __init__(self, message="Insufficient funds"):
        super().__init__(message, status_code=400)


class NotFoundError(WalletServiceError):
    def __init__(self, message="Not found"):
        super().__init__(message, status_code=404)


class ConflictError(WalletServiceError):
    def __init__(self, message="Conflict"):
        super().__init__(message, status_code=409)


class IdempotencyInProgressError(WalletServiceError):
    def __init__(self, message="Request with this idempotency key is still processing"):
        super().__init__(message, status_code=409)


def custom_exception_handler(exc, context):
    from rest_framework.response import Response
    from rest_framework.views import exception_handler

    if isinstance(exc, WalletServiceError):
        return Response({"error": exc.message}, status=exc.status_code)

    return exception_handler(exc, context)
