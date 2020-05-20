from aiohttp import web
from lsst.ts import salobj
import json
import concurrent.futures
import time
import asyncio


async def create_app(*args, **kwargs):
    salinfo_app = web.Application()

    domain = salobj.Domain()
    available_idl_files = list(domain.idl_dir.glob("**/*.idl"))
    names = [
        file.name.split("_",)[-1].replace(".idl", "") for file in available_idl_files
    ]
    if kwargs.get("remotes_len_limit") is not None:
        names = names[: kwargs.get("remotes_len_limit")]

    salinfos = {}
    for name in names:
        salinfos[name] = salobj.SalInfo(domain, name)

    async def get_metadata(request):
        """ Handle get metadata requets."""
        results = {
            salinfos[name].metadata.name: {
                "sal_version": salinfos[name].metadata.sal_version,
                "xml_version": salinfos[name].metadata.xml_version,
            }
            for name in salinfos
        }

        return web.json_response(results)

    async def get_topic_names(request):
        """ Handle get topic names request."""
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
        """ Dump a FieldInfo to dictionary."""
        return {
            k: {
                "name": field_info[k].name,
                "description": field_info[k].description,
                "units": field_info[k].units,
                "type_name": field_info[k].type_name,
            }
            for k in field_info.keys()
        }

    def _get_details(salinfo, categories):
        """ Get detailed data of a given salinfo, for a given set of categories."""
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
        """ Handle get topic data request."""
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
        for name in names:
            await salinfos[name].close()
        await domain.close()

    salinfo_app.on_cleanup.append(on_cleanup)

    return salinfo_app
