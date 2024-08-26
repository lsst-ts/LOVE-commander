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

from aiohttp import web

from .commands import create_app as create_cmd_app
from .efd import create_app as create_efd_app
from .heartbeats import create_app as create_heartbeat_app
from .lfa import create_app as create_lfa_app
from .lovecsc import create_app as create_lovecsc_app
from .reports import create_app as create_reports_app
from .salinfo import create_app as create_salinfo_app
from .tcs import create_app as create_tcs_app


def create_app(*args, **kwargs):
    """Create the application with its subapplications.

    Returns
    -------
    `aiohttp.web.Application`
        the application of applications.
    """
    app = web.Application(middlewares=[web.normalize_path_middleware()])

    app.add_subapp("/cmd/", create_cmd_app())
    app.add_subapp("/heartbeat/", create_heartbeat_app())
    app.add_subapp("/lovecsc/", create_lovecsc_app())
    app.add_subapp("/efd/", create_efd_app())
    app.add_subapp("/tcs/", create_tcs_app())
    app.add_subapp("/lfa/", create_lfa_app())
    app.add_subapp("/reports/", create_reports_app())

    app.add_subapp(
        "/salinfo/",
        create_salinfo_app(remotes_len_limit=kwargs.get("remotes_len_limit")),
    )

    return app
