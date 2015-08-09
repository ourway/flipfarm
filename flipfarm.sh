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
alias "flipfarm-client"="flipfarm;gunicorn -b 127.0.0.1:9000 -k gevent -w 2 --worker-connections 4000 --threads 2 --max-requests 1024 -t 10 -n flipfarm-client -p client.pid --access-logfile logs/client.log client:app --reload"
alias "flipfarm-server"="flipfarm;gunicorn -b 0.0.0.0:9001 -k gevent -w 4 --worker-connections 16000 --threads 2 --max-requests 1024 -t 10 -n flipfarm-server -p server.pid --access-logfile logs/server.log server:app --reload"
alias "flipfarm-client-worker"="flipfarm;celery -A clientAgent worker -c 1 -l info -n `whoami` --statedb=client.state --beat --pidfile=clientAgent.pid -f logs/clientAgent.log"
alias "flipfarm-server-worker"="flipfarm;celery -A serverAgent worker -c 4 -n `whoami`-server --statedb=server.state --beat --pidfile=serverAgent.pid -l info -f logs/serverAgent.log"
