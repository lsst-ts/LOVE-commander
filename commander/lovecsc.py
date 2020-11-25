"""Define the SAL Info subapplication, which provides the endpoints to request info from SAL."""
from aiohttp import web
from lsst.ts import salobj
from commander.lovecsc_controller import LOVECsc
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
    salinfo_app = web.Application()

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
        csc = LOVECsc()
        await csc.start_task
        
        # TODO: how can I check that observing log was added?
        csc.add_observing_log(user, message)
        await csc.close()

        return web.json_response(
            {
                "ack": "Added new observing log to SAL"
            },
            status=200
        )


    salinfo_app.router.add_post("/observinglog", post_observingLog)

    async def on_cleanup(salinfo_app):
        """Close the domain when cleaning the application

        Parameters
        ----------
        """
        pass

    salinfo_app.on_cleanup.append(on_cleanup)

    return salinfo_app
