import sys


def ensure_is_python_string(content):
    """
    Python compatability function.
    Makes sure we get back a str type object for both py2 and py3.

        - In Py2 that means getting str from unicode objects
        - In Py3 that means getting a str from byte objects.
    """
    # If we have bytes (py3), decode.
    # If we have unicode (py2), encode.
    if not isinstance(content, str):
        if sys.version_info < (3, 0):
            # If we're in python 2.6 or 2.7 and we're not a string we're a
            # unicode.
            return content.encode('utf-8')
        else:
            # If we're in python 3 and we're not a string, we're a sequence
            # of bytes.
            return content.decode('utf-8')
    return content
