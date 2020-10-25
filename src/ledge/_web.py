"""Twisted web components of Ledge."""


from twisted.internet import endpoints, reactor
from twisted.web import resource, server
from twisted.web.server import NOT_DONE_YET

from ._utils import inject_logger


class WebRoot(resource.Resource):
    """Class which represents the root of the webserver."""

    isLeaf = True

    def __init__(self, app):
        """Embed the ledge application."""
        self.app = app
        super().__init__()

    def render(self, request):
        """Add a logger to each request + delegate."""
        inject_logger(request)
        return super().render(request)

    def render_GET(self, request):  # pylint: disable=C0103,W0613,R0201
        """Debugging endpoint, so you can see when the server is running."""
        return "<html>Ledge is listening!</html>".encode("utf-8")

    def render_POST(self, request):  # pylint: disable=invalid-name
        """Provide the request to the Ledge instance."""
        # Twisted doesn't like preserving access to content when
        # we use callLater - so we manually read it.
        content = request.content.read(self.app.config.max_content_length)
        # Check to see if there is data left...
        if request.content.read(1):
            request.logger.msg("Request content too large - dropping.")
            request.setResponseCode(413)
            return b""
        content_len = len(content)
        request.logger.msg(f"Content length: {str(content_len)}")
        reactor.callLater(0, self.app.handle_request, request, content)
        return NOT_DONE_YET


def configure_site(app, port=8080):
    """
    Configure the Webroot to listen on a TCP port.

    This should be called before `reactor.run`.
    """
    # Configure twisted
    site = server.Site(WebRoot(app))
    endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
    endpoint.listen(site)
