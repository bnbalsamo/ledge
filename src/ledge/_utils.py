"""Various internal uility functions for ledge."""

import string
from itertools import chain
from uuid import uuid4

import structlog


def inject_logger(request):
    """
    Injects a structlog logger object onto the request.

    This logger contains some basic information about the request.

    Mutates the provided request object. Returns it as a convenience.
    """
    logger = structlog.getLogger()
    request.logger = logger.new(
        request_id=uuid4().hex,
        method=request.method.decode("utf-8"),
        path=request.path.decode("utf-8"),
        client_ip=request.getClientIP(),
    )
    return request


def make_name_safe(name):
    """
    Given a string make it safe to use as an env var.

    At the moment this is used on plugin names when they need to be
    made into subconfig prefixes.
    """
    # TODO: Make this better (anything that makes sense in an env var)
    other_stuff = set(("_", "-"))
    acceptable_set = set(chain(string.ascii_letters, string.digits, other_stuff))
    safe_name = ""
    for character in name:
        if character in acceptable_set:
            safe_name = safe_name + character
        else:
            safe_name = safe_name + "x"
    return safe_name
