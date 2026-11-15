class BusinessError(Exception):
    """Expected domain error safe to expose through the API."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
