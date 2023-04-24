from datetime import datetime
from love.commander.app import create_app


async def test_successful_heartbeat(aiohttp_client):
    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    # build data
    # Act
    response = await client.get("/heartbeat")
    timestamp = datetime.now()
    # Assert status
    assert response.status == 200

    # Assert content
    response_data = await response.json()
    assert (
        datetime.fromtimestamp(response_data["timestamp"]) - timestamp
    ).total_seconds() < 3
