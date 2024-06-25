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


import json

import pytest
from lsst.ts import salobj


@pytest.mark.skip(reason="LOVE CSC is not functional at this moment")
async def test_successful_command(http_client, *args, **kwargs):
    # Arrange
    remote = salobj.Remote(domain=salobj.Domain(), name="LOVE")
    await remote.start_task

    observing_log_msg = {
        "user": "an user",
        "message": "a message",
    }

    # Act
    remote.evt_observingLog.flush()
    response = await http_client.post(
        "/lovecsc/observinglog", data=json.dumps(observing_log_msg)
    )

    # Assert
    assert response.status == 200
    response = await response.json()
    assert response["ack"] == "Added new observing log to SAL"

    result = await remote.evt_observingLog.next(flush=False)
    assert result.user == "an user"
    assert result.message == "a message"

    # Clean up
    await remote.close()


@pytest.mark.skip(reason="LOVE CSC is not functional at this moment")
async def test_wrong_data(http_client, *args, **kwargs):
    # Arrange
    data = {"wrong": "data"}

    # Act
    response = await http_client.post("/lovecsc/observinglog", json=data)

    # Assert
    assert response.status == 400
    response = await response.json()
    assert (
        response["ack"]
        == "Request must have JSON data with the following keys: user, message."
        + f" Received {json.dumps(data)}"
    )
