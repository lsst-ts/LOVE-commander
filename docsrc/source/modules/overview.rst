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


Overview
===============

The LOVE-commander is a backend application that acts as middleware between the LOVE-manager and SAL.

It is built as a Python module that provides and HTTP API to accept command requests and run them using :code:`salobj`, as well as provide some SAL information, such as metadata, topics names, and basic querying for EFD timeseries.
Commands are run during the HTTP request, and their acknowledgement (or failure) is returned as the HTTP response.

.. image:: ../assets/Commander-details.svg