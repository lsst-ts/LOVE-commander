# This file is part of LOVE-commander.
#
# Copyright (c) 2023 Inria Chile.
#
# Developed by Inria Chile.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or at
# your option any later version.
#
# This program is distributed in the hope that it will be useful,but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime

from aiohttp import web


def create_app(*args, **kwargs):
    """Create the Heartbeats application.

    Define the Heartbeats subapplication, which provides the endpoints to
    request a heartbeat.

    Returns
    -------
    `aiohttp.web.Application`
        The application instance.
    """
    remotes = {}

    heartbeat = web.Application()

    async def start_heartbeat(request):
        await request.read()
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        return web.json_response({"timestamp": timestamp})

    heartbeat.router.add_get("/", start_heartbeat)

    async def on_cleanup(heartbeat_app):
        """Close the remotes when cleaning the application.

        Parameters
        ----------
        salinfo_app : `aiohttp.web.Application`
            The Heartbeats application.
        """
        for remote_name in remotes:
            await remotes[remote_name].close()

    heartbeat.on_cleanup.append(on_cleanup)

    return heartbeat
