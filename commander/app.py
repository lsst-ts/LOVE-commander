from aiohttp import web
from lsst.ts import salobj


def create_app():
    remotes = {}

    app = web.Application()

    routes = web.RouteTableDef()
    @routes.post('/cmd')
    async def start_cmd(request):
        data = await request.json()
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
        cmd_result = await cmd.start(timeout=10)

        return web.json_response({'ack': cmd_result.result})

    app.add_routes(routes)

    async def on_cleanup(app):
        for remote_name in remotes:
            await remotes[remote_name].close()
    app.on_cleanup.append(on_cleanup)
    return app
