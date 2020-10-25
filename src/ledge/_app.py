"""Ledge application logic."""

from twisted.internet import reactor, task


class Ledge:
    """The application itself."""

    def __init__(self, config, init_handlers=True, init_responders=True):
        """
        Attach the config to the instance.

        If the corresponding kwargs are passed call init_handlers and
        init_responders.
        """
        self.config = config
        self._responders = []
        self._handlers = []

        if init_handlers:
            self.init_handlers()
        if init_responders:
            self.init_responders()

    def init_handlers(self):
        """Initialize the handlers specified in the config."""
        for impl in self.config.handlers:
            self._handlers.append(impl(self.config))

    def init_responders(self):
        """Initialize the responders specified in the config."""
        for impl in self.config.responders:
            self._responders.append(impl(self.config))

    def _default_response(self, request):  # pylint: disable=no-self-use
        """Return an empty response, with status code 200."""
        request.setResponseCode(200)
        request.finish()

    def schedule_response(self, request, content):
        """
        Schedule the response to the request.

        This method iterates through all the assigned responders, if one
        reports that it handles the request that responder will send the
        response.

        If no responders are interested in the request self._default_response
        will be called.

        All functions are called via reactor.callLater so we can move on
        to dealing with the handlers. However eventually all the response
        functions will run in the reactor thread (so they shouldn't block).

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The content of the request.

        :rtype: `twisted.internet.defer.Deferred`
        :returns: A deferred representing the eventual response to the request.
        """
        for responder in self._responders:
            if responder.handles(request, content):
                request.logger.msg(f"Responder {responder.name} handles this request.")
                return task.deferLater(reactor, 0, responder.respond, request, content)
        request.logger.msg("No responders detected for request. Using default.")
        return task.deferLater(reactor, 0, self._default_response, request)

    def schedule_handlers(self, request, content):
        """
        Schedule the appropriate handlers to run.

        These can run in either the reactor thread or their own thread, depending
        on the plugin class.

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The content of the request.

        :rtype: List[`twisted.internet.defer.Deferred]
        :returns: A list of deferreds representing the eventual handler results.
        """
        results = []
        for handler in self._handlers:
            # Handler.process returns a deferred
            results.append(handler.process(request, content))
        return results

    def handle_request(self, request, content):
        """
        Schedule a response + schedule the handlers.

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The content of the request.

        :rtype: Tuple[
            `twisted.internet.defer.Deferred`, List[twisted.internet.defer.Deferred]
          ]
        :returns: A tuple, with the first element being a deferred representing the
          the eventual response to the request, and the second element being a list
          of deferreds representing the eventual results of all handlers.
        """
        return (
            self.schedule_response(request, content),
            self.schedule_handlers(request, content),
        )
