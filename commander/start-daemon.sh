#!/bin/bash

. /etc/bashrc
. .setup.sh

export PYTHONPATH=$PYTHONPATH:/usr/src/love/commander
if [[ $LSST_DDS_IP != *"."* ]]; then
  echo "Unset LSST_DDS_IP"
  unset LSST_DDS_IP
fi

cd /usr/src/love

python -m aiohttp.web -H 0.0.0.0 -P 5000 commander.app:create_app