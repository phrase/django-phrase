try:
    # Django >= 2.1 uses TokenType enum.
    from django.template.base import TokenType

    TOKEN_MAPPING = None
    TOKEN_TEXT = TokenType.TEXT
    TOKEN_VAR = TokenType.VAR
    TOKEN_BLOCK = TokenType.BLOCK
except ImportError:
    # Django < 2.1 has these literals
    from django.template.base import TOKEN_TEXT, TOKEN_VAR, TOKEN_BLOCK, TOKEN_MAPPING

from six import string_types


def is_string_type(value):
    """Return whether given value is of a known string type."""
    return isinstance(value, string_types)
