# LOVE-commander

LOVE service to send SAL commands from http endpoints using salobj.

See the documentation here: https://love-commander.lsst.io/

## 1. Use as part of the LOVE system

In order to use the LOVE-commander as part of the LOVE system we recommend to use the docker-compose and configuration files provided in the [LOVE-integration-tools](https://github.com/lsst-ts/LOVE-integration-tools) repo. Please follow the instructions there.

## 2. Local load for development

We provide docker images and a docker-compose file in order to load the LOVE-commander locally for development purposes, i.e. run tests and build documentation.

This docker-compose does not copy the code into the image, but instead it mounts the repository inside the image, this way you can edit the code from outside the docker container with no need to rebuild or restart.

### 2.1 Load and get into the docker image

Follow these instructions to run the application in a docker container and get into it:

1. Launch and get into the container:

```
cd docker/
export dev_cycle=develop #Here you can set a specified version of the lsstts/develop-env image
docker-compose up -d --build
docker-compose exec commander bash
```

2. Inside the container:, load the setup and got to love folder

```
source /home/saluser/.setup_dev.sh # Here some configurations will be loaded and you will enter another bash.
pip install -e /usr/src/love # Install the love.commander package
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

### 2.3 Build documentation

Once inside the container and in the `love` folder you can build the documentation as follows:

```
cd docsrc/
./create_docs.sh
```

### Linting & Formatting
This code uses pre-commit to maintain `black` formatting, `isort` and `flake8` compliance. To enable this, run the following commands once (the first removes the previous pre-commit hook):

```
git config --unset-all core.hooksPath
generate_pre_commit_conf
```

For more details on how to use `generate_pre_commit_conf` please follow: https://tssw-developer.lsst.io/procedures/pre_commit.html#ts-pre-commit-conf.
