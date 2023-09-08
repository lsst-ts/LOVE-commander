# This file is part of LOVE-commander.
#
# Copyright (c) 2023 Inria Chile.
#
# Developed by Inria Chile and Vera C. Rubin Observatory Telescope
# and Site Systems.
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


from datetime import datetime
from love.commander.app import create_app


async def test_successful_heartbeat(aiohttp_client):
    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    # build data
    # Act
    response = await client.get("/heartbeat")
    timestamp = datetime.now()
    # Assert status
    assert response.status == 200

    # Assert content
    response_data = await response.json()
    assert (
        datetime.fromtimestamp(response_data["timestamp"]) - timestamp
    ).total_seconds() < 3
