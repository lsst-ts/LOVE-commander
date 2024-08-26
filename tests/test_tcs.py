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
from unittest.mock import MagicMock, patch


# Patch for using MagicMock in async environments
async def async_magic():
    pass


MagicMock.__await__ = lambda x: async_magic().__await__()


class MockATCSClient(object):
    start_task = asyncio.sleep(1)

    async def atcs_command(self, param1, param2, param3):
        """Docstring of atcs_command."""
        return {"value1": param1, "value2": param2, "value3": param3}


class MockMTCSClient(object):
    start_task = asyncio.sleep(1)

    async def mtcs_command(self, param1, param2, param3):
        """Docstring of mtcs_command."""
        return {"value1": param1, "value2": param2, "value3": param3}


async def test_atcs_command(http_client):
    """Test an ATCS command response."""
    # Arrange
    mock_tcs_patcher = patch("love.commander.tcs.ATCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockATCSClient()

    request_data = {
        "command_name": "atcs_command",
        "params": {"param1": "value1", "param2": 2, "param3": True},
    }
    response = await http_client.post("/tcs/aux", json=request_data)
    assert response.status == 200

    response_data = await response.json()
    result = response_data["ack"]
    assert "'value1': 'value1'" in result
    assert "'value2': 2" in result
    assert "'value3': True" in result
    mock_tcs_patcher.stop()


async def test_missing_atcs_command(http_client):
    """Test an ATCS command response."""
    # Arrange
    mock_tcs_patcher = patch("love.commander.tcs.ATCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockATCSClient()

    request_data = {
        "command_name": "missing_atcs_command",
        "params": {"param1": "value1", "param2": 2, "param3": True},
    }
    response = await http_client.post("/tcs/aux", json=request_data)
    assert response.status == 400
    mock_tcs_patcher.stop()


async def test_atcs_docstring(http_client):
    """Test an ATCS command response."""
    # Arrange
    mock_tcs_patcher = patch("love.commander.tcs.ATCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockATCSClient()

    response = await http_client.get("/tcs/aux/docstrings")
    response_data = await response.json()
    assert response.status == 200
    assert response_data["atcs_command"] == "Docstring of atcs_command."
    mock_tcs_patcher.stop()


async def test_mtcs_command(http_client):
    """Test an MTCS command response."""
    # Arrange
    mock_tcs_patcher = patch("love.commander.tcs.MTCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockMTCSClient()

    request_data = {
        "command_name": "mtcs_command",
        "params": {"param1": "value1", "param2": 2, "param3": True},
    }
    response = await http_client.post("/tcs/main", json=request_data)
    assert response.status == 200

    response_data = await response.json()
    result = response_data["ack"]
    assert "'value1': 'value1'" in result
    assert "'value2': 2" in result
    assert "'value3': True" in result
    mock_tcs_patcher.stop()


async def test_missing_mtcs_command(http_client):
    """Test an MTCS command response."""
    # Arrange
    mock_tcs_patcher = patch("love.commander.tcs.MTCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockMTCSClient()

    request_data = {
        "command_name": "missing_mtcs_command",
        "params": {"param1": "value1", "param2": 2, "param3": True},
    }
    response = await http_client.post("/tcs/main", json=request_data)
    assert response.status == 400
    mock_tcs_patcher.stop()


async def test_mtcs_docstring(http_client):
    """Test an MTCS command response."""
    # Arrange
    mock_tcs_patcher = patch("love.commander.tcs.MTCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockMTCSClient()

    response = await http_client.get("/tcs/main/docstrings")
    response_data = await response.json()
    assert response.status == 200
    assert response_data["mtcs_command"] == "Docstring of mtcs_command."
    mock_tcs_patcher.stop()
