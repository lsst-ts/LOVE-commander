import json
import asyncio
from aiohttp import web
from unittest.mock import patch
from itertools import chain, combinations
from lsst.ts import salobj
from commander.app import create_app
from utils import NumpyEncoder
from tests import conftest

index_gen = salobj.index_generator()


async def test_metadata(client, *args, **kwargs):
    """ Test the get metadata response."""
    salobj.set_random_lsst_dds_domain()
    async with salobj.Domain() as domain:
        domain = salobj.Domain()
        available_idl_files = list(domain.idl_dir.glob("**/*.idl"))
        names = [
            file.name.split("_",)[-1].replace(".idl", "")
            for file in available_idl_files
        ]
        names = names[: conftest.REMOTES_LEN_LIMIT]

        response = await client.get("/salinfo/metadata")

        assert response.status == 200

        response_data = await response.json()

        for name, data in response_data.items():
            assert name in names
            assert "sal_version" in data
            assert "xml_version" in data
            assert data["sal_version"].count(".") == 2
            assert data["xml_version"].count(".") == 2


async def test_all_topic_names(client, *args, **kwargs):
    """ Test the get topic_names response."""
    salobj.set_random_lsst_dds_domain()
    async with salobj.Domain() as domain:
        domain = salobj.Domain()
        available_idl_files = list(domain.idl_dir.glob("**/*.idl"))
        names = [
            file.name.split("_",)[-1].replace(".idl", "")
            for file in available_idl_files
        ]
        names = names[: conftest.REMOTES_LEN_LIMIT]

        response = await client.get("/salinfo/topic-names")

        assert response.status == 200

        response_data = await response.json()

        for name, data in response_data.items():
            assert name in names
            assert "command_names" in data
            assert "event_names" in data
            assert "telemetry_names" in data
            assert type(data["command_names"]) == list
            assert type(data["event_names"]) == list
            assert type(data["telemetry_names"]) == list


async def test_some_topic_names(client, *args, **kwargs):
    """ Test the use of query params to get only some of the topic_names."""
    salobj.set_random_lsst_dds_domain()
    async with salobj.Domain() as domain:
        domain = salobj.Domain()
        available_idl_files = list(domain.idl_dir.glob("**/*.idl"))
        names = [
            file.name.split("_",)[-1].replace(".idl", "")
            for file in available_idl_files
        ]
        names = names[: conftest.REMOTES_LEN_LIMIT]

        # Get all combinations of categories:
        categories = ["command", "event", "telemetry"]
        combs = chain.from_iterable(
            combinations(categories, r) for r in range(len(categories) + 1)
        )

        for comb in combs:
            # Get categories to be requested and not to be requested
            requested = list(comb)
            non_req = list(set(categories) - set(requested))
            query_param = "-".join(requested)
            # Requeste them
            response = await client.get(
                "/salinfo/topic-names?categories=" + query_param
            )
            assert response.status == 200
            response_data = await response.json()

            # If query_params is empty no filtering is applied:
            if len(requested) == 0:
                requested = categories
                non_req = []

            for name, data in response_data.items():
                assert name in names
                # Assert that requested categories are in the response
                for r in requested:
                    key = r + "_names"
                    assert key in data
                    assert type(data[key]) == list
                # Assert that non-requested categories are NOT in the response
                for nr in non_req:
                    key = nr + "_names"
                    assert key not in data
