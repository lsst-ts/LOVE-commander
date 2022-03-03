import asyncio
import pandas as pd
from unittest.mock import patch, MagicMock
from aiohttp.test_utils import TestClient, TestServer

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


async def test_efd_timeseries():
    """Test the get timeseries response."""
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()
    loop = asyncio.get_event_loop()
    app = create_app()
    async with TestClient(TestServer(app), loop=loop) as client:
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
        response = await client.post("/efd/timeseries", json=request_data)
        assert response.status == 200

        response_data = await response.json()
        assert "ATDome-0-topic1" in list(response_data.keys())
        assert "ATMCS-1-topic2" in list(response_data.keys())
        assert len(response_data["ATDome-0-topic1"]) == 1
        assert len(response_data["ATMCS-1-topic2"]) == 2
        # Endpoint truncates seconds due to resample
        assert (
            response_data["ATDome-0-topic1"]["field1"][0]["ts"] == "2020-03-06 21:49:00"
        )
        assert response_data["ATDome-0-topic1"]["field1"][0]["value"] == 0.21

        # Stop patching `efd_client`.
        mock_efd_patcher.stop()


async def test_efd_timeseries_with_errors():
    """Test the get timeseries response with errors."""
    # Start patching `efd_client`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()
    mock_efd_client.side_effect = raise_exception
    loop = asyncio.get_event_loop()
    app = create_app()
    async with TestClient(TestServer(app), loop=loop) as client:
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
        response = await client.post("/efd/timeseries", json=request_data)
        assert response.status == 400

        # Stop patching `efd_client`.
        mock_efd_patcher.stop()
