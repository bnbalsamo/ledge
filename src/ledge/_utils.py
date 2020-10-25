"""Various internal uility functions for ledge."""

import string
from itertools import chain
from uuid import uuid4

import structlog
from twisted.internet import reactor, task, threads


def callInThread_or_callLater(kls, func, *args):  # pylint: disable=invalid-name
    """
    Implement the interface for plugin defined async strategies.

    Calls "kls.func" with *args via either
    :func:`twisted.internet.task.deferLater` or
    :func:`twisted.internet.threads.deferToThread`

    If the class has a "NOT_THREAD_SAFE" attr set to a truth-y value
    use callLater, otherwise use callInThread.
    """
    # This is a kind of generous assumption to make, but it provides
    # the kind of async behavior expected in webhook implementations
    if hasattr(kls, "NOT_THREAD_SAFE") and kls.NOT_THREAD_SAFE:
        return task.deferLater(reactor, 0, func, *args)
    return threads.deferToThread(func, *args)


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
