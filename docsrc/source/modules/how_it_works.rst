How it works
===============

.. image:: ../assets/Commander-details.svg
The LOVE-Commander is built as an :code:`aiohttp` application composed by 3 different subapplications:


Commands
---------
Provides the HTTP endpoint to accept and run commands.
It creates a :code:`salobj.Remote` object for the given :code:`CSC` and :code:`salindex`, and runs the given :code:`cmd` with its given :code:`params`.
The command acknowledgement (or failure) is returned as the HTTP response.

SAL Info
-------------
Provides the HTTP endpoints to request data from SAL, such as metadata, names of topics (telemetries, events and commands) and topics data, such as parameters and fields.

Heartbeats
----------------
Provides an HTTP endpoint to accept requests for its own heartbeat. This is used by the :code:`LOVE-Manager` to make sure the :code:`LOVE-Commander` is "alive" and accepting requests.

EFD
----------------
Provides an HTTP endpoint to query an instance of the EFD and return timeseries for any CSCs and topics available

