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

import asyncio
import logging
import math
import signal

import lsst_efd_client
from aiohttp import web
from astropy.time import Time, TimeDelta

EFD_CLIENT_CONNECTION_TIMEOUT = 5
efd_clients = dict()


def raise_timeout(*args):
    raise TimeoutError


def create_app(*args, **kwargs):
    """Create the EFD application.

    Define the EFD subapplication, which provides the endpoints to
    make queries to specific EFD instances.

    Returns
    -------
    `aiohttp.web.Application`
        The application instance.
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
                res[field] = [
                    {
                        "ts": str(item[0]),
                        "value": None if math.isnan(item[1]) else item[1],
                    }
                    for item in items
                ]

        response_data = dict(zip(sources, results))
        return web.json_response(response_data)

    async def query_efd_most_recent_timeseries(request):
        global efd_clients
        req = await request.json()

        try:
            efd_instance = req["efd_instance"]
            cscs = req["cscs"]
            num = int(req.get("num", 1))
            time_cut = req.get("time_cut", None)
        except Exception:
            return web.json_response(
                {"ack": "Some of the required parameters is not present"}, status=400
            )

        efd_client = efd_clients.get(efd_instance)
        if efd_client is None:
            efd_client = connect_to_efd_intance(efd_instance)
        if efd_client is None:
            return unavailable_efd_client()

        query_tasks = []
        sources = []
        for csc in cscs:
            indexes = cscs[csc]
            for index in indexes:
                topics = indexes[index]
                for topic in topics:
                    fields = topics[topic]
                    task = efd_client.select_top_n(
                        f"lsst.sal.{csc}.{topic}",
                        fields,
                        num,
                        time_cut=time_cut,
                        index=int(index),
                    )
                    sources.append(f"{csc}-{index}-{topic}")
                    query_tasks.append(task)

        results = [r for r in await asyncio.gather(*query_tasks)]
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
                    # Make sure the private_rcvStamp field is present
                    if "private_rcvStamp" not in fields:
                        fields.append("private_rcvStamp")
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
        results = [
            sorted(
                r.to_dict("records"), key=lambda x: x["private_rcvStamp"], reverse=True
            )
            for r in results
        ]

        response_data = dict(zip(sources, results))
        return web.json_response(response_data)

    async def query_efd_clients(request):
        try:
            efd_instances = lsst_efd_client.EfdClient.list_efd_names()
            return web.json_response({"instances": efd_instances}, status=200)
        except Exception as e:
            return web.json_response({"ack": e}, status=400)

    efd_app.router.add_post("/timeseries", query_efd_timeseries)
    efd_app.router.add_post("/timeseries/", query_efd_timeseries)
    efd_app.router.add_post("/top_timeseries", query_efd_most_recent_timeseries)
    efd_app.router.add_post("/top_timeseries/", query_efd_most_recent_timeseries)
    efd_app.router.add_post("/logmessages", query_efd_logs)
    efd_app.router.add_post("/logmessages/", query_efd_logs)
    efd_app.router.add_get("/efd_clients", query_efd_clients)
    efd_app.router.add_get("/efd_clients/", query_efd_clients)

    async def on_cleanup(app):
        global efd_clients
        for instance, client in efd_clients.items():
            if client is not None:
                try:
                    client.close()
                except Exception as e:
                    logging.error(f"Error closing EFD client {instance}: {e}")
        efd_clients = dict()

    efd_app.on_cleanup.append(on_cleanup)

    return efd_app
