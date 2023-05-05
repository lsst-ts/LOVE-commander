import re
import asyncio
import types
from unittest.mock import patch, MagicMock
from tempfile import TemporaryFile
from love.commander.app import create_app


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


async def test_lfa_file_exists(aiohttp_client):
    """Test LFA file existence."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    mock_lfa_patcher = patch("lsst.ts.salobj.AsyncS3Bucket")
    mock_lfa_client = mock_lfa_patcher.start()
    mock_lfa_client.return_value = MockAsyncS3Bucket()

    response = await client.post("/lfa/file-exists", json={"file_key": "test-key"})

    assert response.status == 200
    response_data = await response.json()
    assert "exists" in response_data
    assert response_data["exists"] is True


async def test_lfa_upload_file(aiohttp_client):
    """Test LFA file upload."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    mock_lfa_patcher = patch("lsst.ts.salobj.AsyncS3Bucket")
    mock_lfa_client = mock_lfa_patcher.start()
    mock_lfa_client.return_value = MockAsyncS3Bucket()

    with TemporaryFile() as f:
        response = await client.post("/lfa/upload-file", data={"uploaded_file": f})

    assert response.status == 200
    response_data = await response.json()
    assert "ack" in response_data
    assert "url" in response_data
    match_url = re.search(
        r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*",
        response_data["url"],
    )
    assert match_url

    mock_lfa_patcher.stop()


async def test_lfa_upload_erros(aiohttp_client):
    """Test errors on uploading a file."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    mock_lfa_patcher = patch("lsst.ts.salobj.AsyncS3Bucket")
    mock_lfa_client = mock_lfa_patcher.start()
    mock_lfa_client.return_value = MockAsyncS3Bucket()

    # Wrong parameter
    with TemporaryFile() as f:
        response = await client.post("/lfa/upload-file", data={"uploaded_fileS": f})
        assert response.status == 400
        response_data = await response.json()
        assert "ack" in response_data

    # Wrong file format
    response = await client.post("/lfa/upload-file", data={"uploaded_file": None})
    assert response.status == 400

    mock_lfa_patcher.stop()


async def test_lfa_wrong_option(aiohttp_client):
    """Test wrong option."""

    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    response = await client.post("/lfa/upload-fileS", data={"uploaded_file": None})
    assert response.status == 404
