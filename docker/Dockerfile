ARG dev_cycle=develop
FROM lsstts/develop-env:${dev_cycle}

WORKDIR /usr/src/love/
COPY . .

RUN source /opt/lsst/software/stack/loadLSST.bash && \
    pip install lsst_efd_client

CMD ["/usr/src/love/docker/start-daemon.sh"]
