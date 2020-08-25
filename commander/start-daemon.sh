#!/bin/bash
. /home/saluser/.setup_dev.sh


export PYTHONPATH=$PYTHONPATH:/usr/src/love/commander

cd /usr/src/love

python -m aiohttp.web -H 0.0.0.0 -P 5000 commander.app:create_app