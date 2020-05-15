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
        names = names[:1]
    remotes = {}
    for name in names:
        remote = salobj.Remote(domain, name)
        await remote.start_task
        remotes[name] = remote

    async def get_metadata(request):
        results = {
            remotes[remote_name].salinfo.metadata.name: {
                "sal_version": remotes[remote_name].salinfo.metadata.sal_version,
                "xml_version": remotes[remote_name].salinfo.metadata.xml_version
            }
            for remote_name in remotes}

        return web.json_response(results)
    salinfo_app.router.add_post('/metadata', get_metadata)

    async def on_cleanup(salinfo_app):
        for remote_name in remotes:
            await remotes[remote_name].close()
        await domain.close()
    salinfo_app.on_cleanup.append(on_cleanup)

    return salinfo_app