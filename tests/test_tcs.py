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

class MockTCSClient(object):
    async def atcs_command(self, param1, param2, param3):
        return {
            "value1": param1,
            "value2": param2,
            "value3": param3
        }

# Start patching `tcs_client`.
mock_tcs_patcher = patch("lsst.ts.observatory.control.auxtel.ATCS")
mock_tcs_client = mock_tcs_patcher.start()
mock_tcs_client.return_value = MockTCSClient()


async def test_atcs_command(client):
    """ Test an ATCS command response."""

    request_data = {
        "command_name": "atcs_command",
        "params": {
            "param1": "value1",
            "param2": 2,
            "param3": True,
        }
    }
    response = await client.post("/tcs/aux", json=request_data)
    assert response.status == 200

    response_data = await response.json()
    result = response_data["ack"]
    assert result["value1"] == "value1"
    assert result["value2"] == 2
    assert result["value3"] == True

    # Stop patching `tcs_client`.
    mock_tcs_patcher.stop()


