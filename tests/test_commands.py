from aiohttp import web
from commander.app import create_app


async def test_hello(client):
    data = {
        'csc': 'Test',
        'salindex': 1,
        'cmd': 'cmd_setScalars',
        'params': {
            'a': 1,
            'b': 2
        }
    }
    response = await client.post('/', json=data)
    # response = await client.get('/')
    assert response.status == 200
    response_data = await response.json()
    assert response_data == data
