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


"""Define the SAL Info subapplication, which provides the endpoints to request
info from SAL.
"""
from aiohttp import web
from lsst.ts import salobj, xml

salobj_domain = None


def create_app(*args, **kwargs):
    """Create the SAL Info application.

    Define the SAL Info subapplication, which provides the endpoints to
    request info from SAL.

    Returns
    -------
    `aiohttp.web.Application`
        The application instance.
    """
    salinfo_app = web.Application()

    available_component_names = xml.subsystems
    if kwargs.get("remotes_len_limit") is not None:
        available_component_names = available_component_names[
            : kwargs.get("remotes_len_limit")
        ]

    salinfo = {}

    async def connect_to_salinfo_instances():
        """Connect to the SAL Info instances."""
        global salobj_domain
        if not salobj_domain:
            salobj_domain = salobj.Domain()
        for name in available_component_names:
            salinfo[name] = salobj.SalInfo(salobj_domain, name)

    async def get_topic_names(request):
        """Handle get topic names requests.

            Parameters
            ----------
            request : `Request`
                The original HTTP request

            Returns
            -------
            Response
                The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "<CSC_1>": {
                        "event_names": ["<event_name_1>", "<event_name_2>"],
                        "telemetry_names": [
                            "<telemetry_name_1>",
                            "<telemetry_name_2>"
                            ],
                        "command_names": [
                            "<command_name_1>",
                            "<command_name_2>"
                            ]
                    },
                    "<CSC_2>": {
                        "event_names": ["<event_name_1>", "<event_name_2>"],
                        "telemetry_names": [
                            "<telemetry_name_1>",
                            "<telemetry_name_2>"
                            ],
                        "command_names": [
                            "<command_name_1>",
                            "<command_name_2>"
                            ]
                    }
        }
        """
        accepted_categories = ["telemetry", "event", "command"]
        categories = request.rel_url.query.get("categories", "").split("-")
        categories = [c for c in categories if c in accepted_categories]
        if len(categories) == 0:
            categories = accepted_categories
        results = {
            name: {
                c + "_names": salinfo[name].__getattribute__(c + "_names")
                for c in categories
            }
            for name in salinfo
        }
        return web.json_response(results)

    def _dump_field_info(field_info):
        """Dump a FieldInfo to dictionary.

        Parameters
        ----------
        field_info : `dict`
            a list of fields description objects

        Returns
        -------
        dictionary
            The data as a dictionary of fields whose values are subdictionaries
            containing the following keys: name, description, units, type_name
        """
        return {
            k: {
                "name": field_info[k].name,
                "description": field_info[k].description,
                "units": field_info[k].units,
                "type_name": field_info[k].sal_type,
            }
            for k in field_info.keys()
            if not k.startswith("private_")
        }

    def _get_details(salinfo, categories):
        """Get detailed data of a given salinfo, for a given set of categories.

        Parameters
        ----------
        salinfo : `dict`
            Dictionary containing the SAL Info in a tree-like structure
        categories : `list[str]`
            List of categories to include, can contain any of "event",
            "telemetry" or "command".

        Returns
        -------
        dictionary
            The dictionary for the response, with a list of dictionaries
            describing each topic, for all the topics defined in the
            "categories" parameter. The dictionary is indexed by the topic type
            (event_data, telemetry_data or command_data).
        """
        result = {}
        if "telemetry" in categories:
            result["telemetry_data"] = {
                t: _dump_field_info(salinfo.component_info.topics["tel_" + t].fields)
                for t in salinfo.telemetry_names
            }
        if "command" in categories:
            result["command_data"] = {
                t: _dump_field_info(salinfo.component_info.topics["cmd_" + t].fields)
                for t in salinfo.command_names
            }

        if "event" in categories:
            result["event_data"] = {
                t: _dump_field_info(salinfo.component_info.topics["evt_" + t].fields)
                for t in salinfo.event_names
            }

        return result

    async def get_topic_data(request):
        """Handle get topic data requests.

        Parameters
        ----------
        request : `Request`
            The original HTTP request.

        Returns
        -------
        Response
            The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "<CSC_1>": {
                        "event_data": {
                        "<parameter_1>": {
                            "<field_11>": "<value_11>",
                            "<field_12>": "<value_12>",
                        },
                        "<parameter_2>": {
                            "<field_21>": "<value_21>",
                            "<field_22>": "<value_22>",
                        },
                        },
                        "telemetry_data": {
                        "<parameter_1>": {
                            "<field_11>": "<value_11>",
                            "<field_12>": "<value_12>",
                        },
                        "<parameter_2>": {
                            "<field_21>": "<value_21>",
                            "<field_22>": "<value_22>",
                        },
                        },
                        "command_data": {
                        "<parameter_1>": {
                            "<field_11>": "<value_11>",
                            "<field_12>": "<value_12>",
                        },
                        "<parameter_2>": {
                            "<field_21>": "<value_21>",
                            "<field_22>": "<value_22>",
                        },
                        },
                    },
                }
        """
        accepted_categories = ["telemetry", "event", "command"]
        categories = request.rel_url.query.get("categories", "").split("-")
        categories = [c for c in categories if c in accepted_categories]
        if len(categories) == 0:
            categories = accepted_categories
        results = {name: _get_details(salinfo[name], categories) for name in salinfo}
        return web.json_response(results)

    salinfo_app.router.add_get("/topic-names", get_topic_names)
    salinfo_app.router.add_get("/topic-data", get_topic_data)

    async def on_startup(salinfo_app):
        """Connect to the SAL Info instances when starting the application.

        Parameters
        ----------
        salinfo_app : `aiohttp.web.Application`
            The SAL Info application.
        """
        await connect_to_salinfo_instances()

    async def on_cleanup(salinfo_app):
        """Close the Salobj domain and SAL Info instances
        when cleaning the application.

        Parameters
        ----------
        salinfo_app : `aiohttp.web.Application`
            The SAL Info application.
        """
        global salobj_domain
        for name in salinfo:
            await salinfo[name].close()
        await salobj_domain.close()

    salinfo_app.on_startup.append(on_startup)
    salinfo_app.on_cleanup.append(on_cleanup)

    return salinfo_app
