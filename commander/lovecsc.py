"""Define the SAL Info subapplication, which provides the endpoints to request info from SAL."""
from aiohttp import web
from lsst.ts import salobj
import utils
import json

STD_TIMEOUT = 15  # timeout for command ack

index_gen = salobj.index_generator()



def create_app(*args, **kwargs):
    """Create the LOVECsc application

    Returns
    -------
    object
        The application instance
    """
    lovecsc_app = web.Application()
    csc = salobj.Controller("LOVE", index=None, do_callbacks=False)

    async def post_observingLog(request):
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

        data = await request.json()

        try:
            assert "user" in data
            assert "message" in data
        except AssertionError:
            return web.json_response(
                {
                    "ack": f"Request must have JSON data with the following keys: user, message. Received {json.dumps(data)}"
                },
                status=400,
            )

        user = data["user"]
        message = data["message"]

        # LOVECsc
        csc.evt_observingLog.set(user=user, message=message)
        csc.evt_observingLog.put()

        return web.json_response(
            {
                "ack": "Added new observing log to SAL"
            },
            status=200
        )


    lovecsc_app.router.add_post("/observinglog", post_observingLog)

    async def on_cleanup(lovecsc_app):
        await csc.close()

    lovecsc_app.on_cleanup.append(on_cleanup)

    return lovecsc_app
