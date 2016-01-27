#!/bin/bash
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
          DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
            SOURCE="$(readlink "$SOURCE")"
              [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
export FLIPFARM_ROOT="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
alias flipfarm="cd $FLIPFARM_ROOT"
alias "flipfarm-server"="flipfarm;gunicorn -c gu_config.py app:app"
alias "flipfarm-worker"="flipfarm;python clientAgent.py"
alias "flipfarm-pinger"="flipfarm;python pingAgent.py"
#export PATH=$FLIPFARM_ROOT/.pyenv/bin:$PATH
#--access-logfile logs/client.log
# -f logs/clientAgent.log
