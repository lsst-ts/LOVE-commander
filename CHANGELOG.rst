===============
Version History
===============

v7.1.4
------

* Change the build string in the conda recipe. `<https://github.com/lsst-ts/LOVE-commander/pull/83>`_

v7.1.3
------

* Cast bump result to BumpTestStatus to avoid issues with json serializer on reports app. `<https://github.com/lsst-ts/LOVE-commander/pull/82>`_

v7.1.2
------

* Add bump test result to query_m1m3_bump_tests response. `<https://github.com/lsst-ts/LOVE-commander/pull/81>`_

v7.1.1
------

* Refactor reports application to support ts-m1m3-utils v0.3.2. `<https://github.com/lsst-ts/LOVE-commander/pull/80>`_

v7.1.0
------

* Add query_efd_most_recent_timeseries method to the efd app in order to query most recent timeseries. `<https://github.com/lsst-ts/LOVE-commander/pull/79>`_
* Retrieve count from FieldInfo to allow the frontend identify which topic parameters are arrays. `<https://github.com/lsst-ts/LOVE-commander/pull/78>`_

v7.0.1
------

* Refactor dependency on criopy for BumpTestTimes to use lsst.ts.m1m3.utils. `<https://github.com/lsst-ts/LOVE-commander/pull/77>`_

v7.0.0
------

* Update love commander to make it compatible with salobj-kafka. `<https://github.com/lsst-ts/LOVE-commander/pull/76>`_

v6.2.1
------

* Simplify query_efd_logs function and remove constraint on limit of logs `<https://github.com/lsst-ts/LOVE-commander/pull/75>`_

v6.2.0
------

* Add identity to issued salobj.Remote commands `<https://github.com/lsst-ts/LOVE-commander/pull/74>`_

v6.1.2
------

* Hook up to the ts_jenkins_shared_library `<https://github.com/lsst-ts/LOVE-commander/pull/70>`_
* Remove unused files `<https://github.com/lsst-ts/LOVE-commander/pull/72>`_
* Refactor use of pytest-aiohttp plugins `<https://github.com/lsst-ts/LOVE-commander/pull/71>`_
* Refactor use of Dockerfile-dev image `<https://github.com/lsst-ts/LOVE-commander/pull/69>`_

v6.1.1
------

* Remove authlist references `<https://github.com/lsst-ts/LOVE-commander/pull/68>`_

v6.1.0
------

* Add M1M3 Bump Tests reports `<https://github.com/lsst-ts/LOVE-commander/pull/66>`_

v6.0.6
------

* Hotfix for Jenkinsfile `<https://github.com/lsst-ts/LOVE-commander/pull/65>`_
* Move docs creation to CI `<https://github.com/lsst-ts/LOVE-commander/pull/63>`_
* Add ts_pre_commit_conf `<https://github.com/lsst-ts/LOVE-commander/pull/64>`_

v6.0.5
------

* Improve copyright file `<https://github.com/lsst-ts/LOVE-commander/pull/62>`_
* LOVE License `<https://github.com/lsst-ts/LOVE-commander/pull/61>`_
* Move `salobj.SalInfo` call to async function to avoid event loop errors `<https://github.com/lsst-ts/LOVE-commander/pull/60>`_
* Refactor way of getting component names `<https://github.com/lsst-ts/LOVE-commander/pull/59>`_

v6.0.4
-------

* Change query_efd_logs to allow timestamp scale specification `<https://github.com/lsst-ts/LOVE-commander/pull/58>`_

v6.0.3
-------

* Add TimeOut error when connecting to EFD instance `<https://github.com/lsst-ts/LOVE-commander/pull/48>`_

v6.0.2
-------

* Add changelog checker `<https://github.com/lsst-ts/LOVE-commander/pull/57>`_


v6.0.1
-------

* Extend LFA endpoint to allow LOVE config files uploads `<https://github.com/lsst-ts/LOVE-commander/pull/56>`_

v6.0.0
-------

* Update sphinx dependencies `<https://github.com/lsst-ts/LOVE-commander/pull/55>`_
* Transform LOVE-commander repository to be a python package `<https://github.com/lsst-ts/LOVE-commander/pull/54>`_

v5.5.1
-------

* Add repository version history `<https://github.com/lsst-ts/LOVE-commander/pull/53>`_

v5.5.0
-------

* OLE Implementation `<https://github.com/lsst-ts/LOVE-commander/pull/51>`_

v5.4.3
-------

* Update aiohttp-devtools to latest version 1.0.post0 `<https://github.com/lsst-ts/LOVE-commander/pull/52>`_
* tickets/SITCOM-432 `<https://github.com/lsst-ts/LOVE-commander/pull/50>`_

v5.4.2
-------

* Update build to pyproject.toml `<https://github.com/lsst-ts/LOVE-commander/pull/49>`_

v5.4.1
-------

* Change deprecated event.put method `<https://github.com/lsst-ts/LOVE-commander/pull/47>`_
* Add EFD logMessage endpoint `<https://github.com/lsst-ts/LOVE-commander/pull/46>`_

v5.3.1
-------

* Fix problems with EFD querying `<https://github.com/lsst-ts/LOVE-commander/pull/45>`_

v5.2.1
-------

* Refactor docker files path `<https://github.com/lsst-ts/LOVE-commander/pull/43>`_
* Hotfix/update jenkinsfile `<https://github.com/lsst-ts/LOVE-commander/pull/42>`_
* Add methods about the MTCS commands `<https://github.com/lsst-ts/LOVE-commander/pull/41>`_

v5.1.0
-------

* Refactor Observing Logs endpoint `<https://github.com/lsst-ts/LOVE-commander/pull/40>`_
* Refactor EFD Enpoint `<https://github.com/lsst-ts/LOVE-commander/pull/39>`_


v5.0.3
-------

* Upgrade dev-cycle to c0021.007 `<https://github.com/lsst-ts/LOVE-commander/pull/38>`_
* Upgrade dev-cycle to c0020.006 `<https://github.com/lsst-ts/LOVE-commander/pull/37>`_

v5.0.2
-------

* DM-30455: Fix conda recipe in LOVE-commander `<https://github.com/lsst-ts/LOVE-commander/pull/36>`_

v5.0.1
-------

* Add conda packaging. `<https://github.com/lsst-ts/LOVE-commander/pull/35>`_
* Upgrade dev-cycle to c0020.001 `<https://github.com/lsst-ts/LOVE-commander/pull/34>`_

v5.0.0
-------

* LOVE-commander of linode environment stopped working after recent update `<https://github.com/lsst-ts/LOVE-commander/pull/32>`_
* Rollback to previous change `<https://github.com/lsst-ts/LOVE-commander/pull/31>`_
* Tcs api `<https://github.com/lsst-ts/LOVE-commander/pull/25>`_

v4.1.0
-------

* Fix startup script in the deployment image. `<https://github.com/lsst-ts/LOVE-commander/pull/30>`_
* Upgrade develop-env to c0018.001 `<https://github.com/lsst-ts/LOVE-commander/pull/29>`_


v4.0.0
-------

* Rollback to dev env version c0017.000 `<https://github.com/lsst-ts/LOVE-commander/pull/28>`_
* Upgrade to lsstts/develop-env:c0018.000 `<https://github.com/lsst-ts/LOVE-commander/pull/27>`_
* Build docker images from tickets branch `<https://github.com/lsst-ts/LOVE-commander/pull/26>`_
* Hotfix efdclient `<https://github.com/lsst-ts/LOVE-commander/pull/24>`_
* Hotfix efd client `<https://github.com/lsst-ts/LOVE-commander/pull/23>`_
