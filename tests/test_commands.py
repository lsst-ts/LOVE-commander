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

from lsst.ts import salobj

from commander_utils import NumpyEncoder


async def test_successful_command(http_client):
    # Arrange
    # setup dds / csc
    salobj.set_random_lsst_dds_partition_prefix()
    csc = salobj.TestCsc(index=1, config_dir=None, initial_state=salobj.State.ENABLED)
    await csc.start_task

    # build data
    cmd_data = csc.make_random_scalars_dict()
    data = json.loads(
        json.dumps(
            {
                "csc": "Test",
                "salindex": 1,
                "cmd": "cmd_setScalars",
                "params": cmd_data,
                "identity": "test@localhost",
            },
            cls=NumpyEncoder,
        )
    )

    # Act
    response = await http_client.post("/cmd", json=data)

    # Assert status
    assert response.status == 200

    # Assert content
    response_data = await response.json()
    assert response_data == {"ack": "Done"}

    await csc.close()


async def test_wrong_data(http_client):
    # Arrange
    data = {"wrong": "data"}

    # Act
    response = await http_client.post("/cmd", json=data)

    # Assert status
    assert response.status == 400

    # Assert content
    response = await response.json()
    assert (
        response["ack"]
        == "Request must have JSON data with the following keys: csc, salindex, cmd_name, params, identity."
        + f" Received {json.dumps(data)}"
    )


async def test_timeout(http_client):
    # Arrange
    # setup dds / csc
    salobj.set_random_lsst_dds_partition_prefix()
    csc = salobj.TestCsc(index=1, config_dir=None, initial_state=salobj.State.ENABLED)
    await csc.start_task

    # build data
    csc.make_random_scalars_dict()
    data = json.loads(
        json.dumps(
            {
                "csc": "Test",
                "salindex": 1,
                "cmd": "cmd_wait",
                "params": {
                    "duration": -11,
                    "ack": salobj.SalRetCode.CMD_COMPLETE.value,
                },
                "identity": "test@localhost",
            },
            cls=NumpyEncoder,
        )
    )

    # Act
    response = await http_client.post("/cmd", json=data)

    # Assert status
    await response.json()
    assert response.status == 504
    await csc.close()
