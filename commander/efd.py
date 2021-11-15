"""Define the Heartbeats subapplication, which provides the endpoints to request a heartbeat."""
from aiohttp import web
import lsst_efd_client
from astropy.time import Time, TimeDelta
import asyncio

efd_clients = dict()


def create_app(*args, **kwargs):
    """Create the EFD application

    Returns
    -------
    object
        The application instance
    """
    efd_app = web.Application()

    def connect_to_efd_intance(instance):
        global efd_clients
        try:
            efd_clients[instance] = lsst_efd_client.EfdClient(instance)
        except Exception:
            efd_clients[instance] = None
        return efd_clients[instance]

    def unavailableEfdClient():
        return web.json_response(
            {"ack": f"EFD Client could not stablish connection"}, status=400
        )

    async def query_efd_timeseries(request):
        global efd_clients
        req = await request.json()

        efd_instance = req["efd_instance"]
        if efd_clients[efd_instance] is None:
            efd_client = connect_to_efd_intance(efd_instance)

        if efd_clients[efd_instance] is None:
            return unavailableEfdClient()

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

    async def query_efd_clients(request):
        efd_instances = lsst_efd_client.EfdClient.list_efd_names()
        response_data = {"instances": efd_instances}
        return web.json_response(response_data, status=200)

    efd_app.router.add_post("/timeseries", query_efd_timeseries)
    efd_app.router.add_post("/timeseries/", query_efd_timeseries)

    async def on_cleanup(efd_app):
        # Do cleanup
        pass

    efd_app.on_cleanup.append(on_cleanup)

    return efd_app
