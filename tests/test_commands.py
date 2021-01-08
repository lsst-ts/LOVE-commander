from aiohttp import web
from lsst.ts import salobj
from commander.app import create_app
from utils import NumpyEncoder
import json
from unittest.mock import patch

index_gen = salobj.index_generator()


async def test_successful_command(client):
    # Arrange
    # setup dds / csc
    salobj.set_random_lsst_dds_domain()
    index = next(index_gen)
    csc = salobj.TestCsc(index=1, config_dir=None,
                         initial_state=salobj.State.ENABLED)
    await csc.start_task

    # build data
    cmd_data = csc.make_random_cmd_scalars()
    data = json.loads(json.dumps({
        'csc': 'Test',
        'salindex': 1,
        'cmd': 'cmd_setScalars',
        'params': dict(cmd_data.get_vars())
    }, cls=NumpyEncoder))

    # Act
    response = await client.post('/cmd', json=data)

    # Assert status
    assert response.status == 200

    # Assert content
    response_data = await response.json()
    assert response_data == { 'ack': 'Done'}

    await csc.close()

async def test_wrong_data(client):
    # Arrange
    data = {
        'wrong': 'data'
    }

    # Act
    response = await client.post('/cmd', json=data)

    # Assert status
    assert response.status == 400

    # Assert content
    response = await response.json()
    assert response['ack'] == f'Request must have JSON data with the following keys: csc, salindex, cmd_name, params. Received {json.dumps(data)}'


async def test_timeout(client):
    # Arrange
    # setup dds / csc
    salobj.set_random_lsst_dds_domain()
    index = next(index_gen)
    csc = salobj.TestCsc(index=1, config_dir=None,
                         initial_state=salobj.State.ENABLED)
    await csc.start_task

    # build data
    cmd_data = csc.make_random_cmd_scalars()
    data = json.loads(json.dumps({
        'csc': 'Test',
        'salindex': 1,
        'cmd': 'cmd_wait',
        'params': {
            'duration': -11,
            'ack': salobj.SalRetCode.CMD_COMPLETE.value
        }
    }, cls=NumpyEncoder))

    # Act
    response = await client.post('/cmd', json=data)

    # Assert status
    content = await response.json()
    print(content)

    assert response.status == 504
    await csc.close()
