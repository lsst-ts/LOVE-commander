"""Define the Heartbeats subapplication, which provides the endpoints to request a heartbeat."""
from aiohttp import web
import json
from datetime import datetime
import lsst_efd_client
from astropy.time import Time, TimeDelta
import pytest
import asyncio
from astropy.time import Time, TimeDelta

def create_app():
    """Create the EFD application

    Returns
    -------
    object
        The application instance
    """
    efd_app = web.Application()

    async def query_efd_timeseries(request):
        efd_client = lsst_efd_client.EfdClient()
        req = await request.json()

        start_date = req["start_date"]
        time_window = req["time_window"]
        cscs = req["cscs"]
        resample = req["resample"]
        
        parsed_date = Time(start_date, scale='tai')
        time_delta = TimeDelta(time_window, format='sec')
        query_tasks = []
        sources = []
        for csc in cscs:
            indices = cscs[csc]
            for index in indices:
                topics = indices[index]
                for topic in topics:
                    fields = topics[topic]
                    task = efd_client.select_time_series(
                        f"lsst.sal.{csc}.{topic}", 
                        fields,
                        start_date,
                        time_delta,
                        index=index,
                        is_window=True
                    )
                    sources.append(f"{csc}-{index}-{topic}")
                    query_tasks.append(task)

        results = [r.result() for r in await asyncio.gather(*query_tasks)]
        response_data = dict(zip(sources,  results))
        return web.json_response(response_data)

    efd_app.router.add_post("/timeseries", query_efd_timeseries)

    async def on_cleanup(efd_app):
        # Do cleanup
        pass

    efd_app.on_cleanup.append(on_cleanup)

    return efd_app
