"""Define the Heartbeats subapplication, which
provides the endpoints to request a heartbeat."""
from aiohttp import web
from lsst.ts.observatory.control.auxtel import ATCS
from lsst.ts.observatory.control.maintel import MTCS


atcs_client = None
mtcs_client = None


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
            atcs_client = ATCS()
            await atcs_client.start_task
        except Exception:
            atcs_client = None

    def unavailable_atcs_client():
        return web.json_response(
            {"ack": "ATCS Client could not stablish connection"},
            status=400,
        )

    connect_to_atcs_intance()

    async def auxtel_command(request):
        global atcs_client
        if not atcs_client:
            await connect_to_atcs_intance()
        if not atcs_client:
            return unavailable_atcs_client()

        req = await request.json()

        command_name = req["command_name"]
        params = req["params"]

        try:
            command = getattr(atcs_client, command_name)
        except Exception:
            resp = {"ack": "Invalid command"}
            return web.json_response(
                resp,
                status=400,
            )
        try:
            result = await command(**params)
            return web.json_response(
                {"ack": str(result)},
                status=200,
            )
        except Exception as e:
            resp = {"ack": f"Error running command {command_name}: {e}"}
            return web.json_response(
                resp,
                status=400,
            )

    async def auxtel_docstrings(request):
        global atcs_client
        if not atcs_client:
            await connect_to_atcs_intance()
        if not atcs_client:
            return unavailable_atcs_client()

        methods = [
            func
            for func in dir(atcs_client)
            if callable(getattr(atcs_client, func)) and not func.startswith("__")
        ]
        docstrings = {m: getattr(atcs_client, m).__doc__ for m in methods}
        return web.json_response(
            (docstrings),
            status=200,
        )

    async def connect_to_mtcs_intance():
        global mtcs_client
        try:
            mtcs_client = MTCS()
            await mtcs_client.start_task
        except Exception:
            mtcs_client = None

    def unavailable_mtcs_client():
        return web.json_response(
            {"ack": "MTCS Client could not stablish connection"},
            status=400,
        )

    connect_to_mtcs_intance()

    async def maintel_command(request):
        global mtcs_client
        if not mtcs_client:
            await connect_to_mtcs_intance()
        if not mtcs_client:
            return unavailable_mtcs_client()

        req = await request.json()

        command_name = req["command_name"]
        params = req["params"]

        try:
            command = getattr(mtcs_client, command_name)
        except Exception:
            resp = {"ack": "Invalid command"}
            return web.json_response(
                resp,
                status=400,
            )
        try:
            result = await command(**params)
            return web.json_response(
                {"ack": str(result)},
                status=200,
            )
        except Exception as e:
            resp = {"ack": f"Error running command {command_name}: {e}"}
            return web.json_response(
                resp,
                status=400,
            )

    async def maintel_docstrings(request):
        global mtcs_client
        if not mtcs_client:
            await connect_to_mtcs_intance()
        if not mtcs_client:
            return unavailable_mtcs_client()

        methods = [
            func
            for func in dir(mtcs_client)
            if callable(getattr(mtcs_client, func)) and not func.startswith("__")
        ]
        docstrings = {m: getattr(mtcs_client, m).__doc__ for m in methods}
        return web.json_response(
            (docstrings),
            status=200,
        )

    tcs_app.router.add_post("/aux", auxtel_command)
    tcs_app.router.add_post("/aux/", auxtel_command)
    tcs_app.router.add_get("/aux/docstrings", auxtel_docstrings)
    tcs_app.router.add_get("/aux/docstrings/", auxtel_docstrings)
    tcs_app.router.add_post("/main", maintel_command)
    tcs_app.router.add_post("/main/", maintel_command)
    tcs_app.router.add_get("/main/docstrings", maintel_docstrings)
    tcs_app.router.add_get("/main/docstrings/", maintel_docstrings)

    async def on_cleanup(tcs_app):
        # Do cleanup
        pass

    tcs_app.on_cleanup.append(on_cleanup)

    return tcs_app
