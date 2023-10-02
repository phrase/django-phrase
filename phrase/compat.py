from six import string_types


def is_string_type(value):
    """Return whether given value is of a known string type."""
    return isinstance(value, string_types)
