#!/bin/bash
source /home/saluser/.setup_dev.sh
python -m aiohttp.web -H 0.0.0.0 -P 5000 love.commander.app:create_app
