from aiohttp import web
from lsst.ts import salobj
import json


def create_app():
    remotes = {}

    cmd = web.Application()

    async def start_cmd(request):
        data = await request.json()
        try:
            assert 'csc' in data
            assert 'salindex' in data
            assert 'cmd' in data
            assert 'params' in data
        except AssertionError:
            return web.json_response({"ack": f'Request must have JSON data with the following keys: csc, salindex, cmd_name, params. Received {json.dumps(data)}'}, status=400)

        csc = data["csc"]
        salindex = data["salindex"]
        cmd_name = data["cmd"]
        params = data["params"]
        remote_name = f"{csc}.{salindex}"
        if remote_name not in remotes:
            remotes[remote_name] = salobj.Remote(
                salobj.Domain(), csc, salindex)
            await remotes[remote_name].start_task

        cmd = getattr(remotes[remote_name], cmd_name)
        cmd.set(**params)

        try:
            cmd_result = await cmd.start(timeout=10)
            return web.json_response({'ack': cmd_result.result})
        except salobj.AckTimeoutError:
            return web.json_response({"ack": "Command time out"}, status=504)

    cmd.router.add_post('/', start_cmd)

    async def on_cleanup(cmd):
        for remote_name in remotes:
            await remotes[remote_name].close()
    cmd.on_cleanup.append(on_cleanup)

    return cmd
