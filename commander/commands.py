"""Define the Commands subapplication, which provides the endpoints to accept command requests."""
from aiohttp import web
from lsst.ts import salobj
import json


def create_app():
    """Create the Commands application

    Returns
    -------
    object
        The application instance
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
        except AssertionError:
            return web.json_response(
                {
                    "ack": f"Request must have JSON data with the following "
                    f"keys: csc, salindex, cmd_name, params. Received {json.dumps(data)}"
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
            cmd_result = await cmd.start(timeout=10)
            return web.json_response({"ack": cmd_result.result})
        except salobj.AckTimeoutError as e:
            msg = (
                "No ack received from component."
                if e.ackcmd == salobj.SalRetCode.CMD_NOACK
                else f"Last ack received {e.ackcmd}."
            )
            return web.json_response({"ack": f"Command time out. {msg}"}, status=504)

    cmd.router.add_post("/", start_cmd)

    async def on_cleanup(cmd):
        for remote_name in remotes:
            await remotes[remote_name].close()

    cmd.on_cleanup.append(on_cleanup)

    return cmd
