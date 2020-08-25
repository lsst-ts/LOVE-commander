FROM lsstts/develop-env:c0010

WORKDIR /usr/src/love/

COPY . .
# Missing SAL topics
RUN source /opt/lsst/software/stack/loadLSST.bash \
    && source /home/saluser/.setup_salobj.sh \
    && setup ts_sal -t current \
    && /home/saluser/repos/ts_sal/bin/make_idl_files.py Watcher

WORKDIR /home/saluser

CMD ["/usr/src/love/commander/start-daemon.sh"]
