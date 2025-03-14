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

import os
import re

import aiohttp


async def test_lfa_file_exists(http_client):
    """Test LFA file existence."""
    # Act
    response = await http_client.post("/lfa/file-exists", json={"file_key": "test-key"})
    assert response.status == 200
    response_data = await response.json()
    assert "exists" in response_data
    assert response_data["exists"] is True


async def test_lfa_upload_file(http_client):
    """Test LFA file upload."""
    # Arrange
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "data/test_file.txt")

    # Act
    form = aiohttp.FormData()
    form.add_field("uploaded_file", open(file_path, "rb"), filename="test_file.txt")
    response = await http_client.post(
        "/lfa/upload-file",
        data=form,
    )

    assert response.status == 200
    response_data = await response.json()
    assert "ack" in response_data
    assert "url" in response_data
    match_url = re.search(
        r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*",
        response_data["url"],
    )
    assert match_url


async def test_lfa_upload_erros(http_client):
    """Test errors on uploading a file."""
    # Arrange
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "data/test_file.txt")

    # Act
    # Wrong parameter
    form = aiohttp.FormData()
    form.add_field(
        "incorrect_field_name", open(file_path, "rb"), filename="test_file.txt"
    )
    response = await http_client.post(
        "/lfa/upload-file",
        data=form,
    )
    assert response.status == 400
    response_data = await response.json()
    assert "ack" in response_data

    # Wrong file format
    form = aiohttp.FormData()
    form.add_field("uploaded_file", None)
    response = await http_client.post(
        "/lfa/upload-file",
        data=form,
    )
    assert response.status == 400


async def test_lfa_wrong_option(http_client):
    """Test wrong option."""
    # Act
    response = await http_client.post("/lfa/upload-fileS", data={"uploaded_file": None})
    assert response.status == 404
