#!/bin/bash
. /home/saluser/.setup_dev.sh


export PYTHONPATH=$PYTHONPATH:/usr/src/love/commander

cd /usr/src/love
adev runserver commander -p 5000