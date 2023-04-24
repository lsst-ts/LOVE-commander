#!/bin/bash
source /home/saluser/.setup_dev.sh
pip install /usr/src/love/
export PYTHONPATH=$PYTHONPATH:/usr/src/love/python/love/commander
adev runserver commander -p 5000
