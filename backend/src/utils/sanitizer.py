"""HTML content sanitization to prevent XSS attacks."""

import bleach


# Allowed HTML tags for news content
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre',
]

# Allowed attributes for specific tags
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title'],
}

# Allowed protocols for links
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(text: str) -> str:
    """Sanitize HTML content to prevent XSS attacks.

    Removes potentially dangerous HTML/JavaScript while preserving
    safe formatting tags for news content display.

    Args:
        text: Raw HTML content that may contain malicious code

    Returns:
        Sanitized HTML safe for display

    Examples:
        >>> sanitize_html('<script>alert("XSS")</script><p>Safe content</p>')
        '&lt;script&gt;alert("XSS")&lt;/script&gt;<p>Safe content</p>'

        >>> sanitize_html('<a href="javascript:alert()">Click</a>')
        '<a>Click</a>'

        >>> sanitize_html('<p>Normal <strong>text</strong></p>')
        '<p>Normal <strong>text</strong></p>'
    """
    if not text:
        return ""

    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,  # Remove disallowed tags entirely
    )


def sanitize_text(text: str) -> str:
    """Strip all HTML tags and return plain text.

    Use this for content that should never contain HTML,
    such as titles, summaries, or user input fields.

    Args:
        text: Text that may contain HTML

    Returns:
        Plain text with all HTML removed

    Examples:
        >>> sanitize_text('<p>Hello <strong>World</strong></p>')
        'Hello World'

        >>> sanitize_text('Plain text')
        'Plain text'
    """
    if not text:
        return ""

    # Remove all HTML tags
    return bleach.clean(text, tags=[], strip=True)
