class VarSomeAPIException(Exception):
    """Exception raised for VarSome API errors.

    For HTTP errors, *status* is the integer status code and *response*
    is the parsed JSON body (if available).  For connection-level errors
    (timeouts, refused connections) *status* is ``None`` and *response*
    carries a human-readable description.

    Attributes:
        status: HTTP status code, or ``None`` for connection-level errors.
        response: Optional response body / error description from the API.
    """

    ERROR_CODES: dict[int, str] = {
        400: (
            "Bad Request: a parameter you have passed is not valid, "
            "or something in your request is wrong."
        ),
        401: (
            "Unauthorized: authentication credentials are missing or invalid. "
            "Please provide a valid API token."
        ),
        403: (
            "Forbidden: you are authenticated but do not have permission "
            "to access this resource."
        ),
        404: (
            "Not Found: either you're requesting an invalid URI or the "
            "resource in question doesn't exist."
        ),
        429: (
            "Too Many Requests: you have exceeded the allowed request rate. "
            "Please wait before retrying."
        ),
        500: "Internal Server Error: an unexpected error occurred on the server.",
        501: (
            "Not Implemented: the requested feature or endpoint is not "
            "supported by the API."
        ),
        502: (
            "Bad Gateway: the upstream API is unreachable or returned an "
            "invalid response."
        ),
        503: (
            "Service Unavailable: the upstream API is temporarily unable to "
            "handle the request, possibly due to overload. Try again later."
        ),
        504: (
            "Gateway Timeout: the upstream API did not respond in time. "
            "Try again later."
        ),
    }

    def __init__(
        self,
        status: int | None,
        response: object = None,
    ) -> None:
        self.status = status
        self.response = response
        super().__init__(str(self))

    def __str__(self) -> str:
        if self.response is not None:
            detail = self.response
        elif self.status is not None:
            detail = self.ERROR_CODES.get(self.status, "Unknown error.")
        else:
            detail = "Unknown error."
        return f"{self.status} ({detail})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(status={self.status!r})"
