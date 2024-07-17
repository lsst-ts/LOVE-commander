# This file is part of LOVE-commander.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from aiohttp import web
from lsst.ts.planning.tool import ZephyrInterface


def create_app(*args, **kwargs):
    """Create the Planning Tool application.

    Define Planning Tool subapplication, which provides the endpoints to
    interact with lsst.ts.planning.tool methods.

    Returns
    -------
    `aiohttp.web.Application`
        The application instance.
    """

    planning_tool_app = web.Application()

    async def query_zephyr_test_cycles(request):
        req = await request.json()

        try:
            zephyr_api_token = req["zephyr_api_token"]
            jira_api_token = req["jira_api_token"]
            jira_username = req["jira_username"]
        except Exception:
            return web.json_response(
                {"ack": "Some of the required parameters are not present"}, status=400
            )

        zephyr_interface = ZephyrInterface(
            jira_api_token=jira_api_token,
            jira_username=jira_username,
            zephyr_api_token=zephyr_api_token,
        )

        test_cycles = await zephyr_interface.get_test_cycles(cycle_keys=["name"])

        response_data = test_cycles
        return web.json_response(response_data)

    async def query_zephyr_test_cycle(request):
        req = await request.json()

        try:
            zephyr_api_token = req["zephyr_api_token"]
            jira_api_token = req["jira_api_token"]
            jira_username = req["jira_username"]
            test_cycle_key = req["test_cycle_key"]
        except Exception:
            return web.json_response(
                {"ack": "Some of the required parameters are not present"}, status=400
            )

        zephyr_interface = ZephyrInterface(
            jira_api_token=jira_api_token,
            jira_username=jira_username,
            zephyr_api_token=zephyr_api_token,
        )

        test_cycle = await zephyr_interface.get_test_cycle(test_cycle_key)

        response_data = test_cycle
        return web.json_response(response_data)

    async def query_zephyr_test_cases(request):
        req = await request.json()

        try:
            zephyr_api_token = req["zephyr_api_token"]
            jira_api_token = req["jira_api_token"]
            jira_username = req["jira_username"]
            test_cycle_key = req["test_cycle_key"]
        except Exception:
            return web.json_response(
                {"ack": "Some of the required parameters are not present"}, status=400
            )

        zephyr_interface = ZephyrInterface(
            jira_api_token=jira_api_token,
            jira_username=jira_username,
            zephyr_api_token=zephyr_api_token,
        )

        test_cases = await zephyr_interface.get_test_cases(test_cycle_key)

        response_data = test_cases
        return web.json_response(response_data)

    async def query_zephyr_last_test_execution(request):
        req = await request.json()

        try:
            zephyr_api_token = req["zephyr_api_token"]
            jira_api_token = req["jira_api_token"]
            jira_username = req["jira_username"]
            test_cycle_key = req["test_cycle_key"]
            test_case_key = req["test_case_key"]
        except Exception:
            return web.json_response(
                {"ack": "Some of the required parameters are not present"}, status=400
            )

        zephyr_interface = ZephyrInterface(
            jira_api_token=jira_api_token,
            jira_username=jira_username,
            zephyr_api_token=zephyr_api_token,
        )

        test_execution = await zephyr_interface.get_last_test_execution(
            test_cycle_key, test_case_key
        )

        response_data = test_execution
        return web.json_response(response_data)

    # Define the endpoints
    planning_tool_app.router.add_post("/test-cycles", query_zephyr_test_cycles)
    planning_tool_app.router.add_post("/test-cycles/", query_zephyr_test_cycles)
    planning_tool_app.router.add_post("/test-cycle", query_zephyr_test_cycle)
    planning_tool_app.router.add_post("/test-cycle/", query_zephyr_test_cycle)
    planning_tool_app.router.add_post("/test-cases", query_zephyr_test_cases)
    planning_tool_app.router.add_post("/test-cases/", query_zephyr_test_cases)
    planning_tool_app.router.add_post(
        "/test-last-execution", query_zephyr_last_test_execution
    )
    planning_tool_app.router.add_post(
        "/test-last-execution/", query_zephyr_last_test_execution
    )

    async def on_cleanup(planning_tool_app):
        # This app doesn't require cleaning up.
        pass

    planning_tool_app.on_cleanup.append(on_cleanup)

    return planning_tool_app
