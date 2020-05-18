import pytest
from commander.app import create_app
pytest_plugins = 'aiohttp.pytest_plugin'

REMOTES_LEN_LIMIT = 10
@pytest.fixture
async def app():
    app = await create_app(remotes_len_limit=REMOTES_LEN_LIMIT)
    return app

@pytest.fixture
def client(loop, aiohttp_client, app):
    return loop.run_until_complete(aiohttp_client(app))
