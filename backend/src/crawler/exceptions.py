"""Custom exceptions for crawler module."""


class DomainMismatchException(Exception):
    """Exception raised when URL domain doesn't match expected news website domain.

    Attributes:
        url: The invalid URL that caused the exception
        message: Explanation of the error
    """

    def __init__(self, url: str, message: str = "URL domain does not match news website domain"):
        """Initialize DomainMismatchException.

        Args:
            url: The invalid URL
            message: Custom error message (optional)
        """
        self.url = url
        self.message = f"{message}: {url}"
        super().__init__(self.message)
