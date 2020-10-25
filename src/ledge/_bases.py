"""Base classes for plugin implementations."""
from typing import Optional

import environ

from ledge._utils import callInThread_or_callLater, make_name_safe

unset_names = {
    "default": "UNSET_NAME",
    "handler": "UNSET_HANDLER_NAME",
    "responder": "UNSET_RESPONDER_NAME",
}


class _Configurable:
    """
    Interface for classes that can provide subconfigs.

    Handler implementations and Responder implementations both inherit
    from this class.
    """

    #: The configurable objects name. Used for naming the subconfig.
    #: Override this in your plugin implementation. Leaving it set to the
    #: default will raise an error on init-ing your implementation.
    name = unset_names["default"]

    #: The subconfig object. This should be overridden in your subclass
    #: if you need to pass a subconfig up to the ledge configuration.
    #: It is expected to be a class that can be provided to
    #: :func:`environ.config`
    subconfig = None  # type: Optional[type]

    def __init__(self):
        """Check cls.name is set."""
        if self.name in unset_names.values():
            raise NotImplementedError(f"Name unset on {self}.")

    @classmethod
    def provides_subconfig(cls):
        """
        Let ledge know if we provide a subconfig.

        Returns True if `cls.subconfig` is set and truthy.

        :rtype: bool
        """
        return hasattr(cls, "subconfig") and cls.subconfig

    @classmethod
    def provide_subconfig(cls):
        """
        Provide the subconfig to ledge.

        Makes our plugin name implementation safe for mapping to env vars
        and returns it and whatever has been assigned to cls.subconfig, in
        that order, as a tuple.

        :rtype: tuple
        """
        return make_name_safe(cls.name), environ.config(cls.subconfig)


class HandlerImplementation(_Configurable):
    """Interface for classes that provide handlers."""

    #: The handler's name. Used for logging and naming the subconfig.
    #: Override this in your plugin implementation. Leaving it set to the
    #: default will raise an error on init-ing your implementation.
    name = unset_names["handler"]

    # TODO: Remove when upstream fix is available
    # https://github.com/sphinx-doc/sphinx/issues/741
    #: The subconfig object. This should be overridden in your subclass
    #: if you need to pass a subconfig up to the ledge configuration.
    #: It is expected to be a class that can be provided to
    #: :func:`environ.config`
    subconfig = None  # type: Optional[type]

    def __init__(self, config):
        """Attach the config to the instance."""
        self.config = config
        super().__init__()

    def handles(self, request, content):
        """
        Implement this in your subclass.

        It should return a bool, True if this implementation should
        handle the request, otherwise False.

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The content of the incoming request.

        :rtype: bool
        :returns: Whether or not this implementation should handle the
            provided request.
        """
        raise NotImplementedError

    def handle(self, request, content):
        """
        Implement this in your subclass.

        Note that this method will be run its own thread, unless
        cls.NOT_THREAD_SAFE is truthy.

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The content of the incoming request.
        """
        raise NotImplementedError

    def process(self, request, content):
        """
        Process the request.

        Determines whehter or not the handler handles the request by calling
        the plugin implemented `handles` method, and if it returns True
        calls the plugin implemented `handle` method using the proper
        async implementation.

        Plugin implementations should not need to override this method.

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The content of the incoming request.
        """
        request.logger.msg(f"Handler {self.name} processing request.")
        if self.handles(request, content):
            request.logger.msg(f"Handler {self.name} handles this request.")
            return callInThread_or_callLater(self, self.handle, request, content)
        request.logger.msg(f"Handler {self.name} doesn't handle this request.")
        return None


class ResponderImplementation(_Configurable):
    """Interface for classes that provide responders."""

    #: The handler's name. Used for logging.
    #: Override this in your plugin implementation. Leaving it set to the
    #: default will raise an error on init-ing your implementation.
    name = unset_names["responder"]

    # TODO: Remove when upstream fix is available
    # https://github.com/sphinx-doc/sphinx/issues/741
    #: The subconfig object. This should be overridden in your subclass
    #: if you need to pass a subconfig up to the ledge configuration.
    #: It is expected to be a class that can be provided to
    #: :func:`environ.config`
    subconfig = None  # type: Optional[type]

    def __init__(self, config):
        """Attach the config to the instance."""
        self.config = config
        super().__init__()

    def handles(self, request, content):
        """
        Implement this in your subclass.

        It should return a bool, True if this implementation should
        handle the request, otherwise False.

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The content of the incoming request.

        :rtype: bool
        :returns: Whether or not this implementation should handle the
            provided request.
        """
        raise NotImplementedError

    def respond(self, request, content):
        """
        Implement this in your subclass.

        Note that this method will be run in the reactor thread, so it
        should not block.

        At some point the implementation _must_ call `request.finish()`

        :param twisted.web.http.Request request: The incoming request.
        :param bytes content: The content of the incoming request.
        """
        raise NotImplementedError
