import json
from lsst.ts import salobj
from lsst.ts.utils import index_generator
from commander_utils import NumpyEncoder
from commander.app import create_app

index_gen = index_generator()


async def test_successful_command(aiohttp_client):
    # Arrange
    client = await aiohttp_client(create_app())

    # setup dds / csc
    salobj.set_random_lsst_dds_partition_prefix()
    next(index_gen)
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
            },
            cls=NumpyEncoder,
        )
    )

    # Act
    response = await client.post("/cmd", json=data)

    # Assert status
    assert response.status == 200

    # Assert content
    response_data = await response.json()
    assert response_data == {"ack": "Done"}

    await csc.close()


async def test_wrong_data(aiohttp_client):
    # Arrange
    client = await aiohttp_client(create_app())

    data = {"wrong": "data"}

    # Act
    response = await client.post("/cmd", json=data)

    # Assert status
    assert response.status == 400

    # Assert content
    response = await response.json()
    assert (
        response["ack"]
        == "Request must have JSON data with the following keys: csc, salindex, cmd_name, params."
        + f" Received {json.dumps(data)}"
    )


async def test_timeout(aiohttp_client):
    # Arrange
    client = await aiohttp_client(create_app())

    # setup dds / csc
    salobj.set_random_lsst_dds_partition_prefix()
    next(index_gen)
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
            },
            cls=NumpyEncoder,
        )
    )

    # Act
    response = await client.post("/cmd", json=data)

    # Assert status
    await response.json()

    assert response.status == 504
    await csc.close()
