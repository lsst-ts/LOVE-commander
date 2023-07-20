import signal
from aiohttp import web
import lsst_efd_client
from astropy.time import Time, TimeDelta
import asyncio

MAX_EFD_LOGS_LEN = 100
EFD_CLIENT_CONNECTION_TIMEOUT = 5
efd_clients = dict()


def raise_timeout(*args):
    raise TimeoutError


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

        signal.signal(signal.SIGALRM, raise_timeout)

        instance_exists = efd_clients.get(instance)
        if instance_exists is not None:
            return instance_exists

        try:
            signal.alarm(EFD_CLIENT_CONNECTION_TIMEOUT)
            efd_clients[instance] = lsst_efd_client.EfdClient(instance)
        except Exception:
            efd_clients[instance] = None
        finally:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
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
                {"ack": "Some of the required parameters is not present"}, status=400
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
            indexes = cscs[csc]
            for index in indexes:
                topics = indexes[index]
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

    async def query_efd_logs(request):
        global efd_clients
        req = await request.json()

        try:
            efd_instance = req["efd_instance"]
            start_date = req["start_date"]
            end_date = req["end_date"]
            cscs = req["cscs"]
            scale = req["scale"]
        except Exception:
            return web.json_response(
                {"ack": "Some of the required parameters is not present"}, status=400
            )

        efd_client = efd_clients.get(efd_instance)
        if efd_client is None:
            efd_client = connect_to_efd_intance(efd_instance)
        if efd_client is None:
            return unavailable_efd_client()

        start_date = Time(start_date, scale=scale).utc
        end_date = Time(end_date, scale=scale).utc
        query_tasks = []
        sources = []
        for csc in cscs:
            indexes = cscs[csc]
            for index in indexes:
                topics = indexes[index]
                for topic in topics:
                    fields = topics[topic]
                    task = efd_client.select_time_series(
                        f"lsst.sal.{csc}.{topic}",
                        fields,
                        start_date,
                        end_date,
                        index=int(index),
                    )
                    sources.append(f"{csc}-{index}-{topic}")
                    query_tasks.append(task)

        results = [r for r in await asyncio.gather(*query_tasks)]
        results = [r.to_dict("records") for r in results]

        flattened_results = []
        result_id_counter = 0
        for sublist in results:
            for item in sublist:
                result_id_counter += 1
                item["id"] = result_id_counter
                flattened_results.append(item)

        flattened_results.sort(key=lambda x: x["private_rcvStamp"], reverse=False)
        marked_results_ids = [
            item["id"] for item in flattened_results[:MAX_EFD_LOGS_LEN]
        ]

        filtered_results = []
        for s, sublist in enumerate(results):
            filtered_results.append([])
            for i, item in enumerate(sublist):
                if item["id"] not in marked_results_ids:
                    continue
                filtered_results[s].append(results[s][i])

        response_data = dict(zip(sources, filtered_results))
        return web.json_response(response_data)

    async def query_efd_clients(request):
        try:
            efd_instances = lsst_efd_client.EfdClient.list_efd_names()
            return web.json_response({"instances": efd_instances}, status=200)
        except Exception as e:
            return web.json_response({"ack": e}, status=400)

    efd_app.router.add_post("/timeseries", query_efd_timeseries)
    efd_app.router.add_post("/timeseries/", query_efd_timeseries)
    efd_app.router.add_post("/logmessages", query_efd_logs)
    efd_app.router.add_post("/logmessages/", query_efd_logs)
    efd_app.router.add_get("/efd_clients", query_efd_clients)
    efd_app.router.add_get("/efd_clients/", query_efd_clients)

    async def on_cleanup(efd_app):
        # Do cleanup
        pass

    efd_app.on_cleanup.append(on_cleanup)

    return efd_app
