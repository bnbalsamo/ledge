Ledge Plugin Interface
======================

Your plugin should inherit from one of the below classes,
and override the following functionality.

.. note::

   The :ref:`demo_handler` and :ref:`demo_responder` represent
   minimal implementations of the interfaces described below.

.. autoclass:: ledge.HandlerImplementation

   .. autoattribute:: name

   .. autoattribute:: subconfig

   .. automethod:: handles

   .. automethod:: handle

.. autoclass:: ledge.ResponderImplementation

   .. autoattribute:: name

   .. autoattribute:: subconfig

   .. automethod:: handles

   .. automethod:: respond
