"""
Commands for controlling the ledge server.

Meant to be entrypoint targets.
"""

import sys

import environ
import structlog
from twisted.internet import reactor
from twisted.python.log import startLogging

from ._app import Ledge
from ._config import get_config, get_merged_conf_object
from ._web import configure_site


def start():
    """Start the ledge webserver."""
    # Get the config
    config = get_config()

    # --help
    if sys.argv[-1] == "--help":
        help_str = (
            "Ledge and its associated plugins are controlled via "
            + "environmental variables.\nSee the below documentation for information "
            + "on how to configure this particular ledge instance.\n\n"
            + environ.generate_help(get_merged_conf_object(), display_defaults=True)
        )
        print(help_str)
        sys.exit(0)

    # Configure Logging
    structlog.configure(
        processors=[
            structlog.processors.StackInfoRenderer(),
            structlog.twisted.EventAdapter(),
        ],
        context_class=dict,
        logger_factory=structlog.twisted.LoggerFactory(),
        wrapper_class=structlog.twisted.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Start logging
    startLogging(sys.stderr)

    # Init ledge
    app = Ledge(config)

    # Configure twisted
    configure_site(app, port=config.port)

    # Configure threadpool if requested
    if config.thread_pool_size is not None:
        reactor.suggestThreadPoolSize(config.thread_pool_size)

    # Start it up!
    reactor.run()
