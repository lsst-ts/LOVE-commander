from aiohttp import web
from commander.app import create_app

async def test_hello(client):
    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello, world' in text