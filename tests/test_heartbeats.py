from aiohttp import web
from commander.app import create_app
from utils import NumpyEncoder
import json
from datetime import datetime
from unittest.mock import patch


async def test_successful_heartbeat(client):
    # Arrange
    # setup dds / csc

    # build data
    # Act
    response = await client.get('/heartbeat')
    timestamp = datetime.now()
    # Assert status
    assert response.status == 200

    # Assert content
    response_data = await response.json()
    assert (datetime.fromtimestamp(response_data['timestamp']) - timestamp).total_seconds() < 3   