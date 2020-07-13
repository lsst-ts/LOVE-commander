#!/bin/bash
. /home/saluser/.setup_dev.sh


export PYTHONPATH=$PYTHONPATH:/usr/src/love/commander
if [[ $LSST_DDS_IP != *"."* ]]; then
  echo "Unset LSST_DDS_IP"
  unset LSST_DDS_IP
fi

cd /usr/src/love
adev runserver commander -p 5000