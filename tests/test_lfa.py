# This file is part of LOVE-commander.
#
# Copyright (c) 2023 Inria Chile.
#
# Developed by Inria Chile.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or at
# your option any later version.
#
# This program is distributed in the hope that it will be useful,but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.


import asyncio
import re
import types
from tempfile import TemporaryFile
from unittest.mock import MagicMock, patch


# Patch for using MagicMock in async environments
async def async_magic():
    pass


MagicMock.__await__ = lambda x: async_magic().__await__()


class MockAsyncS3Bucket:
    service_resource = types.SimpleNamespace(
        meta=types.SimpleNamespace(
            client=types.SimpleNamespace(
                meta=types.SimpleNamespace(endpoint_url="http://localhost.test")
            )
        )
    )
    name = "rubinobs-lfa"

    def make_bucket_name(self, s3_instance):
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


async def test_lfa_file_exists(http_client):
    """Test LFA file existence."""
    # Arrange
    mock_lfa_patcher = patch("lsst.ts.salobj.AsyncS3Bucket")
    mock_lfa_client = mock_lfa_patcher.start()
    mock_lfa_client.return_value = MockAsyncS3Bucket()

    # Act
    response = await http_client.post("/lfa/file-exists", json={"file_key": "test-key"})
    assert response.status == 200
    response_data = await response.json()
    assert "exists" in response_data
    assert response_data["exists"] is True

    # Stop lfa patch
    mock_lfa_patcher.stop()


async def test_lfa_upload_file(http_client):
    """Test LFA file upload."""
    # Arrange
    mock_lfa_patcher = patch("lsst.ts.salobj.AsyncS3Bucket")
    mock_lfa_client = mock_lfa_patcher.start()
    mock_lfa_client.return_value = MockAsyncS3Bucket()

    # Act
    with TemporaryFile() as f:
        response = await http_client.post("/lfa/upload-file", data={"uploaded_file": f})

        assert response.status == 200
        response_data = await response.json()
        assert "ack" in response_data
        assert "url" in response_data
        match_url = re.search(
            r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*",
            response_data["url"],
        )
        assert match_url

    # Stop lfa patch
    mock_lfa_patcher.stop()


async def test_lfa_upload_erros(http_client):
    """Test errors on uploading a file."""
    # Arrange
    mock_lfa_patcher = patch("lsst.ts.salobj.AsyncS3Bucket")
    mock_lfa_client = mock_lfa_patcher.start()
    mock_lfa_client.return_value = MockAsyncS3Bucket()

    # Act
    # Wrong parameter
    with TemporaryFile() as f:
        response = await http_client.post(
            "/lfa/upload-file", data={"uploaded_fileS": f}
        )
        assert response.status == 400
        response_data = await response.json()
        assert "ack" in response_data

    # Wrong file format
    response = await http_client.post("/lfa/upload-file", data={"uploaded_file": None})
    assert response.status == 400

    # Stop lfa patch
    mock_lfa_patcher.stop()


async def test_lfa_wrong_option(http_client):
    """Test wrong option."""
    # Act
    response = await http_client.post("/lfa/upload-fileS", data={"uploaded_file": None})
    assert response.status == 404
