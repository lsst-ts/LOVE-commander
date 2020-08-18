"""Define the Heartbeats subapplication, which provides the endpoints to request a heartbeat."""
from aiohttp import web
import json
from datetime import datetime


def create_app():
    """Create the Heartbeats application

    Returns
    -------
    object
        The application instance
    """
    remotes = {}

    heartbeat = web.Application()

    async def start_heartbeat(request):
        data = await request.read()
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        return web.json_response({"timestamp": timestamp})

    heartbeat.router.add_get("/", start_heartbeat)

    async def on_cleanup(heartbeat):
        for remote_name in remotes:
            await remotes[remote_name].close()

    heartbeat.on_cleanup.append(on_cleanup)

    return heartbeat
