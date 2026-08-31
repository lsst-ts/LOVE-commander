# This file is part of LOVE-commander.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import asyncio
import os
import types
from unittest.mock import patch

import pytest
from love.commander.app import create_app

from .test_utils import LSST_SITE, REMOTES_LEN_LIMIT

pytest_plugins = "aiohttp.pytest_plugin"

os.environ["LSST_SITE"] = LSST_SITE
os.environ["LSST_TOPIC_SUBNAME"] = "test"
os.environ["S3_INSTANCE"] = "test"


class MockAsyncS3Bucket:
    service_resource = types.SimpleNamespace(
        meta=types.SimpleNamespace(
            client=types.SimpleNamespace(
                meta=types.SimpleNamespace(endpoint_url="http://localhost.test")
            )
        )
    )
    name = "rubinobs-lfa"

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def make_bucket_name(s3instance):
        return "rubinobs-lfa"

    def make_key(self, salname, salindexname, generator, date, suffix):
        return "test-key"

    async def exists(self, key):
        f = asyncio.Future()
        f.set_result(True)
        return True

    async def upload(self, fileobj, key):
        f = asyncio.Future()
        data = {}
        f.set_result(data)
        return f


@pytest.fixture
def mock_async_s3_bucket():
    with patch("lsst.ts.salobj.AsyncS3Bucket", new=MockAsyncS3Bucket):
        yield


@pytest.fixture
def http_client(loop, aiohttp_client, mock_async_s3_bucket):
    app = create_app(remotes_len_limit=REMOTES_LEN_LIMIT)
    return loop.run_until_complete(aiohttp_client(app))
