import pytest
from commander.app import create_app
import asyncio
pytest_plugins = 'aiohttp.pytest_plugin'

REMOTES_LEN_LIMIT = 10
@pytest.fixture
async def app():
    app = await create_app(remotes_len_limit=REMOTES_LEN_LIMIT)
    return app

@pytest.fixture 
def event_loop(): 
    loop = asyncio.get_event_loop() 
    yield loop 
    loop.close()

@pytest.fixture
def client(event_loop, aiohttp_client, app):
    return event_loop.run_until_complete(aiohttp_client(app))
