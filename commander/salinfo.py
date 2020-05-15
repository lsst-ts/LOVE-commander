from aiohttp import web
from lsst.ts import salobj
import json
import concurrent.futures
import time
import asyncio


async def create_app(*args, **kwargs):
    salinfo_app = web.Application()

    domain = salobj.Domain()
    available_idl_files = list(domain.idl_dir.glob('**/*.idl'))
    names = [file.name.split('_', )[-1].replace('.idl', '')
             for file in available_idl_files]
    if kwargs.get('remotes_len_limit') is not None:
        names = names[:kwargs.get('remotes_len_limit')]

    salinfos = {}
    for name in names:
        salinfos[name] = salobj.SalInfo(domain, name)

    async def get_metadata(request):
        results = {
            salinfos[name].metadata.name: {
                "sal_version": salinfos[name].metadata.sal_version,
                "xml_version": salinfos[name].metadata.xml_version
            }
            for name in salinfos}

        return web.json_response(results)
    salinfo_app.router.add_post('/metadata', get_metadata)

    async def on_cleanup(salinfo_app):
        for name in names:
            await salinfos[name].close()
        await domain.close()
    salinfo_app.on_cleanup.append(on_cleanup)

    return salinfo_app