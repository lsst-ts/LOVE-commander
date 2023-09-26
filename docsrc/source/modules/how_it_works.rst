..
    This file is part of LOVE-commander.
..
    Copyright (c) 2023 Inria Chile.
..
    Developed by Inria Chile.
..
    This program is free software: you can redistribute it and/or modify it under 
    the terms of the GNU General Public License as published by the Free Software 
    Foundation, either version 3 of the License, or at your option any later version.
..
    This program is distributed in the hope that it will be useful,but WITHOUT ANY
    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR 
    A PARTICULAR PURPOSE. See the GNU General Public License for more details.
..
    You should have received a copy of the GNU General Public License along with 
    this program. If not, see <http://www.gnu.org/licenses/>.


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

