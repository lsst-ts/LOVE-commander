#!/bin/bash
source /home/saluser/.setup_dev.sh
export PYTHONPATH=$PYTHONPATH:/usr/src/love/commander
adev runserver commander -p 5000
