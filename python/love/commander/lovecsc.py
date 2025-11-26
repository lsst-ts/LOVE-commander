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
import logging

from aiohttp import web
from love.commander.utils import unavailable_love_controller
from lsst.ts import salobj

STD_TIMEOUT = 15  # timeout for command ack
LOVE_controller = None


def create_app(*args, **kwargs):
    """Create the LOVE CSC application.

    Define LOVE CSC subapplication, which provides the endpoints to
    request info to the LOVE CSC from SAL.

    Returns
    -------
    `aiohttp.web.Application`
        The application instance.
    """
    lovecsc_app = web.Application()

    async def connect_to_love_controller():
        """Connect to the LOVE CSC.

        Notes
        -----
        LOVE_controller is a global variable that will be used to store the
        connection to the LOVE CSC using `salobj.Controller`.
        If the connection could not be established, LOVE_controller will
        be set to None.
        """
        global LOVE_controller
        try:
            LOVE_controller = salobj.Controller(
                "LOVE", index=None, do_callbacks=False, write_only=True
            )
            await LOVE_controller.start_task
        except Exception as e:
            logging.warning(e)
            LOVE_controller = None

    async def close_love_controller():
        """Close the connection to the LOVE CSC.

        Notes
        -----
        This function will close the connection to the LOVE CSC and set
        LOVE_controller to None.
        """
        global LOVE_controller
        if LOVE_controller:
            await LOVE_controller.close()
            LOVE_controller = None

    async def post_observing_log(request):
        """Handle post observing log requests.

        Parameters
        ----------
        request : `Request`
            The original HTTP request

        Returns
        -------
        Response
            The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "ack":
                    "<Description about the success state of the request>"
                }
        """
        if not LOVE_controller:
            return unavailable_love_controller()

        data = await request.json()

        try:
            assert "user" in data
            assert "message" in data
        except AssertionError:
            return web.json_response(
                {
                    "ack": "Request must have JSON data with the following keys:"
                    + f" user, message. Received {json.dumps(data)}"
                },
                status=400,
            )

        user = data["user"]
        message = data["message"]
        await LOVE_controller.evt_observingLog.set_write(user=user, message=message)

        return web.json_response({"ack": "Added new observing log to SAL"}, status=200)

    async def on_startup(lovecsc_app):
        logging.info("Running LOVE controller")
        await connect_to_love_controller()

    async def on_cleanup(lovecsc_app):
        logging.info("Closing LOVE controller")
        await close_love_controller()

    lovecsc_app.router.add_post("/observinglog", post_observing_log)

    lovecsc_app.on_startup.append(on_startup)
    lovecsc_app.on_cleanup.append(on_cleanup)

    return lovecsc_app
