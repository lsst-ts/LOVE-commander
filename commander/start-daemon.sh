#!/bin/bash

. /etc/bashrc
. .setup.sh

export PYTHONPATH=$PYTHONPATH:/usr/src/love/commander
if [[ $LSST_DDS_IP != *"."* ]]; then
  echo "Unset LSST_DDS_IP"
  unset LSST_DDS_IP
fi

flask run