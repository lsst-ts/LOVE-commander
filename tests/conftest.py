import pytest
from commander.app import create_app

pytest_plugins = "aiohttp.pytest_plugin"

REMOTES_LEN_LIMIT = 10


@pytest.fixture
def client(loop, test_client):
    return loop.run_until_complete(test_client(create_app))
