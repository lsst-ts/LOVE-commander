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


=============
How to use it
=============


Commands
===============================
Endpoint to run commands on SAL

- Url: :code:`<IP>/cmd/`
- HTTP Operation: POST
- Message Payload:

.. code-block:: json

  {
    "cmd": "<Command name, e.g: cmd_acknowledge>",
    "csc": "<Name of the CSC, e.g: Watcher>",
    "salindex": "<SAL Index in numeric format, e.g. 0>",
    "params": {
      "key1": "value1",
      "key2": "value2",
    },
  }

- Expected Response, if command successful:

.. code-block:: json

  {
    "status": 200,
    "data": {
      "ack": "Done",
    }
  }

- Expected Response, if command timed-out:

.. code-block:: json

  {
    "status": 504,
    "data": {
      "ack": "Command time out",
    }
  }

- Expected Response, command failure:

.. code-block:: json

  {
    "status": 200,
    "data": {
      "ack": "<Text with command result/message>",
    }
  }


SAL Info
==========
Endpoints to request data from SAL.

Metadata
----------------------
Requests :code:`SalInfo.metadata`.
The response contains the SAL and XML version of the different CSCs.

- Url: :code:`<IP>/salinfo/metadata/`
- HTTP Operation: GET

- Expected Response:

.. code-block:: json

  {
    "status": 200,
    "data": {
      "<CSC_1>": {
        "sal_version": "<SAL version in format x.x.x>",
        "xml_version": "<XML version in format x.x.x>"
      },
      "<CSC_2>": {
        "sal_version": "<SAL version in format x.x.x>",
        "xml_version": "<XML version in format x.x.x>"
      },
    },
  }

For example:

.. code-block:: json

  {
    "status": 200,
    "data": {
      "Watcher": {
        "sal_version": "4.1.3",
        "xml_version": "1.0.0"
      },
      "MTM1M3": {
        "sal_version": "4.1.3",
        "xml_version": "1.0.0"
      },
      "ATPtg": {
        "sal_version": "4.1.3",
        "xml_version": "1.0.0"
      },
      "ATPneumatics": {
        "sal_version": "4.1.3",
        "xml_version": "1.0.0"
      },
    },
  }


Topic Names
----------------------
Requests :code:`SalInfo.topic_names`.
The response contains the events, telemetries and command names of each CSC.
The URL accepts :code:`<categories>` as query params, which can be any combination of the following strings separated by "-":
:code:`event`, :code:`telemetry` and :code:`command`. If there is no query param, then all topics are selected.

- Url: :code:`<IP>/salinfo/topic-names?categories=<categories>`
- HTTP Operation: GET

- Expected Response:

.. code-block:: json

  {
    "status": 200,
    "data": {
      "<CSC_1>": {
        "event_names": ["<event_name_1>", "<event_name_2>"],
        "telemetry_names": ["<telemetry_name_1>", "<telemetry_name_2>"],
        "command_names": ["<command_name_1>", "<command_name_2>"]
      },
      "<CSC_2>": {
        "event_names": ["<event_name_1>", "<event_name_2>"],
        "telemetry_names": ["<telemetry_name_1>", "<telemetry_name_2>"],
        "command_names": ["<command_name_1>", "<command_name_2>"]
      },
    },
  }

For example:

.. code-block:: json

  {
    "status": 200,
    "data": {
      "Watcher": {
        "event_names": [
            "alarm",
            "appliedSettingsMatchStart",
            "authList",
            "errorCode",
            "heartbeat",
            "logLevel",
            "logMessage",
            "settingVersions",
            "settingsApplied",
            "simulationMode",
            "softwareVersions",
            "summaryState"
        ],
        "telemetry_names": [],
        "command_names": [
            "abort",
            "acknowledge",
            "disable",
            "enable",
            "enterControl",
            "exitControl",
            "mute",
            "setAuthList",
            "setLogLevel",
            "setValue",
            "showAlarms",
            "standby",
            "start",
            "unacknowledge",
            "unmute"
        ]
      },
    },
  }

Topic Data
----------------------
Requests :code:`SalInfo.topic_data`.
The response contains the events, teelemetries and command data of each CSC.
The URL accepts :code:`<categories>` as query params, which can be any combination of the following strings separated by "-":
:code:`event`, :code:`telemetry` and :code:`command`. If there is no query param, then all topics are selected.

- Url: :code:`<IP>/salinfo/topic-data?categories=<categories>`
- HTTP Operation: GET

- Expected Response:

.. code-block:: json

  {
    "status": 200,
    "data": {
      "<CSC_1>": {
        "event_data": {
          "<parameter_1>": {
            "<field_11>": "<value_11>",
            "<field_12>": "<value_12>",
          },
          "<parameter_2>": {
            "<field_21>": "<value_21>",
            "<field_22>": "<value_22>",
          },
        },
        "telemetry_data": {
          "<parameter_1>": {
            "<field_11>": "<value_11>",
            "<field_12>": "<value_12>",
          },
          "<parameter_2>": {
            "<field_21>": "<value_21>",
            "<field_22>": "<value_22>",
          },
        },
        "command_data": {
          "<parameter_1>": {
            "<field_11>": "<value_11>",
            "<field_12>": "<value_12>",
          },
          "<parameter_2>": {
            "<field_21>": "<value_21>",
            "<field_22>": "<value_22>",
          },
        },
      },
    },
  }


Heartbeats
============
Endpoints to request :code:`LOVE-Commander` heartbeats.

- Url: :code:`<IP>/heartbeat/`
- HTTP Operation: GET

- Expected Response:

.. code-block:: json

  {
    "status": 200,
    "timestamp": "<timestamp of the last heartbeat>",
  }


EFD
============
Endpoint to request EFD timeseries.

- Url: :code:`<IP>/efd/timeseries`
- HTTP Operation: POST
- Message Payload:

.. code-block:: json

  {
    "start_date": "2020-03-16T12:00:00",
    "time_window": 15,
    "cscs": {
      "ATDome": {
        0: {
          "topic1": ["field1"]
        },
      },
      "ATMCS": {
        1: {
          "topic2": ["field2", "field3"]
        },
      }
    },
    "resample": "1min",
  }
  

- Expected Response, if command successful:

.. code-block:: json

  {
    "status": 200,
    "data": {
      "ATDome-0-topic1": {
        "field1": [
          { "ts": "2020-03-06 21:49:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:50:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:51:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:52:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:53:41.471000", "value": 0.21 }
        ]
      },
      "ATMCS-1-topic2": {
        "field2": [
          { "ts": "2020-03-06 21:49:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:50:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:51:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:52:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:53:41.471000", "value": 0.21 }
        ],
        "field3": [
          { "ts": "2020-03-06 21:49:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:50:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:51:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:52:41.471000", "value": 0.21 },
          { "ts": "2020-03-06 21:53:41.471000", "value": 0.21 }
        ]
      }
    }
  }

TCS
============
Endpoint to send TCS commands.

- Url: :code:`<IP>/tcs/aux`
- HTTP Operation: POST
- Message Payload:

.. code-block:: json

  {
    "command_name": "point_azel",
    "params": {
      "az": 80,
      "el": 70
    }
  }
  

- Expected Response, if command successful:

.. code-block:: json

  {
    "status": 200,
    "data": "command_result"
  }
