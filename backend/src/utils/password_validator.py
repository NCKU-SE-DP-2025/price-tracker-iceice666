"""Password strength validation and complexity requirements."""

import re
from typing import Optional


class PasswordStrength:
    """Password complexity validation with configurable requirements.

    Enforces strong password policies to prevent brute force attacks
    and improve overall account security.

    Configuration:
        MIN_LENGTH: Minimum password length (default: 8)
        REQUIRE_UPPERCASE: Require at least one uppercase letter
        REQUIRE_LOWERCASE: Require at least one lowercase letter
        REQUIRE_DIGIT: Require at least one digit
        REQUIRE_SPECIAL: Require at least one special character
    """

    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True

    # Common passwords to reject (top 20 most common)
    COMMON_PASSWORDS = {
        "password", "123456", "12345678", "qwerty", "abc123",
        "monkey", "1234567", "letmein", "trustno1", "dragon",
        "baseball", "111111", "iloveyou", "master", "sunshine",
        "ashley", "bailey", "passw0rd", "shadow", "123123",
    }

    @classmethod
    def validate(cls, password: str) -> Optional[str]:
        """Validate password strength against complexity requirements.

        Args:
            password: Plain text password to validate

        Returns:
            None if password is valid, error message string if invalid

        Examples:
            >>> PasswordStrength.validate("weak")
            'Password must be at least 8 characters'

            >>> PasswordStrength.validate("password")
            'Password is too common'

            >>> PasswordStrength.validate("NoDigits!")
            'Password must contain at least one digit'

            >>> PasswordStrength.validate("Strong123!")
            None  # Valid password
        """
        # Check minimum length
        if len(password) < cls.MIN_LENGTH:
            return f"Password must be at least {cls.MIN_LENGTH} characters"

        # Check against common passwords
        if password.lower() in cls.COMMON_PASSWORDS:
            return "Password is too common. Please choose a stronger password"

        # Check uppercase requirement
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return "Password must contain at least one uppercase letter"

        # Check lowercase requirement
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return "Password must contain at least one lowercase letter"

        # Check digit requirement
        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            return "Password must contain at least one digit"

        # Check special character requirement
        if cls.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;`~]', password):
            return "Password must contain at least one special character (!@#$%^&*...)"

        # Password meets all requirements
        return None

    @classmethod
    def get_requirements_description(cls) -> str:
        """Get human-readable description of password requirements.

        Returns:
            String describing all password requirements

        Examples:
            >>> PasswordStrength.get_requirements_description()
            'Password must be at least 8 characters and contain: uppercase letter, lowercase letter, digit, special character'
        """
        requirements = [f"at least {cls.MIN_LENGTH} characters"]

        if cls.REQUIRE_UPPERCASE:
            requirements.append("uppercase letter")
        if cls.REQUIRE_LOWERCASE:
            requirements.append("lowercase letter")
        if cls.REQUIRE_DIGIT:
            requirements.append("digit")
        if cls.REQUIRE_SPECIAL:
            requirements.append("special character")

        return f"Password must be {requirements[0]} and contain: {', '.join(requirements[1:])}"


def validate_username(username: str) -> Optional[str]:
    """Validate username format and security.

    Args:
        username: Username to validate

    Returns:
        None if valid, error message if invalid

    Examples:
        >>> validate_username("user123")
        None

        >>> validate_username("user@123")
        'Username can only contain letters, numbers, underscores, and hyphens'

        >>> validate_username("ab")
        'Username must be between 3 and 50 characters'
    """
    # Check length
    if len(username) < 3 or len(username) > 50:
        return "Username must be between 3 and 50 characters"

    # Check allowed characters (alphanumeric, underscore, hyphen only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return "Username can only contain letters, numbers, underscores, and hyphens"

    # Check doesn't start with special characters
    if username[0] in '_-':
        return "Username cannot start with underscore or hyphen"

    return None
