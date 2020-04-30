import json
from aiohttp import web
from lsst.ts import salobj
from .commands import create_app as create_cmd_app
from .heartbeats import create_app as create_heartbeat_app


def create_app(*args, **kwargs):
    app = web.Application(
        middlewares=[web.normalize_path_middleware()])

    app.add_subapp('/cmd/', create_cmd_app())
    app.add_subapp('/heartbeat/', create_heartbeat_app())

    return app
