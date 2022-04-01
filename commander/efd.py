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
        instance_exists = efd_clients.get(instance)
        if instance_exists is not None:
            return instance_exists

        try:
            efd_clients[instance] = lsst_efd_client.EfdClient(instance)
        except Exception:
            efd_clients[instance] = None
        return efd_clients[instance]

    def unavailable_efd_client():
        return web.json_response(
            {"ack": "EFD Client could not stablish connection"}, status=400
        )

    async def query_efd_timeseries(request):
        global efd_clients
        req = await request.json()

        try:
            efd_instance = req["efd_instance"]
            start_date = req["start_date"]
            time_window = int(req["time_window"])
            cscs = req["cscs"]
            resample = req["resample"]
        except Exception:
            return web.json_response(
                {"error": "Some of the required parameters is not present"}, status=400
            )

        efd_client = efd_clients.get(efd_instance)
        if efd_client is None:
            efd_client = connect_to_efd_intance(efd_instance)
        if efd_client is None:
            return unavailable_efd_client()

        parsed_date = Time(start_date, scale="utc")
        time_delta = TimeDelta(time_window * 60, format="sec")
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
        try:
            efd_instances = lsst_efd_client.EfdClient.list_efd_names()
            response_data = {"instances": efd_instances}
        except Exception as e:
            response_data = {"error": e}
        return web.json_response(response_data, status=200)

    efd_app.router.add_post("/timeseries", query_efd_timeseries)
    efd_app.router.add_post("/timeseries/", query_efd_timeseries)
    efd_app.router.add_get("/efd_clients", query_efd_clients)
    efd_app.router.add_get("/efd_clients/", query_efd_clients)

    async def on_cleanup(efd_app):
        # Do cleanup
        pass

    efd_app.on_cleanup.append(on_cleanup)

    return efd_app
