#!/bin/bash
# description: Description comes here....

start() {
    # code to start app comes here 
    # example: daemon program_name &
    # TODO (@theMladyPan) toto prerobiť na relatívne cesty
    /home/stanke/xerxes-node/venv/bin/python /home/stanke/xerxes-node/xerxes-worker&PID=$!
}

stop() {
    # code to stop app comes here 
    # example: killproc program_name
    # TODO (@theMladyPan) toto lepšie spraviť
    echo killing worker $PID
    kill $PID
    # killall xerxes-worker
}

case "$1" in 
    start)
       start
       ;;
    stop)
       stop
       ;;
    restart)
       stop
       start
       ;;
    status)
       # code to check status of app comes here 
       # example: status program_name
       ;;
    *)
       echo "Usage: $0 {start|stop|status|restart}"
esac

exit 0 