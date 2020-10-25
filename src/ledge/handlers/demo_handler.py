"""A demo handler module."""

from ledge import HandlerImplementation

# Because our implementations are simple we need to disable
# a few pylint checks. You should remove the following comment
# if you are copy-pasting this module as a template for your own.

# pylint: disable=no-self-use,unused-argument


class DemoHandler(HandlerImplementation):
    """
    A demo handler.

    This demo handler accepts every request and writes a simple
    string to the logs.
    """

    name = "demo_handler"

    def handles(self, request, content):
        """
        Handle every incoming request.

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The request's content.

        :rtype: bool
        :returns: Whether or not this implementation should handle the
        provided request.
        """
        return True

    def handle(self, request, content):
        """
        Write a simple string to the logs.

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The request's content.
        """
        request.logger.msg("Demo handler handling request!")
