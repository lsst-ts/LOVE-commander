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


import logging
import signal
from urllib.parse import urlencode, urlunparse

import lsst_efd_client
from aiohttp import web
from astropy.time import Time
from lsst.ts.criopy.m1m3 import BumpTestTimes
from lsst.ts.xml.tables.m1m3 import force_actuator_from_id

EFD_CLIENT_CONNECTION_TIMEOUT = 5
SITE_DOMAINS = {
    "summit_efd": "summit-lsp.lsst.codes",
    "usdf_efd": "usdf-rsp.slac.stanford.edu",
}
CHRONOGRAF_DASHBOARDS_PATHS = {
    "m1m3_bump_tests": {
        "summit_efd": "/chronograf/sources/1/dashboards/199",
        "usdf_efd": "/chronograf/sources/1/dashboards/61",
    }
}

efd_clients = dict()


def raise_timeout(*args):
    raise TimeoutError


def create_app(*args, **kwargs):
    """Create the Reports application

    Returns
    -------
    object
        The application instance
    """
    reports_app = web.Application()

    def connect_to_efd_intance(instance):
        global efd_clients

        signal.signal(signal.SIGALRM, raise_timeout)

        instance_exists = efd_clients.get(instance)
        if instance_exists is not None:
            return instance_exists

        try:
            signal.alarm(EFD_CLIENT_CONNECTION_TIMEOUT)
            efd_clients[instance] = lsst_efd_client.EfdClient(instance)
        except Exception:
            efd_clients[instance] = None
        finally:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
        return efd_clients[instance]

    def unavailable_efd_client():
        return web.json_response(
            {"ack": "EFD Client could not stablish connection"}, status=400
        )

    async def query_m1m3_bump_tests(request):
        global efd_clients
        req = await request.json()

        try:
            efd_instance = req["efd_instance"]
            start_date = req["start_date"]
            end_date = req["end_date"]
            actuator_id = req["actuator_id"]
        except Exception:
            return web.json_response(
                {"ack": "Some of the required parameters is not present"}, status=400
            )

        efd_client = efd_clients.get(efd_instance)
        if efd_client is None:
            efd_client = connect_to_efd_intance(efd_instance)
        if efd_client is None:
            return unavailable_efd_client()

        btt = BumpTestTimes(efd_client)

        logging.info(
            f"Looking for actuator #{actuator_id} bump test times in {start_date} to {end_date}"
        )
        primary, secondary = await btt.find_times(
            int(actuator_id), Time(start_date), Time(end_date)
        )
        actuator = force_actuator_from_id(actuator_id)

        def add_result(start, end, results):
            def act(index, actuator) -> int:
                return 0 if index is None else actuator

            params = {
                "refresh": "Paused",
                "tempVars[x_index]": act(actuator.x_index, actuator.actuator_id),
                "tempVars[y_index]": act(actuator.y_index, actuator.actuator_id),
                "tempVars[z_index]": actuator.actuator_id,
                "tempVars[s_index]": act(actuator.s_index, actuator.actuator_id),
                "lower": start.isot + "Z",
                "upper": end.isot + "Z",
            }
            url = urlunparse(
                (
                    "https",
                    SITE_DOMAINS[efd_instance],
                    CHRONOGRAF_DASHBOARDS_PATHS["m1m3_bump_tests"][efd_instance],
                    "",
                    urlencode(params),
                    "",
                )
            )
            results.append(
                {
                    "start": start.isot,
                    "end": end.isot,
                    "url": url,
                }
            )

        primary_tests = []
        for bump in primary:
            add_result(bump[0], bump[1], primary_tests)

        secondary_tests = []
        for bump in secondary:
            add_result(bump[0], bump[1], secondary_tests)

        response_data = {
            "primary": primary_tests,
            "secondary": secondary_tests,
        }
        return web.json_response(response_data)

    reports_app.router.add_post("/m1m3-bump-tests", query_m1m3_bump_tests)
    reports_app.router.add_post("/m1m3-bump-tests/", query_m1m3_bump_tests)

    async def on_cleanup(reports_app):
        # This app doesn't require cleaning up.
        pass

    reports_app.on_cleanup.append(on_cleanup)

    return reports_app
