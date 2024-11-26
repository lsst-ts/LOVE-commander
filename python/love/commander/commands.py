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

import json

from aiohttp import web
from lsst.ts import salobj


def create_app(*args, **kwargs):
    """Create the Commands application.

    Define the Commands subapplication, which provides the endpoints to
    accept command requests.

    Returns
    -------
    `aiohttp.web.Application`
        The application instance.
    """
    domain = None
    remotes = {}

    cmd = web.Application()

    async def start_cmd(request):
        nonlocal domain
        data = await request.json()
        try:
            assert "csc" in data
            assert "salindex" in data
            assert "cmd" in data
            assert "params" in data
            assert "identity" in data
        except AssertionError:
            return web.json_response(
                {
                    "ack": f"Request must have JSON data with the following "
                    f"keys: csc, salindex, cmd_name, params, identity. Received {json.dumps(data)}"
                },
                status=400,
            )

        csc = data["csc"]
        salindex = data["salindex"]
        cmd_name = data["cmd"]
        params = data["params"]
        remote_name = f"{csc}.{salindex}"

        # Only create domain if it does not already exist.
        if domain is None:
            print("Creating salobj.Domain()")
            domain = salobj.Domain()
            domain.default_identity = "LOVE"

        # Only create remote if it does not exist already.
        if remote_name not in remotes:
            print(f"Creating remote {remote_name}.")
            # Create remote for commanding only, exclude all events and
            # telemetry topics
            remotes[remote_name] = salobj.Remote(domain, csc, salindex, include=[])
            await remotes[remote_name].start_task

        cmd = getattr(remotes[remote_name], cmd_name)
        cmd.set(**params)

        try:
            cmd_result = await cmd.start(timeout=5)
            return web.json_response({"ack": cmd_result.result})
        except salobj.AckTimeoutError as e:
            msg = (
                "No ack received from component."
                if e.ackcmd == salobj.SalRetCode.CMD_NOACK
                else f"Last ack received {e.ackcmd}."
            )
            return web.json_response({"ack": f"Command time out. {msg}"}, status=504)

    cmd.router.add_post("/", start_cmd)

    async def on_cleanup(cmd_app):
        """Close the remotes when cleaning the application.

        Parameters
        ----------
        cmd_app : `aiohttp.web.Application`
            The Commands application.
        """
        for remote_name in remotes:
            await remotes[remote_name].close()

    cmd.on_cleanup.append(on_cleanup)

    return cmd
