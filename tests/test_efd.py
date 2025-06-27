# This file is part of LOVE-commander.
#
# Copyright (c) 2023 Inria Chile.
#
# Developed by Inria Chile.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or at
# your option any later version.
#
# This program is distributed in the hope that it will be useful,but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.


import asyncio
import time
from unittest.mock import MagicMock, patch

import pandas as pd


# Patch for using MagicMock in async environments
async def async_magic():
    pass


MagicMock.__await__ = lambda x: async_magic().__await__()


class MockEFDClient(object):
    async def select_time_series(
        self, topic_name, fields, start, end, is_window=False, index=None
    ):
        f = asyncio.Future()
        data = {}
        for field in fields:
            # For log messages we use the private_rcvStamp field.
            # Data will be then sorted by this field
            # so we must mock sequential values for it.
            if field == "private_rcvStamp":
                data[field] = {
                    pd.Timestamp("2020-03-06 21:49:41"): time.time(),
                    pd.Timestamp("2020-03-06 21:50:41"): time.time(),
                    pd.Timestamp("2020-03-06 21:51:41"): time.time(),
                    pd.Timestamp("2020-03-06 21:52:41"): time.time(),
                    pd.Timestamp("2020-03-06 21:53:41"): time.time(),
                    pd.Timestamp("2020-03-06 21:54:41"): time.time(),
                    pd.Timestamp("2020-03-06 21:55:41"): time.time(),
                    pd.Timestamp("2020-03-06 21:56:41"): time.time(),
                }
            else:
                data[field] = {
                    pd.Timestamp("2020-03-06 21:49:41"): 0.21,
                    pd.Timestamp("2020-03-06 21:50:41"): 0.21,
                    pd.Timestamp("2020-03-06 21:51:41"): 0.21,
                    pd.Timestamp("2020-03-06 21:52:41"): float("nan"),
                    pd.Timestamp("2020-03-06 21:53:41"): float("nan"),
                    pd.Timestamp("2020-03-06 21:54:41"): float("nan"),
                    pd.Timestamp("2020-03-06 21:55:41"): 0.21,
                    pd.Timestamp("2020-03-06 21:56:41"): 0.21,
                }

        df = pd.DataFrame.from_dict(data)
        f.set_result(df)
        return df

    async def select_top_n(
        self,
        topic_name,
        fields,
        num,
        time_cut=None,
        index=None,
        convert_influx_index=False,
        use_old_csc_indexing=False,
    ):
        data = {}
        for field in fields:
            if field == "private_rcvStamp":
                data[field] = {
                    pd.Timestamp(f"2020-03-06 21:49:4{i}"): time.time()
                    for i in range(num)
                }
            else:
                data[field] = {
                    pd.Timestamp(f"2020-03-06 21:49:4{i}"): 0.21 for i in range(num)
                }

        df = pd.DataFrame.from_dict(data)
        return df


# For EFD client's timeouts
def raise_exception(name):
    print(name)
    raise ConnectionError


async def test_efd_timeseries(http_client):
    """Test the get timeseries response."""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()

    cscs = {
        "ATDome": {
            0: {"topic1": ["field1"]},
        },
        "ATMCS": {
            1: {"topic2": ["field2", "field3"]},
        },
    }
    request_data = {
        "efd_instance": "summit_efd",
        "start_date": "2020-03-16T12:00:00",
        "time_window": 15,
        "cscs": cscs,
        "resample": "1min",
    }

    # Act
    response = await http_client.post("/efd/timeseries/", json=request_data)
    assert response.status == 200
    response_data = await response.json()
    assert "ATDome-0-topic1" in list(response_data.keys())
    assert "ATMCS-1-topic2" in list(response_data.keys())
    assert len(response_data["ATDome-0-topic1"]) == 1
    assert len(response_data["ATMCS-1-topic2"]) == 2
    # Endpoint truncates seconds due to resample
    assert response_data["ATDome-0-topic1"]["field1"][0]["ts"] == "2020-03-06 21:49:00"
    assert response_data["ATDome-0-topic1"]["field1"][0]["value"] == 0.21
    assert response_data["ATMCS-1-topic2"]["field2"][0]["ts"] == "2020-03-06 21:49:00"
    assert response_data["ATMCS-1-topic2"]["field2"][0]["value"] == 0.21
    assert response_data["ATMCS-1-topic2"]["field3"][0]["ts"] == "2020-03-06 21:49:00"
    assert response_data["ATMCS-1-topic2"]["field3"][0]["value"] == 0.21

    # Check nan values are handled correctly
    assert response_data["ATDome-0-topic1"]["field1"][3]["ts"] == "2020-03-06 21:52:00"
    assert response_data["ATDome-0-topic1"]["field1"][3]["value"] is None
    assert response_data["ATMCS-1-topic2"]["field2"][3]["ts"] == "2020-03-06 21:52:00"
    assert response_data["ATMCS-1-topic2"]["field2"][3]["value"] is None
    assert response_data["ATMCS-1-topic2"]["field3"][3]["ts"] == "2020-03-06 21:52:00"
    assert response_data["ATMCS-1-topic2"]["field3"][3]["value"] is None

    # Stop `efd_client` patch
    mock_efd_patcher.stop()


