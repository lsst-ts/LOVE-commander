import pytest
from commander.app import create_app

pytest_plugins = 'aiohttp.pytest_plugin'

@pytest.fixture
def client(loop, aiohttp_client):
    app = create_app()
    return loop.run_until_complete(aiohttp_client(app))
