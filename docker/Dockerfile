ARG dev_cycle=develop
ARG registry=lsstts
FROM ${registry}/develop-env:${dev_cycle}

WORKDIR /usr/src/love/
COPY . .
COPY docker/start-daemon.sh .

RUN source /opt/lsst/software/stack/loadLSST.bash && \
    pip install lsst_efd_client

CMD ["/usr/src/love/start-daemon.sh"]
