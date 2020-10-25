Welcome to ledge's documentation!
=================================

Ledge is a pluggable webhook catcher that handles the complexities of
async Python for you.

It utilizes
`Twisted <https://twistedmatrix.com/>`_,
`environ-config <https://github.com/hynek/environ-config>`_,
and a variety of other packages in order to allow you to easily write
Python code to catch and handle webhooks.

Ledge uses environmental variables for configuration, including specifying
which handlers and responders you want to run on your server, and allows
you to specify anything you can import as a handler or responder. This allows
you to use handlers or responders you've installed via pip, or :code:`.py` files
in your current working directory.

Ledge handlers and responders are subclasses of :class:`ledge.HandlerImplementation`
or :class:`ledge.ResponderImplementation` that minimally override a handful of
functions and attributes.

Take a look at the :ref:`demo_handler` and the :ref:`demo_responder` to see just
how easy it is to write your own webhook handling Python!


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   starting_ledge
   configuration
   plugin_interface
   helpers
   demo_handler
   demo_responder


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