async def test_efd_timeseries_with_efd_client_errors(http_client):
    """Test the get timeseries response with efd client errors."""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()
    mock_efd_client.side_effect = raise_exception

    cscs = {
        "ATDome": {
            0: {"topic1": ["field1"]},
        },
        "ATMCS": {
            1: {"topic2": ["field2", "field3"]},
        },
    }
    request_data = {
        "efd_instance": "summit_efd",
        "start_date": "2020-03-16T12:00:00",
        "time_window": 15,
        "cscs": cscs,
        "resample": "1min",
    }

    # Act
    response = await http_client.post("/efd/timeseries/", json=request_data)
    assert response.status == 400
    assert await response.json() == {"ack": "EFD Client could not stablish connection"}

    # Stop `efd_client` patch
    mock_efd_patcher.stop()


async def test_efd_timeseries_with_missing_params(http_client):
    """Test the get timeseries response with missing parameters."""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()

    request_data = {
        "efd_instance": "summit_efd",
        "start_date": "2020-03-16T12:00:00",
        "time_window": 15,
        "csc": {
            "ATDome": {
                0: {"topic1": ["field1"]},
            },
            "ATMCS": {
                1: {"topic2": ["field2", "field3"]},
            },
        },
        "resample": "1min",
    }

    # Act
    for key in request_data:
        # Remove one key at a time to test missing parameters
        request_data_copy = request_data.copy()
        del request_data_copy[key]

        # Act
        response = await http_client.post("/efd/timeseries/", json=request_data_copy)
        assert response.status == 400
        assert await response.json() == {
            "ack": "Some of the required parameters is not present"
        }

    # Stop `efd_client` patch
    mock_efd_patcher.stop()


async def test_efd_most_recent_timeseries(http_client):
    """Test the get most recent timeseries response."""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()

    cscs = {
        "ATDome": {
            0: {"topic1": ["field1"]},
        },
        "ATMCS": {
            1: {"topic2": ["field2", "field3"]},
        },
    }
    request_data = {
        "efd_instance": "summit_efd",
        "num": 5,
        "cscs": cscs,
    }

    # Act
    response = await http_client.post("/efd/top_timeseries/", json=request_data)
    assert response.status == 200

    response_data = await response.json()
    assert "ATDome-0-topic1" in list(response_data.keys())
    assert "ATMCS-1-topic2" in list(response_data.keys())
    assert len(response_data["ATDome-0-topic1"]) == 1
    assert len(response_data["ATMCS-1-topic2"]) == 2
    assert len(response_data["ATDome-0-topic1"]["field1"]) == 5
    assert len(response_data["ATMCS-1-topic2"]["field2"]) == 5
    assert len(response_data["ATMCS-1-topic2"]["field3"]) == 5

    # Stop `efd_client` patch
    mock_efd_patcher.stop()


