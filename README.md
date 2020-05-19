# LOVE-commander

LOVE service to send SAL commands from http endpoints using salobj

## Running tests

Disabling plugins that may throw errors due to not having write access is recommended:

```
pytest -p no:cacheprovider -p no:pytest_session2file
```

## 1. Use as part of the LOVE system

In order to use the LOVE-commander as part of the LOVE system we recommend to use the docker-compose and configuration files provided in the [LOVE-integration-tools](https://github.com/lsst-ts/LOVE-integration-tools) repo. Please follow the instructions there.

## 2. Local load for development

We provide a docker image and a docker-compose file in order to load the LOVE-commander locally for development purposes, i.e. run tests and build documentation.

This docker-compose does not copy the code into the image, but instead it mounts the repository inside the image, this way you can edit the code from outside the docker container with no need to rebuild or restart.

### 2.1 Load and get into the docker image

Follow these instructions to run the application in a docker container and get into it:

1. Launch and get into the container:

```
docker-compose up -d
docker-exec commander bash
```

2. Inside the container:, load the setup and got to love folder

```
source .setup.sh
cd /usr/src/love
```

### 2.2 Run tests

Once inside the container and in the `love` folder you can run the tests. Disabling plugins that may throw errors due to not having write access is recommended:

```
pytest -p no:cacheprovider -p no:pytest_session2file
```

You may filter tests with the `-k <filter-substring>` flag, where `<filter-substring>` can be a file or a test suite name.
For example the following command:

```
pytest -p no:cacheprovider -p no:pytest_session2file -k metadata
```

will run the `test_metadata` test of the `test_salinfo.py` file.
