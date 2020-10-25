"""
A handler that prints request content to the logs.

This moudle contains the handler itself and its associated subconfig.
"""

import environ

from ledge import HandlerImplementation

# pylint: disable=unused-argument,no-self-use


class SubConfig:  # pylint: disable=too-few-public-methods
    """EchoHandler subconfig."""

    max_chars = environ.var(
        converter=int,
        default=500,
        help="The maximum number of characters to log from request content "
        "before truncating. If this value is negative the entirety of the "
        "request content will be logged.",
    )


class EchoHandler(HandlerImplementation):
    """A handler that prints request content to the logs."""

    name = "echo_handler"
    subconfig = SubConfig

    def handles(self, request, content):
        """Handle all requests."""
        return True

    def handle(self, request, content):
        """Log the request content, potentially truncating it."""
        if content is None:
            request.logger.msg("Request had no content.")
            return
        try:
            request_content = content.decode("utf-8")
            if (
                len(request_content) > self.config.echo_handler.max_chars
                and self.config.echo_handler.max_chars > 0
            ):
                request.logger.msg(
                    f"Truncated request content: "
                    f"{request_content[0:self.config.echo_handler.max_chars]} "
                    f"[TRUNCATED]"
                )
            else:
                request.logger.msg(f"Request content: {request_content}")
        except UnicodeError:
            request.logger.msg("Could not decode request content.")
