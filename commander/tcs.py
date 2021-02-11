"""Define the Heartbeats subapplication, which
provides the endpoints to request a heartbeat."""
from aiohttp import web

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
            resp = {"ack": f"Invalid command"}
            return web.json_response(resp, status=400,)
        try:
            result = await command(**params)
            return web.json_response({"ack": result}, status=200,)
        except Exception:
            pass
        resp = {"ack": f"Error running command"}
        return web.json_response(resp, status=400,)

    async def auxtel_docstrings(request):
        methods = [
            func
            for func in dir(atcs)
            if callable(getattr(atcs, func)) and not func.startswith("__")
        ]
        docstrings = {m: getattr(atcs, m).__doc__ for m in methods}
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
