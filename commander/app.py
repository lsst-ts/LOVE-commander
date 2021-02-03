"""Main application, instantiates the aiohtttp app."""
import json
from aiohttp import web
from lsst.ts import salobj
from .commands import create_app as create_cmd_app
from .heartbeats import create_app as create_heartbeat_app
from .salinfo import create_app as create_salinfo_app
from .lovecsc import create_app as create_lovecsc_app
from .efd import create_app as create_efd_app
from .tcs import create_app as create_tcs_app


async def create_app(*args, **kwargs):
    """Create the aaplication with its subapplications

    Returns
    -------
    object
        the application
    """
    app = web.Application(middlewares=[web.normalize_path_middleware()])

    app.add_subapp("/cmd/", create_cmd_app())
    app.add_subapp("/heartbeat/", create_heartbeat_app())
    app.add_subapp("/lovecsc/", create_lovecsc_app())
    app.add_subapp("/efd/", create_efd_app())
    app.add_subapp("/tcs/", create_tcs_app())

    app.add_subapp(
        "/salinfo/",
        await create_salinfo_app(remotes_len_limit=kwargs.get("remotes_len_limit")),
    )

    return app
