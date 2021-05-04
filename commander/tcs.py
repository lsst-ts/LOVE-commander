"""Define the Heartbeats subapplication, which
provides the endpoints to request a heartbeat."""
from aiohttp import web

# from lsst.ts.observatory.control.auxtel import ATCS
import lsst.ts.observatory.control.auxtel as auxtel

atcs_client = None


def create_app():
    """Create the TCS application

    Returns
    -------
    object
        The application instance
    """
    tcs_app = web.Application()

    async def connect_to_atcs_intance():
        global atcs_client
        try:
            atcs_client = auxtel.ATCS()
            await atcs_client.start_task
        except Exception:
            atcs_client = None

    connect_to_atcs_intance()

    def unavailable_atcs_client():
        return web.json_response(
            {"ack": f"ATCS Client could not stablish connection"}, status=400
        )

    async def auxtel_command(request):
        req = await request.json()

        command_name = req["command_name"]
        params = req["params"]

        try:
            command = getattr(atcs_client, command_name)
        except Exception:
            resp = {"ack": f"Invalid command"}
            return web.json_response(resp, status=400,)
        try:
            result = await command(**params)
            return web.json_response({"ack": str(result)}, status=200,)
        except Exception as e:
            resp = {"ack": f"Error running command {command_name}: {e}"}
            return web.json_response(resp, status=400,)

    async def auxtel_docstrings(request):
        methods = [
            func
            for func in dir(atcs_client)
            if callable(getattr(atcs_client, func)) and not func.startswith("__")
        ]
        docstrings = {m: getattr(atcs_client, m).__doc__ for m in methods}
        return web.json_response((docstrings), status=200,)

    tcs_app.router.add_post("/aux", auxtel_command)
    tcs_app.router.add_post("/aux/", auxtel_command)
    tcs_app.router.add_get("/docstrings", auxtel_docstrings)
    tcs_app.router.add_get("/docstrings/", auxtel_docstrings)

    async def on_cleanup(tcs_app):
        # Do cleanup
        pass

    tcs_app.on_cleanup.append(on_cleanup)

    return tcs_app
