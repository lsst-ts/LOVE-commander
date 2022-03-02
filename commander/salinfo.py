"""Define the SAL Info subapplication, which provides the endpoints to request info from SAL."""
from aiohttp import web
from lsst.ts import salobj


def create_app(*args, **kwargs):
    """Create the SAL Info application

    Returns
    -------
    object
        The application instance
    """
    salinfo_app = web.Application()

    domain = salobj.Domain()
    available_idl_files = list(domain.idl_dir.glob("**/*.idl"))
    names = [
        file.name.split("_",)[
            -1
        ].replace(".idl", "")
        for file in available_idl_files
    ]
    if kwargs.get("remotes_len_limit") is not None:
        names = names[: kwargs.get("remotes_len_limit")]

    salinfos = {}
    for name in names:
        salinfos[name] = salobj.SalInfo(domain, name)

    async def get_metadata(request):
        """Handle get metadata requests.

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
                    "sal_version": "<SAL version in format x.x.x>",
                    "xml_version": "<XML version in format x.x.x>"
                }
        """
        results = {
            salinfos[name].metadata.name: {
                "sal_version": salinfos[name].metadata.sal_version,
                "xml_version": salinfos[name].metadata.xml_version,
            }
            for name in salinfos
        }

        return web.json_response(results)

    async def get_topic_names(request):
        """Handle get topic names requests.

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
                    "<CSC_1>": {
                        "event_names": ["<event_name_1>", "<event_name_2>"],
                        "telemetry_names": ["<telemetry_name_1>", "<telemetry_name_2>"],
                        "command_names": ["<command_name_1>", "<command_name_2>"]
                    },
                    "<CSC_2>": {
                        "event_names": ["<event_name_1>", "<event_name_2>"],
                        "telemetry_names": ["<telemetry_name_1>", "<telemetry_name_2>"],
                        "command_names": ["<command_name_1>", "<command_name_2>"]
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
                c + "_names": salinfos[name].__getattribute__(c + "_names")
                for c in categories
            }
            for name in salinfos
        }
        return web.json_response(results)

    def _dump_field_info(field_info):
        """Dump a FieldInfo to dictionary.

        Parameters
        ----------
        field_info : dictionary of object
            a list of fields description objects

        Returns
        -------
        dictionary
            The data as a dictionary of fields whose values are subdictionaries containing the following keys:
            name, description, units, type_name
        """
        return {
            k: {
                "name": field_info[k].name,
                "description": field_info[k].description,
                "units": field_info[k].units,
                "type_name": field_info[k].type_name,
            }
            for k in field_info.keys()
            if not k.startswith("private_")
        }

    def _get_details(salinfo, categories):
        """Get detailed data of a given salinfo, for a given set of categories.

        Parameters
        ----------
        salinfo : dictionary
            Dictionary containing the SAL Info in a tree-like structure
        categories : list of string
            List of categories to include, can contain any of "event", "telemetry" or "command"

        Returns
        -------
        dictionary
            The dictionary for the response, with a list of dictionaries describing each topic,
            for all the topics defined in the "categories" parameter.
            The dictionary is indexed by the topic type (event_data, telemetry_data or command_data).
        """
        result = {}
        if "telemetry" in categories:
            result["telemetry_data"] = {
                t: _dump_field_info(salinfo.metadata.topic_info[t].field_info)
                for t in salinfo.telemetry_names
            }
        if "command" in categories:
            result["command_data"] = {
                t: _dump_field_info(
                    salinfo.metadata.topic_info["command_" + t].field_info
                )
                for t in salinfo.command_names
            }

        if "event" in categories:
            result["event_data"] = {
                t: _dump_field_info(
                    salinfo.metadata.topic_info["logevent_" + t].field_info
                )
                for t in salinfo.event_names
            }

        return result

    async def get_topic_data(request):
        """Handle get topic data requests.

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
        results = {name: _get_details(salinfos[name], categories) for name in salinfos}
        return web.json_response(results)

    salinfo_app.router.add_get("/metadata", get_metadata)
    salinfo_app.router.add_get("/topic-names", get_topic_names)
    salinfo_app.router.add_get("/topic-data", get_topic_data)

    async def on_cleanup(salinfo_app):
        """Close the domain when cleaning the application

        Parameters
        ----------
        salinfo_app : object
            The SAL Info application
        """
        for name in names:
            await salinfos[name].close()
        await domain.close()

    salinfo_app.on_cleanup.append(on_cleanup)

    return salinfo_app
