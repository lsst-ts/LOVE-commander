import json
from aiohttp import web
from lsst.ts import salobj
from .commands import create_app as create_cmd_app


def create_app():
    app = web.Application(
        middlewares=[web.normalize_path_middleware()])

    app.add_subapp('/cmd/', create_cmd_app())

    return app
