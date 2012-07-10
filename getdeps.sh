#!/bin/bash
PROGDIR="$(dirname -- "$(readlink -f "$0")")"
VENV="$PROGDIR/.venv"
echo "Virtual env dir: $VENV"
if [ -d "$PROGDIR/.venv" ]; then
    echo "Virtual env already exists"
    #exit 1
else
    mkdir "$VENV"
    virtualenv -p python2 "$VENV"
fi
PIP="$VENV/bin/pip"

$PIP install twisted && \
$PIP install tornado && \
$PIP install PyRSS2Gen && \
$PIP install 'git+git://github.com/fiorix/mongo-async-python-driver.git'

