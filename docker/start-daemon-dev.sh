#!/bin/bash
source /home/saluser/.setup_dev.sh
pip install -e /usr/src/love/
adev runserver /usr/src/love/python/love/commander -p 5000
