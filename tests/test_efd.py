import json
import asyncio
from aiohttp import web
from unittest.mock import patch
from itertools import chain, combinations
from lsst.ts import salobj
from commander.app import create_app
from utils import NumpyEncoder
from tests import conftest
import pytest
import pandas as pd
from unittest.mock import patch, call, MagicMock

# Patch for using MagicMock in async environments
async def async_magic():
    pass
MagicMock.__await__ = lambda x: async_magic().__await__()

class MockEFDClient(object):
    async def select_time_series(cls, topic_name, fields, start, end, is_window=False, index=None):
        f = asyncio.Future()
        data = {}
        for field in fields:
            data[field] = {
                "1583531381471":0.21,
                "1583531381692":0.21,
                "1583531381900":0.21,
                "1583531382109":0.21,
                "1583531382316":0.21
            }

        df = pd.DataFrame.from_dict(data)
        f.set_result(df)
        return f

async def test_efd_timeseries(client):
    """ Test the get timeseries response."""
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")

    # Start patching `efd_client`.
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()

    cscs = {
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
    assert response_data["ATDome-0-topic1"]["field1"][0]["ts"] == "1583531381471"
    assert response_data["ATDome-0-topic1"]["field1"][0]["value"] == 0.21

    # Stop patching `efd_client`.
    mock_efd_patcher.stop()


