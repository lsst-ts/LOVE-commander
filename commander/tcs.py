"""Define the Heartbeats subapplication, which provides the endpoints to request a heartbeat."""
from aiohttp import web
import json
from datetime import datetime
from astropy.time import Time, TimeDelta
import pytest
import asyncio
import os
# from lsst.ts.observatory.control.auxtel import ATCS
import lsst.ts.observatory.control.auxtel as auxtel

def create_app():
    """Create the TCS application

    Returns
    -------
    object
        The application instance
    """
    tcs_app = web.Application()
    atcs = auxtel.ATCS()

    async def auxtel_command(request):
        req = await request.json()

        command_name = req["command_name"]
        params = req["params"]

        try:
            command = getattr(atcs, command_name)
        except Exception:
            return web.json_response(
                {
                    "ack": f"Invalid command"
                },
                status=400,
            )
        try:
            result = await command(**params)
            return web.json_response(
                {
                    "ack": result
                },
                status=200,
            )
        except Exception:
            return web.json_response(
                {
                    "ack": f"Error running command"
                },
                status=400,
            )
        return web.json_response(
            {
                "ack": f"Error running command"
            },
            status=400,
        )

    tcs_app.router.add_post("/aux", auxtel_command)
    tcs_app.router.add_post("/aux/", auxtel_command)

    async def on_cleanup(tcs_app):
        # Do cleanup
        pass

    tcs_app.on_cleanup.append(on_cleanup)

    return tcs_app
