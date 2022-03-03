#!/bin/bash
source /home/saluser/.setup_dev.sh
export PYTHONPATH=$PYTHONPATH:/usr/src/love/commander
python -m aiohttp.web -H 0.0.0.0 -P 5000 commander.app:create_app
