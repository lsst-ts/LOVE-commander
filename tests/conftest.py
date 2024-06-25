import os

import pytest
from love.commander.app import create_app

from .test_utils import LSST_SITE, REMOTES_LEN_LIMIT

pytest_plugins = "aiohttp.pytest_plugin"


os.environ["LSST_SITE"] = LSST_SITE


@pytest.fixture
def http_client(loop, aiohttp_client):
    app = create_app(remotes_len_limit=REMOTES_LEN_LIMIT)
    return loop.run_until_complete(aiohttp_client(app))
