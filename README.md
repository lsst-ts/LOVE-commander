# LOVE-commander
LOVE service to send SAL commands from http endpoints using salobj



## Running tests
Disabling plugins that may throw errors due to not having write access is recommended: 

```
pytest -p no:cacheprovider -p no:pytest_session2file
```
