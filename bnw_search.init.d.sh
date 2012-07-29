#!/bin/bash

### BEGIN INIT INFO
# Provides:          bnw_search
# Required-Start:    $network $local_fs
# Required-Stop:     $network $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       Search service for BnW
### END INIT INFO

set -e
NAME=bnw_search
BNW_PATH=$HOME/bnw
BNW_VENV_PATH=$BNW_PATH/.venv
DAEMON=$BNW_VENV_PATH/bin/twistd
PIDFILE=/tmp/bnw_search.pid
DAEMON_OPTS="--pidfile=$PIDFILE
             --logfile=/tmp/bnw_search.log
             --reactor=epoll
             --python=$BNW_PATH/search.tac"
USER=bnw
GROUP=bnw
source $BNW_VENV_PATH/bin/activate

case "$1" in
  start)
        echo -n "Starting daemon: $NAME"
        start-stop-daemon --start --chuid "$USER" --group "$GROUP" --exec "$DAEMON" -- $DAEMON_OPTS
        echo "."
        ;;
  stop)
        echo -n "Stopping daemon: $NAME"
        start-stop-daemon --stop --oknodo --retry 30 --pidfile "$PIDFILE"
        echo "."
        ;;
  restart)
        echo -n "Restarting daemon: $NAME"
        start-stop-daemon --stop --oknodo --retry 30 --pidfile "$PIDFILE"
        start-stop-daemon --start --chuid "$USER" --group "$GROUP" --exec "$DAEMON" -- $DAEMON_OPTS
        echo "."
        ;;
  *)
        echo "Usage: "$1" {start|stop|restart}"
        exit 1
esac

exit 0
