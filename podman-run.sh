#!/bin/bash
set -eu -o pipefail

POD_NAME="${POD_NAME:-bnw}"

podman pod exists "$POD_NAME" || podman pod create --name "$POD_NAME" -p 7808 -p 7809 -p 7810

if ! podman container exists "$POD_NAME-mongo"; then
    podman run --pod "$POD_NAME" --name "$POD_NAME-mongo" --rm -tid docker.io/mongo:3.6
    sleep 2 # yeah, waiting for mongo to come up
fi

if ! podman container exists "$POD_NAME-thumbor"; then
    podman run --pod "$POD_NAME" --name "$POD_NAME-thumbor" --rm -tid \
        --env THUMBOR_PORT=7809 \
        docker.io/minimalcompact/thumbor
fi

podman run --pod "$POD_NAME" --name "$POD_NAME-bnw" --rm -ti \
    --env 'PYTHONUNBUFFERED=x' \
    --env 'BNW_SRVC_NAME=localhost' \
    --env 'BNW_SRVC_PWD=fuckyou' \
    --env 'BNW_WEBUI_PORT=0.0.0.0:7808' \
    --env 'BNW_THUMBOR=http://localhost:7809' \
    --env 'BNW_THUMBOR_KEY=MY_SECURE_KEY' \
    "$@" bnw
