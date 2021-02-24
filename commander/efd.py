"""Define the Heartbeats subapplication, which provides the endpoints to request a heartbeat."""
from aiohttp import web
import lsst_efd_client
from astropy.time import Time, TimeDelta
import asyncio
import os

efd_client = None


def create_app():
    """Create the EFD application

    Returns
    -------
    object
        The application instance
    """
    efd_app = web.Application()
    efd_instance = os.environ.get("EFD_INSTANCE", "summit_efd")

    def connect_to_efd_intance():
        global efd_client
        try:
            efd_client = lsst_efd_client.EfdClient(efd_instance)
        except ConnectionError:
            efd_client = None

    connect_to_efd_intance()

    def unavailableEfdClient():
        return web.json_response(
            {"ack": f"EFD Client could not stablish connection"}, status=400
        )

    async def query_efd_timeseries(request):
        global efd_client
        if efd_client is None:
            connect_to_efd_intance()

        if efd_client is None:
            return unavailableEfdClient()

        req = await request.json()

        start_date = req["start_date"]
        time_window = int(req["time_window"])
        cscs = req["cscs"]
        resample = req["resample"]

        parsed_date = Time(start_date, scale="tai")
        time_delta = TimeDelta(time_window * 60, format="sec", scale="tai")
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
                        parsed_date,
                        time_delta,
                        index=int(index),
                        is_window=True,
                    )
                    sources.append(f"{csc}-{index}-{topic}")
                    query_tasks.append(task)

        results = [
            r.resample(resample).mean() if not r.empty else r
            for r in await asyncio.gather(*query_tasks)
        ]
        results = [r.to_dict() for r in results]

        for res in results:
            for field in res:
                items = res[field].items()
                res[field] = [{"ts": str(item[0]), "value": item[1]} for item in items]

        response_data = dict(zip(sources, results))
        return web.json_response(response_data)

    efd_app.router.add_post("/timeseries", query_efd_timeseries)
    efd_app.router.add_post("/timeseries/", query_efd_timeseries)

    async def on_cleanup(efd_app):
        # Do cleanup
        pass

    efd_app.on_cleanup.append(on_cleanup)

    return efd_app
