#!/bin/bash
source /home/saluser/.setup_dev.sh
pytest -p no:cacheprovider -p no:pytest_session2file /usr/src/love/tests/