import pytest
from commander.app import create_app
REMOTES_LEN_LIMIT = 5
pytest_plugins = 'aiohttp.pytest_plugin'

@pytest.fixture
async def app():
    app = await create_app(remotes_len_limit=REMOTES_LEN_LIMIT)
    return app

@pytest.fixture
def client(loop, aiohttp_client, app):
    return loop.run_until_complete(aiohttp_client(app))
