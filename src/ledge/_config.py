"""Ledge's config classes and helper functions."""

import importlib
from itertools import chain

import environ


def _cls_from_import_path(module_path):
    """Given the import path to a class return that class."""
    path_split = module_path.split(".")
    module_name = path_split[:-1]
    cls_name = path_split[-1]
    module = importlib.import_module(".".join(module_name))
    return getattr(module, cls_name)


def _classes_from_comma_delimited_import_paths(a_str):
    """Return a list of classes, given a comma delimited str of import paths."""
    if a_str == "":
        return []
    module_names = a_str.split(",")

    # Conditional allows hanging commas in the env var
    return [_cls_from_import_path(name) for name in module_names if name]


def _none_or_int(a_str):
    """
    Allow None, otherwise value must be an int.

    (Optional int value)
    """
    if a_str is None:
        return None
    return int(a_str)


class Configuration:  # pylint: disable=too-few-public-methods
    """Application configuration from environmental variables."""

    max_content_length = environ.var(
        converter=int,
        default=50000,  # 50 Mb
        help="The maximum request content size to accept, in bytes.",
    )
    responders = environ.var(
        converter=_classes_from_comma_delimited_import_paths,
        default="",
        help="The full import paths to classes which implement the responder interface",
    )
    handlers = environ.var(
        converter=_classes_from_comma_delimited_import_paths,
        default="",
        help="The full import paths to classes which implement the handler interface",
    )
    port = environ.var(
        converter=int, default=8080, help="The port for the ledge server to listen on."
    )
    thread_pool_size = environ.var(
        converter=_none_or_int,
        default=None,
        help="The size of the threadpool ledge will use to run handlers. If not "
        "supplied the default from Twisted will be used.",
    )


def get_merged_conf_object():
    """
    Get the merged configuration object.

    Note this returns the value environ.config expects as an argument
    (eg, its attrs will be the return value of environ.var, not the
    configured values).
    """
    # Bootstrap a config we can read the modules for the subconfigs from
    bootstrap_config = environ.to_config(environ.config(Configuration, prefix="LEDGE"))

    # Frankenstein our real config together
    for kls in chain(bootstrap_config.handlers, bootstrap_config.responders):
        if kls.provides_subconfig():
            subconfig_name, subconfig = kls.provide_subconfig()
            setattr(Configuration, subconfig_name, environ.group(subconfig))
    return environ.config(Configuration, prefix="LEDGE", frozen=True)


def get_config():
    """Return a populated configuration object."""
    return environ.to_config(get_merged_conf_object())
