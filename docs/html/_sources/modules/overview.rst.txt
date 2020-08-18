Overview
===============

The LOVE-commander is a backend application that acts as middleware between the LOVE-manager and SAL.

It is built as a Python module that provides and HTTP API to accept command requests and run them using :code:`salobj`, and provide some SAL information, such as metadata, topics names, among others.
Commands are run during the HTTP request, and their acknowledgement (or failure) is returned as the HTTP response.

.. image:: ../assets/Commander-details.svg