async def test_efd_most_recent_timeseries_with_efd_client_errors(http_client):
    """Test the get most recent timeseries response with efd client errors."""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()
    mock_efd_client.side_effect = raise_exception

    cscs = {
        "ATDome": {
            0: {"topic1": ["field1"]},
        },
        "ATMCS": {
            1: {"topic2": ["field2", "field3"]},
        },
    }
    request_data = {
        "efd_instance": "summit_efd",
        "num": 5,
        "cscs": cscs,
    }

    # Act
    response = await http_client.post("/efd/top_timeseries/", json=request_data)
    assert response.status == 400
    assert await response.json() == {"ack": "EFD Client could not stablish connection"}

    # Stop `efd_client` patch
    mock_efd_patcher.stop()


async def test_efd_most_recent_timeseries_with_missing_params(http_client):
    """Test the get most recent timeseries response with missing parameters."""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()

    request_data = {
        "efd_instance": "summit_efd",
        "cscs": {
            "ATDome": {
                0: {"topic1": ["field1"]},
            },
            "ATMCS": {
                1: {"topic2": ["field2", "field3"]},
            },
        },
    }

    # Act
    for key in request_data:
        # Remove one key at a time to test missing parameters
        request_data_copy = request_data.copy()
        del request_data_copy[key]

        # Act
        response = await http_client.post(
            "/efd/top_timeseries/", json=request_data_copy
        )
        assert response.status == 400
        assert await response.json() == {
            "ack": "Some of the required parameters is not present"
        }

    # Stop `efd_client` patch
    mock_efd_patcher.stop()


async def test_efd_logmessages(http_client):
    """Test the get logmessages response."""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()

    cscs = {
        "ATDome": {
            0: {
                "logevent_logMessage": [
                    "private_rcvStamp",
                    "level",
                    "message",
                    "traceback",
                ],
                "logevent_errorCode": [
                    "private_rcvStamp",
                    "errorCode",
                    "errorReport",
                    "traceback",
                ],
            },
        },
        "ATMCS": {
            0: {
                "logevent_logMessage": [
                    "private_rcvStamp",
                    "level",
                    "message",
                    "traceback",
                ],
                "logevent_errorCode": [
                    "private_rcvStamp",
                    "errorCode",
                    "errorReport",
                    "traceback",
                ],
            },
        },
    }
    request_data = {
        "efd_instance": "summit_efd",
        "start_date": "2020-03-16T12:00:00",
        "end_date": "2020-03-17T12:00:00",
        "cscs": cscs,
        "scale": "utc",
    }

    # Act
    response = await http_client.post("/efd/logmessages/", json=request_data)
    assert response.status == 200

    response_data = await response.json()

    # CSC topics test
    assert "ATDome-0-logevent_logMessage" in list(response_data.keys())
    assert "ATDome-0-logevent_errorCode" in list(response_data.keys())
    assert "ATMCS-0-logevent_logMessage" in list(response_data.keys())
    assert "ATMCS-0-logevent_errorCode" in list(response_data.keys())

    # Response structure test
    if len(response_data["ATDome-0-logevent_logMessage"]) > 0:
        assert "private_rcvStamp" in response_data["ATDome-0-logevent_logMessage"][0]
        assert "level" in response_data["ATDome-0-logevent_logMessage"][0]
        assert "message" in response_data["ATDome-0-logevent_logMessage"][0]
        assert "traceback" in response_data["ATDome-0-logevent_logMessage"][0]

    if len(response_data["ATDome-0-logevent_errorCode"]) > 0:
        assert "private_rcvStamp" in response_data["ATDome-0-logevent_errorCode"][0]
        assert "errorCode" in response_data["ATDome-0-logevent_errorCode"][0]
        assert "errorReport" in response_data["ATDome-0-logevent_errorCode"][0]
        assert "traceback" in response_data["ATDome-0-logevent_errorCode"][0]

    if len(response_data["ATMCS-0-logevent_logMessage"]) > 0:
        assert "private_rcvStamp" in response_data["ATMCS-0-logevent_logMessage"][0]
        assert "level" in response_data["ATMCS-0-logevent_logMessage"][0]
        assert "message" in response_data["ATMCS-0-logevent_logMessage"][0]
        assert "traceback" in response_data["ATMCS-0-logevent_logMessage"][0]

    if len(response_data["ATMCS-0-logevent_errorCode"]) > 0:
        assert "private_rcvStamp" in response_data["ATMCS-0-logevent_errorCode"][0]
        assert "errorCode" in response_data["ATMCS-0-logevent_errorCode"][0]
        assert "errorReport" in response_data["ATMCS-0-logevent_errorCode"][0]
        assert "traceback" in response_data["ATMCS-0-logevent_errorCode"][0]

    # Make sure the timestamps are sorted in descending order
    for topic in response_data:
        prev_timestamp = time.time()
        for record in response_data[topic]:
            assert record["private_rcvStamp"] < prev_timestamp
            prev_timestamp = record["private_rcvStamp"]

    # Stop `efd_client` patch
    mock_efd_patcher.stop()


