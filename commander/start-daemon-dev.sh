#!/bin/bash
. /home/saluser/.setup_dev.sh


export PYTHONPATH=$PYTHONPATH:/usr/src/love/commander
/home/saluser/repos/ts_sal/bin/make_idl_files.py LOVE

cd /usr/src/love
adev runserver commander -p 5000