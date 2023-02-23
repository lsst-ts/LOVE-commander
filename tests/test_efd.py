import asyncio
import pandas as pd
import random
from unittest.mock import patch, MagicMock
from commander.efd import MAX_EFD_LOGS_LEN
from commander.app import create_app


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
        if not is_window:
            for field in fields:
                data[field] = {}
                for i in range(int(MAX_EFD_LOGS_LEN)):
                    data[field][pd.Timestamp(i)] = random.randint(1, 10000)
        else:
            for field in fields:
                data[field] = {
                    pd.Timestamp("2020-03-06 21:49:41"): 0.21,
                    pd.Timestamp("2020-03-06 21:50:41"): 0.21,
                    pd.Timestamp("2020-03-06 21:51:41"): 0.21,
                    pd.Timestamp("2020-03-06 21:52:41"): 0.21,
                    pd.Timestamp("2020-03-06 21:53:41"): 0.21,
                }

        df = pd.DataFrame.from_dict(data)
        f.set_result(df)
        return df


# For EFD client's timeouts
def raise_exception(name):
    print(name)
    raise ConnectionError


async def test_efd_timeseries(aiohttp_client):
    """Test the get timeseries response."""
    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

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
    response = await client.post("/efd/timeseries/", json=request_data)
    assert response.status == 200

    response_data = await response.json()
    assert "ATDome-0-topic1" in list(response_data.keys())
    assert "ATMCS-1-topic2" in list(response_data.keys())
    assert len(response_data["ATDome-0-topic1"]) == 1
    assert len(response_data["ATMCS-1-topic2"]) == 2
    # Endpoint truncates seconds due to resample
    assert response_data["ATDome-0-topic1"]["field1"][0]["ts"] == "2020-03-06 21:49:00"
    assert response_data["ATDome-0-topic1"]["field1"][0]["value"] == 0.21

    # Stop patching `efd_client`.
    mock_efd_patcher.stop()


async def test_efd_timeseries_with_errors(aiohttp_client):
    """Test the get timeseries response with errors."""
    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

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
        "start_date": "2020-03-16T12:00:00",
        "time_window": 15,
        "cscs": cscs,
        "resample": "1min",
    }
    response = await client.post("/efd/timeseries/", json=request_data)
    assert response.status == 400

    response_data = await response.json()
    print(response_data)

    # Stop patching `efd_client`.
    mock_efd_patcher.stop()


async def test_efd_logmessages(aiohttp_client):
    """Test the get timeseries response."""
    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

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
    }
    response = await client.post("/efd/logmessages/", json=request_data)
    assert response.status == 200

    response_data = await response.json()

    # CSC topics test
    assert "ATDome-0-logevent_logMessage" in list(response_data.keys())
    assert "ATDome-0-logevent_errorCode" in list(response_data.keys())
    assert "ATMCS-0-logevent_logMessage" in list(response_data.keys())
    assert "ATMCS-0-logevent_errorCode" in list(response_data.keys())

    # Response size test
    flattened_results = [
        item for topic in response_data for item in response_data[topic]
    ]
    assert len(flattened_results) <= MAX_EFD_LOGS_LEN

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

    # Stop patching `efd_client`.
    mock_efd_patcher.stop()


async def test_efd_clients(aiohttp_client):
    """Test query_efd_clients method"""
    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

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

    response = await client.get("/efd/efd_clients/")
    assert response.status == 200

    response_data = await response.json()
    print(response_data)

    assert "instances" in response_data
    instances = response_data["instances"]
    assert all(i in instances for i in dummy_efd_instances)

    # Stop patching `efd_client`.
    mock_efd_patcher.stop()