async def test_efd_logmessages_with_efd_client_errors(http_client):
    """Test the get logmessages response with efd client errors."""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()
    mock_efd_client.side_effect = raise_exception

    cscs = {
        "ATDome": {
            0: {
                "logevent_logMessage": [
                    "private_rcvStamp",
                    "level",
                    "message",
                    "traceback",
                ],
                "logevent_errorCode": [
                    "private_rcvStamp",
                    "errorCode",
                    "errorReport",
                    "traceback",
                ],
            },
        },
        "ATMCS": {
            0: {
                "logevent_logMessage": [
                    "private_rcvStamp",
                    "level",
                    "message",
                    "traceback",
                ],
                "logevent_errorCode": [
                    "private_rcvStamp",
                    "errorCode",
                    "errorReport",
                    "traceback",
                ],
            },
        },
    }
    request_data = {
        "efd_instance": "summit_efd",
        "start_date": "2020-03-16T12:00:00",
        "end_date": "2020-03-17T12:00:00",
        "cscs": cscs,
        "scale": "utc",
    }

    # Act
    response = await http_client.post("/efd/logmessages/", json=request_data)
    assert response.status == 400
    assert await response.json() == {"ack": "EFD Client could not stablish connection"}

    # Stop `efd_client` patch
    mock_efd_patcher.stop()


async def test_efd_logmessages_with_missing_params(http_client):
    """Test the get logmessages response with missing parameters."""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()

    request_data = {
        "efd_instance": "summit_efd",
        "start_date": "2020-03-16T12:00:00",
        "end_date": "2020-03-17T12:00:00",
        "cscs": {
            "ATDome": {
                0: {
                    "logevent_logMessage": [
                        "private_rcvStamp",
                        "level",
                        "message",
                        "traceback",
                    ],
                    "logevent_errorCode": [
                        "private_rcvStamp",
                        "errorCode",
                        "errorReport",
                        "traceback",
                    ],
                },
            },
            "ATMCS": {
                0: {
                    "logevent_logMessage": [
                        "private_rcvStamp",
                        "level",
                        "message",
                        "traceback",
                    ],
                    "logevent_errorCode": [
                        "private_rcvStamp",
                        "errorCode",
                        "errorReport",
                        "traceback",
                    ],
                },
            },
        },
        "scale": "utc",
    }

    # Act
    for key in request_data:
        # Remove one key at a time to test missing parameters
        request_data_copy = request_data.copy()
        del request_data_copy[key]

        # Act
        response = await http_client.post("/efd/logmessages/", json=request_data_copy)
        assert response.status == 400
        assert await response.json() == {
            "ack": "Some of the required parameters is not present"
        }

    # Stop `efd_client` patch
    mock_efd_patcher.stop()


async def test_efd_clients(http_client):
    """Test query_efd_clients method"""
    # Arrange
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()

    dummy_efd_instances = [
        "instance1",
        "instance2",
        "instance3",
    ]
    mock_efd_client.list_efd_names = MagicMock(return_value=dummy_efd_instances)

    # Act
    response = await http_client.get("/efd/efd_clients/")
    assert response.status == 200
    response_data = await response.json()
    assert "instances" in response_data
    instances = response_data["instances"]
    assert all(i in instances for i in dummy_efd_instances)

    # Stop `efd_client` patch
    mock_efd_patcher.stop()
