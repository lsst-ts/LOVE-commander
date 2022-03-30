"""Define LOVE CSC subapplication, which provides the endpoints to request info to the LOVE CSC from SAL."""
import json
import logging
from aiohttp import web
from lsst.ts import salobj

STD_TIMEOUT = 15  # timeout for command ack
csc = None


def create_app(*args, **kwargs):
    """Create the LOVECsc application

    Returns
    -------
    object
        The application instance
    """
    lovecsc_app = web.Application()

    def connect_to_love_controller():
        global csc
        try:
            csc = salobj.Controller("LOVE", index=None, do_callbacks=False)
        except Exception as e:
            logging.warning(e)
            csc = None

    connect_to_love_controller()

    def unavailable_love_controller():
        return web.json_response(
            {"ack": "LOVE CSC could not stablish connection"}, status=400
        )

    async def post_observing_log(request):
        """Handle post observing log requests.

        Parameters
        ----------
        request : Request
            The original HTTP request

        Returns
        -------
        Response
            The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "ack": "<Description about the success state of the request>"
                }
        """
        global csc
        if csc is None:
            connect_to_love_controller()
        if csc is None:
            return unavailable_love_controller()
        await csc.start_task

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

        # LOVECsc
        csc.evt_observingLog.set(user=user, message=message)
        csc.evt_observingLog.put()

        return web.json_response({"ack": "Added new observing log to SAL"}, status=200)

    lovecsc_app.router.add_post("/observinglog", post_observing_log)

    async def on_cleanup(lovecsc_app):
        global csc
        if csc is not None:
            await csc.close()

    lovecsc_app.on_cleanup.append(on_cleanup)

    return lovecsc_app
