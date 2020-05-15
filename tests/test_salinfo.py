import json
import asyncio
from aiohttp import web
from unittest.mock import patch
from lsst.ts import salobj
from commander.app import create_app
from utils import NumpyEncoder
from tests import conftest

index_gen = salobj.index_generator()


async def test_metadata(client, *args, **kwargs):
    salobj.set_random_lsst_dds_domain()
    async with salobj.Domain() as domain:
        domain = salobj.Domain()
        available_idl_files = list(domain.idl_dir.glob('**/*.idl'))
        names = [file.name.split('_', )[-1].replace('.idl', '')
                for file in available_idl_files]
        names = names[:conftest.REMOTES_LEN_LIMIT]

        response = await client.get('/salinfo/metadata')

        assert response.status == 200

        response_data = await response.json()

        for name, data in response_data.items():
            assert name in names
            assert 'sal_version' in data
            assert 'xml_version' in data
            assert data['sal_version'].count('.') == 2
            assert data['xml_version'].count('.') == 2