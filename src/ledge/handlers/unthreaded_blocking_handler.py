"""
A demo handler module.

This demo demonstrates that a blocking unthreaded handler will break things.

Threading handlers is the default behavior. It is explicitly disabled here.
"""

from time import sleep

from ledge import HandlerImplementation

# Because our implementations are simple we need to disable
# a few pylint checks. You should remove the following comment
# if you are copy-pasting this module as a template for your own.

# pylint: disable=no-self-use,unused-argument


class UnThreadedBlockingHandler(HandlerImplementation):
    """
    A demo handler.

    This demo handler accepts every request and blocks for a while,
    it is not threaded, so exhausts the threadpool and then causes
    responses to block.
    """

    NOT_THREAD_SAFE = True  # <-- what causes the breaking
    name = "unthreaded_blocking_handler"

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
        Log + Block.

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The request's content.
        """
        request.logger.msg("UnThreadedBlockingHandler sleep starting")
        sleep(60)  # 1 minute
        request.logger.msg("UnThreadedBlockingHandler sleep finished")
