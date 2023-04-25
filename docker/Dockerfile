ARG dev_cycle=develop
ARG registry=lsstts
FROM ${registry}/develop-env:${dev_cycle}

WORKDIR /usr/src/love/
COPY . .
COPY docker/start-daemon.sh .

RUN source /home/saluser/.setup_dev.sh && \
    pip install lsst_efd_client && \
    pip install /usr/src/love/

CMD ["/usr/src/love/start-daemon.sh"]
