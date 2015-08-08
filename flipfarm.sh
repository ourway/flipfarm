#!/bin/bash
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
          DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
            SOURCE="$(readlink "$SOURCE")"
              [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
export FLIPFARM_ROOT="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
alias flipfarm="cd $FLIPFARM_ROOT;source .pyenv/bin/activate"
alias "client-open"="python -c 'import webbrowser as wb;"
alias "flipfarm-client"="flipfarm;gunicorn -b 127.0.0.1:9000 -k gevent -w 2 client:app --reload"
alias "flipfarm-server"="flipfarm;gunicorn -b 0.0.0.0:9001 -k gevent -w 2 server:app --reload"
alias "flipfarm-client-worker"="flipfarm;celery -A clientAgent worker -c 1 -n `whoami` --statedb=client.state --beat --pidfile=clientAgent.pid"
alias "flipfarm-server-worker"="flipfarm;celery -A serverAgent worker -c 4 -n `whoami`-server --statedb=server.state --beat --pidfile=clientAgent.pid"
