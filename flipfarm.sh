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
export MAC=`python -c "import uuid;print uuid.getnode();"`
alias "flipfarm-pinger"="flipfarm;celery -A pingAgent worker -n $MAC -l info --beat;"
export PATH=$FLIPFARM_ROOT/.pyenv/bin:$PATH
#--access-logfile logs/client.log
# -f logs/clientAgent.log
