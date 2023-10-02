from six import string_types

# Django >= 2.1 uses TokenType enum.
from django.template.base import TokenType

TOKEN_MAPPING = None
TOKEN_TEXT = TokenType.TEXT
TOKEN_VAR = TokenType.VAR
TOKEN_BLOCK = TokenType.BLOCK


def is_string_type(value):
    """Return whether given value is of a known string type."""
    return isinstance(value, string_types)
