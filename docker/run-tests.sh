#!/bin/bash
source /home/saluser/.setup_dev.sh
cd /usr/src/love/
# pytest -p no:cacheprovider -p no:pytest_session2file
pip show asyncio
pip show aiohttp
pytest --asyncio-mode=strict