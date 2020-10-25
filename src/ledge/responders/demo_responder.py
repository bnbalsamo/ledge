"""A simple demo responder."""

from ledge import ResponderImplementation
from ledge.helpers import text_response


class DemoResponder(ResponderImplementation):
    """A simple demo responder implementation."""

    name = "demo_responder"

    def handles(self, request, content):
        """Handle all requests."""
        return True

    def respond(self, request, content):
        """Return the string ":)" to every request with a 200 status code."""
        text_response(request, ":)")
        request.logger.msg("Response sent!")
