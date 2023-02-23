import asyncio
from unittest.mock import patch, MagicMock
from commander.app import create_app


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


async def test_atcs_command(aiohttp_client):
    """Test an ATCS command response."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    mock_tcs_patcher = patch("commander.tcs.ATCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockATCSClient()

    request_data = {
        "command_name": "atcs_command",
        "params": {"param1": "value1", "param2": 2, "param3": True},
    }
    response = await client.post("/tcs/aux", json=request_data)
    assert response.status == 200

    response_data = await response.json()
    result = response_data["ack"]
    assert "'value1': 'value1'" in result
    assert "'value2': 2" in result
    assert "'value3': True" in result
    mock_tcs_patcher.stop()


async def test_missing_atcs_command(aiohttp_client):
    """Test an ATCS command response."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    mock_tcs_patcher = patch("commander.tcs.ATCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockATCSClient()

    request_data = {
        "command_name": "missing_atcs_command",
        "params": {"param1": "value1", "param2": 2, "param3": True},
    }
    response = await client.post("/tcs/aux", json=request_data)
    assert response.status == 400
    mock_tcs_patcher.stop()


async def test_atcs_docstring(aiohttp_client):
    """Test an ATCS command response."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    mock_tcs_patcher = patch("commander.tcs.ATCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockATCSClient()

    response = await client.get("/tcs/aux/docstrings")
    response_data = await response.json()
    assert response.status == 200
    assert response_data["atcs_command"] == "Docstring of atcs_command."
    mock_tcs_patcher.stop()


async def test_mtcs_command(aiohttp_client):
    """Test an MTCS command response."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    mock_tcs_patcher = patch("commander.tcs.MTCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockMTCSClient()

    request_data = {
        "command_name": "mtcs_command",
        "params": {"param1": "value1", "param2": 2, "param3": True},
    }
    response = await client.post("/tcs/main", json=request_data)
    assert response.status == 200

    response_data = await response.json()
    result = response_data["ack"]
    assert "'value1': 'value1'" in result
    assert "'value2': 2" in result
    assert "'value3': True" in result
    mock_tcs_patcher.stop()


async def test_missing_mtcs_command(aiohttp_client):
    """Test an MTCS command response."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    mock_tcs_patcher = patch("commander.tcs.MTCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockMTCSClient()

    request_data = {
        "command_name": "missing_mtcs_command",
        "params": {"param1": "value1", "param2": 2, "param3": True},
    }
    response = await client.post("/tcs/main", json=request_data)
    assert response.status == 400
    mock_tcs_patcher.stop()


async def test_mtcs_docstring(aiohttp_client):
    """Test an MTCS command response."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    mock_tcs_patcher = patch("commander.tcs.MTCS")
    mock_tcs_client = mock_tcs_patcher.start()
    mock_tcs_client.return_value = MockMTCSClient()

    response = await client.get("/tcs/main/docstrings")
    response_data = await response.json()
    assert response.status == 200
    assert response_data["mtcs_command"] == "Docstring of mtcs_command."
    mock_tcs_patcher.stop()
