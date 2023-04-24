#!/bin/bash
source /home/saluser/.setup_dev.sh
pip install /usr/src/love/
cd /usr/src/love/
pytest -p no:cacheprovider -p no:pytest_session2file tests/