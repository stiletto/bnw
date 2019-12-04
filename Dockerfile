FROM docker.io/debian:stable AS base

RUN export DEBIAN_FRONTEND=noninteractive; apt-get -qq update && \
    apt-get -qqy install python2.7 python-xapian

FROM base AS builder

RUN export DEBIAN_FRONTEND=noninteractive; apt-get -qq update && \
    apt-get -qq install -y --no-install-recommends python-virtualenv gcc python2.7-dev

RUN python2 -m virtualenv -p python2.7 --system-site-packages /bnw/venv
COPY bnw /bnw/src/bnw
COPY setup.py /bnw/src/setup.py
COPY config.py.docker_env /bnw/config/config.py
RUN cd /bnw/src && /bnw/venv/bin/python2 setup.py install

FROM base

COPY --from=builder /bnw /bnw
ENV PYTHONPATH /bnw/config
ENTRYPOINT ["/bnw/venv/bin/bnw", "-n", "-l-"]
