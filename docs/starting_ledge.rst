Getting Started
===============

Starting the Ledge Server
-------------------------

After installation the ledge server can be started in two ways:

Via a standard CLI command:

.. code-block:: bash

   $ ledge

Or via the :code:`-m` flag to the python interpreter:

.. code-block:: bash

   $ python -m ledge

.. note::

   You will need to use the :code:`python -m ledge` syntax if you
   want the current working directory to be part of Ledge's python path
   (i.e: to use python files in the current directory as handlers or
   responders)

By default ledge will listen on port 8080.
It can be accessed via a browser (or :code:`GET` request)
or via a :code:`POST` request.

(The below code snippets use `the httpie CLI <https://httpie.org/>`_)

On your "client" side you should see something like...

.. code-block:: bash

   $ http localhost:8080
   HTTP/1.1 200 OK
   Content-Length: 32
   Content-Type: text/html
   Date: Mon, 06 Jul 2020 03:43:03 GMT
   Server: TwistedWeb/20.3.0

   <html>Ledge is listening!</html>

   $ http POST localhost:8080
   HTTP/1.1 200 OK
   Content-Type: text/html
   Date: Mon, 06 Jul 2020 03:43:09 GMT
   Server: TwistedWeb/20.3.0
   Transfer-Encoding: chunked

And on the server side you should see logs like...

.. code-block:: bash

   2020-07-05 22:48:07-0500 [-] Log opened.
   2020-07-05 22:48:07-0500 [-] Site starting on 8080
   2020-07-05 22:48:07-0500 [-] Starting factory <twisted.web.server.Site object at 0x7fc7c749b940>
   2020-07-05 22:48:10-0500 [-] "127.0.0.1" - - [06/Jul/2020:03:48:10 +0000] "GET / HTTP/1.1" 200 32 "-" "HTTPie/2.1.0"
   2020-07-05 22:48:13-0500 [_GenericHTTPChannelProtocol,1,127.0.0.1] Content length: 0              client_ip=127.0.0.1 method=POST path=/ request_id=30d136d4a7374877b6c5be61803bd45f
   2020-07-05 22:48:13-0500 [-] No responders detected for request. Using default. client_ip=127.0.0.1 method=POST path=/ request_id=30d136d4a7374877b6c5be61803bd45f
   2020-07-05 22:48:13-0500 [-] "127.0.0.1" - - [06/Jul/2020:03:48:12 +0000] "POST / HTTP/1.1" 200 - "-" "HTTPie/2.1.0"


The ledge server can be stopped by sending the process a :code:`SIGINT` (Ctrl+C)
or :code:`SIGTERM`.

Nothing too exciting yet - let's set up a custom handler and a custom responder
so that we can see them operate.

Using Handlers And Responders
-----------------------------

.. note::
   For more information on how to use environmental variables to configure ledge
   see the :ref:`configuration` section.

Start the ledge server with the following environmental variables set:

.. code-block:: bash

   $ LEDGE_RESPONDERS=ledge.responders.DemoResponder LEDGE_HANDLERS=ledge.handlers.DemoHandler ledge

Make a HTTP :code:`POST` request to the ledge endpoint:

.. code-block:: bash

   $ http POST localhost:8080
   HTTP/1.1 200 OK
   Content-Type: text/html
   Date: Mon, 06 Jul 2020 04:08:56 GMT
   Server: TwistedWeb/20.3.0
   Transfer-Encoding: chunked

   :)

.. note::
   It may be helpful to take a look at the source of the :ref:`demo_responder`
   and :ref:`demo_handler` to get a better idea of whats going on behind the scenes
   after this request is made.

Here we can see our responder in action - it's sent us back a smiley.

If we review the server side logs we can also see that our demo handler
has been called as well.

.. code-block:: bash

   2020-07-05 23:08:54-0500 [-] Log opened.
   2020-07-05 23:08:54-0500 [-] Site starting on 8080
   2020-07-05 23:08:54-0500 [-] Starting factory <twisted.web.server.Site object at 0x7f4eee344cd0>
   2020-07-05 23:08:56-0500 [_GenericHTTPChannelProtocol,0,127.0.0.1] Content length: 0              client_ip=127.0.0.1 method=POST path=/ request_id=a3eca668bdd0400d891c058a0847b027
   2020-07-05 23:08:56-0500 [-] Responder demo_responder handles this request. client_ip=127.0.0.1 method=POST path=/ request_id=a3eca668bdd0400d891c058a0847b027
   2020-07-05 23:08:56-0500 [-] "127.0.0.1" - - [06/Jul/2020:04:08:55 +0000] "POST / HTTP/1.1" 200 2 "-" "HTTPie/2.1.0"
   2020-07-05 23:08:56-0500 [-] Response sent!                 client_ip=127.0.0.1 method=POST path=/ request_id=a3eca668bdd0400d891c058a0847b027
   2020-07-05 23:08:56-0500 [-] Handler demo_handler processing request. client_ip=127.0.0.1 method=POST path=/ request_id=a3eca668bdd0400d891c058a0847b027
   2020-07-05 23:08:56-0500 [-] Handler demo_handler handles this request. client_ip=127.0.0.1 method=POST path=/ request_id=a3eca668bdd0400d891c058a0847b027
   2020-07-05 23:08:56-0500 [-] Demo handler handling request! client_ip=127.0.0.1 method=POST path=/ request_id=a3eca668bdd0400d891c058a0847b027

